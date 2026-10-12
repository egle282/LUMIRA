from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo
import logging
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.gemini_provider import GeminiProvider
from backend.ai.openrouter_provider import OpenRouterProvider
from backend.ai.orchestrator import AIOrchestrator
from backend.api.deps import get_current_user
from backend.astrology.engine import engine
from backend.core.config import settings
from backend.billing.subscriptions import DAILY_AI_LIMITS
from backend.database.database import get_db
from backend.database.models import User, Profile, Subscription, InteractionLog

logger = logging.getLogger("lumira_backend")
router = APIRouter(prefix="/chat", tags=["AI Chat"])

class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    reply: str

@router.post("", response_model=ChatResponse)
async def ai_chat_endpoint(
    msg: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    openrouter_key = os.getenv("OPENROUTER_API_KEY") or settings.OPENROUTER_API_KEY
    gemini_key = os.getenv("LLM_API_KEY") or settings.LLM_API_KEY
    if not openrouter_key and not gemini_key:
        raise HTTPException(status_code=503, detail="Настройте OPENROUTER_API_KEY или LLM_API_KEY для работы AI-чата.")

    result = await db.execute(
        select(Profile).where(Profile.user_id == current_user.id).limit(1)
    )
    profile = result.scalars().first()
    if profile is None:
        raise HTTPException(status_code=400, detail="Сначала заполните профиль рождения в настройках.")

    now = datetime.now(timezone.utc)
    try:
        profile_zone = ZoneInfo(profile.timezone)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="В профиле указан некорректный часовой пояс.") from exc
    subscription_result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc()).limit(1)
    )
    subscription = subscription_result.scalars().first()
    plan_name = "free"
    if subscription and subscription.status in {"active", "trialing"}:
        if subscription.current_period_end is None or subscription.current_period_end > now:
            plan_name = subscription.plan_name.lower()
    daily_limit = DAILY_AI_LIMITS.get(plan_name, DAILY_AI_LIMITS["free"])
    # Daily quotas follow the user's profile timezone, including daylight-saving
    # transitions, rather than resetting at midnight UTC for everyone.
    day_start = now.astimezone(profile_zone).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).astimezone(timezone.utc)
    usage_result = await db.execute(
        select(func.count()).select_from(InteractionLog).where(
            InteractionLog.user_id == current_user.id,
            InteractionLog.intent == "ai_chat",
            InteractionLog.created_at >= day_start,
        )
    )
    daily_usage = int(usage_result.scalar_one())
    if daily_usage >= daily_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Достигнут дневной лимит AI-сообщений для тарифа {plan_name}: {daily_limit}.",
        )

    try:
        zone = ZoneInfo(profile.timezone)
        # The schema stores birth date and birth time separately; combining them
        # is essential for correct ascendant and house calculations.
        birth_date = profile.birth_date.date() if isinstance(profile.birth_date, datetime) else profile.birth_date
        birth_clock = time.fromisoformat(profile.birth_time_str)
        birth_local = datetime.combine(birth_date, birth_clock, tzinfo=zone)
        birth_utc = birth_local.astimezone(timezone.utc)
        current_utc = datetime.now(timezone.utc)
        natal_chart = engine.calculate_natal_chart(birth_utc, profile.lon, profile.lat)
        transits_chart = engine.calculate_natal_chart(current_utc, profile.lon, profile.lat)
        panchanga = engine.calculate_panchanga(current_utc, profile.lon, profile.lat)
        transit_summary = [
            {
                "planet": name,
                "longitude": round(float(data["longitude"]), 4),
                "sign_index": int(float(data["longitude"]) % 360 // 30),
                "retrograde": float(data.get("speed", 0)) < 0,
            }
            for name, data in transits_chart["positions"].items()
        ]
        deterministic_data = {
            "natal_chart": natal_chart,
            "transits": transit_summary,
            "panchanga": panchanga,
            "calculated_at_utc": current_utc.isoformat(),
            "profile_timezone": profile.timezone,
        }
        primary = (
            OpenRouterProvider(api_key=openrouter_key, model_name="meta-llama/llama-3.1-8b-instruct:free")
            if openrouter_key else GeminiProvider(api_key=gemini_key)
        )
        fallback = GeminiProvider(api_key=gemini_key) if openrouter_key and gemini_key else None
        orchestrator = AIOrchestrator(primary_provider=primary, fallback_provider=fallback)
        interp = await orchestrator.interpret_chart(
            user_question=msg.message,
            deterministic_data=deterministic_data,
            memory_context="Пользователь общается с LUMIRA и исследует собственную натальную карту.",
        )
        sections = [interp.summary]
        if interp.opportunities:
            sections.append("🌟 Возможности:\n" + "\n".join(f"- {item}" for item in interp.opportunities))
        if interp.risks:
            sections.append("⚠️ На что обратить внимание:\n" + "\n".join(f"- {item}" for item in interp.risks))
        if interp.recommendations:
            sections.append("💡 Рекомендации:\n" + "\n".join(f"- {item}" for item in interp.recommendations))
        reply = "\n\n".join(sections).strip()
        db.add(InteractionLog(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            intent="ai_chat",
            input_text=msg.message,
            output_text=reply,
            tokens_used=0,
        ))
        await db.commit()
        return ChatResponse(reply=reply)
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        error_id = str(uuid.uuid4())
        logger.error("Chat error [ID: %s]: %s", error_id, exc, exc_info=True)
        return ChatResponse(reply=f"Не удалось завершить AI-интерпретацию. Проверьте настройки AI-провайдера или повторите запрос позже. Код ошибки: {error_id}")
