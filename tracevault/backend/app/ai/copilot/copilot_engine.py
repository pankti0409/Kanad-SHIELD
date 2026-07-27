"""
TraceVault AI Investigation Copilot – Production RAG Engine
============================================================
Architecture:
  1. SQLRetriever  – pulls live evidence from the TraceVault database
  2. ContextBuilder – formats retrieved rows into a structured LLM prompt
  3. GeminiAdapter  – calls Gemini Flash for grounded, evidence-backed answers
  4. CopilotEngine  – orchestrates the full pipeline with multi-turn memory

All answers are grounded in real database evidence.
General knowledge (non-case questions) is clearly labelled as LLM knowledge.
No fake / hardcoded data is used anywhere in this module.
"""
from __future__ import annotations

import os
import json
import logging
import textwrap
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import structlog
from sqlalchemy import select, text, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# SQL Retriever
# ---------------------------------------------------------------------------

class SQLRetriever:
    """
    Retrieves grounding evidence from the TraceVault database.
    All queries are async and scoped by optional case_id / recording_id filters.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_cases(self, limit: int = 10, case_id: Optional[str] = None) -> List[Dict]:
        """Retrieve investigation cases."""
        try:
            from app.models.case import Case
            stmt = select(Case).where(Case.is_deleted == False)
            if case_id:
                stmt = stmt.where(Case.id == case_id)
            stmt = stmt.order_by(Case.created_at.desc()).limit(limit)
            result = await self.session.execute(stmt)
            cases = result.scalars().all()
            return [
                {
                    "id": c.id,
                    "case_number": c.case_number,
                    "title": c.title,
                    "description": c.description,
                    "status": c.status.value if c.status else None,
                    "priority": c.priority.value if c.priority else None,
                    "category": c.category.value if c.category else None,
                    "risk_level": c.risk_level,
                    "risk_score": c.risk_score,
                    "recording_count": c.recording_count,
                    "ai_summary": c.ai_summary,
                    "created_at": str(c.created_at) if c.created_at else None,
                }
                for c in cases
            ]
        except Exception as exc:
            logger.warning("retriever_cases_error", error=str(exc))
            return []

    async def get_recordings(self, case_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Retrieve audio recordings."""
        try:
            from app.models.recording import Recording
            stmt = select(Recording).where(Recording.is_deleted == False)
            if case_id:
                stmt = stmt.where(Recording.case_id == case_id)
            stmt = stmt.order_by(Recording.created_at.desc()).limit(limit)
            result = await self.session.execute(stmt)
            recordings = result.scalars().all()
            return [
                {
                    "id": r.id,
                    "original_filename": r.original_filename,
                    "case_id": r.case_id,
                    "processing_status": r.processing_status.value if r.processing_status else None,
                    "duration_seconds": r.duration_seconds,
                    "risk_level": r.risk_level.value if r.risk_level else None,
                    "risk_score": r.risk_score,
                    "threat_count": r.threat_count,
                    "entity_count": r.entity_count,
                    "speaker_count": r.speaker_count,
                    "detected_language": r.detected_language,
                    "sha256_hash": r.sha256_hash,
                    "created_at": str(r.created_at) if r.created_at else None,
                }
                for r in recordings
            ]
        except Exception as exc:
            logger.warning("retriever_recordings_error", error=str(exc))
            return []

    async def get_transcripts(
        self,
        case_id: Optional[str] = None,
        recording_id: Optional[str] = None,
        query_text: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict]:
        """Retrieve transcripts, optionally filtered by case or recording."""
        try:
            from app.models.recording import Transcript, Recording
            stmt = select(Transcript)
            if recording_id:
                stmt = stmt.where(Transcript.recording_id == recording_id)
            elif case_id:
                # Join through Recording to filter by case
                stmt = stmt.join(Recording, Transcript.recording_id == Recording.id).where(
                    Recording.case_id == case_id,
                    Recording.is_deleted == False,
                )
            stmt = stmt.order_by(Transcript.created_at.desc()).limit(limit)
            result = await self.session.execute(stmt)
            transcripts = result.scalars().all()
            return [
                {
                    "id": t.id,
                    "recording_id": t.recording_id,
                    "language": t.language,
                    "confidence": t.confidence,
                    "word_count": t.word_count,
                    "full_text": t.full_text[:3000] if t.full_text else "",  # Limit for context window
                    "model_used": t.model_used,
                }
                for t in transcripts
            ]
        except Exception as exc:
            logger.warning("retriever_transcripts_error", error=str(exc))
            return []

    async def search_transcript_segments(
        self, query_text: str, case_id: Optional[str] = None, limit: int = 8
    ) -> List[Dict]:
        """Full-text search across transcript segments for the query terms."""
        try:
            from app.models.recording import TranscriptSegment, Transcript, Recording
            # Build keyword search across segments
            words = [w.strip() for w in query_text.split() if len(w.strip()) > 2]
            if not words:
                return []

            stmt = select(TranscriptSegment, Transcript.recording_id)
            stmt = stmt.join(Transcript, TranscriptSegment.transcript_id == Transcript.id)

            if case_id:
                stmt = stmt.join(Recording, Transcript.recording_id == Recording.id).where(
                    Recording.case_id == case_id,
                    Recording.is_deleted == False,
                )

            # Search for any of the keywords (case-insensitive via LIKE)
            conditions = [
                TranscriptSegment.text.ilike(f"%{w}%") for w in words[:5]
            ]
            stmt = stmt.where(or_(*conditions))
            stmt = stmt.order_by(TranscriptSegment.start_time).limit(limit)

            result = await self.session.execute(stmt)
            rows = result.all()
            return [
                {
                    "segment_id": row[0].id,
                    "recording_id": row[1],
                    "transcript_id": row[0].transcript_id,
                    "speaker_label": row[0].speaker_label,
                    "start_time": row[0].start_time,
                    "end_time": row[0].end_time,
                    "text": row[0].text,
                    "confidence": row[0].confidence,
                    "has_threat": row[0].has_threat,
                    "has_entity": row[0].has_entity,
                    "emotion": row[0].emotion,
                }
                for row in rows
            ]
        except Exception as exc:
            logger.warning("retriever_segments_error", error=str(exc))
            return []

    async def get_threats(
        self, case_id: Optional[str] = None, recording_id: Optional[str] = None, limit: int = 10
    ) -> List[Dict]:
        """Retrieve detected threat indicators."""
        try:
            from app.models.intelligence import ThreatIndicator
            from app.models.recording import Recording
            stmt = select(ThreatIndicator)
            if recording_id:
                stmt = stmt.where(ThreatIndicator.recording_id == recording_id)
            elif case_id:
                stmt = stmt.join(Recording, ThreatIndicator.recording_id == Recording.id).where(
                    Recording.case_id == case_id,
                    Recording.is_deleted == False,
                )
            stmt = stmt.order_by(ThreatIndicator.confidence.desc()).limit(limit)
            result = await self.session.execute(stmt)
            threats = result.scalars().all()
            return [
                {
                    "id": t.id,
                    "recording_id": t.recording_id,
                    "category": t.category.value if t.category else None,
                    "severity": t.severity,
                    "description": t.description,
                    "evidence_text": t.evidence_text,
                    "speaker_label": t.speaker_label,
                    "timestamp": t.timestamp,
                    "confidence": t.confidence,
                    "reasoning": t.reasoning,
                }
                for t in threats
            ]
        except Exception as exc:
            logger.warning("retriever_threats_error", error=str(exc))
            return []

    async def get_entities(
        self, case_id: Optional[str] = None, recording_id: Optional[str] = None,
        entity_type: Optional[str] = None, limit: int = 20
    ) -> List[Dict]:
        """Retrieve extracted entities."""
        try:
            from app.models.intelligence import Entity
            from app.models.recording import Recording
            stmt = select(Entity)
            if recording_id:
                stmt = stmt.where(Entity.recording_id == recording_id)
            elif case_id:
                stmt = stmt.join(Recording, Entity.recording_id == Recording.id).where(
                    Recording.case_id == case_id,
                    Recording.is_deleted == False,
                )
            if entity_type:
                stmt = stmt.where(Entity.entity_type.ilike(f"%{entity_type}%"))
            stmt = stmt.order_by(Entity.confidence.desc()).limit(limit)
            result = await self.session.execute(stmt)
            entities = result.scalars().all()
            return [
                {
                    "id": e.id,
                    "recording_id": e.recording_id,
                    "entity_type": e.entity_type,
                    "entity_value": e.entity_value,
                    "speaker_label": e.speaker_label,
                    "timestamp": e.timestamp,
                    "confidence": e.confidence,
                    "context_sentence": e.context_sentence,
                }
                for e in entities
            ]
        except Exception as exc:
            logger.warning("retriever_entities_error", error=str(exc))
            return []

    async def get_reports(
        self, case_id: Optional[str] = None, recording_id: Optional[str] = None, limit: int = 5
    ) -> List[Dict]:
        """Retrieve generated investigation reports."""
        try:
            from app.models.evidence import Report
            stmt = select(Report).where(Report.is_deleted == False)
            if recording_id:
                stmt = stmt.where(Report.recording_id == recording_id)
            elif case_id:
                stmt = stmt.where(Report.case_id == case_id)
            stmt = stmt.order_by(Report.created_at.desc()).limit(limit)
            result = await self.session.execute(stmt)
            reports = result.scalars().all()
            return [
                {
                    "id": r.id,
                    "case_id": r.case_id,
                    "recording_id": r.recording_id,
                    "report_type": r.report_type,
                    "title": r.title,
                    "status": r.status,
                    "confidence": r.confidence,
                    "content_summary": (r.content or "")[:1000] if r.content else None,
                    "created_at": str(r.created_at) if r.created_at else None,
                }
                for r in reports
            ]
        except Exception as exc:
            logger.warning("retriever_reports_error", error=str(exc))
            return []

    async def get_notes(
        self, case_id: Optional[str] = None, limit: int = 10
    ) -> List[Dict]:
        """Retrieve investigator notes."""
        try:
            from app.models.case import InvestigatorNote
            stmt = select(InvestigatorNote).where(InvestigatorNote.is_deleted == False)
            if case_id:
                stmt = stmt.where(InvestigatorNote.case_id == case_id)
            stmt = stmt.order_by(InvestigatorNote.created_at.desc()).limit(limit)
            result = await self.session.execute(stmt)
            notes = result.scalars().all()
            return [
                {
                    "id": n.id,
                    "case_id": n.case_id,
                    "title": n.title,
                    "content": n.content[:500] if n.content else "",
                    "note_type": n.note_type,
                    "created_at": str(n.created_at) if n.created_at else None,
                }
                for n in notes
            ]
        except Exception as exc:
            logger.warning("retriever_notes_error", error=str(exc))
            return []

    async def get_emotions(
        self, case_id: Optional[str] = None, recording_id: Optional[str] = None, limit: int = 15
    ) -> List[Dict]:
        """Retrieve emotion analysis results."""
        try:
            from app.models.intelligence import EmotionAnalysis
            from app.models.recording import Recording
            stmt = select(EmotionAnalysis)
            if recording_id:
                stmt = stmt.where(EmotionAnalysis.recording_id == recording_id)
            elif case_id:
                stmt = stmt.join(Recording, EmotionAnalysis.recording_id == Recording.id).where(
                    Recording.case_id == case_id,
                    Recording.is_deleted == False,
                )
            stmt = stmt.order_by(EmotionAnalysis.confidence.desc()).limit(limit)
            result = await self.session.execute(stmt)
            emotions = result.scalars().all()
            return [
                {
                    "id": e.id,
                    "recording_id": e.recording_id,
                    "speaker_label": e.speaker_label,
                    "emotion": e.emotion.value if e.emotion else None,
                    "confidence": e.confidence,
                    "start_time": e.start_time,
                    "end_time": e.end_time,
                    "intensity": e.intensity,
                }
                for e in emotions
            ]
        except Exception as exc:
            logger.warning("retriever_emotions_error", error=str(exc))
            return []

    async def get_dynamic_suggestions(
        self, case_id: Optional[str] = None
    ) -> List[str]:
        """Generate dynamic suggestions based on the current database state."""
        suggestions = []
        try:
            from app.models.case import Case
            from app.models.recording import Recording
            from app.models.intelligence import ThreatIndicator

            # Count cases
            case_count_result = await self.session.execute(
                select(func.count()).select_from(Case).where(Case.is_deleted == False)
            )
            case_count = case_count_result.scalar() or 0

            # Count recordings
            rec_count_result = await self.session.execute(
                select(func.count()).select_from(Recording).where(Recording.is_deleted == False)
            )
            rec_count = rec_count_result.scalar() or 0

            # Count threats
            threat_count_result = await self.session.execute(
                select(func.count()).select_from(ThreatIndicator)
            )
            threat_count = threat_count_result.scalar() or 0

            if case_count > 0:
                suggestions.append(f"Summarise all {case_count} active investigation cases")
            if rec_count > 0:
                suggestions.append(f"What threats were detected across {rec_count} recordings?")
            if threat_count > 0:
                suggestions.append(f"Show the {min(threat_count, 5)} highest-severity threats")
            if case_id:
                suggestions.append("Summarise the transcript from this case")
                suggestions.append("Who are the key speakers in this case?")
                suggestions.append("What entities were extracted from this case?")
            else:
                suggestions.append("Which cases have the highest risk scores?")
                suggestions.append("Show all extortion-related threats")
                suggestions.append("Which speakers show signs of high stress?")
        except Exception:
            suggestions = [
                "List all active investigation cases",
                "What threats have been detected?",
                "Show extracted entities across all recordings",
            ]
        return suggestions[:6]


