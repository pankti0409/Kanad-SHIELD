"""
TraceVault Settings API Routes
User settings read and update.
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.auth.dependencies import CurrentUser

router = APIRouter(prefix="/settings", tags=["Settings"])


class UserSettingsResponse(BaseModel):
    theme: str
    language: str
    notifications_enabled: bool
    email_alerts: bool
    timezone: str


class UserSettingsUpdateRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    email_alerts: Optional[bool] = None
    timezone: Optional[str] = None


@router.get("", response_model=UserSettingsResponse, summary="Get user settings")
async def get_settings(current_user: CurrentUser) -> UserSettingsResponse:
    """Return the current user settings."""
    return UserSettingsResponse(
        theme="dark",
        language=current_user.language or "en",
        notifications_enabled=True,
        email_alerts=False,
        timezone=current_user.timezone or "UTC",
    )


@router.patch("", response_model=UserSettingsResponse, summary="Update user settings")
async def update_settings(
    body: UserSettingsUpdateRequest,
    current_user: CurrentUser,
) -> UserSettingsResponse:
    """Update current user settings."""
    return UserSettingsResponse(
        theme=body.theme or "dark",
        language=body.language or current_user.language or "en",
        notifications_enabled=body.notifications_enabled if body.notifications_enabled is not None else True,
        email_alerts=body.email_alerts if body.email_alerts is not None else False,
        timezone=body.timezone or current_user.timezone or "UTC",
    )
