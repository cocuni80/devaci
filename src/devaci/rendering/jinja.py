"""Jinja2 template rendering for devaci."""

from __future__ import annotations

from typing import Any

import jinja2

from devaci.exceptions import JinjaError
from devaci.rendering.filters import nan_filter, range_filter, str_to_bool
from devaci.rendering.yaml_loader import load_yaml


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

    @property
    def env(self) -> jinja2.Environment:
        """Return the underlying Jinja environment (for extra filter registration)."""
        return self._env

    def compile(self, template: str) -> jinja2.Template:
        """Compile ``template`` once so it can be rendered many times."""
        try:
            return self._env.from_string(template)
        except Exception as exc:
            line = getattr(exc, "lineno", None)
            location = f" at line {line}" if line is not None else ""
            raise JinjaError(f"failed to compile template{location}: {exc}") from exc

    def render_template(self, template: jinja2.Template, **variables: Any) -> dict[str, Any]:
        """Render a compiled ``template`` with ``variables`` and parse the YAML output."""
        try:
            rendered = template.render(**variables)
            output = load_yaml(rendered)
        except Exception as exc:
            line = getattr(exc, "lineno", None)
            location = f" at line {line}" if line is not None else ""
            raise JinjaError(f"failed to render template{location}: {exc}") from exc
        if not isinstance(output, dict):
            raise JinjaError("template did not produce a mapping")
        return output

    def render(self, template: str, **variables: Any) -> dict[str, Any]:
        """Render ``template`` with ``variables`` and parse the YAML output."""
        return self.render_template(self.compile(template), **variables)
