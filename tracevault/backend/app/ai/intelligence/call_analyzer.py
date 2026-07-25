"""
TraceVault AI Engine — Call Intelligence Analyzer
Uses Gemini API for NER and threat classification.
Falls back to regex + keyword patterns if Gemini unavailable.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Optional
import structlog

logger = structlog.get_logger(__name__)

ENTITY_TYPES = [
    "PERSON", "ALIAS", "ORGANIZATION", "PHONE_NUMBER", "ACCOUNT_NUMBER",
    "MONETARY_AMOUNT", "LOCATION", "ADDRESS", "DATE_TIME", "VEHICLE",
    "WEAPON", "DRUG", "EMAIL", "URL", "ID_NUMBER",
]

THREAT_KEYWORDS = {
    "violence": ["kill", "murder", "shoot", "attack", "beat", "harm", "hurt", "stab", "shoot", "eliminate", "finish"],
    "extortion": ["extort", "blackmail", "ransom", "pay up", "money or else", "consequences", "suffer"],
    "fraud": ["fake", "forged", "cheat", "swindle", "deceive", "fraud", "scam"],
    "drug_activity": ["drug", "narcotics", "supari", "ganja", "cocaine", "heroin", "stuff", "packet"],
    "weapon_discussion": ["gun", "pistol", "rifle", "bomb", "explosive", "knife", "blade", "firearm", "weapon"],
    "money_laundering": ["laundering", "black money", "hawala", "untrace", "cash without receipt"],
    "kidnapping": ["kidnap", "abduct", "hostage", "take away", "hold captive"],
    "human_trafficking": ["trafficking", "sell person", "sold", "supply people"],
    "coercion": ["family safe", "family ko dekh", "children safe", "don't involve police", "keep quiet"],
    "suspicious_coordination": ["code word", "signal", "abort", "change plan", "new location"],
}


class CallAnalyzer:
    """
    Intelligence analysis engine.
    Extracts entities, threats, summary, emotion indicators from transcripts.
    Uses Gemini API (primary) with regex/keyword fallback.
    """

    def __init__(self) -> None:
        self._gemini_client = None
        self._gemini_ready = False
        self._init_gemini()

    def _init_gemini(self) -> None:
        """Initialize Gemini API client if API key is available."""
        try:
            from app.config import get_settings
            settings = get_settings()
            api_key = settings.ai.GEMINI_API_KEY
            if not api_key:
                return

            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self._gemini_client = genai.GenerativeModel("gemini-1.5-flash")
            self._gemini_ready = True
            logger.info("gemini_client_ready")
        except Exception as exc:
            logger.warning("gemini_init_failed", error=str(exc))
            self._gemini_ready = False

    # ── Gemini-powered analysis ───────────────────────────────────────────

    def _analyze_with_gemini(
        self,
        full_text: str,
        language: str,
    ) -> Optional[dict[str, Any]]:
        """Send transcript to Gemini for deep NER + threat classification."""
        if not self._gemini_ready or not self._gemini_client:
            return None

        prompt = f"""You are a forensic intelligence analyst for law enforcement. Analyze this call transcript and extract structured information.

TRANSCRIPT (language: {language}):
---
{full_text[:8000]}
---

Respond ONLY with a valid JSON object in this exact structure:
{{
  "summary": "<2-4 sentence factual summary of the conversation>",
  "primary_topic": "<one phrase describing main topic>",
  "threat_present": <true|false>,
  "threat_category": "<one of: violence|extortion|fraud|drug_activity|weapon_discussion|money_laundering|kidnapping|human_trafficking|coercion|suspicious_coordination|other|none>",
  "threat_severity": "<critical|high|medium|low|none>",
  "threat_description": "<specific description of threat if present, else 'No threat detected'>",
  "threat_evidence": "<direct quote from transcript supporting threat assessment>",
  "threat_confidence": <0.0-1.0>,
  "risk_score": <0.0-100.0>,
  "risk_level": "<critical|high|medium|low|very_low>",
  "entities": [
    {{
      "type": "<PERSON|ALIAS|ORGANIZATION|PHONE_NUMBER|ACCOUNT_NUMBER|MONETARY_AMOUNT|LOCATION|ADDRESS|DATE_TIME|VEHICLE|WEAPON|DRUG|EMAIL|URL|ID_NUMBER>",
      "value": "<extracted entity text>",
      "normalized": "<standardized form if applicable>",
      "context": "<surrounding sentence>",
      "confidence": <0.0-1.0>
    }}
  ],
  "keywords": ["<significant keyword 1>", "<significant keyword 2>"],
  "locations_discussed": ["<location1>", "<location2>"],
  "times_discussed": ["<time/date 1>", "<time/date 2>"],
  "emotion_indicators": {{
    "overall": "<angry|fearful|stressed|calm|urgent|neutral>",
    "urgency_level": "<high|medium|low>"
  }},
  "model_confidence": <0.0-1.0>
}}

