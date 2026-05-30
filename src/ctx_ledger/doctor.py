"""Environment checks for installing and using ctx-ledger."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

from . import git_utils
from .clipboard import check_clipboard
from .paths import is_initialized, load_config


def collect_doctor(root: Path | str = ".") -> list[dict[str, Any]]:
    """Collect environment checks for ctx doctor."""

    checks: list[dict[str, Any]] = []
    checks.append(
        {
            "name": "Python",
            "ok": sys.version_info >= (3, 8),
            "detail": sys.version.split()[0],
            "fix": "Install Python 3.8 or newer.",
        }
    )

    git_path = shutil.which("git")
    if git_path:
        version = git_utils.run_git(["--version"], root)
        checks.append(
            {
                "name": "Git",
                "ok": version.returncode == 0,
                "detail": version.stdout.strip() or git_path,
                "fix": "Install Git and make sure it is on PATH.",
            }
        )
    else:
        checks.append(
            {
                "name": "Git",
                "ok": False,
                "detail": "not found",
                "fix": "Install Git and make sure it is on PATH.",
            }
        )

    try:
        git_utils.ensure_git_repo(root)
        repo_ok = True
        repo_detail = "inside a Git repository"
    except git_utils.GitError as exc:
        repo_ok = False
        repo_detail = str(exc)
    checks.append(
        {
            "name": "Git repository",
            "ok": repo_ok,
            "detail": repo_detail,
            "fix": "Run this command inside a Git repository.",
        }
    )

    checks.append(
        {
            "name": "ctx-ledger initialized",
            "ok": is_initialized(root),
            "detail": ".ctx-ledger found" if is_initialized(root) else ".ctx-ledger not found",
            "fix": "Run ctx init.",
        }
    )

    clipboard_ok, clipboard_error = check_clipboard()
    checks.append(
        {
            "name": "Clipboard",
            "ok": clipboard_ok,
            "detail": "available" if clipboard_ok else clipboard_error or "not available",
            "fix": "Use ctx ask --no-copy or configure clipboard support for this OS.",
        }
    )

    config = load_config(root)
    checks.append(
        {
            "name": "Defaults",
            "ok": True,
            "detail": (
                f"target={config.get('default_target')}, "
                f"language={config.get('default_language')}, "
                f"budget={config.get('default_budget') or 'not set'}"
            ),
            "fix": "Run ctx config to update defaults.",
        }
    )
    return checks
