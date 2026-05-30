from ctx_ledger.paths import ensure_initialized, project_paths


def test_ensure_initialized_creates_expected_paths(tmp_path) -> None:
    paths = ensure_initialized(tmp_path)

    assert paths.ledger.is_dir()
    assert paths.config.is_file()
    assert paths.cards.is_dir()
    assert paths.notes.is_dir()
    assert paths.generated.is_dir()
    assert paths.sent.is_dir()
    assert paths.cache.is_dir()
    assert project_paths(tmp_path).next_prompt.name == "NEXT_PROMPT.md"
    assert ".ctx-ledger/generated/" in (tmp_path / ".gitignore").read_text(encoding="utf-8")
