# devaci

Python library that generates Cisco ACI configuration and optionally pushes it to an APIC controller via Cisco's official Cobra SDK.

## Structure

```
devaci/
├── LICENSE
├── README.md
├── pyproject.toml
├── pyrightconfig.json
├── uv.lock
├── src/
│   └── devaci/
│       ├── __init__.py        # public API
│       ├── console.py         # logging + rich console
│       ├── data.py            # xlsx/csv loading and filtering
│       ├── deploy.py          # DeployClass orchestrator
│       ├── exceptions.py
│       ├── filters.py         # Jinja filters + YAML loader
│       ├── jinja.py           # JinjaRenderer
│       ├── results.py         # result dataclasses
│       └── cobra/
│           ├── __init__.py    # CobraBuilder
│           ├── base.py
│           ├── builders.py    # registered ACI object handlers
│           └── registry.py
└── tests/
    ├── test_cobra.py
    ├── test_deploy.py
    ├── test_devaci.py
    └── test_outputs.py
```

## Installation (development)

```bash
pip install uv          # if you don't have it yet
uv sync                 # creates .venv and installs devaci + dev dependencies
source .venv/bin/activate
```

To add/remove dependencies:

```bash
uv add requests         # runtime dependency
uv add --dev httpx      # development dependency
uv remove requests
```

## External dependency: Cobra SDK

The Cisco ACI Cobra SDK (`acicobra`, `acimodel`, `aciparser`, `acirpc`) is **not on PyPI**.
Download the `.whl` files from Cisco and place them in the `vendor/` folder (not tracked by git), then:

```bash
uv pip install vendor/*.whl
```

Tests that depend on the Cobra SDK fail if it is not installed.

## Tests

```bash
uv run pytest
```

## Lint and type checking

```bash
uv run ruff check .
uv run mypy src
```

## Publishing

```bash
uv build
uv publish
```
