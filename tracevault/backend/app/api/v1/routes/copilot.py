"""
TraceVault AI Copilot FastAPI Route Handler
Requires authentication. Secured with CurrentUser dependency.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser, DBSession
from app.ai.copilot.copilot_engine import CopilotEngine

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


class CopilotChatRequest(BaseModel):
    query: str
    case_id: Optional[str] = None
    recording_id: Optional[str] = None
    chat_history: Optional[List[Dict[str, str]]] = None


class CitationItem(BaseModel):
    title: str
    confidence: float


class CopilotChatResponse(BaseModel):
    answer: str
    citations: List[CitationItem]
    suggestions: List[str]
    confidence_score: float
    model_used: str


@router.post(
    "/chat",
    response_model=CopilotChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask AI Copilot an investigative question",
)
async def chat_with_copilot(
    body: CopilotChatRequest,
    current_user: CurrentUser,
    request: Request,
    db: DBSession,
) -> CopilotChatResponse:
    """
    Generate context-aware AI Copilot answer using Gemini / LLM engine.
    Requires a valid authenticated session.
    """
    engine = CopilotEngine()
    res = await engine.generate_response(
        query=body.query,
        session=db,
        case_id=body.case_id,
        recording_id=body.recording_id,
        chat_history=body.chat_history,
    )
    return CopilotChatResponse(**res)
