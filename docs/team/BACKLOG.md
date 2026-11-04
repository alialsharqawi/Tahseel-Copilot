# Backlog

Generated from `backlog.csv` by `python tools/team_tools.py backlog`. Edit the CSV, not this file.

**Tiers** (Decision Log, D29): Core is never cut; Should is built after the core slice, in the cut order; Delivery is scheduled after the core slice works.

**Size** is a rough effort guess used only to balance the load: S about half a day, M one to two days, L three to five days.

**Wave** shows the order imposed by dependencies. Wave 1 tasks can start now; later waves wait for their dependencies.

**50 tasks:** 41 Core, 7 Should, 2 Delivery.

## Setup

| ID | Task | Tier | Skills | Size | Wave | Depends on |
|---|---|---|---|---|---|---|
| T-001 | Create the GitHub repository, protect main, add the team, load labels and issue templates | Core | GIT (also DOC) | S | 1 | - |
| T-002 | Create the repository skeleton: folders, .gitignore, .env.example, pre-commit hooks | Core | GIT (also DEVOPS) | S | 2 | T-001 |
| T-003 | Docker Compose basics: database with pgvector, backend, frontend, health check | Core | DEVOPS (also DB) | M | 3 | T-002 |
| T-004 | Continuous integration: lint and tests on every pull request | Core | DEVOPS (also QA) | S | 3 | T-002 |

## Backend

| ID | Task | Tier | Skills | Size | Wave | Depends on |
|---|---|---|---|---|---|---|
| T-010 | Data model and migrations for the 19 tables | Core | DB, PY (also API) | L | 4 | T-003 |
| T-011 | Authentication, users, and the three roles | Core | API, SEC (also PY) | M | 5 | T-010 |
| T-012 | Tenant-scoped data layer and the cross-tenant test | Core | DB, SEC (also QA) | M | 5 | T-010 |
| T-013 | Receivables engine: outstanding, overdue, aging, KPIs, with unit tests | Core | PY, QA (also DATA) | L | 5 | T-010 |
| T-014 | Risk score engine: factors, caps, rounding, tenant settings | Core | PY, QA | L | 6 | T-013, T-016 |
| T-015 | Priority, urgency, and the suggested-action rules | Core | PY, QA | M | 7 | T-014 |
| T-016 | Tenant settings and policy rules services with seeded defaults | Should | PY, DB (also API) | M | 5 | T-010 |
| T-017 | Cash forecast with range and confidence, plus the backtest harness | Should | PY, DATA (also QA) | L | 6 | T-013 |

## Data

| ID | Task | Tier | Skills | Size | Wave | Depends on |
|---|---|---|---|---|---|---|
| T-020 | Synthetic data generator with realistic patterns | Core | DATA, PY (also BIZ) | L | 5 | T-010 |
| T-021 | Seed script: tenants, users, settings, rules, sample policies | Core | PY, DATA (also DB) | M | 6 | T-016, T-020 |
| T-022 | Sample policy documents (about 20), including conflicting and missing cases | Core | DOC, AR (also BIZ) | M | 1 | - |

## Import

| ID | Task | Tier | Skills | Size | Wave | Depends on |
|---|---|---|---|---|---|---|
| T-030 | Import API: parse CSV and Excel, mapping, validation, preview | Core | PY, API (also DATA) | L | 6 | T-013 |
| T-031 | LLM-assisted column mapping from headers and masked sample rows | Core | LLM, PY | M | 7 | T-030, T-040 |
| T-032 | Receivables Health Report endpoint | Should | PY, API | M | 7 | T-014 |

## AI

