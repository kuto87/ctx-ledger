"""Sent handoff history recording."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .builder import validate_target
from .paths import ensure_initialized, project_paths


def record_sent(target: str, root: Path | str = ".") -> Path:
    """Record that the latest generated prompt was sent to a target."""

    normalized_target = validate_target(target)
    paths = ensure_initialized(root)
    if not paths.next_prompt.exists():
        raise FileNotFoundError("No generated NEXT_PROMPT.md found. Run 'ctx ask' first.")
    content = paths.next_prompt.read_text(encoding="utf-8")
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record = {
        "target": normalized_target,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "generated_file": str(paths.next_prompt.relative_to(paths.root)),
        "content_hash": digest,
    }
    record_path = paths.sent / f"{stamp}-{normalized_target}.json"
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record_path


def latest_sent(root: Path | str = ".") -> dict[str, Any] | None:
    """Load the latest sent history record."""

    paths = project_paths(root)
    if not paths.sent.exists():
        return None
    records = sorted(paths.sent.glob("*.json"), reverse=True)
    if not records:
        return None
    try:
        return json.loads(records[0].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
