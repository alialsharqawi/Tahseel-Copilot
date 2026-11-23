# Deployment

Docker Compose and production deployment configuration.

## Local stack

The root `compose.yaml` starts PostgreSQL with pgvector, the FastAPI backend, and the
Next.js frontend. Before starting the stack, set `POSTGRES_PASSWORD` in your shell or
in a local, untracked `.env` file.
`POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PORT` can also be set; defaults are
`tahseel`, `tahseel`, and `5432`.

```bash
docker compose up --build -d
docker compose ps
```

Compose starts the backend after the database is healthy and the frontend after the
backend is healthy. The database health check uses `pg_isready`; the backend and
frontend check their HTTP health endpoints. On first database initialization, the SQL
file in `database/init/` enables `vector`. PostgreSQL only runs initialization files
when its data directory is empty.

Keep passwords and other secrets in environment variables or local, untracked files.
Do not add live credentials to source control.
