import pytest

from devaci._values import is_empty, normalize
from devaci.cobra import CobraBuilder
from devaci.exceptions import DataError
from devaci.rendering.jinja import JinjaRenderer
from devaci.schema.engine import SchemaEngine
from devaci.schema.loader import SchemaLoader, resolve_class
from devaci.schema.spec import ParentRef

SCHEMA = """
uni: {class: pol.Uni}
fvTenant:
  class: fv.Tenant
  parent: uni
  requires: {name: "{{ name }}"}
  as_parent: {name: "{{ tenant }}"}
fvAp:
  class: fv.Ap
  parent: fvTenant
  requires: {name: "{{ name }}"}
  as_parent: {name: "{{ ap }}"}
fvAEPg:
  class: fv.AEPg
  parent: fvAp
  requires: {name: "{{ name }}"}
  children:
    fvRsBd:
      class: fv.RsBd
      requires: {tnFvBDName: "{{ bd }}"}
    fvRsDomAtt:
      class: fv.RsDomAtt
      when: "{{ phy }}"
      props: {tDn: "uni/phys-{{ phy }}"}
"""


def run(schema_text, sheets, variables=None):
    schema = SchemaLoader().load(schema_text)
    builder = CobraBuilder()
    logs = SchemaEngine(schema, variables or {}, JinjaRenderer()).run(builder, sheets)
    return builder, logs


def test_resolve_class():
    assert resolve_class("pol.Uni").__name__ == "Uni"
    with pytest.raises(DataError):
        resolve_class("nope.Nope")
    with pytest.raises(DataError):
        resolve_class("bad")


def test_load_parses_dsl():
    schema = SchemaLoader().load(
        """
uni: {class: pol.Uni}
fvAEPg:
  class: fv.AEPg
  parent: {ref: fvTenant, as_parent: {name: "{{ tenant }}"}}
  requires: {name: "{{ name }}"}
  props: {descr: "{{ descr }}"}
  when: "{{ descr }}"
  list: {from: vlans, split: ",", range: true, bind: vlan}
  children:
    - class: fv.RsBd
      requires: {tnFvBDName: "{{ bd }}"}
"""
    )
    node = schema.nodes["fvAEPg"]
    assert isinstance(node.parent, ParentRef)
    assert node.parent.ref == "fvTenant"
    assert node.requires == {"name": "{{ name }}"}
    assert node.props == {"descr": "{{ descr }}"}
    assert node.when == "{{ descr }}"
    assert node.list is not None and node.list.bind == "vlan" and node.list.expand is True
    assert node.children[0].cls_path == "fv.RsBd"


def test_load_rejects_bad_schema():
    with pytest.raises(DataError):
        SchemaLoader().load("fvTenant: not-a-map\n")
    with pytest.raises(DataError):
        SchemaLoader().load("fvTenant: {requires: {name: x}}\n")


def test_engine_builds_parent_chain_and_children():
    builder, logs = run(
        SCHEMA,
        {
            "fvTenant": [{"name": "TN"}],
            "fvAp": [{"name": "AP1", "tenant": "TN"}],
            "fvAEPg": [
                {
                    "name": "v1_EPG",
                    "tenant": "TN",
                    "ap": "AP1",
                    "bd": "BD1",
                    "phy": "Dom1",
                }
            ],
        },
    )
    xml = builder.xml or ""
    assert "name='TN'" in xml
    assert "name='AP1'" in xml
    assert "name='v1_EPG'" in xml
    assert "tnFvBDName='BD1'" in xml
    assert "uni/phys-Dom1" in xml
    assert logs[-1]["objects"] == 3


def test_engine_when_false_skips_child():
    builder, _ = run(
        SCHEMA,
        {"fvAEPg": [{"name": "e", "tenant": "T", "ap": "A", "bd": "B", "phy": ""}]},
    )
    assert "RsDomAtt" not in (builder.xml or "")
    assert "RsBd" in (builder.xml or "")


def test_engine_gate_skips_node_without_required_value():
    builder, logs = run(
        SCHEMA,
        {"fvAEPg": [{"name": "", "tenant": "T", "ap": "A", "bd": "B", "phy": "P"}]},
    )
    assert builder.xml is None
    assert all(event["level"] != "info" for event in logs)


def test_engine_autopass_keeps_empty_non_required_props():
    builder, _ = run(
        SCHEMA,
        {"fvAEPg": [{"name": "e", "tenant": "T", "ap": "A", "bd": "B", "descr": float("nan")}]},
    )
    assert "descr=''" in (builder.xml or "")


