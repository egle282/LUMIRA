from .provider import LLMProvider
from .schema import AstrologyInterpretation, DailyBriefingAIOutput
from typing import Dict, Any
from backend.core.logger import logger

class AIOrchestrator:
    def __init__(self, primary_provider: LLMProvider, fallback_provider: LLMProvider = None):
        self.primary = primary_provider
        self.fallback = fallback_provider

    async def interpret_chart(
        self, 
        user_question: str, 
        deterministic_data: Dict[str, Any], 
        memory_context: str = ""
    ) -> AstrologyInterpretation:
        
        prompt = f"""
        You are LUMIRA, an advanced, professional Vedic Astrologer AI.
        
        USER QUESTION:
        {user_question}
        
        DETERMINISTIC ASTROLOGY DATA (Source of Truth):
        {deterministic_data}
        
        USER MEMORY / CONTEXT:
        {memory_context}
        
        CRITICAL RULES:
        1. Interpret the Deterministic Data to answer the User Question.
        2. If 'natal_chart' is present, use it as the user's birth chart, and interpret 'transits' as current planetary positions relative to it.
        3. Provide risks, opportunities, and timing based ONLY on the data.
        4. ALL RESPONSES MUST BE IN RUSSIAN. DO NOT ANSWER IN ENGLISH.
        5. Do not provide medical, legal, or financial guarantees.
        """
        
        try:
            logger.info("Calling primary AI provider")
            return await self.primary.generate_structured_response(prompt, AstrologyInterpretation)
        except Exception as e:
            logger.error("Primary AI provider failed", error=str(e))
            if self.fallback:
                logger.info("Calling fallback AI provider")
                return await self.fallback.generate_structured_response(prompt, AstrologyInterpretation)
            raise e

    async def generate_daily_briefing_interpretation(
        self,
        panchanga_data: Dict[str, Any],
        transits_data: list
    ) -> DailyBriefingAIOutput:
        prompt = f"""
        You are LUMIRA, a professional Vedic Astrologer AI.
        Generate a personalized daily astrological briefing IN RUSSIAN based on the following deterministic data:
        
        PANCHANGA TODAY:
        {panchanga_data}
        
        CURRENT TRANSITS:
        {transits_data}
        
        CRITICAL RULES:
        1. All text MUST be in Russian.
        2. Keep the interpretation concise (2-3 sentences max).
        3. Provide 2 'DO' recommendations and 1 'DON'T' caution.
        4. Provide 3 life focus areas (e.g., Семья, Карьера, Здоровье).
        """
        
        try:
            logger.info("Calling primary AI provider for Daily Briefing")
            return await self.primary.generate_structured_response(prompt, DailyBriefingAIOutput)
        except Exception as e:
            logger.error("Primary AI provider failed for Daily Briefing", error=str(e))
            if self.fallback:
                logger.info("Calling fallback AI provider for Daily Briefing")
                return await self.fallback.generate_structured_response(prompt, DailyBriefingAIOutput)
            raise e
