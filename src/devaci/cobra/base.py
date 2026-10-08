"""Shared helpers for Cobra object builders."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from math import isnan
from typing import TYPE_CHECKING, Any, Protocol, cast

if TYPE_CHECKING:
    from devaci.cobra import CobraBuilder


class Handler(Protocol):
    """A registered handler for one top-level ACI object key."""

    def __call__(self, builder: CobraBuilder, value: Any) -> None: ...


def _is_invalid(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        value = value.strip()
        return not value or value.lower() == "nan"
    if isinstance(value, float):
        return isnan(value)
    return False


def not_nan_str(value: Mapping[str, Any], keys: Iterable[str]) -> bool:
    """Return True when none of the given keys hold an invalid value.

    A value is considered invalid when it is ``None``, an empty/whitespace
    string, the string ``nan`` (case-insensitive), or a float NaN. Missing
    keys are ignored.
    """
    return not any(_is_invalid(value[k]) for k in keys if k in value)


def _has_objects(config: Any) -> bool:
    return config is not None and bool(config.configMos)


def config_xml(config: Any) -> str | None:
    """Return the XML payload of a ``ConfigRequest``, or None when empty."""
    if not _has_objects(config):
        return None
    return cast("str | None", config.xmldata)


def config_json(config: Any) -> Any:
    """Return the JSON-decoded payload of a ``ConfigRequest``, or None when empty."""
    if not _has_objects(config):
        return None
    return json.loads(config.data)
