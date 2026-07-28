"""
TraceVault Recordings API Routes
Proper DB-backed upload, processing, listing, retrieval, and deletion.
Processing runs via asyncio.create_task() for dev (no Redis required).
"""
from __future__ import annotations

import asyncio
import hashlib
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import and_, desc, func, or_, select, update

from app.auth.dependencies import CurrentUser, DBSession
from app.config import get_settings
from app.models.recording import (
    ProcessingStatus,
    Recording,
    Transcript,
    TranscriptSegment,
)

router = APIRouter(prefix="/recordings", tags=["Recordings"])

ALLOWED_EXTENSIONS = {
    ".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus",
    ".amr", ".wma", ".mp4", ".mkv", ".webm", ".3gp", ".aac",
    ".mpeg",
}

MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB


# ============================================================
# Pydantic Response Schemas
# ============================================================

class TranscriptSegmentOut(BaseModel):
    id: str
    transcript_id: str
    speaker_label: Optional[str]
    sequence_number: int
    start_time: float
    end_time: float
    text: str
    confidence: float
    has_threat: bool
    has_entity: bool
    has_keyword: bool
    emotion: Optional[str]
    word_count: int
    character_count: int

    model_config = {"from_attributes": True}


class TranscriptOut(BaseModel):
    id: str
    recording_id: str
    full_text: str
    language: str
    confidence: float
    word_count: int
    model_used: str
    segments: list[TranscriptSegmentOut] = []

    model_config = {"from_attributes": True}


class RecordingResponse(BaseModel):
    id: str
    filename: str
    file_size_bytes: int
    sha256_hash: str
    duration_seconds: Optional[float]
    detected_language: Optional[str]
    processing_status: str
    processing_progress: int
    processing_error: Optional[str]
    risk_level: Optional[str]
    risk_score: Optional[float]
    threat_count: int
    speaker_count: int
    word_count: int
    case_id: Optional[str]
    warrant_number: Optional[str]
    uploaded_by_id: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, r: Recording) -> "RecordingResponse":
        return cls(
            id=r.id,
            filename=r.original_filename,
            file_size_bytes=r.file_size_bytes,
            sha256_hash=r.sha256_hash,
            duration_seconds=r.duration_seconds,
            detected_language=r.detected_language,
            processing_status=r.processing_status.value if r.processing_status else "queued",
            processing_progress=r.processing_progress,
            processing_error=r.processing_error,
            risk_level=r.risk_level.value if r.risk_level else None,
            risk_score=r.risk_score,
            threat_count=r.threat_count,
            speaker_count=r.speaker_count,
            word_count=r.word_count,
            case_id=r.case_id,
            warrant_number=r.warrant_number,
            uploaded_by_id=r.uploaded_by_id,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )


class RecordingListResponse(BaseModel):
    items: list[RecordingResponse]
    total: int
    page: int
    page_size: int
    pages: int


class RecordingUploadResponse(BaseModel):
    recording: RecordingResponse
    message: str
    task_id: Optional[str] = None


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


class RecordingDetailResponse(BaseModel):
    recording: RecordingResponse
    transcript: Optional[TranscriptOut] = None
    analysis: Optional[CallAnalysisResponse] = None


# ============================================================
# Background Pipeline Task
# ============================================================

