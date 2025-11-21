"""Client helper to interact with the emotion tag service.

This module now re-exports the shared client implementation so EchoPlay and
other tools stay in sync on connection handling and base URL configuration.
"""

from emotion_tags_client import create_tag, get_tag, get_tags, resolve_base_url

__all__ = ["get_tags", "get_tag", "create_tag", "resolve_base_url"]
