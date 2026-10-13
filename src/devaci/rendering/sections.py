"""Split a rendered Jinja template into per-ACI-class sections.

A template is a single file whose top-level keys are ACI class names. To compile
one sheet at a time, devaci extracts the fragment that belongs to each class and
renders it independently, so sections for other classes are never evaluated.
"""

from __future__ import annotations

import re
from collections.abc import Collection

__all__ = ["split_template"]

_SECTION_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")


def split_template(template: str, names: Collection[str]) -> tuple[str, dict[str, str]]:
    """Split ``template`` into ``(preamble, {class_name: fragment})``.

    A section starts at a top-level line ``name:`` (column 0) whose ``name`` is in
    ``names``. Everything before the first section is the ``preamble`` (comments,
    ``{% set %}``, ``{% import %}``...); callers must prepend it to each fragment
    so template-level definitions remain available. When no section matches,
    ``template`` is returned untouched with an empty mapping.
    """
    lines = template.splitlines(keepends=True)
    starts: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = _SECTION_RE.match(line)
        if match and match.group(1) in names:
            starts.append((index, match.group(1)))

    if not starts:
        return template, {}

    preamble = "".join(lines[: starts[0][0]])
    sections: dict[str, str] = {}
    for position, (index, key) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        sections[key] = "".join(lines[index:end])
    return preamble, sections