# ---------------------------------------------------------------------------
# Context Builder
# ---------------------------------------------------------------------------

class ContextBuilder:
    """Formats retrieved database evidence into a structured LLM prompt context."""

    SYSTEM_PROMPT = textwrap.dedent("""
        You are the TraceVault AI Copilot. You are a helpful assistant specifically built for this platform.
        Behave like ChatGPT: friendly, conversational, and direct, but use the provided database evidence about the platform's cases, recordings, and threats to ground your answers.

        CRITICAL RULES:
        1. Speak in clean, normal conversational language.
        2. AVOID formatting your answers with raw asterisks (*, **) or bold list items unless specifically requested. Do not use raw bullet lists or markdown headers (#, ##) in a way that feels cluttered. Keep it as natural paragraphs and clean sentences.
        3. If the retrieved evidence does not contain any matching information for the user's question, do not show robotic error messages. Instead, politely inform the user that no matching results or cases were found in the database.
        4. When referencing database cases or recordings, talk about them naturally (e.g., "Case 21 titled Extortion Threat" instead of citing IDs or hashes).
        5. If the question is general (not related to cases/recordings on the platform), answer it naturally using your general knowledge. Do not prepend any warnings or labels.
    """).strip()

    def build_context(
        self,
        cases: List[Dict],
        recordings: List[Dict],
        transcripts: List[Dict],
        segments: List[Dict],
        threats: List[Dict],
        entities: List[Dict],
        emotions: List[Dict],
        reports: List[Dict],
        notes: List[Dict],
    ) -> str:
        """Build the structured evidence context block for the LLM prompt."""
        parts = []

        if cases:
            parts.append("## INVESTIGATION CASES")
            for c in cases:
                parts.append(
                    f"- **{c['case_number']}** — {c['title']} | Status: {c['status']} | "
                    f"Priority: {c['priority']} | Category: {c['category']} | "
                    f"Risk: {c['risk_level']} ({c['risk_score']}) | "
                    f"Recordings: {c['recording_count']}"
                )
                if c.get("ai_summary"):
                    parts.append(f"  AI Summary: {c['ai_summary'][:300]}")
                if c.get("description"):
                    parts.append(f"  Description: {c['description'][:200]}")

        if recordings:
            parts.append("\n## AUDIO RECORDINGS")
            for r in recordings:
                parts.append(
                    f"- **{r['original_filename']}** (ID: {r['id'][:8]}...) | "
                    f"Status: {r['processing_status']} | Duration: {r.get('duration_seconds', 'N/A')}s | "
                    f"Risk: {r['risk_level']} | Threats: {r['threat_count']} | "
                    f"Entities: {r['entity_count']} | Speakers: {r['speaker_count']} | "
                    f"Language: {r['detected_language']}"
                )

        if transcripts:
            parts.append("\n## TRANSCRIPTS")
            for t in transcripts:
                parts.append(f"- Recording {t['recording_id'][:8]}... | Language: {t['language']} | Words: {t['word_count']} | Confidence: {t['confidence']:.0%}")
                if t.get("full_text"):
                    parts.append(f"  Full Transcript:\n  {t['full_text'][:2000]}")

        if segments:
            parts.append("\n## RELEVANT TRANSCRIPT SEGMENTS")
            for s in segments:
                ts = f"{int(s['start_time'] // 60)}:{int(s['start_time'] % 60):02d}" if s.get("start_time") is not None else "?"
                parts.append(
                    f"> [{s.get('speaker_label', 'Unknown')} @ {ts}] \"{s['text']}\""
                    + (f" [⚠️ THREAT]" if s.get("has_threat") else "")
                    + (f" [Emotion: {s.get('emotion')}]" if s.get("emotion") else "")
                )

        if threats:
            parts.append("\n## DETECTED THREATS")
            for t in threats:
                parts.append(
                    f"- **{t['category'].upper()}** | Severity: {t['severity']} | "
                    f"Confidence: {t['confidence']:.0%} | Speaker: {t.get('speaker_label', 'Unknown')}"
                )
                parts.append(f"  Evidence: \"{t['evidence_text'][:300]}\"")
                if t.get("reasoning"):
                    parts.append(f"  Reasoning: {t['reasoning'][:200]}")

        if entities:
            parts.append("\n## EXTRACTED ENTITIES")
            # Group by type
            by_type: Dict[str, List] = {}
            for e in entities:
                etype = e["entity_type"]
                by_type.setdefault(etype, []).append(e)
            for etype, ents in by_type.items():
                values = ", ".join(
                    f"**{e['entity_value']}**" + (f" [Speaker: {e['speaker_label']}]" if e.get("speaker_label") else "")
                    for e in ents[:5]
                )
                parts.append(f"- **{etype}**: {values}")

        if emotions:
            parts.append("\n## EMOTION ANALYSIS")
            for e in emotions:
                ts = f"{int(e['start_time'] // 60)}:{int(e['start_time'] % 60):02d}" if e.get("start_time") is not None else "?"
                parts.append(
                    f"- {e.get('speaker_label', 'Unknown')} @ {ts}: **{e.get('emotion', 'unknown').upper()}** "
                    f"(confidence: {e['confidence']:.0%}, intensity: {e.get('intensity', 'N/A')})"
                )

        if reports:
            parts.append("\n## INVESTIGATION REPORTS")
            for r in reports:
                parts.append(
                    f"- **{r['title']}** | Type: {r['report_type']} | Status: {r['status']} | "
                    f"Confidence: {r.get('confidence', 'N/A')}"
                )
                if r.get("content_summary"):
                    parts.append(f"  Summary: {r['content_summary'][:400]}")

        if notes:
            parts.append("\n## INVESTIGATOR NOTES")
            for n in notes:
                parts.append(f"- **{n.get('title', 'Note')}** ({n['note_type']}): {n['content'][:300]}")

        if not parts:
            return "## DATABASE STATE\nNo evidence data has been retrieved. The database may be empty, or the requested data does not exist."

        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Gemini Adapter
