# Tahseel AI — Security-Baseline Audit Report

Snapshot of main as of 28 Nov 2026. Items marked Gap may be in progress on branches that were not visible to this audit.

**Branch:** `review/security-baseline-20261128` (created from `main`; `main` untouched)  
**Date:** 28 November 2026  
**Auditor:** report-only (no code, test, migration, or doc changes made)  
**Environment:** PostgreSQL 17 with pgvector 0.8.7 started locally on port 5433; `TEST_DATABASE_URL` set. No Docker Compose stack was used (port 5432 occupied by an unauthenticated instance).

## Executive summary

The implemented starter code is internally consistent and satisfies the tenant-isolation, role, and approval-gate rules where it exists. All 39 backend tests pass against a real pgvector PostgreSQL (0 skipped, 0 failed), including the gated integration tests. Alembic upgrade-to-head / downgrade-to-base / upgrade-to-head cycles run cleanly. `.env` is gitignored and untracked; `.env.example` carries only empty placeholder values; no real secrets exist in tracked files or git history. However, the Core product features required by Decision Log D29 are almost entirely not built: there is no receivables engine, no risk/priority computation, no policy RAG, no agent, no customer-memory write API, no draft API, no collection-task API, no approval-gate endpoints, and no basic eval. Zero Critical findings (nothing in the implemented code breaks a non-negotiable rule); the five High-severity gaps are all "documented Core feature missing from code" items already tracked on other PRs.

---

## Findings table

| ID | Area | Severity | Description | Evidence (file:line) | Decision ref | In PR # | Suggested fix | Verified? |
|----|------|----------|-------------|----------------------|--------------|---------|---------------|-----------|
| F-01 | Core features missing | Gap | Receivables engine (overdue calculation, risk scoring, priority) is documented as Core/never-cut but no engine code exists. The `risk_scores` table exists but nothing populates it; no route computes overdue days, risk, or priority. | `backend/api/v1/` contains only `auth.py`, `users.py`, `customers.py`; `backend/db/models.py:739-764` defines `risk_scores` with no computation code; no `engine/` or `scoring/` module | D29 (Core, never cut); D34; D43; D45 | PR #92 (overdue/aging only; risk scoring and priority not yet in any PR I could see) | Build T-013 receivables engine per D34/D43/D45 formulas | Verified |
| F-02 | Policy RAG | Gap | Policy RAG with citations (Core) is not built. No agent, no retrieval route, no vector-search API endpoint. `evals/rag/` contains only `no_policy_questions.md`. | `backend/api/v1/` has no policy/rag routes; `evals/rag/no_policy_questions.md` is the only eval asset | D29 (Core); D9; D21 | No PR seen by this audit. Team to confirm. | Build policy ingestion, tenant-filtered vector search, citation-returning query | Verified |
| F-03 | Approval gate | Gap | Human approval gate (Core) has no API endpoints. `enforce_recommendation_approval_role()` exists but is not called by any route; no recommendation/draft/message endpoints exist, so nothing can be approved or blocked from auto-send. | `backend/auth/dependencies.py:117-136` defines the function but no route imports/calls it; `backend/api/v1/` has no recommendation or draft routes | D3 (API-level enforcement); D29 (Core); D36 | No PR seen by this audit. Team to confirm. | Add recommendation/draft routes that call `enforce_recommendation_approval_role`; no auto-send endpoint | Verified |
| F-04 | Customer memory write | Gap | Customer memory (notes, promises, call outcomes) is Core but has no write API. Tables exist (`customer_notes`, `promises_to_pay`) but no endpoints to record them with author/timestamp/source. | `backend/db/models.py:289-328` (`customer_notes`), `237-287` (`promises_to_pay`); `backend/api/v1/` has no notes/promises routes | D10; D28; D29 (Core) | No PR seen by this audit. Team to confirm. | Add note/promise/outcome write endpoints with author/timestamp/source | Verified |
| F-05 | Drafts + guardrails | Medium | `draft_versions` table exists but no draft API and no rule-based draft-check guardrail (forbidden phrases, legal threats, tone by tier). | `backend/db/models.py:427-462` (`draft_versions`); no draft routes; no check service | D23 (lite guardrails); D29 (Core) | No PR seen by this audit. Team to confirm. | Add draft create/edit endpoints + draft-check service | Verified |
| F-06 | Collection tasks | Medium | `collection_tasks` table exists but no task API (create, list, complete, cancel). | `backend/db/models.py:465-534` (`collection_tasks`); no task routes | D29 (Core) | No PR seen by this audit. Team to confirm. | Add collection-task endpoints tied to recommendations | Verified |
| F-07 | Basic eval + ablation | Medium | Basic eval with LLM-only vs tool-grounded ablation (Core, never cut) is not built. `evals/rag/` has only `no_policy_questions.md`; no agent/recommendation/safety eval suites. | `evals/` directory contains only `rag/` and `README.md` | D29 (Core); D11 | No PR seen by this audit. Team to confirm. | Build ~15 agent cases, ~10 RAG queries, ~5 safety tests, ablation | Verified |
| F-08 | Navigation vs permissions | Medium | Frontend navigation shows "tasks" to all roles (`navigation.ts:20`), but D15/D30 restricts task ASSIGNMENT to Owner/Finance Manager only. The mismatch is documented as "navigation conventions, not authorization" in `frontend/README.md:25-27`, but the UI does not visually distinguish access from assignment. | `frontend/app/navigation.ts:20`; `frontend/README.md:25-27`; `auth/permissions.py:44` (`ASSIGN_TASKS: _MANAGER_ROLES`) | D15; D30 | No PR seen by this audit. Team to confirm. | Gate task-assignment actions server-side; clarify UI labels | Verified |
| F-09 | Core screens missing | Gap | Three core screens (dashboard, collection queue, customer profile) are Core but not built; frontend has only a welcome page (`page.tsx`). | `frontend/app/page.tsx:1-23` (welcome only); no `/dashboard`, `/queue`, `/customers` page components | D29 (Core); D14 | No PR seen by this audit. Team to confirm. | Build the three core bilingual screens | Verified |

