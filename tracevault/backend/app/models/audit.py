"""
TraceVault Audit Log & Notification Models
Immutable audit logs, notifications, and system events.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BaseModel


class AuditLog(Base):
    """
    IMMUTABLE audit log entry.
    Every security-sensitive operation must create an audit log.
    Audit logs can NEVER be modified or deleted.
    Uses manual ID instead of inheriting BaseModel to keep absolute control.
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        
        
        
        
        
        
        
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Action
    action: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    action_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(
        String(20), default="info", nullable=False, index=True
    )

    # Resource
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    resource_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    case_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # Result
    result: Mapped[str] = mapped_column(String(20), default="success", nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Timestamp (required, not from mixin — ensuring explicit control)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # def __setattr__(self, name: str, value: object) -> None:
    #     """Prevent modification of critical audit fields after creation."""
    #     if hasattr(self, "id") and name in (
    #         "id", "user_id", "action", "resource_id", "created_at", "ip_address"
    #     ):
    #         # Allow setting once during creation
    #         pass
    #     super().__setattr__(name, value)


class Notification(BaseModel):
    """Real-time notifications for users."""
    __tablename__ = "notifications"
    __table_args__ = (
        
        
        
        
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Resource reference
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    action_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User")


class SystemAlert(BaseModel):
    """System-wide alerts for administrators."""
    __tablename__ = "system_alerts"
    __table_args__ = (
        
        
        
    )

    alert_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    component: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


