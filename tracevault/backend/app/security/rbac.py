"""
TraceVault RBAC — Role-Based Access Control
Defines permissions for each role.
All permission checks happen at both API and service layer.
"""
from __future__ import annotations

from enum import Enum as PyEnum
from typing import Optional

from app.models.user import UserRole


class Permission(str, PyEnum):
    """All available permissions in TraceVault."""

    # Cases
    CASE_VIEW = "case:view"
    CASE_CREATE = "case:create"
    CASE_EDIT = "case:edit"
    CASE_ARCHIVE = "case:archive"
    CASE_DELETE = "case:delete"
    CASE_MANAGE_MEMBERS = "case:manage_members"

    # Evidence & Recordings
    EVIDENCE_VIEW = "evidence:view"
    EVIDENCE_UPLOAD = "evidence:upload"
    EVIDENCE_DELETE = "evidence:delete"
    EVIDENCE_VERIFY_INTEGRITY = "evidence:verify_integrity"
    RECORDING_VIEW = "recording:view"
    RECORDING_UPLOAD = "recording:upload"
    RECORDING_DELETE = "recording:delete"

    # Transcripts
    TRANSCRIPT_VIEW = "transcript:view"
    TRANSCRIPT_CORRECT = "transcript:correct"

    # AI Intelligence
    AI_VIEW = "ai:view"
    AI_REVIEW_THREATS = "ai:review_threats"
    AI_REVIEW_ENTITIES = "ai:review_entities"
    AI_COPILOT = "ai:copilot"
    AI_MANAGE_MODELS = "ai:manage_models"

    # Knowledge Graph
    KNOWLEDGE_GRAPH_VIEW = "knowledge_graph:view"
    KNOWLEDGE_GRAPH_EDIT = "knowledge_graph:edit"

    # Reports
    REPORT_VIEW = "report:view"
    REPORT_CREATE = "report:create"
    REPORT_APPROVE = "report:approve"
    REPORT_REJECT = "report:reject"
    REPORT_DELETE = "report:delete"

    # Exports
    EXPORT_CREATE = "export:create"
    EXPORT_DOWNLOAD = "export:download"

    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"

    # Notes
    NOTE_VIEW = "note:view"
    NOTE_CREATE = "note:create"
    NOTE_EDIT_OWN = "note:edit_own"
    NOTE_DELETE_OWN = "note:delete_own"
    NOTE_EDIT_ALL = "note:edit_all"

    # Tasks
    TASK_VIEW = "task:view"
    TASK_CREATE = "task:create"
    TASK_COMPLETE = "task:complete"
    TASK_DELETE = "task:delete"

    # Users
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_EDIT = "user:edit"
    USER_DEACTIVATE = "user:deactivate"
    USER_DELETE = "user:delete"
    USER_MANAGE_ROLES = "user:manage_roles"
    USER_RESET_PASSWORD = "user:reset_password"

    # Audit Logs
    AUDIT_LOG_VIEW = "audit_log:view"

    # Settings
    SETTINGS_VIEW = "settings:view"
    SETTINGS_EDIT = "settings:edit"

    # Security
    SESSION_VIEW_OWN = "session:view_own"
    SESSION_TERMINATE_OWN = "session:terminate_own"
    SESSION_TERMINATE_ANY = "session:terminate_any"

    # System
    SYSTEM_HEALTH_VIEW = "system:health_view"
    SYSTEM_ADMIN = "system:admin"


# ===========================================================================
# Role → Permission mapping
# Higher privilege roles include all lower permissions via inheritance.
# ===========================================================================