**Severity totals:** Critical = 0, Gap = 5 (F-01, F-02, F-03, F-04, F-09), Medium = 4 (F-05, F-06, F-07, F-08), Low = 0.

No finding breaks tenant isolation, the approval gate, or any CLAUDE.md non-negotiable rule in the *implemented* code. All Gap findings are missing Core features (doc-to-code mismatches), not violated invariants.

---

## Read-only verification details

### 1. Test reality check

- **pytest run:** `39 passed, 0 skipped, 0 failed, 0 errors` against a real pgvector PostgreSQL on port 5433 with `TEST_DATABASE_URL` set. PostgreSQL-gated integration tests executed (not skipped): `test_postgresql_end_to_end_auth_users_and_collector_scope` (`test_auth_and_roles.py:1330`), `test_migration_upgrade_and_downgrade_on_postgresql` (`test_models.py:989`), and the `database_session`-gated tests in `test_tenant_access.py:36`.
- **Alembic cycle:** `upgrade head` → `downgrade base` → `upgrade head` on a clean database ran without failure (20 `CREATE TABLE`, unbounded `VECTOR`, no HNSW/ivfflat indexes).

### 2. select( / session.execute bypass check (widened pattern)

Grep of `backend/api` and `backend/auth` for `\.execute(`, `\.query(`, `\.get(`, `\.scalars(`, `\.scalar(`, `text(`, `select(`. Hits outside `db/tenant_access.py`:

