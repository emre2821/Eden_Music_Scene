"""Integration tests for the lightweight emotion tag HTTP service."""

from __future__ import annotations

import http.client
import json
import threading
from contextlib import contextmanager
from http.server import HTTPServer
from pathlib import Path
from typing import Generator

import pytest

from shared.emotion import emotion_service
from shared.emotion.emotion_storage import DatabaseTagStore


@pytest.mark.parametrize("env_value", ["", "   "])
def test_get_store_defaults_for_blank_env(monkeypatch, caplog, env_value):
    monkeypatch.setenv("EMOTION_DB_URL", env_value)
    monkeypatch.setattr(emotion_service, "_STORE", None)

    with caplog.at_level("WARNING"):
        store = emotion_service._get_store()

    try:
        assert "defaulting to SQLite storage" in caplog.text
        assert str(store._engine.url) == "sqlite:///emotion_tags.db"
    finally:
        store.close()
        emotion_service._STORE = None
        default_db = Path("emotion_tags.db")
        if default_db.exists():
            default_db.unlink()


@pytest.fixture
def store(tmp_path) -> Generator[DatabaseTagStore, None, None]:
    database_url = f"sqlite:///{tmp_path/'tags.db'}"
    tag_store = DatabaseTagStore(database_url=database_url)
    emotion_service.configure_store(tag_store)
    tag_store.clear()
    try:
        yield tag_store
    finally:
        tag_store.clear()
        tag_store.close()


@contextmanager
def running_service(store: DatabaseTagStore) -> Generator[tuple[str, int], None, None]:
    """Run the HTTP server in a background thread for the duration of a test."""

    emotion_service.configure_store(store)
    store.clear()
    server = HTTPServer(("127.0.0.1", 0), emotion_service.EmotionTagHandler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield host, port
    finally:
        server.shutdown()
        thread.join(timeout=3)
        store.clear()


def _request(
    host: str, port: int, method: str, path: str, body: object | None = None
) -> tuple[int, dict]:
    payload: bytes | None = None
    headers = {}
    if body is not None:
        payload = (
            json.dumps(body).encode("utf-8") if not isinstance(body, bytes) else body
        )
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


def test_get_tags_initially_empty(store: DatabaseTagStore) -> None:
    with running_service(store) as (host, port):
        status, payload = _request(host, port, "GET", "/tags")
        assert status == 200
        assert payload == []


def test_rejects_invalid_json(store: DatabaseTagStore) -> None:
    with running_service(store) as (host, port):
        conn = http.client.HTTPConnection(host, port, timeout=5)
        conn.request(
            "POST", "/tags", body=b"{", headers={"Content-Type": "application/json"}
        )
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
        (
            {"track_id": "abc", "emotion": "joy", "intensity": 4},
            "intensity must be between 0 and 1",
        ),
        (
            {"track_id": "abc", "emotion": "joy", "intensity": "high"},
            "intensity must be a number",
        ),
        (
            {"track_id": "abc", "emotion": "joy", "intensity": True},
            "intensity must be a number",
        ),
    ],
)
def test_rejects_invalid_payloads(
    payload: dict, expected_message: str, store: DatabaseTagStore
) -> None:
    with running_service(store) as (host, port):
        status, body = _request(host, port, "POST", "/tags", body=payload)
        assert status == 400
        assert expected_message in body["error"]


def test_creates_and_retrieves_tag(store: DatabaseTagStore) -> None:
    with running_service(store) as (host, port):
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


def test_reuses_provided_identifier(store: DatabaseTagStore) -> None:
    with running_service(store) as (host, port):
        payload = {
            "id": "custom-id",
            "track_id": "eden-777",
            "emotion": "euphoria",
        }
        status, body = _request(host, port, "POST", "/tags", body=payload)
        assert status == 201
        assert body["id"] == "custom-id"


def test_accepts_optional_metadata_fields(store: DatabaseTagStore) -> None:
    with running_service(store) as (host, port):
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


def test_unknown_endpoint_returns_404(store: DatabaseTagStore) -> None:
    with running_service(store) as (host, port):
        status, body = _request(host, port, "GET", "/unknown")
        assert status == 404
        assert "unknown endpoint" in body["error"]
