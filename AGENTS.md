# AGENTS.md

`devaci` generates Cisco ACI configuration from Excel/CSV inputs + a declarative schema and can push it to an APIC via Cisco's Cobra SDK. Python library, `src/` layout, managed with `uv`.

## Commands

```bash
uv sync                       # create .venv, install runtime + dev deps
uv run pytest                 # full suite
uv run pytest tests/test_inputs/test_datasets.py::test_apply_filter_no_filters  # single test
uv run pytest --cov=devaci    # with coverage (fails under 80%)
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

Pipeline: input data + declarative schema -> `SchemaEngine` (builds Cobra managed objects per sheet row) -> output / APIC commit. Orchestrated by `DeployClass` in `src/devaci/deploy.py`.

The schema is a **single file** (`schema.j2`, set via `DeployClass.schema`, resolved against `working_folder`) written in a YAML DSL whose values are Jinja expressions evaluated **per row**. `SchemaLoader` (`src/devaci/schema/loader.py`) parses it with the no-coercion `load_yaml` (the `{{ }}` stay literal) and resolves `class: pkg.Clase` to `cobra.model.<pkg>.<Clase>`. `SchemaEngine` (`src/devaci/schema/engine.py`) iterates every schema entry whose key matches a loaded sheet: per row it expands `list`, evaluates `when`, resolves the `parent` chain (`parent: otherEntry` or `{ref, as_parent}`; `pol.Uni` maps to the builder root), applies the `requires`/`as_parent` gate, builds the node, adds it and recurses `children` (mapping = single child, sequence = list). `DataLoader` keeps sheet rows in `sheets` and scalar globals in `variables` (`inputs/datasets.py`).

- The DSL fields are `class`, `parent`, `requires` (gate + naming/required props), `as_parent` (binding used when the entry acts as a parent; defaults to `requires`), `props`, `emit_parents` (also add the constructed ancestors to the request), `children`, `when` and `list` (`{from, split, range, bind}`).
- **Gate**: if any `requires`/`as_parent` value is empty (`_values.is_empty`) the node and its subtree are skipped. Non-required empties are kept and normalised (`None`/`nan` -> `""`) so APIC-valid empty props survive.
- **Props**: each built (sheet) node auto-passes row columns whose name is a valid `cls.meta.props` prop, then applies explicit `props` and `requires`. Children and parents use only their declared bindings. Avoid naming a row column like a prop of the parent class when the value belongs to a child; the SDK ignores unknown props but not name collisions.
- **Adding**: the engine adds each node and its children to the cumulative `ConfigRequest`, which merges by DN. With `emit_parents: true` it also adds the constructed ancestors (used by `fvRsPathAtt` to reproduce the legacy `fv_rs_path_att` merge/overwrite order); ancestors are otherwise built with `as_parent` only and left implicit.
- The engine has **no ACI-specific filters**: all derivations (topology `tDn`, value `map`, ranges) are written inline in `schema.j2` with plain Jinja (`{% if %}`, dict indexing, `range()`, `~`).
- `src/devaci/schema/spec.py` holds the parsed model (`Schema`, `NodeSpec`, `ParentRef`, `ListSpec`); `src/devaci/schema/source.py` resolves the single file.

The package is organized by layer: `inputs/` (tabular data), `rendering/` (Jinja + filters + YAML loader), `schema/` (DSL model + engine), `output/` (writer + run history), `transport/` (APIC session) and `cobra/` (config builder). Shared result models live in `results.py`, centralized logging + the shared rich console in `console.py`, and small shared value predicates in `_values.py` (import via `get_logger`/`get_console`, never create handlers/consoles elsewhere).

- `DeployClass` is configured via a typed `DeployConfig` (`src/devaci/config.py`) or, for backwards compatibility, `**kwargs` at construction; then driven through property setters: set `.schema`, optionally `.xlsx`/`.csv`/`.variables`, then call `.deploy()`.
- `DeployClass` is a thin facade over focused components: `ApicSession` (`transport/apic.py`, login/commit/countdown), `SchemaSource` + `DataLoader` (`inputs/`), `OutputWriter` (`output/writer.py`) and `RunLog` (`output/runlog.py`). Keep new responsibilities in their own component rather than growing the facade.
- `deploy()` is **schema-only**: without a schema it is a no-op; with one it runs the whole schema in a single pass. A `CobraBuilder` is cumulative across runs and devaci never clears the accumulated tree.
- Each `deploy()` builds one **run record** (version, mode, filters, per-run objects/duration and structured `log` events) used for both the printed report (`DeployClass.print_report` / `print_reports`, `show_report`/`verbose` flags) and the history. History is **JSON Lines** (`RunLog`, `.jsonl`), appended one run per line; `RunLog.last()` reads only the final record. Errors are structured events (`level`/`where`/`message`/`type`/`cause`); the printed report is on by default (`show_report=True`; set it to `False` to stay quiet) and is independent of the `logging` history flag, while stdlib logging stays quiet until `configure_logging()`.
- `CobraBuilder.render` / `BUILDERS` (`src/devaci/cobra/builders.py`) remain as a public Python-builder API, but `deploy()` no longer drives them: the schema engine adds managed objects directly via `CobraBuilder.add`. `builders.py` is large and intentionally mirrors the Cobra SDK's PascalCase class/local naming; ruff ignores `N806`/`SIM102` only for this file.
- There is no `src/devaci/_legacy` package; it was removed in 2.x. Don't recreate it, and don't re-add `_legacy` excludes to the tooling config.

## Gotchas

- `load_yaml` (`src/devaci/rendering/yaml_loader.py`) uses a custom loader that deliberately does NOT coerce YAML ints/floats/bools - everything stays a string so APIC values are not mangled. Do not swap in `yaml.safe_load`.
- `schema.j2` is **data**, not a template: `SchemaLoader` parses it as-is and the engine evaluates each value expression per row. Don't pre-render the file with Jinja (per-row variables do not exist at file scope).
- The engine auto-passes row columns that are valid props of the node's class and adds constructed parents to the `ConfigRequest`; this reproduces the legacy per-sheet merge/overwrite order, so keep schema entries in the same order as the class hierarchy.
- `DeployClass` does not prompt at construction; it prompts interactively for missing APIC credentials (via `getpass`) only when committing, unless `testing=True`. Use `testing=True` to dry-run.
- The manual end-to-end runner is `tests/testing/run_deploy.py` (sets `TESTING = True` to avoid the credential prompt). It is a gitignored script, NOT a pytest test. It derives the repo root from its own path (works from any cwd) and can run via `uv run` (local `src/`) or with `tests/testing/release-$VERSION/.venv/bin/python` (PyPI artifact); see `DO_NOT_PUBLISH.md`.
- `pyproject.toml` uses `strict = true` for mypy and ruff `select = [E, F, I, N, UP, B, SIM]`, `line-length = 100`.

## Never commit / never publish

Gitignored and private: `vendor/` (Cobra SDK wheels), `tests/testing/` (real `.xlsx`/`.j2` inputs, generated `outputs/`, scratch), `dist/`, `DO_NOT_PUBLISH.md`, `.env`. `.env` holds a live `UV_PUBLISH_TOKEN`; do not print, commit, or expose it.

**Never delete untracked/gitignored files.** They are not in git and cannot be recovered from history; only move/copy them, and only with explicit user confirmation. This covers everything under `tests/testing/` (real `.xlsx`/`.j2`, `run_deploy.py`, `run_template.py`, `parity_schema.py`, `outputs/`, `tmp/`).

`DO_NOT_PUBLISH.md` documents the release/branching procedure and is the reference for versioning.

## Versioning & branches

- Version lives ONLY in `pyproject.toml`; `devaci/__init__.py` reads it via `importlib.metadata`. Do not hardcode or bump it except when publishing.
- `main` = stable `2.x`; `next` = `3.x` pre-releases (`3.0.0a1` currently). Development happens on feature branches merged via PR. Committing != publishing; only a PyPI release bumps the version. `.github/workflows/publish.yml` (on `main` and `next`) publishes on GitHub release via trusted publishing.
