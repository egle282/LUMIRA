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

@router.post("/upgrade", response_model=SubscriptionUpdateResponse)
async def upgrade_subscription(
    plan_name: str,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if plan_name not in ["pro", "premium"]:
        raise HTTPException(status_code=400, detail="Invalid plan name")
        
    result = await db.execute(select(Subscription).where(Subscription.user_id == current_user.id))
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        subscription = Subscription(
            id=str(uuid.uuid4()),
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            plan_name=plan_name,
            status="active"
        )
        db.add(subscription)
    else:
        subscription.plan_name = plan_name
        subscription.status = "active"
        
    await db.commit()
    
    return SubscriptionUpdateResponse(
        status="success",
        plan_name=plan_name,
        message=f"Successfully upgraded to {plan_name.capitalize()} plan."
    )
