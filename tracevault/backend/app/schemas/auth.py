"""
TraceVault Pydantic Schemas — Authentication
Request/response schemas for all authentication endpoints.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Login with email/username + password."""
    identifier: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Email address or username",
        examples=["investigator@agency.gov"],
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description="Account password",
    )
    remember_me: bool = Field(default=False)
    device_info: Optional[str] = Field(default=None, max_length=512)


class LoginResponse(BaseModel):
    """Successful login response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: "UserBriefResponse"


class RefreshRequest(BaseModel):
    """Refresh token rotation request."""
    refresh_token: str = Field(..., min_length=10)


class RefreshResponse(BaseModel):
    """New token pair after refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LogoutRequest(BaseModel):
    """Logout request — optionally include refresh token for full revocation."""
    refresh_token: Optional[str] = None
    logout_all_devices: bool = False


class PasswordResetRequestBody(BaseModel):
    """Initiate password reset via email."""
    email: EmailStr


class PasswordResetComplete(BaseModel):
    """Complete password reset with token + new password."""
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=12, max_length=512)
    confirm_password: str = Field(..., min_length=12, max_length=512)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        from app.security.password import validate_password_policy
        is_valid, errors = validate_password_policy(v)
        if not is_valid:
            raise ValueError(". ".join(errors))
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match.")
        return v


class ChangePasswordRequest(BaseModel):
    """Change password while authenticated."""
    current_password: str = Field(..., min_length=1, max_length=512)
    new_password: str = Field(..., min_length=12, max_length=512)
    confirm_password: str = Field(..., min_length=12, max_length=512)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        from app.security.password import validate_password_policy
        is_valid, errors = validate_password_policy(v)
        if not is_valid:
            raise ValueError(". ".join(errors))
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match.")
        return v


# ============================================================
# User Schemas
# ============================================================

class UserBriefResponse(BaseModel):
    """Minimal user info for embedding in other responses."""
    id: UUID
    username: str
    email: str
    full_name: str
    role: str
    status: str
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class UserDetailResponse(BaseModel):
    """Full user detail response."""
    id: UUID
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    badge_number: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    organization: Optional[str] = None
    role: str
    status: str
    avatar_url: Optional[str] = None
    timezone: str
    language: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserCreateRequest(BaseModel):
    """Create a new user (admin only)."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=12, max_length=512)
    role: str = Field(default="read_only")
    phone: Optional[str] = Field(default=None, max_length=20)
    badge_number: Optional[str] = Field(default=None, max_length=50)
    department: Optional[str] = Field(default=None, max_length=255)
    designation: Optional[str] = Field(default=None, max_length=255)
    organization: Optional[str] = Field(default=None, max_length=255)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_.-]+$", v):
            raise ValueError("Username can only contain letters, digits, dots, hyphens, and underscores.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        from app.security.password import validate_password_policy
        is_valid, errors = validate_password_policy(v)
        if not is_valid:
            raise ValueError(". ".join(errors))
        return v


class UserUpdateRequest(BaseModel):
    """Update user profile."""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    badge_number: Optional[str] = Field(default=None, max_length=50)
    department: Optional[str] = Field(default=None, max_length=255)
    designation: Optional[str] = Field(default=None, max_length=255)
    organization: Optional[str] = Field(default=None, max_length=255)
    timezone: Optional[str] = Field(default=None, max_length=50)
    language: Optional[str] = Field(default=None, max_length=10)


class UserListResponse(BaseModel):
    """Paginated user list."""
    items: list[UserDetailResponse]
    total: int
    page: int
    page_size: int
    pages: int

    model_config = {"from_attributes": True}


class PaginationParams(BaseModel):
    """Common pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class MessageResponse(BaseModel):
    """Generic success message response."""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    request_id: Optional[str] = None
