"""
TraceVault AI Engine — Emotion Analyzer
Per-segment emotion classification (anger, fear, stress, urgency, neutral, calm).
Uses lexical heuristics — works without any external API.
"""
from __future__ import annotations

from collections import Counter
from typing import Any
import structlog

logger = structlog.get_logger(__name__)

# Lexical emotion indicators (English + common Hinglish)
EMOTION_LEXICON: dict[str, list[str]] = {
    "angry": [
        "how dare", "idiot", "stupid", "fool", "rubbish", "nonsense",
        "shut up", "enough", "moron", "sala", "gandu", "bkl",
        "furious", "mad", "rage", "disgusting",
    ],
    "fear": [
        "please", "i beg", "scared", "afraid", "worried", "nervous",
        "don't hurt", "spare me", "don't kill", "help me", "save me",
        "daro", "mafi", "terror",
    ],
    "stress": [
        "stressed", "pressure", "can't handle", "too much", "overwhelmed",
        "difficult", "problem", "issue", "tension", "pareshani", "trouble",
    ],
    "urgency": [
        "urgent", "immediately", "right now", "asap", "hurry", "quickly",
        "fast", "jaldi", "abhi", "no time", "last chance",
    ],
    "happy": [
        "great", "excellent", "wonderful", "happy", "glad", "pleased",
        "fantastic", "amazing", "love it", "perfect", "well done", "good news",
    ],
    "calm": [
        "okay", "fine", "alright", "sure", "understood", "no problem",
        "i see", "i understand", "of course", "definitely", "certainly",
    ],
}


class EmotionAnalyzer:
    """Per-segment emotion classifier using lexical heuristics."""

    def _lexical_emotion(self, text: str) -> tuple[str, float]:
        text_lower = text.lower()
        scores: dict[str, int] = {}

        for emotion, keywords in EMOTION_LEXICON.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[emotion] = score

        if not scores:
            return "neutral", 0.5

        top = max(scores, key=lambda e: scores[e])
        total = sum(scores.values())
        confidence = min(0.85, 0.5 + (scores[top] / max(total, 1)) * 0.4)
        return top, round(confidence, 3)

    def analyze_segments(self, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Classify emotion for each segment. Returns list of {seg_index, emotion, confidence}."""
        results: list[dict[str, Any]] = []
        for idx, seg in enumerate(segments):
            text = seg.get("text", "")
            if not text.strip():
                results.append({"seg_index": idx, "emotion": "neutral", "confidence": 0.5})
            else:
                emotion, confidence = self._lexical_emotion(text)
                results.append({"seg_index": idx, "emotion": emotion, "confidence": confidence})
        return results

    def get_overall_emotion_timeline(
        self, segment_emotions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if not segment_emotions:
            return {"dominant": "neutral", "distribution": {}, "stress_detected": False}

        counts = Counter(e["emotion"] for e in segment_emotions)
        dominant = counts.most_common(1)[0][0]
        total = len(segment_emotions)
        distribution = {k: round(v / total, 3) for k, v in counts.items()}

        stress_detected = (
            distribution.get("stress", 0) > 0.2 or
            distribution.get("fear", 0) > 0.15 or
            distribution.get("urgency", 0) > 0.15
        )

        return {
            "dominant": dominant,
            "distribution": distribution,
            "stress_detected": stress_detected,
        }
