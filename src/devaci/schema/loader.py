"""Parse the declarative schema DSL into :class:`~devaci.schema.spec.Schema`."""

from __future__ import annotations

import importlib
from functools import cache
from typing import Any

from devaci.exceptions import DataError
from devaci.rendering.yaml_loader import load_yaml
from devaci.schema.spec import ListSpec, NodeSpec, ParentRef, Schema

__all__ = ["SchemaLoader", "resolve_class"]


@cache
def resolve_class(path: str) -> Any:
    """Resolve ``pkg.Clase`` to ``cobra.model.<pkg>.<Clase>`` (cached)."""
    package, separator, name = path.partition(".")
    if not separator or not package or not name:
        raise DataError(f"Invalid class reference {path!r}; expected 'pkg.Class'.")
    try:
        module = importlib.import_module(f"cobra.model.{package}")
        return getattr(module, name)
    except (ImportError, AttributeError) as exc:
        raise DataError(f"Unknown Cobra class {path!r}: {exc}") from exc


def _as_mapping(value: Any, where: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise DataError(f"'{where}' must be a mapping in the schema.")
    return value


def _as_str_mapping(value: Any, where: str) -> dict[str, str]:
    return {str(key): str(item) for key, item in _as_mapping(value, where).items()}


def _is_true(value: Any) -> bool:
    return value is not None and str(value).strip().lower() in ("true", "yes", "1")


class SchemaLoader:
    """Build a :class:`Schema` from the DSL text."""

    def load(self, content: str) -> Schema:
        """Parse ``content`` (YAML with embedded Jinja expressions) into a Schema."""
        data = load_yaml(content)
        if data is None:
            raise DataError("Schema is empty.")
        if not isinstance(data, dict):
            raise DataError("Schema must be a mapping of entries.")
        nodes: dict[str, NodeSpec] = {}
        for key, raw in data.items():
            nodes[str(key)] = self._node(str(key), raw)
        return Schema(nodes=nodes)

    def _node(self, key: str, raw: Any) -> NodeSpec:
        if not isinstance(raw, dict):
            raise DataError(f"Entry '{key}' must be a mapping.")
        cls_path = raw.get("class")
        if not cls_path:
            raise DataError(f"Entry '{key}' is missing 'class'.")
        return NodeSpec(
            key=key,
            cls_path=str(cls_path),
            cls=resolve_class(str(cls_path)),
            parent=self._parent(raw.get("parent"), key),
            requires=_as_str_mapping(raw.get("requires"), f"{key}.requires"),
            as_parent=(
                _as_str_mapping(raw["as_parent"], f"{key}.as_parent")
                if "as_parent" in raw
                else None
            ),
            props=_as_str_mapping(raw.get("props"), f"{key}.props"),
            emit_parents=_is_true(raw.get("emit_parents")),
            children=self._children(raw.get("children"), key),
            when=str(raw["when"]) if "when" in raw else None,
            list=self._list(raw.get("list"), key),
        )

    def _parent(self, raw: Any, key: str) -> str | ParentRef | None:
        if raw is None:
            return None
        if isinstance(raw, dict):
            ref = raw.get("ref")
            if not ref:
                raise DataError(f"Entry '{key}' parent is missing 'ref'.")
            override = (
                _as_str_mapping(raw["as_parent"], f"{key}.parent.as_parent")
                if "as_parent" in raw
                else None
            )
            return ParentRef(ref=str(ref), as_parent=override)
        return str(raw)

    def _children(self, raw: Any, key: str) -> dict[str, NodeSpec] | list[NodeSpec]:
        if raw is None:
            return {}
        if isinstance(raw, list):
            return [
                self._node(self._child_key(child, index), child)
                for index, child in enumerate(raw)
            ]
        if isinstance(raw, dict):
            return {str(name): self._node(str(name), child) for name, child in raw.items()}
        raise DataError(f"Entry '{key}' children must be a mapping or a sequence.")

    @staticmethod
    def _child_key(child: Any, index: int) -> str:
        if isinstance(child, dict) and child.get("class"):
            return str(child["class"]).split(".")[-1].lower()
        return f"child_{index}"

    def _list(self, raw: Any, key: str) -> ListSpec | None:
        if raw is None:
            return None
        mapping = _as_mapping(raw, f"{key}.list")
        source = mapping.get("from")
        bind = mapping.get("bind")
        if not source or not bind:
            raise DataError(f"Entry '{key}' list requires 'from' and 'bind'.")
        return ListSpec(
            source=str(source),
            bind=str(bind),
            split=str(mapping.get("split", ",")),
            expand=_is_true(mapping.get("range")),
        )
