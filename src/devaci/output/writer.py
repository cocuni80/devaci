"""Rendered configuration output helpers for devaci."""

from __future__ import annotations

import json
import xml.dom.minidom
from pathlib import Path
from typing import Any

from rich.syntax import Syntax

from devaci.console import get_console, get_logger

logger = get_logger(__name__)


def print_syntax(
    content: str, lexer: str, theme: str = "fruity", line_numbers: bool = True
) -> None:
    """Pretty-print highlighted source (XML/JSON) to the terminal."""
    get_console().print(Syntax(content, lexer, theme=theme, line_numbers=line_numbers))


class OutputWriter:
    """Renders generated configuration to disk or the terminal."""

    def __init__(self, working_folder: Path, render_to_xml: bool = True) -> None:
        self._working_folder = working_folder
        self._render_to_xml = render_to_xml

    def save(self, content: Any, name: str = "output") -> None:
        """Save ``content`` under ``working_folder`` as XML or JSON."""
        if content is None:
            return

        suffix = "xml" if self._render_to_xml else "json"
        output_path = self._working_folder / f"{name}.{suffix}"
        try:
            if self._render_to_xml:
                text = xml.dom.minidom.parseString(content).toprettyxml(indent="\t")
            else:
                text = json.dumps(content, indent=4, ensure_ascii=False)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text, encoding="utf-8")
        except Exception:
            logger.exception("Failed to save output file %s.", output_path)

    def show(self, content: Any, theme: str = "fruity", line_numbers: bool = True) -> None:
        """Pretty-print ``content`` to the terminal."""
        if content is None:
            return

        try:
            if self._render_to_xml:
                text = xml.dom.minidom.parseString(content).toprettyxml(indent="\t")
                lexer = "xml"
            else:
                text = json.dumps(content, indent=4, ensure_ascii=False)
                lexer = "json"
            print_syntax(text, lexer, theme=theme, line_numbers=line_numbers)
        except Exception:
            logger.exception("Failed to print output.")
