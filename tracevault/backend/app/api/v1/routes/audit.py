"""
TraceVault Audit Log API Routes
Read-only paginated access to the immutable audit trail.
"""
from __future__ import annotations
import math
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from typing import Optional
from app.auth.dependencies import CurrentUser, DBSession, require_permission
from app.models.audit import AuditLog
from app.security.rbac import Permission

router = APIRouter(prefix="/audit", tags=["Audit Log"])


class AuditLogEntry(BaseModel):
    id: str
    action: str
    action_category: str
    user_id: Optional[str]
    ip_address: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    description: Optional[str]
    severity: str
    created_at: str

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    items: list[AuditLogEntry]
    total: int
    page: int
    page_size: int
    pages: int


@router.get("", response_model=AuditLogListResponse, summary="List audit log entries")
async def list_audit_logs(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    action_category: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
) -> AuditLogListResponse:
    """Return paginated audit log entries. Requires supervisor or admin role."""
    q = select(AuditLog)
    count_q = select(func.count()).select_from(AuditLog)

    if action_category:
        q = q.where(AuditLog.action_category == action_category)
        count_q = count_q.where(AuditLog.action_category == action_category)
    if severity:
        q = q.where(AuditLog.severity == severity)
        count_q = count_q.where(AuditLog.severity == severity)

    total_result = await db.execute(count_q)
    total = total_result.scalar_one() or 0

    offset = (page - 1) * page_size
    q = q.order_by(desc(AuditLog.created_at)).offset(offset).limit(page_size)
    result = await db.execute(q)
    entries = list(result.scalars().all())

    return AuditLogListResponse(
        items=[
            AuditLogEntry(
                id=str(e.id),
                action=e.action,
                action_category=e.action_category or "system",
                user_id=str(e.user_id) if e.user_id else None,
                ip_address=e.ip_address,
                resource_type=e.resource_type,
                resource_id=str(e.resource_id) if e.resource_id else None,
                description=e.description,
                severity=e.severity or "info",
                created_at=e.created_at.isoformat(),
            )
            for e in entries
        ],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )
