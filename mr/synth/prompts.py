"""Prompt loader. Reads from prompts/ on each invocation, no compilation."""
from __future__ import annotations

from pathlib import Path


class PromptNotFoundError(Exception):
    """Raised when load_prompt cannot find the named prompt file."""


def load_prompt(prompts_dir: Path, name: str) -> str:
    """Load a prompt file by name (without .md extension)."""
    path = prompts_dir / f"{name}.md"
    if not path.exists():
        raise PromptNotFoundError(f"prompt {name!r} not found at {path}")
    return path.read_text()
