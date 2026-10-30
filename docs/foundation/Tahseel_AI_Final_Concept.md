# Tahseel AI — Final Concept (Capstone Scope)

**Tahseel — تحصيل — means "collection".**
**Status:** Draft for agreement. Once agreed, this file is the single source of truth for the documentation PDF, the code, and the presentation.
**Submission:** LMS, due Sat 31 Oct 2026, 12:00 AM (DEPI GradProject).

---

## 1. One-Liner

**Spoken:** "Every morning, Tahseel tells a distributor's collection team which customers to chase, why, and exactly what to say."

**Documentation:** "Tahseel helps Egyptian distributors collect overdue invoices faster by telling the finance team who to call today, why, and what to say, based on payment history and the company's own credit policy."

Technical framing (architecture section only): an agentic credit-control copilot, with deterministic numbers, cited policy RAG, memory, and human approval. See `Tahseel_AI_Technical_Strength.md` and `Tahseel_AI_Business_Strength.md`.

---

## 2. Problem and User

- **Problem:** Distributors sell on credit. The data (invoices, payments, promises, notes) exists in Excel, ERP exports, WhatsApp, and people's heads, but nobody turns it into a clear daily collection decision.
- **Primary user:** Collection Officer (daily queue, customer context, message drafts).
- **Secondary users:** Finance Manager (approvals, risk and cash visibility), Owner/CFO (summary).
- **Value, measurable:** lower overdue receivables, lower DSO, less time spent sorting spreadsheets, clearer 7/30-day cash expectations.

---

## 3. What We Build (and What We Don't)

### Must have (the demo flow depends on these)

| # | Capability |
|---|---|
| 1 | CSV/Excel import with column mapping, validation, preview |
| 2 | Receivables engine: outstanding, days overdue, per-customer aggregates |
| 3 | Explainable rule-based risk score (0-100) with human-readable factors |
| 4 | Collection priority score and ranked Collection Queue |
| 5 | Policy RAG with citations (credit policy, collection policy, templates) |
| 6 | **Memory** (see section 6): conversation memory + customer memory |
| 7 | Agent with tool calling: answers questions about a customer, recommends next action |
| 8 | Message draft generator (Arabic, selectable tone) |
| 9 | Human approval gate (Approve / Edit / Reject) |
| 10 | Task creation and audit log |
| 11 | Dashboard: 3 screens (Executive, Queue, Customer Profile with AI panel) |
| 12 | Simple 7/30-day cash forecast with stated confidence |
| 13 | **Relationship-aware recommendations:** sales rep note and customer tier are inputs; for strategic accounts the recommendation is "talk to the sales rep first" |
| 14 | **Instant Receivables Health Report** on first upload (aging, risk distribution, top 20 accounts to chase, expected cash) |
| 15 | **Full Arabic (RTL) and full English UI** with a language toggle |
| 16 | **Production practices:** Docker Compose, HTTPS, CI, migrations, logging, per-run LLM cost logging |

### Simplified for the capstone

| PRD version | Capstone version | Why |
|---|---|---|
| 5 separate agents | **One orchestrator with grouped tools** (risk, receivables, policy, forecast, history, drafting, tasks) | Easier to build, test, and defend |
| Hybrid retrieval + reranking | Vector search (pgvector) + metadata filters + citation | Reranking is an optional upgrade |
| 5 RBAC roles | 3 roles: Owner, Finance Manager, Collector | Enough to show permissions and approval flow |
| Celery + Redis | FastAPI background tasks | Less infrastructure |
| 500 customers / 5,000 invoices | ~120 customers / ~1,500 invoices, synthetic | Enough patterns, fast to generate and demo |
| Cloud deployment + HTTPS | Docker Compose, HTTPS reverse proxy, CI, deployed after the core slice works; recorded demo as fallback | Production-mindedness lifts Architecture, Code Quality, and Real-World Value (see Decision Log D17) |

