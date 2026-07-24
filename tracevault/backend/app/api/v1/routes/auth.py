"""
TraceVault Authentication API Routes
Handles Google OAuth 2.0 login/registration, token refresh, and logout.
"""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select

from app.auth.dependencies import CurrentUser, DBSession, get_current_active_user
from app.models.user import User, UserRole, UserStatus, RefreshToken, UserSession
from app.schemas.auth import (
    LoginResponse,
    MessageResponse,
    RefreshRequest,
    RefreshResponse,
    UserBriefResponse,
    UserDetailResponse,
)
from app.schemas.google_auth import GoogleAuthRequest
from app.services.audit_service import AuditService
from app.security.password import generate_secure_password, hash_password
from app.security.tokens import create_access_token, create_refresh_token, hash_token
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/google",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate or register user using Google SSO",
)
async def google_auth(
    body: GoogleAuthRequest,
    request: Request,
    response: Response,
    db: DBSession,
) -> LoginResponse:
    """
    Authenticate or automatically register a user via Google OAuth SSO.
    Issues TraceVault access & refresh tokens.
    """
    settings = get_settings()
    audit_service = AuditService(db)

    email = body.email.lower().strip()
    username = email.split("@")[0].replace(".", "_")

    # Search for existing user by email
    result = await db.execute(
        select(User).where(User.email == email, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    # If user does not exist, auto-register via Google SSO
    if not user:
        role_enum = UserRole.SENIOR_INVESTIGATOR
        try:
            if body.role and hasattr(UserRole, body.role.upper()):
                role_enum = UserRole[body.role.upper()]
        except Exception:
            role_enum = UserRole.SENIOR_INVESTIGATOR

        # Ensure unique username
        existing_user_by_name = await db.execute(
            select(User).where(User.username == username)
        )
        if existing_user_by_name.scalar_one_or_none():
            username = f"{username}_{generate_secure_password(4)}"

        dummy_pwd = generate_secure_password(24)
        user = User(
            email=email,
            username=username,
            full_name=body.name,
            hashed_password=hash_password(dummy_pwd),
            role=role_enum,
            status=UserStatus.ACTIVE,
            avatar_url=body.picture,
            department=body.department or "Law Enforcement Agency",
            designation="Senior Officer",
            organization="Crime Branch",
            timezone="UTC",
            language="en",
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

        await audit_service.log(
            action="auth.google_register",
            action_category="authentication",
            user=user,
            description="User registered via Google OAuth SSO.",
            request=request,
        )
    else:
        # Update avatar if provided
        if body.picture:
            user.avatar_url = body.picture
        if user.status != UserStatus.ACTIVE:
            user.status = UserStatus.ACTIVE

    # Create JWT access and refresh tokens
    access_token, access_jti, access_expiry = create_access_token(
        user_id=str(user.id),
        role=user.role.value,
    )
    refresh_token, refresh_jti, refresh_expiry = create_refresh_token(
        user_id=str(user.id),
        device_info=request.headers.get("user-agent", "")[:200],
    )

    # Save refresh token in DB
    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        jti=refresh_jti,
        device_info=request.headers.get("user-agent", "")[:200],
        ip_address=_get_client_ip(request),
        expires_at=refresh_expiry,
    )
    db.add(rt)

    # Save active session
    session = UserSession(
        user_id=user.id,
        session_token_hash=hash_token(access_token),
        device_info=request.headers.get("user-agent", "")[:200],
        user_agent=request.headers.get("user-agent"),
        ip_address=_get_client_ip(request),
        expires_at=refresh_expiry,
    )
    db.add(session)
    await db.flush()

    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="strict",
        secure=False,
        max_age=settings.jwt.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    await audit_service.log_login(user=user, result="success", request=request)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserBriefResponse.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token",
)
async def refresh_tokens(
    body: RefreshRequest,
    request: Request,
    db: DBSession,
) -> RefreshResponse:
    from app.services.auth_service import AuthService, TokenExpiredError
    auth_service = AuthService(db)
    try:
        result = await auth_service.refresh_tokens(
            refresh_token=body.refresh_token,
            ip_address=_get_client_ip(request),
        )
        return RefreshResponse(**result)
    except TokenExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
)
async def logout(
    response: Response,
    db: DBSession,
    current_user: CurrentUser,
) -> MessageResponse:
    response.delete_cookie("access_token")
    return MessageResponse(message="Logged out successfully.")


@router.get(
    "/me",
    response_model=UserDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
)
async def get_me(current_user: CurrentUser) -> UserDetailResponse:
    return UserDetailResponse.model_validate(current_user)


def _get_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None
