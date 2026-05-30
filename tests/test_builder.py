from ctx_ledger.builder import render_next_prompt
from ctx_ledger.redaction import redact_text


def test_render_next_prompt_contains_core_sections() -> None:
    snapshot = {
        "branch": "main",
        "latest_commit": {"short_hash": "abc123", "subject": "Initial commit"},
        "dirty": True,
        "changed_files": ["README.md"],
        "diff_stat": "README.md | 2 ++",
    }

    prompt = render_next_prompt(snapshot, ["# Note\n\nUse sk-abc123456789"], "codex", 4000, True)
    redacted = redact_text(prompt)

    assert "# Next Prompt" in redacted
    assert "## Current notes" in redacted
    assert "- Branch: main" in redacted
    assert "- README.md" in redacted
    assert "<OPENAI_API_KEY>" in redacted
    assert "sk-abc123456789" not in redacted


def test_render_next_prompt_supports_japanese() -> None:
    snapshot = {
        "branch": "main",
        "latest_commit": {"short_hash": "abc123", "subject": "Initial commit"},
        "dirty": False,
        "changed_files": [],
        "diff_stat": "",
    }

    prompt = render_next_prompt(snapshot, ["# Note\n\n日本語メモ"], "chatgpt", None, False, "ja")

    assert "# 次のプロンプト" in prompt
    assert "## 現在のメモ" in prompt
    assert "- ブランチ: main" in prompt
    assert "- 作業ツリー: クリーン" in prompt
    assert "- メモはまだありません。" not in prompt
