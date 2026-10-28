"""Plugin υπαγόρευσης S2: live/διάστημα, πάροχοι STT και Ιστός."""
from __future__ import annotations

import logging
import threading
import webbrowser

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication, QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from tooldock.core.config import Config
from tooldock.speech.factory import create_provider
from tooldock.speech.microphone import list_input_devices, record_to_wav

WEB_SERVICES = {
    "speechtexter": ("SpeechTexter", "https://www.speechtexter.com/"),
    "speechnotes": ("SpeechNotes", "https://speechnotes.co/"),
    "dictation": ("Dictation", "https://dictation.io/speech"),
}


class _DictationWidget(QWidget):
    """Widget υπαγόρευσης με live/διάστημα και πάροχο Ιστός."""

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
        self.provider.addItem("Ιστός (SpeechTexter κ.λπ.)", "web")
        self.provider.setCurrentIndex(max(
            0, self.provider.findData(config.get("speech.provider", "google"))))
        self.provider.currentIndexChanged.connect(self._provider_changed)

        self.mode = QComboBox()
        self.mode.addItem("Live (τμήματα 2″)", "live")
        self.mode.addItem("Διάστημα (5″)", "interval")
        self.mode.setCurrentIndex(max(
            0, self.mode.findData(config.get("speech.mode", "live"))))
        self.mode.currentIndexChanged.connect(self._mode_changed)

        self.language = QComboBox()
        self.language.addItem("Ελληνικά", "el-GR")
        self.language.addItem("English", "en-US")
        self.language.setCurrentIndex(max(
            0, self.language.findData(config.get("speech.language", "el-GR"))))
        self.language.currentIndexChanged.connect(self._language_changed)

        self.microphone = QComboBox()
        self.microphone.addItem("Προεπιλεγμένο μικρόφωνο", None)
        try:
            for device in list_input_devices():
                self.microphone.addItem(device["name"], device["index"])
        except Exception as exc:
            self.microphone.addItem(f"Μη διαθέσιμα μικρόφωνα: {exc}", None)
        self.microphone.currentIndexChanged.connect(self._microphone_changed)

        self.web_service = QComboBox()
        for key, (label, _url) in WEB_SERVICES.items():
            self.web_service.addItem(label, key)
        self.web_service.setCurrentIndex(max(
            0, self.web_service.findData(config.get("speech.web_service", "speechtexter"))))
        self.web_service.currentIndexChanged.connect(self._web_service_changed)

        self.open_web = QPushButton("Άνοιγμα υπηρεσίας")
        self.open_web.clicked.connect(self.open_web_service)
        self.paste_web = QPushButton("Λήψη από clipboard")
        self.paste_web.clicked.connect(self.paste_from_clipboard)

        self.record_button = QPushButton("Έναρξη")
        self.record_button.clicked.connect(self.toggle_recording)

        for widget in (self.provider, self.mode, self.language, self.microphone,
                       self.record_button):
            row.addWidget(widget)

        web_row = QHBoxLayout()
        for widget in (self.web_service, self.open_web, self.paste_web):
            web_row.addWidget(widget)

        self.status = QLabel("Έτοιμο")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setWordWrap(True)

        layout.addLayout(row)
        layout.addLayout(web_row)
        layout.addWidget(self.status)
        self.status_changed.connect(self.status.setText)
        self.finished.connect(self._on_finished)
        self._update_mode_visibility()

    def _provider_changed(self) -> None:
        self.config.set("speech.provider", self.provider.currentData())
        self.config.save()
        self._update_mode_visibility()

    def _mode_changed(self) -> None:
        self.config.set("speech.mode", self.mode.currentData())
        self.config.save()

    def _language_changed(self) -> None:
        self.config.set("speech.language", self.language.currentData())
        self.config.save()

    def _microphone_changed(self) -> None:
        self.config.set("speech.microphone", self.microphone.currentData())
        self.config.save()

    def _web_service_changed(self) -> None:
        self.config.set("speech.web_service", self.web_service.currentData())
        self.config.save()

    def _update_mode_visibility(self) -> None:
        is_web = self.provider.currentData() == "web"
        self.web_service.setVisible(is_web)
        self.open_web.setVisible(is_web)
        self.paste_web.setVisible(is_web)
        self.record_button.setVisible(not is_web)
        self.mode.setVisible(not is_web)

    def open_web_service(self) -> None:
        """Ανοίγει την επιλεγμένη υπηρεσία στον browser."""
        key = self.web_service.currentData()
        _label, url = WEB_SERVICES.get(key, ("SpeechTexter", "https://www.speechtexter.com/"))
        QDesktopServices.openUrl(QUrl(url))
        self.status_changed.emit("Μίλα στην υπηρεσία και μετά πάτησε «Λήψη από clipboard».")

    def paste_from_clipboard(self) -> None:
        """Παίρνει κείμενο από το clipboard (web υπηρεσίες)."""
        text = QApplication.clipboard().text().strip()
        self.finished.emit(text or "Δεν βρέθηκε κείμενο στο clipboard")

    def toggle_recording(self) -> None:
        """Ξεκινά ή διακόπτει την υπαγόρευση."""
        if self._busy:
            self._stop_event.set()
            self.status_changed.emit("Διακοπή…")
            return
        self._busy = True
        self._stop_event.clear()
        self.record_button.setText("Διακοπή")
        if self.mode.currentData() == "live":
            self.status_changed.emit("Ακούω… μίλα")
        else:
            self.status_changed.emit("Ηχογράφηση 5″…")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
        """ΠΡΟΣΟΧΗ: εκτελείται σε thread· ενημερώνει το UI μέσω Signals."""
        texts: list[str] = []
        try:
            device = self.config.get("speech.microphone", None)
            language = self.config.get("speech.language", "el-GR")
            provider = create_provider(self.config)
            if self.mode.currentData() == "interval":
                wav_path = record_to_wav(seconds=5, device=device)
                text = provider.transcribe(wav_path, language).strip()
                if text:
                    texts.append(text)
            else:
                while not self._stop_event.is_set():
                    wav_path = record_to_wav(seconds=2, device=device)
                    try:
                        text = provider.transcribe(wav_path, language).strip()
                    except Exception as exc:
                        logging.warning("Σφάλμα τμήματος: %s", exc)
                        self.status_changed.emit(
                            f"Σφάλμα τμήματος ({exc}) — συνεχίζω…")
                        continue
                    if text:
                        texts.append(text)
                        self.status_changed.emit("Μερικό: " + " ".join(texts))
        except Exception as exc:
            logging.exception("Σφάλμα υπαγόρευσης")
            self.finished.emit(f"Σφάλμα: {exc}")
            return
        final_text = " ".join(texts).strip()
        self.finished.emit(final_text or "Δεν αναγνωρίστηκε κείμενο")

    def _on_finished(self, text: str) -> None:
        """Επαναφέρει το κουμπί και εμφανίζει το τελικό κείμενο."""
        self._busy = False
        self.record_button.setText("Έναρξη")
        self.status.setText(text)


class DictationPlugin:
    """Υπαγόρευση με επιλογή πάροχου, γλώσσας, μικροφώνου και λειτουργίας."""

    name = "dictation"
    icon = "🎤"

    def __init__(self, config: Config) -> None:
        self.config = config

    def build_widget(self, mode: str = "compact") -> QWidget:
        """Δημιουργεί το UI της υπαγόρευσης."""
        return _DictationWidget(self.config)
