from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MemoryBase(BaseModel):
    memory_type: str = Field(..., description="Type of memory: fact, preference, correction, reading_summary, important_date, question")
    content: str = Field(..., description="The content of the memory")
    confidence: float = Field(1.0, description="Confidence score of the memory")

class MemoryCreate(MemoryBase):
    pass

class MemoryUpdate(BaseModel):
    memory_type: Optional[str] = None
    content: Optional[str] = None
    confidence: Optional[float] = None

class MemoryResponse(MemoryBase):
    id: str
    tenant_id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
