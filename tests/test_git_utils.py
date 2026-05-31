from ctx_ledger.git_utils import is_ignored_status_path


def test_ignores_ctx_ledger_status_paths() -> None:
    assert is_ignored_status_path(".ctx-ledger/")
    assert is_ignored_status_path(".ctx-ledger/generated/NEXT_PROMPT.md")
    assert is_ignored_status_path(r".ctx-ledger\generated\NEXT_PROMPT.md")


def test_keeps_project_files() -> None:
    assert not is_ignored_status_path("todo.py")
    assert not is_ignored_status_path("docs/.ctx-ledger-notes.md")
