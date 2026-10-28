"""Εκκίνηση ToolDock: single instance, config, data, shell."""
from __future__ import annotations
import sys
from PySide6.QtCore import Qt
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication
from tooldock.core.config import Config
from tooldock.core.storage import ensure_data_files
from tooldock.ui.shell import Shell

APP_KEY = "tooldock-single-instance"


def is_already_running() -> bool:
    """Έλεγχος single instance μέσω QLocalSocket."""
    socket = QLocalSocket()
    socket.connectToServer(APP_KEY)
    running = socket.waitForConnected(200)
    socket.abort()
    return running


def main() -> int:
    """Σημείο εισόδου της εφαρμογής."""
    app = QApplication(sys.argv)
    app.setApplicationName("ToolDock")
    app.setQuitOnLastWindowClosed(False)

    if is_already_running():
        return 0

    config = Config()
    base = config.path.parent / config.get("notes.base_file", "data/Base.txt")
    ensure_data_files(base, config.get("notes.topics", []))

    # ΠΡΟΣΟΧΗ: ο server πρέπει να μείνει ζωντανός για όλη τη διάρκεια της εφαρμογής.
    QLocalServer.removeServer(APP_KEY)
    server = QLocalServer()
    server.listen(APP_KEY)

    shell = Shell(config)
    shell.show()
    return app.exec()
