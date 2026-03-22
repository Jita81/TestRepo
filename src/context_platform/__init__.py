"""Context Engineering Platform — core domain and persistence."""

from src.context_platform.store import ContextStore, get_store, init_store

__all__ = ["ContextStore", "get_store", "init_store"]
