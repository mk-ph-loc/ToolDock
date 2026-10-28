"""Γρήγορες ενέργειες S1: Downloads και Browser."""
from __future__ import annotations
import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class QuickActionsWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        downloads = QPushButton("📂 Downloads")
        browser = QPushButton("🌐 Browser")
        downloads.clicked.connect(self.open_downloads)
        browser.clicked.connect(self.open_browser)
        layout.addWidget(downloads); layout.addWidget(browser)

    def open_downloads(self) -> None:
        # ΠΡΟΣΟΧΗ: άνοιγμα τοπικού φακέλου.
        downloads = Path.home() / "Downloads"
        downloads.mkdir(exist_ok=True)
        os.startfile(str(downloads))  # noqa: S606

    def open_browser(self) -> None:
        """Άνοιγμα ιστοσελίδας στον προεπιλεγμένο browser."""
        import webbrowser

        webbrowser.open("https://www.google.com")