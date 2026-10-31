# Tahseel AI — Final Concept (Capstone Scope)

**Tahseel — تحصيل — means "collection".**
**Status:** Consolidated version, 31 October 2026. This file owns the scope: what is in the MVP, what is not, the tiers, the demo flow, and the roadmap. Decisions live in `Tahseel_AI_Decision_Log.md`; if this file disagrees with the log, the log wins (D35). Formulas, schema fields, and the API are specified in `Tahseel_AI_PRD.md`.
**Submission details:** see `LMS_Requirements.md`.

---

## 1. One-Liner

**Spoken:** "Every morning, Tahseel tells a distributor's collection team which customers to chase, why, and exactly what to say."

**Documentation:** "Tahseel helps Egyptian distributors collect overdue invoices faster by telling the finance team who to call today, why, and what to say, based on payment history and the company's own credit policy."

Technical framing (architecture section only): an agentic credit-control copilot, with deterministic numbers, cited policy RAG, memory, and human approval. See `Tahseel_AI_Technical_Strength.md` and `Tahseel_AI_Business_Strength.md`.

---

## 2. Problem and User

- **Problem:** Distributors sell on credit. The data (invoices, payments, promises, notes) exists in Excel, ERP exports, WhatsApp, and people's heads, but nobody turns it into a clear daily collection decision.
- **Primary user:** the Collector (the collection officer): the Collection Queue, customer context, message drafts.
- **Secondary users:** Finance Manager (approvals, risk and cash visibility), Owner (summary).
- **Value we aim to measure (hypotheses until validated):** lower average days beyond terms (the primary metric, D32), lower overdue receivables, DSO as the unit that converts time into cash, less time spent sorting spreadsheets, clearer 7/30-day cash expectations.

---

## 3. What We Build (and What We Don't)

Capabilities are grouped in three tiers (D29). The cut order is in the Decision Log, section E.

### Core: the demo cannot run without these (never cut)

| # | Capability |
|---|---|
| C1 | CSV/Excel import with column mapping, validation, and preview |
| C2 | Receivables engine: outstanding, days overdue, per-customer aggregates, covered by tests |
| C3 | Explainable rule-based risk score (0-100) with human-readable factors (D34) |
| C4 | Priority score and the ranked **Collection Queue**, each row with a rule-based suggested action (D36) |
| C5 | Policy RAG with citations (credit policy, collection policy, templates), including "no relevant policy found" and "policy conflict" answers |
| C6 | **Memory** (see section 6.3): customer memory and conversation memory (D28) |
| C7 | **Recording notes, promises to pay, and call outcomes.** This is how customer memory is written; the agent never writes it (D28) |
| C8 | Agent with tool calling: answers questions about a customer and recommends the next action. Token and cost logging per run (D12) |
| C9 | Message draft generator (Arabic, selectable tone) |
| C10 | Human approval gate (Approve / Edit / Reject), enforced at the API |
| C11 | Task creation and an append-only audit log of every recommendation, approval, and tool call |
| C12 | Dashboard: three screens (Executive, Queue, Customer Profile with the AI panel) |
| C13 | **Tenant isolation and role-based access** (Owner, Finance Manager, Collector), with a cross-tenant test |
| C14 | **Basic evaluation** with the LLM-only versus tool-grounded ablation (D11, D29) |

### Should: built after the core slice, in the cut order

| # | Capability |
|---|---|
| S1 | Simple 7/30-day cash forecast with a range and a stated confidence, plus a time-split backtest harness on synthetic data |
| S2 | **Relationship-aware recommendations:** sales rep note and customer tier are inputs; for strategic accounts the recommendation is `TALK_TO_SALES_REP` first (D36) |
| S3 | **Instant Receivables Health Report** on first upload (aging, risk distribution, top 20 accounts to chase, expected cash) |
| S4 | **Full Arabic (RTL) and full English UI** with a language toggle. The string-dictionary structure exists from day one; only the polish can be cut (D14) |
| S5 | **Two-layer policy:** structured rules in `policy_rules` evaluated by code, plus document RAG for explanation and citation (D21) |
| S6 | **Tenant configuration:** weights, grace periods, escalation triggers, reminder cap, and tone defaults in `tenant_settings`; canonical data schema with the CSV/Excel adapter (D22) |
| S7 | **Lite guardrails:** human-set `disputed` status, reminder cap, rule-based draft check (D23) |

