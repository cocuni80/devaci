import math

from devaci.filters import (
    load_yaml,
    nan_filter,
    range_filter,
    replace_str_nan_with_empty,
    split_filter,
    str_to_bool,
)


def test_split_filter():
    assert split_filter("a,b,c") == ["a", "b", "c"]


def test_split_filter_custom_delimiter():
    assert split_filter("a;b", delimiter=";") == ["a", "b"]


def test_range_filter():
    assert range_filter("1-3,5") == [1, 2, 3, 5]


def test_range_filter_single():
    assert range_filter("7") == [7]


def test_nan_filter():
    assert nan_filter("nan") is False
    assert nan_filter("value") is True


def test_str_to_bool():
    assert str_to_bool(True) is True
    assert str_to_bool("yes") is True
    assert str_to_bool("1") is True
    assert str_to_bool("false") is False
    assert str_to_bool("0") is False


def test_replace_str_nan_with_empty():
    assert replace_str_nan_with_empty("nan") == ""
    assert replace_str_nan_with_empty(" NaN ") == ""
    assert replace_str_nan_with_empty("value") == "value"
    assert replace_str_nan_with_empty(42) == 42
    assert replace_str_nan_with_empty({"a": "nan", "b": {"c": "NaN"}}) == {
        "a": "",
        "b": {"c": ""},
    }
    assert replace_str_nan_with_empty(["nan", 1, None]) == ["", 1, None]


def test_replace_str_nan_keeps_real_nan():
    assert math.isnan(replace_str_nan_with_empty(float("nan")))


def test_load_yaml_no_coercion():
    result = load_yaml("key: 123\nflag: true\nratio: 1.5\nmissing: nan\n")
    assert result == {"key": "123", "flag": "true", "ratio": "1.5", "missing": ""}


def test_load_yaml_nested():
    result = load_yaml("nested:\n  - 1\n  - false\n")
    assert result == {"nested": ["1", "false"]}