| File:line | Code | Bypasses `db/tenant_access.py`? | Notes |
|-----------|------|---------------------------------|-------|
| `backend/api/v1/auth.py:70` | `statement = select(User).where(func.lower(User.email) == payload.email)` | Yes (direct `select(...)`) | Pre-authentication login lookup. Tenant context does not yet exist at login; `tenant_id` is optional disambiguation added as a filter at line 72 when provided. Intentional pre-scope lookup, not a data-access bypass. |
| `backend/api/v1/auth.py:73` | `candidates = list(db.scalars(statement).all())` | Yes (direct `db.scalars(...)`) | Same pre-auth login lookup as line 70; executes the statement built there. Tenant context does not yet exist. Intentional pre-scope lookup, not a data-access bypass. |
| `backend/api/v1/auth.py:108` | `scoped_access = TenantScopedDataAccess(db, TenantContext(user.tenant_id))` | No | Uses `tenant_access` (post-auth, tenant-scoped). |
| `backend/api/v1/auth.py:149` | `user = access.get(User, current_user.id)` | No | Uses `tenant_access` via `access` from `get_tenant_access`. |
| `backend/api/v1/users.py:83` | `user = access.get(User, user_id)` | No | Uses `tenant_access` via `access` from `get_tenant_access`. |
| `backend/api/v1/users.py:214` | `target = access.get(User, user_id)` | No | Uses `tenant_access` via `access` from `get_tenant_access`. |
| `backend/api/v1/users.py:263` | `updated = access.get(User, target.id)` | No | Uses `tenant_access` via `access` from `get_tenant_access`. |
| `backend/auth/dependencies.py:53` | `scoped_access = TenantScopedDataAccess(db, TenantContext(payload.tenant_id))` | No | Uses `tenant_access`. |
| `backend/auth/dependencies.py:54` | `user = scoped_access.get(User, payload.user_id)` | No | Uses `tenant_access`. |
| `backend/auth/dependencies.py:77` | `return TenantScopedDataAccess(db, TenantContext(current_user.tenant_id))` | No | Uses `tenant_access`. |
| `backend/auth/dependencies.py:155` | `customer = access.get(Customer, customer_id)` | No | Uses `tenant_access` via `access` from `get_tenant_access`. |

Other matches were decorators (`@router.get(` at `auth.py:129`, `users.py:26`, `users.py:56`, `customers.py:20`, `customers.py:30`) and a dict lookup (`raw_claims.get("type")` at `security.py:108`) — none are database access.

Only `auth.py:70` and `auth.py:73` issue raw queries outside `TenantScopedDataAccess`, both inside the pre-authentication login flow where no tenant context exists yet. All customer/user routes (`customers.py`, `users.py`) use `get_tenant_access`.

### 3. Direct unit test for `enforce_recommendation_approval_role`

**No dedicated/direct unit test function exists.** The function is imported at `test_auth_and_roles.py:30` and exercised inline (6 calls) within `test_ac014_and_d15_d30_permissions_matrix` (`test_auth_and_roles.py:1016-1067`). It is covered indirectly, but there is no standalone test named for it.

---

## Canonical spec table (D34, D36, D43)

| Spec item | Canonical value | Sources | Status in code | Disagreements |
|-----------|----------------|---------|----------------|---------------|
| Risk weights | `days_overdue = 30`, `historical_delay = 25`, `broken_promises = 25`, `recent_behavior = 20` (total 100); weights live in `tenant_settings`, not code | Decision Log D34 (`docs/governance/Tahseel_AI_Decision_Log.md:332`); PRD line 28 ("Default weights 30/25/25/20") | Not implemented — no engine code; `risk_scores` table exists (`db/models.py:739-764`) but is never populated | None documented vs code; weights exist only in docs |
| Risk levels (after integer rounding) | LOW 0–30, MEDIUM 31–60, HIGH 61–80, CRITICAL 81–100 | Decision Log D34 (`...:336`); `db/models.py:742` (`ck_risk_scores_level_allowed_values`) | Enum present in `risk_scores.level`; not populated by any code | None |
| Risk score meaning | Behavior only (likelihood to pay late); exposure leaves risk and enters priority only; collection probability used only by forecast, never priority | Decision Log D34 (`...:333-338`); PRD line 28 | Not implemented | None |
| Priority formula | `normalize(Risk x Overdue Exposure x Urgency)`; top account scores 100 | Decision Log D34 (`...:334`); PRD lines 523-524 | Not implemented | None |
| Action vocabulary (recommendations) | CALL, WHATSAPP, EMAIL, WAIT, ESCALATE_TO_MANAGER, TALK_TO_SALES_REP; `REVIEW_CREDIT_TERMS` removed | Decision Log D36 (`...:366`); `db/models.py:366-376` (`recommendations.action` check constraint) | Implemented as enum in `recommendations` | None |
| Action vocabulary (collection_tasks) | Same six actions | `db/models.py:469-478` (`collection_tasks.action` check constraint) | Implemented as enum in `collection_tasks` | None |
| Aging buckets | Current (`due_date >= report_date`), 1–30, 31–60, 61–90, 91+ (No upper bound); inclusive, non-overlapping | Decision Log D43 (`...:447`); PRD lines 402-404, 411 (`DEFAULT_AGING_BUCKETS = ((1, 30), (31, 60), (61, 90), (91, None))`) | Not implemented — no aging engine code | None |
| Disputed invoices in aging | Included in aging totals + overdue amount + ratio + DSO, flagged separately; excluded from priority queue | Decision Log D43 (`...:447`); D45 (`...:463`); PRD line 434 | Not implemented | None |

