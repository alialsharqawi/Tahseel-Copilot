# Tahseel AI

> **Every morning, Tahseel tells a distributor's collection team which customers to chase, why, and exactly what to say.**

DEPI graduation project (LMS assignment: "DEPI GradProject"). Team of five.

---

## In plain language

Egyptian distributors sell to other businesses on credit. Their finance teams track unpaid invoices in Excel, ERP exports, and WhatsApp, with little support in deciding who to call each day.

Tahseel reads the receivables data, scores each customer's risk and explains the score, finds the relevant rule and clause in the company's own credit policy, remembers past notes and promises, recommends the next action, and drafts an Arabic message. A human approves everything. Nothing is sent automatically.

---

## Status

Documentation baseline, system architecture, database design, bilingual wireframes, team framework, and repository legal/security standards are completed (November 2026). The skills matrix is filled and skill-weighted assignments are generated. **The repository foundation is implemented:** PR #69 added the repository skeleton, PR #72 delivered Docker Compose, PR #73 delivered the bilingual synthetic policy corpus, PR #74 delivered CI, PR #76 delivered database models/migrations, PR #87/88 delivered authentication and API documentation, and PR #81 delivered the synthetic data generator. **P2 implementation is also underway:** PR #92 delivered T-013 (the receivables engine), and PR #93 delivered T-016 (tenant settings and policy-rule services). As of 28 November 2026, GitHub has **39 merged pull requests** and **54 task issues: 32 open and 22 closed**. The final vertical-slice features are not complete yet. The final defense is **Tuesday, 15 December 2026** (Decision Log, D40). Current status, recent merges, next steps, and open items are tracked in `PROJECT_STATUS.md`.

---

## Where each file lives

```text
Tahseel-Copilot/
├── README.md, LICENSE, CONTRIBUTING.md, CLAUDE.md, LMS_Requirements.md, TEAM.md, PROJECT_STATUS.md, GLOSSARY.md
├── Tahseel_Project_Documentation_v1.pdf       LMS documentation PDF
├── docs/
│   ├── foundation/
│   │   └── Tahseel_AI_Final_Concept.md          scope, tiers, demo flow, architecture, roadmap
│   ├── governance/
│   │   ├── Tahseel_AI_Decision_Log.md           every decision: chosen, not chosen, why
│   │   └── Tahseel_AI_Consistency_Ledger.md     findings from the consolidation review and their status
│   ├── technical/
│   │   ├── Tahseel_AI_PRD.md                    detailed specification: formulas, schema, API, acceptance criteria
│   │   └── Tahseel_AI_Technical_Strength.md     trust design, memory, evaluation plan, security
│   ├── architecture/
│   │   └── Tahseel_AI_Adaptability_Strategy.md  serving many sectors: canonical schema, adapters, configuration
│   ├── business/
│   │   └── Tahseel_AI_Business_Strength.md      evidence, stakeholders, competitors, ROI, validation plan
│   ├── presentation/
│   │   └── Tahseel_AI_Final_Pitch.md            pitch, slide skeleton, demo script, Q&A
│   ├── team/                                    backlog, skills matrix, assignment plan, onboarding, team brief, AI guide
│   ├── lms/parts/                               the six parts of the documentation submitted to the LMS (01 to 06)
│   ├── diagrams/                                ERD, architecture, wireframes (dot, mmd, png, svg)
│   └── archive/                                 superseded raw material, kept for history; not requirements
├── backend/                                     FastAPI service, health endpoint, tests, and Docker configuration
├── frontend/                                    Next.js bilingual interface and tests
├── data/                                        Synthetic policy documents and future seed datasets
├── database/init/                               PostgreSQL initialization scripts
├── evals/                                       RAG and evaluation assets
├── deploy/                                      Docker Compose deployment documentation
├── compose.yaml                                 local backend, frontend, and PostgreSQL/pgvector stack
├── .github/                                     task form, pull request template, label script, SECURITY.md
├── tools/                                       team_tools.py: skills-based assignment and issue creation
└── _private/                                    git-ignored: screenshots and personal references
```

`CLAUDE.md` is for AI assistants working in this repository.

---

## Start here: reading order (about 25 minutes)

