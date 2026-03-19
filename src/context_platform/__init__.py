"""Context Engineering Platform — core domain and persistence."""

from src.context_platform.store import ContextStore, init_store, get_store

__all__ = ["ContextStore", "init_store", "get_store"]
