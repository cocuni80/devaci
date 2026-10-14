"""Shared pytest fixtures for devaci."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from devaci import DeployClass


@pytest.fixture
def deploy(tmp_path: Path) -> Callable[..., DeployClass]:
    """Return a factory that builds a dry-run ``DeployClass`` rooted at ``tmp_path``."""

    def _make(**kwargs: Any) -> DeployClass:
        kwargs.setdefault("testing", True)
        kwargs.setdefault("logging", False)
        kwargs.setdefault("show_report", False)
        kwargs.setdefault("working_folder", tmp_path)
        return DeployClass(**kwargs)

    return _make


@pytest.fixture
def schema_file(tmp_path: Path) -> Callable[[str], Path]:
    """Return a factory that writes a schema file into ``tmp_path``."""

    def _write(content: str, name: str = "schema.j2") -> Path:
        path = tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    return _write
