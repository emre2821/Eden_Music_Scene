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
"""Client helper to interact with the emotion tag service.

Re-exporting the shared client keeps EdenOS EchoShare aligned with the
connection handling used elsewhere in the stack.
"""

from emotion_tags_client import create_tag, get_tag, get_tags, resolve_base_url

__all__ = ["get_tags", "get_tag", "create_tag", "resolve_base_url"]
