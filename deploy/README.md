# Deployment

Docker Compose and production deployment configuration. The public deployment uses
the same services as the local stack, with Caddy as the HTTPS reverse proxy.

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

Compose starts the backend after the database is healthy, the frontend after the
backend is healthy, and Caddy after both app services are healthy. The database health
check uses `pg_isready`; the backend, frontend, and proxy check their health endpoints.
The backend and database share the `database` network. Caddy bridges separate
`backend_proxy` and `frontend_proxy` networks to reach each app; the frontend and
backend do not share a network with each other. On first database initialization, the
SQL file in `database/init/` enables `vector`. PostgreSQL only runs initialization
files when its data directory is empty.

### Volume safety

`docker compose down` preserves named volumes. Do not use `docker compose down -v`,
`docker volume rm`, or `docker volume prune` on a deployment unless you intentionally
want to delete stored data and have verified an independent backup. Removing
`postgres_data` permanently deletes the PostgreSQL database; removing `caddy_data`
deletes Caddy's persisted certificate/account state. `docker volume prune` can also
remove unrelated unused volumes on the host.

## Public deployment

The project has not selected a hosting provider. Use a Linux VPS that can run Docker
Compose, with a DNS name pointed at its public IP address. Allow inbound TCP ports 80
and 443; UDP port 443 is optional and enables HTTP/3. Do not publish database or
application ports to the public network.

1. Copy `.env.example` to `.env` on the server and set a strong, unique
   `POSTGRES_PASSWORD`. Set `DOMAIN` to the DNS name for the deployment (not
   `localhost`).
2. Point the domain's DNS A/AAAA records to the server. Ensure the firewall and any
   provider firewall allow ports 80 and 443.
3. From the repository root, start the stack:

   ```bash
   docker compose up --build -d
   docker compose ps
   ```

Caddy routes `/` to the frontend, `/api/*` to the backend after removing the `/api`
prefix, and `/health` directly to the backend. Requests on HTTP are redirected to
HTTPS. For a public DNS name, Caddy obtains and renews a publicly trusted certificate
automatically. Certificate/account state is persisted in the `caddy_data` volume;
keep that volume when updating the stack. For local use, the default `DOMAIN=localhost`
uses Caddy's local CA and may require trusting that CA in the client.

Check `https://<DOMAIN>/`, `https://<DOMAIN>/api/health`, and
`https://<DOMAIN>/health`. The backend and frontend ports remain bound to loopback for
local diagnostics; only Caddy's ports 80 and 443 should be reachable externally.

Keep passwords and other secrets in environment variables or local, untracked files.
Do not add live credentials, certificate files, or backups to source control. The
database backup and restore commands are documented in the root `README.md`.
