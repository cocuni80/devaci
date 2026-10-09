"""Tabular input loading (CSV/XLSX), filtering, and template variables."""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

import pandas as pd

from devaci.console import get_logger
from devaci.exceptions import DataError

logger = get_logger(__name__)


def apply_filter(
    df: pd.DataFrame,
    column: str,
    filters: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    """Filter a DataFrame by ``column`` and return a list of records.

    When no ``filters`` are given, or the column is missing, all records are
    returned. Empty and ``nan`` values are always excluded from filtering.
    """
    if not filters or not column or column not in df.columns:
        if not filters:
            return cast("list[dict[str, Any]]", df.to_dict("records"))
        return []

    series = df[column]
    return cast(
        "list[dict[str, Any]]",
        df[series.notna() & series.astype(str).str.strip().ne("") & series.isin(filters)].to_dict(
            orient="records"
        ),
    )


def load_csv(
    path: str | Path,
    filters: Sequence[str] | None = None,
    by: str = "tag",
) -> dict[str, list[dict[str, Any]]]:
    """Load a CSV file into ``{filename: [records]}``."""
    path = Path(path)
    df = pd.read_csv(path)
    return {path.stem: apply_filter(df, by, filters)}


def load_xlsx(
    path: str | Path,
    filters: Sequence[str] | None = None,
    by: str = "tag",
    filters_source_sheet: str | None = None,
    filters_condition_field: str = "enabled",
    filters_output_field: str = "name",
) -> dict[str, list[dict[str, Any]]]:
    """Load an XLSX workbook into ``{sheet_name: [records]}``.

    Optionally derives the filter values from a dedicated sheet
    (``filters_source_sheet``) using a boolean condition column.
    """
    path = Path(path)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Data Validation extension is not supported*",
            category=UserWarning,
        )
        sheets = pd.read_excel(path, sheet_name=None)

    resolved_filters = filters
    if filters_source_sheet:
        df_filters = sheets.get(filters_source_sheet)
        if df_filters is None:
            raise DataError(f"Sheet '{filters_source_sheet}' does not exist in '{path}'!")
        resolved_filters = df_filters.loc[
            df_filters[filters_condition_field], filters_output_field
        ].tolist()

    return {name: apply_filter(df, by, resolved_filters) for name, df in sheets.items()}


class DataLoader:
    """Loads CSV/XLSX sheets into the template variable namespace."""

    def __init__(
        self,
        working_folder: Path,
        filters: Sequence[str] | None = None,
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

    @staticmethod
    def _as_files(value: Any) -> list[Any]:
        """Normalise a filename (or list of filenames) into a list.

        Raises:
            TypeError: when ``value`` is neither a string nor a list/tuple.
        """
        if isinstance(value, str):
            return [value]
        if isinstance(value, (list, tuple)):
            return list(value)
        raise TypeError(f"Expected a filename or a list of filenames, got {type(value).__name__}.")

    def add_csv(self, value: Any) -> None:
        """Merge CSV sheet(s) into the variables dict."""
        for file in self._as_files(value):
            try:
                self._variables |= load_csv(self._working_folder / file, self._filters, self._by)
            except Exception:
                logger.exception("Error loading CSV file %r.", file)

    def add_xlsx(self, value: Any) -> None:
        """Merge XLSX sheet(s) into the variables dict."""
        for file in self._as_files(value):
            try:
                self._variables |= load_xlsx(
                    self._working_folder / file,
                    self._filters,
                    self._by,
                    self._source_sheet,
                    self._condition_field,
                    self._output_field,
                )
            except Exception:
                logger.exception("Error loading XLSX file %r.", file)
