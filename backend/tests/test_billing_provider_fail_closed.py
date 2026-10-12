import unittest

from backend.billing.provider import (
    BillingNotConfiguredError,
    StripeProvider,
    TelegramStarsProvider,
)


class BillingProviderFailClosedTests(unittest.TestCase):
    def test_stripe_never_returns_synthetic_checkout_or_accepts_webhook(self):
        provider = StripeProvider("sk_test_placeholder")
        with self.assertRaises(BillingNotConfiguredError):
            provider.create_checkout_session("user-1", "pro")
        self.assertFalse(provider.verify_webhook(b"{}", "fake-signature"))
        with self.assertRaises(BillingNotConfiguredError):
            provider.cancel_subscription("sub_fake")

    def test_telegram_never_returns_synthetic_invoice_or_accepts_webhook(self):
        provider = TelegramStarsProvider("telegram-token-placeholder")
        with self.assertRaises(BillingNotConfiguredError):
            provider.create_checkout_session("user-1", "pro")
        self.assertFalse(provider.verify_webhook({"amount": 1}, "fake-signature"))
        with self.assertRaises(BillingNotConfiguredError):
            provider.cancel_subscription("sub_fake")


if __name__ == "__main__":
    unittest.main()