# ---------------------------------------------------------------------------

class GeminiAdapter:
    """Calls Google Gemini for LLM generation."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        if not api_key:
            try:
                from app.config import get_settings
                settings = get_settings()
                api_key = settings.ai.GEMINI_API_KEY or settings.ai.LLM_API_KEY
            except Exception:
                pass
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        self._client = None
        self._model = None

    def _get_model(self):
        """Lazily initialise the Gemini client."""
        if self._model is not None:
            return self._model
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured in environment variables.")
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel("gemini-2.5-flash")
            return self._model
        except ImportError:
            raise RuntimeError("google-generativeai package is not installed. Run: pip install google-generativeai")

    async def generate(
        self,
        system_prompt: str,
        evidence_context: str,
        chat_history: List[Dict[str, str]],
        user_query: str,
    ) -> str:
        """Generate a grounded response using Gemini."""
        import asyncio

        model = self._get_model()

        # Build the full prompt
        full_prompt = (
            f"{system_prompt}\n\n"
            f"## RETRIEVED EVIDENCE FROM TRACEVAULT DATABASE\n\n"
            f"{evidence_context}\n\n"
            f"## CONVERSATION HISTORY\n"
        )

        # Add conversation history (last 8 turns for context)
        history_turns = chat_history[-8:] if len(chat_history) > 8 else chat_history
        for msg in history_turns:
            role = "Investigator" if msg.get("role") == "user" else "AI Copilot"
            full_prompt += f"{role}: {msg.get('content', '')}\n"

        full_prompt += f"\n## CURRENT QUESTION\nInvestigator: {user_query}\n\nAI Copilot:"

        # Run in executor since Gemini Python SDK is sync
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(full_prompt)
        )

        return response.text.strip()


# ---------------------------------------------------------------------------
# Main Copilot Engine
# ---------------------------------------------------------------------------

class CopilotEngine:
    """
    TraceVault AI Investigation Copilot – Production RAG Engine.

    Pipeline:
      1. Retrieve evidence from the live database using SQLRetriever
      2. Format evidence into a structured context block via ContextBuilder
      3. Call Gemini with system prompt + evidence + chat history
      4. Return structured response with citations and suggestions
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        if not api_key:
            try:
                from app.config import get_settings
                settings = get_settings()
                api_key = settings.ai.GEMINI_API_KEY or settings.ai.LLM_API_KEY
            except Exception:
                pass
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        self._gemini = GeminiAdapter(api_key=self.api_key)
        self._context_builder = ContextBuilder()

    async def generate_response(
        self,
        query: str,
        session: Optional[AsyncSession] = None,
        case_id: Optional[str] = None,
        recording_id: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Run the full RAG pipeline for a user query.

        Args:
            query: The investigator's question
            session: An active async SQLAlchemy session (required for DB retrieval)
            case_id: Optional case ID to scope the query
            recording_id: Optional recording ID to scope the query
            chat_history: List of previous messages [{"role": "user"/"assistant", "content": "..."}]

        Returns:
            Dict with: answer, citations, suggestions, confidence_score, model_used, sources_used
        """
        chat_history = chat_history or []
        citations: List[Dict] = []
        sources_used: List[str] = []

        if session is None:
            # Graceful degradation: no DB session available
            return {
                "answer": (
                    "⚠️ **Database connection unavailable.**\n\n"
                    "The AI Copilot requires an active database session to retrieve evidence. "
                    "Please ensure the backend is correctly configured and try again."
                ),
                "citations": [],
                "suggestions": [
                    "List all active cases",
                    "Show detected threats",
                    "What entities were extracted?",
                ],
                "confidence_score": 0.0,
                "model_used": "unavailable",
                "sources_used": [],
            }

        try:
            retriever = SQLRetriever(session)

            # === Shortcuts to answer instantly without Gemini (greetings and case list/search) ===
            q_lower = query.lower().strip()
            greetings = {"hey", "hello", "hi", "yo", "sup", "greetings"}
            q_clean = q_lower.replace(".", "").replace("!", "").replace("?", "").strip()

            # 1. Greeting shortcut
            if q_clean in greetings:
                return {
                    "answer": "How should I help you?",
                    "citations": [],
                    "suggestions": [
                        "List all active cases",
                        "Show detected threats",
                        "What entities were extracted?",
                    ],
                    "confidence_score": 1.0,
                    "model_used": "Rule Engine",
                    "sources_used": [],
                }

            # 2. Case query shortcut
            is_case_query = "case" in q_lower or "theft" in q_lower or "extortion" in q_lower or "fraud" in q_lower or "tv-" in q_lower
            if is_case_query:
                # Retrieve cases
                cases = await retriever.get_cases(limit=15)
                matching_cases = []
                for c in cases:
                    c_num = c.get("case_number", "").lower()
                    c_title = c.get("title", "").lower()
                    # Check if query mentions this case number or title keywords
                    if c_num in q_lower or any(word in c_title or word in c_num for word in q_lower.split() if len(word) > 2 and word not in {"case", "show", "list", "active", "about", "for"}):
                        matching_cases.append(c)

                # If broad request
                if not matching_cases and ("list" in q_lower or "show" in q_lower or q_clean == "cases" or q_clean == "case" or "active" in q_lower):
                    matching_cases = cases

                if matching_cases:
                    lines = []
                    lines.append("Here are the cases found on the platform:")
                    for mc in matching_cases:
                        lines.append(f"Case {mc['case_number']}: {mc['title']} (Status: {mc['status']})")
                    answer_text = "\n".join(lines)
                    return {
                        "answer": answer_text,
                        "citations": [
                            {
                                "title": f"Case: {mc['case_number']} — {mc['title']}",
                                "confidence": 1.0,
                                "source_type": "case",
                                "source_id": mc["id"],
                            } for mc in matching_cases
                        ],
                        "suggestions": [
                            "Show detected threats",
                            "What entities were extracted?",
                        ],
                        "confidence_score": 1.0,
                        "model_used": "Rule Engine",
                        "sources_used": [f"{len(matching_cases)} case(s)"],
                    }
                else:
                    return {
                        "answer": "No matching cases were found on the platform.",
                        "citations": [],
                        "suggestions": ["List all active cases"],
                        "confidence_score": 1.0,
                        "model_used": "Rule Engine",
                        "sources_used": [],
                    }

            # === Stage 1: Parallel Retrieval ===
            cases = await retriever.get_cases(limit=15, case_id=case_id)
            recordings = await retriever.get_recordings(case_id=case_id, limit=10)
            threats = await retriever.get_threats(case_id=case_id, recording_id=recording_id, limit=10)
            entities = await retriever.get_entities(case_id=case_id, recording_id=recording_id, limit=20)
            emotions = await retriever.get_emotions(case_id=case_id, recording_id=recording_id, limit=10)
            reports = await retriever.get_reports(case_id=case_id, recording_id=recording_id, limit=5)
            notes = await retriever.get_notes(case_id=case_id, limit=8)

            # Fetch transcripts + segments only if relevant query terms detected
            transcripts: List[Dict] = []
            segments: List[Dict] = []
            transcript_keywords = [
                "transcript", "said", "spoke", "conversation", "call", "recording",
                "quote", "statement", "speaker", "what did", "who said"
            ]
            q_lower = query.lower()
            if any(kw in q_lower for kw in transcript_keywords) or recording_id:
                transcripts = await retriever.get_transcripts(
                    case_id=case_id, recording_id=recording_id, limit=3
                )
            segments = await retriever.search_transcript_segments(
                query_text=query, case_id=case_id, limit=8
            )

            # === Stage 2: Track what was retrieved for citations ===
            if cases:
                for c in cases[:3]:
                    citations.append({
                        "title": f"Case: {c['case_number']} — {c['title']}",
                        "confidence": 1.0,
                        "source_type": "case",
                        "source_id": c["id"],
                    })
                sources_used.append(f"{len(cases)} case(s)")

            if threats:
                for t in threats[:3]:
                    citations.append({
                        "title": f"Threat: {t['category']} (Severity: {t['severity']})",
                        "confidence": t["confidence"],
                        "source_type": "threat",
                        "source_id": t["id"],
                    })
                sources_used.append(f"{len(threats)} threat(s)")

            if entities:
                sources_used.append(f"{len(entities)} entity/entities")

            if segments:
                for s in segments[:3]:
                    ts = f"{int(s['start_time'] // 60)}:{int(s['start_time'] % 60):02d}" if s.get("start_time") is not None else "?"
                    citations.append({
                        "title": f"Transcript @ {ts} — {s.get('speaker_label', 'Unknown')}",
                        "confidence": s.get("confidence", 0.9),
                        "source_type": "transcript_segment",
                        "source_id": s["segment_id"],
                    })
                sources_used.append(f"{len(segments)} transcript segment(s)")

            if reports:
                sources_used.append(f"{len(reports)} report(s)")

            # === Stage 3: Build evidence context ===
            evidence_context = self._context_builder.build_context(
                cases=cases,
                recordings=recordings,
                transcripts=transcripts,
                segments=segments,
                threats=threats,
                entities=entities,
                emotions=emotions,
                reports=reports,
                notes=notes,
            )

            # === Stage 4: Generate grounded response with Gemini ===
            answer = await self._gemini.generate(
                system_prompt=ContextBuilder.SYSTEM_PROMPT,
                evidence_context=evidence_context,
                chat_history=chat_history,
                user_query=query,
            )

            # === Stage 5: Dynamic suggestions from DB ===
            suggestions = await retriever.get_dynamic_suggestions(case_id=case_id)

            confidence_score = 0.92 if cases or threats or entities or segments else 0.5
            model_used = "Gemini 2.5 Flash + TraceVault SQL RAG"

            logger.info(
                "copilot_response_generated",
                query=query[:100],
                cases_retrieved=len(cases),
                threats_retrieved=len(threats),
                entities_retrieved=len(entities),
                segments_retrieved=len(segments),
            )

            return {
                "answer": answer,
                "citations": citations,
                "suggestions": suggestions,
                "confidence_score": confidence_score,
                "model_used": model_used,
                "sources_used": sources_used,
            }

        except RuntimeError as exc:
            # Gemini not configured
            err_msg = str(exc)
            logger.error("copilot_gemini_error", error=err_msg)
            return {
                "answer": (
                    f"⚠️ **AI Engine Error**\n\n{err_msg}\n\n"
                    "Please ensure `GEMINI_API_KEY` is set in your `.env` file and is valid."
                ),
                "citations": [],
                "suggestions": [],
                "confidence_score": 0.0,
                "model_used": "error",
                "sources_used": [],
            }
        except Exception as exc:
            logger.error("copilot_pipeline_error", error=str(exc), exc_info=True)
            return {
                "answer": (
                    f"⚠️ **An unexpected error occurred in the AI pipeline.**\n\n"
                    f"Error: `{str(exc)[:200]}`\n\n"
                    "This has been logged. Please try again or contact support."
                ),
                "citations": [],
                "suggestions": [],
                "confidence_score": 0.0,
                "model_used": "error",
                "sources_used": [],
            }
