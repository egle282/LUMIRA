from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import List, Optional
import logging

from backend.database.models import Memory
from backend.memory.schemas import MemoryCreate, MemoryUpdate

logger = logging.getLogger("lumira_backend")

class MemoryService:
    def __init__(self, session: AsyncSession, tenant_id: str, user_id: str):
        self.session = session
        self.tenant_id = tenant_id
        self.user_id = user_id

    async def get_memories(self, memory_type: Optional[str] = None) -> List[Memory]:
        """Fetch all memories for a specific user within a tenant."""
        stmt = select(Memory).where(
            Memory.tenant_id == self.tenant_id,
            Memory.user_id == self.user_id
        )
        if memory_type:
            stmt = stmt.where(Memory.memory_type == memory_type)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_memory(self, memory_data: MemoryCreate) -> Memory:
        """Add a new memory for a user."""
        new_memory = Memory(
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            memory_type=memory_data.memory_type,
            content=memory_data.content,
            confidence=memory_data.confidence
        )
        self.session.add(new_memory)
        await self.session.commit()
        await self.session.refresh(new_memory)
        logger.info(f"Added memory type={new_memory.memory_type} for user_id={self.user_id}")
        return new_memory

    async def update_memory(self, memory_id: str, memory_data: MemoryUpdate) -> Optional[Memory]:
        """Update an existing memory. Ensures tenant and user isolation."""
        stmt = select(Memory).where(
            Memory.id == memory_id,
            Memory.tenant_id == self.tenant_id,
            Memory.user_id == self.user_id
        )
        result = await self.session.execute(stmt)
        memory = result.scalar_one_or_none()

        if not memory:
            return None

        if memory_data.memory_type is not None:
            memory.memory_type = memory_data.memory_type
        if memory_data.content is not None:
            memory.content = memory_data.content
        if memory_data.confidence is not None:
            memory.confidence = memory_data.confidence

        await self.session.commit()
        await self.session.refresh(memory)
        return memory

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete an existing memory. Ensures tenant and user isolation."""
        stmt = select(Memory).where(
            Memory.id == memory_id,
            Memory.tenant_id == self.tenant_id,
            Memory.user_id == self.user_id
        )
        result = await self.session.execute(stmt)
        memory = result.scalar_one_or_none()
        
        if not memory:
            return False
            
        await self.session.delete(memory)
        await self.session.commit()
        logger.info(f"Deleted memory id={memory_id} for user_id={self.user_id}")
        return True
