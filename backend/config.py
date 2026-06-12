"""
Application configuration using pydantic-settings.

Loads settings from environment variables and a .env file located
at the project root. Provides typed, validated configuration for
the entire application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings.

    All values can be overridden via environment variables or a `.env` file
    placed next to this module's parent directory.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Core ────────────────────────────────────────────────────────────
    APP_NAME: str = "AI Wealth Advisor"
    DEBUG: bool = False

    # ── AI / LLM ────────────────────────────────────────────────────────
    MISTRAL_API_KEY: str = ""

    # ── Database ────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./data/wealth_advisor.db"

    # ── File storage ────────────────────────────────────────────────────
    UPLOAD_DIR: str = "./storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # ── Vector DB ───────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"


# Singleton instance used across the application.
settings = Settings()
