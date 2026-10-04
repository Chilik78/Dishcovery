from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mealdb_base_url: str = "https://www.themealdb.com/api/json/v1/1"
    mealdb_api_key: str = "1"          # публичный тестовый ключ
    cache_ttl: int = 3600              # 1 час
    http_timeout: float = 10.0
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_prefix = "DISHCOVERY_"

settings = Settings()