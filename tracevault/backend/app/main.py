"""
TraceVault FastAPI Application Entry Point
Configures middleware, routers, health endpoints, and startup/shutdown hooks.
"""
from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database.engine import check_database_health, engine

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown hooks."""
    settings = get_settings()
    logger.info("TraceVault starting up", version=settings.APP_VERSION, env=settings.APP_ENV)

    # Ensure storage directories exist
    settings.ensure_storage_dirs()

    # Initialize Qdrant collections
    try:
        from app.ai.embeddings.qdrant_client import initialize_qdrant_collections
        await initialize_qdrant_collections()
        logger.info("Qdrant collections initialized")
    except Exception as exc:
        logger.warning("Qdrant initialization failed", error=str(exc))

    logger.info("TraceVault ready to accept requests")
    yield

    # Shutdown
    logger.info("TraceVault shutting down")
    await engine.dispose()
    logger.info("Database connections closed")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="TraceVault API",
        description=(
            "Secure AI-Powered Multilingual Call Intelligence & Investigation Platform. "
            "Enterprise-grade audio analysis, forensic evidence management, and investigation intelligence."
        ),
        version=settings.APP_VERSION,
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # --------------------------------------------------------
    # Middleware Stack (order matters — outer to inner)
    # --------------------------------------------------------

    # 1. CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
    )

    # 2. GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1024)

    # 3. Request ID and logging middleware
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                request_id=request_id,
            )
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                duration_ms=round(duration_ms, 2),
                request_id=request_id,
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "detail": "An unexpected error occurred. Please try again or contact support.",
                },
                headers={"X-Request-ID": request_id},
            )

    # 4. Security headers middleware
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # --------------------------------------------------------
    # API Routers
    # --------------------------------------------------------
    from app.api.v1.routes import auth as auth_router
    from app.api.v1.routes import users as users_router
    from app.api.v1.routes import cases as cases_router
    from app.api.v1.routes import recordings as recordings_router
    from app.api.v1.routes import transcripts as transcripts_router
    from app.api.v1.routes import intelligence as intelligence_router
    from app.api.v1.routes import search as search_router
    from app.api.v1.routes import reports as reports_router
    from app.api.v1.routes import evidence as evidence_router
    from app.api.v1.routes import analytics as analytics_router
    from app.api.v1.routes import notifications as notifications_router
    from app.api.v1.routes import settings as settings_router
    from app.api.v1.routes import audit as audit_router
    from app.api.v1.routes import copilot as copilot_router

    api_prefix = "/api/v1"
    app.include_router(auth_router.router, prefix=api_prefix)
    app.include_router(users_router.router, prefix=api_prefix)
    app.include_router(cases_router.router, prefix=api_prefix)
    app.include_router(recordings_router.router, prefix=api_prefix)
    app.include_router(transcripts_router.router, prefix=api_prefix)
    app.include_router(intelligence_router.router, prefix=api_prefix)
    app.include_router(search_router.router, prefix=api_prefix)
    app.include_router(reports_router.router, prefix=api_prefix)
    app.include_router(evidence_router.router, prefix=api_prefix)
    app.include_router(analytics_router.router, prefix=api_prefix)
    app.include_router(notifications_router.router, prefix=api_prefix)
    app.include_router(settings_router.router, prefix=api_prefix)
    app.include_router(audit_router.router, prefix=api_prefix)
    app.include_router(copilot_router.router, prefix=api_prefix)

    # --------------------------------------------------------
    # Health Check Endpoints
    # --------------------------------------------------------
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        """Basic health check — returns 200 if API is running."""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
        }

    @app.get("/health/detailed", tags=["Health"])
    async def detailed_health_check() -> dict:
        """Detailed health check including all dependencies."""
        checks: dict = {}

        # Database
        db_health = await check_database_health()
        checks["database"] = db_health

        # Redis
        try:
            import redis.asyncio as aioredis
            r = aioredis.from_url(settings.redis.REDIS_URL)
            await r.ping()
            await r.aclose()
            checks["redis"] = {"status": "healthy"}
        except Exception as exc:
            checks["redis"] = {"status": "unhealthy", "details": str(exc)}

        # Qdrant
        try:
            from qdrant_client import AsyncQdrantClient
            qc = AsyncQdrantClient(url=settings.ai.QDRANT_URL)
            await qc.get_collections()
            checks["qdrant"] = {"status": "healthy"}
        except Exception as exc:
            checks["qdrant"] = {"status": "unhealthy", "details": str(exc)}

        overall = "healthy" if all(
            v.get("status") == "healthy" for v in checks.values()
        ) else "degraded"

        return {
            "status": overall,
            "version": settings.APP_VERSION,
            "checks": checks,
        }

    return app


# Create application instance
app = create_application()
