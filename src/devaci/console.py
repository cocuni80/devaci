"""Logging helpers for devaci."""

from __future__ import annotations

import logging

__all__ = ["configure_logging", "get_logger"]

logger = logging.getLogger("devaci")
logger.addHandler(logging.NullHandler())


def get_logger(name: str | None = None) -> logging.Logger:
    """Return the devaci logger, or a child logger when ``name`` is given.

    Modules use ``get_logger(__name__)`` so records carry the ``devaci.<module>``
    name and can be filtered per component. The library ships a
    :class:`~logging.NullHandler` and does not configure output on import; call
    :func:`configure_logging` (or your own logging setup) to emit records.
    """
    return logger if name is None else logger.getChild(name)


def configure_logging(level: int = logging.INFO) -> None:
    """Attach a stream handler to the devaci logger (idempotent)."""
    if any(
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.NullHandler)
        for handler in logger.handlers
    ):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)-8s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)
