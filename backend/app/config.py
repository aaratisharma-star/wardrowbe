from functools import lru_cache

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Wardrowbe"
    debug: bool = False
    secret_key: str = Field(default="change-me-in-production")

    # CORS
    cors_origins: list[str] = Field(default=["http://localhost:3000"])

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://wardrobe:wardrobe@localhost:5432/wardrobe"
    )
    database_echo: bool = False

    # Redis
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")

    # Authentication (Authentik)
    authentik_url: str | None = None
    authentik_client_id: str | None = None
    authentik_client_secret: str | None = None

    # Forward Auth (TinyAuth, Authelia, etc.)
    # When True, trusts Remote-User/Remote-Email headers from proxy
    auth_trust_header: bool = Field(default=False)

    # AI Service (OpenAI-compatible API - supports OpenAI, Ollama, LocalAI, etc.)
    ai_base_url: str = Field(default="")
    ai_api_key: str | None = Field(default=None)  # API key for authenticated AI endpoints
    ai_vision_model: str = Field(default="gpt-4o")  # For image analysis
    ai_text_model: str = Field(default="gpt-4o")  # For text generation (recommendations)
    ai_timeout: int = Field(default=120)
    ai_max_retries: int = Field(default=3)

    # Weather
    openmeteo_url: str = Field(default="https://api.open-meteo.com/v1")

    # Notifications - default ntfy channel (used when user has none configured)
    ntfy_server: str | None = None
    ntfy_topic: str | None = None
    ntfy_token: str | None = None
    # Legacy/other providers
    mattermost_webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None

    # Storage
    storage_path: str = Field(default="/data/wardrobe")
    max_upload_size_mb: int = Field(default=10)

    # Image processing
    thumbnail_size: int = 400
    medium_size: int = 800
    original_max_size: int = 2400
    image_quality: int = 90


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
