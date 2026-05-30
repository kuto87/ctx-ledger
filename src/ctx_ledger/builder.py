"""Markdown context pack generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .notes import load_recent_notes
from .paths import ensure_initialized
from .redaction import redact_text
from .snapshot import ensure_snapshot


VALID_TARGETS = {"chatgpt", "codex", "claude", "cursor"}


def validate_target(target: str) -> str:
    """Validate and normalize a target AI agent name."""

    normalized = target.lower().strip()
    if normalized not in VALID_TARGETS:
        choices = ", ".join(sorted(VALID_TARGETS))
        raise ValueError(f"Unsupported target '{target}'. Choose one of: {choices}.")
    return normalized


def build_context_packs(
    root: Path | str = ".",
    target: str = "chatgpt",
    budget: int | None = None,
    fresh: bool = False,
) -> dict[str, Path]:
    """Build all Markdown context packs and return their paths."""

    normalized_target = validate_target(target)
    paths = ensure_initialized(root)
    snapshot = ensure_snapshot(root)
    notes = load_recent_notes(root)
    next_prompt = render_next_prompt(snapshot, notes, normalized_target, budget, fresh)
    delta_pack = render_delta_pack(snapshot, notes, normalized_target, budget)
    recovery_pack = render_recovery_pack(snapshot, notes, normalized_target, budget)
    outputs = {
        paths.next_prompt: next_prompt,
        paths.delta_pack: delta_pack,
        paths.recovery_pack: recovery_pack,
    }
    for path, content in outputs.items():
        path.write_text(redact_text(content), encoding="utf-8")
    return {
        "next_prompt": paths.next_prompt,
        "delta_pack": paths.delta_pack,
        "recovery_pack": paths.recovery_pack,
    }


def render_next_prompt(
    snapshot: dict[str, Any],
    notes: list[str],
    target: str = "chatgpt",
    budget: int | None = None,
    fresh: bool = False,
) -> str:
    """Render NEXT_PROMPT.md."""

    latest = snapshot.get("latest_commit", {})
    fresh_line = "This is a fresh/recovery handoff." if fresh else "Continue from the current context."
    return "\n".join(
        [
            "# Next Prompt",
            "",
            "## Goal",
            "",
            "Help with the current development task.",
            "",
            "## Handoff settings",
            "",
            f"- Target: {target}",
            f"- Budget hint: {budget if budget else 'not specified'}",
            f"- Mode: {fresh_line}",
            "",
            "## Current notes",
            "",
            format_notes(notes),
            "",
            "## Git state",
            "",
            f"- Branch: {snapshot.get('branch', '(unknown)')}",
            f"- Latest commit: {format_commit(latest)}",
            f"- Working tree: {'dirty' if snapshot.get('dirty') else 'clean'}",
            "",
            "## Changed files",
            "",
            format_changed_files(snapshot.get("changed_files", [])),
            "",
            "## Diff summary",
            "",
            "```text",
            str(snapshot.get("diff_stat") or "No diff summary."),
            "```",
            "",
            "## Please help",
            "",
            "Review the current context and suggest the next safe step.",
            "",
        ]
    )


def render_delta_pack(
    snapshot: dict[str, Any],
    notes: list[str],
    target: str = "chatgpt",
    budget: int | None = None,
) -> str:
    """Render DELTA_PACK.md."""

    return "\n".join(
        [
            "# Delta Pack",
            "",
            f"Target: {target}",
            f"Budget hint: {budget if budget else 'not specified'}",
            "",
            "## Recent notes",
            "",
            format_notes(notes),
            "",
            "## Changed files",
            "",
            format_changed_files(snapshot.get("changed_files", [])),
            "",
            "## Diff summary",
            "",
            "```text",
            str(snapshot.get("diff_stat") or "No diff summary."),
            "```",
            "",
        ]
    )


def render_recovery_pack(
    snapshot: dict[str, Any],
    notes: list[str],
    target: str = "chatgpt",
    budget: int | None = None,
) -> str:
    """Render RECOVERY_PACK.md."""

    latest = snapshot.get("latest_commit", {})
    return "\n".join(
        [
            "# Recovery Pack",
            "",
            "Use this compact context to restart in a fresh AI coding-agent chat.",
            "",
            "## Project state",
            "",
            f"- Target: {target}",
            f"- Budget hint: {budget if budget else 'not specified'}",
            f"- Branch: {snapshot.get('branch', '(unknown)')}",
            f"- Latest commit: {format_commit(latest)}",
            f"- Working tree: {'dirty' if snapshot.get('dirty') else 'clean'}",
            "",
            "## Recent notes",
            "",
            format_notes(notes),
            "",
            "## Changed files",
            "",
            format_changed_files(snapshot.get("changed_files", [])),
            "",
        ]
    )


def format_notes(notes: list[str]) -> str:
    """Format notes for Markdown output."""

    if not notes:
        return "- No notes recorded yet."
    return "\n".join(f"- {first_content_line(note)}" for note in notes)


def first_content_line(note: str) -> str:
    """Return the first useful note line."""

    for line in note.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return "(empty note)"


def format_changed_files(files: list[str]) -> str:
    """Format changed files for Markdown output."""

    if not files:
        return "- No changed files."
    return "\n".join(f"- {file}" for file in files)


def format_commit(commit: dict[str, str]) -> str:
    """Format a latest commit dictionary."""

    short_hash = commit.get("short_hash") or "none"
    subject = commit.get("subject") or "No commits yet"
    return f"{short_hash} {subject}".strip()
