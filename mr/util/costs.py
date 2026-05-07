"""costs.jsonl writer and reader for spend tracking.

Spec §10: one JSON object per line with cache_hits/cache_misses
(token counts), code_execution_container_seconds, and cost_usd.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class CostRecord:
    ts: datetime
    command: str
    model: str
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    cache_hits: int                       # cache_read_input_tokens from API response
    cache_misses: int                     # cache_creation_input_tokens from API response
    code_execution_container_seconds: float
    cost_usd: float


def append_cost(path: Path, rec: CostRecord) -> None:
    """Append a single cost record as a JSON line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(rec)
    payload["ts"] = rec.ts.isoformat()
    with path.open("a") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")


def read_cost_history(path: Path) -> list[CostRecord]:
    """Read all cost records from path. Returns empty list if file is missing."""
    if not path.exists():
        return []
    out: list[CostRecord] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        d["ts"] = datetime.fromisoformat(d["ts"])
        out.append(CostRecord(**d))
    return out


def running_total(path: Path, command: str | None = None) -> float:
    """Sum cost_usd across the cost history. Optionally filter by command."""
    records = read_cost_history(path)
    if command is not None:
        records = [r for r in records if r.command == command]
    return sum(r.cost_usd for r in records)
