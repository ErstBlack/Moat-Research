import time
import pytest
from workers.coordinator import coordinator


class TestTokenBucket:
    def test_first_request_succeeds(self):
        tb = coordinator.TokenBucket(rate_per_min=60, capacity=10)
        assert tb.consume() is True

    def test_capacity_limit(self):
        tb = coordinator.TokenBucket(rate_per_min=60, capacity=5)
        for _ in range(5):
            assert tb.consume() is True
        assert tb.consume() is False

    def test_refill_over_time(self, monkeypatch):
        clock = [1000.0]
        monkeypatch.setattr(coordinator.time, "monotonic", lambda: clock[0])
        tb = coordinator.TokenBucket(rate_per_min=60, capacity=2)
        assert tb.consume() is True
        assert tb.consume() is True
        assert tb.consume() is False
        clock[0] += 2.0
        assert tb.consume() is True
        assert tb.consume() is True
        assert tb.consume() is False


class TestRegistry:
    def test_unknown_source_denied(self):
        reg = coordinator.SourceRegistry({})
        assert reg.consume("nope") is False

    def test_per_source_buckets_independent(self):
        reg = coordinator.SourceRegistry({
            "a": {"rate_per_min": 60, "capacity": 1},
            "b": {"rate_per_min": 60, "capacity": 1},
        })
        assert reg.consume("a") is True
        assert reg.consume("a") is False
        assert reg.consume("b") is True

    def test_load_from_sources_yml(self, tmp_path):
        sources_file = tmp_path / "sources.yml"
        sources_file.write_text("""
sources:
  - id: foo
    rate_budget_per_min: 30
    enabled: true
  - id: bar
    rate_budget_per_min: 6
    enabled: false
""")
        reg = coordinator.SourceRegistry.from_yaml(sources_file)
        assert reg.consume("foo") is True
        assert reg.consume("bar") is False
