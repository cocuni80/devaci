"""Deployment orchestrator for devaci."""

from __future__ import annotations

import getpass
from pathlib import Path
from typing import Any

from devaci.cobra import CobraBuilder
from devaci.config import DeployConfig
from devaci.console import get_logger
from devaci.exceptions import DeployError
from devaci.inputs.datasets import DataLoader
from devaci.inputs.templates import TemplateSource
from devaci.output.runlog import RunLog
from devaci.output.writer import OutputWriter
from devaci.rendering.jinja import JinjaRenderer
from devaci.results import DeployResult, Result
from devaci.transport.apic import ApicSession

logger = get_logger(__name__)


class DeployClass:
    """Deployment manager for Cisco ACI using the Cobra SDK.

    Thin orchestrator that wires the pipeline components together: template
    rendering (:class:`~devaci.rendering.jinja.JinjaRenderer`), Cobra model
    rendering (:class:`~devaci.cobra.CobraBuilder`), input loading
    (:class:`~devaci.inputs.datasets.DataLoader`), output
    (:class:`~devaci.output.writer.OutputWriter`), history
    (:class:`~devaci.output.runlog.RunLog`) and the APIC commit
    (:class:`~devaci.transport.apic.ApicSession`).

    Configured through a typed :class:`~devaci.config.DeployConfig`; the legacy
    keyword-argument form (``DeployClass(**kwargs)``) is still supported.
    """

    def __init__(self, config: DeployConfig | None = None, **kwargs: Any) -> None:
        if config is not None and kwargs:
            raise TypeError("Pass either 'config' or keyword arguments, not both.")
        self._config = config if config is not None else DeployConfig.from_kwargs(**kwargs)

        self._testing = self._config.testing
        self._cobra = CobraBuilder()
        self._templates = TemplateSource(self._config.working_folder)
        self._data = DataLoader(
            self._config.working_folder,
            self._config.filters,
            self._config.filter_by,
            self._config.filters_source_sheet,
            self._config.filters_condition_field,
            self._config.filters_output_field,
        )
        self._writer = OutputWriter(self._config.working_folder, self._config.render_to_xml)
        self._runlog = RunLog(
            self._config.working_folder, self._config.logging_output, self._config.logging
        )
        self._results: list[dict[str, Any]] = []

    # ------------------------------------------------------------------ Control

    def deploy(self) -> None:
        """Execute the deployment workflow for all configured templates."""
        if not self._templates.templates:
            logger.warning("No templates configured.")
            return

        run_results: list[dict[str, Any]] = []
        for content, path in self._templates.templates:
            result = self._deploy_one(content, path).to_dict()
            self._results.append(result)
            run_results.append(result)

        if self._config.show_output:
            self.print_output()

        if self._config.file_output:
            self.save_output(self._config.file_output)

        all_success = bool(run_results) and all(result["success"] for result in run_results)
        if not self._testing and all_success:
            self._commit()

        if self._config.logging:
            self.save_logging()

    def _deploy_one(self, content: str, path: Path) -> DeployResult:
        name = path.name if isinstance(path, Path) else str(path)
        logs: list[str] = []
        success = False

        try:
            renderer = JinjaRenderer()
            output = renderer.render(content, **self._data.variables)
            logs.append(f"Template {name} rendered successfully (Jinja).")
            logger.info("Template %s rendered successfully (Jinja).", name)

            cobra_result = self._cobra.render(output)
            logs.extend(cobra_result.log)
            if not cobra_result.success:
                raise DeployError(f"Template {name} failed to render Cobra objects.")

            logs.append(f"Template {name} rendered successfully (Cobra).")
            logger.info("Template %s rendered successfully (Cobra).", name)
            success = True
        except Exception as exc:
            logs.append(f"Failed to render template {name}: {type(exc).__name__}.")
            logger.exception("Failed to render template %s.", name)

        return DeployResult(success=success, log=logs, path=str(path), name=name)

    def _build_apic(self) -> tuple[ApicSession, str | None]:
        """Build the APIC session, prompting for missing credentials interactively."""
        ip = self._config.ip
        username = self._config.username
        password = self._config.password

        if not self._testing:
            if not ip:
                ip = input("APIC IP Address: ").strip()
            if not username:
                username = input("APIC Username: ").strip()
            if not password:
                password = getpass.getpass("APIC Password: ")

        url = f"https://{ip}" if ip else None
        apic = ApicSession(
            url,
            username,
            password,
            self._config.secure,
            self._config.timeout,
            self._config.timer,
            ip,
        )
        return apic, ip

    def _commit(self) -> None:
        apic, ip = self._build_apic()
        try:
            apic.commit(self._cobra.config)
            msg = f"Configuration deployed successfully to APIC {ip}."
            logger.info("%s", msg)
            self._results.append(Result(success=True, log=[msg]).to_dict())
        except Exception as exc:
            msg = f"Unable to deploy to APIC {ip}: {type(exc).__name__}."
            logger.exception("%s", msg)
            self._results.append(Result(success=False, log=[msg]).to_dict())

    # ------------------------------------------------------------------ Output

    def save_output(self, name: str = "output") -> None:
        """Save rendered configuration to disk (XML or JSON)."""
        self._writer.save(self.config, name)

    def print_output(self, theme: str = "fruity", line_numbers: bool = True) -> None:
        """Pretty-print the rendered configuration to the terminal."""
        self._writer.show(self.config, theme=theme, line_numbers=line_numbers)

    def save_logging(self) -> None:
        """Append execution results to a JSON log file defensively."""
        self._runlog.save(self._results)

    # ------------------------------------------------------------------ Properties

    @property
    def results(self) -> list[dict[str, Any]]:
        return self._results

    @property
    def variables(self) -> dict[str, Any]:
        return self._data.variables

    @variables.setter
    def variables(self, value: dict[str, Any]) -> None:
        self._data.variables = value

    @property
    def template(self) -> list[tuple[str, Path]]:
        return self._templates.templates

    @template.setter
    def template(self, value: Any) -> None:
        self._templates.add(value)

    @property
    def config(self) -> str | dict[str, Any] | None:
        return self._cobra.xml if self._config.render_to_xml else self._cobra.json

    @property
    def csv(self) -> dict[str, Any]:
        return self._data.variables

    @csv.setter
    def csv(self, value: Any) -> None:
        """Load CSV file(s) into the variables dict."""
        self._data.add_csv(value)

    @property
    def xlsx(self) -> dict[str, Any]:
        return self._data.variables

    @xlsx.setter
    def xlsx(self, value: Any) -> None:
        """Load XLSX file(s) into the variables dict."""
        self._data.add_xlsx(value)
