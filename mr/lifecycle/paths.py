"""Repo layout — lifecycle directory names and path resolution.

Spec §6 lifecycle: candidates → scored → {rejected, approved} → graduated.
Spec §10 state dir: .moat-research/{lock, costs.jsonl, seen.jsonl, cache/}.
Spec §12.1 disposition: closed set {candidate, scored, rejected, approved, graduated}.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

LIFECYCLE_DIRS: tuple[str, ...] = (
    "candidates",
    "scored",
    "rejected",
    "approved",
    "graduated",
)
"""Lifecycle directory names in canonical order (forward direction)."""

DISPOSITIONS: tuple[str, ...] = (
    "candidate",
    "scored",
    "rejected",
    "approved",
    "graduated",
)
"""seen.jsonl disposition values, parallel to LIFECYCLE_DIRS."""

_DIR_TO_DISPOSITION: dict[str, str] = dict(zip(LIFECYCLE_DIRS, DISPOSITIONS, strict=True))


def disposition_for_dir(dirname: str) -> str:
    """Map a lifecycle dirname to its disposition string."""
    return _DIR_TO_DISPOSITION[dirname]


@dataclass
class RepoLayout:
    """Resolved file paths for a moat-research repo rooted at `root`."""

    root: Path

    @property
    def candidates(self) -> Path:
        return self.root / "candidates"

    @property
    def scored(self) -> Path:
        return self.root / "scored"

    @property
    def rejected(self) -> Path:
        return self.root / "rejected"

    @property
    def approved(self) -> Path:
        return self.root / "approved"

    @property
    def graduated(self) -> Path:
        return self.root / "graduated"

    @property
    def state_dir(self) -> Path:
        return self.root / ".moat-research"

    @property
    def lock_path(self) -> Path:
        return self.state_dir / "lock"

    @property
    def costs_path(self) -> Path:
        return self.state_dir / "costs.jsonl"

    @property
    def seen_path(self) -> Path:
        return self.state_dir / "seen.jsonl"

    @property
    def config_path(self) -> Path:
        return self.root / "mr.yaml"

    @property
    def wishlist_path(self) -> Path:
        return self.root / "WISHLIST.md"

    @property
    def prompts_dir(self) -> Path:
        return self.root / "prompts"

    def lifecycle_dirs(self) -> Iterator[Path]:
        """Yield the 5 lifecycle directories in canonical order."""
        for name in LIFECYCLE_DIRS:
            yield self.root / name

    def ensure_dirs(self) -> None:
        """Create all lifecycle dirs, the state dir, and the prompts dir."""
        for d in self.lifecycle_dirs():
            d.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
