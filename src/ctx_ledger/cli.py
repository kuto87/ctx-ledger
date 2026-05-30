"""Typer command wiring for the ctx-ledger CLI."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import git_utils
from .builder import build_context_packs, validate_language, validate_target
from .clipboard import copy_text
from .doctor import collect_doctor
from .ledger import record_sent
from .notes import create_note
from .paths import ensure_initialized, load_config, save_config
from .snapshot import create_snapshot
from .status import collect_status


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

app = typer.Typer(
    help="Generate clean context packs for AI coding agents.",
    pretty_exceptions_show_locals=False,
)
console = Console()


@app.command()
def init() -> None:
    """Initialize ctx-ledger in the current project."""

    paths = ensure_initialized(Path.cwd())
    console.print(f"[green]Initialized[/green] {paths.ledger.relative_to(paths.root)}")


@app.command()
def note(message: str) -> None:
    """Save a timestamped project note."""

    note_path = create_note(message, Path.cwd())
    console.print(f"[green]Saved note[/green] {note_path.relative_to(Path.cwd())}")


@app.command()
def snap() -> None:
    """Capture the current Git state."""

    try:
        snapshot = create_snapshot(Path.cwd())
    except git_utils.GitError as exc:
        raise typer.BadParameter(str(exc)) from exc
    console.print(
        f"[green]Captured snapshot[/green] branch={snapshot['branch']} "
        f"dirty={'yes' if snapshot['dirty'] else 'no'}"
    )


@app.command()
def ask(
    target: Optional[str] = typer.Option(None, help="Target AI tool: chatgpt, codex, claude, cursor."),
    budget: Optional[int] = typer.Option(None, help="Optional context budget hint."),
    fresh: bool = typer.Option(False, help="Mark this as a fresh/recovery handoff."),
    no_copy: bool = typer.Option(False, help="Do not copy NEXT_PROMPT.md to the clipboard."),
    lang: Optional[str] = typer.Option(None, help="Output language: en or ja."),
) -> None:
    """Build Markdown context packs for the next AI-agent handoff."""

    try:
        config = load_config(Path.cwd())
        chosen_target = validate_target(str(target or config.get("default_target") or "chatgpt"))
        language = validate_language(str(lang or config.get("default_language") or "en"))
        chosen_budget = budget if budget is not None else normalize_budget(config.get("default_budget"))
        outputs = build_context_packs(
            Path.cwd(),
            target=chosen_target,
            budget=chosen_budget,
            fresh=fresh,
            language=language,
        )
    except (git_utils.GitError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    next_prompt = outputs["next_prompt"]
    console.print(f"[green]Built[/green] {next_prompt.relative_to(Path.cwd())}")
    console.print(f"[green]Built[/green] {outputs['delta_pack'].relative_to(Path.cwd())}")
    console.print(f"[green]Built[/green] {outputs['recovery_pack'].relative_to(Path.cwd())}")
    if no_copy:
        console.print(
            "[yellow]Clipboard copy skipped[/yellow]"
            if language == "en"
            else "[yellow]クリップボードへのコピーをスキップしました[/yellow]"
        )
        return
    copied, error = copy_text(next_prompt.read_text(encoding="utf-8"))
    if copied:
        console.print(
            "[green]Copied prompt to clipboard[/green]"
            if language == "en"
            else "[green]プロンプトをクリップボードにコピーしました[/green]"
        )
        console.print(
            "Paste it into ChatGPT / Codex / Claude Code / Cursor."
            if language == "en"
            else "ChatGPT / Codex / Claude Code / Cursor に貼り付けてください。"
        )
    else:
        console.print(
            f"[yellow]Clipboard copy failed[/yellow] {error}"
            if language == "en"
            else f"[yellow]クリップボードへのコピーに失敗しました[/yellow] {error}"
        )
        console.print(
            f"Prompt is still available at {next_prompt.relative_to(Path.cwd())}"
            if language == "en"
            else f"プロンプトは {next_prompt.relative_to(Path.cwd())} に保存されています"
        )


@app.command()
def sent(target: str = typer.Option(..., help="Target AI tool that received the prompt.")) -> None:
    """Record that the latest generated prompt was sent."""

    try:
        record_path = record_sent(target, Path.cwd())
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    console.print(f"[green]Recorded sent handoff[/green] {record_path.relative_to(Path.cwd())}")


@app.command()
def status(lang: Optional[str] = typer.Option(None, help="Output language: en or ja.")) -> None:
    """Show ctx-ledger and Git status."""

    try:
        config = load_config(Path.cwd())
        language = validate_language(str(lang or config.get("default_language") or "en"))
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    data = collect_status(Path.cwd())
    if language == "ja":
        table = Table(title="ctx-ledger 状態")
        table.add_column("項目")
        table.add_column("値")
        table.add_row("初期化済み", "はい" if data["initialized"] else "いいえ")
        table.add_row("Git ブランチ", str(data["branch"]))
        table.add_row("メモ数", str(data["note_count"]))
        table.add_row("最新プロンプト", data["latest_prompt"] or "(なし)")
        table.add_row("最後の送信先", data["last_sent_target"] or "(なし)")
        table.add_row("未コミット変更", format_dirty(data["dirty"], language))
    else:
        table = Table(title="ctx-ledger status")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("Initialized", "yes" if data["initialized"] else "no")
        table.add_row("Git branch", str(data["branch"]))
        table.add_row("Notes", str(data["note_count"]))
        table.add_row("Latest prompt", data["latest_prompt"] or "(none)")
        table.add_row("Last sent target", data["last_sent_target"] or "(none)")
        table.add_row("Dirty", format_dirty(data["dirty"], language))
    console.print(table)


@app.command("config")
def configure(
    target: Optional[str] = typer.Option(None, help="Default target: chatgpt, codex, claude, cursor."),
    lang: Optional[str] = typer.Option(None, help="Default output language: en or ja."),
    budget: Optional[int] = typer.Option(None, help="Default context budget hint."),
    clear_budget: bool = typer.Option(False, help="Clear the default budget hint."),
) -> None:
    """Show or update ctx-ledger defaults."""

    paths = ensure_initialized(Path.cwd())
    config = load_config(Path.cwd())
    changed = False
    try:
        if target is not None:
            config["default_target"] = validate_target(target)
            changed = True
        if lang is not None:
            config["default_language"] = validate_language(lang)
            changed = True
        if budget is not None:
            config["default_budget"] = budget
            changed = True
        if clear_budget:
            config["default_budget"] = None
            changed = True
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if changed:
        save_config(config, Path.cwd())
        console.print(f"[green]Updated config[/green] {paths.config.relative_to(paths.root)}")
    else:
        console.print(f"[green]Config[/green] {paths.config.relative_to(paths.root)}")
    print_config_table(config)


@app.command()
def doctor(lang: str = typer.Option("en", help="Output language: en or ja.")) -> None:
    """Check local requirements and project readiness."""

    try:
        language = validate_language(lang)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    checks = collect_doctor(Path.cwd())
    table = Table(title="ctx-ledger doctor" if language == "en" else "ctx-ledger 診断")
    table.add_column("Check" if language == "en" else "確認")
    table.add_column("Status" if language == "en" else "状態")
    table.add_column("Detail" if language == "en" else "詳細")
    table.add_column("Fix" if language == "en" else "対応")
    for check in checks:
        ok = bool(check["ok"])
        status_text = "[green]OK[/green]" if ok else "[red]Needs action[/red]"
        if language == "ja":
            status_text = "[green]OK[/green]" if ok else "[red]対応が必要[/red]"
        table.add_row(
            str(check["name"]),
            status_text,
            str(check["detail"]),
            "" if ok else str(check["fix"]),
        )
    console.print(table)


def format_dirty(value: object, language: str) -> str:
    """Format dirty state for status output."""

    if isinstance(value, bool):
        if language == "ja":
            return "あり" if value else "なし"
        return "yes" if value else "no"
    return str(value)


def normalize_budget(value: object) -> Optional[int]:
    """Convert config budget values into an optional integer."""

    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("default_budget must be a number or null.") from exc


def print_config_table(config: dict[str, object]) -> None:
    """Print current config defaults."""

    table = Table(title="ctx-ledger config")
    table.add_column("Setting")
    table.add_column("Value")
    table.add_row("default_target", str(config.get("default_target") or "chatgpt"))
    table.add_row("default_language", str(config.get("default_language") or "en"))
    table.add_row("default_budget", str(config.get("default_budget") or "(none)"))
    console.print(table)


if __name__ == "__main__":
    app()
