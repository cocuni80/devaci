"""Explicit handler registry for Cobra object builders."""

from __future__ import annotations

from collections.abc import Callable

Handler = Callable[..., None]

REGISTRY: dict[str, Handler] = {}


def register(key: str) -> Callable[[Handler], Handler]:
    """Register a builder function under a template/YAML key."""

    def decorator(func: Handler) -> Handler:
        REGISTRY[key] = func
        return func

    return decorator


def get_handler(key: str) -> Handler | None:
    """Return the handler registered under ``key``, or ``None``."""
    return REGISTRY.get(key)