### Delivery: scheduled after the core slice works

| # | Capability |
|---|---|
| P1 | Production practices: Docker Compose, environment config, migrations, seed script, health check, CI with lint and tests (the "basics"), then HTTPS deployment, structured logging, and the rest of the checklist in D17. If the core slice is not complete, deployment is skipped and a recorded demo is used |

### Simplified for the capstone

| PRD version | Capstone version | Why |
|---|---|---|
| 5 separate agents | **One orchestrator with grouped tools** (risk, receivables, policy, forecast, history, drafting, tasks, KPIs) | Easier to build, test, and defend (D7) |
| Hybrid retrieval + reranking | Vector search (pgvector) + metadata filters + citation | Reranking is an optional upgrade (D9) |
| 5 RBAC roles | 3 roles: Owner, Finance Manager, Collector | Enough to show permissions and approval flow (D15) |
| Celery + Redis | FastAPI background tasks | Less infrastructure |
| 500 customers / 5,000 invoices | ~120 customers / ~1,500 invoices, synthetic | Enough patterns, fast to generate and demo (D20) |
| Cloud deployment + HTTPS | Docker Compose first; HTTPS deployment in the Delivery tier; recorded demo as fallback | Production-mindedness lifts Architecture, Code Quality, and Real-World Value (D17) |

### Out of scope for the capstone (explicit non-goals)

