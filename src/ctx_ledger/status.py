"""Status summary collection for the ctx status command."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import git_utils
from .ledger import latest_sent
from .notes import note_count
from .paths import is_initialized, project_paths


def collect_status(root: Path | str = ".") -> dict[str, Any]:
    """Collect a user-facing project status summary."""

    paths = project_paths(root)
    initialized = is_initialized(root)
    branch = "(not a Git repository)"
    dirty: bool | str = "unknown"
    try:
        git_utils.ensure_git_repo(root)
        branch = git_utils.current_branch(root)
        dirty = git_utils.is_dirty(root)
    except git_utils.GitError:
        pass
    sent = latest_sent(root)
    return {
        "initialized": initialized,
        "branch": branch,
        "note_count": note_count(root),
        "latest_prompt": str(paths.next_prompt.relative_to(paths.root)) if paths.next_prompt.exists() else "",
        "last_sent_target": sent.get("target") if sent else "",
        "dirty": dirty,
    }
