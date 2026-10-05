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
