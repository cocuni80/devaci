"""APIC session handling for devaci."""

from __future__ import annotations

import contextlib
import time
from typing import Any

import cobra.mit.access
import cobra.mit.session

from devaci.console import get_console, get_logger

logger = get_logger(__name__)


class ApicSession:
    """Owns the Cobra login session and commits configuration to an APIC.

    Wraps ``LoginSession``/``MoDirectory`` so the deployment orchestrator does
    not manage the session lifecycle itself.
    """

    def __init__(
        self,
        url: str | None,
        username: str | None,
        password: str | None,
        secure: bool,
        timeout: int,
        timer: int,
        ip: str | None,
    ) -> None:
        self._ip = ip
        self._timer = timer
        if not secure:
            logger.warning("TLS certificate verification is disabled (secure=False).")
            self._disable_tls_warnings()
        self._session = cobra.mit.session.LoginSession(url, username, password, secure, timeout)
        self._modir = cobra.mit.access.MoDirectory(self._session)

    @staticmethod
    def _disable_tls_warnings() -> None:
        """Silence urllib3's InsecureRequestWarning for unverified TLS sessions."""
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def commit(self, config: Any) -> None:
        """Log in, commit ``config`` and log out, raising on failure.

        A countdown is shown first so the operator can abort before the commit.
        """
        try:
            self._countdown()
            self._modir.login()
            self._modir.commit(config)
        finally:
            with contextlib.suppress(Exception):
                self._modir.logout()

    def _countdown(self) -> None:
        console = get_console()
        message = f"Deploying templates to APIC [{self._ip}] in"
        for remaining in range(self._timer, -1, -1):
            console.print(f"{message} {remaining} seconds", end="\r", markup=False)
            time.sleep(1)
        console.print()
