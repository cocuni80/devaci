import json

import pandas as pd

from devaci import DeployClass

TENANT_SCHEMA = (
    "uni:\n"
    "  class: pol.Uni\n"
    "fvTenant:\n"
    "  class: fv.Tenant\n"
    "  parent: uni\n"
    '  requires: {name: "{{ name }}"}\n'
)


def _tenant_xlsx(tmp_path, names=("acme",)):
    pd.DataFrame([{"name": name} for name in names]).to_excel(
        tmp_path / "data.xlsx", sheet_name="fvTenant", index=False
    )


def test_deploy_without_schema_is_a_noop(deploy):
    aci = deploy()
    aci.deploy()

    assert aci.results == []
    assert aci.run["templates"] == []
    assert aci.run["success"] is True


def test_deploy_schema_builds_rows_from_xlsx(deploy, schema_file, tmp_path):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path, ("acme", "beta"))

    aci = deploy()
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    config = aci.config
    assert "acme" in config
    assert "beta" in config
    assert aci.results[0]["success"] is True


def test_deploy_schema_uses_variables(deploy, schema_file, tmp_path):
    schema_file(
        "uni:\n  class: pol.Uni\n"
        "fvTenant:\n  class: fv.Tenant\n  parent: uni\n"
        '  requires: {name: "{{ tenant_name }}"}\n'
    )
    pd.DataFrame([{"tag": "x"}]).to_excel(
        tmp_path / "data.xlsx", sheet_name="fvTenant", index=False
    )

    aci = deploy()
    aci.variables = {"tenant_name": "acme"}
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    assert "acme" in aci.config


def test_deploy_schema_property_resolves_against_working_folder(deploy, schema_file, tmp_path):
    schema_file(TENANT_SCHEMA)

    aci = deploy()
    aci.schema = "schema.j2"

    assert aci.schema == tmp_path / "schema.j2"


def test_deploy_missing_schema_file_fails(deploy):
    aci = deploy()
    aci.schema = "missing.j2"
    aci.deploy()

    assert aci.results[0]["success"] is False
    assert any("failed to load schema" in event["message"] for event in aci.results[0]["log"])


def test_deploy_unknown_class_fails(deploy, schema_file):
    schema_file("fvTenant:\n  class: fv.Nope\n  requires: {name: x}\n")

    aci = deploy()
    aci.schema = "schema.j2"
    aci.deploy()

    assert aci.results[0]["success"] is False
    assert any(event["level"] == "error" for event in aci.results[0]["log"])


def test_deploy_commits_when_all_rows_succeed(monkeypatch, schema_file, tmp_path):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)
    committed = []
    monkeypatch.setattr(
        "devaci.transport.apic.ApicSession.commit", lambda self, config: committed.append(config)
    )

    aci = DeployClass(
        testing=False,
        ip="10.0.0.1",
        username="u",
        password="p",
        logging=False,
        working_folder=tmp_path,
    )
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    assert len(committed) == 1
    assert "acme" in aci.config


def test_deploy_skips_commit_when_a_row_fails(monkeypatch, schema_file, tmp_path):
    schema_file("fvTenant:\n  class: fv.Nope\n")
    committed = []
    monkeypatch.setattr(
        "devaci.transport.apic.ApicSession.commit", lambda self, config: committed.append(config)
    )

    aci = DeployClass(
        testing=False,
        ip="10.0.0.1",
        username="u",
        password="p",
        logging=False,
        working_folder=tmp_path,
    )
    aci.schema = "schema.j2"
    aci.deploy()

    assert committed == []
    assert aci.results[0]["success"] is False


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


def test_deploy_persists_one_structured_run_per_line(deploy, schema_file, tmp_path):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)

    aci = deploy(logging=True, show_report=False)
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    path = tmp_path / "outputs/logs/logging.jsonl"
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 1
    assert records[0]["mode"] == "dry_run"
    assert records[0]["templates"][0]["objects"] == 1
    assert records[0]["templates"][0]["log"] == [
        {"level": "info", "where": "fvTenant", "message": "rendered", "objects": 1}
    ]


def test_deploy_report_can_be_disabled(deploy, schema_file, tmp_path, capsys):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)

    aci = deploy(show_report=False)
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    assert capsys.readouterr().out == ""
    assert aci.success is True


