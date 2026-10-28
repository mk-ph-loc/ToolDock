"""Κανονικοποίηση ελληνικού/λατινικού κειμένου."""
from __future__ import annotations
import re
import unicodedata


def normalize(text: str) -> str:
    """Πεζά, αφαίρεση τόνων/διαλυτικών και περιττών κενών."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = unicodedata.normalize("NFC", text).lower()
    return re.sub(r"\s+", " ", text).strip()
