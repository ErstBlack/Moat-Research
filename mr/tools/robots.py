"""robots.txt check using urllib.robotparser.

Spec §8.3: stdlib only. Fail-open on network errors per RFC convention.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


@dataclass
class RobotsResult:
    allowed: bool
    robots_url: str
    error: str | None


def robots_check(url: str, user_agent: str) -> RobotsResult:
    """Check robots.txt for the URL's origin. Fails open on network error."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        parser.read()
    except OSError as e:
        return RobotsResult(allowed=True, robots_url=robots_url, error=str(e))

    allowed = parser.can_fetch(user_agent, url)
    return RobotsResult(allowed=allowed, robots_url=robots_url, error=None)
