"""Internal value predicates shared across devaci layers."""

from __future__ import annotations

from math import isnan
from typing import Any

__all__ = ["is_invalid", "is_nan", "is_nan_text"]


def is_nan_text(value: Any) -> bool:
    """Return True when ``value`` is the text ``nan`` (case-insensitive, stripped)."""
    return isinstance(value, str) and value.strip().lower() == "nan"


def is_nan(value: Any) -> bool:
    """Return True for a float NaN or the text ``nan`` (case-insensitive)."""
    if isinstance(value, float):
        return isnan(value)
    return is_nan_text(value)


def is_invalid(value: Any) -> bool:
    """Return True for None, empty/whitespace strings, text ``nan`` or float NaN."""
    if value is None:
        return True
    if is_nan(value):
        return True
    if isinstance(value, str):
        return not value.strip()
    return False
