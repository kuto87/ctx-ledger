from ctx_ledger.redaction import redact_text


def test_redacts_supported_secret_and_personal_patterns() -> None:
    text = (
        "sk-abc123456789 ghp_abc123456789 someone@example.com "
        r"C:\Users\taro\project"
    )

    redacted = redact_text(text)

    assert "<OPENAI_API_KEY>" in redacted
    assert "<GITHUB_TOKEN>" in redacted
    assert "<EMAIL>" in redacted
    assert r"<USER_HOME>\project" in redacted
    assert "someone@example.com" not in redacted
