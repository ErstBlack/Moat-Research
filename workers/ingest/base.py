"""
Abstract base class for signal ingestors. Subclasses implement fetch_one() and write();
the base class provides the politeness contract (robots check at startup, coordinator
gating before each fetch, exponential backoff on 429/503, healthcheck, daily digest).
"""
from __future__ import annotations

import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlparse

from workers.common.throttle import ThrottleClient

DEFAULT_USER_AGENT = "moat-research-ingest/0.1 (+https://github.com/local/moat-research)"


def _robots_allows(url: str, user_agent: str) -> bool:
    """Check robots.txt for the URL's host. True = allowed (or robots.txt missing)."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        return True
    return rp.can_fetch(user_agent, url)


class BaseIngestor(ABC):
    SOURCE_ID: str = ""

    def __init__(
        self,
        *,
        storage_path: str,
        coordinator_url: str,
        rate_budget_per_min: float,
        robots_check_url: str | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
        cadence_seconds: int = 60,
    ):
        if not self.SOURCE_ID:
            raise ValueError("Subclass must set SOURCE_ID")
        self.storage_path = storage_path
        self.coordinator = ThrottleClient(coordinator_url)
        self.rate_budget_per_min = rate_budget_per_min
        self.robots_check_url = robots_check_url
        self.user_agent = user_agent
        self.cadence_seconds = cadence_seconds
        Path(storage_path).mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def fetch_one(self) -> bytes:
        """Single fetch from upstream. Must NOT call coordinator — base class handles that."""

    @abstractmethod
    def write(self, payload: bytes) -> Path:
        """Persist payload; return the path written."""

    def healthcheck(self) -> bool:
        return Path(self.storage_path).exists()

    def startup(self) -> None:
        if self.robots_check_url:
            if not _robots_allows(self.robots_check_url, self.user_agent):
                raise RuntimeError(
                    f"robots.txt disallows {self.robots_check_url} for {self.user_agent}; refusing to start"
                )

    def run_forever(self) -> None:
        self.startup()
        backoff = 1.0
        while True:
            try:
                if not self.coordinator.consume(self.SOURCE_ID):
                    time.sleep(min(backoff, 30))
                    backoff = min(backoff * 2, 30)
                    continue
                backoff = 1.0
                payload = self.fetch_one()
                self.write(payload)
            except Exception as exc:
                print(f"[{self.SOURCE_ID}] error: {exc}", file=sys.stderr)
                time.sleep(min(backoff, 60))
                backoff = min(backoff * 2, 60)
                continue
            time.sleep(self.cadence_seconds)
