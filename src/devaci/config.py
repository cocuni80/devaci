"""Typed configuration for the devaci deployment workflow."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

from devaci.console import get_logger

__all__ = ["DeployConfig"]

logger = get_logger(__name__)


@dataclass
class DeployConfig:
    """Typed options for :class:`devaci.DeployClass`.

    Mirrors the keyword arguments accepted at construction time. Keeping the
    options in a dataclass gives type checking and autocompletion while
    :meth:`from_kwargs` preserves the legacy ``DeployClass(**kwargs)`` API.
    """

    testing: bool = False
    ip: str | None = None
    username: str | None = None
    password: str | None = None
    timeout: int = 180
    secure: bool = False
    timer: int = 5
    show_output: bool = False
    file_output: str | None = None
    logging_output: str = "outputs/logs/logging.json"
    logging: bool = True
    render_to_xml: bool = True
    filters_source_sheet: str | None = None
    filters_condition_field: str = "enabled"
    filters_output_field: str = "name"
    filters: Iterable[str] | None = None
    filter_by: str = "tag"
    working_folder: Path = field(default_factory=Path.cwd)

    @classmethod
    def from_kwargs(cls, **kwargs: Any) -> DeployConfig:
        """Build a config from keyword arguments, ignoring unknown keys.

        Unknown keys are logged as warnings (they used to be silently
        ignored) so typos such as ``workign_folder`` become visible.
        """
        known = {item.name for item in fields(cls)}
        for key in sorted(set(kwargs) - known):
            logger.warning(f"[Config] -> [ConfigError]: Unknown option '{key}' ignored.")
        return cls(**{key: value for key, value in kwargs.items() if key in known})
