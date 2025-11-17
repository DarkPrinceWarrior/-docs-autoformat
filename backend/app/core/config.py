from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GOST Document Formatter"
    VERSION: str = "1.0.0"

    # AI Provider Settings
    AI_PROVIDER: str = "claude"  # claude, ollama, custom

    # Claude API Settings
    CLAUDE_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    # Custom API Settings (OpenAI-compatible)
    CUSTOM_API_BASE_URL: Optional[str] = None
    CUSTOM_API_KEY: Optional[str] = None
    CUSTOM_API_MODEL: str = "gpt-3.5-turbo"

    # Database
    POSTGRES_USER: str = "gost_user"
    POSTGRES_PASSWORD: str = "gost_password"
    POSTGRES_DB: str = "gost_formatter"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis & Celery
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    UPLOAD_DIR: str = "/tmp/uploads"
    OUTPUT_DIR: str = "/tmp/outputs"

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = "logs/app.log"
    JSON_LOGS: bool = True  # Use JSON format for structured logging
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # Security & Rate Limiting
    ENABLE_RATE_LIMITING: bool = True  # Enable rate limiting
    RATE_LIMIT_PER_MINUTE: int = 200  # Default rate limit per minute
    ALLOWED_HOSTS: list = ["*"]  # Allowed hosts for production

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
