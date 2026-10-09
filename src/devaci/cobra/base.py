"""Shared helpers for Cobra object builders."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, Protocol, cast

from devaci._values import is_invalid

if TYPE_CHECKING:
    from devaci.cobra import CobraBuilder


class Handler(Protocol):
    """A registered handler for one top-level ACI object key."""

    def __call__(self, builder: CobraBuilder, value: Any) -> None: ...


def not_nan_str(value: Mapping[str, Any], keys: Iterable[str]) -> bool:
    """Return True when none of the given keys hold an invalid value.

    A value is considered invalid when it is ``None``, an empty/whitespace
    string, the string ``nan`` (case-insensitive), or a float NaN. Missing
    keys are ignored.
    """
    return not any(is_invalid(value[k]) for k in keys if k in value)


def _has_objects(config: Any) -> bool:
    return config is not None and bool(config.configMos)


def config_xml(config: Any) -> str | None:
    """Return the XML payload of a ``ConfigRequest``, or None when empty."""
    if not _has_objects(config):
        return None
    return cast("str | None", config.xmldata)


def config_json(config: Any) -> dict[str, Any] | None:
    """Return the JSON-decoded payload of a ``ConfigRequest``, or None when empty."""
    if not _has_objects(config):
        return None
    return cast("dict[str, Any]", json.loads(config.data))
