"""Επιλογή πάροχου STT βάσει ρυθμίσεων."""
from __future__ import annotations

from tooldock.core.config import Config
from tooldock.speech.base import STTProvider
from tooldock.speech.google_web import GoogleWebSpeechProvider
from tooldock.speech.whisper_local import FasterWhisperProvider


def create_provider(config: Config) -> STTProvider:
    """Επιστρέφει τον επιλεγμένο πάροχο από το config."""
    name = config.get("speech.provider", "google")
    if name == "whisper":
        return FasterWhisperProvider(config)
    return GoogleWebSpeechProvider(config)
