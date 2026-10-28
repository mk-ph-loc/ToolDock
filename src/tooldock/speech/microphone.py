"""Ηχογράφηση μικροφώνου σε WAV (lazy import sounddevice)."""
from __future__ import annotations

import tempfile
import wave
from pathlib import Path


def record_to_wav(seconds: int = 5, samplerate: int = 16000) -> Path:
    """Ηχογραφεί από το προεπιλεγμένο μικρόφωνο και επιστρέφει WAV αρχείο."""
    try:
        import sounddevice as sd
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "Λείπει το sounddevice. Εγκαταστήστε το από requirements-optional.txt"
        ) from exc
    recording = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    path = Path(tempfile.gettempdir()) / "tooldock_recording.wav"
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(recording.tobytes())
    return path
