import json

from devaci.output.runlog import RunLog


def test_runlog_appends_history(tmp_path):
    runlog = RunLog(tmp_path, "outputs/logs/logging", enabled=True)
    runlog.save([{"a": 1}])
    runlog.save([{"b": 2}])
    log = json.loads((tmp_path / "outputs/logs/logging.json").read_text(encoding="utf-8"))
    assert log == [{"a": 1}, {"b": 2}]


def test_runlog_disabled(tmp_path):
    RunLog(tmp_path, "logging", enabled=False).save([{"a": 1}])
    assert not (tmp_path / "logging.json").exists()


def test_runlog_recovers_from_corrupt_file(tmp_path):
    path = tmp_path / "logging.json"
    path.write_text("not json", encoding="utf-8")

    RunLog(tmp_path, "logging", enabled=True).save([{"a": 1}])

    assert json.loads(path.read_text(encoding="utf-8")) == [{"a": 1}]
