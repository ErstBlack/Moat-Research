from pathlib import Path

import pytest

from mr.lifecycle.paths import (
    DISPOSITIONS,
    LIFECYCLE_DIRS,
    RepoLayout,
    disposition_for_dir,
)


def test_lifecycle_dir_set():
    assert LIFECYCLE_DIRS == ("candidates", "scored", "rejected", "approved", "graduated")


def test_dispositions_match_dirs():
    assert DISPOSITIONS == ("candidate", "scored", "rejected", "approved", "graduated")


def test_disposition_for_dir():
    assert disposition_for_dir("candidates") == "candidate"
    assert disposition_for_dir("scored") == "scored"
    assert disposition_for_dir("graduated") == "graduated"


def test_repo_layout(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    assert layout.root == tmp_path
    assert layout.candidates == tmp_path / "candidates"
    assert layout.scored == tmp_path / "scored"
    assert layout.rejected == tmp_path / "rejected"
    assert layout.approved == tmp_path / "approved"
    assert layout.graduated == tmp_path / "graduated"
    assert layout.state_dir == tmp_path / ".moat-research"
    assert layout.lock_path == tmp_path / ".moat-research" / "lock"
    assert layout.seen_path == tmp_path / ".moat-research" / "seen.jsonl"
    assert layout.config_path == tmp_path / "mr.yaml"
    assert layout.wishlist_path == tmp_path / "WISHLIST.md"
    assert layout.prompts_dir == tmp_path / "prompts"


def test_repo_layout_ensure_dirs(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    for d in LIFECYCLE_DIRS:
        assert (tmp_path / d).is_dir()
    assert layout.state_dir.is_dir()
    assert layout.prompts_dir.is_dir()


def test_lifecycle_dirs_iter(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    paths = list(layout.lifecycle_dirs())
    assert len(paths) == 5
    assert paths[0] == tmp_path / "candidates"
    assert paths[-1] == tmp_path / "graduated"


def test_disposition_for_dir_invalid():
    with pytest.raises(KeyError):
        disposition_for_dir("nonexistent")


def test_ensure_dirs_idempotent(tmp_path: Path):
    """Calling ensure_dirs() twice must not raise (exist_ok=True is preserved)."""
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    layout.ensure_dirs()  # second call must not raise
