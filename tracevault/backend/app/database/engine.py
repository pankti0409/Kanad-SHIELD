"""
TraceVault Database Configuration
SQLAlchemy 2 async engine, session factory, and base model.
Supports both SQLite (dev) and PostgreSQL (prod) via generic types.
"""
from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from app.config import get_settings

logger = logging.getLogger(__name__)


def _build_engine() -> AsyncEngine:
    """Build the async SQLAlchemy engine with production-grade settings."""
    settings = get_settings()
    db_url = settings.db.DATABASE_URL

    pool_kwargs: dict = {}
    is_sqlite = "sqlite" in db_url.lower()

    if is_sqlite:
        # SQLite: use NullPool (no real connection pooling) and enable WAL mode
        pool_kwargs = {
            "poolclass": NullPool,
            "connect_args": {"check_same_thread": False},
        }
    elif settings.is_production:
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

    engine = create_async_engine(
        db_url,
        echo=settings.is_development and not is_sqlite,  # Don't echo SQLite (too verbose)
        **pool_kwargs,
    )

    # Enable WAL mode on SQLite for better concurrency
    if is_sqlite:
        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


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


async def create_all_tables() -> None:
    """Create all database tables (dev/test only). Called on startup."""
    from app.database.base import Base
    # Import all models to ensure they are registered with Base.metadata
    import app.models.user as user_model
    import app.models.case  # noqa: F401
    import app.models.recording  # noqa: F401
    import app.models.intelligence  # noqa: F401
    import app.models.evidence  # noqa: F401
    import app.models.audit  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified.")

    # Seed fallback user and case in development/local mode to prevent FOREIGN KEY errors on upload
    try:
        from sqlalchemy import select
        import app.models.case as case_model
        async with AsyncSessionLocal() as session:
            fallback_id = "00000000-0000-0000-0000-000000000001"
            res = await session.execute(
                select(user_model.User).where(user_model.User.id == fallback_id)
            )
            existing_user = res.scalar_one_or_none()
            if not existing_user:
                logger.info("Seeding fallback investigator user in development database...")
                user = user_model.User(
                    id=fallback_id,
                    email="investigator@agency.gov",
                    username="investigator",
                    full_name="Senior Investigator Officer",
                    hashed_password="",
                    role=user_model.UserRole.SENIOR_INVESTIGATOR,
                    status=user_model.UserStatus.ACTIVE,
                    department="Law Enforcement & Intelligence",
                    designation="Senior Officer",
                    organization="Crime Branch Agency",
                    is_deleted=False,
                )
                session.add(user)
                await session.commit()
                logger.info("Fallback investigator user seeded.")

            # Seed fallback case
            fallback_case_id = "00000000-0000-0000-0000-000000000000"
            res_case = await session.execute(
                select(case_model.Case).where(case_model.Case.id == fallback_case_id)
            )
            existing_case = res_case.scalar_one_or_none()
            if not existing_case:
                logger.info("Seeding fallback case in development database...")
                case = case_model.Case(
                    id=fallback_case_id,
                    case_number="CASE-TEMP-001",
                    title="Default System Case",
                    description="Fallback case for unassigned intercepts",
                    status=case_model.CaseStatus.OPEN,
                    priority=case_model.CasePriority.MEDIUM,
                    category=case_model.CaseCategory.GENERAL,
                    created_by=fallback_id,
                    is_deleted=False,
                )
                session.add(case)
                await session.commit()
                logger.info("Fallback case seeded.")
    except Exception as exc:
        logger.error(f"Failed to seed fallback objects: {exc}")


async def check_database_health() -> dict[str, str]:
    """Check database connectivity. Used by health endpoint."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "details": "Database connection OK"}
    except Exception as exc:
        return {"status": "unhealthy", "details": str(exc)}
