"""Simple REST service for storing and retrieving emotion tags."""

from __future__ import annotations

import json
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict


ALLOWED_FIELDS = {"id", "track_id", "user_id", "emotion", "intensity", "notes"}
TAGS: Dict[str, Dict[str, Any]] = {}


def _validate_tag_payload(tag: Any) -> Dict[str, Any]:
    """Validate an incoming tag payload against the supported schema."""

    if not isinstance(tag, dict):
        raise ValueError("payload must be a JSON object")

    unknown = set(tag) - ALLOWED_FIELDS
    if unknown:
        raise ValueError(f"unexpected field(s): {', '.join(sorted(unknown))}")

    if "track_id" not in tag or "emotion" not in tag:
        raise ValueError("missing required fields: track_id and emotion")

    cleaned: Dict[str, Any] = {}

    def _require_string(field: str) -> None:
        value = tag[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        cleaned[field] = value.strip()

    _require_string("track_id")
    _require_string("emotion")

    if "id" in tag:
        _require_string("id")
    if "user_id" in tag and tag["user_id"] is not None:
        _require_string("user_id")
    if "notes" in tag and tag["notes"] is not None:
        value = tag["notes"]
        if not isinstance(value, str):
            raise ValueError("notes must be a string if provided")
        cleaned["notes"] = value.strip()

    if "intensity" in tag:
        intensity = tag["intensity"]
        if not isinstance(intensity, (int, float)):
            raise ValueError("intensity must be a number between 0 and 1")
        if not 0 <= float(intensity) <= 1:
            raise ValueError("intensity must be between 0 and 1")
        cleaned["intensity"] = float(intensity)

    return cleaned


class EmotionTagHandler(BaseHTTPRequestHandler):
    """HTTP handler that stores and retrieves emotion tags in memory."""

    def _send_json(self, data, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self) -> None:  # pragma: no cover - simple IO
        if self.path == "/tags":
            self._send_json(list(TAGS.values()))
        elif self.path.startswith("/tags/"):
            tag_id = self.path.split("/")[-1]
            tag = TAGS.get(tag_id)
            if tag:
                self._send_json(tag)
            else:
                self._send_json({"error": "not found"}, status=404)
        else:
            self._send_json({"error": "unknown endpoint"}, status=404)

    def do_POST(self) -> None:  # pragma: no cover - simple IO
        if self.path != "/tags":
            self._send_json({"error": "unknown endpoint"}, status=404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            raw_payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, status=400)
            return

        try:
            tag = _validate_tag_payload(raw_payload)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        tag_id = tag.get("id") or str(uuid.uuid4())
        tag["id"] = tag_id
        TAGS[tag_id] = dict(tag)
        self._send_json(tag, status=201)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the emotion tag service."""
    server = HTTPServer((host, port), EmotionTagHandler)
    print(f"Emotion tag service running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":  # pragma: no cover
    run()
