# Demo

This demo shows why ctx-ledger exists: it turns local development context into a clean prompt for the next AI coding-agent chat.

## Example Project

Imagine a tiny TODO CLI where you just added task priorities:

```powershell
python todo.py add "fix login bug" --priority high
python todo.py add "polish README" --priority low
python todo.py list
```

Output:

```text
Added #1 [high]: fix login bug
Added #2 [low]: polish README
[ ] #1 [high] fix login bug
[ ] #2 [low] polish README
```

## Build the AI Handoff

```powershell
ctx handoff "Added priority support. Please review the changes and suggest the next safe step."
```

ctx-ledger generates:

```text
.ctx-ledger/generated/NEXT_PROMPT.md
.ctx-ledger/generated/DELTA_PACK.md
.ctx-ledger/generated/RECOVERY_PACK.md
```

## Example NEXT_PROMPT.md

```md
# Next Prompt

## Current notes

- Added priority support. Please review the changes and suggest the next safe step.

## Changed files

- README.md
- test_todo.py
- todo.py

## Diff summary

README.md    |  2 +-
test_todo.py | 12 +++++++++++-
todo.py      | 33 ++++++++++++++++++++++++++++-----
```

The next ChatGPT, Codex, Claude Code, or Cursor session can start from this context instead of asking you to restate it.
