# Backend Development

## Source of truth

- Backend dependencies: `apps/api/pyproject.toml`
- Locked dependency resolution: `apps/api/uv.lock`
- Test root: `apps/api/tests`

The preferred backend workflow is `uv` with the lockfile. If `uv` is not available on the local machine, use a local virtual environment and install from `pyproject.toml` as a fallback.

## Windows setup

From `C:\Users\SGAEM\Desktop\agy\commercial_area_analysis`:

```powershell
C:\Users\SGAEM\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m venv apps/api/.venv
apps\api\.venv\Scripts\python.exe -m pip install -e .\apps\api
apps\api\.venv\Scripts\python.exe -m pip install pytest httpx
```

Why the extra `pytest httpx` step:

- `apps/api/pyproject.toml` keeps test tools under `[dependency-groups].dev`
- `uv sync --group dev` installs that group
- plain `pip install -e` does not install `dependency-groups`

## Preferred uv setup

From `C:\Users\SGAEM\Desktop\agy\commercial_area_analysis\apps\api`:

```powershell
uv sync --group dev
```

## FastAPI import check

From `C:\Users\SGAEM\Desktop\agy\commercial_area_analysis\apps\api`:

```powershell
.venv\Scripts\python.exe -c "from app.main import app; print(app.title if hasattr(app, 'title') else 'ok')"
```

Expected output:

```text
Commercial Area Analysis API
```

## Test commands

Targeted provider/runtime checks:

```powershell
.venv\Scripts\python.exe -m pytest apps/api/tests/adapters/test_geo_provider.py apps/api/tests/api/test_geo_endpoints.py -q
.venv\Scripts\python.exe -m pytest apps/api/tests/api/test_analysis_endpoints.py apps/api/tests/ingest/test_stores_ingest.py -q
```

Full backend suite:

```powershell
.venv\Scripts\python.exe -m pytest apps/api/tests -q
```

## Local API run

From `C:\Users\SGAEM\Desktop\agy\commercial_area_analysis\apps\api`:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir . --reload --host 127.0.0.1 --port 8000
```

## Notes

- Do not write real API keys into `.env`.
- Keep `GEO_PROVIDER=mock` for default local and test runs unless a manual smoke test explicitly needs Kakao.
- Backend tests should stay on mocked geo-provider paths unless real-provider smoke is intentionally enabled later.
