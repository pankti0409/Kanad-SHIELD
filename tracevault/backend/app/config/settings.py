"""
TraceVault Backend Configuration
Central configuration management using Pydantic Settings.
All values loaded from environment variables.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "tracevault"
    POSTGRES_USER: str = "tracevault"
    POSTGRES_PASSWORD: SecretStr = Field(...)
    DATABASE_URL: Optional[str] = None

    @model_validator(mode="after")
    def build_database_url(self) -> "DatabaseSettings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD.get_secret_value()}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[SecretStr] = None
    REDIS_URL: Optional[str] = None
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @model_validator(mode="after")
    def build_redis_urls(self) -> "RedisSettings":
        password_part = (
            f":{self.REDIS_PASSWORD.get_secret_value()}@"
            if self.REDIS_PASSWORD
            else ""
        )
        base = f"redis://{password_part}{self.REDIS_HOST}:{self.REDIS_PORT}"
        if not self.REDIS_URL:
            self.REDIS_URL = f"{base}/0"
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = f"{base}/1"
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = f"{base}/2"
        return self


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    JWT_SECRET: SecretStr = Field(...)
    JWT_REFRESH_SECRET: SecretStr = Field(...)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Whisper
    WHISPER_MODEL: str = "large-v3"
    WHISPER_MODEL_SIZE: str = "large-v3"  # Alias used in some code paths
    WHISPER_DEVICE: str = "auto"  # auto, cuda, cpu
    WHISPER_COMPUTE_TYPE: str = "float16"

    # Embedding
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_BATCH_SIZE: int = 32

    # Gemini (primary LLM for NER + threat analysis)
    GEMINI_API_KEY: Optional[str] = None
    LLM_API_KEY: Optional[str] = None  # Alias

    # Ollama
    OLLAMA_HOST: str = "localhost"
    OLLAMA_PORT: int = 11434
    OLLAMA_BASE_URL: Optional[str] = None
    OLLAMA_MODEL: str = "qwen2.5:7b-instruct"

    # NER
    NER_MODEL: str = "knowledgator/gliner-multitask-large-v0.5"
    GLINER_MODEL_NAME: str = "knowledgator/gliner-multitask-large-v0.5"

    # Emotion
    EMOTION_MODEL: str = "speechbrain/emotion-recognition-wav2vec2-IEMOCAP"

    # HuggingFace
    HF_TOKEN: Optional[SecretStr] = None

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_URL: Optional[str] = None

    # Confidence thresholds
    ENTITY_CONFIDENCE_THRESHOLD: float = 0.5
    THREAT_CONFIDENCE_THRESHOLD: float = 0.6
    EMOTION_CONFIDENCE_THRESHOLD: float = 0.5
    SEARCH_SIMILARITY_THRESHOLD: float = 0.7

    @model_validator(mode="after")
    def build_urls(self) -> "AISettings":
        # Sync GEMINI_API_KEY from LLM_API_KEY alias if not set
        if not self.GEMINI_API_KEY and self.LLM_API_KEY:
            self.GEMINI_API_KEY = self.LLM_API_KEY
        if not self.OLLAMA_BASE_URL:
            self.OLLAMA_BASE_URL = f"http://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}"
        if not self.QDRANT_URL:
            self.QDRANT_URL = f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"
        return self


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    UPLOAD_DIRECTORY: str = "./storage/uploads"
    PROCESSED_DIRECTORY: str = "./storage/processed"
    REPORT_DIRECTORY: str = "./storage/reports"
    TEMP_DIRECTORY: str = "./storage/temp"
    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_AUDIO_FORMATS: str = "wav,mp3,m4a,aac,ogg,flac,opus"

    @property
    def allowed_formats_list(self) -> list[str]:
        return [fmt.strip() for fmt in self.ALLOWED_AUDIO_FORMATS.split(",")]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


class SecuritySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    AES_SECRET_KEY: SecretStr = Field(...)
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 30
    PASSWORD_MIN_LENGTH: int = 12
    SESSION_IDLE_TIMEOUT_MINUTES: int = 60
    CORS_ORIGINS: Optional[str] = None  # JSON string from env
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:80"]

    @model_validator(mode="after")
    def parse_cors_origins(self) -> "SecuritySettings":
        import json
        if self.CORS_ORIGINS:
            try:
                parsed = json.loads(self.CORS_ORIGINS)
                if isinstance(parsed, list):
                    self.ALLOWED_ORIGINS = parsed
            except Exception:
                pass
        return self


class Settings(BaseSettings):
    """Master application settings — loads all sub-settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Application
    APP_ENV: str = "development"
    APP_NAME: str = "TraceVault"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: SecretStr = Field(...)
    DEBUG: bool = False

    # Sub-settings (composed)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    ai: AISettings = Field(default_factory=AISettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    def ensure_storage_dirs(self) -> None:
        """Create storage directories if they don't exist."""
        for directory in [
            self.storage.UPLOAD_DIRECTORY,
            self.storage.PROCESSED_DIRECTORY,
            self.storage.REPORT_DIRECTORY,
            self.storage.TEMP_DIRECTORY,
        ]:
            Path(directory).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings. Call once at startup."""
    return Settings()
