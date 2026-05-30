# AGENTS.md

## Project purpose

`ctx-ledger` helps developers stop repeating project context when using AI coding agents. It records notes, Git state, generated context packs, and sent handoff history in a local `.ctx-ledger` directory.

## v0.1.0 scope

Implement a small local-first Python CLI with these commands:

- `ctx init`
- `ctx note "message"`
- `ctx snap`
- `ctx ask`
- `ctx sent --target chatgpt`
- `ctx status`
- `ctx config`
- `ctx doctor`

Do not add AI API integrations, GUI features, cloud sync, RAG/vector search, or automatic source-code modification in v0.1.0.

## Code map

- `src/ctx_ledger/cli.py`: CLI command definitions and wiring only.
- `src/ctx_ledger/paths.py`: `.ctx-ledger` path management.
- `src/ctx_ledger/git_utils.py`: Git subprocess helpers.
- `src/ctx_ledger/notes.py`: Note creation and loading.
- `src/ctx_ledger/snapshot.py`: Git snapshot creation and loading.
- `src/ctx_ledger/builder.py`: Markdown pack generation.
- `src/ctx_ledger/clipboard.py`: Clipboard copy helper.
- `src/ctx_ledger/redaction.py`: Secret and personal-info redaction.
- `src/ctx_ledger/ledger.py`: Sent handoff history.
- `src/ctx_ledger/status.py`: Status display data.
- `src/ctx_ledger/doctor.py`: Environment readiness checks.

## Commands

```powershell
ctx init
ctx note "message"
ctx snap
ctx ask --target chatgpt --budget 4000
ctx ask --no-copy
ctx sent --target chatgpt
ctx status
ctx config --lang ja --target chatgpt --budget 4000
ctx doctor
```

## Test instructions

```powershell
python -m pip install -e ".[dev]"
pytest
```

Run smoke tests in a temporary Git repository, not in the `ctx-ledger` project root.

## Do-not rules

- Do not read `.env` contents.
- Do not scan huge binary files.
- Do not add AI API calls by default.
- Do not rewrite unrelated files.
- Do not collapse all logic into `cli.py`.

## AI editing guidance

When modifying this project, prefer small, targeted edits.

Before editing:
1. Read this AGENTS.md.
2. Check the code map.
3. Identify the smallest set of files needed for the change.

Do not scan or rewrite unrelated files.

Keep responsibilities separated:
- CLI wiring belongs in `cli.py`.
- Path handling belongs in `paths.py`.
- Git commands belong in `git_utils.py`.
- Note handling belongs in `notes.py`.
- Snapshot logic belongs in `snapshot.py`.
- Markdown generation belongs in `builder.py`.
- Redaction belongs in `redaction.py`.
- Clipboard helpers belong in `clipboard.py`.
- Sent history belongs in `ledger.py`.
- Status display belongs in `status.py`.

Avoid large rewrites unless explicitly requested.

## Release guidance

When asked to release:
1. Run tests.
2. Check `git status`.
3. Commit with a clear message.
4. Push `main`.
5. Create and push a semantic version tag.
6. Report the repository URL and tag.

For PyPI release preparation:

```powershell
python -m pip install -e ".[dev]"
python -m build
python -m twine check dist/*
```

Publishing to PyPI requires PyPI credentials or a trusted publishing setup.

## Definition of done

- `ctx init` works.
- `ctx note "test"` works.
- `ctx snap` works.
- `ctx ask` generates Markdown files.
- `ctx ask` attempts clipboard copy.
- `ctx sent --target chatgpt` records sent history.
- `ctx status` shows useful status.
- README.md explains the project clearly.
- AGENTS.md includes future AI editing guidance.
- Basic pytest tests pass.
- `ctx doctor` reports useful environment readiness information.
- Git commit exists.
- GitHub repository exists and is public.
- `main` is pushed.
- A semantic version tag is created and pushed.
