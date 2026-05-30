# ctx-ledger

**Stop repeating project context.**

Generate clean, copy-ready context packs for ChatGPT, Codex, Claude Code, Cursor, and other AI coding agents.

Git manages your code changes.  
ctx-ledger manages what your AI agent needs to know.

## Overview

`ctx-ledger` is a local-first CLI tool for developers who use AI coding agents across multiple chats or tools. It records project notes, captures Git state, generates Markdown context packs, copies the next prompt to the clipboard, and records when handoffs are sent.

No AI API key is required. The tool works with local files and Git.

## Why it exists

AI coding agents work better when they have clear project context. Repeating that context by hand is slow and error-prone. `ctx-ledger` keeps the important handoff details in a small project-local ledger so each new chat can start with cleaner context.

## Quickstart

```powershell
python -m pip install -e ".[dev]"
ctx init
ctx note "Implement the first CLI workflow."
ctx snap
ctx ask --target chatgpt
```

`ctx ask` writes Markdown files to `.ctx-ledger/generated/` and copies `NEXT_PROMPT.md` to the clipboard by default.

## Commands

```powershell
ctx init
ctx note "message"
ctx snap
ctx ask
ctx ask --target codex --budget 4000 --fresh
ctx ask --no-copy
ctx sent --target chatgpt
ctx status
```

## Example output

```text
Built .ctx-ledger/generated/NEXT_PROMPT.md
Built .ctx-ledger/generated/DELTA_PACK.md
Built .ctx-ledger/generated/RECOVERY_PACK.md
Copied prompt to clipboard
Paste it into ChatGPT / Codex / Claude Code / Cursor.
```

## v0.1.0 scope

Included:

- Local-first CLI
- Git repository awareness
- Note saving
- Git snapshot collection
- Markdown prompt generation
- Clipboard copy by default
- Sent handoff history
- Basic status command
- Basic secret redaction

Not included:

- AI API integrations
- VS Code extension
- GUI
- Cloud sync
- RAG or vector search
- Automatic source-code modification
- Advanced large-repository optimization

## Code map

- `src/ctx_ledger/cli.py`: CLI command definitions and wiring only.
- `src/ctx_ledger/paths.py`: `.ctx-ledger` path management and initialization.
- `src/ctx_ledger/git_utils.py`: Git subprocess helpers.
- `src/ctx_ledger/notes.py`: Note creation and loading.
- `src/ctx_ledger/snapshot.py`: Git snapshot creation and loading.
- `src/ctx_ledger/builder.py`: Markdown pack generation.
- `src/ctx_ledger/clipboard.py`: Clipboard copy helper.
- `src/ctx_ledger/redaction.py`: Secret and personal-info redaction.
- `src/ctx_ledger/ledger.py`: Sent handoff history.
- `src/ctx_ledger/status.py`: Status summary collection.

## Local-first by default

`ctx-ledger` does not call OpenAI, Anthropic, or any other AI service. It does not require an API key. Generated context packs are local Markdown files.

## Roadmap

- Configurable prompt templates
- More target-specific prompt styles
- Better large-repository summaries
- Optional note categories
- Optional release packaging

Suggested GitHub topics: `ai`, `cli`, `developer-tools`, `git`, `context`, `python`.