_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.READ_ONLY: {
        Permission.CASE_VIEW,
        Permission.EVIDENCE_VIEW,
        Permission.RECORDING_VIEW,
        Permission.TRANSCRIPT_VIEW,
        Permission.AI_VIEW,
        Permission.KNOWLEDGE_GRAPH_VIEW,
        Permission.REPORT_VIEW,
        Permission.ANALYTICS_VIEW,
        Permission.NOTE_VIEW,
        Permission.TASK_VIEW,
        Permission.AUDIT_LOG_VIEW,
        Permission.SETTINGS_VIEW,
        Permission.SESSION_VIEW_OWN,
        Permission.SESSION_TERMINATE_OWN,
    },
    UserRole.ANALYST: {
        Permission.CASE_VIEW,
        Permission.EVIDENCE_VIEW,
        Permission.EVIDENCE_VERIFY_INTEGRITY,
        Permission.RECORDING_VIEW,
        Permission.TRANSCRIPT_VIEW,
        Permission.AI_VIEW,
        Permission.AI_REVIEW_THREATS,
        Permission.AI_REVIEW_ENTITIES,
        Permission.AI_COPILOT,
        Permission.KNOWLEDGE_GRAPH_VIEW,
        Permission.REPORT_VIEW,
        Permission.REPORT_CREATE,
        Permission.EXPORT_CREATE,
        Permission.EXPORT_DOWNLOAD,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_EXPORT,
        Permission.NOTE_VIEW,
        Permission.NOTE_CREATE,
        Permission.NOTE_EDIT_OWN,
        Permission.NOTE_DELETE_OWN,
        Permission.TASK_VIEW,
        Permission.TASK_CREATE,
        Permission.TASK_COMPLETE,
        Permission.AUDIT_LOG_VIEW,
        Permission.SETTINGS_VIEW,
        Permission.SESSION_VIEW_OWN,
        Permission.SESSION_TERMINATE_OWN,
    },
    UserRole.LEGAL_OFFICER: {
        Permission.CASE_VIEW,
        Permission.EVIDENCE_VIEW,
        Permission.EVIDENCE_VERIFY_INTEGRITY,
        Permission.RECORDING_VIEW,
        Permission.TRANSCRIPT_VIEW,
        Permission.AI_VIEW,
        Permission.AI_COPILOT,
        Permission.KNOWLEDGE_GRAPH_VIEW,
        Permission.REPORT_VIEW,
        Permission.REPORT_CREATE,
        Permission.REPORT_APPROVE,
        Permission.EXPORT_CREATE,
        Permission.EXPORT_DOWNLOAD,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_EXPORT,
        Permission.NOTE_VIEW,
        Permission.NOTE_CREATE,
        Permission.NOTE_EDIT_OWN,
        Permission.AUDIT_LOG_VIEW,
        Permission.SETTINGS_VIEW,
        Permission.SESSION_VIEW_OWN,
        Permission.SESSION_TERMINATE_OWN,
    },
    UserRole.INVESTIGATOR: {
        Permission.CASE_VIEW,
        Permission.CASE_CREATE,
        Permission.CASE_EDIT,
        Permission.EVIDENCE_VIEW,
        Permission.EVIDENCE_UPLOAD,
        Permission.EVIDENCE_VERIFY_INTEGRITY,
        Permission.RECORDING_VIEW,
        Permission.RECORDING_UPLOAD,
        Permission.TRANSCRIPT_VIEW,
        Permission.TRANSCRIPT_CORRECT,
        Permission.AI_VIEW,
        Permission.AI_REVIEW_THREATS,
        Permission.AI_REVIEW_ENTITIES,
        Permission.AI_COPILOT,
        Permission.KNOWLEDGE_GRAPH_VIEW,
        Permission.KNOWLEDGE_GRAPH_EDIT,
        Permission.REPORT_VIEW,
        Permission.REPORT_CREATE,
        Permission.EXPORT_CREATE,
        Permission.EXPORT_DOWNLOAD,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_EXPORT,
        Permission.NOTE_VIEW,
        Permission.NOTE_CREATE,
        Permission.NOTE_EDIT_OWN,
        Permission.NOTE_DELETE_OWN,
        Permission.TASK_VIEW,
        Permission.TASK_CREATE,
        Permission.TASK_COMPLETE,
        Permission.TASK_DELETE,
        Permission.AUDIT_LOG_VIEW,
        Permission.SETTINGS_VIEW,
        Permission.SESSION_VIEW_OWN,
        Permission.SESSION_TERMINATE_OWN,
    },
    UserRole.SENIOR_INVESTIGATOR: {
        Permission.CASE_VIEW,
        Permission.CASE_CREATE,
        Permission.CASE_EDIT,
        Permission.CASE_ARCHIVE,
        Permission.CASE_MANAGE_MEMBERS,
        Permission.EVIDENCE_VIEW,
        Permission.EVIDENCE_UPLOAD,
        Permission.EVIDENCE_DELETE,
        Permission.EVIDENCE_VERIFY_INTEGRITY,
        Permission.RECORDING_VIEW,
        Permission.RECORDING_UPLOAD,
        Permission.RECORDING_DELETE,
        Permission.TRANSCRIPT_VIEW,
        Permission.TRANSCRIPT_CORRECT,
        Permission.AI_VIEW,
        Permission.AI_REVIEW_THREATS,
        Permission.AI_REVIEW_ENTITIES,
        Permission.AI_COPILOT,
        Permission.KNOWLEDGE_GRAPH_VIEW,
        Permission.KNOWLEDGE_GRAPH_EDIT,
        Permission.REPORT_VIEW,
        Permission.REPORT_CREATE,
        Permission.REPORT_APPROVE,
        Permission.EXPORT_CREATE,
        Permission.EXPORT_DOWNLOAD,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_EXPORT,
        Permission.NOTE_VIEW,
        Permission.NOTE_CREATE,
        Permission.NOTE_EDIT_OWN,
        Permission.NOTE_DELETE_OWN,
        Permission.NOTE_EDIT_ALL,
        Permission.TASK_VIEW,
        Permission.TASK_CREATE,
        Permission.TASK_COMPLETE,
        Permission.TASK_DELETE,
        Permission.USER_VIEW,
        Permission.AUDIT_LOG_VIEW,
        Permission.SETTINGS_VIEW,
        Permission.SESSION_VIEW_OWN,
        Permission.SESSION_TERMINATE_OWN,
        Permission.SYSTEM_HEALTH_VIEW,
    },
    UserRole.SUPERVISOR: {
        Permission.CASE_VIEW,
        Permission.CASE_CREATE,
        Permission.CASE_EDIT,
        Permission.CASE_ARCHIVE,
        Permission.CASE_DELETE,
        Permission.CASE_MANAGE_MEMBERS,
        Permission.EVIDENCE_VIEW,
        Permission.EVIDENCE_UPLOAD,
        Permission.EVIDENCE_DELETE,
        Permission.EVIDENCE_VERIFY_INTEGRITY,
        Permission.RECORDING_VIEW,
        Permission.RECORDING_UPLOAD,
        Permission.RECORDING_DELETE,
        Permission.TRANSCRIPT_VIEW,
        Permission.TRANSCRIPT_CORRECT,
        Permission.AI_VIEW,
        Permission.AI_REVIEW_THREATS,
        Permission.AI_REVIEW_ENTITIES,
        Permission.AI_COPILOT,
        Permission.KNOWLEDGE_GRAPH_VIEW,
        Permission.KNOWLEDGE_GRAPH_EDIT,
        Permission.REPORT_VIEW,
        Permission.REPORT_CREATE,
        Permission.REPORT_APPROVE,
        Permission.REPORT_REJECT,
        Permission.REPORT_DELETE,
        Permission.EXPORT_CREATE,
        Permission.EXPORT_DOWNLOAD,
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_EXPORT,
        Permission.NOTE_VIEW,
        Permission.NOTE_CREATE,
        Permission.NOTE_EDIT_OWN,
        Permission.NOTE_DELETE_OWN,
        Permission.NOTE_EDIT_ALL,
        Permission.TASK_VIEW,
        Permission.TASK_CREATE,
        Permission.TASK_COMPLETE,
        Permission.TASK_DELETE,
        Permission.USER_VIEW,
        Permission.USER_CREATE,
        Permission.USER_EDIT,
        Permission.USER_RESET_PASSWORD,
        Permission.AUDIT_LOG_VIEW,
        Permission.SETTINGS_VIEW,
        Permission.SETTINGS_EDIT,
        Permission.SESSION_VIEW_OWN,
        Permission.SESSION_TERMINATE_OWN,
        Permission.SESSION_TERMINATE_ANY,
        Permission.SYSTEM_HEALTH_VIEW,
    },
    UserRole.SYSTEM_ADMIN: set(Permission),  # All permissions
}


def get_role_permissions(role: UserRole) -> set[Permission]:
    """Return the complete set of permissions for a given role."""
    return _PERMISSIONS.get(role, set())


def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in get_role_permissions(role)


def require_permission(
    user_role: UserRole,
    permission: Permission,
) -> None:
    """
    Assert that a user role has the required permission.
    Raises: PermissionError if not authorized.
    """
    if not has_permission(user_role, permission):
        raise PermissionError(
            f"Role '{user_role}' does not have permission '{permission}'."
        )
