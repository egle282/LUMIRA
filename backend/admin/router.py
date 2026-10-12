import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List

from backend.api.deps import get_current_user
from backend.database.database import get_admin_db
from backend.database.models import User, Profile, Subscription, InteractionLog

logger = logging.getLogger(__name__)

admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized. Admin role required.")
    return current_user

@admin_router.get("/metrics/ai-cost")
async def get_ai_costs(admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_admin_db)):
    logger.info(f"Admin action by user {admin_user.id}: Accessed AI cost metrics")
    total_messages = await db.scalar(
        select(func.count()).select_from(InteractionLog).where(InteractionLog.intent == "ai_chat")
    ) or 0
    # Providers do not currently return normalized token usage, so do not invent
    # token totals or dollar costs from a hard-coded price assumption.
    return {
        "total_ai_messages": total_messages,
        "token_usage_tracking": False,
        "estimated_cost_usd": None,
    }

@admin_router.get("/users")
async def list_users(admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_admin_db)):
    logger.info(f"Admin action by user {admin_user.id}: Listed all users")
    result = await db.execute(select(User.id, User.email, User.role, User.created_at))
    users = result.all()
    
    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at
        } for u in users
    ]

@admin_router.post("/feature-flags")
async def toggle_feature(feature_name: str, enabled: bool, admin_user: User = Depends(require_admin)):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Persistent feature-flag storage is not implemented.",
    )

