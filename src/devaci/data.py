"""Input data loading (xlsx/csv) and filtering for devaci."""

from __future__ import annotations

import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

import pandas as pd

from devaci.exceptions import DataError


def apply_filter(
    df: pd.DataFrame,
    column: str,
    filters: Iterable[str] | None = None,
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
    filters: Iterable[str] | None = None,
    by: str = "tag",
) -> dict[str, list[dict[str, Any]]]:
    """Load a CSV file into ``{filename: [records]}``."""
    path = Path(path)
    df = pd.read_csv(path)
    return {path.stem: apply_filter(df, by, filters)}


def load_xlsx(
    path: str | Path,
    filters: Iterable[str] | None = None,
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
