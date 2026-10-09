"""YAML loading that deliberately avoids type coercion.

APIC values are kept as their original strings: YAML ints/floats/bools are
NOT converted to Python types, and ``nan`` strings are normalised to ``""``.
"""

from __future__ import annotations

from typing import Any

from yaml import load
from yaml.composer import Composer
from yaml.constructor import SafeConstructor
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner

from devaci._values import is_nan_text


def no_convert_int_constructor(loader: Any, node: Any) -> Any:
    """Keep YAML integers as their original string."""
    return node.value


def no_convert_float_constructor(loader: Any, node: Any) -> Any:
    """Keep YAML floats as their original string."""
    return node.value


def replace_str_nan_with_empty(obj: Any) -> Any:
    """Recursively replace string values equal to ``nan`` with ``""``."""
    if isinstance(obj, dict):
        return {k: replace_str_nan_with_empty(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [replace_str_nan_with_empty(v) for v in obj]
    if is_nan_text(obj):
        return ""
    return obj


class _SafeConstructor(SafeConstructor):
    pass


def bool_constructor(loader: Any, node: Any) -> Any:
    """Keep YAML booleans as their original string."""
    return loader.construct_scalar(node)


_SafeConstructor.add_constructor("tag:yaml.org,2002:bool", bool_constructor)


class SafeLoader(Reader, Scanner, Parser, Composer, _SafeConstructor, Resolver):
    """YAML loader that leaves int/float/bool values as strings."""

    def __init__(self, stream: Any) -> None:
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        _SafeConstructor.__init__(self)
        Resolver.__init__(self)


SafeLoader.add_constructor("tag:yaml.org,2002:int", no_convert_int_constructor)
SafeLoader.add_constructor("tag:yaml.org,2002:float", no_convert_float_constructor)

for _first_char, _resolvers in list(SafeLoader.yaml_implicit_resolvers.items()):
    _filtered = [r for r in _resolvers if r[0] != "tag:yaml.org,2002:bool"]
    if _filtered:
        SafeLoader.yaml_implicit_resolvers[_first_char] = _filtered
    else:
        del SafeLoader.yaml_implicit_resolvers[_first_char]


def load_yaml(stream: Any) -> Any:
    """Load YAML without type coercion and normalise ``nan`` strings."""
    return replace_str_nan_with_empty(load(stream, SafeLoader))  # type: ignore[arg-type]
