"""Ηχογράφηση μικροφώνου σε WAV (lazy import sounddevice)."""
from __future__ import annotations

import tempfile
import wave
from pathlib import Path


def list_input_devices() -> list[dict]:
    """Επιστρέφει τις διαθέσιμες συσκευές εισόδου."""
    import sounddevice as sd

    devices = sd.query_devices()
    return [
        {"index": i, "name": d["name"]}
        for i, d in enumerate(devices)
        if d["max_input_channels"] > 0
    ]


def record_to_wav(seconds: int = 5, samplerate: int = 16000,
                  device: int | None = None) -> Path:
    """Ηχογραφεί από επιλεγμένο μικρόφωνο και επιστρέφει WAV αρχείο."""
    import sounddevice as sd
    import numpy as np

    recording = sd.rec(
        int(seconds * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="int16",
        device=device,
    )
    sd.wait()
    path = Path(tempfile.gettempdir()) / "tooldock_recording.wav"
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(recording.tobytes())
    return path