"""Note creation and loading for ctx-ledger."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .paths import ensure_initialized, project_paths


def timestamp() -> str:
    """Return a UTC timestamp safe for filenames."""

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_note(message: str, root: Path | str = ".") -> Path:
    """Save a human-readable timestamped note."""

    paths = ensure_initialized(root)
    filename = f"{timestamp()}.md"
    note_path = paths.notes / filename
    note_id = filename[:-3]
    note_path.write_text(
        f"# Note {note_id}\n\n{message.strip()}\n",
        encoding="utf-8",
    )
    return note_path


def load_recent_notes(root: Path | str = ".", limit: int = 10) -> list[str]:
    """Load recent notes as plain Markdown strings."""

    paths = project_paths(root)
    if not paths.notes.exists():
        return []
    note_paths = sorted(paths.notes.glob("*.md"), reverse=True)[:limit]
    notes: list[str] = []
    for note_path in note_paths:
        try:
            notes.append(note_path.read_text(encoding="utf-8").strip())
        except OSError:
            continue
    return notes


def note_count(root: Path | str = ".") -> int:
    """Count saved notes."""

    paths = project_paths(root)
    return len(list(paths.notes.glob("*.md"))) if paths.notes.exists() else 0
