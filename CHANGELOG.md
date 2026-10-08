# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Reorganized the package into layer subpackages: `inputs/`, `rendering/`,
  `output/` and `transport/` (`results.py`, `config.py`, `console.py`,
  `deploy.py` stay at the top level). Import paths changed accordingly.
- Unified the ACI handler registries into a single `BUILDERS` mapping in
  `cobra/builders.py`; the `Handler` type is now a protocol in `cobra/base.py`.
- XML/JSON payload extraction is shared between `CobraBuilder` and `CobraResult`.
- The library attaches a `NullHandler` and only emits logs when
  `configure_logging()` (now public) or another logging setup is used.

### Fixed

- `JinjaRenderer.render` no longer fails when a template variable is named `name`.
- `CobraBuilder.xml`/`json` no longer raise when the configuration is empty.
- `DeployClass.deploy` only commits when **every** template succeeded.
- `range_filter` raises a clear `ValueError` on malformed input.
- TLS warnings are no longer disabled at import time; they are silenced only
  when an insecure (`secure=False`) session is created.

### Removed

- `cobra/registry.py` (`build_registry`), superseded by the unified `BUILDERS` map.
- Permissive `pyrightconfig.json`; `mypy` (strict) is the type-checking gate.

### Added

- pytest fixtures in `tests/conftest.py` and a test tree mirroring `src/`.
- CI workflow running ruff + mypy, with a coverage gate (`fail_under = 80`).

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
