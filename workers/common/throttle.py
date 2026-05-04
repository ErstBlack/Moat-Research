"""
Client for the swarm coordinator. Ingestors must call ThrottleClient.consume(source_id)
before every external request and only proceed on True.
"""
from __future__ import annotations

import json
from urllib.request import urlopen
from urllib.error import HTTPError, URLError


class _Resp:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body

    def json(self):
        return json.loads(self._body)


def _http_get(url: str, timeout: float):
    """Stdlib HTTP GET; returns object with .status_code and .json()."""
    try:
        with urlopen(url, timeout=timeout) as r:
            return _Resp(r.status, r.read().decode())
    except HTTPError as e:
        return _Resp(e.code, e.read().decode() if e.fp else "{}")
    except URLError:
        return _Resp(599, "{}")


class ThrottleClient:
    def __init__(self, coordinator_url: str, timeout: float = 2.0):
        self.coordinator_url = coordinator_url.rstrip("/")
        self.timeout = timeout

    def consume(self, source_id: str) -> bool:
        url = f"{self.coordinator_url}/token?source_id={source_id}"
        r = _http_get(url, timeout=self.timeout)
        return r.status_code == 200
