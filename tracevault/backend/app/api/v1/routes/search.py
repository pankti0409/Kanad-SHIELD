"""
TraceVault Search API Routes
Cross-resource full-text search across cases, recordings, transcripts, and entities.
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import or_, select
from app.auth.dependencies import CurrentUser, DBSession
from app.models.case import Case

router = APIRouter(prefix="/search", tags=["Search"])


class SearchResult(BaseModel):
    type: str
    id: str
    title: str
    subtitle: str
    href: str


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]


@router.get("", response_model=SearchResponse, summary="Full-text cross-resource search")
async def search(
    db: DBSession,
    current_user: CurrentUser,
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
) -> SearchResponse:
    """Search across cases, recordings, transcripts, and entities."""
    results: list[SearchResult] = []
    pattern = f"%{q}%"

    # Search cases
    cases_result = await db.execute(
        select(Case).where(
            Case.is_deleted == False,
            or_(
                Case.title.ilike(pattern),
                Case.case_number.ilike(pattern),
                Case.description.ilike(pattern),
            )
        ).limit(limit)
    )
    for case in cases_result.scalars().all():
        results.append(SearchResult(
            type="case",
            id=str(case.id),
            title=case.title,
            subtitle=f"{case.case_number} · {case.priority.value if case.priority else 'medium'} priority",
            href=f"/cases/{case.id}",
        ))

    return SearchResponse(query=q, total=len(results), results=results)
