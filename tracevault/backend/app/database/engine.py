"""
TraceVault Database Configuration
SQLAlchemy 2 async engine, session factory, and base model.
"""
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from app.config import get_settings


def _build_engine() -> AsyncEngine:
    """Build the async SQLAlchemy engine with production-grade settings."""
    settings = get_settings()
    db_url = settings.db.DATABASE_URL

    pool_kwargs: dict = {}
    if settings.is_production:
        pool_kwargs = {
            "poolclass": AsyncAdaptedQueuePool,
            "pool_size": 20,
            "max_overflow": 10,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
    else:
        pool_kwargs = {
            "poolclass": NullPool,
        }

    return create_async_engine(
        db_url,
        echo=settings.is_development,
        **pool_kwargs,
    )


# Module-level engine (singleton)
engine: AsyncEngine = _build_engine()

# Session factory
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: yields an async database session.
    Session is automatically committed on success, rolled back on error.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_database_health() -> dict[str, str]:
    """Check database connectivity. Used by health endpoint."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "details": "PostgreSQL connection OK"}
    except Exception as exc:
        return {"status": "unhealthy", "details": str(exc)}
