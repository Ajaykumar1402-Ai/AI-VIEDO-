from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://storytelling_app:storytelling_pass_2026@localhost:5432/storytelling_db",
        description="SQLAlchemy PostgreSQL Connection URL"
    )
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
        default="gemini-2.5-flash",
        description="Gemini model identifier"
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
