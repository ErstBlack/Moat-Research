import multiprocessing
import time
from pathlib import Path

import pytest

from mr.util.lock import LockTimeout, exclusive_lock


def test_acquires_and_releases(tmp_path: Path):
    lockfile = tmp_path / ".lock"
    with exclusive_lock(lockfile, timeout_seconds=2.0):
        assert lockfile.exists()
    # Re-acquiring after release works
    with exclusive_lock(lockfile, timeout_seconds=2.0):
        pass


def _hold_lock(lockfile: str, hold_seconds: float, ready_q: multiprocessing.Queue):
    from mr.util.lock import exclusive_lock as el
    with el(Path(lockfile), timeout_seconds=2.0):
        ready_q.put("acquired")
        time.sleep(hold_seconds)


def test_blocks_then_times_out(tmp_path: Path):
    lockfile = tmp_path / ".lock"
    ready: multiprocessing.Queue = multiprocessing.Queue()
    holder = multiprocessing.Process(target=_hold_lock, args=(str(lockfile), 3.0, ready))
    holder.start()
    try:
        ready.get(timeout=2.0)  # wait for holder to acquire
        with pytest.raises(LockTimeout), exclusive_lock(lockfile, timeout_seconds=0.5):
            pass
    finally:
        holder.join(timeout=5.0)


def test_creates_parent_dir(tmp_path: Path):
    lockfile = tmp_path / "subdir" / ".lock"
    with exclusive_lock(lockfile, timeout_seconds=2.0):
        assert lockfile.parent.is_dir()
