"""Client helper to interact with the emotion tag service.
This module now re-exports the shared client implementation so EchoPlay and
other tools stay in sync on connection handling and base URL configuration.
"""
from importlib import util as _import_util

if _import_util.find_spec("emotion_tags_client") is not None:
    from emotion_tags_client import create_tag, get_tag, get_tags, resolve_base_url
else:
    from ._emotion_tags_client import create_tag, get_tag, get_tags, resolve_base_url

__all__ = ["get_tags", "get_tag", "create_tag", "resolve_base_url"]
