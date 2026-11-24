# Backend

FastAPI application for authentication, tenant isolation, receivables, policy rules, agent tools, and audit logging.

## Run locally

Use Python 3.11 or newer. From this directory, create and activate a virtual environment,
then install the runtime dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API listens on `http://localhost:8000`. Its `GET /health` endpoint returns
`{"status":"ok"}`. Set `TAHSEEL_APP_TITLE` in the environment to change the API title.

## Tests

Install the development dependencies and run the backend tests:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Lint

Run Ruff checks from the repository root:

```bash
ruff check backend
ruff format --check backend
```
