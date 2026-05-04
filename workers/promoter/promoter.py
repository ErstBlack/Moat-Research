"""
Promoter worker: scans briefs/scored/, moves any brief with an axis=0 to briefs/rejected/.

Stateless; runs as a 60s sweep loop in production. The unit-tested function is sweep().
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from workers.common import brief as brief_lib


def sweep(repo_root: Path) -> list[Path]:
    """
    One pass over briefs/scored/. Returns the list of files moved to rejected/.
    Malformed files are moved to briefs/_quarantine/ instead of crashing.
    """
    repo_root = Path(repo_root)
    scored_dir = repo_root / "briefs" / "scored"
    rejected_dir = repo_root / "briefs" / "rejected"
    quarantine_dir = repo_root / "briefs" / "_quarantine"
    quarantine_dir.mkdir(exist_ok=True)

    moved: list[Path] = []
    for path in sorted(scored_dir.glob("*.md")):
        try:
            b = brief_lib.parse_brief(path)
        except Exception as exc:
            dst = quarantine_dir / path.name
            path.rename(dst)
            print(f"[promoter] quarantined {path.name}: {exc}", file=sys.stderr)
            continue

        axis = brief_lib.failed_axis(b)
        if axis is None:
            continue

        original = path.name
        if "-" in original:
            tail = original.split("-", 1)[1]
        else:
            tail = original
        new_name = f"00.000-{axis}-{tail}"
        dst = rejected_dir / new_name

        b.status = "rejected"
        b.body = (b.body or "") + f"\n\n<!-- rejection_reason: axis={axis} composite=0 (auto) -->\n"
        brief_lib.write_brief(b, dst)
        raw = dst.read_text()
        raw = raw.replace("---\n", f"---\nrejection_reason: \"axis={axis}\"\n", 1)
        dst.write_text(raw)
        path.unlink()
        moved.append(dst)
        print(f"[promoter] rejected {original} -> {new_name} (axis={axis})")

    return moved


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    interval = 60
    while True:
        try:
            sweep(repo)
        except Exception as exc:
            print(f"[promoter] sweep failed: {exc}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    main()
