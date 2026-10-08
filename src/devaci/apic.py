"""APIC session handling for devaci."""

from __future__ import annotations

import contextlib
import sys
import time
from typing import Any

import cobra.mit.access
import cobra.mit.session
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
        self._session = cobra.mit.session.LoginSession(url, username, password, secure, timeout)
        self._modir = cobra.mit.access.MoDirectory(self._session)

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
        message = f"Deploying templates to APIC [{self._ip}] in"
        for remaining in range(self._timer, -1, -1):
            sys.stdout.write(f"\r{message} {remaining} seconds")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\n")
