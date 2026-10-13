"""Execution history persistence for devaci."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from devaci.console import get_logger

logger = get_logger(__name__)

_CHUNK_SIZE = 65536


class RunLog:
    """Appends run records to a JSON Lines history file."""

    def __init__(self, working_folder: Path, logging_output: str, enabled: bool = True) -> None:
        self._working_folder = working_folder
        self._logging_output = logging_output
        self._enabled = enabled

    @property
    def path(self) -> Path:
        """Return the JSON Lines history location."""
        return Path(self._working_folder / self._logging_output).with_suffix(".jsonl")

    def save(self, run: dict[str, Any]) -> None:
        """Append one run record to the JSON Lines history defensively."""
        if not self._enabled:
            return

        log_file = self.path
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(run, ensure_ascii=False) + "\n")
        except Exception:
            logger.exception("Failed to write run log %s.", log_file)

    def last(self) -> dict[str, Any] | None:
        """Return the latest record without loading the complete history."""
        log_file = self.path
        if not log_file.exists():
            return None
        try:
            with open(log_file, "rb") as handle:
                end = handle.seek(0, 2)
                while end > 0:
                    end -= 1
                    handle.seek(end)
                    if handle.read(1) not in b"\r\n":
                        break
                while end > 0:
                    end -= 1
                    handle.seek(end)
                    if handle.read(1) == b"\n":
                        end += 1
                        break
                handle.seek(end)
                line = handle.readline().decode("utf-8").strip()
            return self._parse(line)
        except (OSError, UnicodeDecodeError):
            logger.warning("Failed to read latest run log %s.", log_file)
            return None

    def iter_runs(self, reverse: bool = True) -> Iterator[dict[str, Any]]:
        """Yield run records, newest first by default, skipping malformed lines.

        ``reverse=True`` reads the file backwards in blocks so only as much as
        consumed is loaded, which keeps large histories cheap.
        """
        log_file = self.path
        if not log_file.exists():
            return
        if not reverse:
            try:
                with open(log_file, encoding="utf-8") as handle:
                    for line in handle:
                        record = self._parse(line)
                        if record is not None:
                            yield record
            except OSError:
                logger.warning("Failed to read run log %s.", log_file)
            return
        try:
            with open(log_file, "rb") as handle:
                position = handle.seek(0, 2)
                carry = b""
                while position > 0:
                    size = min(position, _CHUNK_SIZE)
                    position -= size
                    handle.seek(position)
                    parts = (handle.read(size) + carry).split(b"\n")
                    carry = parts[0]
                    for raw in reversed(parts[1:]):
                        record = self._parse(raw.decode("utf-8"))
                        if record is not None:
                            yield record
                record = self._parse(carry.decode("utf-8"))
                if record is not None:
                    yield record
        except OSError:
            logger.warning("Failed to read run log %s.", log_file)

    @staticmethod
    def _parse(line: str) -> dict[str, Any] | None:
        text = line.strip()
        if not text:
            return None
        try:
            record = json.loads(text)
        except json.JSONDecodeError:
            return None
        return record if isinstance(record, dict) else None
