"""Client helper to interact with the emotion tag service packaged with EchoShare."""

from __future__ import annotations

import json
import os
from urllib import request

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def resolve_base_url() -> str:
    """Return the service base URL, allowing an environment override.

    The optional ``EMOTION_TAGS_BASE_URL`` environment variable lets callers point
    the client at a non-default service endpoint without editing the code.
    """

    return os.getenv("EMOTION_TAGS_BASE_URL", DEFAULT_BASE_URL)


BASE_URL = resolve_base_url()


def get_tags():
    """Retrieve all emotion tags from the service."""
    with request.urlopen(f"{BASE_URL}/tags") as resp:
        return json.load(resp)


def get_tag(tag_id: str):
    """Retrieve a single tag by its identifier."""
    with request.urlopen(f"{BASE_URL}/tags/{tag_id}") as resp:
        return json.load(resp)


def create_tag(tag: dict):
    """Create a new emotion tag.

    Parameters
    ----------
    tag: dict
        Dictionary matching the emotion_tag_schema.json structure.
    """
    data = json.dumps(tag).encode("utf-8")
    req = request.Request(
        f"{BASE_URL}/tags", data=data, headers={"Content-Type": "application/json"}
    )
    with request.urlopen(req) as resp:
        return json.load(resp)
