"""POSIX flock(2)-based exclusive lock for .moat-research/.lock.

Per spec §10: blocks up to 60s by default, then errors. Local POSIX
filesystem only — NFS is unsupported.
"""
from __future__ import annotations

import errno
import fcntl
import os
import time
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


class LockTimeout(Exception):  # noqa: N818
    """Raised when the lock cannot be acquired within timeout_seconds."""


@contextmanager
def exclusive_lock(path: Path, timeout_seconds: float = 60.0) -> Generator[None]:
    """Hold an exclusive flock on `path` for the duration of the with-block.

    Creates the parent directory and the lockfile if missing. Polls
    every 100ms; raises LockTimeout if the lock isn't available within
    timeout_seconds.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    fd = -1
    try:
        fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as e:
                if e.errno not in (errno.EAGAIN, errno.EACCES):
                    raise
                if time.monotonic() >= deadline:
                    raise LockTimeout(
                        f"could not acquire {path} within {timeout_seconds:.1f}s"
                    ) from e
                time.sleep(0.1)
        yield
    finally:
        if fd != -1:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)
