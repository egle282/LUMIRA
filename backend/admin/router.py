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
    # Join Profile and Subscription to return actual user name and plan
    stmt = (
        select(
            User.id,
            User.email,
            User.role,
            User.created_at,
            Profile.name.label("profile_name"),
            Subscription.plan_name.label("plan_name"),
            Subscription.status.label("sub_status")
        )
        .outerjoin(Profile, User.id == Profile.user_id)
        .outerjoin(Subscription, User.id == Subscription.user_id)
        .order_by(User.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        {
            "id": r.id,
            "email": r.email,
            "role": r.role,
            "name": r.profile_name,
            "plan": r.plan_name or "free",
            "subscription_status": r.sub_status or "active",
            "created_at": r.created_at
        } for r in rows
    ]


class UpdateUserRolePayload(BaseModel):
    role: str  # admin, user


@admin_router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    payload: UpdateUserRolePayload,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_admin_db)
):
    if payload.role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="Invalid role specified. Allowed: admin, user")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Safety: protect last admin from demotion
    if user.id == admin_user.id and payload.role != "admin":
        admin_count = await db.scalar(select(func.count()).select_from(User).where(User.role == "admin"))
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot demote the last remaining administrator")

    user.role = payload.role
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "email": user.email, "role": user.role}


@admin_router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_admin_db)
):
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own administrator account")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Protect last admin from deletion
    if user.role == "admin":
        admin_count = await db.scalar(select(func.count()).select_from(User).where(User.role == "admin"))
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last remaining administrator")

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully", "id": user_id}


@admin_router.post("/feature-flags")
async def toggle_feature(feature_name: str, enabled: bool, admin_user: User = Depends(require_admin)):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Persistent feature-flag storage is not implemented.",
    )

