from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_KEY: str = "default_dev_key"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT: str = "100/minute"
    CACHE_REFRESH_INTERVAL: int = 5
    QUEUE_MAX_SIZE: int = 10000
    CORS_ORIGINS: List[str] = ["*"]
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    DATABASE_URL: str = "sqlite:///data/firewall.db"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
