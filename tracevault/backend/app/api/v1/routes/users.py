"""
TraceVault Users API Routes
User profile read and basic management endpoints.
"""
from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from app.auth.dependencies import CurrentUser, DBSession
from app.models.user import User
from app.schemas.auth import UserDetailResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserDetailResponse, summary="Get current user profile")
async def get_my_profile(current_user: CurrentUser) -> UserDetailResponse:
    """Return the current authenticated user full profile."""
    return UserDetailResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserDetailResponse, summary="Get user by ID")
async def get_user(
    user_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> UserDetailResponse:
    """Get user profile by ID. Accessible by supervisors and admins."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return UserDetailResponse.model_validate(user)
