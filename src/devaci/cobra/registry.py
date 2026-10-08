"""Handler registry for Cobra object builders."""

from __future__ import annotations

from collections.abc import Callable, Mapping

Handler = Callable[..., None]


def build_registry(*mappings: Mapping[str, Handler]) -> dict[str, Handler]:
    """Merge handler mappings into one dict, rejecting duplicate ACI keys."""
    registry: dict[str, Handler] = {}
    for mapping in mappings:
        for key, handler in mapping.items():
            if key in registry:
                raise ValueError(f"Duplicate ACI handler key: {key}")
            registry[key] = handler
    return registry
