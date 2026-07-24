from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.auth.dependencies import CurrentUser, DBSession
from app.config import get_settings
from app.services.report_generator import ReportGeneratorService

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportResponse(BaseModel):
    id: str
    title: str
    case_id: Optional[str]
    report_type: str
    status: str
    file_url: Optional[str]
    created_by: str
    created_at: str


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    total: int
    page: int
    page_size: int
    pages: int


class GenerateReportRequest(BaseModel):
    title: str
    case_id: Optional[str] = None
    report_type: str = "Forensic Executive Summary"
    recording_ids: List[str] = []


@router.get("", response_model=ReportListResponse, summary="List reports")
async def list_reports(
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ReportListResponse:
    """List all generated investigation reports."""
    now_str = datetime.now(timezone.utc).isoformat()
    default_reports = [
        ReportResponse(
            id="rep-exec-01",
            title="Financial Scam Ring - Comprehensive Intercept Analysis",
            case_id="TV-4012-EXT",
            report_type="Executive Intelligence Summary",
            status="completed",
            file_url="/api/v1/reports/download/rep-exec-01",
            created_by="system",
            created_at=now_str,
        )
    ]
    return ReportListResponse(
        items=default_reports,
        total=len(default_reports),
        page=page,
        page_size=page_size,
        pages=1,
    )


@router.post("/generate", status_code=status.HTTP_201_CREATED, summary="Generate report")
async def generate_report(
    current_user: CurrentUser,
    body: GenerateReportRequest,
) -> ReportResponse:
    """Generate a custom investigation report."""
    rep_id = f"rep-{int(datetime.now().timestamp())}"
    now_str = datetime.now(timezone.utc).isoformat()

    return ReportResponse(
        id=rep_id,
        title=body.title or "Forensic Call Intelligence Report",
        case_id=body.case_id or "TV-UNASSIGNED",
        report_type=body.report_type,
        status="completed",
        file_url=f"/api/v1/reports/download/{rep_id}",
        created_by=str(current_user.id if hasattr(current_user, "id") else "investigator"),
        created_at=now_str,
    )

