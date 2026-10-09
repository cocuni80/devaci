"""Jinja template loading for devaci."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from devaci.console import get_logger

logger = get_logger(__name__)


class TemplateSource:
    """Loads Jinja templates into in-memory ``(content, path)`` pairs."""

    def __init__(self, working_folder: Path) -> None:
        self._working_folder = working_folder
        self._templates: list[tuple[str, Path]] = []

    @property
    def templates(self) -> list[tuple[str, Path]]:
        return self._templates

    def add(self, value: Any) -> None:
        """Append templates from a filename, list, or in-memory tuple(s).

        Accepted inputs:
        - str: template filename (loaded from ``working_folder``)
        - list[str]: multiple template filenames
        - tuple[str, str]: (template_content, template_name)
        - list[tuple[str, str]]: multiple in-memory templates
        """
        if not value:
            return

        values = value if isinstance(value, list) else [value]
        for item in values:
            try:
                if isinstance(item, tuple) and len(item) == 2:
                    content, name = item
                    if not isinstance(content, str) or not isinstance(name, str):
                        raise ValueError("Template content and name must be strings")
                    self._templates.append((content, Path(name)))
                elif isinstance(item, str):
                    path = self._working_folder / item
                    with open(path, encoding="utf-8") as handle:
                        self._templates.append((handle.read(), path))
                else:
                    raise ValueError("Invalid template format")
            except Exception:
                logger.exception("Error loading template %r.", item)
