# Contributing to devaci

Thanks for your interest in improving devaci.

## Development setup

```bash
uv sync                     # create .venv, install devaci + dev dependencies
source .venv/bin/activate
```

The Cisco ACI Cobra SDK is not on PyPI and is required even to `import devaci`.
Place the `acicobra` / `acimodel` wheels in `vendor/` and install them:

```bash
uv pip install vendor/*.whl
```

## Before opening a pull request

Run the checks in this order and make sure they are clean:

```bash
uv run ruff check .         # lint
uv run mypy src             # typecheck (strict)
uv run pytest --cov=devaci  # tests + coverage (fails under 80%)
```

Guidelines:

- Add or update tests for any behavior change; the test tree mirrors `src/`.
- Keep the layered structure: put new responsibilities in their own component
  (`inputs/`, `rendering/`, `output/`, `transport/`, `cobra/`) rather than
  growing `DeployClass`.
- Do not add inline comments unless they clarify a non-obvious decision.
- Do not reformat `src/devaci/cobra/builders.py`: it intentionally mirrors the
  Cobra SDK's PascalCase naming (ruff exceptions are scoped to that file).

## Branches and commits

- `main` = stable `1.x`; `next` = `2.x` pre-releases.
- Work on a `feat/...` or `fix/...` branch and open a pull request.
- Reference the issue in the PR description (`Closes #N`).
- Commits do **not** bump the version; only a PyPI release does.

## Releasing

Versioning and publishing are documented in `DO_NOT_PUBLISH.md` (private
checklist). In short: bump the version in `pyproject.toml`, move the
`CHANGELOG.md` entries out of `[Unreleased]`, tag, then `uv build && uv publish`.
