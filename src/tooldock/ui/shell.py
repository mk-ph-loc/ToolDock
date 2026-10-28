"""Shell v0.1.1: μετακίνηση, dock τρέχουσας οθόνης, tray και έξοδος."""
from __future__ import annotations
import logging
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QHBoxLayout, QMainWindow,
    QMenu, QPushButton, QStackedWidget, QStyle, QSystemTrayIcon,
    QVBoxLayout, QWidget,
)
from tooldock.core.config import Config
from tooldock.core.placement import place
from tooldock.tools.text_notes import TextNotesPlugin
from tooldock.tools.quick_actions.plugin import QuickActionsPlugin
from tooldock.tools.dictation import DictationPlugin


class Shell(QMainWindow):
    """Κεντρικό παράθυρο με ανεξάρτητο dock και always-on-top."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        log_dir = config.path.parent / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=str(log_dir / "tooldock.log"),
                            encoding="utf-8", level=logging.INFO)
        self._adjusting = True
        self._quitting = False
        self.setWindowTitle("ToolDock v0.1.1")
        if config.get("window.layout_version", 0) < 1:
            config.set("window.dock", "floating")
            config.set("window.layout_version", 1)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._remember)
        self.plugins = [
            TextNotesPlugin(config),
            QuickActionsPlugin(config),
            DictationPlugin(config),
        ]
        self.stack = QStackedWidget()
        central = QWidget()
        layout = QVBoxLayout(central)
        toolbar = QHBoxLayout()
        self.position = QComboBox()
        for label, value in (("Ελεύθερο", "floating"), ("Dock αριστερά", "left"),
                             ("Dock δεξιά", "right"), ("Dock πάνω", "top"),
                             ("Dock κάτω", "bottom")):
            self.position.addItem(label, value)
        self.position.currentIndexChanged.connect(self._dock_changed)
        self.pin = QCheckBox("Πάνω")
        self.pin.setToolTip("Πάντα πάνω από άλλα παράθυρα")
        self.pin.toggled.connect(self._pin_changed)
        settings = QPushButton("Ρυθμίσεις")
        settings.clicked.connect(self.open_settings)
        quit_button = QPushButton("Έξοδος")
        quit_button.clicked.connect(self.quit_app)
        for widget in (self.position, self.pin, settings, quit_button):
            toolbar.addWidget(widget)
        layout.addLayout(toolbar)
        tools = QHBoxLayout()
        for index, plugin in enumerate(self.plugins):
            self.stack.addWidget(plugin.build_widget("compact"))
            button = QPushButton(plugin.icon)
            button.clicked.connect(lambda checked=False, i=index: self.stack.setCurrentIndex(i))
            tools.addWidget(button)
        layout.addLayout(tools)
        layout.addWidget(self.stack)
        self.setCentralWidget(central)
        self.resize(config.get("window.width", 480), config.get("window.height", 520))
        self._make_tray()
        app = QApplication.instance()
        app.screenRemoved.connect(self._screens_changed)
        app.screenAdded.connect(self._screens_changed)
        for screen in app.screens():
            screen.availableGeometryChanged.connect(self._screens_changed)
        self.apply_window_settings(restore=True)
        app.aboutToQuit.connect(self._remember)

    def _target_screen(self):
        """Προτεραιότητα στην οθόνη που περιέχει το κέντρο του παραθύρου."""
        return (QGuiApplication.screenAt(self.frameGeometry().center())
                or self.screen() or QGuiApplication.primaryScreen())

    def apply_window_settings(self, restore: bool = False) -> None:
        """Επαναφορά flags και θέσης χωρίς απώλεια του ορατού παραθύρου."""
        self._timer.stop()
        self._adjusting = True
        config = self.config
        dock = config.get("window.dock", "floating")
        screen = self._target_screen()
        if restore:
            screen = next((s for s in QGuiApplication.screens()
                           if s.name() == config.get("window.screen")), screen)
        self.position.blockSignals(True)
        self.position.setCurrentIndex(max(0, self.position.findData(dock)))
        self.position.blockSignals(False)
        self.pin.blockSignals(True)
        self.pin.setChecked(config.get("window.always_on_top", True))
        self.pin.blockSignals(False)
        flags = Qt.WindowType.Window
        if dock != "floating":
            flags |= Qt.WindowType.FramelessWindowHint
        if self.pin.isChecked():
            flags |= Qt.WindowType.WindowStaysOnTopHint
        previous = self.frameGeometry().topLeft()
        self.setWindowFlags(flags)
        self.show()
        rect = screen.availableGeometry()
        if restore:
            previous = QPoint(config.get("window.x", rect.x() + 40),
                              config.get("window.y", rect.y() + 40))
        QTimer.singleShot(0, lambda: self._fit(screen, previous))

    def _fit(self, screen=None, position=None) -> None:
        """Περιορισμός του εξωτερικού πλαισίου, μαζί με τη μπάρα τίτλου."""
        if screen not in QGuiApplication.screens():
            screen = self._target_screen()
        bounds = screen.availableGeometry()
        frame = self.frameGeometry()
        extra_w = frame.width() - self.width()
        extra_h = frame.height() - self.height()
        point = position if position is not None else frame.topLeft()
        x, y, w, h = place((bounds.x(), bounds.y(), bounds.width(), bounds.height()),
                          (frame.width(), frame.height()), (point.x(), point.y()),
                          self.config.get("window.dock", "floating"))
        self.resize(max(1, w - extra_w), max(1, h - extra_h))
        delta = QPoint(x, y) - self.frameGeometry().topLeft()
        self.move(self.pos() + delta)
        self._adjusting = False
        self._remember()

    def _dock_changed(self) -> None:
        self.config.set("window.dock", self.position.currentData())
        self.apply_window_settings()

    def _pin_changed(self, enabled: bool) -> None:
        self.config.set("window.always_on_top", enabled)
        self.apply_window_settings()

    def _remember(self) -> None:
        if self._adjusting:
            return
        rect = self.frameGeometry()
        for key, value in (("x", rect.x()), ("y", rect.y()),
                           ("width", self.width()), ("height", self.height()),
                           ("screen", self._target_screen().name())):
            self.config.set(f"window.{key}", value)
        try:
            self.config.save()
        except OSError:
            logging.exception("Αδυναμία αποθήκευσης θέσης παραθύρου")

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        if not self._adjusting:
            self._timer.start(400)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._adjusting:
            self._timer.start(400)

    def _screens_changed(self, *args) -> None:
        for screen in QGuiApplication.screens():
            try:
                screen.availableGeometryChanged.connect(self._screens_changed, Qt.ConnectionType.UniqueConnection)
            except (RuntimeError, TypeError):
                pass
        QTimer.singleShot(100, self._fit)

    def _make_tray(self) -> None:
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.setWindowIcon(icon)
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("ToolDock v0.1.1")
        menu = QMenu(self)
        for label, callback in (("Εμφάνιση", self.showNormal),
                                ("Ρυθμίσεις", self.open_settings),
                                ("Έξοδος", self.quit_app)):
            action = QAction(label, self)
            action.triggered.connect(callback)
            menu.addAction(action)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def open_settings(self) -> None:
        from tooldock.ui.settings import SettingsDialog
        if SettingsDialog(self.config, self).exec():
            self.apply_window_settings()

    def quit_app(self) -> None:
        """ΠΡΟΣΟΧΗ: έξοδος· μη υποβλημένο κείμενο δεν αποθηκεύεται."""
        self._remember()
        self._quitting = True
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event) -> None:
        self._remember()
        if self._quitting or not QSystemTrayIcon.isSystemTrayAvailable():
            event.accept()
            QApplication.quit()
        else:
            event.ignore()
            self.hide()
