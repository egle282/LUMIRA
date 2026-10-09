from aiogram import Router, F
from aiogram.types import Message
from backend.core.logger import logger
from backend.database.database import AsyncSessionLocal
from sqlalchemy import select
from backend.database.models import User, Profile
from backend.ai.gemini_provider import GeminiProvider
from backend.ai.orchestrator import AIOrchestrator
from backend.astrology.engine import engine
from backend.core.config import settings
from datetime import datetime

router = Router()

@router.message(F.text)
async def handle_user_message(message: Message):
    logger.info("Received chat message", tg_id=message.from_user.id)
    
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        async with AsyncSessionLocal() as db:
            tg_id_str = str(message.from_user.id)
            user_res = await db.execute(select(User).where(User.telegram_id == tg_id_str))
            user = user_res.scalar_one_or_none()
            
            if not user:
                await message.answer("Please use /start to set up your profile first.")
                return
                
            prof_res = await db.execute(select(Profile).where(Profile.user_id == user.id))
            profile = prof_res.scalar_one_or_none()
            
            if not profile:
                await message.answer("Your profile is incomplete. Please use /start.")
                return
                
            # Compute astrology data
            if profile.birth_time_str:
                time_parts = profile.birth_time_str.split(':')
                hour, minute = int(time_parts[0]), int(time_parts[1])
            else:
                hour, minute = 12, 0
                
            dt = datetime(
                profile.birth_date.year,
                profile.birth_date.month,
                profile.birth_date.day,
                hour,
                minute
            )
            
            chart_data = engine.calculate_natal_chart(
                dt=dt,
                lon=profile.lon or 0.0,
                lat=profile.lat or 0.0
            )
            
            provider = GeminiProvider(api_key=settings.LLM_API_KEY)
            orchestrator = AIOrchestrator(primary_provider=provider)
            
            response = await orchestrator.interpret_chart(
                user_question=message.text,
                deterministic_data=chart_data,
                memory_context="No prior memory in MVP."
            )
            
            response_text = f"✨ <i>I am interpreting your chart for:</i>\n\n«{message.text}»\n\n"
            response_text += response.interpretation
            
            await message.answer(response_text)
            
    except Exception as e:
        logger.error("Error processing AI chat", error=str(e))
        await message.answer("I am sorry, my connection to the stars is currently disrupted. Please try again later. 🌌")
