from datetime import datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo
import asyncio

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from backend.ai.gemini_provider import GeminiProvider
from backend.ai.openrouter_provider import OpenRouterProvider
from backend.ai.orchestrator import AIOrchestrator
from backend.astrology.engine import engine
from backend.core.config import settings
from backend.core.logger import logger
from backend.database.database import AdminAsyncSessionLocal, AsyncSessionLocal
from backend.database.models import Profile, User
from backend.briefing.service import BriefingService
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
        birth_utc = local_dt.astimezone(dt_timezone.utc)
        chart_data = await asyncio.to_thread(
            engine.calculate_natal_chart,
            dt=birth_utc,
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


@router.callback_query(F.data.startswith("menu_"))
async def handle_main_menu(callback: CallbackQuery):
    """Handle every button emitted by main_menu_keyboard."""
    await callback.answer()
    action = callback.data or ""
    if callback.message is None or callback.from_user is None:
        return

    try:
        user = await find_telegram_user(str(callback.from_user.id))
        if user is None:
            await callback.message.answer("Для начала выполните /start.")
            return

        async with AsyncSessionLocal() as db:
            await set_tenant_context(db, str(user.tenant_id))
            result = await db.execute(
                select(Profile).where(Profile.user_id == user.id).limit(1)
            )
            profile = result.scalars().first()
            if profile is None:
                await callback.message.answer("Профиль не заполнен. Выполните /start.")
                return
            birth_date = profile.birth_date
            birth_time_str = profile.birth_time_str
            lat, lon = profile.lat, profile.lon
            timezone_name = profile.timezone
            profile_name = profile.name

        zone = ZoneInfo(timezone_name)
        local_birth = datetime(
            birth_date.year, birth_date.month, birth_date.day,
            *map(int, birth_time_str.split(":")),
            tzinfo=zone,
        )
        birth_utc = local_birth.astimezone(dt_timezone.utc)

        if action == "menu_my_chart":
            chart = await asyncio.to_thread(
                engine.calculate_natal_chart, birth_utc, lon, lat
            )
            signs = ("Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
                     "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы")
            lines = []
            for planet, data in chart["positions"].items():
                longitude = float(data["longitude"]) % 360
                sign = signs[int(longitude // 30)]
                degree = longitude % 30
                lines.append(f"• {planet}: {sign}, {degree:.1f}° · накшатра #{int(data['nakshatra_index']) + 1}, пада {data['pada']}")
            await callback.message.answer(
                f"🗺️ <b>Натальная карта · {profile_name}</b>\n"
                + "\n".join(lines)
                + "\n\n<i>Расчёт Swiss Ephemeris, сидерический зодиак Лахири.</i>"
            )
            return

        if action == "menu_daily_briefing":
            briefing = await BriefingService(
                user_id=user.id, tenant_id=user.tenant_id
            ).generate_daily_briefing(target_date=None)
            await callback.message.answer(
                f"📅 <b>Дневной брифинг · {briefing.date.date()}</b>\n\n"
                f"<b>Панчанга</b>\n"
                f"Титхи: {briefing.panchanga.tithi}\n"
                f"Вара: {briefing.panchanga.vara}\n"
                f"Накшатра: {briefing.panchanga.nakshatra}\n"
                f"Йога: {briefing.panchanga.yoga}\n\n"
                f"{briefing.ai_interpretation}\n\n"
                f"<i>Традиционная астрологическая интерпретация, не гарантия событий.</i>"
            )
            return

        if action == "menu_muhurta":
            local_now = datetime.now(zone)
            panchanga = await asyncio.to_thread(
                engine.calculate_panchanga, local_now.astimezone(dt_timezone.utc), lon, lat
            )
            await callback.message.answer(
                "⏳ <b>Панчанга на текущий момент</b>\n"
                f"Титхи: {panchanga['tithi']}\n"
                f"Накшатра: {panchanga['nakshatra']}\n"
                f"Йога: {panchanga['yoga']}\n"
                f"Карана: {panchanga['karana']}\n\n"
                "Это справочная Панчанга, а не полный расчёт мухурты. "
                "Для выбора времени события учитывайте ограничения и персональные условия."
            )
            return

        if action == "menu_settings":
            from aiogram.fsm.context import FSMContext
            from backend.bot.handlers.onboarding import OnboardingStates
            # The state is set through the FSM middleware in the onboarding router
            # in a dedicated callback handler below.
            await callback.message.answer(
                "⚙️ <b>Настройки профиля</b>\n"
                f"Имя: {profile_name}\n"
                f"Дата рождения: {birth_date.date().isoformat()}\n"
                f"Время: {birth_time_str}\n"
                f"Координаты: {lat}, {lon}\n"
                f"Часовой пояс: {timezone_name}\n\n"
                "Чтобы изменить данные, отправьте команду /edit_profile."
            )
            return

        if action == "menu_ai_chat":
            await callback.message.answer("✨ Напишите свой вопрос — я отвечу с учётом вашей натальной карты.")
            return
    except Exception:
        logger.exception("Error handling Telegram menu callback", tg_id=callback.from_user.id)
        await callback.message.answer("Не удалось выполнить действие. Попробуйте ещё раз позже.")


@router.message(F.text == "/edit_profile")
async def edit_profile(message: Message, state):
    from backend.bot.handlers.onboarding import OnboardingStates
    await state.set_state(OnboardingStates.waiting_for_name)
    await message.answer("Введите новое имя. Затем обновим дату, время, координаты и часовой пояс рождения.")
