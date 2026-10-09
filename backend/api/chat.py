from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.api.deps import get_current_user
from backend.database.database import get_db
from backend.database.models import User, Profile
from backend.ai.orchestrator import AIOrchestrator
from backend.ai.openrouter_provider import OpenRouterProvider
from backend.astrology.engine import engine
from datetime import datetime
import os
import logging

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
    db: AsyncSession = Depends(get_db)
):
    """
    MVP AI Chat endpoint.
    Routes to the AI Orchestrator with deterministic data.
    """
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    if not openrouter_key:
        return ChatResponse(reply="API-ключ OpenRouter не настроен. Бэкенд запущен в режиме-заглушке.")

    try:
        # Calculate deterministic astrological state for today
        target_date = datetime.utcnow()
        
        stmt = select(Profile).where(Profile.user_id == current_user.id)
        result = await db.execute(stmt)
        profile = result.scalars().first()

        lat, lon = 55.75, 37.61
        natal_chart = None
        if profile:
            lat = profile.lat
            lon = profile.lon
            natal_chart = engine.calculate_natal_chart(profile.birth_date, lon, lat)
            
        panchanga = engine.calculate_panchanga(target_date, lon, lat)
        transits = engine.calculate_transits(target_date)
        
        # Prepare data context
        deterministic_data = {
            "panchanga": panchanga.model_dump(),
            "transits": [t.model_dump() for t in transits],
        }
        if natal_chart:
            deterministic_data["natal_chart"] = natal_chart

        provider = OpenRouterProvider(api_key=openrouter_key, model_name="meta-llama/llama-3.1-8b-instruct:free")
        orchestrator = AIOrchestrator(primary_provider=provider)
        
        # Generate structured interpretation
        interp = await orchestrator.interpret_chart(
            user_question=msg.message,
            deterministic_data=deterministic_data,
            memory_context="User is exploring their chart via LUMIRA chat."
        )

        # Format into a readable chat string in Russian
        reply = f"{interp.summary}\n\n"
        if interp.opportunities:
            reply += f"🌟 **Возможности:**\n" + "\n".join([f"- {opt}" for opt in interp.opportunities]) + "\n\n"
        if interp.risks:
            reply += f"⚠️ **Риски:**\n" + "\n".join([f"- {risk}" for risk in interp.risks]) + "\n\n"
        if interp.recommendations:
            reply += f"💡 **Рекомендации:**\n" + "\n".join([f"- {rec}" for rec in interp.recommendations])
            
        return ChatResponse(reply=reply.strip())
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(reply=f"Произошла ошибка при обращении к оракулу: {str(e)}")
