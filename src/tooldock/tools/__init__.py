"""Κοινό interface plugins."""
from __future__ import annotations
from typing import Protocol
from PySide6.QtWidgets import QWidget


class ToolPlugin(Protocol):
    """Κάθε εργαλείο υλοποιεί αυτό το interface."""
    name: str
    icon: str
    enabled: bool

    def build_widget(self, mode: str) -> QWidget:
        """Δημιουργεί το widget του εργαλείου για το δοσμένο mode."""
        ...

    def settings_schema(self) -> dict:
        """Επιστρέφει σχήμα ρυθμίσεων (μελλοντικά)."""
        return {}
