# Tahseel AI — Technical Strength

**Purpose:** Why the technical design is strong, what we build to prove it, and what we honestly do not claim.
**Status:** Design document, consolidated 31 October 2026. It describes the plan. Nothing here is claimed as built or measured until the README, the slides, or the evaluation results say so.
**Companions:** `Tahseel_AI_Decision_Log.md` (decisions), `Tahseel_AI_Final_Concept.md` (scope), `Tahseel_AI_PRD.md` (formulas, fields, API), `Tahseel_AI_Business_Strength.md` (market and value).

---

## 1. Technical Thesis

> **Trust by construction.** Every number comes from tested code. Every policy statement comes from a cited document or a rule with a source. Every customer memory comes from a human-authored or rule-derived event. Every consequential action waits for a human.

A finance team will not adopt a copilot it cannot verify. So the design goal is not "the smartest AI", it is **the most checkable AI**. Every technical choice below serves that goal.

---

## 2. Pipeline vs Agent (what is agentic and what is not)

| Work | Mode | Why |
|---|---|---|
| Outstanding, days overdue, risk score, priority score, forecast for all customers | **Batch pipeline, no LLM** | Deterministic, cheap, unit-testable, reproducible |
| Policy rules (thresholds, grace periods, escalation triggers) evaluated per customer | **Batch pipeline, no LLM** | Hard thresholds must not depend on semantic search (D21) |
| Collection Queue with a rule-based suggested action (thresholds from config) | **Batch pipeline** | Same input gives the same output; no LLM cost per page load |
| Explain a customer, answer open questions, investigate ("why did this risk rise?", "which overdue accounts are above EGP 100K?") | **Agent** (LLM selects tools, multi-step) | Open-ended; needs tool selection and combination |
| Retrieve policy passages and cite them | Agent tool | Grounding |
| Read customer memory | Agent tool (read only) | Context |
| Draft a message in a chosen tone | Agent tool | Language task |
| Create a task | Agent tool, **blocked until human approval** | Consequential |
| Write an audit entry | **Always**, for every recommendation, approval, edit, rejection, and tool call | Traceability; it does not wait for approval |
| Record a note, a call result, or a promise | **A human**, through the UI and API | The agent never writes customer memory (D28) |

**Claim we make:** the system is agentic where open-ended reasoning is needed and deterministic where correctness is needed. We do not call a fixed pipeline an agent.

The queue shows a rule-based **suggested action**. The agent's **recommendation** can differ when memory or retrieved passages add context. The UI shows both and says why (D36).

---

## 3. Technical Differentiators (ranked by value to the rubric)

| # | Differentiator | How we prove it |
|---|---|---|
| T1 | **Tool-grounded numeric integrity.** The LLM never calculates; it calls tools and quotes their output. | Ablation: LLM-only on raw CSV vs tool-grounded; count wrong or fabricated numbers |
| T2 | **Explainable risk and priority.** Every score lists its factors and points. | UI shows the factor list; unit tests assert the factor points add up to the score |
| T3 | **Policy RAG with citations and honest refusal.** Cites document and section; says "no relevant policy found" or "policies conflict" when true. | RAG eval set includes missing-policy and conflicting-policy cases |
| T4 | **Memory with write rules and decision impact.** Memory changes what the agent recommends and is visible in the UI. | Scenario tests: a broken promise changes tone; a rejected recommendation is surfaced next time |
| T5 | **Human approval and audit by design.** Approval is enforced at the API, not only the UI. | Test: the execute endpoint rejects any recommendation without approved status |
| T6 | **Tenant isolation and injection-aware retrieval.** The tenant filter is part of the vector query; retrieved text is treated as data. | Cross-tenant test; prompt-injection test documents |
| T7 | **AI-assisted import.** The LLM proposes the column mapping from the headers and a few masked sample rows; the user confirms before import. | Mapping accuracy on messy sample files |
| T8 | **Operational guardrails.** A human-set dispute status pauses follow-up; a reminder frequency cap; a rule-based draft check. | Tests: a disputed invoice leaves the ranked queue, appears in the Disputed list, and alerts the manager; the cap requires a manager override for the extra draft; drafts with legal-threat phrases are flagged |

