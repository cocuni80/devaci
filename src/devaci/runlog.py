"""Execution history persistence for devaci."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from devaci.console import logger


class RunLog:
    """Appends deployment results to a JSON history file."""

    def __init__(self, working_folder: Path, logging_output: str, enabled: bool = True) -> None:
        self._working_folder = working_folder
        self._logging_output = logging_output
        self._enabled = enabled

    def save(self, results: list[dict[str, Any]]) -> None:
        """Append ``results`` to the JSON log file defensively."""
        if not self._enabled:
            return

        log_file = Path(self._working_folder / self._logging_output).with_suffix(".json")
        history: list[Any] = []
        try:
            if log_file.exists():
                try:
                    with open(log_file, encoding="utf-8") as handle:
                        history = json.load(handle)
                        if not isinstance(history, list):
                            history = []
                except json.JSONDecodeError:
                    history = []

            history.extend(results)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, "w", encoding="utf-8") as handle:
                json.dump(history, handle, indent=4, ensure_ascii=False)
        except Exception as exc:
            logger.error(f"[LoggingError]: {type(exc).__name__}: {exc}")
