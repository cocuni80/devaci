# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
