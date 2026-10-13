# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-10-13

### Added

- Structured run reporting: `DeployClass.deploy()` builds one run record
  (version, mode, filters, per-template objects/duration and structured `log`
  events) and prints a summary by default (`show_report=True`; opt out with
  `show_report=False`, `verbose=True` for per-class detail).
- `DeployClass.print_report()` (latest run) and
  `DeployClass.print_reports(limit=5, paginate=True)` (history; press SPACE to
  page through older runs, `paginate=False` prints them all).
- `DeployClass.run`, `DeployClass.success` and `RunLog.iter_runs()`.
- Errors carry type, cause and message; `console.get_error_console()` sends
  report failures to stderr.

### Changed

- Rendering is per sheet: the shared template is split into per-class fragments
  (`rendering/sections.py`) and each sheet is rendered once per row and compiled
  separately onto the same `ConfigRequest`. Templates no longer need an outer
  `{% for %}`; the sheet name must be the ACI class (singular).
- `DeployConfig` gains `show_report`, `verbose` and `connect_timeout` (APIC
  connect timeout, separate from the read `timeout`).

### Fixed

- Explicit `filters` take precedence over `filters_source_sheet`.
- `apply_filter` matches tags ignoring surrounding whitespace.
- Error messages dropped the `[Component] -> [Type]` prefixes and use exception
  chaining.

### Breaking

- The previous single-render flow (one template with `{% for %}` over plural
  sheet variables) is replaced. `DataLoader.variables` no longer holds sheets;
  rows live in `DataLoader.sheets`.
- `Result.log` changed from a list of strings to a list of structured events
  (`level`, `where`, `message`, `type`, `cause`, `objects`).
- Run history changed from a JSON array (`.json`) to JSON Lines (`.jsonl`),
  appended one run per line; `RunLog.last()` reads only the final record.
- `report` was renamed to `show_report`; `print_result` / `print_results` were
  renamed to `print_report` / `print_reports`.

## [2.0.0a3] - 2026-10-09

### Added

- `next` now ships the `publish.yml` GitHub Actions workflow, so pre-releases
  publish to PyPI via trusted publishing on GitHub Release.

## [2.0.0a2] - 2026-10-08

### Changed

- Reorganized the package into layer subpackages: `inputs/`, `rendering/`,
  `output/` and `transport/` (`results.py`, `config.py`, `console.py`,
  `deploy.py` stay at the top level). Import paths changed accordingly.
- Unified the ACI handler registries into a single `BUILDERS` mapping in
  `cobra/builders.py`; the `Handler` type is now a protocol in `cobra/base.py`.
- XML/JSON payload extraction is shared between `CobraBuilder` and `CobraResult`.
- The library attaches a `NullHandler` and only emits logs when
  `configure_logging()` (now public) or another logging setup is used.
- Centralized logging and terminal output in `console.py`: `get_logger()`,
  `configure_logging()` (idempotent, level/format/stream aware) and a shared
  `get_console()`; the APIC countdown and rendered output go through it.
- `DeployClass` no longer prompts for APIC credentials at construction; it
  prompts only when committing.
- `DeployConfig.filters` is now a materialized `Sequence[str]`.
- Narrowed `Any` on the public configuration/JSON surfaces.

### Fixed

- `JinjaRenderer.render` no longer fails when a template variable is named `name`.
- `CobraBuilder.xml`/`json` no longer raise when the configuration is empty.
- `DeployClass.deploy` only commits when **every** template succeeded.
- `range_filter` raises a clear `ValueError` on malformed input.
- TLS warnings are no longer disabled at import time; they are silenced only
  when an insecure (`secure=False`) session is created.
- `get_logger()` no longer produces doubled logger names (`devaci.devaci.<x>`);
  module records are now emitted as `devaci.<module>`.
- `nan_filter` now also matches a float `NaN`, not just the text `nan`.

### Removed

- `cobra/registry.py` (`build_registry`), superseded by the unified `BUILDERS` map.
- Permissive `pyrightconfig.json`; `mypy` (strict) is the type-checking gate.

### Added

- pytest fixtures in `tests/conftest.py` and a test tree mirroring `src/`.
- CI workflow running ruff + mypy, with a coverage gate (`fail_under = 80`).
- CI now runs on Python 3.10/3.11/3.12 with `ruff format --check` and `uv build`.
- `README.md` rewritten (quick start, templates, data/filters, logging) and a
  `CONTRIBUTING.md` added.
- Error-path tests for template/data loading, output, run log, APIC countdown,
  handler failures and result payloads; shared value predicates in `_values.py`.

## [2.0.0a1] - 2026-10-05

### Added

- Start of the 2.x development line (breaking changes to templates and backend).

## [1.0.1] - 2026-10-07

### Fixed

- `JinjaRenderer.render` no longer fails when a template variable is named `name`.
- `CobraBuilder.xml`/`json` no longer raise when the configuration is empty.

## [1.0.0] - 2026-10-05

### Added

- Initial release: generate Cisco ACI configuration and optionally push it to an APIC controller via the Cisco Cobra SDK.
- Registry-based ACI object builders (`@register`).
- Jinja2 template rendering with a coercion-free YAML loader.
- XLSX/CSV input loading and tag-based filtering.
- Deployment orchestrator with dry-run mode and APIC commit.
