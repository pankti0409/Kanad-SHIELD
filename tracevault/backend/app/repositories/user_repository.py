"""
TraceVault User Repository
Data access layer for user-related operations.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserStatus


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(
            select(User).where(
                and_(User.email == email.lower().strip(), User.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self._session.execute(
            select(User).where(
                and_(User.username == username.strip(), User.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get user by email OR username — used for login."""
        identifier = identifier.strip()
        result = await self._session.execute(
            select(User).where(
                and_(
                    or_(
                        User.email == identifier.lower(),
                        User.username == identifier,
                    ),
                    User.is_deleted == False,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> User:
        """Create a new user."""
        if "email" in kwargs:
            kwargs["email"] = kwargs["email"].lower().strip()
        user = User(**kwargs)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update_last_login(
        self, user_id: uuid.UUID, ip_address: Optional[str] = None
    ) -> None:
        await self._session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                last_login_at=datetime.now(timezone.utc),
                last_login_ip=ip_address,
                failed_login_attempts=0,
                locked_until=None,
            )
        )

    async def increment_failed_attempts(self, user_id: uuid.UUID) -> int:
        """Increment failed login attempts, return new count."""
        user = await self.get_by_id(user_id)
        if not user:
            return 0
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        await self._session.flush()
        return user.failed_login_attempts

    async def lock_account(
        self, user_id: uuid.UUID, locked_until: datetime
    ) -> None:
        await self._session.execute(
            update(User)
            .where(User.id == user_id)
            .values(locked_until=locked_until, status=UserStatus.LOCKED)
        )

    async def unlock_account(self, user_id: uuid.UUID) -> None:
        await self._session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                locked_until=None,
                status=UserStatus.ACTIVE,
                failed_login_attempts=0,
            )
        )

    async def update_password(
        self, user_id: uuid.UUID, hashed_password: str
    ) -> None:
        await self._session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                hashed_password=hashed_password,
                password_changed_at=datetime.now(timezone.utc),
                must_change_password=False,
            )
        )

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 50,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None,
    ) -> tuple[list[User], int]:
        """List users with filtering and pagination."""
        from sqlalchemy import func

        q = select(User).where(User.is_deleted == False)
        count_q = select(func.count()).select_from(User).where(User.is_deleted == False)

        if role:
            q = q.where(User.role == role)
            count_q = count_q.where(User.role == role)

        if status:
            q = q.where(User.status == status)
            count_q = count_q.where(User.status == status)

        if search:
            pattern = f"%{search}%"
            search_filter = or_(
                User.full_name.ilike(pattern),
                User.email.ilike(pattern),
                User.username.ilike(pattern),
            )
            q = q.where(search_filter)
            count_q = count_q.where(search_filter)

        total_result = await self._session.execute(count_q)
        total = total_result.scalar_one()

        q = q.order_by(User.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(q)
        users = list(result.scalars().all())

        return users, total

    async def email_exists(self, email: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
        q = select(User.id).where(
            and_(User.email == email.lower().strip(), User.is_deleted == False)
        )
        if exclude_id:
            q = q.where(User.id != exclude_id)
        result = await self._session.execute(q)
        return result.scalar_one_or_none() is not None

    async def username_exists(
        self, username: str, exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        q = select(User.id).where(
            and_(User.username == username.strip(), User.is_deleted == False)
        )
        if exclude_id:
            q = q.where(User.id != exclude_id)
        result = await self._session.execute(q)
        return result.scalar_one_or_none() is not None
