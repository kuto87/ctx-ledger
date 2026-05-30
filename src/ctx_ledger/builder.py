"""Markdown context pack generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .notes import load_recent_notes
from .paths import ensure_initialized
from .redaction import redact_text
from .snapshot import ensure_snapshot


VALID_TARGETS = {"chatgpt", "codex", "claude", "cursor"}
VALID_LANGUAGES = {"en", "ja"}


def validate_target(target: str) -> str:
    """Validate and normalize a target AI agent name."""

    normalized = target.lower().strip()
    if normalized not in VALID_TARGETS:
        choices = ", ".join(sorted(VALID_TARGETS))
        raise ValueError(f"Unsupported target '{target}'. Choose one of: {choices}.")
    return normalized


def validate_language(language: str) -> str:
    """Validate and normalize an output language code."""

    normalized = language.lower().strip()
    if normalized not in VALID_LANGUAGES:
        choices = ", ".join(sorted(VALID_LANGUAGES))
        raise ValueError(f"Unsupported language '{language}'. Choose one of: {choices}.")
    return normalized


def build_context_packs(
    root: Path | str = ".",
    target: str = "chatgpt",
    budget: int | None = None,
    fresh: bool = False,
    language: str = "en",
) -> dict[str, Path]:
    """Build all Markdown context packs and return their paths."""

    normalized_target = validate_target(target)
    normalized_language = validate_language(language)
    paths = ensure_initialized(root)
    snapshot = ensure_snapshot(root)
    notes = load_recent_notes(root)
    next_prompt = render_next_prompt(snapshot, notes, normalized_target, budget, fresh, normalized_language)
    delta_pack = render_delta_pack(snapshot, notes, normalized_target, budget, normalized_language)
    recovery_pack = render_recovery_pack(snapshot, notes, normalized_target, budget, normalized_language)
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
    language: str = "en",
) -> str:
    """Render NEXT_PROMPT.md."""

    if language == "ja":
        return render_next_prompt_ja(snapshot, notes, target, budget, fresh)
    return render_next_prompt_en(snapshot, notes, target, budget, fresh)


def render_next_prompt_en(
    snapshot: dict[str, Any],
    notes: list[str],
    target: str = "chatgpt",
    budget: int | None = None,
    fresh: bool = False,
) -> str:
    """Render NEXT_PROMPT.md in English."""

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
    language: str = "en",
) -> str:
    """Render DELTA_PACK.md."""

    if language == "ja":
        return render_delta_pack_ja(snapshot, notes, target, budget)
    return render_delta_pack_en(snapshot, notes, target, budget)


def render_delta_pack_en(
    snapshot: dict[str, Any],
    notes: list[str],
    target: str = "chatgpt",
    budget: int | None = None,
) -> str:
    """Render DELTA_PACK.md in English."""

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
    language: str = "en",
) -> str:
    """Render RECOVERY_PACK.md."""

    if language == "ja":
        return render_recovery_pack_ja(snapshot, notes, target, budget)
    return render_recovery_pack_en(snapshot, notes, target, budget)


def render_recovery_pack_en(
    snapshot: dict[str, Any],
    notes: list[str],
    target: str = "chatgpt",
    budget: int | None = None,
) -> str:
    """Render RECOVERY_PACK.md in English."""

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


def render_next_prompt_ja(
    snapshot: dict[str, Any],
    notes: list[str],
    target: str = "chatgpt",
    budget: int | None = None,
    fresh: bool = False,
) -> str:
    """Render NEXT_PROMPT.md in Japanese."""

    latest = snapshot.get("latest_commit", {})
    fresh_line = "新しいチャットへの引き継ぎです。" if fresh else "現在の文脈から続けてください。"
    return "\n".join(
        [
            "# 次のプロンプト",
            "",
            "## 目的",
            "",
            "現在の開発タスクを手伝ってください。",
            "",
            "## 引き継ぎ設定",
            "",
            f"- 対象: {target}",
            f"- 予算目安: {budget if budget else '指定なし'}",
            f"- モード: {fresh_line}",
            "",
            "## 現在のメモ",
            "",
            format_notes(notes, language="ja"),
            "",
            "## Git 状態",
            "",
            f"- ブランチ: {snapshot.get('branch', '(不明)')}",
            f"- 最新コミット: {format_commit(latest, language='ja')}",
            f"- 作業ツリー: {'変更あり' if snapshot.get('dirty') else 'クリーン'}",
            "",
            "## 変更ファイル",
            "",
            format_changed_files(snapshot.get("changed_files", []), language="ja"),
            "",
            "## 差分サマリー",
            "",
            "```text",
            str(snapshot.get("diff_stat") or "差分サマリーはありません。"),
            "```",
            "",
            "## お願い",
            "",
            "現在の文脈を確認し、次に安全に進める手順を提案してください。",
            "",
        ]
    )


def render_delta_pack_ja(
    snapshot: dict[str, Any],
    notes: list[str],
    target: str = "chatgpt",
    budget: int | None = None,
) -> str:
    """Render DELTA_PACK.md in Japanese."""

    return "\n".join(
        [
            "# 差分パック",
            "",
            f"対象: {target}",
            f"予算目安: {budget if budget else '指定なし'}",
            "",
            "## 最近のメモ",
            "",
            format_notes(notes, language="ja"),
            "",
            "## 変更ファイル",
            "",
            format_changed_files(snapshot.get("changed_files", []), language="ja"),
            "",
            "## 差分サマリー",
            "",
            "```text",
            str(snapshot.get("diff_stat") or "差分サマリーはありません。"),
            "```",
            "",
        ]
    )


def render_recovery_pack_ja(
    snapshot: dict[str, Any],
    notes: list[str],
    target: str = "chatgpt",
    budget: int | None = None,
) -> str:
    """Render RECOVERY_PACK.md in Japanese."""

    latest = snapshot.get("latest_commit", {})
    return "\n".join(
        [
            "# 復旧パック",
            "",
            "新しい AI コーディングエージェントのチャットで再開するための簡潔な文脈です。",
            "",
            "## プロジェクト状態",
            "",
            f"- 対象: {target}",
            f"- 予算目安: {budget if budget else '指定なし'}",
            f"- ブランチ: {snapshot.get('branch', '(不明)')}",
            f"- 最新コミット: {format_commit(latest, language='ja')}",
            f"- 作業ツリー: {'変更あり' if snapshot.get('dirty') else 'クリーン'}",
            "",
            "## 最近のメモ",
            "",
            format_notes(notes, language="ja"),
            "",
            "## 変更ファイル",
            "",
            format_changed_files(snapshot.get("changed_files", []), language="ja"),
            "",
        ]
    )


def format_notes(notes: list[str], language: str = "en") -> str:
    """Format notes for Markdown output."""

    if not notes:
        return "- メモはまだありません。" if language == "ja" else "- No notes recorded yet."
    return "\n".join(f"- {first_content_line(note)}" for note in notes)


def first_content_line(note: str) -> str:
    """Return the first useful note line."""

    for line in note.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return "(empty note)"


def format_changed_files(files: list[str], language: str = "en") -> str:
    """Format changed files for Markdown output."""

    if not files:
        return "- 変更ファイルはありません。" if language == "ja" else "- No changed files."
    return "\n".join(f"- {file}" for file in files)


def format_commit(commit: dict[str, str], language: str = "en") -> str:
    """Format a latest commit dictionary."""

    short_hash = commit.get("short_hash") or "none"
    subject = commit.get("subject") or ("コミットはまだありません" if language == "ja" else "No commits yet")
    return f"{short_hash} {subject}".strip()