| ID | Task | Tier | Skills | Size | Wave | Depends on |
|---|---|---|---|---|---|---|
| T-040 | LLMClient: OpenRouter, timeouts, retries, fallback, cost logging | Core | LLM, PY (also API) | M | 5 | T-010 |
| T-041 | Policy ingestion: parse, chunk, embed, store with the tenant filter | Core | VEC, PY (also DB) | L | 5 | T-010 |
| T-042 | retrieve_policy tool: rules, passages, citations, honest refusal | Core | VEC, LLM (also PY) | L | 6 | T-041, T-016 |
| T-043 | Agent orchestrator: tool-calling loop, tool registry, logging, number post-check | Core | LLM, PY (also API) | L | 6 | T-040, T-013 |
| T-044 | Agent tools: receivables, risk, priority, history, KPIs, forecast | Core | PY, LLM (also API) | M | 7 | T-043 |
| T-045 | Customer memory API: notes, call results, promises, promise status rule | Core | API, DB (also PY) | M | 5 | T-010 |
| T-046 | Note embeddings and the recall tool | Core | VEC, PY | M | 6 | T-045, T-041 |
| T-047 | Conversation memory: threads, last N turns, labeled summary | Core | LLM, API (also DB) | M | 7 | T-043 |
| T-048 | Draft generator: Arabic, tones, tier defaults | Core | LLM, AR (also PY) | L | 6 | T-040 |
| T-049 | Recommendations and the approval gate | Core | API, SEC (also PY) | L | 7 | T-043, T-011 |
| T-050 | Tasks and the append-only audit log | Core | DB, API (also SEC) | M | 8 | T-049 |
| T-051 | Guardrails: dispute status, the reminder cap, and the rule-based draft check | Should | API, PY (also QA) | M | 8 | T-048, T-049 |
| T-052 | Relationship-aware recommendation for strategic accounts | Should | PY | S | 8 | T-015 |

## Frontend

| ID | Task | Tier | Skills | Size | Wave | Depends on |
|---|---|---|---|---|---|---|
| T-060 | Frontend skeleton: Next.js, TypeScript, EN/AR dictionaries, RTL, navigation by role | Core | FE, UX (also GIT) | L | 3 | T-002 |
| T-061 | Import screen | Core | FE (also UX) | M | 7 | T-060, T-030 |
| T-062 | Executive dashboard | Core | FE, UX (also DATA) | L | 6 | T-060, T-013 |
| T-063 | Collection Queue screen | Core | FE (also UX) | M | 8 | T-060, T-015 |
| T-064 | Customer Profile screen with the note, call result, and promise form | Core | FE, UX | L | 6 | T-060, T-045 |
| T-065 | AI recommendation panel with all states | Core | FE, UX | L | 8 | T-049, T-048 |
| T-066 | Settings, policy rules, and documents screens | Should | FE (also UX) | M | 6 | T-016 |
| T-067 | Review all Arabic interface text | Core | AR, UX | M | 4 | T-060 |

## Quality

| ID | Task | Tier | Skills | Size | Wave | Depends on |
|---|---|---|---|---|---|---|
| T-070 | Evaluation harness and the basic eval sets | Core | EVAL, PY (also QA) | L | 7 | T-043, T-042 |
| T-071 | Ablation: LLM with the raw file versus the tool-grounded system | Core | EVAL, DATA (also DOC) | M | 8 | T-070 |
| T-072 | Safety tests: injection, cross-tenant, no send without approval | Core | QA, SEC | M | 8 | T-049 |
| T-073 | End-to-end demo rehearsal and bug list | Core | QA (also PRES) | M | 9 | T-065 |

## Delivery

| ID | Task | Tier | Skills | Size | Wave | Depends on |
|---|---|---|---|---|---|---|
| T-080 | HTTPS deployment and reverse proxy | Delivery | DEVOPS, SEC | L | 4 | T-003 |
| T-081 | README Quick Start and setup documentation | Delivery | DOC, GIT | S | 4 | T-003 |

## Docs

| ID | Task | Tier | Skills | Size | Wave | Depends on |
|---|---|---|---|---|---|---|
| T-090 | LMS part: Project Planning and Management | Core | DOC, BIZ | M | 1 | - |
| T-091 | Assemble the documentation PDF | Core | DOC (also GIT) | M | 2 | T-090 |
| T-092 | Presentation slides (PDF) from the pitch skeleton | Core | PRES, DOC | L | 1 | - |
| T-093 | Demo video | Core | PRES (also QA) | M | 10 | T-073 |
| T-094 | Local-competitor scan (assumption A9) | Should | BIZ (also DOC) | M | 1 | - |

## Acceptance criteria and AI tips

Each task's acceptance criteria and the references to read first are in `backlog.csv` and are copied into the GitHub issue.
