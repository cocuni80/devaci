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

Releases are published from `main` and `next` via **GitHub Releases** using
trusted publishing (`.github/workflows/publish.yml`) — no PyPI token needed.

In short:

1. Bump the version in `pyproject.toml` (run `uv lock`) and add a
   `CHANGELOG.md` entry.
2. Push to `next`, then create a **pre-release** GitHub Release with a new
   tag (`vX.Y.Z`) targeting `next`.
3. Publishing a release triggers the workflow, which builds and uploads to PyPI.

Never reuse a version number (PyPI is immutable). The full checklist is in
`DO_NOT_PUBLISH.md` (private).
