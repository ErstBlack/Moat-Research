from pathlib import Path

import pytest

from mr.synth.prompts import PromptNotFoundError, load_prompt


def test_load_existing(tmp_path: Path):
    p = tmp_path / "discover.md"
    p.write_text("# Discover prompt\n\nRules...")
    text = load_prompt(tmp_path, "discover")
    assert "Discover prompt" in text


def test_load_missing_raises(tmp_path: Path):
    with pytest.raises(PromptNotFoundError, match="discover"):
        load_prompt(tmp_path, "discover")
