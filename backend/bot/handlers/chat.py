from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import select

from backend.ai.gemini_provider import GeminiProvider
from backend.ai.openrouter_provider import OpenRouterProvider
from backend.ai.orchestrator import AIOrchestrator
from backend.astrology.engine import engine
from backend.core.config import settings
from backend.core.logger import logger
from backend.database.database import AdminAsyncSessionLocal, AsyncSessionLocal
from backend.database.models import Profile, User
from backend.database.tenant import set_tenant_context

router = Router()


async def find_telegram_user(telegram_id: str) -> User | None:
    if AdminAsyncSessionLocal is None:
        raise RuntimeError("ADMIN_DATABASE_URL is required for Telegram account lookup")
    async with AdminAsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()


@router.message(F.text)
async def handle_user_message(message: Message):
    if not message.text:
        return
    logger.info("Received chat message", tg_id=message.from_user.id)
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        user = await find_telegram_user(str(message.from_user.id))
        if user is None:
            await message.answer("Для начала выполните /start и настройте профиль.")
            return

        async with AsyncSessionLocal() as db:
            await set_tenant_context(db, str(user.tenant_id))
            result = await db.execute(select(Profile).where(Profile.user_id == user.id))
            profile = result.scalars().first()
            if profile is None:
                await message.answer("Профиль не заполнен. Выполните /start.")
                return
            # Copy scalar fields before closing the session.
            birth_date = profile.birth_date
            birth_time_str = profile.birth_time_str
            lat, lon, timezone = profile.lat, profile.lon, profile.timezone

        hour, minute = map(int, birth_time_str.split(":"))
        local_dt = datetime(
            birth_date.year, birth_date.month, birth_date.day, hour, minute,
            tzinfo=ZoneInfo(timezone),
        )
        chart_data = await asyncio.to_thread(
            engine.calculate_natal_chart,
            dt=local_dt.replace(tzinfo=None),
            lon=lon,
            lat=lat,
        )

        # Prefer OpenRouter when configured; use Gemini as fallback when available.
        if settings.OPENROUTER_API_KEY:
            provider = OpenRouterProvider(api_key=settings.OPENROUTER_API_KEY)
            fallback = (
                GeminiProvider(api_key=settings.LLM_API_KEY)
                if settings.LLM_API_KEY
                else None
            )
        elif settings.LLM_API_KEY:
            provider = GeminiProvider(api_key=settings.LLM_API_KEY)
            fallback = None
        else:
            await message.answer(
                "AI-провайдер не настроен. Добавьте OPENROUTER_API_KEY "
                "или LLM_API_KEY в .env и перезапустите бота."
            )
            return

        orchestrator = AIOrchestrator(
            primary_provider=provider,
            fallback_provider=fallback,
        )
        response = await orchestrator.interpret_chart(
            user_question=message.text,
            deterministic_data=chart_data,
            memory_context="No prior memory in MVP.",
        )
        await message.answer(
            f"✨ <i>Разбор вопроса:</i>\n\n«{message.text}»\n\n{response.interpretation}"
        )
    except Exception:
        logger.exception("Error processing AI chat", tg_id=message.from_user.id)
        await message.answer(
            "Сейчас не удалось подготовить ответ. Попробуйте ещё раз позже. 🌌"
        )