def test_engine_parent_ref_override():
    schema = """
uni: {class: pol.Uni}
fvTenant:
  class: fv.Tenant
  parent: uni
  requires: {name: "{{ name }}"}
  as_parent: {name: "{{ tenant }}"}
fvAp:
  class: fv.Ap
  parent: fvTenant
  requires: {name: "{{ name }}"}
  as_parent: {name: "{{ ap }}"}
fvAEPg:
  class: fv.AEPg
  parent: fvAp
  requires: {name: "{{ name }}"}
  as_parent: {name: "v{{ vlan }}_EPG"}
fvRsPathAtt:
  class: fv.RsPathAtt
  parent: {ref: fvAEPg, as_parent: {name: "v{{ vlan }}_EPG"}}
  list: {from: vlans, split: ",", range: true, bind: vlan}
  requires: {tDn: "topology/pod-{{ pod }}/protpaths-{{ leaf }}/pathep-[{{ port }}]"}
  props: {encap: "vlan-{{ vlan }}", mode: "{{ {'trunk': 'regular'}.get(mode, '') }}"}
"""
    builder, logs = run(
        schema,
        {
            "fvRsPathAtt": [
                {
                    "tenant": "TN",
                    "ap": "AP1",
                    "vlans": "3,35",
                    "type": "bundle",
                    "pod": 1,
                    "leaf": "101-102",
                    "port": "PC1",
                    "mode": "trunk",
                }
            ]
        },
    )
    xml = builder.xml or ""
    assert xml.count("<fvRsPathAtt ") == 2
    assert "encap='vlan-3'" in xml
    assert "encap='vlan-35'" in xml
    assert "mode='regular'" in xml
    assert "topology/pod-1/protpaths-101-102/pathep-[PC1]" in xml
    assert logs[-1]["objects"] == 2


def test_engine_list_from_expression():
    builder, _ = run(
        "uni: {class: pol.Uni}\n"
        "infraInfra: {class: infra.Infra, parent: uni}\n"
        "fvnsVlanInstP:\n"
        "  class: fvns.VlanInstP\n"
        "  parent: infraInfra\n"
        "  requires: {name: \"{{ name }}\"}\n"
        "  children:\n"
        "    fvnsEncapBlk:\n"
        "      class: fvns.EncapBlk\n"
        "      list: {from: \"{{ first }}-{{ last }}\", range: true, bind: vlan}\n"
        "      props: {from_: \"vlan-{{ vlan }}\", to: \"vlan-{{ vlan }}\"}\n",
        {"fvnsVlanInstP": [{"name": "pool", "allocMode": "static", "first": 10, "last": 12}]},
    )
    xml = builder.xml or ""
    assert xml.count("<fvnsEncapBlk ") == 3
    assert "from='vlan-12'" in xml


def test_engine_emit_parents():
    schema = (
        "uni: {class: pol.Uni}\n"
        "fvTenant:\n  class: fv.Tenant\n  parent: uni\n  requires: {name: \"{{ name }}\"}\n"
        "  as_parent: {name: \"{{ tenant }}\"}\n"
        "fvAp:\n  class: fv.Ap\n  parent: fvTenant\n  requires: {name: \"{{ name }}\"}\n"
        "  as_parent: {name: \"{{ ap }}\"}\n"
        "fvAEPg:\n  class: fv.AEPg\n  parent: fvAp\n  requires: {name: \"{{ name }}\"}\n"
        "  as_parent: {name: \"v{{ vlan }}_EPG\"}\n"
        "fvRsPathAtt:\n  class: fv.RsPathAtt\n"
        "  parent: {ref: fvAEPg, as_parent: {name: \"v{{ vlan }}_EPG\"}}\n"
        "  list: {from: vlans, range: true, bind: vlan}\n"
        "  requires: {tDn: x}\n"
        "  emit_parents: true\n"
    )
    with_parents, _ = run(schema, {"fvRsPathAtt": [{"tenant": "T", "ap": "A", "vlans": "5"}]})
    assert "name='A'" in (with_parents.xml or "")
    without_parents, _ = run(
        schema.replace("  emit_parents: true\n", ""),
        {"fvRsPathAtt": [{"tenant": "T", "ap": "A", "vlans": "5"}]},
    )
    assert "name='A'" not in (without_parents.xml or "")
    assert "<fvRsPathAtt " in (without_parents.xml or "")


def test_is_empty_and_normalize():
    assert is_empty(None)
    assert is_empty("")
    assert is_empty("   ")
    assert is_empty("nan")
    assert is_empty("None")
    assert is_empty(float("nan"))
    assert not is_empty("x")
    assert normalize(None) == ""
    assert normalize(float("nan")) == ""
    assert normalize("nan") == ""
    assert normalize("  ") == "  "
    assert normalize("x") == "x"
