import json

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
        tmp_path / "data.xlsx", sheet_name="fvTenant", index=False
    )

    aci = deploy()
    aci.xlsx = "data.xlsx"
    aci.template = ("fvTenant:\n  - name: {{ fvTenant.name }}\n", "tenant.j2")
    aci.deploy()

    config = aci.config
    assert "acme" in config
    assert "beta" in config

    assert aci.results[0]["success"] is True


def test_deploy_per_sheet_onto_same_config(deploy, tmp_path):
    with pd.ExcelWriter(tmp_path / "data.xlsx") as writer:
        pd.DataFrame([{"name": "acme"}]).to_excel(writer, sheet_name="fvTenant", index=False)
        pd.DataFrame([{"name": "web", "tenant": "acme"}]).to_excel(
            writer, sheet_name="fvAp", index=False
        )

    aci = deploy()
    aci.xlsx = "data.xlsx"
    aci.template = (
        "fvTenant:\n  - name: {{ fvTenant.name }}\n"
        "\n"
        "fvAp:\n  - name: {{ fvAp.name }}\n    tenant: {{ fvAp.tenant }}\n",
        "fabric.j2",
    )
    aci.deploy()

    assert "acme" in aci.config
    assert "web" in aci.config
    assert aci.config.count("<fvTenant ") == 1
    assert aci.config.count("<fvAp ") == 1


def test_deploy_self_contained_template(deploy):
    aci = deploy()
    aci.template = (
        '{% set names = ["one", "two"] %}\n'
        "fvTenant:\n"
        "  {% for name in names %}\n"
        "  - name: {{ name }}\n"
        "  {% endfor %}\n",
        "static.j2",
    )
    aci.deploy()

    assert "one" in aci.config
    assert "two" in aci.config
    assert aci.results[0]["success"] is True


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
        tmp_path / "fvTenant.csv", index=False
    )

    aci = deploy()
    aci.csv = "fvTenant.csv"
    aci.template = ("fvTenant:\n  - name: {{ fvTenant.name }}\n", "tenant.j2")
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


def test_deploy_persists_one_structured_run_per_line(deploy, tmp_path):
    aci = deploy(logging=True, show_report=False)
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()

    path = tmp_path / "outputs/logs/logging.jsonl"
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 1
    assert records[0]["mode"] == "dry_run"
    assert records[0]["templates"][0]["objects"] == 1
    assert records[0]["templates"][0]["log"] == [
        {"level": "info", "where": "fvTenant", "message": "rendered", "objects": 1}
    ]


def test_deploy_report_can_be_disabled(deploy, capsys):
    aci = deploy(show_report=False)
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()

    assert capsys.readouterr().out == ""
    assert aci.success is True


def test_failed_commit_keeps_error_for_the_report(monkeypatch):
    monkeypatch.setattr(
        "devaci.transport.apic.ApicSession.commit",
        lambda self, config: (_ for _ in ()).throw(ConnectionError("host unreachable")),
    )
    aci = DeployClass(
        testing=False,
        ip="1.1.1.1",
        username="u",
        password="p",
        timer=0,
        logging=False,
        show_report=False,
    )
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()

    commit = aci.run["commit"]
    assert commit["success"] is False
    assert commit["log"][0]["type"] == "ConnectionError"
    assert "host unreachable" in commit["log"][0]["message"]


def test_print_report_shows_latest_run(deploy, capsys):
    aci = deploy()
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()

    aci.print_report()

    out = capsys.readouterr().out
    assert "tenant.j2" in out
    assert "Result: OK" in out


def test_print_reports_without_pagination_prints_all(deploy, capsys):
    aci = deploy(logging=True)
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()
    aci.deploy()

    aci.print_reports(paginate=False)

    assert capsys.readouterr().out.count("Result: OK") == 2


def test_print_reports_paginated_stops_without_tty(deploy, capsys):
    aci = deploy(logging=True)
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    for _ in range(3):
        aci.deploy()

    aci.print_reports(limit=1)

    out = capsys.readouterr().out
    assert out.count("Result: OK") == 1
    assert "older runs not shown" in out


def test_unmatched_sheets_are_debug_only(deploy, tmp_path):
    with pd.ExcelWriter(tmp_path / "data.xlsx") as writer:
        pd.DataFrame([{"name": "acme"}]).to_excel(writer, sheet_name="fvTenant", index=False)
        pd.DataFrame([{"name": "x"}]).to_excel(writer, sheet_name="OCs", index=False)

    aci = deploy()
    aci.xlsx = "data.xlsx"
    aci.template = ("fvTenant:\n  - name: {{ fvTenant.name }}\n", "tenant.j2")
    aci.deploy()

    log = aci.run["templates"][0]["log"]
    assert all(event["level"] != "warning" for event in log)
    assert any(event["level"] == "debug" and "OCs" in event["message"] for event in log)


def test_report_without_templates(deploy, capsys):
    aci = deploy(show_report=True)

    aci.deploy()

    assert "nothing to do" in capsys.readouterr().out


def test_verbose_report_includes_object_counts(deploy, tmp_path, capsys):
    pd.DataFrame([{"name": "acme"}, {"name": "beta"}]).to_excel(
        tmp_path / "data.xlsx", sheet_name="fvTenant", index=False
    )

    aci = deploy(verbose=True)
    aci.xlsx = "data.xlsx"
    aci.template = ("fvTenant:\n  - name: {{ fvTenant.name }}\n", "tenant.j2")
    aci.deploy()

    aci.print_report()

    assert "fvTenant: rendered (2 objects)" in capsys.readouterr().out


def test_report_prefers_current_run_over_stale_file(deploy, monkeypatch, capsys):
    aci = deploy(logging=True)
    aci.template = ("fvTenant:\n  - name: acme\n", "one.j2")
    aci.deploy()

    monkeypatch.setattr(aci._runlog, "last", lambda: {"stale": True})
    aci.print_report()

    assert "one.j2" in capsys.readouterr().out


def test_report_shows_all_errors(deploy, monkeypatch, capsys):
    from devaci.cobra.builders import BUILDERS

    def boom(builder, value):
        raise ValueError("nope")

    monkeypatch.setitem(BUILDERS, "fvTenant", boom)
    monkeypatch.setitem(BUILDERS, "fvBD", boom)

    aci = deploy()
    aci.template = ("fvTenant:\n  - name: t\n\nfvBD:\n  - name: b\n", "both.j2")
    aci.deploy()

    aci.print_report()

    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "failed to build fvTenant" in text
    assert "failed to build fvBD" in text


def test_deploy_without_templates_resets_results(deploy):
    aci = deploy()
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()
    assert aci.results

    aci._templates._templates.clear()
    aci.deploy()

    assert aci.results == []
    assert aci.run["templates"] == []


def test_print_report_reads_file_regardless_of_logging(deploy, capsys):
    aci = deploy(logging=True)
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()

    aci._config.logging = False
    aci._run = None
    aci.print_report()

    assert "tenant.j2" in capsys.readouterr().out


def test_print_reports_reads_file_regardless_of_logging(deploy, capsys):
    aci = deploy(logging=True)
    aci.template = ("fvTenant:\n  - name: acme\n", "tenant.j2")
    aci.deploy()

    aci._config.logging = False
    aci._run = None
    aci.print_reports()

    assert "tenant.j2" in capsys.readouterr().out
