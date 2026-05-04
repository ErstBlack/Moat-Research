from pathlib import Path
import pytest
from workers.ingest import base
from workers.common import throttle


class TestThrottleClient:
    def test_consume_calls_coordinator(self, monkeypatch):
        calls = []

        def fake_get(url, timeout):
            calls.append(url)
            class R:
                status_code = 200
                def json(self): return {"ok": True}
            return R()

        monkeypatch.setattr(throttle, "_http_get", fake_get)
        c = throttle.ThrottleClient("http://coord:8080")
        assert c.consume("foo") is True
        assert "source_id=foo" in calls[0]

    def test_consume_returns_false_on_429(self, monkeypatch):
        def fake_get(url, timeout):
            class R:
                status_code = 429
                def json(self): return {"ok": False}
            return R()
        monkeypatch.setattr(throttle, "_http_get", fake_get)
        c = throttle.ThrottleClient("http://coord:8080")
        assert c.consume("foo") is False


class _ConcreteIngestor(base.BaseIngestor):
    SOURCE_ID = "concrete_test"

    def fetch_one(self):
        return b"payload"

    def write(self, payload):
        return Path(self.storage_path) / "out.txt"


class TestBaseIngestor:
    def test_subclass_must_set_source_id(self):
        class Bad(base.BaseIngestor):
            def fetch_one(self): return b""
            def write(self, p): return Path("/tmp/x")
        with pytest.raises(ValueError, match="SOURCE_ID"):
            Bad(storage_path="/tmp", coordinator_url="http://x", rate_budget_per_min=1)

    def test_subclass_must_implement_fetch_one(self):
        class Bad(base.BaseIngestor):
            SOURCE_ID = "x"
            def write(self, p): return Path("/tmp/x")
        with pytest.raises(TypeError):
            Bad(storage_path="/tmp", coordinator_url="http://x", rate_budget_per_min=1)

    def test_concrete_instantiates(self, tmp_path):
        ing = _ConcreteIngestor(
            storage_path=str(tmp_path),
            coordinator_url="http://coord:8080",
            rate_budget_per_min=1,
        )
        assert ing.SOURCE_ID == "concrete_test"
        assert ing.healthcheck() is True

    def test_robots_check_called_at_startup(self, tmp_path, monkeypatch):
        called = []
        monkeypatch.setattr(base, "_robots_allows", lambda url, ua: called.append(url) or True)
        ing = _ConcreteIngestor(
            storage_path=str(tmp_path),
            coordinator_url="http://coord:8080",
            rate_budget_per_min=1,
            robots_check_url="https://example.com/somepath",
        )
        ing.startup()
        assert called and "example.com" in called[0]

    def test_robots_disallow_refuses_to_start(self, tmp_path, monkeypatch):
        monkeypatch.setattr(base, "_robots_allows", lambda url, ua: False)
        ing = _ConcreteIngestor(
            storage_path=str(tmp_path),
            coordinator_url="http://coord:8080",
            rate_budget_per_min=1,
            robots_check_url="https://example.com/x",
        )
        with pytest.raises(RuntimeError, match="robots"):
            ing.startup()
