"""Jinja2 filters registered by devaci's renderer."""

from __future__ import annotations

from typing import Any


def split_filter(value: Any, delimiter: str = ",") -> list[str]:
    """Split a value into a list of strings."""
    return str(value).split(delimiter)


def range_filter(value: Any) -> list[int]:
    """Expand a string such as ``1-3,5`` into a list of integers.

    Raises:
        ValueError: when a token is neither an integer nor a ``start-end``
            range, so template errors surface as a clear message.
    """
    result: list[int] = []
    for raw in str(value).split(","):
        part = raw.strip()
        try:
            if "-" in part:
                start, end = part.split("-", 1)
                result.extend(range(int(start), int(end) + 1))
            else:
                result.append(int(part))
        except ValueError as exc:
            raise ValueError(f"Invalid range value: {value!r}") from exc
    return result


def nan_filter(value: Any) -> bool:
    """Return False when the value is the string ``nan``."""
    return str(value) != "nan"


def str_to_bool(value: Any) -> bool:
    """Convert common truthy strings to a boolean."""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "yes", "1")
