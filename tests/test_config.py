from pathlib import Path

import pandas as pd
import pytest

from devaci import DeployClass, DeployConfig


def test_config_defaults():
    config = DeployConfig()
    assert config.testing is False
    assert config.timeout == 180
    assert config.secure is False
    assert config.timer == 5
    assert config.filter_by == "tag"
    assert config.logging is True
    assert config.logging_output == "outputs/logs/logging.json"
    assert config.render_to_xml is True
    assert config.working_folder == Path.cwd()


def test_config_from_kwargs():
    config = DeployConfig.from_kwargs(testing=True, ip="10.0.0.1", timeout=30, filter_by="name")
    assert config.testing is True
    assert config.ip == "10.0.0.1"
    assert config.timeout == 30
    assert config.filter_by == "name"


def test_config_from_kwargs_ignores_unknown():
    config = DeployConfig.from_kwargs(testing=True, workign_folder=Path("/tmp"))
    assert config.testing is True
    assert config.working_folder == Path.cwd()


def test_deploy_accepts_config():
    aci = DeployClass(config=DeployConfig(testing=True, logging=False))
    assert aci.variables == {}


def test_deploy_rejects_config_and_kwargs():
    with pytest.raises(TypeError):
        DeployClass(DeployConfig(testing=True), testing=True)


def test_deploy_kwargs_backcompat(tmp_path):
    (tmp_path / "schema.j2").write_text(
        "uni:\n  class: pol.Uni\n"
        "fvTenant:\n  class: fv.Tenant\n  parent: uni\n"
        '  requires: {name: "{{ name }}"}\n',
        encoding="utf-8",
    )
    pd.DataFrame([{"name": "acme"}]).to_excel(
        tmp_path / "data.xlsx", sheet_name="fvTenant", index=False
    )

    aci = DeployClass(testing=True, working_folder=tmp_path, logging=False)
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    assert aci.results[0]["success"] is True
