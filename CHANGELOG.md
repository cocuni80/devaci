# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [1.0.0] - 2026-10-05

### Added

- Initial release: generate Cisco ACI configuration and optionally push it to an APIC controller via the Cisco Cobra SDK.
- Registry-based ACI object builders (`@register`).
- Jinja2 template rendering with a coercion-free YAML loader.
- XLSX/CSV input loading and tag-based filtering.
- Deployment orchestrator with dry-run mode and APIC commit.
