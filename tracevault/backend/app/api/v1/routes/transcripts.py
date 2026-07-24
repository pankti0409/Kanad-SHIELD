"""
TraceVault Transcripts API Routes
List and retrieve transcripts with segment detail.
"""
from __future__ import annotations
import math
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from app.auth.dependencies import CurrentUser, DBSession

router = APIRouter(prefix="/transcripts", tags=["Transcripts"])


class TranscriptSegmentResponse(BaseModel):
    id: str
    speaker_label: str
    text: str
    start_time: float
    end_time: float
    confidence: float
    language: str
    emotion: Optional[str]


class TranscriptResponse(BaseModel):
    id: str
    recording_id: str
    case_id: Optional[str]
    language: str
    full_text: str
    duration_seconds: float
    status: str
    segments: list[TranscriptSegmentResponse]
    created_at: str


class TranscriptListResponse(BaseModel):
    items: list[dict]
    total: int
    page: int
    page_size: int
    pages: int


@router.get("", response_model=TranscriptListResponse, summary="List transcripts")
async def list_transcripts(
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    case_id: Optional[str] = Query(default=None),
) -> TranscriptListResponse:
    """List all transcripts the current user has access to."""
    return TranscriptListResponse(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
        pages=1,
    )


@router.get("/{transcript_id}", response_model=TranscriptResponse, summary="Get transcript detail")
async def get_transcript(
    transcript_id: uuid.UUID,
    current_user: CurrentUser,
) -> TranscriptResponse:
    """Get transcript with full segment breakdown."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Transcript not found.",
    )
