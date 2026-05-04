"""
Indexer worker: regenerates briefs/index.json from all briefs across lifecycle dirs.

Stateless; runs as a 60s sweep loop in production. The unit-tested function is rebuild().
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from dataclasses import asdict

from workers.common import brief as brief_lib

LIFECYCLE_DIRS = ("candidates", "scored", "rejected", "approved", "graduated")


def rebuild(repo_root: Path) -> None:
    """Walk all lifecycle dirs, parse every brief, write briefs/index.json."""
    repo_root = Path(repo_root)
    entries = []
    for sub in LIFECYCLE_DIRS:
        d = repo_root / "briefs" / sub
        if not d.exists():
            continue
        for path in sorted(d.glob("*.md")):
            if path.name.endswith(".init-prompt.md"):
                continue
            try:
                b = brief_lib.parse_brief(path)
            except Exception as exc:
                print(f"[indexer] skipping {path}: {exc}", file=sys.stderr)
                continue
            entry = asdict(b)
            entry.pop("body", None)
            entry["lifecycle_dir"] = sub
            entry["filename"] = path.name
            entries.append(entry)
    entries.sort(
        key=lambda e: (e.get("composite_score") if e.get("composite_score") is not None else float("-inf")),
        reverse=True,
    )
    out_path = repo_root / "briefs" / "index.json"
    out_path.write_text(json.dumps({"briefs": entries}, indent=2, default=str), encoding="utf-8")


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    interval = 60
    while True:
        try:
            rebuild(repo)
        except Exception as exc:
            print(f"[indexer] rebuild failed: {exc}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    main()
