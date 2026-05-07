from pathlib import Path

import pytest

from mr.lifecycle.paths import RepoLayout
from mr.lifecycle.transitions import TransitionError, move_brief


def _make_brief(path: Path, content: str = "---\nschema_version: 1\n---\n# x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def test_move_candidate_to_scored(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    src = _make_brief(layout.candidates / "20260507-foo.md")

    dst = layout.scored / "07221-20260507-foo.md"
    move_brief(src, dst)
    assert not src.exists()
    assert dst.exists()


def test_move_to_existing_dest_raises(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    src = _make_brief(layout.candidates / "20260507-foo.md")
    existing = _make_brief(layout.scored / "07221-20260507-foo.md", content="existing")

    with pytest.raises(TransitionError, match="already exists"):
        move_brief(src, existing)
    assert src.exists()  # source untouched on failure
    assert existing.read_text() == "existing"  # dest untouched


def test_move_creates_dest_parent_if_missing(tmp_path: Path):
    src = tmp_path / "candidates" / "20260507-foo.md"
    _make_brief(src)
    dst = tmp_path / "scored" / "07221-20260507-foo.md"
    # scored/ doesn't exist yet
    move_brief(src, dst)
    assert dst.exists()


def test_move_missing_source_raises(tmp_path: Path):
    src = tmp_path / "absent.md"
    dst = tmp_path / "out.md"
    with pytest.raises(TransitionError, match="not found"):
        move_brief(src, dst)