---

## Gap analysis vs D29 (Core tier — never cut)

| D29 Core item | Status | Evidence (one line) |
|---------------|--------|---------------------|
| Import receivables | Not started | No import route/adapter in `backend/api/v1/`; only a CSV sample at `data/demo/receivables_import_sample.csv` |
| Receivables engine | Not started | No scoring/overdue/priority code anywhere in `backend/` |
| Risk with factors | Not started | `risk_scores` table exists (`db/models.py:739-764`) but nothing populates it |
| Priority + Collection Queue | Not started | `collection_tasks` table exists (`db/models.py:465-534`) but no queue or task API |
| Policy RAG with citations | Not started | No policy/retrieval routes; `evals/rag/` has only `no_policy_questions.md` |
| Customer memory (notes/promises/outcomes) | Models only | `customer_notes` + `promises_to_pay` tables exist but no write API |
| Agent | Not started | No agent/tool-calling loop; no `agent_run`-driven endpoints |
| Drafts | Models only | `draft_versions` table exists (`db/models.py:427-462`) but no draft API or guardrail check |
| Approval gate | Not started | `enforce_recommendation_approval_role` defined (`auth/dependencies.py:117`) but never called by a route |
| Tasks + audit log | Partial | `audit_logs` written by `auth.py:109-119` and `users.py:147-161, 270-285`; `collection_tasks` model exists with no task API |
| Three core screens | Not started | Frontend has only welcome page (`frontend/app/page.tsx:1-23`) |
| Tenant isolation with roles | Built + tested | `db/tenant_access.py` + 3-role RBAC; all 39 tests pass incl. tenant-isolation integration tests |
| Basic eval with ablation | Not started | `evals/` lacks agent/recommendation/safety suites |

---

## Could not verify

| Item | Reason |
|------|--------|
| Frontend build/lint/tests (`npm ci`, `npm run lint`, `npm test`, `tsc --noEmit`, `npm run build`) | Node.js not confirmed installed in this environment; scope deferred per instructions (no Arabic UI/CSS/i18n review) |
| Ruff lint/format on backend (`ruff check backend`, `ruff format --check backend`) | Not run; ruff is installed in the venv but not executed during this audit |
| CI workflow execution | GitHub Actions cannot be run locally; reviewed `.github/workflows/ci.yml` statically (see below) |
| Public deployment (Caddy HTTPS, domain, DNS, VPS) | Requires a configured domain and external infrastructure; not available locally |
| Arabic wireframes / bidi rendering | Deferred per instructions |
| Import CSV semantics beyond the sample | Deferred per instructions |

---

## CI workflow review (`.github/workflows/ci.yml`)

CI sets `TEST_DATABASE_URL` and `DATABASE_URL` (lines 20-22) to a localhost PostgreSQL service (pgvector image, line 25), installs backend dependencies (line 50), runs lint (lines 53-55), and runs `python -m pytest` (line 59) from `backend/`. Because `TEST_DATABASE_URL` is set, the PostgreSQL-gated integration tests (`test_postgresql_end_to_end_auth_users_and_collector_scope` at `test_auth_and_roles.py:1330`, `test_migration_upgrade_and_downgrade_on_postgresql` at `test_models.py:989`, and the `database_session`-gated tests in `test_tenant_access.py:36`) **do execute in CI** and are not skipped. Frontend CI (lines 61-86) runs lint and tests but does not set a database variable (frontend tests do not require PostgreSQL).

---

## Secrets scan summary

- `.env` is listed in `.gitignore` (`.gitignore:14`) and is **not tracked** (`git ls-files .env` returns empty). A local `.env` file exists on disk (544 bytes, dated 25 Nov 2026) but is untracked.
- `.env.example` is tracked and contains **only empty placeholder values** (e.g. `APP_SECRET_KEY=`, `POSTGRES_PASSWORD=`, `OPENROUTER_API_KEY=`). Git history shows it was deliberately blanked in commit `0694809` ("chore(repo): blank the remaining .env.example defaults").
- Grep of tracked files and git history for `sk-`, `AKIA`, `github_pat`, `glpat`, `ghp_`, hardcoded `password=`, `token=`, `api_key=`, `APP_SECRET_KEY=`, `DATABASE_URL=` found **no real secrets**. The only secret-like string is `TEST_SECRET = "synthetic-test-secret-key-at-least-32-bytes-long"` in `backend/tests/test_auth_and_roles.py:52`, which is an explicitly synthetic test value.

