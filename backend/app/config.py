from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Chain APIs
    ETHERSCAN_API_KEY: str
    BSCSCAN_API_KEY: str
    POLYGONSCAN_API_KEY: str
    SOLSCAN_API_KEY: str

    # Payments
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    LEMONSQUEEZY_API_KEY: str
    LEMONSQUEEZY_WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
