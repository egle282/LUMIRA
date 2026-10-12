from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "LUMIRA"
    DATABASE_URL: str
    ADMIN_DATABASE_URL: str | None = None
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    JWT_SECRET: str
    LLM_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    STRIPE_PRICE_PRO: str | None = None
    STRIPE_PRICE_PREMIUM: str | None = None
    FRONTEND_URL: str = "http://localhost:5173"
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    ALLOWED_ORIGINS: list[str] | str = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    @model_validator(mode='after')
    def validate_security_settings(self):
        if self.ENVIRONMENT == "production":
            placeholder_secrets = {
                "your_jwt_secret_here",
                "default_secret",
                "your_super_secret_jwt_key_at_least_32_chars_long",
                "change_me",
                "changeme",
            }
            if (
                not self.JWT_SECRET
                or len(self.JWT_SECRET) < 32
                or self.JWT_SECRET.strip().lower() in placeholder_secrets
                or self.JWT_SECRET.strip().lower().startswith(("your_", "change_me", "changeme"))
            ):
                raise ValueError("A unique, non-placeholder JWT_SECRET of at least 32 characters is required in production")
        return self

    @property
    def cors_origins(self) -> list[str]:
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [x.strip() for x in self.ALLOWED_ORIGINS.split(",") if x.strip()]
        return self.ALLOWED_ORIGINS

settings = Settings()
