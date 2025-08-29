"""Client helper to interact with the emotion tag service."""

import json
from urllib import request

BASE_URL = "http://127.0.0.1:8000"


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

    Returns
    -------
    dict
        The created emotion tag as returned by the service.
    """
    data = json.dumps(tag).encode("utf-8")
    req = request.Request(
        f"{BASE_URL}/tags", data=data, headers={"Content-Type": "application/json"}
    )
    with request.urlopen(req) as resp:
        return json.load(resp)
