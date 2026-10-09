import logging

import pandas as pd
import pytest

from devaci.exceptions import DataError
from devaci.inputs.datasets import DataLoader, apply_filter, load_csv, load_xlsx


def _df() -> pd.DataFrame:
    return pd.DataFrame({"tag": ["a", "b", None, ""], "name": ["x", "y", "z", "w"]})


def test_apply_filter_no_filters():
    assert len(apply_filter(_df(), "tag")) == 4


def test_apply_filter_with_filters():
    assert apply_filter(_df(), "tag", ["a"]) == [{"tag": "a", "name": "x"}]


def test_apply_filter_missing_column():
    assert apply_filter(_df(), "missing", ["a"]) == []


def test_apply_filter_empty_filters():
    assert len(apply_filter(_df(), "tag", [])) == 4


def test_load_csv(tmp_path):
    path = tmp_path / "tenants.csv"
    pd.DataFrame({"tag": ["a", "b"], "name": ["x", "y"]}).to_csv(path, index=False)

    assert load_csv(path, filters=["a"], by="tag") == {"tenants": [{"tag": "a", "name": "x"}]}


def test_load_xlsx_with_filters_sheet(tmp_path):
    path = tmp_path / "data.xlsx"
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame({"tag": ["a", "b"], "name": ["x", "y"]}).to_excel(
            writer, sheet_name="tenants", index=False
        )
        pd.DataFrame({"name": ["a"], "enabled": [True]}).to_excel(
            writer, sheet_name="filters", index=False
        )

    result = load_xlsx(path, by="tag", filters_source_sheet="filters")
    assert result["tenants"] == [{"tag": "a", "name": "x"}]


def test_load_xlsx_missing_filters_sheet(tmp_path):
    path = tmp_path / "data.xlsx"
    pd.DataFrame({"tag": ["a"], "name": ["x"]}).to_excel(path, sheet_name="tenants", index=False)

    with pytest.raises(DataError):
        load_xlsx(path, by="tag", filters_source_sheet="nope")


def test_data_loader_csv(tmp_path):
    pd.DataFrame({"tag": ["a"], "name": ["x"]}).to_csv(tmp_path / "d.csv", index=False)

    loader = DataLoader(tmp_path)
    loader.add_csv("d.csv")

    assert loader.variables == {"d": [{"tag": "a", "name": "x"}]}


def test_data_loader_xlsx(tmp_path):
    pd.DataFrame({"tag": ["a"], "name": ["x"]}).to_excel(
        tmp_path / "d.xlsx", sheet_name="tenants", index=False
    )

    loader = DataLoader(tmp_path)
    loader.add_xlsx("d.xlsx")

    assert loader.variables == {"tenants": [{"tag": "a", "name": "x"}]}


def test_data_loader_accepts_list_of_files(tmp_path):
    pd.DataFrame({"tag": ["a"], "name": ["x"]}).to_csv(tmp_path / "one.csv", index=False)
    pd.DataFrame({"tag": ["b"], "name": ["y"]}).to_csv(tmp_path / "two.csv", index=False)

    loader = DataLoader(tmp_path)
    loader.add_csv(["one.csv", "two.csv"])

    assert set(loader.variables) == {"one", "two"}


def test_data_loader_rejects_invalid_type(tmp_path):
    loader = DataLoader(tmp_path)

    with pytest.raises(TypeError, match="Expected a filename"):
        loader.add_csv(123)


def test_data_loader_logs_csv_errors(tmp_path, caplog):
    loader = DataLoader(tmp_path)

    with caplog.at_level(logging.ERROR, logger="devaci"):
        loader.add_csv("missing.csv")

    assert loader.variables == {}
    assert any("Error loading CSV" in record.getMessage() for record in caplog.records)


def test_data_loader_logs_xlsx_errors(tmp_path, caplog):
    loader = DataLoader(tmp_path)

    with caplog.at_level(logging.ERROR, logger="devaci"):
        loader.add_xlsx("missing.xlsx")

    assert loader.variables == {}
    assert any("Error loading XLSX" in record.getMessage() for record in caplog.records)
