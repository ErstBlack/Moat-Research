"""Hand-off prompt builder for delivery_form: project (fresh project init).

Spec §13.1.
"""
from __future__ import annotations

from mr.lifecycle.frontmatter import Brief
from mr.util.config import Config


def build_project_handoff(brief: Brief, *, cfg: Config, adjacent_appendix: str) -> str:
    """Render the project init-prompt to stdout for `mr graduate`."""
    hw = cfg.hardware
    return f"""You are starting {brief.slug}. Brief follows verbatim.

Hardware envelope:
  CPU: {hw['cpu']}
  RAM: {hw['ram_gb']} GB
  GPU: {hw['gpu']} — plan for ≤4 GB sustained
  Storage: {hw['storage_tb']} TB NAS
  Network: {hw['network']}

Brief:
{_brief_markdown(brief)}

{adjacent_appendix}

First action: read CLAUDE.md if present, then ask 1–3 clarifying questions before scaffolding.
"""


def _brief_markdown(brief: Brief) -> str:
    """Render the brief body with frontmatter context."""
    scores = brief.scores or {}
    score_line = (
        f"Scores: defensibility={scores.get('defensibility', '?')} | "
        f"financial={scores.get('financial', '?')} | "
        f"implementation={scores.get('implementation', '?')} | "
        f"hardware={scores.get('hardware', '?')} | "
        f"composite={scores.get('composite', '?')}"
    )
    src_lines = "\n".join(f"  - {s.get('url', '?')} ({s.get('role', '?')})" for s in brief.sources)
    return f"""# {brief.title}

Lane: {brief.lane}  ·  Niche: {brief.niche}  ·  Date: {brief.date_created}
{score_line}
Sources:
{src_lines}

{brief.body}"""
