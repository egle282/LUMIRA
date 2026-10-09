from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List

from backend.api.deps import get_current_user, get_db
from backend.database.models import User, Profile, Subscription, InteractionLog

router = APIRouter(prefix="/admin", tags=["Admin"])

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized. Admin role required.")
    return current_user

@router.get("/stats")
async def get_system_stats(admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    users_count = await db.scalar(select(func.count(User.id)))
    profiles_count = await db.scalar(select(func.count(Profile.id)))
    active_subs = await db.scalar(select(func.count(Subscription.id)).where(Subscription.status == "active"))
    total_tokens = await db.scalar(select(func.sum(InteractionLog.tokens_used))) or 0
    
    return {
        "total_users": users_count,
        "total_profiles": profiles_count,
        "active_subscriptions": active_subs,
        "total_ai_tokens_used": total_tokens
    }

@router.get("/users")
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
