import json

from devaci.output.writer import OutputWriter


def test_output_writer_saves_json(tmp_path):
    OutputWriter(tmp_path, render_to_xml=False).save({"a": 1}, "out")
    assert json.loads((tmp_path / "out.json").read_text(encoding="utf-8")) == {"a": 1}


def test_output_writer_saves_xml(tmp_path):
    OutputWriter(tmp_path, render_to_xml=True).save("<config/>", "out")
    assert (tmp_path / "out.xml").exists()


def test_output_writer_skips_none(tmp_path):
    OutputWriter(tmp_path).save(None, "out")
    assert not list(tmp_path.iterdir())


def test_output_writer_creates_parent_dirs(tmp_path):
    OutputWriter(tmp_path, render_to_xml=False).save({"a": 1}, "nested/dir/out")
    assert (tmp_path / "nested" / "dir" / "out.json").exists()
