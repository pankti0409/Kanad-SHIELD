"""
TraceVault Authentication Service
Core authentication business logic:
- Login with account lockout protection
- Token issuance and rotation
- Logout and session management
- Password reset
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import RefreshToken, User, UserSession, UserStatus, PasswordResetToken
from app.repositories.user_repository import UserRepository
from app.security.password import (
    generate_secure_token,
    hash_password,
    verify_password,
)
from app.security.tokens import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_token,
)


class AuthError(Exception):
    """Authentication-specific error."""
    pass


class AccountLockedError(AuthError):
    """Raised when account is locked due to failed attempts."""
    pass


class InvalidCredentialsError(AuthError):
    """Raised when credentials are invalid."""
    pass


class TokenExpiredError(AuthError):
    """Raised when a token has expired."""
    pass


class AuthService:
    """Service for all authentication operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._settings = get_settings()
        self._user_repo = UserRepository(db)

    async def authenticate(
        self,
        identifier: str,
        password: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> dict:
        """
        Authenticate a user by email/username + password.
        Returns: dict with tokens and user info.
        Raises: InvalidCredentialsError, AccountLockedError.
        """
        user = await self._user_repo.get_by_email_or_username(identifier)

        if user is None:
            # Constant-time dummy verification to prevent timing attacks
            hash_password("dummy_verification_prevents_timing_attack")
            raise InvalidCredentialsError("Invalid credentials. Please try again.")

        # Check if account is locked
        if user.is_locked:
            raise AccountLockedError(
                "Your account is temporarily locked due to multiple failed login attempts. "
                "Please try again later or contact your administrator."
            )

        # Verify password
        if not verify_password(password, user.hashed_password):
            failed_count = await self._user_repo.increment_failed_attempts(user.id)
            max_attempts = self._settings.security.MAX_LOGIN_ATTEMPTS

            if failed_count >= max_attempts:
                lockout_until = datetime.now(timezone.utc) + timedelta(
                    minutes=self._settings.security.ACCOUNT_LOCKOUT_MINUTES
                )
                await self._user_repo.lock_account(user.id, lockout_until)
                raise AccountLockedError(
                    f"Account locked after {max_attempts} failed attempts. "
                    f"Try again in {self._settings.security.ACCOUNT_LOCKOUT_MINUTES} minutes."
                )
            raise InvalidCredentialsError(
                f"Invalid credentials. {max_attempts - failed_count} attempts remaining."
            )

        # Check account status
        if user.status == UserStatus.INACTIVE:
            raise AuthError("Your account is inactive. Contact your administrator.")
        if user.status == UserStatus.SUSPENDED:
            raise AuthError("Your account has been suspended. Contact your administrator.")

        # Create tokens
        access_token, access_jti, access_expiry = create_access_token(
            user_id=str(user.id),
            role=user.role.value,
        )
        refresh_token, refresh_jti, refresh_expiry = create_refresh_token(
            user_id=str(user.id),
            device_info=device_info,
        )

        # Store refresh token
        rt = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            jti=refresh_jti,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=refresh_expiry,
        )
        self._db.add(rt)

        # Create session
        session = UserSession(
            user_id=user.id,
            session_token_hash=hash_token(access_token),
            device_info=device_info,
            user_agent=user_agent,
            ip_address=ip_address,
            last_activity_at=datetime.now(timezone.utc),
            expires_at=refresh_expiry,
        )
        self._db.add(session)

        # Update last login
        await self._user_repo.update_last_login(user.id, ip_address)
        await self._db.flush()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self._settings.jwt.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user,
        }

    async def refresh_tokens(
        self,
        refresh_token: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> dict:
        """
        Rotate refresh token and issue new access + refresh tokens.
        Old refresh token is immediately revoked.
        """
        from sqlalchemy import select

        try:
            payload = decode_refresh_token(refresh_token)
        except Exception:
            raise TokenExpiredError("Refresh token is invalid or expired.")

        token_hash = hash_token(refresh_token)
        result = await self._db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked == False,
            )
        )
        stored_token = result.scalar_one_or_none()

        if not stored_token:
            raise TokenExpiredError("Refresh token has been revoked or is invalid.")

        if not stored_token.is_valid:
            raise TokenExpiredError("Refresh token has expired.")

        user = await self._user_repo.get_by_id(stored_token.user_id)
        if not user or not user.is_active:
            raise AuthError("User account not found or inactive.")

        # Revoke old token immediately (token rotation)
        stored_token.is_revoked = True
        stored_token.revoked_at = datetime.now(timezone.utc)

        # Issue new tokens
        access_token, _, access_expiry = create_access_token(
            user_id=str(user.id),
            role=user.role.value,
        )
        new_refresh_token, new_jti, new_expiry = create_refresh_token(
            user_id=str(user.id),
            device_info=device_info or stored_token.device_info,
        )

        # Store new refresh token
        new_rt = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh_token),
            jti=new_jti,
            device_info=device_info or stored_token.device_info,
            ip_address=ip_address or stored_token.ip_address,
            expires_at=new_expiry,
        )
        self._db.add(new_rt)
        await self._db.flush()

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": self._settings.jwt.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def logout(
        self,
        user_id: uuid.UUID,
        access_token: str,
        refresh_token: Optional[str] = None,
    ) -> None:
        """Revoke current session and refresh token."""
        from sqlalchemy import select, update

        # Revoke all current refresh tokens
        if refresh_token:
            rt_hash = hash_token(refresh_token)
            result = await self._db.execute(
                select(RefreshToken).where(
                    RefreshToken.token_hash == rt_hash,
                    RefreshToken.user_id == user_id,
                )
            )
            rt = result.scalar_one_or_none()
            if rt:
                rt.is_revoked = True
                rt.revoked_at = datetime.now(timezone.utc)

        # Deactivate session
        token_hash = hash_token(access_token)
        result = await self._db.execute(
            select(UserSession).where(
                UserSession.session_token_hash == token_hash,
                UserSession.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()
        if session:
            session.is_active = False

        await self._db.flush()

    async def logout_all_sessions(self, user_id: uuid.UUID) -> None:
        """Revoke all sessions and refresh tokens for a user."""
        from sqlalchemy import update

        await self._db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
            .values(
                is_revoked=True,
                revoked_at=datetime.now(timezone.utc),
            )
        )
        await self._db.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id, UserSession.is_active == True)
            .values(is_active=False)
        )
        await self._db.flush()

    async def request_password_reset(
        self, email: str, ip_address: Optional[str] = None
    ) -> Optional[str]:
        """
        Initiate password reset. Returns a reset token (or None if user not found).
        Always returns None externally to prevent user enumeration.
        """
        user = await self._user_repo.get_by_email(email)
        if not user:
            return None

        # Invalidate previous reset tokens
        from sqlalchemy import select, update
        await self._db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.is_used == False,
            )
            .values(is_used=True, used_at=datetime.now(timezone.utc))
        )

        # Generate new reset token
        raw_token = generate_secure_token(32)
        prt = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            ip_address=ip_address,
        )
        self._db.add(prt)
        await self._db.flush()

        return raw_token  # Caller sends this via email

    async def complete_password_reset(
        self, token: str, new_password: str
    ) -> None:
        """Complete password reset with a valid token."""
        from sqlalchemy import select

        token_hash = hash_token(token)
        result = await self._db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.is_used == False,
            )
        )
        prt = result.scalar_one_or_none()

        if not prt or not prt.is_valid:
            raise AuthError("Password reset token is invalid or has expired.")

        # Hash new password
        new_hash = hash_password(new_password)
        await self._user_repo.update_password(prt.user_id, new_hash)

        # Mark token as used
        prt.is_used = True
        prt.used_at = datetime.now(timezone.utc)

        # Revoke all sessions for security
        await self.logout_all_sessions(prt.user_id)
        await self._db.flush()
