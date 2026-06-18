from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.config.settings import settings
from app.core.logging import setup_logging, get_logger
from app.database.base import engine, Base
from app.database.redis import get_redis, close_redis
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.utils.exception_handlers import register_exception_handlers

logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]")

    # Initialize DB tables (migrations should handle schema; this is for new deploys)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Test Redis
    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("Redis connected successfully")
    except Exception as exc:
        logger.warning(f"Redis unavailable (caching disabled): {exc}")

    # Seed demo data (no-op if already seeded)
    from app.scripts.seed import seed_all
    await seed_all()

    logger.info("Application startup complete")
    yield

    # Shutdown
    await close_redis()
    await engine.dispose()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Enterprise-grade Inventory & Order Management System API",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time"],
    )

    # Trusted hosts (skip in dev)
    if settings.is_production:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts_list)

    # GZip
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Request logging
    app.add_middleware(RequestLoggingMiddleware)

    # Routes
    app.include_router(api_router)

    # Exception handlers
    register_exception_handlers(app)

    # Health check endpoints
    @app.get("/health", tags=["Observability"], include_in_schema=False)
    async def health() -> dict:
        return {"status": "healthy", "version": settings.APP_VERSION}

    @app.get("/readiness", tags=["Observability"], include_in_schema=False)
    async def readiness() -> dict:
        from sqlalchemy import text
        from app.database.base import AsyncSessionLocal
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            db_ok = False

        try:
            redis = await get_redis()
            await redis.ping()
            redis_ok = True
        except Exception:
            redis_ok = False

        all_ok = db_ok and redis_ok
        return {
            "status": "ready" if all_ok else "not_ready",
            "checks": {"database": "ok" if db_ok else "error", "redis": "ok" if redis_ok else "error"},
        }

    return app


app = create_app()
