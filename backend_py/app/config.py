from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os

class Settings(BaseSettings):
    DATABASE_URL: str = Field(
        default="",
        description="SQLAlchemy PostgreSQL Connection URL (Supabase)"
    )

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """
        Normalize database URLs to use the psycopg 3 driver dialect.
        Supabase URLs often begin with postgresql:// or postgres://.
        SQLAlchemy requires postgresql+psycopg:// since only psycopg v3 is installed.
        """
        if not v:
            return v
        v = v.strip()
        if v.startswith("postgres://"):
            return "postgresql+psycopg://" + v[len("postgres://"):]
        if v.startswith("postgresql://") and not v.startswith("postgresql+"):
            return "postgresql+psycopg://" + v[len("postgresql://"):]
        return v
    FRONTEND_ORIGIN: str = Field(
        default="http://localhost:3000",
        description="Allowed frontend origin for CORS"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment: development or production"
    )
    JWT_SECRET: str = Field(
        default="sivacine_storytelling_super_secret_jwt_key_2026",
        description="Secret key for signing session JWT tokens"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7

    # Gemini LLM Integration
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API Key"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-3.5-flash",
        description="Gemini model identifier"
    )

    # Supabase Storage Configuration
    SUPABASE_URL: str = Field(
        default="",
        description="Supabase Project URL (e.g. https://your-project.supabase.co)"
    )
    SUPABASE_KEY: str = Field(
        default="",
        description="Supabase API key (service_role or anon)"
    )
    SUPABASE_SCRIPTS_BUCKET: str = Field(
        default="scripts",
        description="Supabase Storage bucket name for JSON scripts"
    )

    # Output & Artifacts Storage
    OUTPUT_ROOT: str = Field(
        default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"),
        description="Absolute filesystem root for exported stories and audio artifacts"
    )

    # TTS Settings
    TTS_PROVIDER: str = Field(
        default="mock",
        description="TTS Engine Provider: mock, kokoro, vibevoice, edge, system"
    )
    TTS_MODEL_PATH: str = Field(
        default="",
        description="Local path to self-hosted TTS model weights (Thunder Compute / Local GPU)"
    )

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
