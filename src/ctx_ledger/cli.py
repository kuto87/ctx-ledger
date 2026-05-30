"""Typer command wiring for the ctx-ledger CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import git_utils
from .builder import build_context_packs
from .clipboard import copy_text
from .ledger import record_sent
from .notes import create_note
from .paths import ensure_initialized
from .snapshot import create_snapshot
from .status import collect_status


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
    target: str = typer.Option("chatgpt", help="Target AI tool: chatgpt, codex, claude, cursor."),
    budget: Optional[int] = typer.Option(None, help="Optional context budget hint."),
    fresh: bool = typer.Option(False, help="Mark this as a fresh/recovery handoff."),
    no_copy: bool = typer.Option(False, help="Do not copy NEXT_PROMPT.md to the clipboard."),
) -> None:
    """Build Markdown context packs for the next AI-agent handoff."""

    try:
        outputs = build_context_packs(Path.cwd(), target=target, budget=budget, fresh=fresh)
    except (git_utils.GitError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    next_prompt = outputs["next_prompt"]
    console.print(f"[green]Built[/green] {next_prompt.relative_to(Path.cwd())}")
    console.print(f"[green]Built[/green] {outputs['delta_pack'].relative_to(Path.cwd())}")
    console.print(f"[green]Built[/green] {outputs['recovery_pack'].relative_to(Path.cwd())}")
    if no_copy:
        console.print("[yellow]Skipped clipboard copy[/yellow]")
        return
    copied, error = copy_text(next_prompt.read_text(encoding="utf-8"))
    if copied:
        console.print("[green]Copied prompt to clipboard[/green]")
        console.print("Paste it into ChatGPT / Codex / Claude Code / Cursor.")
    else:
        console.print(f"[yellow]Clipboard copy failed[/yellow] {error}")
        console.print(f"Prompt is still available at {next_prompt.relative_to(Path.cwd())}")


@app.command()
def sent(target: str = typer.Option(..., help="Target AI tool that received the prompt.")) -> None:
    """Record that the latest generated prompt was sent."""

    try:
        record_path = record_sent(target, Path.cwd())
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    console.print(f"[green]Recorded sent handoff[/green] {record_path.relative_to(Path.cwd())}")


@app.command()
def status() -> None:
    """Show ctx-ledger and Git status."""

    data = collect_status(Path.cwd())
    table = Table(title="ctx-ledger status")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Initialized", "yes" if data["initialized"] else "no")
    table.add_row("Git branch", str(data["branch"]))
    table.add_row("Notes", str(data["note_count"]))
    table.add_row("Latest prompt", data["latest_prompt"] or "(none)")
    table.add_row("Last sent target", data["last_sent_target"] or "(none)")
    table.add_row("Dirty", str(data["dirty"]))
    console.print(table)


if __name__ == "__main__":
    app()
