import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from mr.util.costs import CostRecord, append_cost, read_cost_history, running_total


def test_append_and_read_roundtrip(tmp_path: Path):
    path = tmp_path / "costs.jsonl"
    rec = CostRecord(
        ts=datetime(2026, 5, 7, 12, 0, 0, tzinfo=UTC),
        command="discover",
        model="claude-opus-4-7",
        input_tokens=1000,
        cached_input_tokens=500,
        output_tokens=200,
        cache_hits=500,
        cache_misses=0,
        code_execution_container_seconds=2.5,
        cost_usd=0.0345,
    )
    append_cost(path, rec)
    records = read_cost_history(path)
    assert len(records) == 1
    assert records[0].command == "discover"
    assert records[0].cost_usd == 0.0345


def test_appends_to_existing_file(tmp_path: Path):
    path = tmp_path / "costs.jsonl"
    for i in range(3):
        append_cost(path, CostRecord(
            ts=datetime(2026, 5, 7, 12, i, 0, tzinfo=UTC),
            command="score",
            model="claude-opus-4-7",
            input_tokens=100, cached_input_tokens=0, output_tokens=50,
            cache_hits=0, cache_misses=0,
            code_execution_container_seconds=0.0, cost_usd=0.01,
        ))
    records = read_cost_history(path)
    assert len(records) == 3


def test_running_total_for_command(tmp_path: Path):
    path = tmp_path / "costs.jsonl"
    for cmd, cost in [("discover", 0.10), ("score", 0.05), ("discover", 0.20)]:
        append_cost(path, CostRecord(
            ts=datetime(2026, 5, 7, 12, 0, 0, tzinfo=UTC),
            command=cmd,
            model="claude-opus-4-7",
            input_tokens=0, cached_input_tokens=0, output_tokens=0,
            cache_hits=0, cache_misses=0,
            code_execution_container_seconds=0.0, cost_usd=cost,
        ))
    assert running_total(path) == pytest.approx(0.35)


def test_jsonl_format_one_object_per_line(tmp_path: Path):
    path = tmp_path / "costs.jsonl"
    append_cost(path, CostRecord(
        ts=datetime(2026, 5, 7, 12, 0, 0, tzinfo=UTC),
        command="discover", model="claude-opus-4-7",
        input_tokens=1, cached_input_tokens=0, output_tokens=1,
        cache_hits=0, cache_misses=0,
        code_execution_container_seconds=0.0, cost_usd=0.0001,
    ))
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["command"] == "discover"
