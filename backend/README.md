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

## Authentication, roles, and users (T-011)

The authentication and user-management endpoints are:

| Method and path | Access | Purpose |
|---|---|---|
| `POST /api/v1/auth/login` | Public | Verify email/password and issue an HS256 bearer token |
| `GET /api/v1/auth/me` | Authenticated | Return the current database-backed user profile |
| `GET /api/v1/users` | Owner only | List users in the Owner's tenant |
| `GET /api/v1/users/{user_id}` | Owner only | Retrieve a user in the Owner's tenant |
| `POST /api/v1/users` | Owner only | Create a user in the Owner's tenant |
| `PATCH /api/v1/users/{user_id}` | Owner only | Update a user's name, email, role, or password |

Send protected requests with `Authorization: Bearer <access_token>`. Tokens are
signed with `APP_SECRET_KEY` (at least 32 bytes); `ACCESS_TOKEN_TTL_MINUTES` defaults
to `60`. Login accepts an optional `tenant_id` to disambiguate matching credentials
across tenants. The server assigns a new user's tenant from the authenticated Owner,
stores passwords as Argon2id hashes, and never returns password hashes. Email
uniqueness is case-insensitive within a tenant. User updates are Owner-only, and the
last Owner in a tenant cannot be demoted.

The `OWNER`, `FINANCE_MANAGER`, and `COLLECTOR` permissions are enforced server-side.
Owners and Finance Managers see all customers in their tenant; Collectors see only
customers where `assigned_collector` matches their user ID. The permission matrix is
defined in Decision Log D15/D30 and implemented in `backend/auth/`.

Request/response schemas, examples, and status codes are specified in
[PRD section 21](../docs/technical/Tahseel_AI_PRD.md#21-api). FastAPI exposes the
generated OpenAPI document at `http://localhost:8000/openapi.json` and Swagger UI at
`http://localhost:8000/docs`.

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

PostgreSQL integration tests use `TEST_DATABASE_URL`. It must point to a
disposable PostgreSQL database with pgvector enabled; the migration integration
test upgrades and downgrades its schema. CI provides an isolated database.

## Lint

Run Ruff checks from the repository root:

```bash
ruff check backend
ruff format --check backend
```
