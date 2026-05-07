from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from mr.tools.wayback import WaybackResult, wayback_check


@patch("mr.tools.wayback.WaybackMachineCDXServerAPI")
def test_returns_count_first_last(mock_cdx_class):
    snapshot1 = MagicMock(timestamp="20230412120000", original="https://example.com/")
    snapshot2 = MagicMock(timestamp="20260430120000", original="https://example.com/")
    mock_instance = MagicMock()
    mock_instance.snapshots.return_value = [snapshot1, snapshot2]
    mock_cdx_class.return_value = mock_instance

    result = wayback_check("https://example.com/")
    assert isinstance(result, WaybackResult)
    assert result.count == 2
    assert result.first == date(2023, 4, 12)
    assert result.last == date(2026, 4, 30)


@patch("mr.tools.wayback.WaybackMachineCDXServerAPI")
def test_no_snapshots(mock_cdx_class):
    mock_instance = MagicMock()
    mock_instance.snapshots.return_value = []
    mock_cdx_class.return_value = mock_instance

    result = wayback_check("https://no-archive.example.com/")
    assert result.count == 0
    assert result.first is None
    assert result.last is None


@patch("mr.tools.wayback.WaybackMachineCDXServerAPI")
def test_years_helper(mock_cdx_class):
    snapshot1 = MagicMock(timestamp="20230101000000", original="https://example.com/")
    snapshot2 = MagicMock(timestamp="20260101000000", original="https://example.com/")
    mock_instance = MagicMock()
    mock_instance.snapshots.return_value = [snapshot1, snapshot2]
    mock_cdx_class.return_value = mock_instance

    result = wayback_check("https://example.com/")
    assert result.years == pytest.approx(3.0, abs=0.01)