| Order | File | Why read it |
|---:|---|---|
| 1 | `README.md` (this file) | The big picture and the 12 key facts below |
| 2 | `PROJECT_STATUS.md` | Current merged work, open tasks, blockers, phase gates, and next steps |
| 3 | `LMS_Requirements.md` | What we must submit and how we are graded |
| 4 | `docs/foundation/Tahseel_AI_Final_Concept.md` | Exact scope: what we build, in which tier, what we do not, the demo flow |
| 5 | `docs/governance/Tahseel_AI_Decision_Log.md` | Every major choice: what we chose, what we rejected, and why |
| 6 | `docs/technical/Tahseel_AI_Technical_Strength.md` | How the design earns trust; memory design; evaluation plan, and security |
| 7 | `docs/business/Tahseel_AI_Business_Strength.md` | Evidence for the problem, stakeholders, competitors, value model, and validation plan |
| 8 | `docs/technical/Tahseel_AI_PRD.md` | Detailed formulas, data model, API, acceptance criteria, and implementation requirements |
| 9 | `docs/architecture/Tahseel_AI_Adaptability_Strategy.md` | How one platform serves sectors through configuration and adapters |
| 10 | `docs/presentation/Tahseel_AI_Final_Pitch.md` | Pitch, slide skeleton, demo script, measured-result placeholders, and likely questions |
| Anytime | `GLOSSARY.md`, `TEAM.md` | Shared terms and team roles |
| New to the team | `docs/team/ONBOARDING.md`, then `CONTRIBUTING.md` | How to get started and how we work |

When two documents disagree, the higher one in the hierarchy wins: Decision Log, then Final Concept, then PRD, then the strength documents, then the pitch (Decision Log, D35).

---

## The 12 things everyone on the team must know

1. **Problem:** collection decisions are made from spreadsheets and memory. We turn receivables data into a ranked daily action list.
2. **Users:** the Collector uses it daily, the Finance Manager approves and oversees, the Owner sees the summary.
3. **Numbers come from tested code, never from the LLM.** The LLM explains, drafts messages, and answers questions by calling tools.
4. **The Collection Queue is a pipeline. The agent is for investigation** and open questions.
5. **Risk is a transparent weighted-rules score, not machine learning.** Every score lists its reasons.
6. **Policy is two layers:** structured rules evaluated by code, and cited document passages for explanation. If no relevant policy exists, the system says so.
7. **Customer memory stores only human-authored or rule-derived events** (notes, promises, decisions). Conversation memory is short-term context and never a source of facts.
8. **A human approves before anything consequential happens,** enforced at the API level.
9. **We use synthetic data and never claim real customers, pilots, or interviews.** Every business claim carries an evidence label.
10. **Stack:** Next.js, FastAPI, PostgreSQL with pgvector, OpenRouter for LLM access, Docker.
11. **The UI is fully Arabic (RTL) and fully English,** with a language toggle.
12. **We aim for production quality** (HTTPS, CI, logging, tests), but only after the core demo flow works.

One framing to keep in mind: **Tahseel does not prevent lateness. It is designed to shorten it and reduce forgetting** (a hypothesis we will test).

---

## Not doing (non-goals for the capstone)

Payments or wallets, automatic credit blocking, automatic WhatsApp or email sending, legal advice, a trained ML risk model, ERP or CRM integrations (only the CSV/Excel adapter is built), credit-limit recommendations. Cheque tracking and other later ideas are on the roadmap in `Final_Concept`, section 12.

---

## Working principles

- **Honesty first.** If we did not do or measure it, we do not claim it. Label assumptions as assumptions.
- **Decisions go in the Decision Log.** If you change a decision, add or edit its entry.
- **Update `PROJECT_STATUS.md`** when something is finished, blocked, or newly decided.
- **Everyone commits under their own GitHub account.** Team collaboration is graded on the repository history.
- **If a document contradicts the Decision Log, flag it** and resolve it in the log rather than leaving both.
- **Each topic has one owner file;** other files link to it instead of repeating it (D35).
- **Work through issues and pull requests,** with a reviewer, as described in `CONTRIBUTING.md` (D37).

---

## Quick start

### Prerequisites

- Git
- Docker Engine or Docker Desktop with Docker Compose v2

You do not need a separate Python or Node.js installation for the Docker Compose stack.

### 1. Clone the repository

```bash
git clone https://github.com/alialsharqawi/Tahseel-Copilot.git
cd Tahseel-Copilot
```

### 2. Create local environment settings

