"""Exception hierarchy for devaci."""

from __future__ import annotations

__all__ = ["CobraError", "DataError", "DeployError", "DevaciError", "JinjaError"]


class DevaciError(Exception):
    """Base exception for all devaci errors."""


class CobraError(DevaciError):
    """Raised when building or committing Cobra model objects fails."""


class JinjaError(DevaciError):
    """Raised when rendering a Jinja template fails."""


class DataError(DevaciError):
    """Raised when loading input data (xlsx/csv) fails."""


class DeployError(DevaciError):
    """Raised when the deployment workflow fails."""
