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
        kwargs.setdefault("working_folder", tmp_path)
        return DeployClass(**kwargs)

    return _make


@pytest.fixture
def tenant_template() -> tuple[str, str]:
    return ("fvTenant:\n  - name: acme\n", "tenant.j2")
