"""
TraceVault Intelligence API Routes
Entity extractions, threat indicators, and voice analytics.
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.auth.dependencies import CurrentUser

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])


class EntityItem(BaseModel):
    id: str
    entity_type: str
    value: str
    confidence: float
    case_id: Optional[str]
    recording_id: Optional[str]
    segment_timestamp: Optional[str]


class ThreatItem(BaseModel):
    id: str
    category: str
    severity: str
    evidence_text: str
    confidence: float
    case_id: Optional[str]
    timestamp: Optional[str]


@router.get("/entities", summary="List extracted entities")
async def list_entities(
    current_user: CurrentUser,
    case_id: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict:
    """List NER-extracted entities from transcripts."""
    return {"items": [], "total": 0}


@router.get("/threats", summary="List detected threat indicators")
async def list_threats(
    current_user: CurrentUser,
    case_id: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict:
    """List detected threat and criminal behavior indicators."""
    return {"items": [], "total": 0}


@router.get("/summary", summary="Get intelligence summary")
async def get_intelligence_summary(current_user: CurrentUser) -> dict:
    """Return a summary of intelligence findings across all cases."""
    return {
        "total_entities": 0,
        "total_threats": 0,
        "critical_threats": 0,
        "entity_types": {},
        "threat_categories": {},
    }
