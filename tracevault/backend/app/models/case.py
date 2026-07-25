"""
TraceVault Case Management Models
Investigation cases, members, status tracking.
Uses generic SQLAlchemy types for cross-database compatibility.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BaseModel, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.recording import Recording
    from app.models.evidence import EvidenceFile, Report
    from app.models.audit import AuditLog


class CaseStatus(str, PyEnum):
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    PENDING_REVIEW = "pending_review"
    EVIDENCE_PROCESSING = "evidence_processing"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CLOSED = "closed"


class CasePriority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CaseCategory(str, PyEnum):
    FRAUD = "fraud"
    CYBERCRIME = "cybercrime"
    EXTORTION = "extortion"
    DRUG_TRAFFICKING = "drug_trafficking"
    HUMAN_TRAFFICKING = "human_trafficking"
    VIOLENCE = "violence"
    FINANCIAL_CRIME = "financial_crime"
    ORGANIZED_CRIME = "organized_crime"
    TERRORISM = "terrorism"
    CORRUPTION = "corruption"
    GENERAL = "general"
    OTHER = "other"


class CaseMemberRole(str, PyEnum):
    LEAD = "lead"
    MEMBER = "member"
    OBSERVER = "observer"


class Case(BaseModel, SoftDeleteMixin):
    """
    Investigation case — the primary organizational unit in TraceVault.
    Every recording, evidence, transcript, and report belongs to a case.
    """
    __tablename__ = "cases"
    __table_args__ = (
        UniqueConstraint("case_number", name="uq_cases_case_number"),
    )

    # Identity
    case_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Classification
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status_enum"),
        default=CaseStatus.OPEN,
        nullable=False,
        index=True,
    )
    priority: Mapped[CasePriority] = mapped_column(
        Enum(CasePriority, name="case_priority_enum"),
        default=CasePriority.MEDIUM,
        nullable=False,
        index=True,
    )
    category: Mapped[CaseCategory] = mapped_column(
        Enum(CaseCategory, name="case_category_enum"),
        default=CaseCategory.GENERAL,
        nullable=False,
        index=True,
    )
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # People
    lead_investigator_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Dates
    expected_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Risk & Intelligence
    risk_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Counters (denormalized for performance)
    recording_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    report_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Extra metadata
    case_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    lead_investigator: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[lead_investigator_id]
    )
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    members: Mapped[list["CaseMember"]] = relationship(
        "CaseMember", back_populates="case", cascade="all, delete-orphan"
    )
    recordings: Mapped[list["Recording"]] = relationship(
        "Recording", back_populates="case", cascade="all, delete-orphan"
    )
    evidence_files: Mapped[list["EvidenceFile"]] = relationship(
        "EvidenceFile", back_populates="case", cascade="all, delete-orphan"
    )
    reports: Mapped[list["Report"]] = relationship(
        "Report", back_populates="case", cascade="all, delete-orphan"
    )
    notes: Mapped[list["InvestigatorNote"]] = relationship(
        "InvestigatorNote", back_populates="case", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["CaseTask"]] = relationship(
        "CaseTask", back_populates="case", cascade="all, delete-orphan"
    )


class CaseMember(BaseModel):
    """Association between users and cases with role tracking."""
    __tablename__ = "case_members"
    __table_args__ = (
        UniqueConstraint("case_id", "user_id", name="uq_case_members_case_user"),
    )

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[CaseMemberRole] = mapped_column(
        Enum(CaseMemberRole, name="case_member_role_enum"),
        default=CaseMemberRole.MEMBER,
        nullable=False,
    )
    added_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    can_upload: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_export: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_edit: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="members")
    user: Mapped["User"] = relationship("User")


class InvestigatorNote(BaseModel, SoftDeleteMixin):
    """Investigator notes attached to cases, recordings, or segments."""
    __tablename__ = "investigator_notes"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recording_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    segment_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    author_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    note_type: Mapped[str] = mapped_column(String(50), default="general", nullable=False)
    timestamp_reference: Mapped[Optional[float]] = mapped_column(nullable=True)
    attachments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    revision_history: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="notes")
    author: Mapped["User"] = relationship("User")


class CaseTask(BaseModel):
    """Tasks assigned within cases."""
    __tablename__ = "case_tasks"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_to_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    related_evidence_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    related_recording_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="tasks")
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
