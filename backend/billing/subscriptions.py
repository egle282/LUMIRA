from enum import Enum
from pydantic import BaseModel
from typing import Dict


class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class SubscriptionPlan(BaseModel):
    id: str
    name: PlanType
    monthly_price: float
    max_daily_ai_messages: int
    max_saved_charts: int
    features: list[str]


PLANS: Dict[PlanType, SubscriptionPlan] = {
    PlanType.FREE: SubscriptionPlan(
        id="free",
        name=PlanType.FREE,
        monthly_price=0.0,
        max_daily_ai_messages=5,
        max_saved_charts=1,
        features=["Natal chart", "Daily Panchanga", "Basic AI chat"],
    ),
    PlanType.PRO: SubscriptionPlan(
        id="pro",
        name=PlanType.PRO,
        monthly_price=9.99,
        max_daily_ai_messages=50,
        max_saved_charts=1,
        features=["Natal chart", "Personal life-area signals", "Panchanga screening", "AI chat"],
    ),
    PlanType.PREMIUM: SubscriptionPlan(
        id="premium",
        name=PlanType.PREMIUM,
        monthly_price=24.99,
        max_daily_ai_messages=9999,
        max_saved_charts=1,
        features=["All currently implemented astrology features", "Expanded AI chat limit", "Stripe subscription management"],
    ),
}

DAILY_AI_LIMITS = {plan.value: details.max_daily_ai_messages for plan, details in PLANS.items()}


class UsageTracker:
    """Usage counters are persisted in InteractionLog by the API layer."""

    def check_ai_message_limit(self, user_id: str, plan: PlanType, current_daily_usage: int) -> bool:
        plan_limits = PLANS.get(plan, PLANS[PlanType.FREE])
        return current_daily_usage < plan_limits.max_daily_ai_messages

    def record_ai_message(self, user_id: str):
        """Usage is persisted as InteractionLog rows by the chat API."""
        return None