Payments and wallets, automatic credit blocking, automatic WhatsApp or email sending, legal advice, ERP/CRM integrations (only the CSV/Excel adapter is built; the adapter interface is in scope), a trained ML risk model, and credit-limit recommendations (storing a customer's credit limit as data is fine). Later ideas that are not rejected are in the roadmap (section 12).

---

## 4. Core Demo Flow

This is the single canonical flow. `Final_Pitch` adds timing and numbers but does not change the steps.

```text
1.  Upload the receivables CSV (mapping, validation, preview)
2.  Dashboard / Health Report: total, overdue, high-risk exposure, expected cash
3.  Collection Queue ranks customers (risk, priority, suggested action)
4.  Open a customer: invoices, payments, promises, risk explanation
5.  Ask the agent: "What should we do with this customer?"
6.  Agent calls tools, retrieves the relevant policy, reads customer memory
7.  Agent returns recommendation + reasons + policy citation
8.  Generate an Arabic message draft (choose a tone)
9.  Collector or Finance Manager edits and approves (flagged items go to the Finance Manager)
10. Task is created, event is written to the audit log
11. Collector records the call result: a note and a promise to pay (customer memory)
12. Follow-up question in the same chat uses conversation memory; "what did we agree last time?" finds the recorded note
```

**Extra moments if the Should tier is built:** switch the language to Arabic (S4); switch to a Finance Manager to approve a flagged recommendation (S5, C13); mark an invoice as disputed and watch it leave the queue (S7); hit the reminder cap and see the manager override (S7).

---

## 5. Key Design Decisions

1. **Numbers come from code, not from the LLM.** Outstanding, overdue days, risk score, priority, and forecast are computed deterministically and tested. The LLM only explains, retrieves policy, drafts, and answers questions by calling those tools. This prevents invented financial facts.
2. **Explainable risk, no fake ML.** Weighted rules with default weights: days overdue 30, historical delay 25, broken promises 25, recent behavior 20. The weights are configurable per tenant (`tenant_settings`). The score estimates likelihood of late payment, so the amount owed is not part of it (D34). Every score lists its factors.
3. **Priority is separate from risk.** Priority = normalize(Risk x Overdue Exposure x Urgency). Factors are shown. Exact formulas are in the PRD.
4. **Human-in-the-loop everywhere it matters.** The AI recommends and drafts. It never sends, blocks, or changes financial records.
5. **Never invent policy.** If no relevant policy is retrieved, say so. If policies conflict, flag for human review. Hard thresholds are structured rules evaluated by code; RAG explains and cites (D21).
6. **Forecast is expected cash, not guaranteed cash.** Each invoice contributes `outstanding x probability of payment in the window`, where the probability (the collection probability) comes from that customer's historical behavior. Promises are weighted by the customer's promise-keep rate. Output includes a low/expected/high range and a confidence label. The collection probability is used by the forecast only.
7. **Data honesty.** The demo uses synthetic data, generated with realistic patterns (reliable payers, chronic late payers, partial payments, broken promises, seasonality). We do not claim real pilot customers unless we actually have them.
8. **Memory has a write rule.** Customer memory contains only human-authored or rule-derived events. Conversation memory is context, never a source of facts (D28).

---

## 6. AI Layer

### 6.1 Agent tools

| Tool | Purpose |
|---|---|
| `get_receivables(customer_id)` | Outstanding, overdue, max days overdue |
| `get_customer_history(customer_id)` | Invoices, payments, promises, collector notes |
| `get_portfolio_kpis(window_days)` | Totals, overdue ratio, average days beyond terms, DSO |
| `calculate_risk(customer_id)` | Score, level, factors |
| `calculate_priority(customer_id)` | Priority score and factors |
| `retrieve_policy(query, customer_id?)` | Policy chunks with citation, plus triggered policy rules |
| `forecast_cash(window_days)` | Expected cash with range and confidence |
| `draft_message(customer_id, tone)` | Arabic draft using data + policy context |
| `create_task(...)` | Only after human approval |

No tool writes customer memory. Notes, promises, and outcomes are written by humans through the UI and API (C7).

### 6.2 RAG

- **Sources:** credit policy, collection policy, payment terms, approved message templates, customer contracts (synthetic), and collector notes (so RAG is not limited to a few policy pages).
- **Pipeline:** parse, chunk, metadata (`tenant_id`, `document_type`, `section`, `effective_date`, `customer_id`), embed, pgvector search with tenant filter, answer with citation.
- **Safety:** "no relevant policy found" and "policy conflict" responses are first-class outputs. Retrieved text is untrusted input.

### 6.3 Memory

| Type | What it stores | How it is used |
|---|---|---|
| **Customer memory** (long term) | Collector notes, promises to pay and whether they were kept, past recommendations and whether they were approved or rejected, preferred contact channel, dispute status | Fetched by `get_customer_history`; notes are also embedded so the agent can answer "what did we agree last time?". Written only by humans or by rules |
| **Conversation memory** (short term) | Chat threads per user and customer (`conversations`, `messages`) | Last N turns, and optionally a running summary labeled AI-generated, injected into the agent so follow-ups work ("draft it softer", "what about the other invoice?"). Never a source of facts; nothing moves into customer memory unless a human saves it |

Rejections and edits are stored, so the agent can see that a previous recommendation was rejected and why.

---

## 7. Architecture

```text
Next.js / React (Dashboard, Queue, Customer Profile, AI panel)
                      |
                   FastAPI  (auth, RBAC, tenant scoping, audit)
                      |
     +----------------+------------------+
     |                |                  |
 Receivables      Agent Orchestrator   Import / Jobs
 Engine           (LLM + tool calling)
 (risk, priority,      |
  forecast,     +------+--------+
  policy rules) |      |        |
     |       Policy   Memory   Draft
     |       RAG      Store    Generator
     |          |      |
     +------ PostgreSQL + pgvector ------+
                                         |
                              Audit log / Agent runs
```

Every table carries `tenant_id`. Every agent run, recommendation, approval, and task creation is written to `agent_runs` and `audit_logs`, whether or not it is approved.

---

## 8. Data Model (slim)

`tenants`, `users` (each with a role), `customers`, `invoices`, `payments`, `promises_to_pay`, `collection_tasks`, `documents`, `document_chunks` (embedding), `risk_scores`, `recommendations`, `conversations`, `messages`, `customer_notes`, `agent_runs`, `audit_logs`.

Added by the reconciliation and consolidation decisions: `policy_rules` (structured rules with source document and section, D21), `tenant_settings` (weights, thresholds, grace periods, escalation triggers, reminder cap, tone defaults, D22), `draft_versions` (original and edited text with the reason, D23), and the invoice status `disputed`.

Points that matter for correctness (field-level detail is in the PRD):
- `customers` carries `tier` (strategic / regular), `sales_rep`, and `assigned_collector` (what makes "assigned only" enforceable, D30).
- `payments` is the source of truth for what has been paid. An invoice's paid amount is derived from it; any stored copy is a cache that the engine recomputes and tests.
- The embedding of a collector note is a column on `customer_notes` (D16). `document_chunks` holds policy and contract passages.
- Cheque tracking is deferred to the roadmap until validated.

Key additions versus the PRD: `recommendations` (status: pending / approved / edited / rejected), `conversations` + `messages` (conversation memory), `customer_notes` (customer memory), `document_chunks` (RAG).

---

## 9. Tech Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js / React + TypeScript |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Database | PostgreSQL + pgvector |
| AI | LLM access through OpenRouter behind our own `LLMClient` interface; a plain tool-calling loop (D12, D13); a multilingual embedding model (D16) |
| Infra | Docker Compose |
| Tests | pytest for risk, priority, overdue, forecast, and tenant isolation; evaluation sets for agent, RAG, recommendations, and safety, plus the ablation |

---

## 10. Mapping to the Grading Rubric

| Criterion | Weight | What we show |
|---|---:|---|
| System Architecture | 20% | Layered diagram, deterministic engine vs LLM boundary, multi-tenancy, audit trail, documented decisions |
| UI & Dashboard | 15% | Executive dashboard, ranked queue, customer profile with AI recommendation panel and approve/edit/reject |
| RAG & Memory | 15% | Cited policy retrieval, conversation memory, customer memory with a write rule, "no policy found" behavior, small RAG eval |
| Code Quality | 15% | Clean module layout, typed Pydantic schemas, tests on core calculations, README, `.env.example`, no secrets |
| Real-World Value | 10% | Measurable KPIs (days beyond terms, overdue, collector time), Egyptian distributor workflow, Arabic drafts with tone options |
| Presentation | 15% | Demo flow in section 4, recorded video, slide PDF |
| Team Collaboration | 10% | Roles table, GitHub history, issues/PRs (reflect what actually happened) |

---

## 11. Success Criteria (demo checklist)

Items marked (S) belong to the Should tier; the rest are Core.

- [ ] CSV import works with validation and preview
- [ ] Overdue and outstanding calculations are tested
- [ ] Every risk score shows its factors
- [ ] Queue is ranked and each row has a suggested action
- [ ] Policy answers carry a citation; missing policy is stated honestly; conflicting policies are flagged
- [ ] A Collector can record a note and a promise, and the agent uses them next time
- [ ] Follow-up chat question works through conversation memory
- [ ] Agent answer uses customer memory (notes and past promises)
- [ ] Arabic draft generated with tone choice
- [ ] Nothing executes without approval, and a test proves the API rejects it
- [ ] Task and audit entries are created, including for recommendations that are rejected
- [ ] Tenant A cannot read tenant B data (test exists); a Collector sees only assigned customers
- [ ] Basic eval and ablation results are reported, including weaknesses
- [ ] (S) Forecast shows range and confidence, never "guaranteed"
- [ ] (S) Health Report appears after the first upload
- [ ] (S) The UI works in Arabic (RTL) and English with a language toggle
- [ ] (S) A disputed invoice leaves the queue and pauses follow-up; the reminder cap needs a manager override

---

## 12. Decisions and Roadmap

**Decisions** are in `Tahseel_AI_Decision_Log.md`. The ones that shape this file: OpenRouter behind `LLMClient` (D12), plain tool-calling loop (D13), full Arabic and English UI (D14), three roles (D15), collector notes embedded (D16), production-minded delivery (D17), two-layer policy (D21), canonical schema and tenant configuration (D22), lite guardrails (D23), memory rule (D28), tiers (D29), scoring (D34), actions (D36).

**Roadmap** (the single list; nothing here is promised or validated):
- Odoo and ETA adapters
- Sales approval step (a Sales Manager role)
- Extracting policy rules from documents with LLM help, then human confirmation
- WhatsApp Business draft-to-send with approval
- Risk re-calibration from outcomes (needs real data)
- Send-time pattern learning
- OCR receipt reconciliation
- A field-collector app
- Cheque tracking (validate first; sources conflict on how common cheques are)
- Credit-limit and working-capital analytics (validate first)
- A trained ML risk model, once real data exists