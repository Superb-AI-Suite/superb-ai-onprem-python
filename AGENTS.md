# Repository Guidelines

## Project Structure & Module Organization
- `spb_onprem/`: SDK source. Each domain (`activities/`, `datasets/`, `data/`, `slices/`, `exports/`, `contents/`, `users/`) follows a consistent layout: `entities/` (Pydantic models), `params/` (request DTOs), `queries.py` (API shapes), and `service.py` (public methods).
- `tests/`: Mirrors domains (e.g., `tests/activities/`, `tests/exports/`) with unit and light integration tests.
- Packaging: `setup.py`, `pyproject.toml` (setuptools_scm), `Pipfile` for local dev.

## Build, Test, and Development Commands
- Create env (Pipenv, Python 3.11): `pipenv install` then `pipenv shell`.
- Install locally (editable): `pipenv install -e .` (already in Pipfile) or `pip install -e .`.
- Run tests: `pytest -q` or `pipenv run pytest -q`.
- Skip networked tests by default: `pytest -q -k 'not real_test and not integration'`.

## Coding Style & Naming Conventions
- Indentation: 4 spaces; follow PEP 8; keep functions small and pure.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Types & docs: prefer type hints; add concise docstrings describing inputs/outputs and error cases.
- Imports: absolute within `spb_onprem` (avoid fragile relative chains).

## Testing Guidelines
- Framework: `pytest` with `pytest-mock`. Place tests under `tests/<domain>/test_*.py`.
- Mocks: patch HTTP calls (e.g., `requests`) in unit tests. Reserve `real_test.py` and `test_integration.py` for environments with valid on‑prem credentials.
- Run a focused subset: `pytest tests/exports/test_service.py -q`.

## Commit & Pull Request Guidelines
- Commits: present tense, concise summary + scope (e.g., "Fix data list bug"). Group related changes; reference issues (e.g., `Fixes #123`).
- PRs: include a clear description, rationale, and before/after behavior. Link issues, attach sample code or logs for API changes, and include/updated tests.
- Checks: ensure `pytest` passes locally and new APIs include tests and minimal docs in `README.md` as needed.

## Security & Configuration Tips
- Never commit credentials. For local auth use `~/.spb/onprem-config` or env vars: `SUPERB_SYSTEM_SDK=true`, `SUPERB_SYSTEM_SDK_HOST` (or `SUNRISE_SERVER_URL`), `SUPERB_SYSTEM_SDK_USER_EMAIL`.
- Prefer configuration via file/env; avoid hardcoding hosts/keys in code or tests.

