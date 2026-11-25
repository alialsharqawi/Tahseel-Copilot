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

## Database migrations

The SQLAlchemy models and Alembic migration target PostgreSQL with pgvector. From
the repository root, start the database and backend after setting
`POSTGRES_PASSWORD`:

```bash
docker compose up -d db backend
docker compose exec backend alembic upgrade head
```

For a local Python environment, set `DATABASE_URL` to a
`postgresql+psycopg://...` connection URL, then run these commands from `backend/`:

```bash
alembic upgrade head
alembic downgrade base
```

The initial migration enables the pgvector extension and creates all 19 tables.
Embeddings use PostgreSQL's unbounded `VECTOR` type until the embedding model and
dimension are selected. No approximate-nearest-neighbor index is created.
Downgrading to `base` drops these tables, so only use it on a disposable database
or when intentionally removing the schema.

## Tests

Install the development dependencies and run the backend tests:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Synthetic receivables data

Generate the canonical fixture from the repository root:

```bash
python backend/scripts/generate_synthetic_data.py
```

The default seed is `2026`, and the default reference date is `2026-12-15`.
Use `--help` to view configurable seed, tenant, reference-date, and output
options. The fixture does not write to the database and is not a seed script.

## Lint

Run Ruff checks from the repository root:

```bash
ruff check backend
ruff format --check backend
```
