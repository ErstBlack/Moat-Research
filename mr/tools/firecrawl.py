"""Firecrawl wrapper for JS-rendered or structured-extraction targets.

Spec §8.3: optional dependency, only loaded when MR_FIRECRAWL_API_KEY is set.
Used as fallback by mr discover and mr wishlist expand.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from firecrawl import FirecrawlApp
except ImportError:
    FirecrawlApp = None  # type: ignore[assignment,misc]


class FirecrawlNotConfiguredError(Exception):
    """Raised when firecrawl_scrape is called without MR_FIRECRAWL_API_KEY."""


@dataclass
class FirecrawlResult:
    markdown: str
    url: str


def is_firecrawl_available() -> bool:
    """True iff MR_FIRECRAWL_API_KEY is set in the environment."""
    return bool(os.environ.get("MR_FIRECRAWL_API_KEY"))


def firecrawl_scrape(url: str) -> FirecrawlResult:
    """Scrape a URL via Firecrawl and return its markdown.

    Raises FirecrawlNotConfigured if the API key is missing or the
    optional firecrawl-py dependency isn't installed.
    """
    api_key = os.environ.get("MR_FIRECRAWL_API_KEY")
    if not api_key:
        raise FirecrawlNotConfiguredError(
            "MR_FIRECRAWL_API_KEY not set; install moat-research[firecrawl] "
            "and export the key to enable JS-rendered scraping."
        )
    if FirecrawlApp is None:
        raise FirecrawlNotConfiguredError(
            "firecrawl-py not installed; run `uv sync --group firecrawl`."
        )

    app = FirecrawlApp(api_key=api_key)
    response = app.scrape(url)
    return FirecrawlResult(markdown=response.markdown, url=url)
