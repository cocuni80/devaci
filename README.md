# devaci

Python library that generates Cisco ACI configuration and optionally pushes it to an APIC controller via Cisco's official Cobra SDK.

## Structure

```
devaci/
├── LICENSE
├── README.md
├── pyproject.toml
├── uv.lock
├── src/
│   └── devaci/
│       ├── __init__.py        # public API
│       ├── config.py          # typed DeployConfig
│       ├── console.py         # logging only
│       ├── deploy.py          # DeployClass orchestrator
│       ├── exceptions.py
│       ├── results.py         # result dataclasses
│       ├── inputs/
│       │   ├── templates.py   # TemplateSource
│       │   └── datasets.py    # DataLoader + xlsx/csv loading and filtering
│       ├── rendering/
│       │   ├── jinja.py       # JinjaRenderer
│       │   ├── filters.py     # Jinja filters
│       │   └── yaml_loader.py # non-coercing YAML loader
│       ├── output/
│       │   ├── writer.py      # OutputWriter + rich terminal output
│       │   └── runlog.py      # RunLog history
│       ├── transport/
│       │   └── apic.py        # ApicSession (login/commit)
│       └── cobra/
│           ├── __init__.py    # CobraBuilder
│           ├── base.py        # shared helpers + Handler protocol
│           └── builders.py    # BUILDERS mapping (unified)
└── tests/
    ├── conftest.py
    ├── test_config.py
    ├── test_console.py
    ├── test_deploy.py
    ├── test_devaci.py
    ├── test_results.py
    ├── test_cobra/
    ├── test_inputs/
    ├── test_output/
    ├── test_rendering/
    └── test_transport/
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
