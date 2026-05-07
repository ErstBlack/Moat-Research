from unittest.mock import MagicMock, patch

import pytest

from mr.tools.firecrawl import FirecrawlNotConfiguredError, firecrawl_scrape, is_firecrawl_available


def test_unavailable_when_env_unset(monkeypatch):
    monkeypatch.delenv("MR_FIRECRAWL_API_KEY", raising=False)
    assert is_firecrawl_available() is False


def test_available_when_env_set(monkeypatch):
    monkeypatch.setenv("MR_FIRECRAWL_API_KEY", "fc-test-key")
    assert is_firecrawl_available() is True


def test_scrape_raises_without_env(monkeypatch):
    monkeypatch.delenv("MR_FIRECRAWL_API_KEY", raising=False)
    with pytest.raises(FirecrawlNotConfiguredError):
        firecrawl_scrape("https://example.com")


@patch("mr.tools.firecrawl.FirecrawlApp")
def test_scrape_returns_markdown(mock_app_cls, monkeypatch):
    monkeypatch.setenv("MR_FIRECRAWL_API_KEY", "fc-test-key")
    mock_app = MagicMock()
    mock_app.scrape.return_value = MagicMock(markdown="# Hello\n\nworld")
    mock_app_cls.return_value = mock_app

    result = firecrawl_scrape("https://example.com")
    assert result.markdown == "# Hello\n\nworld"
    mock_app_cls.assert_called_once_with(api_key="fc-test-key")
