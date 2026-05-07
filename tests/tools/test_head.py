from unittest.mock import MagicMock, patch

from mr.tools.head import head_check


@patch("mr.tools.head.httpx.Client")
def test_returns_status_and_headers(mock_client_cls):
    mock_client = MagicMock()
    mock_response = MagicMock(status_code=200, headers={
        "content-type": "text/html; charset=utf-8",
        "last-modified": "Wed, 07 May 2026 12:00:00 GMT",
    })
    mock_client.head.return_value = mock_response
    mock_client_cls.return_value.__enter__.return_value = mock_client

    r = head_check("https://example.com/")
    assert r.status == 200
    assert r.content_type == "text/html; charset=utf-8"
    assert r.last_modified is not None


@patch("mr.tools.head.httpx.Client")
def test_4xx_status(mock_client_cls):
    mock_client = MagicMock()
    mock_response = MagicMock(status_code=404, headers={})
    mock_client.head.return_value = mock_response
    mock_client_cls.return_value.__enter__.return_value = mock_client

    r = head_check("https://example.com/missing")
    assert r.status == 404
    assert r.content_type is None


@patch("mr.tools.head.httpx.Client")
def test_network_error(mock_client_cls):
    import httpx
    mock_client = MagicMock()
    mock_client.head.side_effect = httpx.ConnectError("connection refused")
    mock_client_cls.return_value.__enter__.return_value = mock_client

    r = head_check("https://offline.example/")
    assert r.status is None
    assert r.error is not None
