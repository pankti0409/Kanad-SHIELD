"""
TraceVault Security — JWT Token Management
Access tokens (15 min) + Refresh tokens (7 days) with rotation.
All JWTs include jti (JWT ID) for revocation support.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt

from app.config import get_settings


class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"


def _get_jwt_settings():
    return get_settings().jwt


def create_access_token(
    user_id: str,
    role: str,
    session_id: Optional[str] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> tuple[str, str, datetime]:
    """
    Create a JWT access token.
    Returns: (token_string, jti, expiry_datetime)
    """
    settings = _get_jwt_settings()
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "jti": jti,
        "type": TokenType.ACCESS,
        "role": role,
        "iat": now,
        "exp": expiry,
        "nbf": now,
    }
    if session_id:
        payload["sid"] = session_id
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(
        payload,
        settings.JWT_SECRET.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, jti, expiry


def create_refresh_token(
    user_id: str,
    device_info: Optional[str] = None,
) -> tuple[str, str, datetime]:
    """
    Create a JWT refresh token.
    Returns: (token_string, jti, expiry_datetime)
    """
    settings = _get_jwt_settings()
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "jti": jti,
        "type": TokenType.REFRESH,
        "iat": now,
        "exp": expiry,
        "nbf": now,
    }
    if device_info:
        payload["device"] = device_info

    token = jwt.encode(
        payload,
        settings.JWT_REFRESH_SECRET.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, jti, expiry


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.
    Raises: JWTError on invalid/expired token.
    """
    settings = _get_jwt_settings()
    payload = jwt.decode(
        token,
        settings.JWT_SECRET.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["sub", "jti", "type", "role", "exp"]},
    )
    if payload.get("type") != TokenType.ACCESS:
        raise JWTError("Invalid token type: expected access token.")
    return payload


def decode_refresh_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT refresh token.
    Raises: JWTError on invalid/expired token.
    """
    settings = _get_jwt_settings()
    payload = jwt.decode(
        token,
        settings.JWT_REFRESH_SECRET.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["sub", "jti", "type", "exp"]},
    )
    if payload.get("type") != TokenType.REFRESH:
        raise JWTError("Invalid token type: expected refresh token.")
    return payload


def hash_token(token: str) -> str:
    """
    Hash a token for database storage.
    NEVER store raw tokens in the database.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def extract_user_id(token_payload: dict[str, Any]) -> str:
    """Extract and validate user ID from token payload."""
    user_id = token_payload.get("sub")
    if not user_id:
        raise JWTError("Token missing subject claim.")
    return user_id


def extract_jti(token_payload: dict[str, Any]) -> str:
    """Extract JWT ID from token payload."""
    jti = token_payload.get("jti")
    if not jti:
        raise JWTError("Token missing JWT ID.")
    return jti
