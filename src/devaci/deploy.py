"""Deployment orchestration and run reporting for devaci."""

from __future__ import annotations

import getpass
import itertools
import sys
from collections.abc import Iterator
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from time import perf_counter
from typing import Any

from devaci.cobra import CobraBuilder
from devaci.cobra.builders import BUILDERS
from devaci.config import DeployConfig
from devaci.console import get_console, get_error_console, get_logger
from devaci.inputs.datasets import DataLoader
from devaci.inputs.templates import TemplateSource
from devaci.output.runlog import RunLog
from devaci.output.writer import OutputWriter
from devaci.rendering.jinja import JinjaRenderer
from devaci.rendering.sections import split_template
from devaci.results import DeployResult
from devaci.transport.apic import ApicSession

logger = get_logger(__name__)


def _version() -> str:
    try:
        return version("devaci")
    except PackageNotFoundError:
        return "0.0.0"


def _duration(seconds: float) -> str:
    return f"{round(seconds * 1000)}ms" if seconds < 1 else f"{seconds:.1f}s"


def _read_key() -> str:
    """Read a single keypress without Enter, returning ``""`` when unavailable."""
    try:
        import termios
        import tty
    except ImportError:  # pragma: no cover - Windows
        try:
            import msvcrt
        except ImportError:
            return ""
        getwch = getattr(msvcrt, "getwch", None)
        return str(getwch()) if getwch is not None else ""

    try:
        old = termios.tcgetattr(sys.stdin.fileno())
    except (termios.error, ValueError, OSError):
        return ""
    try:
        tty.setraw(sys.stdin.fileno())
        return sys.stdin.read(1)
    except OSError:
        return ""
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)


