import pandas as pd

from devaci import DeployClass


def test_deploy_in_memory_template(tmp_path):
    aci = DeployClass(testing=True, working_folder=tmp_path, logging=False)
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()

    assert "acme" in aci.config
    assert aci.results[0]["success"] is True


def test_deploy_from_xlsx(tmp_path):
    pd.DataFrame([{"name": "acme"}, {"name": "beta"}]).to_excel(
        tmp_path / "data.xlsx", sheet_name="tenants", index=False
    )

    aci = DeployClass(testing=True, working_folder=tmp_path, logging=False)
    aci.xlsx = "data.xlsx"
    aci.template = (
        "fvTenant:\n{% for row in tenants %}\n  - name: {{ row.name }}\n{% endfor %}\n",
        "tenant.j2",
    )
    aci.deploy()

    config = aci.config
    assert "acme" in config
    assert "beta" in config


def test_deploy_multiple_templates(tmp_path):
    aci = DeployClass(testing=True, working_folder=tmp_path, logging=False)
    aci.template = [
        ("fvTenant:\n  - name: one\n", "one.j2"),
        ("fvTenant:\n  - name: two\n", "two.j2"),
    ]
    aci.deploy()

    assert len(aci.results) == 2
    assert all(result["success"] for result in aci.results)


def test_deploy_template_from_file(tmp_path):
    (tmp_path / "tenant.j2").write_text("fvTenant:\n  - name: acme\n", encoding="utf-8")

    aci = DeployClass(testing=True, working_folder=tmp_path, logging=False)
    aci.template = "tenant.j2"
    aci.deploy()

    assert "acme" in aci.config


def test_deploy_from_csv(tmp_path):
    pd.DataFrame({"tag": ["a", "b"], "name": ["acme", "beta"]}).to_csv(
        tmp_path / "tenants.csv", index=False
    )

    aci = DeployClass(testing=True, working_folder=tmp_path, logging=False)
    aci.csv = "tenants.csv"
    aci.template = (
        "fvTenant:\n{% for row in tenants %}\n  - name: {{ row.name }}\n{% endfor %}\n",
        "tenant.j2",
    )
    aci.deploy()

    config = aci.config
    assert "acme" in config
    assert "beta" in config


def test_deploy_save_output(tmp_path):
    aci = DeployClass(
        testing=True,
        working_folder=tmp_path,
        logging=False,
        file_output="scripts/config",
    )
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()

    output = tmp_path / "scripts" / "config.xml"
    assert output.exists()
    assert "acme" in output.read_text(encoding="utf-8")


def test_deploy_variable_named_name(tmp_path):
    aci = DeployClass(testing=True, working_folder=tmp_path, logging=False)
    aci.variables = {"name": "test", "descr": "Test tenant"}
    aci.template = (
        "fvTenant:\n  - name: {{ name }}\n    descr: {{ descr }}\n",
        "tenant.j2",
    )
    aci.deploy()

    assert aci.results[0]["success"] is True
    assert "test" in aci.config
