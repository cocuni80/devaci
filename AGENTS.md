# AGENTS.md

`devaci` generates Cisco ACI configuration from Excel/CSV inputs + Jinja2 templates and can push it to an APIC via Cisco's Cobra SDK. Python library, `src/` layout, managed with `uv`.

## Commands

```bash
uv sync                       # create .venv, install runtime + dev deps
uv run pytest                 # full suite (currently 58 tests)
uv run pytest tests/test_data.py::test_apply_filter_no_filters   # single test
uv run pytest --cov=devaci    # with coverage
uv run ruff check .           # lint
uv run mypy src               # typecheck (strict)
```

Run order when verifying a change: `ruff check .` -> `mypy src` -> `pytest`.

## Critical: Cobra SDK is not on PyPI

The Cisco SDK (`acicobra`, `acimodel`) is required even just to `import devaci`, so the whole test suite fails at collection if it is missing. The `.whl` files are NOT tracked and live in `vendor/` (gitignored). If `import devaci` fails, install them:

```bash
uv pip install vendor/*.whl
```

The importable package is `cobra` (not `acicobra`). `vendor/` only holds `acicobra` + `acimodel` here; other modules are optional.

## Architecture

Pipeline: input data + template -> `JinjaRenderer.render` (template -> YAML dict) -> `CobraBuilder.render` (dict -> `ConfigRequest`) -> output / APIC commit. Orchestrated by `DeployClass` in `src/devaci/deploy.py`.

- `DeployClass` is configured via a typed `DeployConfig` (`src/devaci/config.py`) or, for backwards compatibility, `**kwargs` at construction; then driven through property setters: set `.template`, optionally `.xlsx`/`.csv`/`.variables`, then call `.deploy()`.
- `DeployClass` is a thin facade over focused components: `ApicSession` (`apic.py`, login/commit/countdown), `TemplateSource` + `DataLoader` (`inputs.py`), `OutputWriter` (`output.py`) and `RunLog` (`runlog.py`). Keep new responsibilities in their own component rather than growing the facade.
- `CobraBuilder.render` dispatches each non-empty top-level YAML key to the `BUILDERS` mapping (`src/devaci/cobra/builders.py`), composed per ACI domain (Tenant/Fabric/Infra/Policies) with `build_registry` (`registry.py`), which rejects duplicate keys. Unknown keys mark the whole render as failed. To add an ACI object type, add a handler and register it in the matching domain mapping.
- `builders.py` is large and intentionally mirrors the Cobra SDK's PascalCase class/local naming. Keep that style; ruff ignores `N806`/`SIM102` only for this file.
- There is no `src/devaci/_legacy` package; it was removed in 2.x. Don't recreate it, and don't re-add `_legacy` excludes to the tooling config.

## Gotchas

- `load_yaml` (`src/devaci/filters.py`) uses a custom loader that deliberately does NOT coerce YAML ints/floats/bools - everything stays a string so APIC values are not mangled. Do not swap in `yaml.safe_load`.
- `DeployClass` prompts interactively for APIC credentials (via `getpass`) unless `testing=True`. Use `testing=True` to dry-run.
- The manual end-to-end runner is `tests/testing/run_deploy.py` (sets `TESTING = True` to avoid the credential prompt). It is a gitignored script, NOT a pytest test.
- `pyproject.toml` uses `strict = true` for mypy and ruff `select = [E, F, I, N, UP, B, SIM]`, `line-length = 100`.

## Never commit / never publish

Gitignored and private: `vendor/`, `data/` (real `.xlsx`/`.j2`), `outputs/`, `tests/testing/`, `dist/`, `DO_NOT_PUBLISH.md`, `.env`. `.env` holds a live `UV_PUBLISH_TOKEN`; do not print, commit, or expose it.

`DO_NOT_PUBLISH.md` documents the release/branching procedure (currently stale on some details, e.g. test counts) and is the reference for versioning.

## Versioning & branches

- Version lives ONLY in `pyproject.toml`; `devaci/__init__.py` reads it via `importlib.metadata`. Do not hardcode or bump it except when publishing.
- `main` = stable `1.x`; `next` = `2.x` pre-releases (`2.0.0a1` currently). Development happens on feature branches merged via PR. Committing != publishing; only a PyPI release bumps the version. `.github/workflows/publish.yml` (on `main`) publishes on GitHub release via trusted publishing.
