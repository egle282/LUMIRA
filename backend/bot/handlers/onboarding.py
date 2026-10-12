from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import uuid

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import select

from backend.bot.keyboards import main_menu_keyboard
from backend.core.logger import logger
from backend.database.database import AdminAsyncSessionLocal, AsyncSessionLocal
from backend.database.models import Profile, Tenant, User
from backend.database.tenant import set_tenant_context

router = Router()


class OnboardingStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_birth_date = State()
    waiting_for_birth_time = State()
    waiting_for_location = State()
    waiting_for_coordinates = State()


async def find_telegram_user(telegram_id: str) -> User | None:
    if AdminAsyncSessionLocal is None:
        raise RuntimeError("ADMIN_DATABASE_URL is required for Telegram account lookup")
    async with AdminAsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    tg_id = str(message.from_user.id)
    logger.info("Telegram user started bot", tg_id=message.from_user.id)
    user = await find_telegram_user(tg_id)

    if user is None:
        async with AsyncSessionLocal() as db:
            # Set tenant context before INSERT to satisfy tenant-table RLS.
            tenant = Tenant(id=str(uuid.uuid4()), name=f"telegram_{tg_id}")
            await set_tenant_context(db, str(tenant.id))
            db.add(tenant)
            await db.flush()
            user = User(
                id=str(uuid.uuid4()),
                tenant_id=tenant.id,
                role="user",
                telegram_id=tg_id,
            )
            db.add(user)
            await db.commit()
        user = await find_telegram_user(tg_id)

    if user is None:
        await message.answer("Не удалось создать профиль. Попробуйте ещё раз позже.")
        return

    async with AsyncSessionLocal() as db:
        await set_tenant_context(db, str(user.tenant_id))
        result = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = result.scalars().first()

    if profile:
        await message.answer(
            f"С возвращением, {profile.name}! 🙏 Чем могу помочь?",
            reply_markup=main_menu_keyboard(),
        )
        await state.clear()
        return

    await message.answer(
        f"Намасте, <b>{message.from_user.first_name}</b>! 🙏\n\n"
        "Я LUMIRA — ваш AI-астролог ведической традиции.\n"
        "Чтобы подготовить персональную карту, укажите данные рождения.\n"
        "Как вас зовут?"
    )
    await state.set_state(OnboardingStates.waiting_for_name)


@router.message(OnboardingStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name or len(name) > 120:
        await message.answer("Укажите имя длиной от 1 до 120 символов.")
        return
    await state.update_data(name=name)
    await message.answer("Введите дату рождения в формате ГГГГ-ММ-ДД:")
    await state.set_state(OnboardingStates.waiting_for_birth_date)


@router.message(OnboardingStates.waiting_for_birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    try:
        value = datetime.strptime((message.text or "").strip(), "%Y-%m-%d")
        if value.date() > datetime.utcnow().date():
            raise ValueError("Birth date cannot be in the future")
    except ValueError:
        await message.answer("Неверная дата. Используйте формат ГГГГ-ММ-ДД.")
        return
    await state.update_data(birth_date=value)
    await message.answer("Введите время рождения в формате ЧЧ:ММ (24-часовой формат):")
    await state.set_state(OnboardingStates.waiting_for_birth_time)


@router.message(OnboardingStates.waiting_for_birth_time)
async def process_birth_time(message: Message, state: FSMContext):
    value = (message.text or "").strip()
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError:
        await message.answer("Неверное время. Используйте формат ЧЧ:ММ, например 14:30.")
        return
    await state.update_data(birth_time_str=value)
    await message.answer("Укажите город и страну рождения (например, Кострома, Россия):")
    await state.set_state(OnboardingStates.waiting_for_location)


@router.message(OnboardingStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    location = (message.text or "").strip()
    if len(location) < 2 or len(location) > 200:
        await message.answer("Укажите город и страну рождения.")
        return
    await state.update_data(location=location)
    await message.answer(
        "Автоматический геокодер пока не настроен, поэтому я не буду подставлять "
        "чужие координаты. Пришлите координаты и часовой пояс в формате: "
        "широта, долгота, IANA-часовой пояс. Пример: 57.7679, 40.9269, Europe/Moscow."
    )
    await state.set_state(OnboardingStates.waiting_for_coordinates)


@router.message(OnboardingStates.waiting_for_coordinates)
async def process_coordinates(message: Message, state: FSMContext):
    try:
        parts = [part.strip() for part in (message.text or "").split(",")]
        if len(parts) != 3:
            raise ValueError("Expected latitude, longitude, timezone")
        lat, lon = float(parts[0]), float(parts[1])
        timezone = parts[2]
        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError("Coordinates out of range")
        ZoneInfo(timezone)
    except (ValueError, ZoneInfoNotFoundError):
        await message.answer(
            "Не удалось проверить данные. Формат: широта, долгота, IANA-часовой пояс "
            "(например: 57.7679, 40.9269, Europe/Moscow)."
        )
        return

    data = await state.get_data()
    user = await find_telegram_user(str(message.from_user.id))
    if user is None:
        await state.clear()
        await message.answer("Сначала выполните /start, затем повторите настройку.")
        return

    async with AsyncSessionLocal() as db:
        await set_tenant_context(db, str(user.tenant_id))
        existing = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = existing.scalars().first()
        if profile is None:
            profile = Profile(
                id=str(uuid.uuid4()),
                tenant_id=user.tenant_id,
                user_id=user.id,
                name=data["name"],
                birth_date=data["birth_date"],
                birth_time_str=data["birth_time_str"],
                lat=lat,
                lon=lon,
                timezone=timezone,
            )
            db.add(profile)
        else:
            profile.name = data["name"]
            profile.birth_date = data["birth_date"]
            profile.birth_time_str = data["birth_time_str"]
            profile.lat = lat
            profile.lon = lon
            profile.timezone = timezone
        await db.commit()

    await state.clear()
    await message.answer(
        f"Спасибо, {data['name']}! Данные профиля сохранены. 🌌",
        reply_markup=main_menu_keyboard(),
    )
