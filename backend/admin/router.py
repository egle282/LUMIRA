from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List

from backend.api.deps import get_current_user, get_db
from backend.database.models import User, Profile, Subscription, InteractionLog

admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized. Admin role required.")
    return current_user

@admin_router.get("/metrics/ai-cost")
async def get_ai_costs(admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    total_tokens = await db.scalar(select(func.sum(InteractionLog.tokens_used))) or 0
    # Assuming $0.01 per 1000 tokens for calculation
    cost = (total_tokens / 1000) * 0.01
    
    return {
        "total_tokens_used": total_tokens,
        "estimated_cost_usd": round(cost, 4),
    }

@admin_router.get("/users")
async def list_users(admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
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
    # Mock feature flag DB storage
    return {"status": "success", "feature": feature_name, "state": "enabled" if enabled else "disabled"}

