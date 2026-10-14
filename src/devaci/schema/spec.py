"""In-memory model of the declarative ACI schema (DSL)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["ListSpec", "NodeSpec", "ParentRef", "Schema"]


@dataclass(frozen=True)
class ListSpec:
    """Expand a delimited cell into one node per item.

    Attributes:
        source: Row column (or global variable) holding the delimited value.
        bind: Name bound to each expanded item for the node expressions.
        split: Delimiter used when ``expand`` is false.
        expand: Interpret each token as an integer/range (``3-5`` -> 3,4,5).
    """

    source: str
    bind: str
    split: str = ","
    expand: bool = False


@dataclass(frozen=True)
class ParentRef:
    """Reference to another registry entry used as this node's parent."""

    ref: str
    as_parent: dict[str, str] | None = None


@dataclass
class NodeSpec:
    """One entry (or inline child) of the schema."""

    key: str
    cls_path: str
    cls: Any = None
    parent: str | ParentRef | None = None
    requires: dict[str, str] = field(default_factory=dict)
    as_parent: dict[str, str] | None = None
    props: dict[str, str] = field(default_factory=dict)
    emit_parents: bool = False
    children: dict[str, NodeSpec] | list[NodeSpec] = field(default_factory=dict)
    when: str | None = None
    list: ListSpec | None = None


@dataclass
class Schema:
    """The parsed schema: a flat registry of top-level entries by key."""

    nodes: dict[str, NodeSpec] = field(default_factory=dict)

    @property
    def uni(self) -> NodeSpec | None:
        """Return the root ``pol.Uni`` entry when present."""
        return self.nodes.get("uni")
