import pytest

from devaci.exceptions import JinjaError
from devaci.rendering.jinja import JinjaRenderer


def test_render_mapping():
    renderer = JinjaRenderer()
    out = renderer.render("fvTenant:\n  - name: acme\n")
    assert out == {"fvTenant": [{"name": "acme"}]}


def test_render_with_variables():
    renderer = JinjaRenderer()
    out = renderer.render("fvTenant:\n  - name: {{ tenant }}\n", tenant="acme")
    assert out == {"fvTenant": [{"name": "acme"}]}


def test_render_variable_named_name():
    renderer = JinjaRenderer()
    out = renderer.render("fvTenant:\n  - name: {{ name }}\n", name="acme")
    assert out == {"fvTenant": [{"name": "acme"}]}


def test_render_syntax_error():
    renderer = JinjaRenderer()
    with pytest.raises(JinjaError):
        renderer.render("{% if %}")


def test_render_non_mapping():
    renderer = JinjaRenderer()
    with pytest.raises(JinjaError):
        renderer.render("- a\n- b\n")
