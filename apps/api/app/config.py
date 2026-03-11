from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve .env from project root (two levels up from apps/api/)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent / ".env"


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./alpha_copilot.db"
    anthropic_api_key: str = ""
    worker_pool_size: int = 4
    model_name: str = "claude-sonnet-4-5-20250514"

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"}
