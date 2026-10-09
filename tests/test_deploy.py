import pandas as pd

from devaci import DeployClass


def test_deploy_in_memory_template(deploy, tenant_template):
    aci = deploy()
    aci.template = tenant_template
    aci.deploy()

    assert "acme" in aci.config
    assert aci.results[0]["success"] is True


def test_deploy_from_xlsx(deploy, tmp_path):
    pd.DataFrame([{"name": "acme"}, {"name": "beta"}]).to_excel(
        tmp_path / "data.xlsx", sheet_name="tenants", index=False
    )

    aci = deploy()
    aci.xlsx = "data.xlsx"
    aci.template = (
        "fvTenant:\n{% for row in tenants %}\n  - name: {{ row.name }}\n{% endfor %}\n",
        "tenant.j2",
    )
    aci.deploy()

    config = aci.config
    assert "acme" in config
    assert "beta" in config


def test_deploy_multiple_templates(deploy):
    aci = deploy()
    aci.template = [
        ("fvTenant:\n  - name: one\n", "one.j2"),
        ("fvTenant:\n  - name: two\n", "two.j2"),
    ]
    aci.deploy()

    assert len(aci.results) == 2
    assert all(result["success"] for result in aci.results)
    assert aci.config.count("<fvTenant ") == 2


def test_deploy_template_from_file(deploy, tmp_path):
    (tmp_path / "tenant.j2").write_text("fvTenant:\n  - name: acme\n", encoding="utf-8")

    aci = deploy()
    aci.template = "tenant.j2"
    aci.deploy()

    assert "acme" in aci.config


def test_deploy_from_csv(deploy, tmp_path):
    pd.DataFrame({"tag": ["a", "b"], "name": ["acme", "beta"]}).to_csv(
        tmp_path / "tenants.csv", index=False
    )

    aci = deploy()
    aci.csv = "tenants.csv"
    aci.template = (
        "fvTenant:\n{% for row in tenants %}\n  - name: {{ row.name }}\n{% endfor %}\n",
        "tenant.j2",
    )
    aci.deploy()

    config = aci.config
    assert "acme" in config
    assert "beta" in config


def test_deploy_save_output(deploy, tmp_path):
    aci = deploy(file_output="scripts/config")
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()

    output = tmp_path / "scripts" / "config.xml"
    assert output.exists()
    assert "acme" in output.read_text(encoding="utf-8")


def test_deploy_commits_when_all_templates_succeed(monkeypatch):
    committed = []
    monkeypatch.setattr(
        "devaci.transport.apic.ApicSession.commit", lambda self, config: committed.append(config)
    )

    aci = DeployClass(testing=False, ip="10.0.0.1", username="u", password="p", logging=False)
    aci.template = [
        ("fvTenant:\n  - name: one\n", "one.j2"),
        ("fvTenant:\n  - name: two\n", "two.j2"),
    ]
    aci.deploy()

    assert len(committed) == 1
    assert "one" in aci.config
    assert "two" in aci.config


def test_deploy_skips_commit_when_a_template_fails(monkeypatch):
    committed = []
    monkeypatch.setattr(
        "devaci.transport.apic.ApicSession.commit", lambda self, config: committed.append(config)
    )

    aci = DeployClass(testing=False, ip="10.0.0.1", username="u", password="p", logging=False)
    aci.template = [
        ("{{ missing_helper() }}\n", "bad.j2"),
        ("fvTenant:\n  - name: good\n", "good.j2"),
    ]
    aci.deploy()

    assert committed == []
    assert aci.results[0]["success"] is False
    assert aci.results[1]["success"] is True


def test_deploy_does_not_prompt_at_construction(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("credentials must not be requested at construction")

    monkeypatch.setattr("builtins.input", fail)
    monkeypatch.setattr("devaci.deploy.getpass.getpass", fail)

    DeployClass(testing=False, logging=False)


def test_build_apic_prompts_for_missing_credentials(monkeypatch):
    answers = iter(["10.0.0.1", "admin"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr("devaci.deploy.getpass.getpass", lambda _: "secret")

    aci = DeployClass(testing=False, logging=False)
    apic, ip = aci._build_apic()

    assert ip == "10.0.0.1"
    assert apic is not None


def test_deploy_variable_named_name(deploy):
    aci = deploy()
    aci.variables = {"name": "test", "descr": "Test tenant"}
    aci.template = (
        "fvTenant:\n  - name: {{ name }}\n    descr: {{ descr }}\n",
        "tenant.j2",
    )
    aci.deploy()

    assert aci.results[0]["success"] is True
    assert "test" in aci.config
