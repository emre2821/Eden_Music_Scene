"""Integration tests for the lightweight emotion tag HTTP service."""

from __future__ import annotations

import http.client
import json
import threading
from contextlib import contextmanager
from http.server import HTTPServer
from typing import Generator

import pytest

import emotion_service


@contextmanager
def running_service() -> Generator[tuple[str, int], None, None]:
    """Run the HTTP server in a background thread for the duration of a test."""

    emotion_service.TAGS.clear()
    server = HTTPServer(("127.0.0.1", 0), emotion_service.EmotionTagHandler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield host, port
    finally:
        server.shutdown()
        thread.join(timeout=3)
        emotion_service.TAGS.clear()


def _request(host: str, port: int, method: str, path: str, body: object | None = None) -> tuple[int, dict]:
    payload: bytes | None = None
    headers = {}
    if body is not None:
        payload = json.dumps(body).encode("utf-8") if not isinstance(body, bytes) else body
        headers["Content-Type"] = "application/json"

    conn = http.client.HTTPConnection(host, port, timeout=5)
    conn.request(method, path, body=payload, headers=headers)
    response = conn.getresponse()
    data = response.read()
    try:
        parsed = json.loads(data.decode("utf-8")) if data else {}
    except json.JSONDecodeError:  # pragma: no cover - service always emits json
        parsed = {}
    conn.close()
    return response.status, parsed


def test_get_tags_initially_empty() -> None:
    with running_service() as (host, port):
        status, payload = _request(host, port, "GET", "/tags")
        assert status == 200
        assert payload == []


def test_rejects_invalid_json() -> None:
    with running_service() as (host, port):
        conn = http.client.HTTPConnection(host, port, timeout=5)
        conn.request("POST", "/tags", body=b"{" , headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        assert response.status == 400
        assert json.loads(response.read()) == {"error": "invalid json"}
        conn.close()


@pytest.mark.parametrize(
    "payload, expected_message",
    [
        ({"emotion": "joy"}, "missing required fields"),
        ({"track_id": "abc"}, "missing required fields"),
        ({"track_id": 101, "emotion": "joy"}, "track_id must be a non-empty string"),
        ({"track_id": "abc", "emotion": 5}, "emotion must be a non-empty string"),
        ({"track_id": "abc", "emotion": "joy", "extra": 1}, "unexpected field"),
        ({"track_id": "abc", "emotion": "joy", "intensity": 4}, "intensity must be between 0 and 1"),
        ({"track_id": "abc", "emotion": "joy", "intensity": "high"}, "intensity must be a number"),
    ],
)
def test_rejects_invalid_payloads(payload: dict, expected_message: str) -> None:
    with running_service() as (host, port):
        status, body = _request(host, port, "POST", "/tags", body=payload)
        assert status == 400
        assert expected_message in body["error"]


def test_creates_and_retrieves_tag() -> None:
    with running_service() as (host, port):
        payload = {
            "track_id": "eden-001",
            "emotion": "serenity",
            "intensity": 0.75,
            "notes": "For twilight rituals",
        }
        status, body = _request(host, port, "POST", "/tags", body=payload)
        assert status == 201
        assert body["track_id"] == "eden-001"
        assert body["emotion"] == "serenity"
        assert body["intensity"] == pytest.approx(0.75)
        assert body["notes"] == "For twilight rituals"
        assert "id" in body

        tag_id = body["id"]
        status, retrieved = _request(host, port, "GET", f"/tags/{tag_id}")
        assert status == 200
        assert retrieved == body


def test_reuses_provided_identifier() -> None:
    with running_service() as (host, port):
        payload = {
            "id": "custom-id",
            "track_id": "eden-777",
            "emotion": "euphoria",
        }
        status, body = _request(host, port, "POST", "/tags", body=payload)
        assert status == 201
        assert body["id"] == "custom-id"


def test_accepts_optional_metadata_fields() -> None:
    with running_service() as (host, port):
        payload = {
            "track_id": "   eden-002   ",
            "emotion": " wonder ",
            "user_id": " listener-9 ",
            "notes": "  whispered through static  ",
        }
        status, body = _request(host, port, "POST", "/tags", body=payload)
        assert status == 201
        assert body["track_id"] == "eden-002"
        assert body["emotion"] == "wonder"
        assert body["user_id"] == "listener-9"
        assert body["notes"] == "whispered through static"


def test_unknown_endpoint_returns_404() -> None:
    with running_service() as (host, port):
        status, body = _request(host, port, "GET", "/unknown")
        assert status == 404
        assert "unknown endpoint" in body["error"]
