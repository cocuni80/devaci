"""Logging and console helpers for devaci."""

from __future__ import annotations

import logging

from rich.console import Console
from rich.syntax import Syntax

logger = logging.getLogger("devaci")

console = Console()


def get_logger(name: str | None = None) -> logging.Logger:
    """Return the devaci logger, or a child logger when ``name`` is given."""
    return logger if name is None else logger.getChild(name)


def configure_logging(level: int = logging.INFO) -> None:
    """Attach a stream handler to the devaci logger (idempotent)."""
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)-8s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)


def print_syntax(
    content: str, lexer: str, theme: str = "fruity", line_numbers: bool = True
) -> None:
    """Pretty-print highlighted source (XML/JSON) to the terminal."""
    console.print(Syntax(content, lexer, theme=theme, line_numbers=line_numbers))
