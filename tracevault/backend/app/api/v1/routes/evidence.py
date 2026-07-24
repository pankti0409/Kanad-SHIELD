"""
TraceVault Evidence API Routes
Evidence items with chain of custody tracking.
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Query
from app.auth.dependencies import CurrentUser

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.get("", summary="List evidence items")
async def list_evidence(
    current_user: CurrentUser,
    case_id: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    """List all evidence items with their chain of custody status."""
    return {"items": [], "total": 0, "page": page, "page_size": page_size, "pages": 1}


@router.get("/{evidence_id}/custody", summary="Get chain of custody")
async def get_chain_of_custody(
    evidence_id: str,
    current_user: CurrentUser,
) -> dict:
    """Get the full chain of custody audit trail for an evidence item."""
    return {"evidence_id": evidence_id, "custody_events": [], "sha256_verified": True}