---

## 4. Memory Design

Two kinds of memory (D28).

### Customer memory (long term)

| Memory | Written by | Used for | How it changes decisions |
|---|---|---|---|
| Customer notes and call outcomes | Collector (or a manager) | Context and semantic recall ("what did we agree last time?") | The agent cites the note; it is shown in the UI |
| Promises and their outcomes | A human records the promise; the system marks it kept or broken from payments by rule | Risk factor and message tone | A broken promise adds risk points and escalates the tone |
| Recommendation outcomes | The approver (approve, edit, reject, with a reason); the original and edited draft text are stored | Showing past decisions to approvers | A rejected recommendation with a reason is surfaced next time; the approval rate is a KPI |
| Contact preferences (channel, contact person) | Collector | Message drafting and the suggested action | The draft uses the preferred channel and contact |
| Dispute status | A human (D23) | Pausing follow-up | The invoice leaves the ranked queue and the manager is alerted |

**Write rules**
1. Only human-authored or rule-derived events are stored as customer memory. No LLM-inferred fact is ever stored there.
2. Every entry has author, timestamp, and source.
3. Memory is tenant-scoped. A Finance Manager or Owner can edit or delete an entry; deletion is a soft delete written to the audit log.
4. The UI shows which memories were used ("Used: note by Ahmed, 12 Oct").
5. Memory text is untrusted input to the LLM (see T6).
6. The agent has no tool that writes customer memory.

### Conversation memory (short term)

| Memory | Written by | Used for | Rules |
|---|---|---|---|
| Chat turns of a thread | The system (messages) | Follow-up questions in the same thread | The last N turns are injected into the agent. A running summary written by the LLM is allowed, stored with `is_summary` and labeled AI-generated. It is context, never a source of facts, and nothing moves into customer memory unless a human saves it |

---

## 5. Evaluation Plan (the strongest technical claim)

Two tiers (D29). The **basic** tier is in Core and is never cut. The **full** tier is a stretch. Targets are goals, not results. We report actual results in the README and slides, including failures.

| Eval | Basic (never cut) | Full (stretch) | What it measures | Goal |
|---|---|---|---|---|
| **Agent eval** | ~15 cases | ~40 cases | Correct customer resolution, correct tool selection, numeric fidelity (every number in the answer matches a tool output), "I don't have enough data" when data is missing | No fabricated number in the eval set; tool selection of at least 90% |
| **RAG eval** | ~10 queries, including no-policy and conflicting-policy cases | ~30 queries over ~20 policy documents | Retrieval recall@k, citation accuracy, groundedness, correct "no policy found" and "conflict" behavior (documents include deliberately conflicting sections) | Citation accuracy of at least 90% |
| **Recommendation eval** | n/a | ~30 labeled customers | Agreement with a rule-based baseline; blind usefulness rating by team members | Report agreement and ratings honestly |
| **Safety tests** | ~5 tests | ~10 tests | A prompt injection in a policy or note must not trigger actions; cross-tenant retrieval returns nothing; no external send without approval; PII minimized in prompts | All pass |
| **Ablation (headline slide)** | Same questions, two setups | Same | (a) LLM with raw CSV pasted vs (b) tool-grounded system: numeric error rate | Show the measured gap, whatever it is |

---

## 6. What We Claim and What We Do Not (validation honesty)

These are the claims we will make **once the work is built and measured**. Until then they are the plan.

