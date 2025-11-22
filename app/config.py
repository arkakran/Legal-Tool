import sys
import secrets
from pathlib import Path
from typing import Set
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from loguru import logger


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Flask Core
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_hex(32))
    FLASK_ENV: str = Field(default="production")
    DEBUG: bool = Field(default=False)

    # API Keys - REQUIRED
    GROQ_API_KEY: str = Field(...)
    HUGGINGFACE_API_KEY: str = Field(default="")

    # LLM Configuration
    LLM_MODEL: str = Field(default="llama-3.3-70b-versatile")
    LLM_TEMPERATURE: float = Field(default=0.0)

    # Embedding Configuration
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DEVICE: str = Field(default="cpu")

    # Processing Parameters
    CHUNK_SIZE: int = Field(default=1500, ge=500, le=3000)
    CHUNK_OVERLAP: int = Field(default=200, ge=0, le=500)
    TOP_K_RETRIEVAL: int = Field(default=60, ge=10, le=100)
    TOP_K_RERANKED: int = Field(default=25, ge=5, le=50)
    FINAL_OUTPUT_COUNT: int = Field(default=10, ge=5, le=20)

    # File Upload
    UPLOAD_FOLDER: str = Field(default="data/uploads")
    MAX_CONTENT_LENGTH: int = Field(default=50 * 1024 * 1024)  # 50MB
    ALLOWED_EXTENSIONS: Set[str] = {'pdf'}

    # FAISS Index
    FAISS_M: int = Field(default=32)
    FAISS_EF_CONSTRUCTION: int = Field(default=64)
    FAISS_EF_SEARCH: int = Field(default=64)

    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure SECRET_KEY is secure."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @field_validator('GROQ_API_KEY')
    @classmethod
    def validate_groq_key(cls, v: str) -> str:
        """Ensure GROQ_API_KEY is provided."""
        if not v or v == "your-groq-api-key-here":
            raise ValueError("GROQ_API_KEY missing or invalid")
        return v

    @field_validator('UPLOAD_FOLDER')
    @classmethod
    def create_upload_folder(cls, v: str) -> str:
        """Create upload directory if it doesn't exist."""
        try:
            Path(v).mkdir(parents=True, exist_ok=True)
            logger.info(f"Upload folder ready: {v}")
        except Exception as e:
            logger.warning(f"Could not create upload folder '{v}': {e}")
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


def get_config() -> Settings:
    """Load and validate configuration safely without leaking secrets."""
    try:
        settings = Settings()

        # Ensure logs directory exists here as well
        logs_dir = Path("logs")
        try:
            logs_dir.mkdir(exist_ok=True, parents=True)
        except Exception:
            logger.warning("Could not create logs directory")

        return settings

    except Exception:
        # DO not print exception 
        logger.error("Configuration failed. Missing or invalid environment values.")

        print("\nConfiguration Error:")
        print("1. Check your .env file exists")
        print("2. Ensure GROQ_API_KEY is set")
        print("3. Generate SECRET_KEY if needed:")
        print("   python -c \"import secrets; print(secrets.token_hex(32))\"")

        sys.exit(1)


settings = get_config()