def test_failed_commit_keeps_error_for_the_report(monkeypatch, schema_file, tmp_path):
    monkeypatch.setattr(
        "devaci.transport.apic.ApicSession.commit",
        lambda self, config: (_ for _ in ()).throw(ConnectionError("host unreachable")),
    )
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)
    aci = DeployClass(
        testing=False,
        ip="1.1.1.1",
        username="u",
        password="p",
        timer=0,
        logging=False,
        show_report=False,
        working_folder=tmp_path,
    )
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    commit = aci.run["commit"]
    assert commit["success"] is False
    assert commit["log"][0]["type"] == "ConnectionError"
    assert "host unreachable" in commit["log"][0]["message"]


def test_print_report_shows_latest_run(deploy, schema_file, tmp_path, capsys):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)

    aci = deploy()
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    aci.print_report()

    out = capsys.readouterr().out
    assert "schema.j2" in out
    assert "Result: OK" in out


def test_print_reports_without_pagination_prints_all(deploy, schema_file, tmp_path, capsys):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)

    aci = deploy(logging=True)
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()
    aci.deploy()

    aci.print_reports(paginate=False)

    assert capsys.readouterr().out.count("Result: OK") == 2


def test_print_reports_paginated_stops_without_tty(deploy, schema_file, tmp_path, capsys):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)

    aci = deploy(logging=True)
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    for _ in range(3):
        aci.deploy()

    aci.print_reports(limit=1)

    out = capsys.readouterr().out
    assert out.count("Result: OK") == 1
    assert "older runs not shown" in out


def test_report_without_schema(deploy, capsys):
    aci = deploy(show_report=True)

    aci.deploy()

    assert "nothing to do" in capsys.readouterr().out


def test_verbose_report_includes_object_counts(deploy, schema_file, tmp_path, capsys):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path, ("acme", "beta"))

    aci = deploy(verbose=True)
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    aci.print_report()

    assert "fvTenant: rendered (2 objects)" in capsys.readouterr().out


def test_report_prefers_current_run_over_stale_file(
    deploy, schema_file, tmp_path, monkeypatch, capsys
):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)

    aci = deploy(logging=True)
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    monkeypatch.setattr(aci._runlog, "last", lambda: {"stale": True})
    aci.print_report()

    assert "schema.j2" in capsys.readouterr().out


def test_report_shows_all_errors(deploy, schema_file, tmp_path, capsys):
    schema_file(
        "fvTenant:\n  class: fv.Tenant\n  requires: {name: \"{{ 1 / 0 }}\"}\n"
        "fvAp:\n  class: fv.Ap\n  requires: {name: \"{{ 1 / 0 }}\"}\n"
    )
    with pd.ExcelWriter(tmp_path / "data.xlsx") as writer:
        pd.DataFrame([{"name": "t"}]).to_excel(writer, sheet_name="fvTenant", index=False)
        pd.DataFrame([{"name": "a"}]).to_excel(writer, sheet_name="fvAp", index=False)

    aci = deploy()
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    aci.print_report()

    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "failed to build fvTenant" in text
    assert "failed to build fvAp" in text


def test_deploy_without_schema_resets_results(deploy, schema_file, tmp_path):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)

    aci = deploy()
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()
    assert aci.results

    aci._schema._path = None
    aci.deploy()

    assert aci.results == []
    assert aci.run["templates"] == []


def test_print_report_reads_file_regardless_of_logging(deploy, schema_file, tmp_path, capsys):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)

    aci = deploy(logging=True)
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    aci._config.logging = False
    aci._run = None
    aci.print_report()

    assert "schema.j2" in capsys.readouterr().out


def test_print_reports_reads_file_regardless_of_logging(deploy, schema_file, tmp_path, capsys):
    schema_file(TENANT_SCHEMA)
    _tenant_xlsx(tmp_path)

    aci = deploy(logging=True)
    aci.xlsx = "data.xlsx"
    aci.schema = "schema.j2"
    aci.deploy()

    aci._config.logging = False
    aci._run = None
    aci.print_reports()

    assert "schema.j2" in capsys.readouterr().out