---

## Compliance with CLAUDE.md non-negotiable rules (implemented code only)

| Rule | Implemented-code status |
|------|------------------------|
| 1. Numbers from tested code | No financial figures are computed by routes (no engine exists); synthetic data generator is tested (`test_synthetic_data.py`) |
| 2. Never invent policy | No hard-coded thresholds in code; policy would live in `policy_rules` table (`db/models.py:664-705`) |
| 3. Human approval at API | No auto-send endpoint exists; approval function defined but not yet wired to routes (F-03) |
| 4. Customer memory rules | Memory model enforces author/timestamp/source via schema; LLM never writes memory (no agent exists yet) |
| 5. Honesty about evidence | No claims of real customers/pilots in code; synthetic data labeled (`scripts/generate_synthetic_data.py:394`) |
| 6. Tenant isolation | Every table has `tenant_id`; `TenantScopedDataAccess` filters by `tenant_id` on all CRUD/vector operations (`db/tenant_access.py:37-153`) |
| 7. Untrusted input as data | No RAG/agent ingestion path exists yet; to be addressed when built |
| 8. No secrets in repo | `.env` gitignored+untracked; `.env.example` empty; no secrets in history |
| 9. Decision changes logged | Audit scope is report-only; no decisions changed |
| 10. Scope within tiers | No features beyond Core/Should/Delivery in code (Core features are missing, not extra) |

---

## Ledger entry (Consistency Ledger, D35)

Added to `docs/governance/Tahseel_AI_Consistency_Ledger.md` as finding #99 so this report is not an orphan:

| 99 | Security-baseline audit report produced (`Tahseel_AI_Audit_Report.md`): 0 Critical, 5 Gap, 4 Medium findings; no tenant-isolation, approval-gate, or non-negotiable-rule violations in implemented code; Core-tier receivables engine, policy RAG, agent, memory write API, draft API, task API, approval-gate endpoints, and basic eval are not yet built | `docs/governance/Tahseel_AI_Audit_Report.md` | Open | Open |

Ledger numbering note: entry numbers #53 and #76 were never used (confirmed by scanning all ledger rows); #99 is the highest entry and collides with nothing on main (max 98) or on open PR branches #92/#93 (max 98). Not a finding.

---

# Doc consistency audit (read-only, no changes made)

Authority order per D35: Decision Log > Final Concept > PRD > Strength docs > Pitch.
Every finding cites file:line evidence. "Kind" classifies each row as Decision (a cross-doc conflict needing a governing doc) or Doc fix (missing documentation to add). "Winner per D35" identifies which document's statement governs when two docs conflict, or "needs team decision" where no doc resolves the gap.

Headline count: Findings = 14 (DA-01 to DA-13, DA-19), of which 7 need a team decision (DA-08, DA-09, DA-10, DA-11, DA-12, DA-13, DA-19). Confirmations = 5 (DA-14 to DA-18, no fix needed).

| ID | Kind | Type | What conflicts or is undefined | Evidence file:line | Winner per D35 or "needs team decision" | Suggested minimal doc fix |
|----|------|------|-------------------------------|-------------------|------------------------------------------|---------------------------|

### Findings (need resolution)

