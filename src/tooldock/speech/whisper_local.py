"""Τοπική αναγνώριση με faster-whisper (lazy import, χωρίς αυτόματη λήψη)."""
from __future__ import annotations

import logging
from pathlib import Path

from tooldock.core.config import Config
from tooldock.speech.base import STTProvider


class FasterWhisperProvider(STTProvider):
    """Offline αναγνώριση με faster-whisper."""

    name = "whisper"

    def __init__(self, config: Config) -> None:
        self.config = config
        self._model = None

    def transcribe(self, audio_path: Path, language: str) -> str:
        """Αναγνωρίζει WAV αρχείο τοπικά. ΠΡΟΣΟΧΗ: μπορεί να κατεβάσει μοντέλο στην πρώτη χρήση."""
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "Λείπει το faster-whisper. Εγκαταστήστε το από requirements-optional.txt"
            ) from exc
        model_name = self.config.get("speech.whisper.model", "small")
        if self._model is None:
            self._model = WhisperModel(model_name, device="cpu", compute_type="int8")
        segments, _info = self._model.transcribe(str(audio_path), language=language[:2])
        return " ".join(segment.text.strip() for segment in segments).strip()
