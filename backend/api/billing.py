from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from backend.api.deps import get_current_user, get_db
from backend.database.models import User, Subscription
import uuid

router = APIRouter(prefix="/billing", tags=["Billing"])

class SubscriptionUpdateResponse(BaseModel):
    status: str
    plan_name: str
    message: str

@router.get("/status")
async def get_billing_status(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subscription).where(Subscription.user_id == current_user.id))
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        return {
            "plan_name": "free",
            "status": "active",
            "current_period_end": None
        }
        
    return {
        "plan_name": subscription.plan_name,
        "status": subscription.status,
        "current_period_end": subscription.current_period_end
    }

@router.post("/upgrade")
async def upgrade_subscription(
    plan_name: str,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # LUM-BILL-001: Prevent billing activation bypass.
    # Billing must be implemented via a secure provider with webhook verification.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Billing provider is unconfigured. Cannot activate paid plans without verified provider evidence."
    )

@router.post("/webhook")
async def billing_webhook():
    # Placeholder for billing provider webhook.
    # Must validate signature, check replay, and safely update subscription state.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Billing provider is unconfigured."
    )
