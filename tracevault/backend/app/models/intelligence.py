"""
TraceVault AI Intelligence Models
Entities, keywords, topics, emotions, threats, risk scores, and summaries.
Uses generic SQLAlchemy types for cross-database compatibility.
"""
from __future__ import annotations

import uuid
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, BaseModel


class ThreatCategory(str, PyEnum):
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    KIDNAPPING = "kidnapping"
    FRAUD = "fraud"
    SCAM = "scam"
    MONEY_LAUNDERING = "money_laundering"
    DRUG_ACTIVITY = "drug_activity"
    WEAPON_DISCUSSION = "weapon_discussion"
    EXTORTION = "extortion"
    CYBER_ATTACK = "cyber_attack"
    BLACKMAIL = "blackmail"
    BRIBERY = "bribery"
    HUMAN_TRAFFICKING = "human_trafficking"
    ILLEGAL_TRADE = "illegal_trade"
    SUSPICIOUS_COORDINATION = "suspicious_coordination"
    COERCION = "coercion"
    ILLEGAL_TRANSACTION = "illegal_transaction"
    OTHER = "other"


class EmotionType(str, PyEnum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    STRESS = "stress"
    CALM = "calm"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    URGENCY = "urgency"
    UNKNOWN = "unknown"


class SentimentType(str, PyEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class Entity(BaseModel):
    """Named entity extracted from transcripts."""
    __tablename__ = "entities"

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transcript_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("transcripts.id", ondelete="CASCADE"),
        nullable=True,
    )
    segment_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_value: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    normalized_value: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    speaker_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    timestamp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    end_timestamp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    context_sentence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    char_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    char_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    review_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    entity_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class Keyword(BaseModel):
    """Keywords extracted from transcripts."""
    __tablename__ = "keywords"

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    keyword_text: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    normalized_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    frequency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    speaker_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    first_occurrence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_occurrence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    occurrences: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)


class Topic(BaseModel):
    """Topic classification for recordings."""
    __tablename__ = "topics"

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    evidence_segments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)


class EmotionAnalysis(BaseModel):
    """Emotion analysis for recording segments."""
    __tablename__ = "emotions"

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    segment_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    speaker_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    emotion: Mapped[EmotionType] = mapped_column(
        Enum(EmotionType, name="emotion_type_enum"),
        nullable=False,
        index=True,
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    intensity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_scores: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class ThreatIndicator(BaseModel):
    """Detected threat indicators in recordings."""
    __tablename__ = "threats"

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    segment_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    category: Mapped[ThreatCategory] = mapped_column(
        Enum(ThreatCategory, name="threat_category_enum"),
        nullable=False,
        index=True,
    )
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)
    speaker_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    timestamp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    end_timestamp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    review_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    reviewed_by_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    supporting_segments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)


class RiskScore(BaseModel):
    """Overall risk assessment for a recording."""
    __tablename__ = "risk_scores"
    __table_args__ = (
        UniqueConstraint("recording_id", name="uq_risk_scores_recording"),
    )

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    threat_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    emotion_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    entity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    topic_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    keyword_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    factors: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class ConversationSummary(BaseModel):
    """AI-generated conversation summaries."""
    __tablename__ = "summaries"

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evidence_references: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)


class TimelineEvent(BaseModel):
    """Investigation timeline events generated from AI analysis."""
    __tablename__ = "timeline_events"

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    end_timestamp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    speaker_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    evidence_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entities: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class EmbeddingMetadata(BaseModel):
    """Metadata for vector embeddings stored in Qdrant."""
    __tablename__ = "embeddings_metadata"

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    segment_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    qdrant_point_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    qdrant_collection: Mapped[str] = mapped_column(String(100), nullable=False)
    text_chunk: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_chunks: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class RelationshipGraph(BaseModel):
    """Entity relationships extracted from transcripts."""
    __tablename__ = "relationship_graphs"

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_entity: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_entity: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    speaker_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class InvestigationRecommendation(BaseModel):
    """AI-generated investigation recommendations."""
    __tablename__ = "investigation_recommendations"

    recording_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    supporting_evidence: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    related_entities: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_actioned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    actioned_by_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

