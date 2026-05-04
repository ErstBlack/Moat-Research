"""
Swarm-aggregate token-bucket throttle. Ingestors call GET /token?source_id=<id>
before each external request. The coordinator owns the per-source rate budget,
so the swarm can never exceed it in aggregate (per spec §9.1).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlparse

import yaml

DEFAULT_CAPACITY_FACTOR = 2


@dataclass
class TokenBucket:
    rate_per_min: float
    capacity: int

    def __post_init__(self):
        self._tokens = float(self.capacity)
        self._last = time.monotonic()
        self._lock = Lock()

    def consume(self, n: float = 1.0) -> bool:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            refill = elapsed * (self.rate_per_min / 60.0)
            self._tokens = min(float(self.capacity), self._tokens + refill)
            self._last = now
            if self._tokens >= n:
                self._tokens -= n
                return True
            return False


class SourceRegistry:
    def __init__(self, configs: dict):
        self._buckets: dict[str, TokenBucket] = {}
        for sid, cfg in configs.items():
            rate = float(cfg["rate_per_min"])
            cap = int(cfg.get("capacity") or max(1, int(rate / 60 * DEFAULT_CAPACITY_FACTOR)))
            self._buckets[sid] = TokenBucket(rate_per_min=rate, capacity=cap)

    @classmethod
    def from_yaml(cls, path: Path) -> "SourceRegistry":
        data = yaml.safe_load(Path(path).read_text()) or {}
        configs = {}
        for entry in (data.get("sources") or []):
            if not entry.get("enabled", False):
                continue
            sid = entry["id"]
            rate = float(entry.get("rate_budget_per_min", 1.0))
            configs[sid] = {"rate_per_min": rate}
        return cls(configs)

    def consume(self, source_id: str) -> bool:
        bucket = self._buckets.get(source_id)
        if bucket is None:
            return False
        return bucket.consume()


def make_handler(registry: SourceRegistry):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path != "/token":
                self.send_error(404)
                return
            qs = parse_qs(parsed.query)
            source_id = (qs.get("source_id") or [""])[0]
            if not source_id:
                self.send_error(400, "missing source_id")
                return
            ok = registry.consume(source_id)
            self.send_response(200 if ok else 429)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": ok, "source_id": source_id}).encode())

        def log_message(self, fmt, *args):
            pass
    return Handler


def main() -> None:
    sources_yml = Path("/app/signals/sources.yml")
    registry = SourceRegistry.from_yaml(sources_yml) if sources_yml.exists() else SourceRegistry({})
    server = HTTPServer(("0.0.0.0", 8080), make_handler(registry))
    print("[coordinator] listening on :8080")
    server.serve_forever()


if __name__ == "__main__":
    main()
