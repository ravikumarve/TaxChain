import logging
import os
from pydantic_settings import BaseSettings
from pydantic import validator, Field
from functools import lru_cache

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Required
    DATABASE_URL: str
    SECRET_KEY: str = Field(..., min_length=32)

    # Optional with defaults
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: str = "http://localhost:3000"
    DEBUG: bool = False

    # Chain API keys (optional at dev, required in prod)
    ETHERSCAN_API_KEY: str = ""
    BSCSCAN_API_KEY: str = ""
    POLYGONSCAN_API_KEY: str = ""
    SOLSCAN_API_KEY: str = ""
    COINGECKO_API_KEY: str = ""

    # Payment provider keys
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    LEMONSQUEEZY_API_KEY: str = ""
    LEMONSQUEEZY_WEBHOOK_SECRET: str = ""

    # Payment plan IDs (parameterized — set via .env or defaults)
    RAZORPAY_PLAN_STARTER: str = "plan_starter_monthly"
    RAZORPAY_PLAN_PRO: str = "plan_pro_monthly"
    LEMONSQUEEZY_VARIANT_STARTER: str = "variant_starter_monthly"
    LEMONSQUEEZY_VARIANT_PRO: str = "variant_pro_monthly"
    LEMONSQUEEZY_STORE_ID: str = "1"

    class Config:
        env_file = ".env"

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long for security"
            )
        return v

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql", "sqlite")):
            raise ValueError(
                "DATABASE_URL must start with postgresql:// or sqlite:///"
            )
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings — validates on first call."""
    settings = Settings()

    # Warn about missing production secrets (not fail — dev is fine)
    app_env = os.getenv("APP_ENV", "dev")
    if app_env == "prod":
        required_keys = [
            ("RAZORPAY_KEY_SECRET", settings.RAZORPAY_KEY_SECRET),
            ("LEMONSQUEEZY_API_KEY", settings.LEMONSQUEEZY_API_KEY),
            ("RAZORPAY_KEY_ID", settings.RAZORPAY_KEY_ID),
        ]
        for name, value in required_keys:
            if not value:
                logger.warning(
                    "PRODUCTION WARNING: %s is not set — payments will fail", name
                )

    return settings


settings = get_settings()
