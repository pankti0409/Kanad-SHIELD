"""TraceVault Models Package — registers all models for Alembic discovery."""
from app.models.user import User, UserRole, UserStatus, UserSession, RefreshToken, PasswordResetToken
from app.models.case import Case, CaseMember, CaseStatus, CasePriority, CaseCategory, InvestigatorNote, CaseTask
from app.models.recording import (
    Recording, Speaker, Transcript, TranscriptSegment, ProcessingLog,
    ProcessingStatus, RiskLevel, ChainOfCustodyEvent
)
from app.models.intelligence import (
    Entity, Keyword, Topic, EmotionAnalysis, ThreatIndicator, RiskScore,
    ConversationSummary, RelationshipGraph, TimelineEvent, InvestigationRecommendation,
    EmbeddingMetadata, ThreatCategory, EmotionType, SentimentType
)
from app.models.evidence import (
    EvidenceFile, Report, ReportExport, EvidenceType
)
from app.models.audit import AuditLog, Notification, SystemAlert

__all__ = [
    # User
    "User", "UserRole", "UserStatus", "UserSession", "RefreshToken", "PasswordResetToken",
    # Case
    "Case", "CaseMember", "CaseStatus", "CasePriority", "CaseCategory",
    "InvestigatorNote", "CaseTask",
    # Recording
    "Recording", "Speaker", "Transcript", "TranscriptSegment", "ProcessingLog",
    "ProcessingStatus", "RiskLevel",
    # Intelligence
    "Entity", "Keyword", "Topic", "EmotionAnalysis", "ThreatIndicator", "RiskScore",
    "ConversationSummary", "RelationshipGraph", "TimelineEvent",
    "InvestigationRecommendation", "EmbeddingMetadata",
    "ThreatCategory", "EmotionType", "SentimentType",
    # Evidence
    "EvidenceFile", "ChainOfCustodyEvent", "Report", "ReportExport", "EvidenceType",
    # Audit
    "AuditLog", "Notification", "SystemAlert",
]


