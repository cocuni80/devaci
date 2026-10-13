"""Typed configuration for the devaci deployment workflow."""

from __future__ import annotations

from collections.abc import Sequence
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

    Attributes:
        testing: Dry run. Skip the commit and the interactive APIC credential
            prompt (default ``False``).
        ip: APIC IP/hostname. Prompted at commit time when missing.
        username: APIC username. Prompted at commit time when missing.
        password: APIC password. Prompted at commit time when missing.
        timeout: APIC read timeout in seconds (default ``180``).
        connect_timeout: APIC connection timeout in seconds (default ``5``).
        secure: Verify the APIC TLS certificate (default ``False``).
        timer: Countdown in seconds shown before committing (default ``5``).
        show_output: Pretty-print the rendered configuration to the terminal
            (default ``False``).
        file_output: Base path (relative to ``working_folder``) to save the
            rendered configuration; the ``.xml``/``.json`` suffix is added.
        logging_output: History location relative to ``working_folder``; the
            ``.jsonl`` suffix is added (default ``outputs/logs/logging.json``).
        logging: Persist one run record per ``deploy()`` to the history
            (default ``True``); it does not control the printed report.
        show_report: Print the run report at the end of ``deploy()``
            (default ``True``; set ``False`` to stay quiet).
        verbose: Add per-class detail to the report (default ``False``).
        render_to_xml: Render the configuration as XML (default ``True``) or
            JSON (``False``).
        filters: Values to keep, matched against the ``filter_by`` column.
            Takes precedence over ``filters_source_sheet``.
        filter_by: Column used to match ``filters`` (default ``tag``).
        filters_source_sheet: Fully qualified sheet used to derive the filter
            values when ``filters`` is empty.
        filters_condition_field: Boolean column of ``filters_source_sheet`` used
            to select rows (default ``enabled``).
        filters_output_field: Column of ``filters_source_sheet`` whose values
            become the filters (default ``name``).
        working_folder: Base folder for templates, data, outputs and history
            (default: current directory).
    """

    testing: bool = False
    ip: str | None = None
    username: str | None = None
    password: str | None = None
    timeout: int = 180
    connect_timeout: int = 5
    secure: bool = False
    timer: int = 5
    show_output: bool = False
    file_output: str | None = None
    logging_output: str = "outputs/logs/logging.json"
    logging: bool = True
    show_report: bool = True
    verbose: bool = False
    render_to_xml: bool = True
    filters_source_sheet: str | None = None
    filters_condition_field: str = "enabled"
    filters_output_field: str = "name"
    filters: Sequence[str] | None = None
    filter_by: str = "tag"
    working_folder: Path = field(default_factory=Path.cwd)

    def __post_init__(self) -> None:
        if self.filters is not None:
            self.filters = list(self.filters)

    @classmethod
    def from_kwargs(cls, **kwargs: Any) -> DeployConfig:
        """Build a config from keyword arguments, ignoring unknown keys.

        Unknown keys are logged as warnings (they used to be silently
        ignored) so typos such as ``workign_folder`` become visible.
        """
        known = {item.name for item in fields(cls)}
        for key in sorted(set(kwargs) - known):
            logger.warning("Unknown option %r ignored.", key)
        return cls(**{key: value for key, value in kwargs.items() if key in known})