### Out of scope (explicit non-goals)

Payments, wallets, automatic credit blocking, automatic WhatsApp or email sending, legal advice, ERP/CRM integrations, ML risk model, credit-limit recommendations.

---

## 4. Core Demo Flow

```text
1. Upload receivables CSV
2. Dashboard shows total / overdue / high-risk exposure / expected cash
3. Collection Queue ranks customers (risk + priority + recommended action)
4. Open a customer: invoices, payments, promises, risk explanation
5. Ask the agent: "What should we do with this customer?"
6. Agent calls tools, retrieves the relevant policy, reads customer memory
7. Agent returns recommendation + reasons + policy citation
8. Generate Arabic message draft (choose tone)
9. Collector/Finance Manager edits and approves
10. Task is created, event is written to the audit log
11. Follow-up question in the same chat uses conversation memory
```

---

## 5. Key Design Decisions

1. **Numbers come from code, not from the LLM.** Outstanding, overdue days, risk score, priority, and forecast are computed deterministically and tested. The LLM only explains, retrieves policy, drafts, and answers questions by calling those tools. This prevents invented financial facts.
2. **Explainable risk, no fake ML.** Weighted rules (days overdue 25%, historical delay 20%, broken promises 20%, exposure 20%, recent behavior 15%). Every score lists its factors.
3. **Priority is separate from risk.** Priority = normalized(Risk x Exposure x Urgency x Collection Probability). Factors are shown.
4. **Human-in-the-loop everywhere it matters.** The AI recommends and drafts. It never sends, blocks, or changes financial records.
5. **Never invent policy.** If no relevant policy is retrieved, say so. If policies conflict, flag for human review.
6. **Forecast is expected cash, not guaranteed cash.** Each invoice contributes `outstanding x probability of payment in the window`, where the probability comes from that customer's historical behavior. Promises are weighted by the customer's promise-keep rate. Output includes a low/expected/high range and a confidence label.
7. **Data honesty.** The demo uses synthetic data, generated with realistic patterns (reliable payers, chronic late payers, partial payments, broken promises, seasonality). We do not claim real pilot customers unless we actually have them.

---

## 6. AI Layer

### 6.1 Agent tools

| Tool | Purpose |
|---|---|
| `get_receivables(customer_id)` | Outstanding, overdue, max days overdue |
| `get_customer_history(customer_id)` | Invoices, payments, promises, collector notes |
| `calculate_risk(customer_id)` | Score, level, factors |
| `calculate_priority(customer_id)` | Priority score and factors |
| `retrieve_policy(query, customer_id?)` | Policy chunks with citation |
| `forecast_cash(window_days)` | Expected cash with range and confidence |
| `draft_message(customer_id, tone)` | Arabic draft using data + policy context |
| `create_task(...)` | Only after human approval |

### 6.2 RAG

- **Sources:** credit policy, collection policy, payment terms, approved message templates, customer contracts (synthetic), and collector notes (so RAG is not limited to a few policy pages).
- **Pipeline:** parse, chunk, metadata (`tenant_id`, `document_type`, `section`, `effective_date`, `customer_id`), embed, pgvector search with tenant filter, answer with citation.
- **Safety:** "no relevant policy found" and "policy conflict" responses are first-class outputs.

### 6.3 Memory

| Type | What it stores | How it is used |
|---|---|---|
| **Conversation memory** | Chat threads per user and customer (`conversations`, `messages`) | Last N turns injected into the agent so follow-ups work ("draft it softer", "what about the other invoice?") |
| **Customer memory** | Collector notes, promises to pay and whether they were kept, past recommendations and whether they were approved or rejected, preferred contact channel | Fetched by `get_customer_history`; notes are also embedded so the agent can answer "what did we agree last time?" |

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
  forecast)     +------+--------+
     |          |      |        |
     |       Policy   Memory   Draft
     |       RAG      Store    Generator
     |          |      |
     +------ PostgreSQL + pgvector ------+
                                         |
                              Audit log / Agent runs
