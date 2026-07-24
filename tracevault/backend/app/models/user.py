"""
TraceVault User & Authentication Models
All authentication-related database models.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Enum,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BaseModel, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case


# ============================================================
# Enums
# ============================================================

class UserRole(str, PyEnum):
    """User roles with increasing privilege levels."""
    SYSTEM_ADMIN = "system_admin"
    SUPERVISOR = "supervisor"
    SENIOR_INVESTIGATOR = "senior_investigator"
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    LEGAL_OFFICER = "legal_officer"
    READ_ONLY = "read_only"


class UserStatus(str, PyEnum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    LOCKED = "locked"


# ============================================================
# User Model
# ============================================================

class User(BaseModel, SoftDeleteMixin):
    """
    Core user model for TraceVault.
    Passwords are NEVER stored in plaintext — always Argon2 hashed.
    """
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("username", name="uq_users_username"),
    )

    # Identity
    username: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    badge_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Authentication
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum"),
        nullable=False,
        default=UserRole.READ_ONLY,
        index=True,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status_enum"),
        nullable=False,
        default=UserStatus.PENDING_VERIFICATION,
        index=True,
    )

    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Profile
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # Metadata
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE and not self.is_deleted

    @property
    def is_locked(self) -> bool:
        if self.locked_until is None:
            return False
        return datetime.now(timezone.utc) < self.locked_until

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.SYSTEM_ADMIN

    @property
    def can_upload(self) -> bool:
        return self.role in (
            UserRole.SYSTEM_ADMIN,
            UserRole.SUPERVISOR,
            UserRole.SENIOR_INVESTIGATOR,
            UserRole.INVESTIGATOR,
        )

    @property
    def can_export(self) -> bool:
        return self.role in (
            UserRole.SYSTEM_ADMIN,
            UserRole.SUPERVISOR,
            UserRole.SENIOR_INVESTIGATOR,
            UserRole.INVESTIGATOR,
            UserRole.ANALYST,
            UserRole.LEGAL_OFFICER,
        )

    @property
    def can_approve(self) -> bool:
        return self.role in (
            UserRole.SYSTEM_ADMIN,
            UserRole.SUPERVISOR,
            UserRole.SENIOR_INVESTIGATOR,
        )

    @property
    def can_archive(self) -> bool:
        return self.role in (UserRole.SYSTEM_ADMIN, UserRole.SUPERVISOR)

    @property
    def can_manage_users(self) -> bool:
        return self.role == UserRole.SYSTEM_ADMIN


# ============================================================
# Session Model
# ============================================================

class UserSession(BaseModel):
    """Active user session tracking."""
    __tablename__ = "user_sessions"
    __table_args__ = (
        
        
        
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_token_hash: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    operating_system: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="sessions")


# ============================================================
# Refresh Token Model
# ============================================================

class RefreshToken(BaseModel):
    """Refresh token storage for JWT rotation."""
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        
        
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    jti: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)  # JWT ID
    device_info: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    @property
    def is_valid(self) -> bool:
        return (
            not self.is_revoked
            and datetime.now(timezone.utc) < self.expires_at
        )


# ============================================================
# Password Reset Token
# ============================================================

class PasswordResetToken(BaseModel):
    """One-time password reset token."""
    __tablename__ = "password_reset_tokens"
    __table_args__ = (
        
        
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="password_reset_tokens")

    @property
    def is_valid(self) -> bool:
        return (
            not self.is_used
            and datetime.now(timezone.utc) < self.expires_at
        )


