from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from backend.core.logger import logger
from backend.database.database import AsyncSessionLocal
from sqlalchemy import select
from backend.database.models import User, Profile, Tenant
from backend.bot.keyboards import main_menu_keyboard
import uuid
from datetime import datetime

router = Router()

class OnboardingStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_birth_date = State()
    waiting_for_birth_time = State()
    waiting_for_location = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    logger.info("New user started bot", tg_id=message.from_user.id)
    
    async with AsyncSessionLocal() as db:
        tg_id_str = str(message.from_user.id)
        result = await db.execute(select(User).where(User.telegram_id == tg_id_str))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create default tenant and user
            tenant = Tenant(id=str(uuid.uuid4()), name=f"TG_{message.from_user.username}")
            db.add(tenant)
            user = User(
                id=str(uuid.uuid4()),
                tenant_id=tenant.id,
                role="user",
                telegram_id=tg_id_str,
            )
            db.add(user)
            await db.commit()
            
        profile_result = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = profile_result.scalar_one_or_none()
        
        if profile:
            welcome_text = f"Welcome back, {profile.name}! 🙏 How can I assist you today?"
            await message.answer(welcome_text, reply_markup=main_menu_keyboard())
            return
            
    # Start Onboarding
    welcome_text = (
        f"Namaste, <b>{message.from_user.first_name}</b>! 🙏\n\n"
        "I am <b>LUMIRA</b>, your personal Vedic AI Astrologer.\n\n"
        "To give you accurate insights, I need your Birth Data.\n"
        "First, what is your <b>Name</b>?"
    )
    await message.answer(welcome_text)
    await state.set_state(OnboardingStates.waiting_for_name)

@router.message(OnboardingStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Great! Now, please enter your <b>Date of Birth</b> (YYYY-MM-DD):")
    await state.set_state(OnboardingStates.waiting_for_birth_date)

@router.message(OnboardingStates.waiting_for_birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text.strip(), "%Y-%m-%d")
        await state.update_data(birth_date=dt)
        await message.answer("Got it. Now enter your <b>Time of Birth</b> (HH:MM):")
        await state.set_state(OnboardingStates.waiting_for_birth_time)
    except ValueError:
        await message.answer("Invalid format. Please use YYYY-MM-DD (e.g., 1990-05-15).")

@router.message(OnboardingStates.waiting_for_birth_time)
async def process_birth_time(message: Message, state: FSMContext):
    await state.update_data(birth_time_str=message.text.strip())
    await message.answer("Finally, please tell me your <b>City of Birth</b>:")
    await state.set_state(OnboardingStates.waiting_for_location)

@router.message(OnboardingStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    data = await state.get_data()
    
    # In production, use Geocoding API to get lat/lon/timezone from city name.
    # For MVP, we mock it:
    lat, lon, timezone = 19.0760, 72.8777, "Asia/Kolkata" # Mock Mumbai
    
    async with AsyncSessionLocal() as db:
        tg_id_str = str(message.from_user.id)
        result = await db.execute(select(User).where(User.telegram_id == tg_id_str))
        user = result.scalar_one_or_none()
        
        profile = Profile(
            id=str(uuid.uuid4()),
            tenant_id=user.tenant_id,
            user_id=user.id,
            name=data['name'],
            birth_date=data['birth_date'],
            birth_time_str=data['birth_time_str'],
            lat=lat,
            lon=lon,
            timezone=timezone
        )
        db.add(profile)
        await db.commit()
        
    await state.clear()
    await message.answer(f"Thank you, {data['name']}! Your profile is saved. 🌌\nYou can now ask me astrology questions.", reply_markup=main_menu_keyboard())