class DeployClass:
    """Deployment orchestrator for Cisco ACI."""

    def __init__(self, config: DeployConfig | None = None, **kwargs: Any) -> None:
        """Configure the deployment.

        Renders Jinja2 templates against XLSX/CSV input and compiles the result into a
        Cobra ``ConfigRequest``, optionally committing it to an APIC.

        Configure it with a :class:`~devaci.config.DeployConfig` or the equivalent
        keyword arguments (all optional):

        - ``testing`` (bool, default ``False``): dry run; skips the commit and
          credential prompt.
        - ``ip`` / ``username`` / ``password`` (str, default ``None``): APIC
          access; prompted at commit when missing.
        - ``timeout`` (int, default ``180``) / ``connect_timeout`` (int, default
          ``5``): APIC read/connect timeouts in seconds.
        - ``secure`` (bool, default ``False``): verify the APIC TLS certificate.
        - ``timer`` (int, default ``5``): countdown seconds before committing.
        - ``show_output`` (bool, default ``False``): print the rendered
          configuration.
        - ``file_output`` (str, default ``None``): save the rendered
          configuration.
        - ``logging_output`` (str, default ``"outputs/logs/logging.json"``):
          run-history path (``.jsonl`` suffix added).
        - ``logging`` (bool, default ``True``): persist one run record per
          ``deploy()``.
        - ``show_report`` (bool, default ``True``): print a run report at the
          end of ``deploy()``.
        - ``verbose`` (bool, default ``False``): add per-class detail to the
          report.
        - ``render_to_xml`` (bool, default ``True``): render XML or JSON.
        - ``filters`` (list[str], default ``None``) / ``filter_by`` (str,
          default ``"tag"``): rows to keep.
        - ``filters_source_sheet`` (str, default ``None``) /
          ``filters_condition_field`` (str, default ``"enabled"``) /
          ``filters_output_field`` (str, default ``"name"``): derive the filters
          from a dedicated sheet.
        - ``working_folder`` (Path, default: current directory): base folder for
          data, outputs and history.

        Then drive it through the ``template``, ``xlsx``, ``csv`` and ``variables``
        properties and call :meth:`deploy`.
        """
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
        self._run: dict[str, Any] | None = None

    def deploy(self) -> None:
        """Run all configured templates and create one run record."""
        if not self._templates.templates:
            logger.warning("No templates configured.")
            self._results = []
            self._run = self._empty_run()
            if self._config.show_report:
                self.print_report()
            return
        started = perf_counter()
        self._results = []
        templates: list[dict[str, Any]] = []
        for content, path in self._templates.templates:
            record = self._deploy_one(content, path)
            templates.append(record)
            self._results.append(record)

        if self._config.show_output:
            self.print_output()
        if self._config.file_output:
            self.save_output(self._config.file_output)

        all_success = bool(templates) and all(template["success"] for template in templates)
        commit = self._commit() if not self._testing and all_success else None
        success = all_success and (commit is None or commit["success"])
        self._run = {
            "date": datetime.now().isoformat(timespec="seconds"),
            "version": _version(),
            "mode": "dry_run" if self._testing else "deploy",
            "filters": list(self._config.filters or []),
            "success": success,
            "duration_s": round(perf_counter() - started, 3),
            "templates": templates,
            "commit": commit,
        }
        if self._config.logging:
            self.save_logging()
        if self._config.show_report:
            self.print_report()

    def _empty_run(self) -> dict[str, Any]:
        return {
            "date": datetime.now().isoformat(timespec="seconds"),
            "version": _version(),
            "mode": "dry_run" if self._testing else "deploy",
            "filters": list(self._config.filters or []),
            "success": True,
            "duration_s": 0.0,
            "templates": [],
            "commit": None,
        }

    def _deploy_one(self, content: str, path: Path) -> dict[str, Any]:
        """Render one template and return its structured run template record."""
        name = path.name
        logs: list[dict[str, Any]] = []
        success = True
        before = len(self._cobra.config.configMos)
        started = perf_counter()
        try:
            renderer = JinjaRenderer()
            names = set(self._data.sheets) | set(BUILDERS)
            preamble, sections = split_template(content, names)
            data_keys = [key for key in sections if key in self._data.sheets]
            for sheet in sorted(set(self._data.sheets) - set(sections)):
                if self._data.sheets[sheet]:
                    logs.append(
                        {"level": "debug", "message": f"sheet '{sheet}' has no matching section"}
                    )
            if data_keys:
                success = self._render_sections(renderer, preamble, sections, name, logs)
            else:
                result = self._cobra.render(renderer.render(content, **self._data.variables))
                logs.extend(result.log)
                success = result.success
            if data_keys and len(self._cobra.config.configMos) == before:
                result = self._cobra.render({})
                logs.extend(result.log)
                success = success and result.success
        except Exception as exc:
            success = False
            message = f"failed to render template {name}: {exc}"
            logs.append(
                {
                    "level": "error",
                    "where": name,
                    "message": message,
                    "type": type(exc).__name__,
                    "cause": type(exc.__cause__).__name__ if exc.__cause__ else None,
                }
            )
            logger.exception("%s", message)
        record = DeployResult(success=success, log=logs, path=str(path), name=name).to_dict()
        record.pop("date")
        record["path"] = self._relative_path(path)
        record["objects"] = self._objects(logs)
        record["duration_s"] = round(perf_counter() - started, 3)
        return record

    def _render_sections(
        self,
        renderer: JinjaRenderer,
        preamble: str,
        sections: dict[str, str],
        name: str,
        logs: list[dict[str, Any]],
    ) -> bool:
        """Render every section and compile each sheet's objects separately."""
        success = True
        for key, fragment in sections.items():
            objects = self._render_objects(renderer, preamble, fragment, key)
            if not objects:
                continue
            result = self._cobra.render({key: objects})
            logs.extend(result.log)
            success = success and result.success
            logger.info("Template %s section %s rendered (%d objects).", name, key, len(objects))
        return success

    def _render_objects(
        self, renderer: JinjaRenderer, preamble: str, fragment: str, key: str
    ) -> list[dict[str, Any]]:
        """Render one section once per sheet row (or a single time for static ones)."""
        template = renderer.compile(preamble + fragment)
        rows = self._data.sheets.get(key)
        if rows is None:
            return list(renderer.render_template(template, **self._data.variables).get(key) or [])
        objects: list[dict[str, Any]] = []
        for row in rows:
            output = renderer.render_template(template, **{**self._data.variables, key: row})
            objects.extend(output.get(key) or [])
        return objects

    def _build_apic(self) -> tuple[ApicSession, str | None]:
        """Build the APIC session, prompting for missing credentials interactively."""
        ip, username, password = self._config.ip, self._config.username, self._config.password
        if not self._testing:
            if not ip:
                ip = input("APIC IP Address: ").strip()
            if not username:
                username = input("APIC Username: ").strip()
            if not password:
                password = getpass.getpass("APIC Password: ")
        apic = ApicSession(
            f"https://{ip}" if ip else None,
            username,
            password,
            self._config.secure,
            (self._config.connect_timeout, self._config.timeout),
            self._config.timer,
            ip,
        )
        return apic, ip

    def _commit(self) -> dict[str, Any]:
        started = perf_counter()
        apic, ip = self._build_apic()
        objects = len(self._cobra.config.configMos)
        endpoint = f"APIC {ip}" if ip else "APIC"
        try:
            apic.commit(self._cobra.config)
            logger.info("Configuration deployed successfully to %s.", endpoint)
            return {
                "success": True,
                "endpoint": endpoint,
                "objects": objects,
                "duration_s": round(perf_counter() - started, 3),
                "log": [{"level": "info", "message": "committed", "objects": objects}],
            }
        except Exception as exc:
            message = f"failed to deploy to {endpoint}: {exc}"
            logger.exception("%s", message)
            return {
                "success": False,
                "endpoint": endpoint,
                "objects": objects,
                "duration_s": round(perf_counter() - started, 3),
                "log": [
                    {
                        "level": "error",
                        "message": message,
                        "type": type(exc).__name__,
                        "cause": type(exc.__cause__).__name__ if exc.__cause__ else None,
                    }
                ],
            }

    def save_output(self, name: str = "output") -> None:
        """Save the rendered configuration to disk (XML or JSON)."""
        self._writer.save(self.config, name)

    def print_output(self, theme: str = "fruity", line_numbers: bool = True) -> None:
        """Pretty-print the rendered configuration to the terminal."""
        self._writer.show(self.config, theme=theme, line_numbers=line_numbers)

    def save_logging(self) -> None:
        """Append the current run record to the JSON Lines history defensively."""
        if self._run is not None:
            self._runlog.save(self._run)

    def print_report(self) -> None:
        """Print the latest run, preferring the in-memory record over the file."""
        record = self._run or self._runlog.last()
        if record is not None:
            self._format_run(record)

    def print_reports(self, limit: int = 5, paginate: bool = True) -> None:
        """Print the run history, newest first.

        With ``paginate=True`` (default) shows the ``limit`` (default 5) most
        recent runs and waits for SPACE to continue with older ones until the
        history ends. With ``paginate=False`` prints every run without prompting.
        """
        if not paginate:
            for record in self._iter_history():
                self._format_run(record)
            return

        history = self._iter_history()
        interactive = sys.stdin.isatty()
        while True:
            batch = list(itertools.islice(history, limit))
            if not batch:
                break
            for record in batch:
                self._format_run(record)
            remaining = next(history, None)
            if remaining is None:
                break
            history = itertools.chain([remaining], history)
            if not interactive:
                get_console().print(
                    "... older runs not shown (use print_reports(paginate=False))",
                    markup=False,
                )
                break
            get_console().print("Press SPACE for older runs, any other key to stop...", end="")
            key = _read_key()
            get_console().print()
            if key != " ":
                break

    def _iter_history(self) -> Iterator[dict[str, Any]]:
        """Yield run records newest first from the file, or the in-memory run.

        Reading the history is independent of the ``logging`` persistence flag:
        the file is used whenever it exists, otherwise the in-memory run.
        """
        if self._runlog.path.exists():
            return self._runlog.iter_runs(reverse=True)
        if self._run is not None:
            return iter([self._run])
        return iter(())

    def _format_run(self, record: dict[str, Any]) -> None:
        """Render one run record to the console, sending failures to stderr."""
        out, err = get_console(), get_error_console()
        mode = "dry run" if record.get("mode") == "dry_run" else "deploy"
        out.print(f"devaci {record.get('version', '?')} · {mode} · {record.get('date', '')}")
        filters = record.get("filters") or []
        if filters:
            out.print(f"Filters: {', '.join(filters)}")

        templates = record.get("templates", [])
        for template in templates:
            self._format_template(template, out, err)
        self._print_commit(record, out, err)

        target = out if record.get("success") else err
        target.print()
        if not templates:
            target.print("Result: OK · nothing to do")
            return
        succeeded = sum(1 for template in templates if template.get("success"))
        if record.get("mode") == "dry_run":
            ending = "dry run"
        elif record.get("success"):
            ending = "committed"
        else:
            ending = "nothing committed"
        target.print(
            f"Result: {'OK' if record.get('success') else 'FAILED'} · {succeeded} of "
            f"{len(templates)} templates succeeded · {ending}"
        )

    def _format_template(self, template: dict[str, Any], out: Any, err: Any) -> None:
        success = template.get("success", False)
        target = out if success else err
        status = "[green]✔ SUCCESS[/green]" if success else "[red]✘ FAILED[/red]"
        target.print()
        target.print(template.get("name", "template"), markup=False)
        target.print(f"  Status:     {status}")
        target.print(f"  Objects:    {template.get('objects', 0)}")
        target.print(f"  Duration:   {_duration(template.get('duration_s', 0.0))}")
        log = template.get("log", [])
        warnings = self._events(log, "warning")
        if warnings:
            target.print(
                f"  Warnings:   {len(warnings)} · {warnings[0].get('message', '')}",
                markup=False,
            )
        for error in self._events(log, "error"):
            target.print(
                f"  Error:      {error.get('type', 'Error')}: {error.get('message', '')}",
                markup=False,
            )
        if self._config.verbose:
            for event in log:
                where = event.get("where")
                objects = event.get("objects")
                prefix = f"{where}: " if where else ""
                suffix = f" ({objects} objects)" if objects is not None else ""
                message = event.get("message", "")
                target.print(
                    f"  {event.get('level', 'info').title()}: {prefix}{message}{suffix}",
                    markup=False,
                )

    def _print_commit(self, record: dict[str, Any], out: Any, err: Any) -> None:
        commit = record.get("commit")
        if commit is None:
            return
        success = commit.get("success", False)
        target = out if success else err
        status = "[green]✔ SUCCESS[/green]" if success else "[red]✘ FAILED[/red]"
        target.print()
        target.print("commit")
        target.print(f"  Status:     {status}")
        target.print(f"  Endpoint:   {commit.get('endpoint', '')}", markup=False)
        target.print(f"  Objects:    {commit.get('objects', 0)}")
        target.print(f"  Duration:   {_duration(commit.get('duration_s', 0.0))}")
        for error in self._events(commit.get("log", []), "error"):
            target.print(
                f"  Error:      {error.get('type', 'Error')}: {error.get('message', '')}",
                markup=False,
            )

    @staticmethod
    def _events(log: list[dict[str, Any]], level: str) -> list[dict[str, Any]]:
        """Return the log events with the given ``level``."""
        return [event for event in log if event.get("level") == level]

    @staticmethod
    def _objects(log: list[dict[str, Any]]) -> int:
        """Sum the objects reported by the info events of ``log``."""
        return sum(int(event.get("objects", 0)) for event in log if event.get("level") == "info")

    def _relative_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self._config.working_folder))
        except ValueError:
            return str(path)

    @property
    def results(self) -> list[dict[str, Any]]:
        """Per-template records of the most recent ``deploy()``."""
        return self._results

    @property
    def run(self) -> dict[str, Any] | None:
        """Run record of the most recent ``deploy()`` (or ``None``)."""
        return self._run

    @property
    def success(self) -> bool:
        """Whether the most recent run rendered (and committed) successfully."""
        return bool(self._run and self._run["success"])

    @property
    def variables(self) -> dict[str, Any]:
        """Scalar variables available to every render."""
        return self._data.variables

    @variables.setter
    def variables(self, value: dict[str, Any]) -> None:
        """Set scalar variables available to every render."""
        self._data.variables = value

    @property
    def template(self) -> list[tuple[str, Path]]:
        """Configured templates as ``(content, path)`` pairs."""
        return self._templates.templates

    @template.setter
    def template(self, value: Any) -> None:
        """Append template(s) from a filename, list, or ``(content, name)``."""
        self._templates.add(value)

    @property
    def config(self) -> str | dict[str, Any] | None:
        """Rendered configuration (XML string or JSON dict) of the run."""
        return self._cobra.xml if self._config.render_to_xml else self._cobra.json

    @property
    def csv(self) -> dict[str, list[dict[str, Any]]]:
        """Loaded CSV sheet rows, keyed by file stem."""
        return self._data.sheets

    @csv.setter
    def csv(self, value: Any) -> None:
        """Load CSV file(s) into the sheets mapping."""
        self._data.add_csv(value)

    @property
    def xlsx(self) -> dict[str, list[dict[str, Any]]]:
        """Loaded XLSX sheet rows, keyed by sheet name."""
        return self._data.sheets

    @xlsx.setter
    def xlsx(self, value: Any) -> None:
        """Load XLSX file(s) into the sheets mapping."""
        self._data.add_xlsx(value)
