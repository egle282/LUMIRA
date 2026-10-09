from enum import Enum
from pydantic import BaseModel
from typing import Dict

class PlanType(str, Enum):
    FREE = "FREE"
    SEEKER = "SEEKER"       # Basic tier
    ORACLE = "ORACLE"       # Premium tier
    ENTERPRISE = "ENTERPRISE" # API/Astrologer tier

class SubscriptionPlan(BaseModel):
    id: str
    name: PlanType
    monthly_price: float
    max_daily_ai_messages: int
    max_saved_charts: int
    features: list[str]

PLANS: Dict[PlanType, SubscriptionPlan] = {
    PlanType.FREE: SubscriptionPlan(
        id="plan_free",
        name=PlanType.FREE,
        monthly_price=0.0,
        max_daily_ai_messages=5,
        max_saved_charts=1,
        features=["Basic Natal Chart", "Daily Transits"]
    ),
    PlanType.SEEKER: SubscriptionPlan(
        id="plan_seeker",
        name=PlanType.SEEKER,
        monthly_price=9.99,
        max_daily_ai_messages=50,
        max_saved_charts=10,
        features=["Full Natal Chart", "Karma Timeline", "Muhurta Insights"]
    ),
    PlanType.ORACLE: SubscriptionPlan(
        id="plan_oracle",
        name=PlanType.ORACLE,
        monthly_price=29.99,
        max_daily_ai_messages=9999, # Unlimited
        max_saved_charts=9999,
        features=["All Features", "Destiny Matrix", "Priority AI Context", "No Limits"]
    )
}

class UsageTracker:
    """
    Tracks and limits user usage based on their active subscription plan.
    Must integrate with PostgreSQL/Redis to persist usage counts.
    """
    
    def check_ai_message_limit(self, user_id: str, plan: PlanType, current_daily_usage: int) -> bool:
        plan_limits = PLANS[plan]
        return current_daily_usage < plan_limits.max_daily_ai_messages

    def record_ai_message(self, user_id: str):
        # Increment daily counter in DB/Redis
        pass
