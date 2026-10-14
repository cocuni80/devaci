"""Execute the declarative schema against loaded sheet rows."""

from __future__ import annotations

from typing import Any

from devaci._values import is_empty, normalize
from devaci.exceptions import DataError
from devaci.rendering.filters import range_filter
from devaci.rendering.jinja import JinjaRenderer
from devaci.schema.spec import ListSpec, NodeSpec, ParentRef, Schema

__all__ = ["SchemaEngine"]

_SKIP = object()
"""Sentinel returned by parent resolution when the parent's gate fails."""

_MISSING = object()
"""Sentinel meaning 'resolve the parent from the node spec'."""


class SchemaEngine:
    """Build Cobra managed objects from a :class:`Schema` and sheet rows."""

    def __init__(
        self,
        schema: Schema,
        variables: dict[str, Any],
        renderer: JinjaRenderer | None = None,
    ) -> None:
        self._schema = schema
        self._variables = variables
        self._renderer = renderer or JinjaRenderer()

    def run(self, builder: Any, sheets: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
        """Build every schema entry whose key matches a loaded sheet.

        Returns the structured log events (one ``info`` event per non-empty
        entry, one ``error`` event per failed row).
        """
        logs: list[dict[str, Any]] = []
        for key, node in self._schema.nodes.items():
            rows = sheets.get(key)
            if rows is None:
                continue
            count = 0
            for row in rows:
                context = self._context(key, row)
                try:
                    count += self._build(builder, node, row, context, auto=True)
                except Exception as exc:
                    logs.append(
                        {
                            "level": "error",
                            "where": key,
                            "message": f"failed to build {key}: {exc}",
                            "type": type(exc).__name__,
                        }
                    )
            if count:
                logs.append(
                    {"level": "info", "where": key, "message": "rendered", "objects": count}
                )
        return logs

    def _build(
        self,
        builder: Any,
        node: NodeSpec,
        row: dict[str, Any],
        context: dict[str, Any],
        auto: bool,
        parent_mo: Any = _MISSING,
    ) -> int:
        if node.list is not None:
            return self._build_list(builder, node, row, context, auto, parent_mo)
        return self._build_node(builder, node, row, context, auto, parent_mo)

    def _build_list(
        self,
        builder: Any,
        node: NodeSpec,
        row: dict[str, Any],
        context: dict[str, Any],
        auto: bool,
        parent_mo: Any = _MISSING,
    ) -> int:
        assert node.list is not None
        total = 0
        for item in self._expand(node.list, context):
            item_row = {**row, node.list.bind: item}
            item_context = {**context, node.list.bind: item, node.key: item_row}
            total += self._build_node(builder, node, item_row, item_context, auto, parent_mo)
        return total

    def _build_node(
        self,
        builder: Any,
        node: NodeSpec,
        row: dict[str, Any],
        context: dict[str, Any],
        auto: bool,
        parent_mo: Any = _MISSING,
    ) -> int:
        if node.when is not None and not self._truthy(self._render(node.when, context)):
            return 0
        if any(is_empty(self._render(expr, context)) for expr in node.requires.values()):
            return 0
        if parent_mo is _MISSING:
            parent_mo = self._parent_mo(builder, node.parent, context, node.emit_parents)
            if parent_mo is _SKIP:
                return 0
        kwargs = self._self_kwargs(node, row, context, auto)
        mo = node.cls(parent_mo if parent_mo is not None else "", **kwargs)
        builder.add(mo)
        count = 1
        for child in self._iter_children(node):
            count += self._build(builder, child, row, context, auto=False, parent_mo=mo)
        return count

    def _parent_mo(
        self, builder: Any, parent: Any, context: dict[str, Any], emit: bool = False
    ) -> Any:
        if parent is None:
            return None
        if isinstance(parent, ParentRef):
            ref_key, override = parent.ref, parent.as_parent
        else:
            ref_key, override = str(parent), None
        ref = self._schema.nodes.get(ref_key)
        if ref is None:
            raise DataError(f"unknown parent reference {ref_key!r}")
        if ref.cls_path == "pol.Uni":
            return builder.uni
        binding = dict(ref.as_parent if ref.as_parent is not None else ref.requires)
        if override:
            binding.update(override)
        kwargs = {
            name: normalize(self._render(expr, context)) for name, expr in binding.items()
        }
        if any(is_empty(value) for value in kwargs.values()):
            return _SKIP
        grand = self._parent_mo(builder, ref.parent, context, emit)
        if grand is _SKIP:
            return _SKIP
        mo = ref.cls(grand if grand is not None else "", **kwargs)
        if emit:
            builder.add(mo)
        return mo

    def _self_kwargs(
        self,
        node: NodeSpec,
        row: dict[str, Any],
        context: dict[str, Any],
        auto: bool,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        if auto:
            valid = self._valid_props(node.cls)
            for name, value in row.items():
                if name in valid:
                    kwargs[name] = normalize(str(value))
        for name, expr in node.props.items():
            kwargs[name] = normalize(self._render(expr, context))
        for name, expr in node.requires.items():
            kwargs[name] = normalize(self._render(expr, context))
        return kwargs

    @staticmethod
    def _valid_props(cls: Any) -> set[str]:
        props = getattr(getattr(cls, "meta", None), "props", None)
        if props is None:
            return set()
        try:
            return set(props.keys())
        except AttributeError:
            return {prop.name for prop in props}

    @staticmethod
    def _iter_children(node: NodeSpec) -> list[NodeSpec]:
        if isinstance(node.children, dict):
            return list(node.children.values())
        return list(node.children)

    def _expand(self, spec: ListSpec, context: dict[str, Any]) -> list[Any]:
        raw = context.get(spec.source)
        if raw is None and ("{{" in spec.source or "{%" in spec.source):
            raw = self._render(spec.source, context)
        if is_empty(raw):
            return []
        if spec.expand:
            return list(range_filter(raw))
        return str(raw).split(spec.split)

    def _render(self, expression: str, context: dict[str, Any]) -> str:
        return self._renderer.compile(expression).render(**context)

    @staticmethod
    def _truthy(text: str) -> bool:
        folded = text.strip().lower()
        return bool(folded) and folded not in ("false", "0", "no", "nan", "none")

    def _context(self, key: str, row: dict[str, Any]) -> dict[str, Any]:
        return {**self._variables, key: row, **row}
