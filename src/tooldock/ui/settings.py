"""Παράθυρο ρυθμίσεων S1."""
from __future__ import annotations
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
)
from tooldock.core.config import Config


class SettingsDialog(QDialog):
    """Βασικές ρυθμίσεις: mode, dock, on-top, autostart, συντόμευση."""

    def __init__(self, config: Config, parent=None) -> None:
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Ρυθμίσεις ToolDock")
        form = QFormLayout(self)

        self.dock = QComboBox()
        self.dock.addItems(["floating", "left", "right", "top", "bottom"])
        self.dock.setCurrentText(config.get("window.dock", "right"))
        self.on_top = QCheckBox("Πάντα από πάνω")
        self.on_top.setChecked(config.get("window.always_on_top", True))
        self.autostart = QCheckBox("Εκκίνηση με τα Windows")
        self.autostart.setChecked(config.get("autostart", False))
        self.desktop = QCheckBox("Δημιουργία συντόμευσης επιφάνειας εργασίας")

        form.addRow("Θέση", self.dock)
        form.addRow("", self.on_top)
        form.addRow("", self.autostart)
        form.addRow("", self.desktop)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def save(self) -> None:
        """Αποθήκευση ρυθμίσεων και δημιουργία shortcuts αν χρειάζεται."""
        self.config.set("window.dock", self.dock.currentText())
        self.config.set("window.always_on_top", self.on_top.isChecked())
        self.config.set("autostart", self.autostart.isChecked())
        self.config.save()
        if self.desktop.isChecked():
            self._create_shortcut("desktop")
        if self.autostart.isChecked():
            self._create_shortcut("startup")
        self.accept()

    def _create_shortcut(self, target: str) -> None:
        """Δημιουργία .lnk μέσω PowerShell (desktop ή shell:startup)."""
        # ΠΡΟΣΟΧΗ: δημιουργεί αρχείο .lnk εκτός της εφαρμογής.
        if target == "desktop":
            folder = Path.home() / "Desktop"
        else:
            folder = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
        folder.mkdir(parents=True, exist_ok=True)
        link = folder / "ToolDock.lnk"
        app = Path(__file__).resolve().parents[2] / "run.bat"
        ps = (
            f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{link}');"
            f"$s.TargetPath='{app}';$s.Save()"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False)  # noqa: S603,S607
