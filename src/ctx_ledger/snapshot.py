"""Git snapshot creation and loading."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import git_utils
from .paths import ensure_initialized, project_paths


def create_snapshot(root: Path | str = ".") -> dict[str, Any]:
    """Collect current Git state and write the latest snapshot cache."""

    git_utils.ensure_git_repo(root)
    paths = ensure_initialized(root)
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "branch": git_utils.current_branch(root),
        "latest_commit": git_utils.latest_commit(root),
        "changed_files": git_utils.changed_files(root),
        "diff_stat": git_utils.diff_stat(root),
        "dirty": git_utils.is_dirty(root),
    }
    paths.snapshot.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot


def load_snapshot(root: Path | str = ".") -> dict[str, Any] | None:
    """Load the latest cached Git snapshot."""

    paths = project_paths(root)
    if not paths.snapshot.exists():
        return None
    try:
        return json.loads(paths.snapshot.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def ensure_snapshot(root: Path | str = ".") -> dict[str, Any]:
    """Return the latest snapshot, creating one if needed."""

    return load_snapshot(root) or create_snapshot(root)
