"""Plugin γρήγορων ενεργειών."""
from __future__ import annotations
from PySide6.QtWidgets import QWidget
from tooldock.tools.quick_actions.__main_widget import QuickActionsWidget


class QuickActionsPlugin:
    name = "quick_actions"
    icon = "⚡"
    enabled = True

    def __init__(self, config=None) -> None:
        self.config = config

    def build_widget(self, mode: str) -> QWidget:
        return QuickActionsWidget()

    def settings_schema(self) -> dict:
        return {}