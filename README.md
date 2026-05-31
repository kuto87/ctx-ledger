# ctx-ledger

[![tests](https://github.com/kuto87/ctx-ledger/actions/workflows/tests.yml/badge.svg)](https://github.com/kuto87/ctx-ledger/actions/workflows/tests.yml)

**Stop repeating project context.**

Generate clean, copy-ready context packs for ChatGPT, Codex, Claude Code, Cursor, and other AI coding agents.

Git manages your code changes.  
ctx-ledger manages what your AI agent needs to know.

日本語の説明は [README.ja.md](README.ja.md) を参照してください。

## Why

AI coding agents are useful, but project context often gets lost when you start a new chat, switch tools, return days later, or move to another machine. `ctx-ledger` keeps a small local ledger of notes, Git state, generated handoff packs, and sent history so the next AI chat starts with useful context.

## Install

Install from GitHub:

```powershell
python -m pip install "ctx-ledger @ git+https://github.com/kuto87/ctx-ledger.git"
```

For local development:

```powershell
git clone https://github.com/kuto87/ctx-ledger.git
cd ctx-ledger
python -m pip install -e ".[dev]"
pytest
```

PyPI packaging is ready, but the project is not published on PyPI yet.

## Quickstart

Run this once inside a Git project:

```powershell
ctx init
ctx config --lang ja --target chatgpt
```

Most days, use one command:

```powershell
ctx handoff "Describe what changed or what you want the next AI chat to do"
```

This saves a note, snapshots Git, builds Markdown handoff packs, and copies `NEXT_PROMPT.md` to the clipboard.

If you forget the commands, run:

```powershell
ctx
```

## Common Commands

```powershell
ctx handoff "message"       # note + snapshot + prompt
ctx note "message"          # save a project note
ctx ask                     # build handoff packs
ctx status                  # show project status
ctx doctor                  # check environment readiness
ctx config --lang ja        # set Japanese output as the default
```

Supported output languages are `en` and `ja`. This changes generated handoff text and CLI labels; it does not affect the programming language of your project.

`budget` is only a rough context size hint for generated prompts, such as `4000`. It does not call an AI API and does not spend money.

## Demo

See [docs/demo.md](docs/demo.md) for a short before/after workflow using a sample TODO app.

## Code Map

- `src/ctx_ledger/cli.py`: CLI command definitions and wiring.
- `src/ctx_ledger/paths.py`: `.ctx-ledger` paths, initialization, and config.
- `src/ctx_ledger/git_utils.py`: Git subprocess helpers.
- `src/ctx_ledger/notes.py`: Note creation and loading.
- `src/ctx_ledger/snapshot.py`: Git snapshot creation and loading.
- `src/ctx_ledger/builder.py`: Markdown handoff pack generation.
- `src/ctx_ledger/clipboard.py`: Clipboard helpers.
- `src/ctx_ledger/redaction.py`: Secret and personal-info redaction.
- `src/ctx_ledger/ledger.py`: Sent handoff history.
- `src/ctx_ledger/status.py`: Status summary collection.
- `src/ctx_ledger/doctor.py`: Environment readiness checks.

## Project Status

`ctx-ledger` is an early-stage local-first CLI. It does not integrate with OpenAI, Anthropic, Claude, Cursor, or cloud APIs. It only generates local Markdown files and optionally copies text to your clipboard.

## License

MIT
