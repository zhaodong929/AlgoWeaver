"""Application configuration loaded from environment variables and .env."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Environment variables use the ALGOWEAVER_ prefix."""

    model_config = SettingsConfigDict(
        env_prefix="ALGOWEAVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AlgoWeaver"
    app_env: Literal["development", "test", "production"] = "development"
    llm_mode: Literal["mock", "litellm"] = "mock"
    llm_model: str | None = None
    code_llm_model: str | None = None
    llm_api_key: SecretStr | None = None
    llm_api_base: str | None = None
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    llm_timeout_seconds: float = Field(default=60.0, gt=0.0, le=600.0)
    embedding_mode: Literal["mock", "dashscope"] = "mock"
    embedding_model: str = "text-embedding-v4"
    embedding_api_key: SecretStr | None = None
    embedding_api_base: str = "https://dashscope.aliyuncs.com/api/v1"
    embedding_timeout_seconds: float = Field(default=60.0, gt=0.0, le=600.0)
    reranker_mode: Literal["mock", "dashscope"] = "mock"
    reranker_model: str = "qwen3-rerank"
    reranker_api_key: SecretStr | None = None
    reranker_api_base: str = "https://dashscope.aliyuncs.com/api/v1"
    reranker_timeout_seconds: float = Field(default=60.0, gt=0.0, le=600.0)
    max_input_chars: int = Field(default=40_000, ge=1_000, le=500_000)
    registry_path: Path = Path("data/processed/capabilities.sqlite3")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
