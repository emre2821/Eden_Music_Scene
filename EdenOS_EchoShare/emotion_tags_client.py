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

This module vendors the shared client helpers so an EdenOS_EchoShare install
does not rely on out-of-package modules being present.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional
from urllib import error, request
from urllib.parse import urljoin

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
_BASE_URL_ENV = "EMOTION_SERVICE_URL"


def resolve_base_url() -> str:
    """Return the configured base URL for the emotion service.

    The environment variable :envvar:`EMOTION_SERVICE_URL` can override the
    default to point at a remote deployment. Trailing slashes are trimmed so
    URL joins remain predictable.
    """

    override = os.getenv(_BASE_URL_ENV)
    if override:
        cleaned = override.strip()
        return cleaned[:-1] if cleaned.endswith("/") else cleaned
    return DEFAULT_BASE_URL


def _build_url(path: str, base_url: Optional[str] = None) -> str:
    base = (base_url or resolve_base_url()).rstrip("/")
    return urljoin(f"{base}/", path.lstrip("/"))


def _request_json(
    path: str, *, base_url: Optional[str] = None, payload: Optional[Dict[str, Any]] = None, timeout: float = 5.0
):
    url = _build_url(path, base_url)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = request.Request(url, data=data, headers=headers)
    try:
        with request.urlopen(req, timeout=timeout) as resp:  # type: ignore[arg-type]
            return json.load(resp)
    except error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise ConnectionError(f"Emotion service returned HTTP {exc.code} for {url}") from exc
    except error.URLError as exc:
        raise ConnectionError(f"Failed to reach emotion service at {url}") from exc


def get_tags(*, base_url: Optional[str] = None, timeout: float = 5.0) -> List[Dict[str, Any]]:
    """Retrieve all emotion tags from the service."""

    result = _request_json("/tags", base_url=base_url, timeout=timeout)
    return list(result or [])


def get_tag(tag_id: str, *, base_url: Optional[str] = None, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    """Retrieve a single tag by its identifier.

    Returns ``None`` when the server responds with HTTP 404.
    """

    return _request_json(f"/tags/{tag_id}", base_url=base_url, timeout=timeout)


def create_tag(tag: Dict[str, Any], *, base_url: Optional[str] = None, timeout: float = 5.0) -> Dict[str, Any]:
    """Create a new emotion tag.

    Parameters
    ----------
    tag: dict
        Dictionary matching the :mod:`emotion_tag_schema.json` structure.
    """

    result = _request_json("/tags", base_url=base_url, payload=tag, timeout=timeout)
    if result is None:
        raise ConnectionError("Emotion service did not return a response for tag creation")
    return result


__all__ = ["get_tags", "get_tag", "create_tag", "resolve_base_url"]
