import cobra.mit.request
import cobra.model.coop
import pytest

from devaci.cobra import CobraBuilder
from devaci.cobra.base import not_nan_str
from devaci.cobra.builders import BUILDERS
from devaci.cobra.registry import build_registry


def test_cobra_model_coop_available():
    assert hasattr(cobra.model.coop, "Pol")


def test_cobra_mit_request_available():
    assert hasattr(cobra.mit.request, "ConfigRequest")


def test_not_nan_str():
    assert not_nan_str({"name": "ok"}, ["name"]) is True
    assert not_nan_str({"name": None}, ["name"]) is False
    assert not_nan_str({"name": ""}, ["name"]) is False
    assert not_nan_str({"name": "  "}, ["name"]) is False
    assert not_nan_str({"name": "nan"}, ["name"]) is False
    assert not_nan_str({"name": " NaN "}, ["name"]) is False
    assert not_nan_str({"name": float("nan")}, ["name"]) is False
    assert not_nan_str({}, ["name"]) is True
    assert not_nan_str({"other": "x"}, ["name"]) is True


def test_cobra_builder_renders_tenant():
    builder = CobraBuilder()
    result = builder.render({"fvTenant": [{"name": "acme"}]})
    assert result.success is True
    assert builder.xml is not None
    assert "acme" in builder.xml


def test_cobra_builder_unknown_key():
    builder = CobraBuilder()
    result = builder.render({"unknownKey": [{"x": 1}]})
    assert result.success is False
    assert any("does not exist" in msg for msg in result.log)


def test_cobra_builder_empty_output():
    builder = CobraBuilder()
    result = builder.render({})
    assert result.success is False
    assert any("No object was found" in msg for msg in result.log)


def test_cobra_builder_skips_empty_values():
    builder = CobraBuilder()
    result = builder.render({"fvTenant": []})
    assert result.success is False


def _noop(*args, **kwargs):
    return None


def test_builders_mapping():
    assert "fvTenant" in BUILDERS
    assert all(callable(handler) for handler in BUILDERS.values())


def test_build_registry_rejects_duplicates():
    with pytest.raises(ValueError):
        build_registry({"dup": _noop}, {"dup": _noop})