| Topic | We claim | We do not claim |
|---|---|---|
| Data | Pipeline correctness and rule behavior on synthetic data with realistic patterns | Predictive accuracy on real distributors |
| Risk score | Explainable, rule-based, configurable weights | A trained ML model |
| Forecast | Expected cash with a range and a confidence label; a time-split backtest harness on synthetic data is planned (S1) | Guaranteed cash; accuracy proven on real data |
| Arabic drafts | Tone options; review by native speakers on the team is planned | Validated by real collectors |
| Policies | Structured rules evaluated by code, plus retrieved and cited document passages | Legal or credit-decision authority |
| Hallucination | Numeric hallucination is reduced by construction and measured in the ablation | That hallucination is eliminated |
| Learning | The system stores human decisions (approvals, edits, rejections) as context | Model retraining, automatic recalibration, or "the AI learns" |
| Business impact | The product is designed to shorten lateness and reduce forgetting (a hypothesis, see the business file) | Measured impact on real receivables |
| Security and privacy | Tenant isolation, TLS in transit, encryption at rest as a deployment setting, minimal personal data in prompts, synthetic data only in the demo | End-to-end encryption, or absolute promises about how third-party model providers handle data |

---

## 7. Key Architecture Decisions (ADR-style)

| ID | Decision | Reason | Trade-off |
|---|---|---|---|
| ADR-1 | Deterministic engine separate from the LLM | Correctness and testability | Less "magic" in the demo |
| ADR-2 | pgvector in the same PostgreSQL | One datastore, tenant filter in the same query, less infrastructure | Less scalable than a dedicated vector DB |
| ADR-3 | One orchestrator with grouped tools | Simpler to build, test, defend | Fewer "agents" to point at |
| ADR-4 | Approval enforced at the API | UI bugs cannot bypass it | More backend code |
| ADR-5 | Append-only audit log of recommendations, approvals, edits, rejections, tool calls, and memory edits. The application's database role has no update or delete permission on it | Traceability | Storage growth |
| ADR-6 | Multilingual embedding model | Policies and notes may be Arabic or mixed | Must test Arabic retrieval quality |
| ADR-7 | Two-layer policy: structured rules evaluated by the deterministic engine, plus document RAG for explanation and citation (D21) | Hard thresholds must not depend on semantic search; users still need readable, cited explanations | In the MVP rules are entered manually or seeded, then confirmed by a human; extracting them with an LLM is roadmap |
| ADR-8 | Canonical data schema with an adapter interface; tenant configuration instead of hard-coded thresholds (D22) | Adaptability across sectors without code changes | One more abstraction to maintain; only one adapter is built in the MVP |
| ADR-9 | LLM access through OpenRouter behind our own `LLMClient`, with per-task model config, timeouts, retries, a fallback model, and per-run token and cost logging (D12) | Switch models freely, compare cost and quality, limit spend | Tool-calling and structured-output support varies by model, so each model needs testing |
| ADR-10 | A plain tool-calling loop in the OpenAI tool-schema style (D13) | Fewer dependencies; every tool call can be logged and gated | We write the loop ourselves |
| ADR-11 | Tenant isolation through one tenant-scoped data-access layer, plus the tenant filter inside every vector query, proven by a cross-tenant test. Database row-level security is a possible later hardening | Isolation that does not depend on every developer remembering a filter | Slightly more code than ad hoc queries |
| ADR-12 | Customer memory is written only by humans and rules; conversation memory is context only (D28) | Keeps the trust thesis while keeping follow-up questions | Two memory paths to explain and test |

---

## 8. Security and Trust

The controls that let a finance team trust the system with sensitive data. This section is the home of the approved content from the earlier trust and challenges notes (D31).

- **Tenant isolation.** `tenant_id` on every table. All reads and writes go through a tenant-scoped layer. The tenant filter is part of the vector query itself. A cross-tenant test is required (ADR-11).
- **Access control.** Three roles enforced on the server: Owner, Finance Manager, Collector. A Collector sees only assigned customers. The permission matrix is in the Decision Log (D15, D30).
- **Numbers and language are separate.** Calculations run in deterministic Python code. The LLM explains, retrieves, and drafts; it never calculates. A post-check confirms that every number in an answer appears in a tool result.
- **Audit.** Append-only log of every recommendation, approval, edit, rejection, tool call, and memory edit or deletion (ADR-5).
- **Data in transit and at rest.** TLS in transit. Encryption at rest is a deployment setting. Passwords are hashed, secrets stay outside the repository, and the database user has least privilege.
- **Third-party model providers.** LLM calls go through a gateway to third-party providers. We minimize personal data in prompts. The demo uses synthetic data only. Before real data is used, we restrict the providers and review their retention settings. We make no absolute promise about provider behavior (D12, D27).
- **Untrusted text.** Retrieved passages, notes, and uploaded documents are data, not instructions. No tool runs because a document says so, and nothing executes without approval.
- **Guardrails.** Dispute status set by a human pauses follow-up and alerts the manager. A configurable reminder cap needs a manager override beyond the cap. A rule-based check flags drafts with legal threats or forbidden phrases (T8, D23).

