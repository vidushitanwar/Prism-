"""
PRISM backend configuration.

All configuration is read from environment variables (see .env.example).
No secrets are hardcoded. By default the app uses a local SQLite file so it
runs immediately with zero external setup; set DATABASE_URL to point at
PostgreSQL for a production-style run.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "PRISM Workforce Intelligence API"
    ENVIRONMENT: str = "development"
    API_PREFIX: str = "/api"

    # Default: local SQLite file, zero external setup required.
    # Example Postgres value:
    # postgresql+psycopg://prism_user:prism_password@localhost:5432/prism
    DATABASE_URL: str = "sqlite:///./data/prism.db"

    # Comma-separated list of allowed origins for CORS.
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174"
    )

    # Reserved for a future natural-language search/explanation layer.
    # Not currently read by any code path — see .env.example.
    ANTHROPIC_API_KEY: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
