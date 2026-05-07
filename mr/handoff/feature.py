"""Hand-off prompt builder for delivery_form: feature (patch proposal).

Spec §13.2.
"""
from __future__ import annotations

from mr.handoff.project import _brief_markdown  # noqa: PLC2701
from mr.lifecycle.frontmatter import Brief
from mr.util.config import Config

_FIRST_ACTION = (
    "First action: read this repo's CLAUDE.md, the existing architecture, and any modules"
    " relevant to the brief. Do not create new files until you have understood the current"
    " shape. Propose a feature branch name and a draft PR description before any code edits."
)


def build_feature_handoff(brief: Brief, *, cfg: Config, adjacent_appendix: str) -> str:
    """Render the feature patch-proposal prompt for `mr graduate`."""
    if not brief.parent_project:
        raise ValueError(f"feature brief {brief.slug!r} missing parent_project")
    hw = cfg.hardware
    return f"""You are extending the `{brief.parent_project}` repo with a new feature. Brief follows verbatim.

Hardware envelope:
  CPU: {hw['cpu']}
  RAM: {hw['ram_gb']} GB
  GPU: {hw['gpu']} — plan for ≤4 GB sustained
  Storage: {hw['storage_tb']} TB NAS
  Network: {hw['network']}

Brief:
{_brief_markdown(brief)}

{adjacent_appendix}

{_FIRST_ACTION}
"""
