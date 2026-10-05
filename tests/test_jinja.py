import pytest

from devaci.exceptions import JinjaError
from devaci.jinja import JinjaRenderer


def test_render_mapping():
    renderer = JinjaRenderer()
    out = renderer.render("fvTenant:\n  - name: acme\n", name="t.j2")
    assert out == {"fvTenant": [{"name": "acme"}]}


def test_render_with_variables():
    renderer = JinjaRenderer()
    out = renderer.render("fvTenant:\n  - name: {{ tenant }}\n", name="t.j2", tenant="acme")
    assert out == {"fvTenant": [{"name": "acme"}]}


def test_render_syntax_error():
    renderer = JinjaRenderer()
    with pytest.raises(JinjaError):
        renderer.render("{% if %}", name="t.j2")


def test_render_non_mapping():
    renderer = JinjaRenderer()
    with pytest.raises(JinjaError):
        renderer.render("- a\n- b\n", name="t.j2")