async def _run_pipeline(recording_id: str, file_path: str, language: str) -> None:
    """
    Background AI pipeline for a recording.
    Stages: preprocess → transcribe → diarize → analyze → report → complete
    Updates recording.processing_status + processing_progress in DB at each stage.
    """
    from app.database.engine import AsyncSessionLocal
    from app.models.recording import Speaker
    from app.models.intelligence import (
        ThreatIndicator, Entity, Keyword,
        ConversationSummary, EmotionAnalysis, ThreatCategory,
    )
    from app.models.evidence import Report
    import structlog

    logger = structlog.get_logger(__name__)

    async def _set_status(status: ProcessingStatus, progress: int, error: Optional[str] = None):
        async with AsyncSessionLocal() as s:
            await s.execute(
                update(Recording)
                .where(Recording.id == recording_id)
                .values(
                    processing_status=status,
                    processing_progress=progress,
                    processing_error=error,
                )
            )
            await s.commit()

    try:
        await _set_status(ProcessingStatus.PREPARING, 5)

        # ── Stage 1: Transcription ─────────────────────────────
        await _set_status(ProcessingStatus.TRANSCRIBING, 20)

        from app.ai.transcription.whisper_engine import WhisperTranscriptionEngine
        settings = get_settings()
        model_size = settings.ai.WHISPER_MODEL_SIZE or "base"
        stt_engine = WhisperTranscriptionEngine(model_size=model_size)
        stt_result = await stt_engine.transcribe(file_path, language=language)

        full_text: str = stt_result.get("full_text", "")
        detected_lang: str = stt_result.get("language", "en")
        duration: float = stt_result.get("duration_seconds", 0.0)
        raw_segments: list = stt_result.get("segments", [])

        # Update recording with detected language and duration
        async with AsyncSessionLocal() as s:
            await s.execute(
                update(Recording)
                .where(Recording.id == recording_id)
                .values(
                    detected_language=detected_lang,
                    duration_seconds=duration,
                    word_count=len(full_text.split()),
                )
            )
            await s.commit()

        # ── Stage 2: Diarization ───────────────────────────────
        await _set_status(ProcessingStatus.DETECTING_SPEAKERS, 40)

        from app.ai.diarization.diarizer import SpeakerDiarizer
        diarizer = SpeakerDiarizer()
        diarized_segments = await diarizer.diarize_segments(file_path, raw_segments)

        # Count unique speakers
        unique_speakers = set(s.get("speaker_label", "Speaker_00") for s in diarized_segments)
        speaker_count = len(unique_speakers)

        # ── Stage 3: Intelligence Analysis ────────────────────
        await _set_status(ProcessingStatus.RUNNING_AI, 60)

        from app.ai.intelligence.call_analyzer import CallAnalyzer
        analyzer = CallAnalyzer()
        analysis = analyzer.analyze(
            full_text=full_text,
            segments=diarized_segments,
            language=detected_lang,
        )

        # ── Stage 4: Emotion Analysis ─────────────────────────
        await _set_status(ProcessingStatus.RUNNING_AI, 75)

        try:
            from app.ai.emotion.analyzer import EmotionAnalyzer
            emotion_analyzer = EmotionAnalyzer()
            emotion_results = emotion_analyzer.analyze_segments(diarized_segments)
        except Exception:
            emotion_results = []

        # ── Stage 5: Save All Results to DB ───────────────────
        await _set_status(ProcessingStatus.SAVING_RESULTS, 85)

        async with AsyncSessionLocal() as s:
            # Create Transcript
            transcript = Transcript(
                id=str(uuid.uuid4()),
                recording_id=recording_id,
                full_text=full_text,
                language=detected_lang,
                confidence=stt_result.get("confidence", 0.85),
                word_count=len(full_text.split()),
                character_count=len(full_text),
                duration_seconds=duration,
                model_used=stt_result.get("model_used", "faster-whisper"),
            )
            s.add(transcript)
            await s.flush()

            # Create Speaker records
            speaker_map: dict[str, str] = {}  # label -> speaker_id
            for label in unique_speakers:
                spk_segs = [sg for sg in diarized_segments if sg.get("speaker_label") == label]
                total_dur = sum(
                    sg.get("end_time", 0) - sg.get("start_time", 0) for sg in spk_segs
                )
                speaker = Speaker(
                    id=str(uuid.uuid4()),
                    recording_id=recording_id,
                    speaker_label=label,
                    speaking_duration_seconds=total_dur,
                    turn_count=len(spk_segs),
                )
                s.add(speaker)
                await s.flush()
                speaker_map[label] = speaker.id

            # Create TranscriptSegment records
            emotion_map: dict[int, dict] = {e.get("seg_index", -1): e for e in emotion_results}
            threat_segment_ids: set[str] = set()
            seg_ids: list[str] = []

            for idx, seg in enumerate(diarized_segments):
                label = seg.get("speaker_label", "Speaker_00")
                emo_data = emotion_map.get(idx, {})
                seg_id = str(uuid.uuid4())
                seg_ids.append(seg_id)

                has_threat = seg.get("has_threat", False)
                if has_threat:
                    threat_segment_ids.add(seg_id)

                segment = TranscriptSegment(
                    id=seg_id,
                    transcript_id=transcript.id,
                    speaker_id=speaker_map.get(label),
                    speaker_label=label,
                    sequence_number=idx,
                    start_time=seg.get("start_time", 0.0),
                    end_time=seg.get("end_time", 0.0),
                    text=seg.get("text", ""),
                    confidence=seg.get("confidence", 0.85),
                    word_count=len(seg.get("text", "").split()),
                    character_count=len(seg.get("text", "")),
                    has_threat=has_threat,
                    has_entity=seg.get("has_entity", False),
                    has_keyword=seg.get("has_keyword", False),
                    emotion=emo_data.get("emotion"),
                    emotion_confidence=emo_data.get("confidence"),
                )
                s.add(segment)

            # Save entities
            entities = analysis.get("entities", [])
            for ent in entities:
                entity = Entity(
                    id=str(uuid.uuid4()),
                    recording_id=recording_id,
                    transcript_id=transcript.id,
                    entity_type=ent.get("type", "UNKNOWN"),
                    entity_value=ent.get("value", ""),
                    normalized_value=ent.get("normalized"),
                    speaker_label=ent.get("speaker_label"),
                    timestamp=ent.get("timestamp"),
                    confidence=ent.get("confidence", 0.8),
                    context_sentence=ent.get("context"),
                    model_used=ent.get("model_used", "gemini"),
                )
                s.add(entity)

            # Save threats
            threats = analysis.get("threats", [])
            for threat in threats:
                try:
                    threat_cat = ThreatCategory(threat.get("category", "other"))
                except ValueError:
                    threat_cat = ThreatCategory.OTHER
                t = ThreatIndicator(
                    id=str(uuid.uuid4()),
                    recording_id=recording_id,
                    category=threat_cat,
                    severity=threat.get("severity", "medium"),
                    description=threat.get("description", ""),
                    evidence_text=threat.get("evidence_text", ""),
                    speaker_label=threat.get("speaker_label"),
                    timestamp=threat.get("timestamp"),
                    confidence=threat.get("confidence", 0.7),
                    reasoning=threat.get("reasoning"),
                    model_used=threat.get("model_used", "gemini"),
                )
                s.add(t)

            # Save summary
            summary_text = analysis.get("summary", "")
            if summary_text:
                summary = ConversationSummary(
                    id=str(uuid.uuid4()),
                    recording_id=recording_id,
                    summary_type="full",
                    content=summary_text,
                    confidence=analysis.get("confidence", 0.85),
                    model_used=analysis.get("model_used", "gemini"),
                    language=detected_lang,
                )
                s.add(summary)

            # Update recording counters
            risk_score = analysis.get("risk_score", 0.0)
            risk_level_str = analysis.get("risk_level", "low")
            # Map string risk_level to RiskLevel enum (default to LOW if unrecognized)
            from app.models.recording import RiskLevel
            _risk_level_map = {
                "very_low": RiskLevel.VERY_LOW,
                "low": RiskLevel.LOW,
                "medium": RiskLevel.MEDIUM,
                "high": RiskLevel.HIGH,
                "critical": RiskLevel.CRITICAL,
            }
            risk_level_enum = _risk_level_map.get(risk_level_str.lower(), RiskLevel.LOW)
            await s.execute(
                update(Recording)
                .where(Recording.id == recording_id)
                .values(
                    threat_count=len(threats),
                    entity_count=len(entities),
                    speaker_count=speaker_count,
                    word_count=len(full_text.split()),
                    transcription_confidence=stt_result.get("confidence", 0.85),
                    risk_score=risk_score,
                    risk_level=risk_level_enum,
                )
            )

            await s.commit()

        # ── Stage 6: Generate Report ───────────────────────────
        await _set_status(ProcessingStatus.SAVING_RESULTS, 95)

        try:
            from app.services.report_generator import ReportGeneratorService
            async with AsyncSessionLocal() as s:
                rec_q = await s.execute(select(Recording).where(Recording.id == recording_id))
                rec = rec_q.scalar_one_or_none()
                if rec:
                    report_svc = ReportGeneratorService()
                    report_path = await report_svc.generate_report(
                        recording=rec,
                        segments=diarized_segments,
                        analysis=analysis,
                    )
                    logger.info("Report generated", path=report_path)
        except Exception as e:
            logger.warning("Report generation failed (non-fatal)", error=str(e))

        await _set_status(ProcessingStatus.COMPLETED, 100)
        logger.info("Pipeline completed", recording_id=recording_id)

    except Exception as exc:
        logger.error("Pipeline failed", recording_id=recording_id, error=str(exc))
        await _set_status(ProcessingStatus.FAILED, 0, error=str(exc))


