"""Clipboard helper with non-fatal failure handling."""

from __future__ import annotations

import pyperclip


def copy_text(text: str) -> tuple[bool, str | None]:
    """Copy text to the clipboard and return success plus optional error."""

    try:
        pyperclip.copy(text)
    except pyperclip.PyperclipException as exc:
        return False, str(exc)
    return True, None
