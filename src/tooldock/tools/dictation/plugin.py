"""Plugin υπαγόρευσης S2: μικρόφωνο, πάροχοι STT και γραμμή κατάστασης."""
from __future__ import annotations

import logging
import tempfile
import threading
from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from tooldock.core.config import Config
from tooldock.speech.base import STTProvider
from tooldock.speech.factory import create_provider
from tooldock.speech.microphone import record_to_wav


class DictationPlugin:
    """Υπαγόρευση με επιλογή πάροχου και γλώσσας."""

    name = "dictation"
    icon = "🎤"

    def __init__(self, config: Config) -> None:
        self.config = config
        self._busy = False

    def build_widget(self, mode: str = "compact") -> QWidget:
        """Δημιουργεί το UI της υπαγόρευσης."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        row = QHBoxLayout()
        self.provider = QComboBox()
        self.provider.addItem("Google Web Speech", "google")
        self.provider.addItem("faster-whisper (τοπικά)", "whisper")
        self.provider.setCurrentIndex(max(0, self.provider.findData(
            self.config.get("speech.provider", "google"))))
        self.provider.currentIndexChanged.connect(self._provider_changed)
        self.language = QComboBox()
        for label, code in (("Ελληνικά", "el-GR"), ("English", "en-US")):
            self.language.addItem(label, code)
        self.language.setCurrentIndex(max(0, self.language.findData(
            self.config.get("speech.language", "el-GR"))))
        self.language.currentIndexChanged.connect(self._language_changed)
        self.record = QPushButton("Ηχογράφηση")
        self.record.clicked.connect(self.start_recording)
        for item in (self.provider, self.language, self.record):
            row.addWidget(item)
        self.status = QLabel("Έτοιμο")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(row)
        layout.addWidget(self.status)
        return widget

    def set_status(self, text: str) -> None:
        """Ενημερώνει τη γραμμή κατάστασης."""
        self.status.setText(text)

    def _provider_changed(self) -> None:
        self.config.set("speech.provider", self.provider.currentData())
        self.config.save()

    def _language_changed(self) -> None:
        self.config.set("speech.language", self.language.currentData())
        self.config.save()

    def start_recording(self) -> None:
        """Ξεκινά ηχογράφηση και αναγνώριση σε background thread."""
        if self._busy:
            return
        self._busy = True
        self.set_status("Ηχογράφηση…")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
        """ΠΡΟΣΟΧΗ: εκτελείται σε thread· ενημερώνει UI μέσω QTimer."""
        from PySide6.QtCore import QTimer
        try:
            wav = record_to_wav()
            provider = create_provider(self.config)
            text = provider.transcribe(wav, self.config.get("speech.language", "el-GR"))
            QTimer.singleShot(0, lambda: self.set_status(f"Κείμενο: {text[:80]}"))
        except Exception as exc:  # noqa: BLE001
            logging.exception("Σφάλμα υπαγόρευσης")
            QTimer.singleShot(0, lambda: self.set_status(f"Σφάλμα: {exc}"))
        finally:
            self._busy = False
