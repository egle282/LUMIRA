from typing import List, Dict, Any
from .memory import MemoryEngine
from .orchestrator import AIOrchestrator
from .tools import tools
from core.logger import logger

class ChatSession:
    def __init__(self, user_id: str, orchestrator: AIOrchestrator, memory_engine: MemoryEngine):
        self.user_id = user_id
        self.orchestrator = orchestrator
        self.memory_engine = memory_engine
        self.history: List[Dict[str, str]] = []

    async def send_message(self, message: str, profile_data: Dict[str, Any], db_session: Any) -> str:
        """
        Handles conversational turns.
        1. Retrieves user memory.
        2. Decide if tools (Astrology Engine) need to be called based on intent.
        3. Pass data to Orchestrator.
        4. Save interaction and extract new memories.
        """
        logger.info("Processing chat message", user_id=self.user_id)
        
        # 1. Retrieve Memory
        memory_context = await self.memory_engine.retrieve_memories(self.user_id, db_session)
        
        # 2. Append to short-term history
        self.history.append({"role": "user", "content": message})
        
        # (In a full implementation, we'd do an Intent Detection step here to decide which tools to run)
        # For MVP, assume we always provide the natal chart as base context.
        deterministic_data = profile_data.get("natal_chart", {})
        
        # 3. Call Orchestrator
        interpretation = await self.orchestrator.interpret_chart(
            user_question=message,
            deterministic_data=deterministic_data,
            memory_context=memory_context
        )
        
        response_text = interpretation.summary + "\n\n" + "\n".join(interpretation.recommendations)
        
        # 4. Background Memory Extraction & Logging (would be sent to background task)
        # memory_updates = await self.memory_engine.extract_memory_from_turn(message, response_text)
        # Save to DB...
        
        self.history.append({"role": "assistant", "content": response_text})
        
        return response_text
