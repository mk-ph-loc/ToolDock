"""Διαχείριση config.json με default τιμές."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parents[3]
CONFIG_PATH = APP_DIR / "config.json"

DEFAULTS: dict[str, Any] = {
    "window": {"mode": "compact", "dock": "right", "always_on_top": True,
               "width": 360, "height": 520},
    "notes": {"base_file": "data/Base.txt",
              "topics": ["ΣΧΟΛΕΙΟ", "PROMPT", "TO-DO", "ΛΟΓΑΡΙΑΣΜΟΣ",
                         "ΥΠΕΝΘΥΜΙΣΗ", "ΔΟΚΙΜΕΣ", "ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΣ", "SNIPPET"]},
    "quick_actions": {"downloads": True, "browser": True},
    "autostart": False,
}


def deep_merge(base: dict, extra: dict) -> dict:
    """Συγχώνευση defaults με αποθηκευμένες ρυθμίσεις."""
    out = dict(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


class Config:
    """Φόρτωση/αποθήκευση ρυθμίσεων σε JSON."""

    def __init__(self, path: Path = CONFIG_PATH) -> None:
        self.path = path
        self.data: dict = deep_merge(DEFAULTS, self._load())

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def save(self) -> None:
        """Αποθήκευση config.json."""
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self.data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def set(self, dotted: str, value: Any) -> None:
        parts = dotted.split(".")
        node = self.data
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
