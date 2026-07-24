"""
TraceVault Security — Password Hashing with Argon2
All passwords hashed with Argon2id — never stored in plaintext.
"""
from __future__ import annotations

import secrets
import string
from passlib.context import CryptContext

# Argon2id is the recommended hashing algorithm for password storage (OWASP 2024)
_pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=3,       # Iterations
    argon2__memory_cost=65536, # 64 MB
    argon2__parallelism=2,     # Threads
    argon2__hash_len=32,       # Output length
    argon2__type="ID",         # Argon2id
)


def hash_password(plain_password: str) -> str:
    """
    Hash a password using Argon2id.
    Returns: Argon2id hash string (includes salt, parameters).
    """
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against an Argon2id hash.
    Returns: True if password matches.
    """
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Check if a password hash needs to be rehashed (algorithm upgrade)."""
    return _pwd_context.needs_update(hashed_password)


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def generate_secure_password(length: int = 16) -> str:
    """Generate a secure random password meeting all policy requirements."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        # Ensure it meets policy: uppercase, lowercase, digit, special char
        if (
            any(c.isupper() for c in password)
            and any(c.islower() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)
        ):
            return password


def validate_password_policy(password: str) -> tuple[bool, list[str]]:
    """
    Validate password against policy requirements.
    Returns: (is_valid, list of error messages)
    """
    errors: list[str] = []
    if len(password) < 12:
        errors.append("Password must be at least 12 characters long.")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit.")
    if not any(c in "!@#$%^&*()-_=+[]{}|;':\",./<>?" for c in password):
        errors.append("Password must contain at least one special character.")

    # Check common weak patterns
    common_weak = ["password", "123456", "qwerty", "admin", "letmein"]
    if any(weak in password.lower() for weak in common_weak):
        errors.append("Password contains a commonly used pattern.")

    return (len(errors) == 0, errors)