```

Every table carries `tenant_id`. Every agent run, recommendation, approval, and task creation is written to `agent_runs` and `audit_logs`.

---

## 8. Data Model (slim)

`tenants`, `users`, `customers`, `invoices`, `payments`, `promises_to_pay`, `collection_tasks`, `documents`, `document_chunks` (embedding), `risk_scores`, `recommendations`, `conversations`, `messages`, `customer_notes`, `agent_runs`, `audit_logs`.

`customers` also carries `tier` (strategic / regular) and `sales_rep`, used by relationship-aware recommendations. Cheque tracking is deferred to the roadmap until validated.

Key additions versus the PRD: `recommendations` (status: pending / approved / edited / rejected), `conversations` + `messages` (conversation memory), `customer_notes` (customer memory), `document_chunks` (RAG).

---

## 9. Tech Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js / React + TypeScript |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Database | PostgreSQL + pgvector |
| AI | LLM API with tool calling; embeddings; orchestration with plain tool-calling loop or LangGraph |
| Infra | Docker Compose |
| Tests | pytest for risk, priority, overdue, forecast, tenant isolation; small eval set for agent and RAG |

---

## 10. Mapping to the Grading Rubric

| Criterion | Weight | What we show |
|---|---:|---|
| System Architecture | 20% | Layered diagram, deterministic engine vs LLM boundary, multi-tenancy, audit trail, documented decisions |
| UI & Dashboard | 15% | Executive dashboard, ranked queue, customer profile with AI recommendation panel and approve/edit/reject |
| RAG & Memory | 15% | Cited policy retrieval, conversation memory, customer memory, "no policy found" behavior, small RAG eval |
| Code Quality | 15% | Clean module layout, typed Pydantic schemas, tests on core calculations, README, `.env.example`, no secrets |
| Real-World Value | 10% | Measurable KPIs (overdue, DSO, collector time), Egyptian distributor workflow, Arabic drafts with tone options |
| Presentation | 15% | Demo flow in section 4, recorded video, slide PDF |
| Team Collaboration | 10% | Roles table, GitHub history, issues/PRs (reflect what actually happened) |

---

## 11. Success Criteria (demo checklist)

- [ ] CSV import works with validation and preview
- [ ] Overdue and outstanding calculations are tested
- [ ] Every risk score shows its factors
- [ ] Queue is ranked and each row has a recommended action
- [ ] Policy answers carry a citation; missing policy is stated honestly
- [ ] Follow-up chat question works through conversation memory
- [ ] Agent answer uses customer memory (notes and past promises)
- [ ] Arabic draft generated with tone choice
- [ ] Nothing executes without approval
- [ ] Task and audit entries are created
- [ ] Forecast shows range and confidence, never "guaranteed"
- [ ] Tenant A cannot read tenant B data (test exists)

---

## 12. Decisions

**Resolved** (details in `Tahseel_AI_Decision_Log.md`, section C): OpenRouter as the LLM gateway behind our own `LLMClient`; plain tool-calling loop; full Arabic (RTL) and English UI; three roles (Owner, Finance Manager, Collector); collector notes embedded in pgvector; production-minded delivery with HTTPS deployment and a recorded demo as fallback.

### Original open questions (superseded)

1. **UI language:** English UI with Arabic message drafts, or full Arabic/RTL UI? **English UI, Arabic drafts.**
2. **Roles:** **3 roles (Owner, Finance Manager, Collector)** or a single admin role to save time?
3. **LLM provider and model:** which API key do we have available for the demo?
4. **Orchestration:** **plain tool-calling loop** (fewer dependencies) or LangGraph (looks more "agentic" in the docs)?
5. **Customer memory embeddings:** **embed collector notes in pgvector** or keep notes as plain recent-N retrieval?
6. **Deployment:** **recorded local demo** or also a public deployment if time allows?
