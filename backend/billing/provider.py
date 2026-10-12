"""Billing provider contracts.

Never return synthetic checkout URLs or accept unverified webhook events.
Providers must fail closed until backed by a real payment integration.
"""
from abc import ABC, abstractmethod
from typing import Any


class BillingNotConfiguredError(RuntimeError):
    """Raised when a payment provider is not implemented/configured."""


class BillingProvider(ABC):
    @abstractmethod
    def create_checkout_session(self, user_id: str, plan_id: str) -> str:
        """Create a real checkout session and return its provider URL."""

    @abstractmethod
    def verify_webhook(self, payload: Any, signature: str) -> bool:
        """Verify the provider's cryptographic webhook signature."""

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a real subscription at the payment provider."""


class TelegramStarsProvider(BillingProvider):
    """Explicitly unavailable until Telegram invoice/subscription flow is wired."""

    def __init__(self, bot_token: str):
        if not bot_token:
            raise ValueError("Telegram bot token is required")
        self.bot_token = bot_token

    def create_checkout_session(self, user_id: str, plan_id: str) -> str:
        raise BillingNotConfiguredError(
            "Telegram Stars checkout is not implemented; refusing to create a fake invoice."
        )

    def verify_webhook(self, payload: Any, signature: str) -> bool:
        # Telegram payment updates must be validated by the Telegram Bot API flow,
        # not accepted as arbitrary webhook payloads.
        return False

    def cancel_subscription(self, subscription_id: str) -> bool:
        raise BillingNotConfiguredError(
            "Telegram subscription cancellation is not implemented."
        )


class StripeProvider(BillingProvider):
    """Explicitly unavailable until Stripe Checkout and webhook verification are wired."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Stripe API key is required")
        self.api_key = api_key

    def create_checkout_session(self, user_id: str, plan_id: str) -> str:
        raise BillingNotConfiguredError(
            "Stripe Checkout is not implemented; refusing to return a fake checkout URL."
        )

    def verify_webhook(self, payload: Any, signature: str) -> bool:
        # Do not accept payment state changes without Stripe signature verification.
        return False

    def cancel_subscription(self, subscription_id: str) -> bool:
        raise BillingNotConfiguredError(
            "Stripe subscription cancellation is not implemented."
        )
