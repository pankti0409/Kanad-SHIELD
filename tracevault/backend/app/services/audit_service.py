"""
TraceVault Audit Service
Creates immutable audit log entries for all security-sensitive operations.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.user import User


class AuditService:
    """Service for creating immutable audit logs."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def log(
        self,
        action: str,
        action_category: str,
        result: str = "success",
        user: Optional[User] = None,
        user_id: Optional[uuid.UUID] = None,
        username: Optional[str] = None,
        user_role: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        case_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        severity: str = "info",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_info: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        changes: Optional[dict] = None,
        error_message: Optional[str] = None,
        extra_data: Optional[dict] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Create an immutable audit log entry.
        Extracts request context automatically if Request is provided.
        """
        # Extract from User object if provided
        if user:
            user_id = user_id or user.id
            username = username or user.username
            user_role = user_role or user.role.value

        # Extract from Request if provided
        if request:
            ip_address = ip_address or _get_client_ip(request)
            user_agent = user_agent or request.headers.get("user-agent")
            request_id = request_id or str(request.state.request_id) if hasattr(request.state, "request_id") else None

        entry = AuditLog(
            user_id=user_id,
            username=username,
            user_role=user_role,
            action=action,
            action_category=action_category,
            description=description,
            severity=severity,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            resource_name=resource_name,
            case_id=case_id,
            result=result,
            error_message=error_message,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            session_id=session_id,
            correlation_id=correlation_id,
            request_id=request_id,
            extra_data=extra_data,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(entry)
        await self._db.flush()
        return entry

    async def log_login(self, user: User, result: str, request: Optional[Request] = None, **kwargs) -> AuditLog:
        return await self.log(
            action="auth.login",
            action_category="authentication",
            result=result,
            user=user,
            severity="info" if result == "success" else "warning",
            request=request,
            **kwargs,
        )

    async def log_logout(self, user: User, request: Optional[Request] = None) -> AuditLog:
        return await self.log(
            action="auth.logout",
            action_category="authentication",
            user=user,
            request=request,
        )

    async def log_upload(
        self,
        user: User,
        resource_type: str,
        resource_id: str,
        resource_name: str,
        case_id: Optional[uuid.UUID] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        return await self.log(
            action=f"{resource_type}.upload",
            action_category="evidence",
            user=user,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            case_id=case_id,
            severity="info",
            request=request,
        )

    async def log_export(
        self,
        user: User,
        resource_type: str,
        resource_id: str,
        export_format: str,
        case_id: Optional[uuid.UUID] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        return await self.log(
            action=f"{resource_type}.export",
            action_category="export",
            user=user,
            resource_type=resource_type,
            resource_id=resource_id,
            case_id=case_id,
            severity="info",
            extra_data={"format": export_format},
            request=request,
        )

    async def log_permission_change(
        self,
        performed_by: User,
        target_user_id: uuid.UUID,
        old_role: str,
        new_role: str,
        request: Optional[Request] = None,
    ) -> AuditLog:
        return await self.log(
            action="user.permission_change",
            action_category="administration",
            user=performed_by,
            resource_type="user",
            resource_id=str(target_user_id),
            severity="high",
            changes={"old_role": old_role, "new_role": new_role},
            request=request,
        )


def _get_client_ip(request: Request) -> Optional[str]:
    """Extract real client IP address, handling proxies."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client:
        return request.client.host
    return None
