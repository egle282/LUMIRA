from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.database.database import get_db
from backend.api.deps import get_current_user
from backend.memory.schemas import MemoryCreate, MemoryUpdate, MemoryResponse
from backend.memory.service import MemoryService
from backend.database.models import User

router = APIRouter(prefix="/memory", tags=["Memory"])

def get_memory_service(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MemoryService:
    # Ensure tenant_id is available from current_user
    if not current_user.tenant_id:
        raise HTTPException(status_code=400, detail="User does not belong to a tenant")
    return MemoryService(session=db, tenant_id=current_user.tenant_id, user_id=current_user.id)

@router.get("/", response_model=List[MemoryResponse])
async def get_memories(
    memory_type: Optional[str] = Query(None, description="Filter by memory type"),
    service: MemoryService = Depends(get_memory_service)
):
    """Get all memories for the current user."""
    return await service.get_memories(memory_type=memory_type)

@router.post("/", response_model=MemoryResponse)
async def create_memory(
    memory: MemoryCreate,
    service: MemoryService = Depends(get_memory_service)
):
    """Add a new memory for the current user."""
    return await service.add_memory(memory)

@router.patch("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    memory_update: MemoryUpdate,
    service: MemoryService = Depends(get_memory_service)
):
    """Update a memory."""
    memory = await service.update_memory(memory_id, memory_update)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    service: MemoryService = Depends(get_memory_service)
):
    """Delete a memory."""
    success = await service.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "success"}
