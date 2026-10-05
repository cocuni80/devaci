"""Shared helpers for Cobra object builders."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from math import isnan
from typing import Any


def not_nan_str(value: Mapping[str, Any], keys: Iterable[str]) -> bool:
    """Return True when none of the given keys hold an invalid value.

    A value is considered invalid when it is ``None``, an empty/whitespace
    string, the string ``nan`` (case-insensitive), or a float NaN. Missing
    keys are ignored.
    """

    def is_invalid(v: Any) -> bool:
        if v is None:
            return True
        if isinstance(v, str):
            v = v.strip()
            return not v or v.lower() == "nan"
        if isinstance(v, float):
            return isnan(v)
        return False

    return not any(is_invalid(value[k]) for k in keys if k in value)
