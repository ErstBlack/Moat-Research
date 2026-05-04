"""
For each brief in briefs/approved/, render a sibling <id>.init-prompt.md from template.md.

Stateless; runs as a 60s sweep loop in production. Idempotent.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from string import Template

from workers.common import brief as brief_lib

TEMPLATE_PATH = Path(__file__).parent / "template.md"
INIT_PROMPT_SUFFIX = ".init-prompt.md"


def _format_signals(signals: list) -> str:
    if not signals:
        return "  (none recorded)"
    lines = []
    for s in signals:
        url = s.get("url", "?")
        note = s.get("note", "")
        lines.append(f"  - {url} — {note}")
    return "\n".join(lines)


def render(b: brief_lib.Brief, filename: str) -> str:
    """Render the init-prompt for a single Brief."""
    tmpl = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
    pc = b.proposed_capture or {}
    er = b.estimated_resources or {}
    return tmpl.safe_substitute(
        title=b.title,
        id=b.id,
        slug=b.id.replace("brief_", "").replace("_", "-"),
        description=(b.description or "").strip(),
        capture_what=pc.get("what", ""),
        capture_retention=pc.get("retention", ""),
        capture_derived_artifacts=", ".join(pc.get("derived_artifacts") or []),
        source_signals_block=_format_signals(b.source_signals or []),
        resource_storage_gb_per_month=er.get("storage_gb_per_month", "?"),
        resource_cpu_cores=er.get("cpu_cores", "?"),
        resource_ram_gb=er.get("ram_gb", "?"),
        resource_gpu=er.get("gpu", "?"),
        resource_request_rate_per_min=er.get("request_rate_per_min", "?"),
        resource_concurrent_services=er.get("concurrent_services", "?"),
        filename=filename,
        lane=b.lane,
        composite_score=f"{b.composite_score:.3f}" if b.composite_score is not None else "?",
        last_reviewed=b.last_reviewed or "?",
    )


def sweep(repo_root: Path) -> list[Path]:
    """One pass over briefs/approved/. Returns list of artifacts written/updated."""
    repo_root = Path(repo_root)
    approved_dir = repo_root / "briefs" / "approved"
    written: list[Path] = []
    for path in sorted(approved_dir.glob("*.md")):
        if path.name.endswith(INIT_PROMPT_SUFFIX):
            continue
        try:
            b = brief_lib.parse_brief(path)
        except Exception as exc:
            print(f"[init-prompt-gen] skipping {path.name}: {exc}", file=sys.stderr)
            continue
        if b.status != "approved":
            print(f"[init-prompt-gen] skipping {path.name}: status={b.status}", file=sys.stderr)
            continue
        artifact = approved_dir / f"{b.id}{INIT_PROMPT_SUFFIX}"
        new_content = render(b, path.name)
        if artifact.exists() and artifact.read_text() == new_content:
            continue
        artifact.write_text(new_content, encoding="utf-8")
        written.append(artifact)
    return written


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    interval = 60
    while True:
        try:
            sweep(repo)
        except Exception as exc:
            print(f"[init-prompt-gen] sweep failed: {exc}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    main()
