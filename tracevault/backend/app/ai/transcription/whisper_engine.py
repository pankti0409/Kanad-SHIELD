"""
TraceVault AI Engine — Speech-to-Text & Audio Transcription
Prioritizes faster-whisper (best performance), falls back to openai-whisper,
then SpeechRecognition as last resort.
"""
from __future__ import annotations

import asyncio
import wave
from pathlib import Path
from typing import Any, Optional
import structlog

logger = structlog.get_logger(__name__)

# ── Detect available transcription backends ────────────────────────────────

HAS_FASTER_WHISPER = False
HAS_OPENAI_WHISPER = False
HAS_SPEECH_RECOGNITION = False

try:
    from faster_whisper import WhisperModel as FasterWhisperModel
    HAS_FASTER_WHISPER = True
    logger.debug("faster_whisper available")
except ImportError:
    pass

if not HAS_FASTER_WHISPER:
    try:
        import whisper as openai_whisper
        HAS_OPENAI_WHISPER = True
        logger.debug("openai_whisper available")
    except ImportError:
        pass

try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
    logger.debug("speech_recognition available")
except ImportError:
    pass


class WhisperTranscriptionEngine:
    """
    Speech-to-Text engine.
    Backend priority: faster-whisper > openai-whisper > SpeechRecognition
    """

    def __init__(self, model_size: str = "base", device: str = "auto") -> None:
        # Clamp model size to avoid OOM on dev machines
        safe_models = {"tiny", "base", "small", "medium", "large", "large-v2", "large-v3"}
        self.model_size = model_size if model_size in safe_models else "base"
        self.device = device
        self._fw_model = None
        self._ow_model = None

    # ── Model loaders ─────────────────────────────────────────────────────

    def _get_faster_whisper_model(self):
        if self._fw_model is None and HAS_FASTER_WHISPER:
            try:
                # Use CPU + int8 for universal compatibility
                compute_type = "int8"
                self._fw_model = FasterWhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type=compute_type,
                )
                logger.info("faster_whisper_loaded", model=self.model_size)
            except Exception as exc:
                logger.warning("faster_whisper_load_failed", error=str(exc))
                self._fw_model = None
        return self._fw_model

    def _get_openai_whisper_model(self):
        if self._ow_model is None and HAS_OPENAI_WHISPER:
            try:
                self._ow_model = openai_whisper.load_model(self.model_size)
                logger.info("openai_whisper_loaded", model=self.model_size)
            except Exception as exc:
                logger.warning("openai_whisper_load_failed", error=str(exc))
                self._ow_model = None
        return self._ow_model

    # ── Audio utilities ───────────────────────────────────────────────────

    def _probe_audio_duration(self, path: Path) -> float:
        """Estimate audio duration from file header or size."""
        try:
            if path.suffix.lower() in (".wav", ".wave"):
                with wave.open(str(path), "rb") as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    if rate > 0:
                        return float(frames) / rate
        except Exception:
            pass
        # Try pydub for accurate duration across all formats
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(path))
            return len(audio) / 1000.0
        except Exception:
            pass
        size_bytes = path.stat().st_size
        return min(max(3.0, round(size_bytes / 32000.0, 1)), 7200.0)

    def _preprocess_audio(self, path: Path) -> Path:
        """
        Convert audio to 16kHz mono WAV for reliable Whisper transcription.
        Returns path to the (possibly converted) WAV file.
        Falls back to the original file if pydub is unavailable.
        """
        # Already a WAV — just return as-is
        if path.suffix.lower() in (".wav", ".wave"):
            return path

        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(path))
            # Normalize: 16kHz mono
            audio = audio.set_frame_rate(16000).set_channels(1)
            wav_path = path.with_suffix(".converted.wav")
            audio.export(str(wav_path), format="wav")
            logger.info("audio_preprocessed", original=path.name, output=wav_path.name)
            return wav_path
        except Exception as exc:
            logger.warning("audio_preprocess_failed_fallback", error=str(exc), path=str(path))
            return path  # Fall back to original file, let Whisper attempt it directly

    # ── Transcription backends ────────────────────────────────────────────

    def _transcribe_faster_whisper(
        self, path: Path, language: Optional[str] = None
    ) -> dict[str, Any]:
        model = self._get_faster_whisper_model()
        if model is None:
            return {}

        try:
            lang_arg = None if language in (None, "auto") else language
            segments_gen, info = model.transcribe(
                str(path),
                language=lang_arg,
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
            )

            segments_list = list(segments_gen)  # materialize generator
            full_text = " ".join(seg.text.strip() for seg in segments_list)
            detected_lang = info.language if info.language else (language or "en")
            duration = info.duration if info.duration else self._probe_audio_duration(path)

            raw_segments = []
            for idx, seg in enumerate(segments_list):
                text = seg.text.strip()
                if text:
                    avg_logprob = getattr(seg, "avg_logprob", -0.15)
                    confidence = min(1.0, max(0.0, 1.0 + avg_logprob))
                    raw_segments.append({
                        "sequence_number": idx,
                        "start": round(float(seg.start), 2),
                        "end": round(float(seg.end), 2),
                        "text": text,
                        "confidence": round(confidence, 3),
                    })

            return {
                "full_text": full_text,
                "detected_language": detected_lang,
                "duration": duration,
                "confidence": 0.92,
                "segments": raw_segments,
                "model_used": f"faster-whisper-{self.model_size}",
            }
        except Exception as exc:
            logger.warning("faster_whisper_transcribe_failed", error=str(exc))
            return {}

    def _transcribe_openai_whisper(
        self, path: Path, language: Optional[str] = None
    ) -> dict[str, Any]:
        model = self._get_openai_whisper_model()
        if model is None:
            return {}

        try:
            lang_arg = None if language in (None, "auto") else language
            result = model.transcribe(
                str(path),
                language=lang_arg,
                beam_size=1,
                best_of=1,
                fp16=False,
            )
            full_text = result.get("text", "").strip()
            detected_lang = result.get("language", language or "en")

            raw_segments = []
            for idx, seg in enumerate(result.get("segments", [])):
                text = seg.get("text", "").strip()
                if text:
                    raw_segments.append({
                        "sequence_number": idx,
                        "start": round(float(seg.get("start", 0.0)), 2),
                        "end": round(float(seg.get("end", 0.0)), 2),
                        "text": text,
                        "confidence": 0.90,
                    })

            return {
                "full_text": full_text,
                "detected_language": detected_lang,
                "duration": self._probe_audio_duration(path),
                "confidence": 0.90,
                "segments": raw_segments,
                "model_used": f"openai-whisper-{self.model_size}",
            }
        except Exception as exc:
            logger.warning("openai_whisper_transcribe_failed", error=str(exc))
            return {}

    def _transcribe_speech_recognition(self, path: Path, language: Optional[str] = None) -> dict[str, Any]:
        if not HAS_SPEECH_RECOGNITION:
            return {}
        try:
            import speech_recognition as sr
            import re
            r = sr.Recognizer()
            with sr.AudioFile(str(path)) as source:
                audio_data = r.record(source)
                
                lang_code = "en-US"
                if language and language != "auto":
                    lang_map = {
                        "en": "en-US", "hi": "hi-IN", "es": "es-ES", "fr": "fr-FR",
                        "de": "de-DE", "it": "it-IT", "zh": "zh-CN", "ja": "ja-JP",
                        "ru": "ru-RU", "pt": "pt-BR", "ar": "ar-SA",
                    }
                    lang_code = lang_map.get(language.lower()[:2], language)
                
                text = r.recognize_google(audio_data, language=lang_code)
            
            raw_text = text.strip()
            duration = self._probe_audio_duration(path)

            # Split into sentence-level segments
            sentence_ends = re.compile(r'([.!?।]+)\s*')
            parts = sentence_ends.split(raw_text)
            sentences = []
            for j in range(0, len(parts) - 1, 2):
                sent = parts[j] + parts[j+1]
                if sent.strip():
                    sentences.append(sent.strip())
            if len(parts) % 2 == 1 and parts[-1].strip():
                sentences.append(parts[-1].strip())
            
            # If no sentence boundaries are present, split into chunks of ~12 words
            has_punctuation = any(p in raw_text for p in ['.', '!', '?', '।'])
            if not has_punctuation or not sentences:
                words = raw_text.split()
                chunk_size = 12
                sentences = []
                for idx in range(0, len(words), chunk_size):
                    chunk = " ".join(words[idx:idx+chunk_size])
                    if chunk:
                        sentences.append(chunk)

            if not sentences:
                sentences = [raw_text]

            # Generate segments with proportional timeline timestamps
            total_chars = sum(len(s) for s in sentences)
            current_time = 0.0
            raw_segments = []
            for idx, sent in enumerate(sentences):
                char_ratio = len(sent) / total_chars if total_chars > 0 else 1.0
                sent_duration = duration * char_ratio
                
                start_time = round(current_time, 2)
                end_time = round(current_time + sent_duration, 2)
                current_time = end_time
                
                raw_segments.append({
                    "sequence_number": idx,
                    "start": start_time,
                    "end": end_time,
                    "text": sent,
                    "confidence": 0.80,
                })

            return {
                "full_text": raw_text,
                "detected_language": language if (language and language != "auto") else "en",
                "duration": duration,
                "confidence": 0.80,
                "segments": raw_segments,
                "model_used": "speech-recognition-google",
            }
        except Exception as exc:
            logger.debug("speech_recognition_failed", error=str(exc))
            return {}

    # ── Public API ────────────────────────────────────────────────────────

    async def transcribe(
        self,
        audio_path: str,
        language: str = "auto",
    ) -> dict[str, Any]:
        """
        Transcribe audio file. Returns segments with timestamps and metadata.
        Runs blocking model inference in a thread executor to avoid blocking the event loop.
        Automatically preprocesses non-WAV audio (MP3, M4A, OGG, etc.) to 16kHz mono WAV.
        """
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        duration = self._probe_audio_duration(path)
        lang = None if language == "auto" else language

        loop = asyncio.get_event_loop()

        # Preprocess audio: convert to 16kHz mono WAV for best Whisper compatibility
        processed_path = await loop.run_in_executor(None, self._preprocess_audio, path)

        # Try faster-whisper first
        if HAS_FASTER_WHISPER:
            result = await loop.run_in_executor(
                None, self._transcribe_faster_whisper, processed_path, lang
            )
            if result.get("full_text"):
                return self._format_result(result, duration)

        # Try SpeechRecognition next (much faster online fallback than CPU-based openai-whisper)
        if HAS_SPEECH_RECOGNITION:
            sr_path = processed_path if processed_path.suffix.lower() in (".wav", ".wave") else path
            if sr_path.suffix.lower() in (".wav", ".wave"):
                result = await loop.run_in_executor(
                    None, self._transcribe_speech_recognition, sr_path, lang
                )
                if result.get("full_text"):
                    return self._format_result(result, duration)

        # Try openai-whisper as last resort
        if HAS_OPENAI_WHISPER:
            result = await loop.run_in_executor(
                None, self._transcribe_openai_whisper, processed_path, lang
            )
            if result.get("full_text"):
                return self._format_result(result, duration)

        # No speech detected / no backend available
        logger.warning("no_transcription_backend_succeeded", audio=str(path))
        return self._empty_result(path.name, duration, language)

    def _format_result(self, result: dict, fallback_duration: float) -> dict[str, Any]:
        """Normalise result dict into the standard output format."""
        return {
            "language": result.get("detected_language", "en"),
            "language_confidence": 0.95,
            "full_text": result.get("full_text", ""),
            "duration_seconds": result.get("duration") or fallback_duration,
            "word_count": len(result.get("full_text", "").split()),
            "character_count": len(result.get("full_text", "")),
            "confidence": result.get("confidence", 0.85),
            "segments": result.get("segments", []),
            "model_used": result.get("model_used", "unknown"),
        }

    def _empty_result(self, filename: str, duration: float, language: str) -> dict[str, Any]:
        text = f"[No audible speech detected in recording: {filename}]"
        return {
            "language": language if language != "auto" else "en",
            "language_confidence": 0.5,
            "full_text": text,
            "duration_seconds": duration,
            "word_count": 0,
            "character_count": len(text),
            "confidence": 0.0,
            "segments": [{"sequence_number": 0, "start": 0.0, "end": duration, "text": text, "confidence": 0.0}],
            "model_used": "none",
        }
