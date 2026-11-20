from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DISHCOVERY_",
        env_file=Path(__file__).with_name(".env"),
        env_file_encoding="utf-8-sig",
        env_ignore_empty=True,
        extra="ignore",
    )

    mealdb_base_url: str = "https://www.themealdb.com/api/json/v1/1"
    mealdb_api_key: str = "1"          # публичный тестовый ключ
    cache_ttl: int = 3600              # 1 час
    http_timeout: float = 10.0
    recipe_steps_function_id: str = ""
    recipe_steps_function_api_key: SecretStr | None = None
    recipe_steps_use_env_proxy: bool = False
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

settings = Settings()
