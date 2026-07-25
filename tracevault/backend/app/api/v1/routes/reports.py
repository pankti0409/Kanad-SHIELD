"""
TraceVault Reports API Routes
DB-backed routes for listing, downloading, and managing investigation reports.
"""
from __future__ import annotations

import math
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select, func, desc

from app.auth.dependencies import CurrentUser, DBSession
from app.config import get_settings
from app.models.evidence import Report
from app.models.recording import Recording

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportResponse(BaseModel):
    id: str
    title: str
    case_id: Optional[str]
    recording_id: Optional[str]
    report_type: str
    status: str
    created_by: str
    created_at: str
    content: Optional[str]

    @classmethod
    def from_model(cls, r: Report) -> "ReportResponse":
        return cls(
            id=r.id,
            title=r.title,
            case_id=r.case_id,
            recording_id=r.recording_id,
            report_type=r.report_type,
            status=r.status,
            created_by=r.created_by,
            created_at=r.created_at.isoformat(),
            content=r.content,
        )


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
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    case_id: Optional[str] = Query(default=None),
) -> ReportListResponse:
    """List all generated investigation reports from DB."""
    q = select(Report).where(Report.is_deleted == False)
    count_q = select(func.count()).select_from(Report).where(Report.is_deleted == False)

    if case_id:
        q = q.where(Report.case_id == case_id)
        count_q = count_q.where(Report.case_id == case_id)

    total_res = await db.execute(count_q)
    total = total_res.scalar_one()

    offset = (page - 1) * page_size
    q = q.order_by(desc(Report.created_at)).offset(offset).limit(page_size)
    result = await db.execute(q)
    reports = list(result.scalars().all())

    return ReportListResponse(
        items=[ReportResponse.from_model(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED, summary="Generate report")
async def generate_report(
    db: DBSession,
    current_user: CurrentUser,
    body: GenerateReportRequest,
) -> ReportResponse:
    """Generate a custom investigation report from one or more recordings."""
    import uuid
    from app.services.report_generator import ReportGeneratorService
    from app.models.recording import TranscriptSegment

    if not body.recording_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one recording_id is required to generate a report.",
        )

    # Load recording
    rec_id = body.recording_ids[0]
    rec_res = await db.execute(select(Recording).where(Recording.id == rec_id))
    recording = rec_res.scalar_one_or_none()

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {rec_id} not found.",
        )

    # Load transcript segments
    from app.models.recording import Transcript
    tr_res = await db.execute(select(Transcript).where(Transcript.recording_id == rec_id))
    transcript = tr_res.scalar_one_or_none()

    segments = []
    if transcript:
        seg_res = await db.execute(
            select(TranscriptSegment)
            .where(TranscriptSegment.transcript_id == transcript.id)
            .order_by(TranscriptSegment.sequence_number)
        )
        segments_raw = list(seg_res.scalars().all())
        segments = [
            {
                "start_time": s.start_time,
                "end_time": s.end_time,
                "speaker_label": s.speaker_label or "Speaker",
                "text": s.text,
                "confidence": s.confidence,
                "has_threat": s.has_threat,
                "has_entity": s.has_entity,
            }
            for s in segments_raw
        ]

    # Generate the report files and save to DB
    from app.ai.intelligence.call_analyzer import CallAnalyzer
    analyzer = CallAnalyzer()
    analysis = analyzer.analyze(transcript.full_text if transcript else "")

    report_svc = ReportGeneratorService()
    pdf_path = await report_svc.generate_report(recording, segments, analysis)

    # Query back the newly generated report
    rep_res = await db.execute(
        select(Report)
        .where(Report.recording_id == rec_id)
        .order_by(desc(Report.created_at))
    )
    report = rep_res.scalars().first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate and save report.",
        )

    return ReportResponse.from_model(report)


@router.get("/download/{report_id}", summary="Download report file")
async def download_report(
    report_id: str,
    db: DBSession,
    current_user: CurrentUser,
    format: str = Query(default="pdf"),
) -> FileResponse:
    """Download the generated report in pdf, csv, or json format."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    file_path_str: Optional[str] = None
    media_type = "application/octet-stream"
    filename = f"report_{report_id}.{format}"

    if format == "pdf":
        file_path_str = report.pdf_path
        media_type = "application/pdf"
    elif format == "csv":
        file_path_str = report.csv_path
        media_type = "text/csv"
    elif format == "json":
        file_path_str = report.json_path
        media_type = "application/json"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{format}'. Use pdf, csv, or json.",
        )

    if not file_path_str or not Path(file_path_str).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report file not found on disk for format '{format}'.",
        )

    return FileResponse(
        path=file_path_str,
        media_type=media_type,
        filename=filename,
    )
