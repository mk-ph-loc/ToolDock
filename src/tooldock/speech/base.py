"""Κοινό interface παρόχων STT."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TranscriptionResult:
    """Αποτέλεσμα αναγνώρισης."""

    text: str
    provider: str
    language: str


class STTProvider(ABC):
    """Βασική κλάση για όλους τους πάροχους αναγνώρισης."""

    name: str = "base"

    @abstractmethod
    def transcribe(self, audio_path: Path, language: str) -> str:
        """Επιστρέφει κείμενο από αρχείο ήχου WAV."""

    def available(self) -> bool:
        """Ελέγχει αν ο πάροχος μπορεί να χρησιμοποιηθεί."""
        return True
