"""Cobra model builder for devaci."""

from __future__ import annotations

import json
from typing import Any, cast

import cobra.mit.request
import cobra.model.pol

from devaci.cobra.registry import REGISTRY
from devaci.console import logger
from devaci.results import CobraResult


class CobraBuilder:
    """Build an ACI configuration (:class:`ConfigRequest`) from a rendered dict.

    The dict's top-level keys map to registered handlers (see
    :mod:`devaci.cobra.builders`). Each handler receives the builder and the
    list of objects and is responsible for adding Mo instances to
    :attr:`config`.
    """

    def __init__(self) -> None:
        self._root = ""
        self._uni = cobra.model.pol.Uni(self._root)
        self.config = cobra.mit.request.ConfigRequest()
        self.result: CobraResult | None = None

    @property
    def root(self) -> str:
        """Return the ACI root (policy universe DN)."""
        return self._root

    @property
    def uni(self) -> cobra.model.pol.Uni:
        """Return the root ``pol.Uni`` managed object."""
        return self._uni

    @property
    def xml(self) -> str | None:
        """Return the rendered XML payload, or None when the config is empty."""
        if not self.config.configMos:
            return None
        return cast(str | None, self.config.xmldata)

    @property
    def json(self) -> Any:
        """Return the rendered JSON payload as a dict, or None when the config is empty."""
        if not self.config.configMos:
            return None
        return json.loads(self.config.data)

    def render(self, output: dict[str, Any]) -> CobraResult:
        """Render ``output`` through the registered handlers.

        Keys with empty values are skipped; unknown keys and handler errors
        are logged and reported via the returned :class:`CobraResult`.
        """
        logs: list[str] = []
        success = True

        for key, value in output.items():
            if value in (None, [], {}, ""):
                continue

            handler = REGISTRY.get(key)
            if handler is None:
                success = False
                msg = f"[Cobra] -> [ConfigError]: Class {key} does not exist."
                logger.warning(msg)
                logs.append(msg)
                continue

            try:
                handler(self, value)
                msg = f"[Cobra]: Class {key} was rendered successfully."
                logger.info(msg)
                logs.append(msg)
            except Exception as exc:
                success = False
                msg = f"[Cobra] -> [{type(exc).__name__}]: Class {key} failed: {exc}"
                logger.error(msg)
                logs.append(msg)

        if not self.config.configMos:
            success = False
            msg = "[Cobra] -> [ConfigError]: No object was found in configuration."
            logger.warning(msg)
            logs.append(msg)

        self.result = CobraResult(success=success, log=logs, config=self.config)
        return self.result


from devaci.cobra import builders  # noqa: E402, F401
