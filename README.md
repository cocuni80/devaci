# devaci

Python library that generates Cisco ACI configuration from Jinja2 templates +
Excel/CSV inputs, and optionally pushes it to an APIC controller via Cisco's
official Cobra SDK.

Pipeline: **data + template → `JinjaRenderer` (Jinja2 → YAML dict) →
`CobraBuilder` (dict → `ConfigRequest`) → output / APIC commit**, orchestrated
by `DeployClass`.

## Requirements

- Python 3.10+
- The Cisco ACI **Cobra SDK** (`acicobra`, `acimodel`) — see below; it is
  **not on PyPI**.

## Installation

```bash
uv sync                 # create .venv, install devaci + dev dependencies
source .venv/bin/activate
```

### External dependency: Cobra SDK

The Cisco ACI Cobra SDK is distributed as `.whl`/`.egg` by Cisco and is **not
on PyPI**. Download the wheels and place them in `vendor/` (not tracked by
git), then:

```bash
uv pip install vendor/*.whl
```

The importable package is `cobra`. This repository vendors `acicobra` +
`acimodel`; other Cisco modules are optional. `import devaci` (and therefore
the whole test suite) fails until the SDK is installed.

## Quick start

```python
from pathlib import Path

from devaci import DeployClass

aci = DeployClass(
    testing=True,                 # True = dry run, no APIC credentials prompted
    working_folder=Path.cwd(),    # base folder for templates/data/outputs
    file_output="outputs/scripts/config",   # optional: save XML/JSON
    show_output=False,            # print the rendered config to the terminal
    logging=True,                 # append results to logging_output (JSON)
)

aci.xlsx = "data/aci.xlsx"        # load every sheet into template variables
aci.template = "templates/tenant.j2"
aci.deploy()

print(aci.config)                 # rendered XML (or JSON dict)
print(aci.results)                # per-template result dicts
```

`DeployClass` accepts either a typed `DeployConfig` or the keyword arguments
shown above:

```python
from devaci import DeployConfig, DeployClass

config = DeployConfig(testing=True, render_to_xml=False)
aci = DeployClass(config=config)
```

With `testing=False` and no `ip`/`username`/`password`, the APIC credentials are
prompted interactively (`getpass`). `deploy()` commits to the APIC **only when
every template in the run succeeded**.

## Templates

A template is a Jinja2 file that renders to YAML. Each **top-level key maps to
an ACI object class** handled by `CobraBuilder` (`fvTenant`, `fvAp`, `mcpInstPol`,
`fabricNodeControl`, ...). Values may be a list of objects or a nested mapping:

```jinja
fvTenant:
  - name: {{ tenant_name }}
    descr: {{ tenant_descr }}
    status: {{ status }}

fvAp:
  - name: web
    fvRsCtx:
      tnFvCtxName: {{ vrf }}
```

Rendering uses a **coercion-free YAML loader**: YAML ints/floats/bools are kept
as strings so APIC values are never mangled, and the string `nan` becomes `""`.

### Template filters

| Filter        | Example                     | Result              |
|---------------|-----------------------------|---------------------|
| `bool`        | `{{ "yes" \| bool }}`       | `True`              |
| `range`       | `{{ "1-3,5" \| range }}`    | `[1, 2, 3, 5]`      |
| `nan`         | `{{ value \| nan }}`        | `False` when `nan`  |
| `split`       | `{{ "a,b" \| split }}`      | `["a", "b"]`        |

## Data inputs (XLSX / CSV)

Both `aci.xlsx` and `aci.csv` accept a filename or a list of filenames:

- An **XLSX** workbook loads one variable per **sheet**, named after the sheet.
- A **CSV** file loads one variable named after the file **stem**.

Each variable is a list of row dicts, so a sheet named `tenants` is used as
`{% for row in tenants %}`.

### Filtering

- `filters`: list of values to keep, matched against the `filter_by` column
  (default `tag`). Rows with empty/`NaN` tags are always dropped.
- `filters_source_sheet`: derive the filter values from a dedicated sheet. Rows
  where `filters_condition_field` (default `enabled`) is truthy contribute their
  `filters_output_field` (default `name`) as a filter value.

```python
aci = DeployClass(
    testing=True,
    filters=["IBK-6", "IBK-7"],
    filter_by="tag",
    filters_source_sheet="OCs",       # optional
    filters_condition_field="enabled",
    filters_output_field="name",
)
```

## Output

- `render_to_xml=True` (default): config is XML (`.xml`); otherwise JSON (`.json`).
- `file_output="outputs/scripts/config"`: write the rendered config to disk.
- `show_output=True`: pretty-print the rendered config to the terminal.
- `save_output(name)` / `print_output()` can be called directly.

## Logging

devaci uses the standard library `logging` module. It attaches a
`NullHandler` on import (no output by default); opt in with the public
`configure_logging()`:

```python
import logging
from devaci import configure_logging

configure_logging(level=logging.INFO)   # idempotent; adds one stream handler
```

Module loggers are exposed as `devaci.<module>` (e.g. `devaci.deploy`) and
propagate to the stdlib root logger, so per-module levels can be tuned with
normal logging configuration. Terminal output of rendered configuration and the
APIC countdown go through the shared rich console in `devaci.console`.

> `RunLog` (`logging_output`, default `outputs/logs/logging.json`) is a JSON
> **execution history**, not stdlib logging. Disable with `logging=False`.

## Project structure

```
src/devaci/
├── __init__.py        # public API
├── config.py          # typed DeployConfig
├── console.py         # centralized logging + shared rich console
├── deploy.py          # DeployClass orchestrator
├── exceptions.py
├── results.py         # result dataclasses
├── _values.py         # shared value predicates (nan/empty checks)
├── inputs/            # TemplateSource + DataLoader (xlsx/csv, filters)
├── rendering/         # JinjaRenderer, filters, non-coercing YAML loader
├── output/            # OutputWriter + RunLog
├── transport/         # ApicSession (login/commit)
└── cobra/             # CobraBuilder + BUILDERS mapping
```

## Development

```bash
uv run pytest                 # full test suite
uv run pytest --cov=devaci    # with coverage (fails under 80%)
uv run ruff check .           # lint
uv run mypy src               # typecheck (strict)
```

Run order when verifying a change: `ruff check .` → `mypy src` → `pytest`.

## Publishing

```bash
uv build
uv publish
```

Only a PyPI release bumps the version; commits do not. See `CONTRIBUTING.md`.
