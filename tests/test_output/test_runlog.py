import json

from devaci.output.runlog import RunLog


def test_runlog_appends_history(tmp_path):
    runlog = RunLog(tmp_path, "outputs/logs/logging", enabled=True)
    runlog.save({"a": 1})
    runlog.save({"b": 2})
    log = (tmp_path / "outputs/logs/logging.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line) for line in log] == [{"a": 1}, {"b": 2}]
    assert runlog.last() == {"b": 2}


def test_runlog_disabled(tmp_path):
    RunLog(tmp_path, "logging", enabled=False).save({"a": 1})
    assert not (tmp_path / "logging.jsonl").exists()


def test_runlog_ignores_corrupt_last_record(tmp_path):
    path = tmp_path / "logging.jsonl"
    path.write_text('{"a": 1}\nnot json\n', encoding="utf-8")

    runlog = RunLog(tmp_path, "logging", enabled=True)

    assert runlog.last() is None
    runlog.save({"b": 2})
    assert runlog.last() == {"b": 2}


def test_runlog_swallows_write_errors(tmp_path):
    (tmp_path / "blocked").write_text("a file, not a directory", encoding="utf-8")

    RunLog(tmp_path, "blocked/logging", enabled=True).save({"a": 1})


def test_runlog_iter_runs_orders_and_skips_corrupt(tmp_path):
    runlog = RunLog(tmp_path, "logging", enabled=True)
    for index in range(3):
        runlog.save({"i": index})
    with open(runlog.path, "a", encoding="utf-8") as handle:
        handle.write("not json\n")

    assert [record["i"] for record in runlog.iter_runs(reverse=True)] == [2, 1, 0]
    assert [record["i"] for record in runlog.iter_runs(reverse=False)] == [0, 1, 2]
