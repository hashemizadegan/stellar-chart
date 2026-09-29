from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Stellar Chart"
    base_url: str = "http://localhost:8000"
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./astro.db"

    subscription_price_usd: float = 9.99
    subscription_days: int = 30
    questions_per_day: int = 5

    nowpayments_api_key: str = ""
    nowpayments_ipn_secret: str = ""
    pay_currency: str = "usdttrc20"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5-5"

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    telegram_webhook_secret: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    se_ephe_path: str = ""
    geocoder_user_agent: str = "stellar-chart-app/1.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
