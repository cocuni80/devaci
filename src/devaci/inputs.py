"""Template and tabular input loading for devaci."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from devaci.console import logger
from devaci.data import load_csv, load_xlsx


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
            except Exception as exc:
                logger.error(f"[TemplateException]: Error loading template: {exc}")


class DataLoader:
    """Loads CSV/XLSX sheets into the template variable namespace."""

    def __init__(
        self,
        working_folder: Path,
        filters: Iterable[str] | None = None,
        by: str = "tag",
        source_sheet: str | None = None,
        condition_field: str = "enabled",
        output_field: str = "name",
    ) -> None:
        self._working_folder = working_folder
        self._filters = filters
        self._by = by
        self._source_sheet = source_sheet
        self._condition_field = condition_field
        self._output_field = output_field
        self._variables: dict[str, Any] = {}

    @property
    def variables(self) -> dict[str, Any]:
        return self._variables

    @variables.setter
    def variables(self, value: dict[str, Any]) -> None:
        self._variables = value

    def add_csv(self, value: Any) -> None:
        """Merge CSV sheet(s) into the variables dict."""
        files = [value] if isinstance(value, str) else value
        for file in files:
            try:
                self._variables |= load_csv(self._working_folder / file, self._filters, self._by)
            except Exception as exc:
                logger.error(f"[CSVException]: Error loading CSV file: {exc}")

    def add_xlsx(self, value: Any) -> None:
        """Merge XLSX sheet(s) into the variables dict."""
        files = [value] if isinstance(value, str) else value
        for file in files:
            try:
                self._variables |= load_xlsx(
                    self._working_folder / file,
                    self._filters,
                    self._by,
                    self._source_sheet,
                    self._condition_field,
                    self._output_field,
                )
            except Exception as exc:
                logger.error(f"[XLSXException]: Error loading XLSX file '{file}': {exc}")
