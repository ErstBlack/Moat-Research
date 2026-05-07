"""Atomic lifecycle transitions via os.replace.

Spec §6.2 (transitions table) + §12.1 (atomicity contract).
"""
from __future__ import annotations

import os
from pathlib import Path


class TransitionError(Exception):
    """Raised when a brief move cannot proceed safely."""


def move_brief(src: Path, dst: Path) -> None:
    """Atomically move src to dst. Refuses to overwrite an existing dest.

    Creates dst's parent directory if missing. Source must exist.
    Uses os.replace (atomic on POSIX same-filesystem renames).
    """
    if not src.exists():
        raise TransitionError(f"source not found: {src}")
    if dst.exists():
        raise TransitionError(f"destination already exists: {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.replace(src, dst)
