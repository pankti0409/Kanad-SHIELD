"""
TraceVault Case Management API Routes
CRUD operations for cases, members, notes, tasks.
"""
from __future__ import annotations

import math
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, DBSession, require_permission
from app.models.case import Case, CaseMember, CasePriority, CaseStatus, CaseTask, InvestigatorNote
from app.models.user import UserRole
from app.security.rbac import Permission
from app.services.audit_service import AuditService

router = APIRouter(prefix="/cases", tags=["Cases"])


# ============================================================
# Pydantic Schemas
# ============================================================

class CaseCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: str = Field(default="medium")
    category: str = Field(default="general")
    tags: Optional[list[str]] = None
    lead_investigator_id: Optional[uuid.UUID] = None
    expected_completion_date: Optional[str] = None


class CaseUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list[str]] = None
    lead_investigator_id: Optional[uuid.UUID] = None


class CaseResponse(BaseModel):
    id: uuid.UUID
    case_number: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    category: str
    tags: Optional[list[str]] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    recording_count: int
    evidence_count: int
    report_count: int
    lead_investigator_id: Optional[uuid.UUID] = None
    created_by: uuid.UUID
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, case: Case) -> "CaseResponse":
        return cls(
            id=case.id,
            case_number=case.case_number,
            title=case.title,
            description=case.description,
            status=case.status.value if case.status else "open",
            priority=case.priority.value if case.priority else "medium",
            category=case.category.value if case.category else "general",
            tags=case.tags,
            risk_score=case.risk_score,
            risk_level=case.risk_level,
            recording_count=case.recording_count,
            evidence_count=case.evidence_count,
            report_count=case.report_count,
            lead_investigator_id=case.lead_investigator_id,
            created_by=case.created_by,
            created_at=case.created_at.isoformat(),
            updated_at=case.updated_at.isoformat(),
        )


class CaseListResponse(BaseModel):
    items: list[CaseResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================
# Case Endpoints
# ============================================================

@router.get("", response_model=CaseListResponse, summary="List cases")
async def list_cases(
    db: DBSession,
    current_user: User = Depends(require_permission(Permission.CASE_VIEW)),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=200),
) -> CaseListResponse:
    """List all cases the current user has access to."""
    q = select(Case).where(Case.is_deleted == False)
    count_q = select(func.count()).select_from(Case).where(Case.is_deleted == False)

    # Non-admin users see only their cases
    if current_user.role not in (UserRole.SYSTEM_ADMIN, UserRole.SUPERVISOR):
        # Show cases where user is a member or lead investigator
        member_subq = select(CaseMember.case_id).where(
            CaseMember.user_id == current_user.id
        )
        q = q.where(
            or_(
                Case.lead_investigator_id == current_user.id,
                Case.created_by == current_user.id,
                Case.id.in_(member_subq),
            )
        )
        count_q = count_q.where(
            or_(
                Case.lead_investigator_id == current_user.id,
                Case.created_by == current_user.id,
                Case.id.in_(member_subq),
            )
        )

    if status:
        q = q.where(Case.status == status)
        count_q = count_q.where(Case.status == status)
    if priority:
        q = q.where(Case.priority == priority)
        count_q = count_q.where(Case.priority == priority)
    if category:
        q = q.where(Case.category == category)
        count_q = count_q.where(Case.category == category)
    if search:
        pattern = f"%{search}%"
        search_filter = or_(
            Case.title.ilike(pattern),
            Case.description.ilike(pattern),
            Case.case_number.ilike(pattern),
        )
        q = q.where(search_filter)
        count_q = count_q.where(search_filter)

    total_result = await db.execute(count_q)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    q = q.order_by(desc(Case.created_at)).offset(offset).limit(page_size)
    result = await db.execute(q)
    cases = list(result.scalars().all())

    return CaseListResponse(
        items=[CaseResponse.from_model(c) for c in cases],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED, summary="Create case")
async def create_case(
    body: CaseCreateRequest,
    request: Request,
    db: DBSession,
    current_user: User = Depends(require_permission(Permission.CASE_CREATE)),
) -> CaseResponse:
    """Create a new investigation case."""
    import shortuuid
    from datetime import datetime

    # Generate unique case number
    case_number = f"TV-{shortuuid.uuid()[:8].upper()}"

    case = Case(
        case_number=case_number,
        title=body.title,
        description=body.description,
        priority=body.priority,
        category=body.category,
        tags=body.tags,
        lead_investigator_id=body.lead_investigator_id or current_user.id,
        created_by=current_user.id,
        status=CaseStatus.OPEN,
    )
    db.add(case)
    await db.flush()
    await db.refresh(case)

    # Add creator as lead member
    member = CaseMember(
        case_id=case.id,
        user_id=current_user.id,
        role="lead",
        added_by=current_user.id,
    )
    db.add(member)
    await db.flush()

    # Audit log
    audit = AuditService(db)
    await audit.log(
        action="case.create",
        action_category="case_management",
        user=current_user,
        resource_type="case",
        resource_id=str(case.id),
        resource_name=case.title,
        case_id=case.id,
        request=request,
    )

    return CaseResponse.from_model(case)


@router.get("/{case_id}", response_model=CaseResponse, summary="Get case details")
async def get_case(
    case_id: uuid.UUID,
    db: DBSession,
    current_user: User = Depends(require_permission(Permission.CASE_VIEW)),
) -> CaseResponse:
    """Get full case details."""
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.is_deleted == False)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")
    return CaseResponse.from_model(case)


@router.patch("/{case_id}", response_model=CaseResponse, summary="Update case")
async def update_case(
    case_id: uuid.UUID,
    body: CaseUpdateRequest,
    request: Request,
    db: DBSession,
    current_user: User = Depends(require_permission(Permission.CASE_EDIT)),
) -> CaseResponse:
    """Update case fields."""
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.is_deleted == False)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")

    update_data = body.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(case, key, value)

    await db.flush()
    await db.refresh(case)

    audit = AuditService(db)
    await audit.log(
        action="case.update",
        action_category="case_management",
        user=current_user,
        resource_type="case",
        resource_id=str(case.id),
        resource_name=case.title,
        case_id=case.id,
        changes=update_data,
        request=request,
    )

    return CaseResponse.from_model(case)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft delete case")
async def delete_case(
    case_id: uuid.UUID,
    request: Request,
    db: DBSession,
    current_user: User = Depends(require_permission(Permission.CASE_DELETE)),
) -> None:
    """Soft delete a case (requires supervisor or admin role)."""
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.is_deleted == False)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")

    case.soft_delete()
    await db.flush()

    audit = AuditService(db)
    await audit.log(
        action="case.delete",
        action_category="case_management",
        user=current_user,
        resource_type="case",
        resource_id=str(case_id),
        resource_name=case.title,
        case_id=case.id,
        severity="high",
        request=request,
    )
