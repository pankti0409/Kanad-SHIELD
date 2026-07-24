"""
TraceVault Recordings API Routes
List, upload, and manage call recordings with SHA-256 evidence integrity.
"""
from __future__ import annotations
import hashlib
import uuid
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile, status
from pydantic import BaseModel
from datetime import datetime, timezone
from app.auth.dependencies import CurrentUser, DBSession
from app.config import get_settings

from app.ai.transcription.whisper_engine import WhisperTranscriptionEngine
from app.ai.diarization.diarizer import SpeakerDiarizer
from app.ai.intelligence.call_analyzer import CallAnalyzer
from app.services.report_generator import ReportGeneratorService

router = APIRouter(prefix="/recordings", tags=["Recordings"])

ALLOWED_EXTENSIONS = {
    ".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".amr", ".wma", ".mp4", ".mkv", ".webm", ".3gp"
}


class RecordingResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    sha256_hash: str
    duration_seconds: Optional[float]
    language: Optional[str]
    status: str
    case_id: Optional[str]
    warrant_number: Optional[str]
    created_at: str


class RecordingListResponse(BaseModel):
    items: list[RecordingResponse]
    total: int
    page: int
    page_size: int
    pages: int


class TranscriptSegmentResponse(BaseModel):
    id: str
    transcript_id: str
    speaker_label: str
    sequence_number: int
    start_time: float
    end_time: float
    text: str
    confidence: float
    has_threat: bool
    has_entity: bool
    has_keyword: bool
    word_count: int
    character_count: int


class CallAnalysisResponse(BaseModel):
    transcriptDateTime: str
    analysisDateTime: str
    summary: str
    topicDiscussed: Optional[str] = "General Conversation"
    threatPresent: bool
    threatCategory: str
    threatDetails: str
    locationsDiscussed: list[str]
    timesDiscussed: list[str]
    otherInfo: str


class RecordingUploadResponse(BaseModel):
    recording: RecordingResponse
    segments: List[TranscriptSegmentResponse]
    analysis: CallAnalysisResponse


@router.get("", response_model=RecordingListResponse, summary="List recordings")
async def list_recordings(
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    case_id: Optional[str] = Query(default=None),
) -> RecordingListResponse:
    """List all recordings."""
    return RecordingListResponse(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
        pages=1,
    )


@router.post("/upload", response_model=RecordingUploadResponse, status_code=status.HTTP_201_CREATED, summary="Upload recording")
async def upload_recording(
    request: Request,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    case_id: Optional[str] = Query(default=None),
    warrant_number: Optional[str] = Query(default=None),
    language: Optional[str] = Query(default="auto"),
) -> RecordingUploadResponse:
    """
    Upload call recording and trigger AI Whisper Speech-to-Text & Diarization pipeline.
    Calculates SHA-256 for evidence chain of custody and performs intelligence extraction.
    """
    settings = get_settings()

    # Validate extension
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported format '{suffix}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    file_size = len(contents)
    sha256_hash = hashlib.sha256(contents).hexdigest()
    recording_id = f"rec-{uuid.uuid4()}"

    # Write to upload directory
    storage_dir = Path(settings.storage.UPLOAD_DIRECTORY)
    storage_dir.mkdir(parents=True, exist_ok=True)
    dest_path = storage_dir / f"{recording_id}{suffix}"
    dest_path.write_bytes(contents)

    # Pipeline Step 1: Speech-to-Text with Whisper Engine
    stt_engine = WhisperTranscriptionEngine(model_size="base")
    stt_res = await stt_engine.transcribe(str(dest_path), language=language or "auto")

    # Pipeline Step 2: Speaker Diarization
    diarizer = SpeakerDiarizer()
    raw_segments = await diarizer.diarize_segments(str(dest_path), stt_res.get("segments", []))

    # Convert to response segment models
    segment_responses = [
        TranscriptSegmentResponse(
            id=s["id"],
            transcript_id=s["transcript_id"],
            speaker_label=s["speaker_label"],
            sequence_number=s["sequence_number"],
            start_time=s["start_time"],
            end_time=s["end_time"],
            text=s["text"],
            confidence=s["confidence"],
            has_threat=s["has_threat"],
            has_entity=s["has_entity"],
            has_keyword=s["has_keyword"],
            word_count=s["word_count"],
            character_count=s["character_count"],
        )
        for s in raw_segments
    ]

    # Pipeline Step 3: Intelligence & Details Extraction
    analyzer = CallAnalyzer()
    analysis_dict = analyzer.analyze(
        full_text=stt_res.get("full_text", ""),
        filename=file.filename or dest_path.name,
        sha256_hash=sha256_hash,
        warrant_number=warrant_number or "",
    )

    analysis_response = CallAnalysisResponse(
        transcriptDateTime=analysis_dict["transcriptDateTime"],
        analysisDateTime=analysis_dict["analysisDateTime"],
        summary=analysis_dict["summary"],
        topicDiscussed=analysis_dict.get("topicDiscussed", "General Conversation"),
        threatPresent=analysis_dict["threatPresent"],
        threatCategory=analysis_dict["threatCategory"],
        threatDetails=analysis_dict["threatDetails"],
        locationsDiscussed=analysis_dict["locationsDiscussed"],
        timesDiscussed=analysis_dict["timesDiscussed"],
        otherInfo=analysis_dict["otherInfo"],
    )

    # Pipeline Step 4: Generate Forensic Case Report
    report_svc = ReportGeneratorService()
    report_pdf_path = storage_dir / f"report_{recording_id}.pdf"
    report_svc.generate_report_pdf(
        output_path=str(report_pdf_path),
        recording_meta={
            "filename": file.filename or dest_path.name,
            "sha256_hash": sha256_hash,
            "duration_seconds": stt_res.get("duration_seconds", 0.0),
            "warrant_number": warrant_number or "WR-UNASSIGNED",
            "case_id": case_id or "UNASSIGNED",
            "language": stt_res.get("language", "auto"),
        },
        segments=raw_segments,
        analysis=analysis_dict,
    )

    now = datetime.now(timezone.utc)
    rec_resp = RecordingResponse(
        id=recording_id,
        filename=file.filename or f"recording{suffix}",
        file_size=file_size,
        sha256_hash=sha256_hash,
        duration_seconds=stt_res.get("duration_seconds", 0.0),
        language=stt_res.get("language", language),
        status="completed",
        case_id=case_id or "",
        warrant_number=warrant_number or "WR-2026-TEMP",
        created_at=now.isoformat(),
    )

    return RecordingUploadResponse(
        recording=rec_resp,
        segments=segment_responses,
        analysis=analysis_response,
    )

