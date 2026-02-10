from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./market_intelligence.db"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_CORS_ORIGINS: str = "http://localhost:3000,https://*.vercel.app,https://*.railway.app"

    SCRAPING_INTERVAL_HOURS: int = 12
    SCRAPING_RATE_LIMIT_SECONDS: float = 2.0
    SCRAPING_TIMEOUT_SECONDS: int = 30
    SCRAPING_MAX_RETRIES: int = 3

    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    LOG_LEVEL: str = "INFO"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
