from datetime import datetime
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


async def find_telegram_user(telegram_id: str) -> User | None:
    if AdminAsyncSessionLocal is None:
        raise RuntimeError("ADMIN_DATABASE_URL is required for Telegram account lookup")
    async with AdminAsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    tg_id = str(message.from_user.id)
    logger.info("Telegram user started bot", tg_id=message.from_user.id)
    user = await find_telegram_user(tg_id)

    if user is None:
        async with AsyncSessionLocal() as db:
            tenant = Tenant(name=f"telegram_{tg_id}")
            db.add(tenant)
            await db.flush()
            await set_tenant_context(db, str(tenant.id))
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
        profile = result.scalar_one_or_none()

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

    # Geocoding/time-zone lookup is intentionally not faked. Ask for coordinates
    # and IANA timezone when no geocoder is configured.
    data = await state.get_data()
    await state.update_data(location=location)
    await message.answer(
        "Чтобы расчёт был корректным, нужен часовой пояс и координаты города. "
        "Сервис геокодирования пока не настроен. Пришлите данные в формате: "
        "широта, долгота, часовой пояс (например: 57.7679, 40.9269, Europe/Moscow)."
    )
    await state.set_state(OnboardingStates.waiting_for_location_coordinates)


class _CoordinatesState(StatesGroup):
    waiting_for_coordinates = State()
