"""Plugin υπαγόρευσης S2: μικρόφωνο, πάροχοι STT και live γραμμή κατάστασης."""
from __future__ import annotations

import logging
import threading

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from tooldock.core.config import Config
from tooldock.speech.factory import create_provider
from tooldock.speech.microphone import list_input_devices, record_to_wav


class _DictationWidget(QWidget):
    """Widget υπαγόρευσης με live μερική αναγνώριση."""

    status_changed = Signal(str)
    finished = Signal(str)

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self._busy = False
        self._stop_event = threading.Event()

        layout = QVBoxLayout(self)
        row = QHBoxLayout()

        self.provider = QComboBox()
        self.provider.addItem("Google Web Speech", "google")
        self.provider.addItem("faster-whisper (τοπικά)", "whisper")
        self.provider.setCurrentIndex(max(
            0, self.provider.findData(config.get("speech.provider", "google"))))
        self.provider.currentIndexChanged.connect(self._save_provider)

        self.language = QComboBox()
        self.language.addItem("Ελληνικά", "el-GR")
        self.language.addItem("English", "en-US")
        self.language.setCurrentIndex(max(
            0, self.language.findData(config.get("speech.language", "el-GR"))))
        self.language.currentIndexChanged.connect(self._save_language)

        self.microphone = QComboBox()
        self.microphone.addItem("Προεπιλεγμένο μικρόφωνο", None)
        try:
            for device in list_input_devices():
                self.microphone.addItem(device["name"], device["index"])
        except Exception as exc:
            self.microphone.addItem(f"Μη διαθέσιμα μικρόφωνα: {exc}", None)
        self.microphone.currentIndexChanged.connect(self._save_microphone)

        self.record_button = QPushButton("Έναρξη")
        self.record_button.clicked.connect(self.toggle_recording)

        for widget in (self.provider, self.language, self.microphone, self.record_button):
            row.addWidget(widget)

        self.status = QLabel("Έτοιμο")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setWordWrap(True)

        layout.addLayout(row)
        layout.addWidget(self.status)
        self.status_changed.connect(self.status.setText)
        self.finished.connect(self._on_finished)

    def _save_provider(self) -> None:
        self.config.set("speech.provider", self.provider.currentData())
        self.config.save()

    def _save_language(self) -> None:
        self.config.set("speech.language", self.language.currentData())
        self.config.save()

    def _save_microphone(self) -> None:
        self.config.set("speech.microphone", self.microphone.currentData())
        self.config.save()

    def toggle_recording(self) -> None:
        """Ξεκινά ή διακόπτει τη ζωντανή υπαγόρευση."""
        if self._busy:
            self._stop_event.set()
            self.status_changed.emit("Διακοπή…")
            return
        self._busy = True
        self._stop_event.clear()
        self.record_button.setText("Διακοπή")
        self.status_changed.emit("Ακούω… μίλα")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
        """ΠΡΟΣΟΧΗ: εκτελείται σε thread· ενημερώνει το UI μέσω Signals."""
        texts: list[str] = []
        try:
            device = self.config.get("speech.microphone", None)
            language = self.config.get("speech.language", "el-GR")
            provider = create_provider(self.config)
            while not self._stop_event.is_set():
                wav_path = record_to_wav(seconds=2, device=device)
                text = provider.transcribe(wav_path, language).strip()
                if text:
                    texts.append(text)
                    self.status_changed.emit("Μερικό: " + " ".join(texts))
        except Exception as exc:
            logging.exception("Σφάλμα ζωντανής υπαγόρευσης")
            self.finished.emit(f"Σφάλμα: {exc}")
            return
        final_text = " ".join(texts).strip()
        self.finished.emit(final_text or "Δεν αναγνωρίστηκε κείμενο")

    def _on_finished(self, text: str) -> None:
        """Επαναφέρει το κουμπί και εμφανίζει το τελικό κείμενο."""
        self._busy = False
        self.record_button.setText("Έναρξη")
        self.status.setText(text if not text.startswith("Μερικό:") else text)


class DictationPlugin:
    """Υπαγόρευση με επιλογή πάροχου, γλώσσας και μικροφώνου."""

    name = "dictation"
    icon = "🎤"

    def __init__(self, config: Config) -> None:
        self.config = config

    def build_widget(self, mode: str = "compact") -> QWidget:
        """Δημιουργεί το UI της υπαγόρευσης."""
        return _DictationWidget(self.config)