Copy `.env.example` to the Git-ignored `.env` file:

**PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS/Linux**

```bash
cp .env.example .env
```

Open `.env` and set a local value for `POSTGRES_PASSWORD`. This setting is required by
Docker Compose. Do not use a real secret or commit `.env`; it is ignored by Git.

Required for the Compose stack:

| Setting | Required value |
|---|---|
| `POSTGRES_PASSWORD` | A non-empty local password |

The other database settings are optional. Their defaults are:

| Setting | Default |
|---|---|
| `POSTGRES_DB` | `tahseel` |
| `POSTGRES_USER` | `tahseel` |
| `POSTGRES_PORT` | `5432` |

Set `DOMAIN=localhost` for local use. For a public deployment, replace it with the
public DNS name. The remaining variables in `.env.example` are for future application
configuration and are not required to start the current Docker Compose stack. This
includes OpenRouter, embedding, application, and `NEXT_PUBLIC_API_URL` settings.

### 3. Start the stack

From the repository root:

```bash
docker compose up --build -d
docker compose ps
```

Compose starts PostgreSQL with pgvector, the FastAPI backend, and the Next.js frontend.
Database migrations are not required for the current starter application's health checks.
Database-backed features may require migrations later; see `backend/README.md`.
The Caddy reverse proxy exposes HTTP and HTTPS on ports 80 and 443. Locally, use
`https://localhost` (Caddy's local certificate may not be trusted automatically).
Public deployment prerequisites and routing are documented in `deploy/README.md`.

### 4. Verify the services

In `docker compose ps`, the `db`, `backend`, `frontend`, and `proxy` services should
become `healthy`.

Then open:

- Frontend: https://localhost
- Frontend health: http://127.0.0.1:3000/api/health
- Backend health: http://127.0.0.1:8000/health
- PostgreSQL: `127.0.0.1:5432` by default

The frontend and backend health URLs should return `{"status":"ok"}`. The public
backend health check is https://localhost/api/health. These endpoints verify only the
current starter application, not unfinished collection, policy, memory, or agent
features.

If a port is already in use, stop the conflicting local service before starting Compose.
To use a different PostgreSQL host port, set `POSTGRES_PORT` in `.env`.

### 5. Stop the stack

From the repository root:

```bash
docker compose down
```

This stops and removes the Compose containers while preserving the named PostgreSQL
volume. Do not add `-v` or manually remove/prune Docker volumes unless you intend to
permanently delete the database and Caddy state after verifying a backup.

More deployment details are in `deploy/README.md`. The frontend and backend can also be
run separately using `frontend/README.md` and `backend/README.md`.

### Database backup and restore

Create a PostgreSQL custom-format backup from the running database. Keep backups
outside version control, encrypt them at rest, and copy them to protected off-host
storage:

```bash
mkdir -p backups
docker compose exec -T db sh -c \
  'pg_dump -Fc --no-owner -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  > "backups/tahseel-$(date -u +%Y%m%dT%H%M%SZ).dump"
```

For a full restore, restore into a new, empty database rather than over the live
database. `pg_restore --clean --if-exists` only removes objects present in the archive;
objects created after the backup but absent from it can remain. The following example
uses `tahseel_restore`. Choose a name that does not already exist; `createdb` will fail
rather than overwrite an existing database.

```bash
docker compose stop backend
docker compose exec -T db sh -c \
  'createdb -U "$POSTGRES_USER" tahseel_restore'
docker compose exec -T db sh -c \
  'pg_restore --no-owner --exit-on-error -U "$POSTGRES_USER" -d tahseel_restore' \
  < backups/tahseel-YYYYMMDDTHHMMSSZ.dump
```

Replace the example dump filename with the backup to restore. Verify the restored
database, then set `POSTGRES_DB=tahseel_restore` in `.env` and run
`docker compose up -d --force-recreate db backend` to point the application at it.
The existing database and PostgreSQL volume are left in place. Test restores against a
non-production database regularly; do not treat a successful backup command as proof
that a backup is restorable.

## Repository code layout

```text
backend/  FastAPI service, health endpoint, tests, and Docker configuration
frontend/ Next.js bilingual interface and tests
data/      Synthetic policy corpus and future seed datasets
evals/     RAG, agent, recommendation, and safety evaluation assets
deploy/    Docker Compose deployment documentation
database/  PostgreSQL initialization scripts
```
