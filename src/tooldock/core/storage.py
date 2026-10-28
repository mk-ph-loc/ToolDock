"""Αποθήκευση σημειώσεων σε Base.txt και αρχεία θεμάτων."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path

SEP = "─" * 8


def ensure_data_files(base_file: Path, topics: list[str]) -> None:
    """Δημιουργία Base.txt και αρχείων θεμάτων στην πρώτη εκτέλεση."""
    base_file.parent.mkdir(parents=True, exist_ok=True)
    base_file.touch(exist_ok=True)
    notes_dir = base_file.parent / "notes"
    notes_dir.mkdir(exist_ok=True)
    for topic in topics:
        (notes_dir / f"{topic}.txt").touch(exist_ok=True)


def format_entry(text: str, topic: str | None, now: datetime | None = None) -> str:
    """Μορφή εγγραφής κατά §5: κεφαλίδα, κείμενο, γραμμή-υπογραφή."""
    now = now or datetime.now()
    stamp = now.strftime("%Y-%m-%d %H:%M")
    if topic:
        header = f"{SEP} {stamp} · {topic} {SEP}"
    else:
        header = f"{SEP} {stamp} {SEP}"
    signature = f"[ΘΕΜΑ: {topic} · {stamp}]" if topic else f"[ΣΗΜΕΙΩΣΗ · {stamp}]"
    return f"{header}\n{text.strip()}\n{signature}\n"


def append_note(base_file: Path, text: str, topic: str | None = None) -> Path:
    """Προσθήκη σημείωσης στο Base.txt και, αν υπάρχει θέμα, στο αρχείο θέματος."""
    ensure_data_files(base_file, [])
    entry = format_entry(text, topic)
    with base_file.open("a", encoding="utf-8") as file:
        file.write(entry)
    if topic:
        topic_file = base_file.parent / "notes" / f"{topic}.txt"
        topic_file.parent.mkdir(parents=True, exist_ok=True)
        # Στο αρχείο θέματος η κεφαλίδα δεν επαναλαμβάνει το θέμα.
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with topic_file.open("a", encoding="utf-8") as file:
            file.write(f"{SEP} {stamp} {SEP}\n{text.strip()}\n[ΘΕΜΑ: {topic} · {stamp}]\n")
    return base_file
