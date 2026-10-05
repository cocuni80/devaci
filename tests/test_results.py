from dataclasses import FrozenInstanceError

import pytest

from devaci.results import CobraResult, DeployResult, JinjaResult, Result


def test_result_to_dict():
    result = Result(success=True, log=["a"], date="d")
    assert result.to_dict() == {"date": "d", "success": True, "log": ["a"]}


def test_deploy_result_to_dict():
    result = DeployResult(success=False, log=[], date="d", path="/p", name="n")
    assert result.to_dict() == {
        "date": "d",
        "success": False,
        "log": [],
        "path": "/p",
        "name": "n",
    }


def test_jinja_result_to_dict():
    result = JinjaResult(success=True, log=[], date="d", output={"a": 1})
    assert result.to_dict() == {"date": "d", "success": True, "log": [], "output": {"a": 1}}


def test_cobra_result_none_config():
    result = CobraResult(config=None)
    assert result.xml is None
    assert result.json is None


def test_results_are_frozen():
    result = Result()
    with pytest.raises(FrozenInstanceError):
        result.success = True
