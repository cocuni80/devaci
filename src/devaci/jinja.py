"""Jinja2 template rendering for devaci."""

from __future__ import annotations

from typing import Any

import jinja2

from devaci.exceptions import JinjaError
from devaci.filters import load_yaml, nan_filter, range_filter, str_to_bool


class JinjaRenderer:
    """Render a Jinja2 template into a Python dict.

    The rendered output is expected to be YAML whose top-level keys map to
    ACI object types (see :mod:`devaci.cobra`).
    """

    def __init__(self) -> None:
        self._env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            extensions=["jinja2.ext.do"],
        )
        self._env.filters["bool"] = str_to_bool
        self._env.filters["range"] = range_filter
        self._env.filters["nan"] = nan_filter

    def render(self, template: str, name: str | None = None, **variables: Any) -> dict[str, Any]:
        """Render ``template`` with ``variables`` and parse the YAML output."""
        try:
            rendered = self._env.from_string(template).render(**variables)
        except Exception as exc:
            line = getattr(exc, "lineno", None)
            raise JinjaError(f"[Jinja] -> [{type(exc).__name__}]: {exc}. Line: {line}") from exc

        output = load_yaml(rendered)
        if not isinstance(output, dict):
            raise JinjaError(
                f"[Jinja] -> [ConfigError]: Template {name} did not produce a mapping."
            )
        return output
