from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BillingProvider(ABC):
    @abstractmethod
    def create_checkout_session(self, user_id: str, plan_id: str) -> str:
        """Returns a URL or token for the user to complete checkout."""
        pass

    @abstractmethod
    def verify_webhook(self, payload: Any, signature: str) -> bool:
        """Verifies the authenticity of an incoming webhook."""
        pass

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancels an active subscription."""
        pass

class TelegramStarsProvider(BillingProvider):
    """
    Implementation of Telegram Stars or Telegram Payments for the bot.
    """
    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    def create_checkout_session(self, user_id: str, plan_id: str) -> str:
        # Generate an invoice link using aiogram/Telegram API
        return f"tg://invoice?payload={user_id}_{plan_id}"

    def verify_webhook(self, payload: Any, signature: str) -> bool:
        return True # Handled via aiogram pre_checkout_query

    def cancel_subscription(self, subscription_id: str) -> bool:
        # Telegram stars subscriptions are often managed in-app by the user
        return True

class StripeProvider(BillingProvider):
    """
    Implementation of Stripe for the Web Application SaaS.
    """
    def __init__(self, api_key: str):
        # stripe.api_key = api_key
        pass

    def create_checkout_session(self, user_id: str, plan_id: str) -> str:
        # stripe.checkout.Session.create(...)
        return f"https://checkout.stripe.com/pay/{user_id}_{plan_id}"

    def verify_webhook(self, payload: Any, signature: str) -> bool:
        # stripe.Webhook.construct_event(...)
        return True

    def cancel_subscription(self, subscription_id: str) -> bool:
        # stripe.Subscription.delete(...)
        return True