CRITICAL RULES:
- Do NOT hallucinate entities. Only extract what is explicitly in the transcript.
- If uncertain about threat, set threat_present=false.
- All fields are required. Use empty arrays [] for missing list fields.
"""

        try:
            response = self._gemini_client.generate_content(
                prompt,
                generation_config={"temperature": 0.1, "max_output_tokens": 2048},
            )
            text = response.text.strip()
            # Strip markdown code blocks if present
            if text.startswith("```"):
                text = re.sub(r"```(?:json)?\s*", "", text).rstrip("```").strip()
            data = json.loads(text)
            data["model_used"] = "gemini-1.5-flash"
            return data
        except json.JSONDecodeError as exc:
            logger.warning("gemini_json_parse_failed", error=str(exc))
            return None
        except Exception as exc:
            logger.warning("gemini_analysis_failed", error=str(exc))
            return None

    # ── Regex/Keyword fallback ────────────────────────────────────────────

    def _analyze_with_regex(
        self,
        full_text: str,
        segments: list[dict],
    ) -> dict[str, Any]:
        """Rule-based NER + threat detection as fallback."""
        text_lower = full_text.lower()

        # Entity extraction — phones, amounts, basic patterns
        entities: list[dict] = []

        # Phone numbers (Indian format primarily)
        for match in re.finditer(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b", full_text):
            entities.append({"type": "PHONE_NUMBER", "value": match.group(), "confidence": 0.85, "context": "", "normalized": match.group().replace(" ", "").replace("-", "")})

        # Monetary amounts
        for match in re.finditer(r"(?:rs\.?|inr|₹)\s*[\d,]+(?:\.\d{2})?|[\d,]+\s*(?:lakh|crore|thousand|k)\b", full_text, re.IGNORECASE):
            entities.append({"type": "MONETARY_AMOUNT", "value": match.group(), "confidence": 0.80, "context": "", "normalized": match.group()})

        # Threat detection
        detected_threats: list[tuple[str, list[str]]] = []
        for category, keywords in THREAT_KEYWORDS.items():
            found = [kw for kw in keywords if kw in text_lower]
            if found:
                detected_threats.append((category, found))

        threat_present = len(detected_threats) > 0
        threat_category = detected_threats[0][0] if detected_threats else "none"
        threat_severity = "high" if len(detected_threats) >= 2 else ("medium" if detected_threats else "none")
        risk_score = min(100.0, len(detected_threats) * 25.0 + len(entities) * 5.0)

        # Location hints
        locations = re.findall(r"\b(?:mumbai|delhi|surat|ahmedabad|bangalore|pune|hyderabad|chennai|kolkata|jaipur|lucknow|chandigarh|zurich|london|dubai)\b", text_lower)

        # Time/date hints
        times = re.findall(r"\b(?:\d{1,2}(?::\d{2})?\s*(?:am|pm|बजे)|(?:tomorrow|today|yesterday|kal|aaj|sunday|monday|tuesday|wednesday|thursday|friday|saturday))\b", text_lower)

        word_count = len(full_text.split())
        summary = f"Call transcript processed ({word_count} words). " + (
            f"Threat indicators detected: {', '.join(t[0] for t in detected_threats)}." if detected_threats else "No explicit threat indicators detected."
        )

        return {
            "summary": summary,
            "primary_topic": threat_category if threat_category != "none" else "General Conversation",
            "threat_present": threat_present,
            "threat_category": threat_category,
            "threat_severity": threat_severity,
            "threat_description": f"Keywords detected: {', '.join(detected_threats[0][1])}" if detected_threats else "No threat detected.",
            "threat_evidence": "",
            "threat_confidence": 0.65 if threat_present else 0.0,
            "risk_score": risk_score,
            "risk_level": "high" if risk_score >= 60 else ("medium" if risk_score >= 30 else "low"),
            "entities": entities,
            "keywords": [kw for _, kws in detected_threats for kw in kws[:3]],
            "locations_discussed": list(set(locations)),
            "times_discussed": list(set(times)),
            "emotion_indicators": {"overall": "neutral", "urgency_level": "low"},
            "model_confidence": 0.60,
            "model_used": "regex-keyword-fallback",
        }

    # ── Main Analysis ─────────────────────────────────────────────────────

    def analyze(
        self,
        full_text: str,
        segments: Optional[list[dict]] = None,
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Analyze transcript for entities, threats, summary, and risk score.
        Returns structured dict for DB persistence.
        """
        segments = segments or []
        now = datetime.now(timezone.utc).isoformat()

        # Try Gemini first
        result: Optional[dict] = None
        if full_text.strip() and self._gemini_ready:
            result = self._analyze_with_gemini(full_text, language)

        # Fall back to regex/keyword
        if result is None:
            result = self._analyze_with_regex(full_text, segments)

        # Build threat records for DB
        threats: list[dict] = []
        if result.get("threat_present"):
            threats.append({
                "category": result.get("threat_category", "other"),
                "severity": result.get("threat_severity", "medium"),
                "description": result.get("threat_description", ""),
                "evidence_text": result.get("threat_evidence", ""),
                "confidence": result.get("threat_confidence", 0.7),
                "reasoning": result.get("summary", ""),
                "model_used": result.get("model_used", "fallback"),
            })

        # Mark threat segments
        if segments and threats:
            threat_evidence_lower = (result.get("threat_evidence", "") + " " + " ".join(result.get("keywords", []))).lower()
            for seg in segments:
                if any(kw in seg.get("text", "").lower() for kw in result.get("keywords", [])):
                    seg["has_threat"] = True

        return {
            "summary": result.get("summary", ""),
            "primary_topic": result.get("primary_topic", "General Conversation"),
            "threat_present": result.get("threat_present", False),
            "threat_category": result.get("threat_category", "none"),
            "threat_severity": result.get("threat_severity", "none"),
            "threats": threats,
            "entities": result.get("entities", []),
            "keywords": result.get("keywords", []),
            "locations_discussed": result.get("locations_discussed", []),
            "times_discussed": result.get("times_discussed", []),
            "emotion_indicators": result.get("emotion_indicators", {}),
            "risk_score": result.get("risk_score", 0.0),
            "risk_level": result.get("risk_level", "low"),
            "confidence": result.get("model_confidence", 0.7),
            "model_used": result.get("model_used", "unknown"),
            "transcript_datetime": now,
            "analysis_datetime": now,
        }
