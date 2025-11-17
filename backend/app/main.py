from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.middleware import setup_middleware
from app.api.routes import documents, health
from app.core.database import engine, Base
import os

# Initialize logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    json_logs=settings.JSON_LOGS,
    max_bytes=settings.LOG_MAX_BYTES,
    backup_count=settings.LOG_BACKUP_COUNT
)

logger = get_logger(__name__)

# Создание приложения FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Setup custom middleware (rate limiting, logging, security headers)
setup_middleware(app, enable_rate_limiting=settings.ENABLE_RATE_LIMITING)


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    logger.info("Application startup initiated")

    try:
        # Создание директорий для загрузок и выгрузок
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        logger.info(f"Created directories: {settings.UPLOAD_DIR}, {settings.OUTPUT_DIR}")

        # Создание таблиц в базе данных
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Application startup failed: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке приложения"""
    logger.info("Application shutdown initiated")

    try:
        await engine.dispose()
        logger.info("Database connections closed")
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


# Подключение роутеров
app.include_router(
    documents.router,
    prefix=f"{settings.API_V1_STR}/documents",
    tags=["documents"]
)

app.include_router(
    health.router,
    tags=["health"]
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    logger.info("Root endpoint accessed")
    return {
        "message": "GOST Document Formatter API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }
