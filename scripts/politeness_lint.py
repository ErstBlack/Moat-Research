"""
Lint signals/sources.yml against the politeness checklist (spec §13).

Exit code 0 if clean, 1 if any violation. Designed to run in pre-commit / CI.

Usage: python scripts/politeness_lint.py signals/sources.yml
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED_FIELDS = ("id", "url", "cadence", "rate_budget_per_min", "storage_path", "parser", "enabled")


def lint(path: Path) -> list[str]:
    """Return a list of human-readable violation strings; empty list = clean."""
    data = yaml.safe_load(Path(path).read_text()) or {}
    sources = data.get("sources") or []
    violations: list[str] = []
    for i, entry in enumerate(sources):
        sid = entry.get("id", f"<index {i}>")
        for field in REQUIRED_FIELDS:
            if field not in entry:
                violations.append(f"source '{sid}' is missing required field '{field}'")
        if "rate_budget_per_min" in entry and entry["rate_budget_per_min"] is not None:
            try:
                rate = float(entry["rate_budget_per_min"])
                if rate <= 0:
                    violations.append(f"source '{sid}' has rate_budget_per_min={rate}; must be >0")
            except (TypeError, ValueError):
                violations.append(f"source '{sid}' has non-numeric rate_budget_per_min")
    return violations


def main(argv: list[str]) -> int:
    if len(argv) < 1:
        print("usage: politeness_lint.py <sources.yml>", file=sys.stderr)
        return 2
    path = Path(argv[0])
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 2
    violations = lint(path)
    if not violations:
        print(f"OK: {path} clean ({len(yaml.safe_load(path.read_text()).get('sources') or [])} source(s) checked)")
        return 0
    for v in violations:
        print(f"VIOLATION: {v}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
