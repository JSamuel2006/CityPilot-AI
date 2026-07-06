"""
Centralised application configuration.
Reads from environment variables / .env file using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    # ── Database ────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+psycopg://username:password@localhost:5432/citypilot"
    GEMINI_API_KEY: str = ""

    # ── Security ─────────────────────────────────────────────────────
    SECRET_KEY: str = "changeme-replace-in-production"

    # Connection-pool tuning
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ── CORS ─────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins, or "*" for development.
    # In production set to your Vercel frontend URL, e.g.:
    #   CORS_ORIGINS=https://citypilot.vercel.app
    CORS_ORIGINS: str = "*"

    # ── Uploads ─────────────────────────────────────────────────────
    # /tmp/uploads works on Render (ephemeral FS) and locally.
    # For persistent storage switch to a cloud bucket.
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: set[str] = {
        ".pdf", ".doc", ".docx", ".txt", ".csv",
        ".xls", ".xlsx", ".json", ".md", ".png",
        ".jpg", ".jpeg",
    }

    # ── App metadata ────────────────────────────────────────────────
    APP_TITLE: str = "CityPilot AI API"
    APP_VERSION: str = "1.0.0-beta"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()
