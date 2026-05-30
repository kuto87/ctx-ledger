"""Path helpers for the .ctx-ledger workspace directory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


LEDGER_DIR = ".ctx-ledger"


@dataclass(frozen=True)
class LedgerPaths:
    """Resolved paths used by ctx-ledger inside a project."""

    root: Path
    ledger: Path
    config: Path
    cards: Path
    notes: Path
    generated: Path
    sent: Path
    cache: Path
    snapshot: Path
    next_prompt: Path
    delta_pack: Path
    recovery_pack: Path


def project_paths(root: Path | str = ".") -> LedgerPaths:
    """Return all ctx-ledger paths for a project root."""

    root_path = Path(root).resolve()
    ledger = root_path / LEDGER_DIR
    generated = ledger / "generated"
    cache = ledger / "cache"
    return LedgerPaths(
        root=root_path,
        ledger=ledger,
        config=ledger / "config.yml",
        cards=ledger / "cards",
        notes=ledger / "notes",
        generated=generated,
        sent=ledger / "sent",
        cache=cache,
        snapshot=cache / "latest_snapshot.json",
        next_prompt=generated / "NEXT_PROMPT.md",
        delta_pack=generated / "DELTA_PACK.md",
        recovery_pack=generated / "RECOVERY_PACK.md",
    )


def managed_directories(paths: LedgerPaths) -> Iterable[Path]:
    """Return directories created by ctx init."""

    return (
        paths.ledger,
        paths.cards,
        paths.notes,
        paths.generated,
        paths.sent,
        paths.cache,
    )


def ensure_initialized(root: Path | str = ".") -> LedgerPaths:
    """Create the .ctx-ledger directory layout and default config."""

    paths = project_paths(root)
    for directory in managed_directories(paths):
        directory.mkdir(parents=True, exist_ok=True)
    if not paths.config.exists():
        paths.config.write_text(
            yaml.safe_dump(
                {"version": "0.1.0", "default_target": "chatgpt"},
                sort_keys=False,
            ),
            encoding="utf-8",
        )
    update_gitignore(paths.root)
    return paths


def is_initialized(root: Path | str = ".") -> bool:
    """Return whether a project has a ctx-ledger directory."""

    return project_paths(root).ledger.is_dir()


def update_gitignore(root: Path) -> None:
    """Add ctx-ledger ignore rules without removing user content."""

    ignore_path = root / ".gitignore"
    required = [
        ".ctx-ledger/generated/",
        ".ctx-ledger/cache/",
        ".ctx-ledger/sent/",
        "__pycache__/",
        ".pytest_cache/",
        ".venv/",
        "dist/",
        "build/",
        "*.egg-info/",
    ]
    existing = ignore_path.read_text(encoding="utf-8").splitlines() if ignore_path.exists() else []
    merged = existing[:]
    for line in required:
        if line not in merged:
            merged.append(line)
    ignore_path.write_text("\n".join(merged).rstrip() + "\n", encoding="utf-8")
