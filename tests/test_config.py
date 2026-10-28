"""Tests για Config."""
from pathlib import Path
from tooldock.core.config import Config, DEFAULTS, deep_merge


def test_defaults(tmp_path: Path):
    config = Config(tmp_path / "config.json")
    assert config.get("window.dock") == "right"
    assert config.get("notes.topics")[0] == "ΣΧΟΛΕΙΟ"


def test_save_and_reload(tmp_path: Path):
    path = tmp_path / "config.json"
    config = Config(path)
    config.set("window.dock", "left")
    config.save()
    assert Config(path).get("window.dock") == "left"


def test_deep_merge_keeps_defaults():
    merged = deep_merge(DEFAULTS, {"window": {"dock": "top"}})
    assert merged["window"]["dock"] == "top"
    assert merged["window"]["always_on_top"] is True
