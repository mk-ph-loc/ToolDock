"""Κύριο παράθυρο: 3 modes, dock, always-on-top, tray."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QMenu, QPushButton, QStackedWidget,
    QSystemTrayIcon, QVBoxLayout, QWidget,
)
from tooldock.core.config import Config
from tooldock.tools.text_notes import TextNotesPlugin
from tooldock.tools.quick_actions.plugin import QuickActionsPlugin


class Shell(QMainWindow):
    """Κύριο shell της εφαρμογής."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self.setWindowTitle("ToolDock")
        self.plugins = [TextNotesPlugin(config), QuickActionsPlugin(config)]
        self.stack = QStackedWidget()
        for plugin in self.plugins:
            self.stack.addWidget(plugin.build_widget("compact"))

        side = QHBoxLayout()
        self.mode_buttons: list[QPushButton] = []
        for index, plugin in enumerate(self.plugins):
            button = QPushButton(plugin.icon)
            button.setFixedWidth(40)
            button.clicked.connect(lambda _=False, i=index: self.stack.setCurrentIndex(i))
            self.mode_buttons.append(button)
            side.addWidget(button)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addLayout(side)
        layout.addWidget(self.stack)
        self.setCentralWidget(central)

        self.apply_window_settings()
        self._make_tray()

    def apply_window_settings(self) -> None:
        """Εφαρμογή mode, dock και always-on-top από config."""
        win = self.config.get("window", {})
        self.resize(win.get("width", 360), win.get("height", 520))
        flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        if win.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        dock = win.get("dock", "right")
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = self.width(), self.height()
        positions = {
            "left": (screen.left(), screen.center().y() - h // 2),
            "right": (screen.right() - w, screen.center().y() - h // 2),
            "top": (screen.center().x() - w // 2, screen.top()),
            "bottom": (screen.center().x() - w // 2, screen.bottom() - h),
            "floating": (screen.center().x() - w // 2, screen.center().y() - h // 2),
        }
        self.move(*positions.get(dock, positions["right"]))

    def _make_tray(self) -> None:
        """Εικονίδιο tray και μενού."""
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("ToolDock")
        menu = QMenu()
        show_action = QAction("Εμφάνιση", self)
        show_action.triggered.connect(self.showNormal)
        settings_action = QAction("Ρυθμίσεις", self)
        settings_action.triggered.connect(self.open_settings)
        quit_action = QAction("Έξοδος", self)
        quit_action.triggered.connect(QApplication.quit)
        for action in (show_action, settings_action, quit_action):
            menu.addAction(action)
        self.tray.setContextMenu(menu)
        self.tray.setIcon(self.windowIcon() or QIcon())
        from PySide6.QtWidgets import QStyle
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray.setIcon(icon)
        self.tray.show()

    def open_settings(self) -> None:
        """Άνοιγμα παραθύρου ρυθμίσεων."""
        from tooldock.ui.settings import SettingsDialog
        SettingsDialog(self.config, self).exec()
        self.apply_window_settings()

    def closeEvent(self, event) -> None:  # noqa: N802
        """Κλείσιμο → ελαχιστοποίηση στο tray."""
        event.ignore()
        self.hide()
