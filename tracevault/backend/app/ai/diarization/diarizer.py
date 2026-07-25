"""
TraceVault AI Engine — Speaker Diarization
Assigns speech segments to individual speakers using pyannote.audio when available,
with an energy-based VAD fallback for development (no HF token required).
"""
from __future__ import annotations

import asyncio
import re
import uuid
from pathlib import Path
from typing import Any, Optional
import structlog

logger = structlog.get_logger(__name__)

# ── Detect available backends ──────────────────────────────────────────────

HAS_PYANNOTE = False
try:
    from pyannote.audio import Pipeline as PyannotePipeline
    HAS_PYANNOTE = True
except ImportError:
    pass

HAS_LIBROSA = False
try:
    import librosa
    import numpy as np
    HAS_LIBROSA = True
except ImportError:
    pass


class SpeakerDiarizer:
    """
    Speaker diarization engine.
    Backend priority: pyannote.audio (if HF_TOKEN is set) > energy-based VAD fallback
    """

    def __init__(self, min_speakers: int = 1, max_speakers: int = 6) -> None:
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self._pyannote_pipeline = None

    def _try_load_pyannote(self, hf_token: Optional[str]) -> bool:
        """Attempt to load pyannote.audio pipeline."""
        if not HAS_PYANNOTE or not hf_token:
            return False
        try:
            self._pyannote_pipeline = PyannotePipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token,
            )
            logger.info("pyannote_pipeline_loaded")
            return True
        except Exception as exc:
            logger.warning("pyannote_load_failed", error=str(exc))
            return False

    def _run_pyannote(self, audio_path: str) -> Optional[list[dict]]:
        """Run pyannote speaker diarization. Returns list of {start, end, speaker} dicts."""
        if self._pyannote_pipeline is None:
            return None
        try:
            diarization = self._pyannote_pipeline(audio_path)
            turns = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                turns.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker,
                })
            return turns
        except Exception as exc:
            logger.warning("pyannote_diarize_failed", error=str(exc))
            return None

    def _energy_based_speaker_assignment(
        self,
        audio_path: str,
        segments: list[dict],
    ) -> list[str]:
        """
        Energy-based heuristic speaker assignment.
        Uses RMS energy per segment — high energy vs low energy as proxy for 2 speakers.
        Falls back to alternating 2-speaker assignment if librosa unavailable.
        """
        if not HAS_LIBROSA or len(segments) == 0:
            # Simple alternating 2-speaker fallback
            return [f"Speaker_0{(i % 2)}" for i in range(len(segments))]

        try:
            y, sr = librosa.load(audio_path, sr=16000, mono=True)
            labels = []
            energies = []

            for seg in segments:
                start_s = seg.get("start", 0.0)
                end_s = seg.get("end", start_s + 1.0)
                start_idx = int(start_s * sr)
                end_idx = min(int(end_s * sr), len(y))

                if start_idx >= end_idx or start_idx >= len(y):
                    energies.append(0.0)
                else:
                    chunk = y[start_idx:end_idx]
                    rms = float(np.sqrt(np.mean(chunk ** 2)))
                    energies.append(rms)

            if len(energies) == 0:
                return [f"Speaker_0{(i % 2)}" for i in range(len(segments))]

            # Median split: above median = Speaker_01, below = Speaker_00
            median_e = float(np.median(energies))
            for e in energies:
                labels.append("Speaker_01" if e >= median_e else "Speaker_00")
            return labels

        except Exception as exc:
            logger.warning("energy_diarize_failed", error=str(exc))
            return [f"Speaker_0{(i % 2)}" for i in range(len(segments))]

    def _assign_speakers_from_pyannote(
        self,
        segments: list[dict],
        turns: list[dict],
    ) -> list[str]:
        """Assign speaker labels to segments based on pyannote turn timestamps."""
        labels = []
        for seg in segments:
            seg_mid = (seg.get("start", 0.0) + seg.get("end", 0.0)) / 2.0
            best_speaker = "Speaker_00"
            for turn in turns:
                if turn["start"] <= seg_mid <= turn["end"]:
                    # Convert pyannote SPEAKER_00 → Speaker_00 format
                    raw = str(turn["speaker"])
                    best_speaker = re.sub(r"SPEAKER_?(\d+)", r"Speaker_\1", raw)
                    break
            labels.append(best_speaker)
        return labels

    # ── Public API ────────────────────────────────────────────────────────

    async def diarize_segments(
        self,
        audio_path: str,
        segments: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Assign speaker labels to transcript segments.
        Returns enriched segment dicts with speaker_label, has_threat, has_entity, etc.
        """
        from app.config import get_settings
        settings = get_settings()

        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if not segments:
            return []

        loop = asyncio.get_event_loop()

        # Try pyannote (requires HF token)
        speaker_labels: list[str] = []
        hf_token = (
            settings.ai.HF_TOKEN.get_secret_value()
            if settings.ai.HF_TOKEN else None
        )
        if HAS_PYANNOTE and hf_token and self._pyannote_pipeline is None:
            await loop.run_in_executor(None, self._try_load_pyannote, hf_token)

        if self._pyannote_pipeline is not None:
            turns = await loop.run_in_executor(None, self._run_pyannote, audio_path)
            if turns:
                speaker_labels = self._assign_speakers_from_pyannote(segments, turns)

        # Fall back to energy-based
        if not speaker_labels:
            speaker_labels = await loop.run_in_executor(
                None, self._energy_based_speaker_assignment, audio_path, segments
            )

        # Pad speaker labels if needed
        while len(speaker_labels) < len(segments):
            speaker_labels.append("Speaker_00")

        # Build enriched segment dicts
        diarized = []
        for idx, (seg, label) in enumerate(zip(segments, speaker_labels)):
            text = seg.get("text", "")
            text_lower = text.lower()

            # Basic threat flags (refined by call_analyzer later)
            threat_terms = {
                "kill", "murder", "shoot", "bomb", "attack", "extort",
                "blackmail", "ransom", "threaten", "destroy", "burn sim",
                "finish", "eliminate", "police ko bata",
            }
            has_threat = any(term in text_lower for term in threat_terms)

            # Entity hints (digits, known place patterns)
            has_entity = (
                any(c.isdigit() for c in text) or
                bool(re.search(r"\b(?:road|nagar|street|colony|district|city|town)\b", text_lower))
            )

            diarized.append({
                "id": str(uuid.uuid4()),
                "transcript_id": "",  # filled by recording pipeline
                "speaker_label": label,
                "sequence_number": idx,
                "start_time": float(seg.get("start", 0.0)),
                "end_time": float(seg.get("end", 0.0)),
                "text": text,
                "confidence": float(seg.get("confidence", 0.85)),
                "has_threat": has_threat,
                "has_entity": has_entity,
                "has_keyword": has_threat or has_entity,
                "word_count": len(text.split()),
                "character_count": len(text),
            })

        unique_speakers = set(s["speaker_label"] for s in diarized)
        logger.info(
            "diarization_completed",
            audio=path.name,
            segments=len(diarized),
            speakers=len(unique_speakers),
        )
        return diarized
