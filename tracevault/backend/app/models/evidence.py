"""
TraceVault Evidence, Chain of Custody & Report Models
Evidence files, chain of custody events, reports, and exports.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BaseModel, SoftDeleteMixin


class EvidenceType(str, PyEnum):
    AUDIO_RECORDING = "audio_recording"
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    EXTERNAL_REFERENCE = "external_reference"
    OTHER = "other"


class EvidenceFile(BaseModel):
    """
    Digital evidence file associated with a case.
    Original files are IMMUTABLE after upload.
    """
    __tablename__ = "evidence_files"
    __table_args__ = (
        
        
        
        
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    recording_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recordings.id", ondelete="SET NULL"),
        nullable=True,
    )

    # File Properties
    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType, name="evidence_type_enum"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Integrity
    integrity_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    integrity_last_checked: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    evidence_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    upload_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="evidence_files")
    custody_events: Mapped[list["ChainOfCustodyEvent"]] = relationship(
        "ChainOfCustodyEvent",
        foreign_keys="[ChainOfCustodyEvent.evidence_file_id]",
        back_populates="evidence_file",
        cascade="all, delete-orphan",
    )


class ChainOfCustodyEvent(BaseModel):
    """
    Every interaction with evidence creates a custody event.
    Chain of custody events are IMMUTABLE.
    """
    __tablename__ = "chain_of_custody"
    __table_args__ = (
        
        
        
        
        
    )

    evidence_file_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence_files.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    recording_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recordings.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    previous_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    current_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    evidence_file: Mapped[Optional["EvidenceFile"]] = relationship(
        "EvidenceFile",
        foreign_keys=[evidence_file_id],
        back_populates="custody_events",
    )
    recording: Mapped[Optional["Recording"]] = relationship(
        "Recording", back_populates="chain_of_custody"
    )
    user: Mapped["User"] = relationship("User")


class Report(BaseModel, SoftDeleteMixin):
    """Generated investigation report."""
    __tablename__ = "reports"
    __table_args__ = (
        
        
        
        
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    recording_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recordings.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Report Identity
    report_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default="draft", nullable=False, index=True
    )
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Content
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Generation Metadata
    model_used: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    generation_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evidence_references: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pipeline_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Report Config
    include_sections: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    watermark_text: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    confidentiality_level: Mapped[str] = mapped_column(
        String(50), default="confidential", nullable=False
    )

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="reports")
    exports: Mapped[list["ReportExport"]] = relationship(
        "ReportExport", back_populates="report", cascade="all, delete-orphan"
    )


class ReportExport(BaseModel):
    """Track report exports with audit information."""
    __tablename__ = "report_exports"
    __table_args__ = (
        
        
        
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exported_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    format: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    file_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    sha256_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    export_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    report: Mapped["Report"] = relationship("Report", back_populates="exports")
    exporter: Mapped["User"] = relationship("User")


