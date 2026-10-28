"""Πλήρες zip με επιλεγμένο κώδικα/docs, χωρίς προσωπικά δεδομένα."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    out = ROOT / "dist" / f"tooldock-v{version}.zip"
    out.parent.mkdir(exist_ok=True)
    candidates = []
    for directory in ("src", "tests", "scripts", "docs"):
        candidates.extend((ROOT / directory).rglob("*"))
    for pattern in ("*.md", "VERSION", "requirements*.txt", "pyproject.toml",
                    "config.example.json", "run.bat", ".gitignore", ".gitattributes"):
        candidates.extend(ROOT.glob(pattern))
    with ZipFile(out, "w", ZIP_DEFLATED) as archive:
        for file in sorted(set(candidates)):
            if not file.is_file(): continue
            relative = file.relative_to(ROOT)
            if any(p in {"__pycache__", ".pytest_cache", ".git", ".venv", "data", "backups"}
                   or p.endswith(".egg-info") for p in relative.parts): continue
            if file.suffix in {".pyc", ".pyo", ".log"} or file.name in {"config.json", ".env"}: continue
            archive.write(file, str(Path("ToolDock") / relative))
    print(f"Δημιουργήθηκε: {out}")

if __name__ == "__main__": main()
