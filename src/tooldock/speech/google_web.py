"""Google Web Speech μέσω SpeechRecognition (lazy import)."""
from __future__ import annotations

import logging
from pathlib import Path

from tooldock.speech.base import STTProvider


class GoogleWebSpeechProvider(STTProvider):
    """Online αναγνώριση μέσω Google Web Speech API."""

    name = "google"

    def transcribe(self, audio_path: Path, language: str) -> str:
        """Αναγνωρίζει WAV αρχείο και επιστρέφει κείμενο."""
        try:
            import speech_recognition as sr
        except ImportError as exc:
            raise RuntimeError(
                "Λείπει το SpeechRecognition. Εγκαταστήστε το από requirements-optional.txt"
            ) from exc
        recognizer = sr.Recognizer()
        with sr.AudioFile(str(audio_path)) as source:
            audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio, language=language)
        except Exception as exc:  # noqa: BLE001
            logging.exception("Αποτυχία Google Web Speech")
            raise RuntimeError(f"Google Web Speech απέτυχε: {exc}") from exc
