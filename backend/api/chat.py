from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import logging
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.gemini_provider import GeminiProvider
from backend.ai.openrouter_provider import OpenRouterProvider
from backend.ai.orchestrator import AIOrchestrator
from backend.api.deps import get_current_user
from backend.astrology.engine import engine
from backend.core.config import settings
from backend.database.database import get_db
from backend.database.models import User, Profile

logger = logging.getLogger("lumira_backend")
router = APIRouter(prefix="/chat", tags=["AI Chat"])

class ChatMessage(BaseModel):
    message: str

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

    try:
        zone = ZoneInfo(profile.timezone)
        birth_utc = profile.birth_date.replace(tzinfo=zone).astimezone(timezone.utc)
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
        return ChatResponse(reply="\n\n".join(sections).strip())
    except HTTPException:
        raise
    except Exception as exc:
        error_id = str(uuid.uuid4())
        logger.error("Chat error [ID: %s]: %s", error_id, exc, exc_info=True)
        return ChatResponse(reply=f"Не удалось завершить AI-интерпретацию. Проверьте настройки AI-провайдера или повторите запрос позже. Код ошибки: {error_id}")
