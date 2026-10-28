"""Εργαλείο σημειώσεων/υπαγόρευσης-κειμένου του S1."""
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QComboBox, QHBoxLayout
from tooldock.core.config import Config
from tooldock.core.storage import append_note


class TextNotesWidget(QWidget):
    """Πλαίσιο κειμένου + OK/Enter: clipboard, Base.txt και αρχείο θέματος."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        layout = QVBoxLayout(self)
        self.text = QPlainTextEdit()
        self.text.setPlaceholderText("Γράψε ή επικόλλησε κείμενο… (Enter = OK, Shift+Enter = νέα γραμμή)")
        self.topic = QComboBox()
        self.topic.addItem("— Χωρίς θέμα —")
        self.topic.addItems(config.get("notes.topics", []))
        row = QHBoxLayout()
        self.ok = QPushButton("OK")
        self.notepad = QPushButton("📝 Notepad")
        row.addWidget(self.topic); row.addWidget(self.notepad); row.addWidget(self.ok)
        layout.addWidget(self.text); layout.addLayout(row)
        self.ok.clicked.connect(self.save_note)
        self.notepad.clicked.connect(self.open_notepad)

    def keyPressEvent(self, event) -> None:  # noqa: N802
        from PySide6.QtCore import Qt
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.save_note()
        else:
            super().keyPressEvent(event)

    def save_note(self) -> None:
        """Αποθήκευση: clipboard + Base.txt (+ θέμα)."""
        # ΠΡΟΣΟΧΗ: το clipboard αντικαθίσταται με το τρέχον κείμενο.
        from PySide6.QtWidgets import QApplication
        text = self.text.toPlainText().strip()
        if not text:
            return
        topic = None if self.topic.currentIndex() == 0 else self.topic.currentText()
        QApplication.clipboard().setText(text)
        base = self.config.path.parent / self.config.get("notes.base_file", "data/Base.txt")
        append_note(base, text, topic)
        self.text.clear()

    def open_notepad(self) -> None:
        """Άνοιγμα Base.txt στο Notepad."""
        import subprocess
        base = self.config.path.parent / self.config.get("notes.base_file", "data/Base.txt")
        base.parent.mkdir(parents=True, exist_ok=True)
        base.touch(exist_ok=True)
        subprocess.Popen(["notepad.exe", str(base)])


class TextNotesPlugin:
    name = "text_notes"
    icon = "📝"
    enabled = True

    def __init__(self, config: Config) -> None:
        self.config = config

    def build_widget(self, mode: str) -> QWidget:
        return TextNotesWidget(self.config)

    def settings_schema(self) -> dict:
        return {}
