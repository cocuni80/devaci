"""Deployment orchestrator for devaci."""

from __future__ import annotations

import contextlib
import getpass
import json
import sys
import time
import xml.dom.minidom
from datetime import datetime
from pathlib import Path
from typing import Any

import cobra.mit.access
import cobra.mit.session
import urllib3

from devaci.cobra import CobraBuilder
from devaci.console import logger, print_syntax
from devaci.data import load_csv, load_xlsx
from devaci.exceptions import DeployError
from devaci.jinja import JinjaRenderer
from devaci.results import DeployResult

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DeployClass:
    """Deployment manager for Cisco ACI using the Cobra SDK.

    Handles the full workflow: template rendering, Cobra model rendering,
    optional input filtering, output visualization/persistence, and optional
    commit to APIC.

    Configuration options:
    - ip (str): APIC IPv4 address
    - username (str): APIC username
    - password (str): APIC password
    - testing (bool): enable dry-run mode (default: False)
    - filter_by (str): variable name used for filtering (default: "tag")
    - timer (int): countdown in seconds before commit (default: 5)
    - show_output (bool): pretty-print rendered output to the terminal
    - file_output (str): output filename (JSON or XML)
    - secure (bool): verify SSL certificates (default: False)
    - render_to_xml (bool): render output as XML instead of JSON (default: True)
    - working_folder (Path): base directory for templates and data files
    - logging_output (str): logging filename (default: "outputs/logs/logging.json")
    - logging (bool): enable execution logging to file
    """

    def __init__(self, **kwargs: Any) -> None:
        self._testing = kwargs.get("testing", False)

        self._ip = kwargs.get("ip")
        self._username = kwargs.get("username")
        self._password = kwargs.get("password")

        if not self._testing:
            if not self._ip:
                self._ip = input("APIC IP Address: ").strip()
            if not self._username:
                self._username = input("APIC Username: ").strip()
            if not self._password:
                self._password = getpass.getpass("APIC Password: ")

        self._url = f"https://{self._ip}" if self._ip else None
        self._timeout = kwargs.get("timeout", 180)
        self._secure = kwargs.get("secure", False)
        self._timer = kwargs.get("timer", 5)
        self._show_output = kwargs.get("show_output", False)
        self._file_output = kwargs.get("file_output")
        self._logging_output = kwargs.get("logging_output", "outputs/logs/logging.json")
        self._logging = kwargs.get("logging", True)
        self._render_to_xml = kwargs.get("render_to_xml", True)
        self._filters_source_sheet = kwargs.get("filters_source_sheet")
        self._filters_condition_field = kwargs.get("filters_condition_field", "enabled")
        self._filters_output_field = kwargs.get("filters_output_field", "name")
        self._filters = kwargs.get("filters")
        self._filter_by = kwargs.get("filter_by", "tag")
        self._working_folder: Path = kwargs.get("working_folder", Path.cwd())

        self._cobra = CobraBuilder()
        self._session = cobra.mit.session.LoginSession(
            self._url, self._username, self._password, self._secure, self._timeout
        )
        self._modir = cobra.mit.access.MoDirectory(self._session)

        self._template: list[tuple[str, Path]] = []
        self._variables: dict[str, Any] = {}
        self._results: list[dict[str, Any]] = []

    # ------------------------------------------------------------------ Control

    def deploy(self) -> None:
        """Execute the deployment workflow for all configured templates."""
        if not self._template:
            logger.warning("[Deploy] -> [ConfigError]: No templates configured!")
            return

        for content, path in self._template:
            self._results.append(self._deploy_one(content, path).to_dict())

        if self._show_output:
            self.print_output()

        if self._file_output:
            self.save_output(self._file_output)

        if not self._testing and self._cobra.result is not None and self._cobra.result.success:
            self._commit()

        if self._logging:
            self.save_logging()

    def _deploy_one(self, content: str, path: Path) -> DeployResult:
        name = path.name if isinstance(path, Path) else str(path)
        logs: list[str] = []
        success = False

        try:
            renderer = JinjaRenderer()
            output = renderer.render(content, name=name, **self._variables)
            logs.append(f"[Jinja]: Template {name} was rendered successfully.")
            logger.info(logs[-1])

            cobra_result = self._cobra.render(output)
            logs.extend(cobra_result.log)
            if not cobra_result.success:
                raise DeployError(f"Template {name} failed to render Cobra objects.")

            logs.append(f"[Deploy]: Template {name} was rendered successfully.")
            logger.info(logs[-1])
            success = True
        except Exception as exc:
            logs.append(f"[Deploy] -> [{type(exc).__name__}]: Failed to render template {name}.")
            logger.error(
                f"[Deploy] -> [{type(exc).__name__}]: Failed to render template {name}: {exc}"
            )

        return DeployResult(success=success, log=logs, path=str(path), name=name)

    def _commit(self) -> None:
        try:
            self._countdown()
            self._modir.login()
            self._modir.commit(self._cobra.config)
            msg = f"[Deploy]: Template was successfully deployed to APIC: {self._ip}."
            logger.info(msg)
            self._results.append(
                {"date": datetime.now().strftime("%d/%m/%Y-%H:%M:%S"), "success": True, "log": msg}
            )
        except Exception as exc:
            msg = f"[Deploy] -> [{type(exc).__name__}]: Unable to deploy to APIC: {self._ip}, {exc}"
            logger.error(msg)
            self._results.append(
                {"date": datetime.now().strftime("%d/%m/%Y-%H:%M:%S"), "success": False, "log": msg}
            )
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

    # ------------------------------------------------------------------ Output

    def save_output(self, name: str = "output") -> None:
        """Save rendered configuration to disk (XML or JSON)."""
        content = self.config
        if content is None:
            return

        suffix = "xml" if self._render_to_xml else "json"
        output_path = self._working_folder / f"{name}.{suffix}"
        try:
            if self._render_to_xml:
                dom = xml.dom.minidom.parseString(content)
                text = dom.toprettyxml(indent="\t")
            else:
                text = json.dumps(content, indent=4, ensure_ascii=False)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text, encoding="utf-8")
        except Exception as exc:
            logger.error(f"[SaveOutputError]: Failed to save output file! {exc}")

    def print_output(self, theme: str = "fruity", line_numbers: bool = True) -> None:
        """Pretty-print the rendered configuration to the terminal."""
        content = self.config
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
        except Exception as exc:
            logger.error(f"[PrintOutputError]: Error printing output! {exc}")

    def save_logging(self) -> None:
        """Append execution results to a JSON log file defensively."""
        if not self._logging:
            return

        log_file = Path(self._working_folder / self._logging_output).with_suffix(".json")
        history: list[Any] = []
        try:
            if log_file.exists():
                try:
                    with open(log_file, encoding="utf-8") as handle:
                        history = json.load(handle)
                        if not isinstance(history, list):
                            history = []
                except json.JSONDecodeError:
                    history = []

            history.extend(self._results)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, "w", encoding="utf-8") as handle:
                json.dump(history, handle, indent=4, ensure_ascii=False)
        except Exception as exc:
            logger.error(f"[LoggingError]: {type(exc).__name__}: {exc}")

    # ------------------------------------------------------------------ Properties

    @property
    def results(self) -> list[dict[str, Any]]:
        return self._results

    @property
    def variables(self) -> dict[str, Any]:
        return self._variables

    @variables.setter
    def variables(self, value: dict[str, Any]) -> None:
        self._variables = value

    @property
    def template(self) -> list[tuple[str, Path]]:
        return self._template

    @template.setter
    def template(self, value: Any) -> None:
        """Load template content into memory.

        Accepted inputs:
        - str: template filename (loaded from working_folder)
        - list[str]: multiple template filenames
        - tuple[str, str]: (template_content, template_name)
        - list[tuple[str, str]]: multiple in-memory templates
        """
        if not value:
            return

        values = value if isinstance(value, list) else [value]
        for item in values:
            try:
                if isinstance(item, tuple) and len(item) == 2:
                    content, name = item
                    if not isinstance(content, str) or not isinstance(name, str):
                        raise ValueError("Template content and name must be strings")
                    self._template.append((content, Path(name)))
                elif isinstance(item, str):
                    path = self._working_folder / item
                    with open(path, encoding="utf-8") as handle:
                        self._template.append((handle.read(), path))
                else:
                    raise ValueError("Invalid template format")
            except Exception as exc:
                logger.error(f"[TemplateException]: Error loading template: {exc}")

    @property
    def config(self) -> Any:
        return self._cobra.xml if self._render_to_xml else self._cobra.json

    @property
    def csv(self) -> dict[str, Any]:
        return self._variables

    @csv.setter
    def csv(self, value: Any) -> None:
        """Load CSV file(s) into the variables dict."""
        files = [value] if isinstance(value, str) else value
        for file in files:
            try:
                self._variables |= load_csv(
                    self._working_folder / file, self._filters, self._filter_by
                )
            except Exception as exc:
                logger.error(f"[CSVException]: Error loading CSV file: {exc}")

    @property
    def xlsx(self) -> dict[str, Any]:
        return self._variables

    @xlsx.setter
    def xlsx(self, value: Any) -> None:
        """Load XLSX file(s) into the variables dict."""
        files = [value] if isinstance(value, str) else value
        for file in files:
            try:
                self._variables |= load_xlsx(
                    self._working_folder / file,
                    self._filters,
                    self._filter_by,
                    self._filters_source_sheet,
                    self._filters_condition_field,
                    self._filters_output_field,
                )
            except Exception as exc:
                logger.error(f"[XLSXException]: Error loading XLSX file '{file}': {exc}")
