"""
TraceVault SQLAlchemy Base Model
All database models inherit from this base.
Includes UUID primary key, timestamps, and soft delete support.
Uses generic SQLAlchemy types for cross-database compatibility (SQLite dev, PostgreSQL prod).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, String, func, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Cross-database UUID type: PostgreSQL uses native UUID, SQLite uses String(36)
try:
    from sqlalchemy.dialects.postgresql import UUID as PgUUID
    _UUID_TYPE = PgUUID(as_uuid=True)
except Exception:
    _UUID_TYPE = String(36)  # type: ignore[assignment]


def _uuid_col(**kwargs):
    """Return a UUID mapped_column compatible with both PostgreSQL and SQLite."""
    return mapped_column(String(36), **kwargs)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    type_annotation_map: dict[Any, Any] = {
        str: String,
        dict: JSON,
        list: JSON,
    }


class TimestampMixin:
    """Mixin adding created_at and updated_at to models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin adding soft delete capability."""

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,
    )

    def soft_delete(self) -> None:
        """Mark record as deleted without removing from database."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)


class BaseModel(TimestampMixin, Base):
    """
    Abstract base for all TraceVault database models.
    Provides: UUID primary key (String), created_at, updated_at.
    Works with both SQLite (dev) and PostgreSQL (prod).
    """

    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
