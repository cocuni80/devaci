from pathlib import Path

from devaci.inputs.templates import TemplateSource


def test_template_source_in_memory():
    source = TemplateSource(Path.cwd())
    source.add(("fvTenant:\n  - name: acme\n", "tenant.j2"))
    assert source.templates == [("fvTenant:\n  - name: acme\n", Path("tenant.j2"))]


def test_template_source_from_file(tmp_path):
    (tmp_path / "tenant.j2").write_text("fvTenant:\n  - name: acme\n", encoding="utf-8")
    source = TemplateSource(tmp_path)
    source.add("tenant.j2")
    assert source.templates[0][0] == "fvTenant:\n  - name: acme\n"


def test_template_source_multiple_in_memory():
    source = TemplateSource(Path.cwd())
    source.add(
        [
            ("fvTenant:\n  - name: one\n", "one.j2"),
            ("fvTenant:\n  - name: two\n", "two.j2"),
        ]
    )
    assert [path.name for _, path in source.templates] == ["one.j2", "two.j2"]


def test_template_source_empty_is_noop():
    source = TemplateSource(Path.cwd())
    source.add(None)
    assert source.templates == []
