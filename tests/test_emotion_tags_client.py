import io

import pytest

from shared.emotion import emotion_tags_client as client


class _FakeResponse:
    def __init__(self, body: str):
        self._buffer = io.StringIO(body)

    def read(self):
        return self._buffer.read()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_request_json_rejects_invalid_json(monkeypatch):
    """Ensure the client surfaces invalid JSON responses as connection errors."""

    def fake_urlopen(req, timeout=5.0):
        return _FakeResponse("not-json")

    monkeypatch.setattr(client.request, "urlopen", fake_urlopen)

    with pytest.raises(ConnectionError) as excinfo:
        client._request_json("/tags", base_url="http://example.com")

    assert "invalid JSON" in str(excinfo.value)
