"""
TraceVault Notifications API Routes
Notification listing and acknowledgment.
"""
from __future__ import annotations
from fastapi import APIRouter, Query
from app.auth.dependencies import CurrentUser

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", summary="List notifications")
async def list_notifications(
    current_user: CurrentUser,
    unread_only: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    """List notifications for the current user."""
    return {"items": [], "total": 0, "unread_count": 0}


@router.post("/{notification_id}/read", summary="Mark notification as read")
async def mark_notification_read(
    notification_id: str,
    current_user: CurrentUser,
) -> dict:
    """Mark a notification as read."""
    return {"id": notification_id, "read": True}


@router.post("/read-all", summary="Mark all notifications as read")
async def mark_all_read(current_user: CurrentUser) -> dict:
    """Mark all notifications for the current user as read."""
    return {"marked_read": 0}
