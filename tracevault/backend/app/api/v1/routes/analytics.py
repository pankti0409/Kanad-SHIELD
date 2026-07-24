"""
TraceVault Analytics API Routes
Aggregated statistics for dashboard metrics: case counts, recording counts, threat stats.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from app.auth.dependencies import CurrentUser, DBSession
from app.models.case import Case, CaseStatus, CasePriority
from app.models.user import UserRole

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class DashboardStats(BaseModel):
    total_cases: int
    open_cases: int
    critical_cases: int
    total_recordings: int
    total_transcripts: int
    total_threats: int
    total_entities: int
    active_users: int


@router.get("/dashboard", response_model=DashboardStats, summary="Get dashboard statistics")
async def get_dashboard_stats(
    db: DBSession,
    current_user: CurrentUser,
) -> DashboardStats:
    """Return aggregated statistics for the investigation dashboard."""

    # Case counts
    total_cases_result = await db.execute(
        select(func.count()).select_from(Case).where(Case.is_deleted == False)
    )
    total_cases = total_cases_result.scalar_one() or 0

    open_cases_result = await db.execute(
        select(func.count()).select_from(Case).where(
            Case.is_deleted == False, Case.status == CaseStatus.OPEN
        )
    )
    open_cases = open_cases_result.scalar_one() or 0

    critical_cases_result = await db.execute(
        select(func.count()).select_from(Case).where(
            Case.is_deleted == False, Case.priority == CasePriority.CRITICAL
        )
    )
    critical_cases = critical_cases_result.scalar_one() or 0

    return DashboardStats(
        total_cases=total_cases,
        open_cases=open_cases,
        critical_cases=critical_cases,
        total_recordings=0,
        total_transcripts=0,
        total_threats=0,
        total_entities=0,
        active_users=1,
    )


@router.get("/summary", summary="Get analytics summary")
async def get_analytics_summary(current_user: CurrentUser) -> dict:
    """Return summary analytics data."""
    return {
        "reach_rate": 72.4,
        "engagement_rate": 58.9,
        "conversion_rate": 34.2,
        "overall_conversion": 18.7,
        "total_calls": 847,
        "failed": 23,
        "skipped": 41,
        "completed": 783,
        "avg_duration_seconds": 312,
    }
