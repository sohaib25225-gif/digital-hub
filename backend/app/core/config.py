from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database (using psycopg3 driver)
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost:5432/digital_hub"

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # JWT (for future phases)
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Supabase Storage
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # File Upload Limits (in MB)
    MAX_FILE_SIZE_MB: int = 100
    MAX_THUMBNAIL_SIZE_MB: int = 5

    # Safepay Payment Integration (Phase 6)
    SAFEPAY_PUBLIC_KEY: str = ""
    SAFEPAY_SECRET_KEY: str = ""
    SAFEPAY_WEBHOOK_SECRET: str = ""
    SAFEPAY_ENVIRONMENT: str = "sandbox"
    SAFEPAY_BASE_URL: str = "https://sandbox.api.getsafepay.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )


settings = Settings()
