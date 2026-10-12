import pytest
from pydantic import ValidationError

from backend.core.config import Settings


def test_production_rejects_example_jwt_secret():
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            JWT_SECRET="your_super_secret_jwt_key_at_least_32_chars_long",
            ENVIRONMENT="production",
        )


def test_production_accepts_unique_long_jwt_secret():
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        JWT_SECRET="9f1c0b82a6d47e35a1c9e8f4b6d2037a9f1c0b82a6d47e35",
        ENVIRONMENT="production",
    )
    assert settings.ENVIRONMENT == "production"
