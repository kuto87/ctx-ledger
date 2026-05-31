"""Small Git subprocess helpers used by ctx-ledger commands."""

from __future__ import annotations

import subprocess
from pathlib import Path


IGNORED_STATUS_PREFIXES = (".ctx-ledger/", ".ctx-ledger\\")


class GitError(RuntimeError):
    """Raised when a Git command cannot be completed."""


def run_git(args: list[str], cwd: Path | str = ".") -> subprocess.CompletedProcess[str]:
    """Run a Git command and capture text output."""

    try:
        return subprocess.run(
            ["git", *args],
            cwd=Path(cwd),
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitError("Git was not found. Please install Git and try again.") from exc


def ensure_git_repo(cwd: Path | str = ".") -> None:
    """Raise a friendly error if cwd is not inside a Git repository."""

    result = run_git(["rev-parse", "--is-inside-work-tree"], cwd)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise GitError("This command must be run inside a Git repository.")


def current_branch(cwd: Path | str = ".") -> str:
    """Return the current branch or HEAD state."""

    result = run_git(["branch", "--show-current"], cwd)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    fallback = run_git(["rev-parse", "--short", "HEAD"], cwd)
    return fallback.stdout.strip() if fallback.returncode == 0 else "(no commits)"


def latest_commit(cwd: Path | str = ".") -> dict[str, str]:
    """Return latest commit information, handling empty repositories."""

    result = run_git(["log", "-1", "--format=%H%x00%s"], cwd)
    if result.returncode != 0:
        return {"hash": "", "short_hash": "", "subject": "No commits yet"}
    raw = result.stdout.rstrip("\n")
    commit_hash, _, subject = raw.partition("\x00")
    return {
        "hash": commit_hash,
        "short_hash": commit_hash[:12],
        "subject": subject or "(no subject)",
    }


def changed_files(cwd: Path | str = ".") -> list[str]:
    """Return changed file paths from porcelain status."""

    result = run_git(["status", "--short"], cwd)
    if result.returncode != 0:
        return []
    files: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not is_ignored_status_path(path):
            files.append(path)
    return files


def is_ignored_status_path(path: str) -> bool:
    """Return whether a Git status path should be hidden from context packs."""

    normalized = path.strip().strip('"')
    return normalized.startswith(IGNORED_STATUS_PREFIXES)


def diff_stat(cwd: Path | str = ".") -> str:
    """Return a compact diff stat for tracked and staged changes."""

    unstaged = run_git(["diff", "--stat"], cwd)
    staged = run_git(["diff", "--cached", "--stat"], cwd)
    parts = []
    if staged.returncode == 0 and staged.stdout.strip():
        parts.append("Staged changes:\n" + staged.stdout.strip())
    if unstaged.returncode == 0 and unstaged.stdout.strip():
        parts.append("Unstaged changes:\n" + unstaged.stdout.strip())
    return "\n\n".join(parts) if parts else "No tracked diff."


def is_dirty(cwd: Path | str = ".") -> bool:
    """Return whether the Git working tree has changes."""

    result = run_git(["status", "--porcelain"], cwd)
    return bool(result.stdout.strip()) if result.returncode == 0 else False
