from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "LUMIRA"
    DATABASE_URL: str
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    JWT_SECRET: str = "default_secret"
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()
