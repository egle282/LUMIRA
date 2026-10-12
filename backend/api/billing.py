"""Stripe subscription checkout with signed, idempotent-by-state webhook handling."""
import asyncio
import time
from datetime import datetime, timezone
from typing import Any

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user, get_db
from backend.core.config import settings
from backend.database.models import User, Subscription
from backend.database.tenant import set_tenant_context

router = APIRouter(prefix="/billing", tags=["Billing"])
PLANS = {
    "pro": ("PRO", lambda: settings.STRIPE_PRICE_PRO),
    "premium": ("PREMIUM", lambda: settings.STRIPE_PRICE_PREMIUM),
}

@router.get("/status")
async def get_billing_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc()).limit(1)
    )
    subscription = result.scalars().first()
    if not subscription:
        return {"plan_name": "free", "status": "active", "current_period_end": None}
    return {
        "plan_name": subscription.plan_name,
        "status": subscription.status,
        "current_period_end": subscription.current_period_end,
    }

@router.post("/upgrade")
async def upgrade_subscription(
    plan_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if plan_name not in PLANS:
        raise HTTPException(status_code=400, detail="Unknown subscription plan.")
    existing_result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc()).limit(1)
    )
    existing = existing_result.scalars().first()
    if existing and existing.status in {"active", "trialing"} and existing.stripe_subscription_id:
        raise HTTPException(status_code=409, detail="An active subscription already exists. Manage it through the Stripe customer portal.")
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe checkout is not configured.")
    plan_id = PLANS[plan_name][1]()
    if not plan_id:
        raise HTTPException(status_code=503, detail=f"Stripe price for {plan_name} is not configured.")
    try:
        session = await asyncio.to_thread(
            stripe.checkout.Session.create,
            api_key=settings.STRIPE_SECRET_KEY,
            mode="subscription",
            line_items=[{"price": plan_id, "quantity": 1}],
            success_url=f"{settings.FRONTEND_URL.rstrip('/')}/?billing=success",
            cancel_url=f"{settings.FRONTEND_URL.rstrip('/')}/?billing=cancelled",
            client_reference_id=str(current_user.id),
            customer_email=current_user.email,
            metadata={
                "user_id": str(current_user.id),
                "tenant_id": str(current_user.tenant_id),
                "plan_name": plan_name,
            },
            subscription_data={"metadata": {
                "user_id": str(current_user.id),
                "tenant_id": str(current_user.tenant_id),
                "plan_name": plan_name,
            }},
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Stripe could not create a checkout session.") from exc
    if not session.url:
        raise HTTPException(status_code=502, detail="Stripe returned no checkout URL.")
    return {"status": "pending", "checkout_url": session.url, "session_id": session.id}

@router.post("/portal")
async def create_customer_portal(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe-hosted portal session for the authenticated user's customer."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe billing is not configured.")
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc()).limit(1)
    )
    subscription = result.scalars().first()
    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(status_code=404, detail="No Stripe customer is linked to this account.")
    try:
        session = await asyncio.to_thread(
            stripe.billing_portal.Session.create,
            api_key=settings.STRIPE_SECRET_KEY,
            customer=subscription.stripe_customer_id,
            return_url=settings.FRONTEND_URL.rstrip("/") + "/?billing=portal-return",
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Stripe could not create a customer portal session.") from exc
    if not session.url:
        raise HTTPException(status_code=502, detail="Stripe returned no customer portal URL.")
    return {"portal_url": session.url}


@router.post("/webhook")
async def billing_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Stripe webhook is not configured.")
    signature = request.headers.get("stripe-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature.")
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature or payload.") from exc

    event_type = event["type"]
    obj: dict[str, Any] = event["data"]["object"]
    if event_type not in {
        "checkout.session.completed",
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:
        return {"received": True, "ignored": True}

    metadata = obj.get("metadata") or {}
    user_id = metadata.get("user_id")
    tenant_id = metadata.get("tenant_id")
    plan_name = metadata.get("plan_name", "pro").lower()
    if not user_id or not tenant_id:
        # Ignore unrelated Stripe objects rather than mutate local subscription state.
        return {"received": True, "ignored": True}
    if plan_name not in PLANS:
        return {"received": True, "ignored": True}

    await set_tenant_context(db, tenant_id)
    user_result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == tenant_id).limit(1)
    )
    user = user_result.scalars().first()
    if user is None:
        return {"received": True, "ignored": True}

    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
        .order_by(Subscription.created_at.desc()).limit(1)
    )
    subscription = result.scalars().first()
    if subscription is None:
        subscription = Subscription(
            tenant_id=tenant_id, user_id=user_id, plan_name="free", status="active"
        )
        db.add(subscription)

    if event_type == "checkout.session.completed":
        # Checkout completion alone is not enough to grant access; subscription
        # lifecycle webhooks determine active/canceled status.
        subscription.stripe_customer_id = str(obj.get("customer") or "") or None
        subscription.stripe_subscription_id = str(obj.get("subscription") or "") or None
    else:
        stripe_status = obj.get("status", "inactive")
        subscription.plan_name = plan_name if stripe_status in {"active", "trialing"} else "free"
        subscription.status = stripe_status
        subscription.stripe_customer_id = str(obj.get("customer") or "") or None
        subscription.stripe_subscription_id = str(obj.get("id") or "") or None
        period_end = obj.get("current_period_end")
        subscription.current_period_end = datetime.fromtimestamp(period_end, timezone.utc) if period_end else None
        if event_type == "customer.subscription.deleted":
            subscription.plan_name = "free"
            subscription.status = "canceled"
    await db.commit()
    return {"received": True}