---

## 9. Mapping to the Rubric (technical criteria)

| Criterion | Weight | Evidence we show |
|---|---:|---|
| System Architecture | 20% | Layered diagram, pipeline vs agent split, ADR table, tenant isolation, audit |
| RAG & Memory | 15% | Cited retrieval, refusal behavior, memory tables with write rules, RAG eval results |
| Code Quality | 15% | Modular layout, typed schemas, tests on risk, priority, overdue, forecast, and tenant isolation, README, `.env.example`, no secrets |
| UI & Dashboard | 15% | Queue, customer profile, AI panel showing reasons, policy citation, used memories, approve/edit/reject |

---

## 10. Build Priority (highest score per hour)

The order follows the tiers: Core first, then Should, then Delivery (D29). The cut order is in the Decision Log, section E.

1. Repo skeleton and the delivery basics: Docker Compose, environment config, CI running lint and tests
2. Data model, migrations, authentication, tenant scoping, and the three roles, with the cross-tenant test
3. Receivables engine plus unit tests
4. Synthetic data generator (reliable, late, chronic, partial, broken-promise, disputed, and strategic patterns)
5. CSV import plus the instant Receivables Health Report
6. Risk and priority with factor lists, and the suggested-action rules
7. Queue and Customer Profile UI, with the string-dictionary structure for Arabic and English from day one, and the forms to record notes, call results, and promises
8. Policy RAG with citations and refusal behavior, plus `policy_rules` and `tenant_settings`
9. Agent tools, approval gate, and audit log
10. Memory: conversation memory and note recall
11. Basic eval and ablation (do not leave this to the last day)
12. Should tier in the cut order: relationship-aware recommendations, lite guardrails, forecast, bilingual polish
13. README, diagrams, deployment, demo video (Delivery tier)

---

## 11. Technical Risks

| Risk | Mitigation |
|---|---|
| Arabic retrieval quality is weak | Multilingual embeddings; test with Arabic and mixed queries; keep policy chunks small and titled |
| LLM ignores tool outputs or invents numbers | Structured tool outputs; post-check that every number in the answer appears in tool results |
| Prompt injection through notes or documents | Treat retrieved text as data; strip instructions; no tool can execute without approval |
| Scope creep | Follow the tiers and the cut order in the Decision Log |
| Messy Excel formats | LLM-assisted mapping from headers and masked samples, plus validation, plus preview |
| Sample rows sent to a third-party model during import | Send headers and masked samples only; synthetic data in the demo |
| Synthetic data too clean | Inject noise: missing fields, duplicates, partial payments, format errors |
| The eval grows too large to finish | Do the basic tier first and report it honestly; the full tier is a stretch |

---

## 12. Technical Decisions

**Resolved** (see `Tahseel_AI_Decision_Log.md`): OpenRouter behind an `LLMClient` interface with per-task model config, fallback, and cost logging (D12); plain tool-calling loop (D13); full Arabic and English UI (D14); three roles (D15); collector notes embedded (D16); production-minded delivery (D17); two-layer policy (D21); canonical schema and tenant configuration (D22); lite guardrails (D23); memory rule (D28); tiers (D29); scoring (D34); actions (D36).

**Still open:** the exact OpenRouter models (after tool-calling and Arabic tests) and the exact embedding model (after an Arabic retrieval test).