| DA-01 | Doc fix | Undefined value set | `agent_runs.run_type` column exists in `db/models.py:346` and PRD schema (`Tahseel_AI_PRD.md:1239`) but no allowed values are documented anywhere. | `db/models.py:346`; `Tahseel_AI_PRD.md:1239`; no doc defines run_type values | needs team decision | Add allowed run_type values (e.g. `forecast`, `risk`, `priority`, `rag`, `draft`) to PRD schema section and/or Decision Log |
| DA-02 | Doc fix | Undefined value set | `agent_runs.status` column exists in `db/models.py:350` and PRD schema (`Tahseel_AI_PRD.md:1243`) but no allowed values are documented anywhere. | `db/models.py:350`; `Tahseel_AI_PRD.md:1243`; no doc defines status values | needs team decision | Add allowed status values (e.g. `pending`, `completed`, `failed`) to PRD schema section |
| DA-03 | Doc fix | Undefined value set | `recommendations.action` has check constraint with six values in `db/models.py:366-376` but PRD schema table (`Tahseel_AI_PRD.md:1095`) lists only `action` without allowed values. D36 documents them in prose. | `db/models.py:366-376`; `Tahseel_AI_PRD.md:1095`; Decision Log D36 (`Tahseel_AI_Decision_Log.md:366`) | Decision Log D36 wins | Add the six action values to PRD schema table for `recommendations.action` and `collection_tasks.action` |
| DA-04 | Doc fix | Undefined value set | `collection_tasks.priority` has check constraint (HIGH/MEDIUM/LOW) in `db/models.py:470-471` but PRD schema (`Tahseel_AI_PRD.md:1129`) lists only `priority` without values. | `db/models.py:470-471`; `Tahseel_AI_PRD.md:1129` | needs team decision | Add priority values to PRD schema table |
| DA-05 | Doc fix | Undefined value set | `collection_tasks.action` has check constraint with six values in `db/models.py:469-478` but PRD schema (`Tahseel_AI_PRD.md:1130`) lists only `action` without values. | `db/models.py:469-478`; `Tahseel_AI_PRD.md:1130` | Decision Log D36 wins | Add the six action values to PRD schema table |
| DA-06 | Doc fix | Undefined value set | `draft_versions.tone` has check constraint (formal/friendly/firm) in `db/models.py:430-431` but PRD schema (`Tahseel_AI_PRD.md:1112`) lists only `tone` without values; PRD prose mentions them at line 815. | `db/models.py:430-431`; `Tahseel_AI_PRD.md:1112`; `Tahseel_AI_PRD.md:815` | PRD prose wins | Add tone values to PRD schema table |
| DA-07 | Doc fix | Undefined value set | `risk_scores.level` has check constraint (LOW/MEDIUM/HIGH/CRITICAL) in `db/models.py:742` but PRD schema (`Tahseel_AI_PRD.md:1228`) lists only `level` without values; D34 documents them. | `db/models.py:742`; `Tahseel_AI_PRD.md:1228`; Decision Log D34 (`Tahseel_AI_Decision_Log.md:336`) | Decision Log D34 wins | Add level values to PRD schema table |
| DA-08 | Decision | Key-name mismatch | Risk-weight key names differ across docs: Decision Log D34 uses prose ("days overdue", "historical delay", "broken promises", "recent behavior") with no code key names; PRD example uses `historical_delay`, `recent_behavior` (`Tahseel_AI_PRD.md:719,721`); PR 93 schema uses `historical_payment_delay`, `recent_payment_behavior` (`backend/configuration/schemas.py:26,29`). Only `days_overdue` and `broken_promises` are consistent. | `Tahseel_AI_Decision_Log.md:332`; `Tahseel_AI_PRD.md:719,721`; `backend/configuration/schemas.py:26,29` (PR 93 diff) | needs team decision (D34 is prose-only; no doc wins under D35) | Align PR 93 schema key names with PRD example (`historical_delay`, `recent_behavior`) or update PRD example to match; document the canonical key names in one place |
| DA-09 | Decision | Capability with no spec home | D23 says "the agent may flag a suspected dispute from collector notes" but this capability is not specified in the PRD schema, API, or agent tools. | `Tahseel_AI_Decision_Log.md:225` (D23); `Tahseel_AI_PRD.md` (no flag-suspected-dispute spec); `backend/api/v1/` (no dispute-flag route) | needs team decision | Add the flag-suspected-dispute capability to PRD (agent tool + route + rule) or remove it from D23 |
| DA-10 | Doc fix | Dangling reference | FR-23 and FR-24 are referenced in `docs/team/backlog.csv:28` (T-048 draft generator). They are defined in LMS parts 03 (`docs/lms/parts/03_Requirements_and_Stakeholders.md:110-111`) but NOT in the PRD. | `docs/team/backlog.csv:28`; `docs/lms/parts/03_Requirements_and_Stakeholders.md:110-111`; `Tahseel_AI_PRD.md` (no FR-23/FR-24) | needs team decision | Add FR-23/FR-24 to PRD acceptance criteria or FR table, or drop the references from backlog.csv |
| DA-11 | Doc fix | Term missing from GLOSSARY | The six D36 action names (CALL, WHATSAPP, EMAIL, WAIT, ESCALATE_TO_MANAGER, TALK_TO_SALES_REP) are used in `db/models.py` and D36 but are not defined as glossary terms. | `db/models.py:366-376,469-478`; `Tahseel_AI_Decision_Log.md:366`; `GLOSSARY.md` (no entry for the six actions) | needs team decision | Add the six action names to GLOSSARY |
| DA-12 | Doc fix | Term missing from GLOSSARY | "approval gate" is used in `Final_Concept.md:45` (C10), `Final_Concept.md:239`, and `PROJECT_STATUS.md` but is not a glossary term. | `Tahseel_AI_Final_Concept.md:45,239`; `PROJECT_STATUS.md`; `GLOSSARY.md` (no entry) | needs team decision | Add "approval gate" to GLOSSARY |
| DA-13 | Decision | Cross-doc mismatch | `customers.contact_person` exists in `db/models.py:141` and PRD schema (`Tahseel_AI_PRD.md:1014`) but has no API write path, noted in Consistency Ledger as an open info item. | `db/models.py:141`; `Tahseel_AI_PRD.md:1014`; `Tahseel_AI_Consistency_Ledger.md` (round 2 info item) | needs team decision | Add contact_person write path or document it as intentionally absent |
| DA-19 | Decision | Type mismatch | Urgency multipliers are `float` (2.0, 1.5, 1.0) in PR 93 `UrgencySettings` (`backend/configuration/schemas.py:52-62`) while exposure amounts are `Decimal`/`Numeric(14,2)` (`db/models.py` invoice/payment columns; PRD line 1805 "Use Decimal with no engine-level rounding"). Mixing float and Decimal in priority multiplication risks rounding/precision issues. | `backend/configuration/schemas.py:52-62` (PR 93 diff); `db/models.py:185-186,199-200`; `Tahseel_AI_PRD.md:1805` | needs team decision | Define urgency as Decimal or cast explicitly at the multiplication point; document the numeric type contract |

