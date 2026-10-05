import pandas as pd
import pytest

from devaci.data import apply_filter, load_csv, load_xlsx
from devaci.exceptions import DataError


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

    assert load_csv(path, filters=["a"], by="tag") == {
        "tenants": [{"tag": "a", "name": "x"}]
    }


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
