"""Centralized logging and terminal output for devaci.

This module is the single place where the library configures logging and
terminal output. Import the root logger through :func:`get_logger` (modules use
``get_logger(__name__)``) and the shared rich console through
:func:`get_console`; do not create handlers or consoles elsewhere.
"""

from __future__ import annotations

import logging
from typing import TextIO

from rich.console import Console

__all__ = [
    "LOGGER_NAME",
    "LOG_FORMAT",
    "configure_logging",
    "get_console",
    "get_logger",
    "logger",
]

LOGGER_NAME = "devaci"
LOG_FORMAT = "%(levelname)-8s %(name)s: %(message)s"
_STREAM_HANDLER_NAME = "devaci-stream"

logger = logging.getLogger(LOGGER_NAME)
logger.addHandler(logging.NullHandler())

_console: Console | None = None


def get_logger(name: str | None = None) -> logging.Logger:
    """Return the devaci logger, or a child logger when ``name`` is given.

    Modules use ``get_logger(__name__)`` so records carry the ``devaci.<module>``
    name and can be filtered per component. Names already rooted at ``devaci``
    are used as-is; any other name becomes a child of the ``devaci`` logger.

    The library ships a :class:`~logging.NullHandler` and does not configure
    output on import; call :func:`configure_logging` (or your own logging setup)
    to emit records.
    """
    if name is None:
        return logger
    if name == LOGGER_NAME or name.startswith(f"{LOGGER_NAME}."):
        return logging.getLogger(name)
    return logger.getChild(name)


def configure_logging(
    level: int = logging.INFO,
    fmt: str = LOG_FORMAT,
    stream: TextIO | None = None,
) -> None:
    """Attach a stream handler to the devaci logger.

    Safe to call repeatedly: the level is applied on every call while the
    stream handler is added only once (tracked by a named handler). Records
    still propagate to the stdlib root logger, so per-module levels can be
    tuned independently.
    """
    logger.setLevel(level)

    for handler in logger.handlers:
        if handler.get_name() == _STREAM_HANDLER_NAME:
            return

    handler = logging.StreamHandler(stream)
    handler.set_name(_STREAM_HANDLER_NAME)
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)


def get_console() -> Console:
    """Return the shared rich console used for rendered configuration output."""
    global _console
    if _console is None:
        _console = Console()
    return _console