# ============================================================
# Endpoints
# ============================================================

@router.get("", response_model=RecordingListResponse, summary="List recordings")
async def list_recordings(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    case_id: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=200),
    processing_status: Optional[str] = Query(default=None),
    language: Optional[str] = Query(default=None),
) -> RecordingListResponse:
    """List all recordings with pagination, search, and filtering."""
    q = select(Recording).where(Recording.is_deleted == False)
    count_q = select(func.count()).select_from(Recording).where(Recording.is_deleted == False)

    if case_id:
        q = q.where(Recording.case_id == case_id)
        count_q = count_q.where(Recording.case_id == case_id)

    if processing_status:
        q = q.where(Recording.processing_status == processing_status)
        count_q = count_q.where(Recording.processing_status == processing_status)

    if language:
        q = q.where(Recording.detected_language == language)
        count_q = count_q.where(Recording.detected_language == language)

    if search:
        pattern = f"%{search}%"
        q = q.where(Recording.original_filename.ilike(pattern))
        count_q = count_q.where(Recording.original_filename.ilike(pattern))

    total_result = await db.execute(count_q)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    q = q.order_by(desc(Recording.created_at)).offset(offset).limit(page_size)
    result = await db.execute(q)
    recordings = list(result.scalars().all())

    return RecordingListResponse(
        items=[RecordingResponse.from_model(r) for r in recordings],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.post(
    "/upload",
    response_model=RecordingUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload recording",
)
async def upload_recording(
    request: Request,
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    case_id: Optional[str] = Query(default=None),
    warrant_number: Optional[str] = Query(default=None),
    language: Optional[str] = Query(default="auto"),
) -> RecordingUploadResponse:
    """
    Upload a call recording.
    Returns immediately with recording_id and status=queued.
    AI pipeline runs in the background — poll GET /recordings/{id} for progress.
    """
    settings = get_settings()

    # Validate file extension
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported format '{suffix}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Read file content
    contents = await file.read()
    file_size = len(contents)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.storage.MAX_UPLOAD_SIZE_MB} MB.",
        )

    # Compute SHA-256 for evidence integrity
    sha256_hash = hashlib.sha256(contents).hexdigest()
    recording_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())

    # Write to storage
    storage_dir = Path(settings.storage.UPLOAD_DIRECTORY)
    storage_dir.mkdir(parents=True, exist_ok=True)
    dest_path = storage_dir / f"{recording_id}{suffix}"
    dest_path.write_bytes(contents)

    # Detect MIME type (basic fallback)
    mime_map = {
        ".wav": "audio/wav", ".mp3": "audio/mpeg", ".m4a": "audio/mp4",
        ".flac": "audio/flac", ".ogg": "audio/ogg", ".opus": "audio/opus",
        ".aac": "audio/aac", ".wma": "audio/x-ms-wma", ".mp4": "video/mp4",
        ".mkv": "video/x-matroska", ".webm": "video/webm", ".3gp": "video/3gpp",
        ".amr": "audio/amr", ".mpeg": "video/mpeg",
    }
    mime_type = mime_map.get(suffix, "audio/octet-stream")

    # Persist recording record to DB (status=QUEUED)
    now = datetime.now(timezone.utc)
    recording = Recording(
        id=recording_id,
        case_id=case_id.strip() if (case_id and case_id.strip() not in ("None", "null", "undefined", "")) else None,
        uploaded_by_id=current_user.id,
        original_filename=file.filename or f"recording{suffix}",
        stored_filename=f"{recording_id}{suffix}",
        storage_path=str(dest_path),
        sha256_hash=sha256_hash,
        file_size_bytes=file_size,
        mime_type=mime_type,
        processing_status=ProcessingStatus.QUEUED,
        processing_progress=0,
        warrant_number=warrant_number,
        task_id=task_id,
        upload_ip=request.client.host if request.client else None,
    )
    db.add(recording)
    await db.flush()
    await db.refresh(recording)
    # CRITICAL: Commit BEFORE launching the background task.
    # asyncio.create_task() fires immediately — if DB is not committed,
    # the pipeline will fail to find the recording.
    await db.commit()

    # Launch background pipeline (asyncio.create_task = no Redis required)
    asyncio.create_task(
        _run_pipeline(
            recording_id=recording_id,
            file_path=str(dest_path),
            language=language or "auto",
        )
    )

    return RecordingUploadResponse(
        recording=RecordingResponse.from_model(recording),
        message="Recording uploaded and queued for AI processing. Poll GET /recordings/{id} for status updates.",
        task_id=task_id,
    )


