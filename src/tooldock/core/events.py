"""Απλό bus σημάτων για μελλοντική ένδειξη δραστηριότητας."""
from __future__ import annotations
from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    """Κοινά σήματα εφαρμογής."""
    activity = Signal(str)


events = EventBus()
