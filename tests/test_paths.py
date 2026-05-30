from ctx_ledger.paths import ensure_initialized, load_config, project_paths, save_config


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


def test_config_defaults_and_updates(tmp_path) -> None:
    ensure_initialized(tmp_path)

    config = load_config(tmp_path)
    assert config["default_target"] == "chatgpt"
    assert config["default_language"] == "en"
    assert config["default_budget"] is None

    save_config({"default_language": "ja", "default_budget": 4000}, tmp_path)
    updated = load_config(tmp_path)
    assert updated["default_target"] == "chatgpt"
    assert updated["default_language"] == "ja"
    assert updated["default_budget"] == 4000
