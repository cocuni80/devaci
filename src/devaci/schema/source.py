"""Single-file schema source resolution against a working folder."""

from __future__ import annotations

from pathlib import Path

from devaci.exceptions import DataError

__all__ = ["SchemaSource"]


class SchemaSource:
    """Resolve and read the single schema file configured for a deploy."""

    def __init__(self, working_folder: Path) -> None:
        self._working_folder = working_folder
        self._path: Path | None = None

    @property
    def path(self) -> Path | None:
        """Return the resolved schema path, or None when unset."""
        return self._path

    def set(self, value: str | Path) -> None:
        """Set the schema path, resolved against ``working_folder`` when relative."""
        self._path = Path(value) if Path(value).is_absolute() else self._working_folder / value

    def read(self) -> str:
        """Read the schema file, raising :class:`DataError` on failure."""
        if self._path is None:
            raise DataError("No schema configured.")
        try:
            return self._path.read_text(encoding="utf-8")
        except OSError as exc:
            raise DataError(f"Failed to read schema '{self._path}': {exc}") from exc
