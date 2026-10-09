"""Cobra model builder for devaci."""

from __future__ import annotations

from typing import Any

import cobra.mit.request
import cobra.model.pol

from devaci.cobra.base import config_json, config_xml
from devaci.cobra.builders import BUILDERS
from devaci.console import get_logger
from devaci.results import CobraResult

logger = get_logger(__name__)


class CobraBuilder:
    """Build an ACI configuration (:class:`ConfigRequest`) from a rendered dict.

    The dict's top-level keys map to registered handlers (see
    :mod:`devaci.cobra.builders`). Each handler receives the builder and the
    list of objects and is responsible for adding Mo instances to
    :attr:`config`.

    A builder is **cumulative**: every object added by :meth:`render` stays in
    the same :class:`ConfigRequest` rooted at :attr:`uni`, so several renders
    (e.g. several templates) build one tree that is committed once. To start a
    fresh tree, create a new :class:`CobraBuilder`; devaci never clears the
    accumulated tree.
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
        return config_xml(self.config)

    @property
    def json(self) -> dict[str, Any] | None:
        """Return the rendered JSON payload as a dict, or None when the config is empty."""
        return config_json(self.config)

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

            handler = BUILDERS.get(key)
            if handler is None:
                success = False
                msg = f"Class {key} does not exist."
                logger.warning("%s", msg)
                logs.append(msg)
                continue

            try:
                handler(self, value)
                msg = f"Class {key} rendered successfully."
                logger.info("%s", msg)
                logs.append(msg)
            except Exception as exc:
                success = False
                msg = f"Class {key} failed: {exc}"
                logger.exception("%s", msg)
                logs.append(msg)

        if not self.config.configMos:
            success = False
            msg = "No object was found in configuration."
            logger.warning("%s", msg)
            logs.append(msg)

        self.result = CobraResult(success=success, log=logs, config=self.config)
        return self.result
