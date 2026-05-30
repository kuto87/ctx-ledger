"""Secret and personal information redaction for generated prompts."""

from __future__ import annotations

import re


OPENAI_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b")
GITHUB_TOKEN_RE = re.compile(r"\bghp_[A-Za-z0-9_]{8,}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
WINDOWS_USER_RE = re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+")


def redact_text(text: str) -> str:
    """Mask supported secret and personal-info patterns."""

    redacted = OPENAI_KEY_RE.sub("<OPENAI_API_KEY>", text)
    redacted = GITHUB_TOKEN_RE.sub("<GITHUB_TOKEN>", redacted)
    redacted = EMAIL_RE.sub("<EMAIL>", redacted)
    redacted = WINDOWS_USER_RE.sub("<USER_HOME>", redacted)
    return redacted
