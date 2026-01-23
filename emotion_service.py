"""Simple REST service for storing and retrieving emotion tags."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid

TAGS: dict[str, dict] = {}

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
            tag = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, status=400)
            return

        if "track_id" not in tag or "emotion" not in tag:
            self._send_json({"error": "missing required fields"}, status=400)
            return

        tag_id = tag.get("id") or str(uuid.uuid4())
        tag["id"] = tag_id
        TAGS[tag_id] = tag
        self._send_json(tag, status=201)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the emotion tag service."""
    server = HTTPServer((host, port), EmotionTagHandler)
    print(f"Emotion tag service running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":  # pragma: no cover
    run()