### Confirmations (no fix needed)

| DA-14 | Doc fix | Role matrix consistency | D15/D30 permission matrix is fully implemented in `auth/permissions.py:38-55` and tested in `backend/tests/test_auth_and_roles.py:1069-1098`. No mismatch found between Decision Log, PRD, models, and code. | `Tahseel_AI_Decision_Log.md:123-139`; `auth/permissions.py:38-55`; `db/models.py:90-95` | Decision Log D15/D30 | No fix needed — fully consistent |
| DA-15 | Doc fix | Tier consistency | Final Concept section 3 (Core C1-C14, Should S1-S7, Delivery P1) matches Decision Log D29 Core list. No mismatch found. | `Tahseel_AI_Final_Concept.md:32-67`; `Tahseel_AI_Decision_Log.md:301-306` | Both consistent | No fix needed |
| DA-16 | Doc fix | Deadline consistency | D40 sets final defense at 15 December 2026; `PROJECT_STATUS.md` confirms the same date. No mismatch. | `Tahseel_AI_Decision_Log.md:418-421`; `PROJECT_STATUS.md:4` | Both consistent | No fix needed |
| DA-17 | Doc fix | Repo name consistency | D26 (amended) sets repository name as `Tahseel-Copilot`; `README.md` and all references use `Tahseel-Copilot`. No mismatch. | `Tahseel_AI_Decision_Log.md:244-248`; `README.md:28` | Both consistent | No fix needed |
| DA-18 | Doc fix | Table count consistency | `test_models.py:698` asserts 19 tables; `db/models.py` defines 19 tables; Final Concept section 8 lists 19 (16 + 3 added); migration 0001 creates 19 tables. All consistent. | `backend/tests/test_models.py:698`; `db/models.py`; `Tahseel_AI_Final_Concept.md:185-187`; `backend/alembic/versions/0001_initial_schema.py` | All consistent | No fix needed |



# Leader decision sheet

Exactly 7 decisions needed from the team leader. Status for all rows: "Open - leader to decide". None are decided in this report.

