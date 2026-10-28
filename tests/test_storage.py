"""Tests για μορφή και αποθήκευση εγγραφών."""
from datetime import datetime
from pathlib import Path
from tooldock.core.storage import append_note, ensure_data_files, format_entry


def test_format_entry_with_topic():
    now = datetime(2026, 10, 28, 13, 41)
    entry = format_entry("δοκιμή", "PROMPT", now)
    assert "2026-10-28 13:41 · PROMPT" in entry
    assert "δοκιμή" in entry
    assert "[ΘΕΜΑ: PROMPT · 2026-10-28 13:41]" in entry


def test_format_entry_without_topic():
    entry = format_entry("σημείωση", None, datetime(2026, 10, 28, 13, 41))
    assert "· PROMPT" not in entry
    assert "[ΣΗΜΕΙΩΣΗ · 2026-10-28 13:41]" in entry


def test_append_note_creates_files(tmp_path: Path):
    base = tmp_path / "data" / "Base.txt"
    ensure_data_files(base, ["ΣΧΟΛΕΙΟ"])
    append_note(base, "σύνολο", "ΣΧΟΛΕΙΟ")
    assert "σύνολο" in base.read_text(encoding="utf-8")
    topic = tmp_path / "data" / "notes" / "ΣΧΟΛΕΙΟ.txt"
    assert "σύνολο" in topic.read_text(encoding="utf-8")
