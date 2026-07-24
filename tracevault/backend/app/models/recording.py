"""
TraceVault Recording & Audio Processing Models
Evidence recordings, processing jobs, transcripts, and speaker models.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

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
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BaseModel, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.user import User


class ProcessingStatus(str, PyEnum):
    QUEUED = "queued"
    PREPARING = "preparing"
    ENHANCING = "enhancing"
    REDUCING_NOISE = "reducing_noise"
    DETECTING_SPEECH = "detecting_speech"
    DETECTING_SPEAKERS = "detecting_speakers"
    TRANSCRIBING = "transcribing"
    RUNNING_AI = "running_ai"
    GENERATING_EMBEDDINGS = "generating_embeddings"
    SAVING_RESULTS = "saving_results"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class RiskLevel(str, PyEnum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Recording(BaseModel, SoftDeleteMixin):
    """
    Audio recording evidence.
    Original files are NEVER modified after upload.
    SHA-256 hash ensures integrity.
    """
    __tablename__ = "recordings"
    __table_args__ = (
        
        
        
        
        
        
    )

    # Case Reference
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

    # File Information (Evidence Identity)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    processed_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    noise_reduced_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # File Integrity (Immutable)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    codec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Audio Properties (Original)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sample_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    channels: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bitrate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bit_depth: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Processing Status
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status_enum"),
        default=ProcessingStatus.QUEUED,
        nullable=False,
        index=True,
    )
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Language
    detected_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    detected_language_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_multilingual: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # AI Results
    risk_level: Mapped[Optional[RiskLevel]] = mapped_column(
        Enum(RiskLevel, name="risk_level_enum"),
        nullable=True,
        index=True,
    )
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threat_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    entity_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    keyword_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    speaker_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    transcription_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Evidence Metadata
    upload_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    evidence_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    integrity_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    integrity_last_checked: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Extra
    recording_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    pipeline_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_versions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="recordings")
    uploader: Mapped["User"] = relationship("User", foreign_keys=[uploaded_by_id])
    transcript: Mapped[Optional["Transcript"]] = relationship(
        "Transcript", back_populates="recording", uselist=False
    )
    speakers: Mapped[list["Speaker"]] = relationship(
        "Speaker", back_populates="recording", cascade="all, delete-orphan"
    )
    processing_logs: Mapped[list["ProcessingLog"]] = relationship(
        "ProcessingLog", back_populates="recording", cascade="all, delete-orphan"
    )
    chain_of_custody: Mapped[list["ChainOfCustodyEvent"]] = relationship(
        "ChainOfCustodyEvent", back_populates="recording", cascade="all, delete-orphan"
    )


class Speaker(BaseModel):
    """Identified speaker within a recording."""
    __tablename__ = "speakers"
    __table_args__ = (
        UniqueConstraint("recording_id", "speaker_label", name="uq_speakers_recording_label"),
        
    )

    recording_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    speaker_label: Mapped[str] = mapped_column(String(20), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    identified_as: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    speaking_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    speaking_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    turn_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    color_hex: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    embedding_vector: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationship
    recording: Mapped["Recording"] = relationship("Recording", back_populates="speakers")


class Transcript(BaseModel):
    """Full transcript for a recording."""
    __tablename__ = "transcripts"
    __table_args__ = (
        UniqueConstraint("recording_id", name="uq_transcripts_recording"),
        
    )

    recording_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    character_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pipeline_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    transcript_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    recording: Mapped["Recording"] = relationship("Recording", back_populates="transcript")
    segments: Mapped[list["TranscriptSegment"]] = relationship(
        "TranscriptSegment", back_populates="transcript", cascade="all, delete-orphan",
        order_by="TranscriptSegment.start_time"
    )


class TranscriptSegment(BaseModel):
    """Individual segment of a transcript with timestamps and speaker info."""
    __tablename__ = "transcript_segments"
    __table_args__ = (
        
        
        
    )

    transcript_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcripts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    speaker_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("speakers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    speaker_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    character_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    has_threat: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_entity: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_keyword: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    emotion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    words: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Word-level timestamps

    # Relationships
    transcript: Mapped["Transcript"] = relationship("Transcript", back_populates="segments")
    speaker: Mapped[Optional["Speaker"]] = relationship("Speaker")


class ProcessingLog(BaseModel):
    """Logs for every stage of the AI processing pipeline."""
    __tablename__ = "processing_logs"
    __table_args__ = (
        
        
    )

    recording_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hardware_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    memory_usage_mb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cpu_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gpu_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    warnings: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    output_summary: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationship
    recording: Mapped["Recording"] = relationship("Recording", back_populates="processing_logs")