| ID | Decision needed | Options | Suggestion (not decided) | What breaks if undecided | Status |
|----|-----------------|---------|--------------------------|--------------------------|--------|
| DA-08 | Risk-weight config keys | Code names (`historical_payment_delay`, `recent_payment_behavior`) / PRD names (`historical_delay`, `recent_behavior`) | Code names; update PRD lines 718-721 | Engine reads the wrong key; a `.get()` default would silently score the factor as 0 | Open - leader to decide |
| DA-19 | Urgency multiplier type | `Decimal` in config / `float` in config with one explicit conversion in the engine | Keep `float`, convert in the engine, document in PRD | `Decimal * float` raises `TypeError` | Open - leader to decide |
| DA-01/02 | `agent_runs.run_type` and `status` value sets | Any strings / constrained enumerated sets | Suggestion for status: `PENDING | RUNNING | SUCCEEDED | FAILED`. `run_type`: derive from the agent's actual workflows | Parallel PRs invent different strings; no check constraint can catch it | Open - leader to decide |
| DA-09 | D23 flag-suspected-dispute | Core / Should / remove | Agent suggests, human confirms; Should tier unless Core is needed | Capability exists in one doc with no spec | Open - leader to decide |
| DA-04 | `collection_tasks.priority` | Computed from score thresholds / set manually | Computed; thresholds in `tenant_settings` | No documented rule | Open - leader to decide |
| DA-13 | `customers.contact_person` write path | Add to API / document as seed-only | Add | Imported customers have no contact person and the UI cannot fix it | Open - leader to decide |

## Doc fixes pending leader decisions

All marked "Doc fix - not started".

| ID | Doc fix | What to do | Status |
|----|---------|------------|--------|
| DA-03 | Copy `recommendations.action` six values from D36/models into the PRD schema table | Add allowed values to PRD schema table for `recommendations.action` | Doc fix - not started |
| DA-05 | Copy `collection_tasks.action` six values from D36/models into the PRD schema table | Add allowed values to PRD schema table for `collection_tasks.action` | Doc fix - not started |
| DA-06 | Copy `draft_versions.tone` three values from D23/models into the PRD schema table | Add tone values to PRD schema table | Doc fix - not started |
| DA-07 | Copy `risk_scores.level` four values from D34/models into the PRD schema table | Add level values to PRD schema table | Doc fix - not started |
| DA-11 | Add the six D36 action names to GLOSSARY | CALL, WHATSAPP, EMAIL, WAIT, ESCALATE_TO_MANAGER, TALK_TO_SALES_REP | Doc fix - not started |
| DA-12 | Add "approval gate" to GLOSSARY | Define the term | Doc fix - not started |
| DA-10 | Decide the official home for FR-23/FR-24 | Currently defined in LMS part 03 (`docs/lms/parts/03_Requirements_and_Stakeholders.md:110-111`); referenced in `docs/team/backlog.csv:28`. Either add to PRD or drop backlog references. | Doc fix - not started |
## Specs other work depends on (sorted by likelihood someone builds on them next)

1. **PRD section 30 Acceptance Criteria** (`Tahseel_AI_PRD.md:1737-1807`) — AC-001 through AC-015 make every Core capability testable; PR #92 (receivables engine) builds directly on AC-002, AC-010, AC-015.
2. **Decision Log D34 scoring specification** (`Tahseel_AI_Decision_Log.md:330-339`) — risk weights, levels, priority formula; PR #92 implements the engine but risk scoring (T-014) builds on this next.
3. **Decision Log D36 action vocabulary** (`Tahseel_AI_Decision_Log.md:366`) — the six actions; PR #93's policy-rules service references `review_required` rule_type which ties to `ESCALATE_TO_MANAGER`.
4. **PRD section 12 Collection Priority** (`Tahseel_AI_PRD.md:505-527`) — urgency values (2.0/1.5/1.0) and windows; PR 93 `UrgencySettings` matches these exactly.
5. **Decision Log D23 lite guardrails** (`Tahseel_AI_Decision_Log.md:223-231`) — dispute status, reminder cap, draft check; the flag-suspected-dispute agent capability has no spec home (DA-09).
6. **LMS parts 03 FR table** (`docs/lms/parts/03_Requirements_and_Stakeholders.md:63-132`) — FR-01 through FR-32; FR-23/FR-24 defined here but not in PRD (DA-10).
7. **GLOSSARY** (`GLOSSARY.md`) — missing six D36 actions and "approval gate" (DA-11, DA-12).
