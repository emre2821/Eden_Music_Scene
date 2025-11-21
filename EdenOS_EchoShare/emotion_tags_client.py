"""Client helper to interact with the emotion tag service.

Re-exporting the shared client keeps EdenOS EchoShare aligned with the
connection handling used elsewhere in the stack.
"""

from emotion_tags_client import create_tag, get_tag, get_tags, resolve_base_url

__all__ = ["get_tags", "get_tag", "create_tag", "resolve_base_url"]
