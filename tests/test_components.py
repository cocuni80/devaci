import json
from pathlib import Path

import pandas as pd

from devaci.inputs import DataLoader, TemplateSource
from devaci.output import OutputWriter
from devaci.runlog import RunLog


def test_template_source_in_memory():
    source = TemplateSource(Path.cwd())
    source.add(("fvTenant:\n  - name: acme\n", "tenant.j2"))
    assert source.templates == [("fvTenant:\n  - name: acme\n", Path("tenant.j2"))]


def test_template_source_from_file(tmp_path):
    (tmp_path / "tenant.j2").write_text("fvTenant:\n  - name: acme\n", encoding="utf-8")
    source = TemplateSource(tmp_path)
    source.add("tenant.j2")
    assert source.templates[0][0] == "fvTenant:\n  - name: acme\n"


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


def test_output_writer_saves_json(tmp_path):
    OutputWriter(tmp_path, render_to_xml=False).save({"a": 1}, "out")
    assert json.loads((tmp_path / "out.json").read_text(encoding="utf-8")) == {"a": 1}


def test_output_writer_saves_xml(tmp_path):
    OutputWriter(tmp_path, render_to_xml=True).save("<config/>", "out")
    assert (tmp_path / "out.xml").exists()


def test_output_writer_skips_none(tmp_path):
    OutputWriter(tmp_path).save(None, "out")
    assert not list(tmp_path.iterdir())


def test_runlog_appends_history(tmp_path):
    runlog = RunLog(tmp_path, "outputs/logs/logging", enabled=True)
    runlog.save([{"a": 1}])
    runlog.save([{"b": 2}])
    log = json.loads((tmp_path / "outputs/logs/logging.json").read_text(encoding="utf-8"))
    assert log == [{"a": 1}, {"b": 2}]


def test_runlog_disabled(tmp_path):
    RunLog(tmp_path, "logging", enabled=False).save([{"a": 1}])
    assert not (tmp_path / "logging.json").exists()
