from devaci.rendering.sections import split_template

TEMPLATE = (
    "# header comment\n"
    "fvTenant:\n"
    "  - name: {{ fvTenant.name }}\n"
    "\n"
    "fvAp:\n"
    "  - name: {{ fvAp.name }}\n"
)


def test_split_template_sections():
    preamble, sections = split_template(TEMPLATE, {"fvTenant", "fvAp"})

    assert preamble == "# header comment\n"
    assert set(sections) == {"fvTenant", "fvAp"}
    assert sections["fvTenant"] == "fvTenant:\n  - name: {{ fvTenant.name }}\n\n"
    assert sections["fvAp"] == "fvAp:\n  - name: {{ fvAp.name }}\n"


def test_split_template_no_match_returns_original():
    preamble, sections = split_template(TEMPLATE, {"fvBD"})

    assert preamble == TEMPLATE
    assert sections == {}


def test_split_template_ignores_unknown_top_level_keys():
    template = "unknown:\n  - x\n\nfvTenant:\n  - name: acme\n"

    _, sections = split_template(template, {"fvTenant"})

    assert set(sections) == {"fvTenant"}


def test_split_template_does_not_cut_inside_set_block():
    template = '{% set epgs = {\n"Border_AP": [3, 35],\n} %}\nfvRsPathAtt:\n  - tenant: acme\n'

    preamble, sections = split_template(template, {"fvRsPathAtt"})

    assert preamble == '{% set epgs = {\n"Border_AP": [3, 35],\n} %}\n'
    assert set(sections) == {"fvRsPathAtt"}