@router.get(
    "/{recording_id}",
    response_model=RecordingDetailResponse,
    summary="Get recording details and transcript",
)
async def get_recording(
    recording_id: str,
    db: DBSession,
    current_user: CurrentUser,
    include_transcript: bool = Query(default=True),
) -> RecordingDetailResponse:
    """Get full recording details including transcript if processing is complete."""
    result = await db.execute(
        select(Recording).where(
            Recording.id == recording_id,
            Recording.is_deleted == False,
        )
    )
    recording = result.scalar_one_or_none()
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found.",
        )

    transcript_out: Optional[TranscriptOut] = None

    if include_transcript and recording.processing_status == ProcessingStatus.COMPLETED:
        tr = await db.execute(
            select(Transcript).where(Transcript.recording_id == recording_id)
        )
        transcript = tr.scalar_one_or_none()

        if transcript:
            segs_r = await db.execute(
                select(TranscriptSegment)
                .where(TranscriptSegment.transcript_id == transcript.id)
                .order_by(TranscriptSegment.sequence_number)
            )
            segments = list(segs_r.scalars().all())
            transcript_out = TranscriptOut(
                id=transcript.id,
                recording_id=transcript.recording_id,
                full_text=transcript.full_text,
                language=transcript.language,
                confidence=transcript.confidence,
                word_count=transcript.word_count,
                model_used=transcript.model_used,
                segments=[
                    TranscriptSegmentOut(
                        id=seg.id,
                        transcript_id=seg.transcript_id,
                        speaker_label=seg.speaker_label,
                        sequence_number=seg.sequence_number,
                        start_time=seg.start_time,
                        end_time=seg.end_time,
                        text=seg.text,
                        confidence=seg.confidence,
                        has_threat=seg.has_threat,
                        has_entity=seg.has_entity,
                        has_keyword=seg.has_keyword,
                        emotion=seg.emotion,
                        word_count=seg.word_count,
                        character_count=seg.character_count,
                    )
                    for seg in segments
                ],
            )

    analysis_out: Optional[CallAnalysisResponse] = None

    if recording.processing_status == ProcessingStatus.COMPLETED:
        from app.models.intelligence import ConversationSummary, ThreatIndicator, Entity, Topic

        # Get Summary
        sum_res = await db.execute(
            select(ConversationSummary).where(ConversationSummary.recording_id == recording_id)
        )
        summary_model = sum_res.scalar_one_or_none()
        summary_text = summary_model.content if summary_model else ""

        # Get Threats
        threat_res = await db.execute(
            select(ThreatIndicator).where(ThreatIndicator.recording_id == recording_id)
        )
        threat_models = list(threat_res.scalars().all())
        threat_present = len(threat_models) > 0
        threat_category = threat_models[0].category.value if threat_models else "none"
        threat_details = threat_models[0].description if threat_models else "No threat detected."

        # Get Entities for locations and times
        ent_res = await db.execute(
            select(Entity).where(Entity.recording_id == recording_id)
        )
        ent_models = list(ent_res.scalars().all())
        locations = [ent.entity_value for ent in ent_models if ent.entity_type == "LOCATION"]
        times = [ent.entity_value for ent in ent_models if ent.entity_type == "DATE_TIME"]

        # Topic
        top_res = await db.execute(
            select(Topic).where(Topic.recording_id == recording_id)
        )
        topic_model = top_res.scalar_one_or_none()
        topic_discussed = topic_model.topic_name if topic_model else "General Conversation"

        analysis_out = CallAnalysisResponse(
            transcriptDateTime=recording.created_at.isoformat(),
            analysisDateTime=recording.updated_at.isoformat(),
            summary=summary_text,
            topicDiscussed=topic_discussed,
            threatPresent=threat_present,
            threatCategory=threat_category,
            threatDetails=threat_details,
            locationsDiscussed=list(set(locations)),
            timesDiscussed=list(set(times)),
            otherInfo=f"SHA-256 Checksum: {recording.sha256_hash}",
        )

    return RecordingDetailResponse(
        recording=RecordingResponse.from_model(recording),
        transcript=transcript_out,
        analysis=analysis_out,
    )


@router.delete(
    "/{recording_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete recording",
)
async def delete_recording(
    recording_id: str,
    request: Request,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """Soft delete a recording (marks as deleted, does not remove file)."""
    result = await db.execute(
        select(Recording).where(
            Recording.id == recording_id,
            Recording.is_deleted == False,
        )
    )
    recording = result.scalar_one_or_none()
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found.",
        )

    recording.soft_delete()
    await db.flush()
