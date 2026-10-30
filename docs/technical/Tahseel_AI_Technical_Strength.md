# Tahseel AI — Technical Strength

**Purpose:** Why the technical design is strong, what we build to prove it, and what we honestly do not claim.
**Companions:** `Tahseel_AI_Final_Concept.md` (scope) and `Tahseel_AI_Business_Strength.md` (market and value).

---

## 1. Technical Thesis

> **Trust by construction.** Every number comes from tested code. Every policy statement comes from a cited document. Every memory comes from a human-confirmed event. Every consequential action waits for a human.

A finance team will not adopt a copilot it cannot verify. So the design goal is not "the smartest AI", it is **the most checkable AI**. Every technical choice below serves that goal.

---

## 2. Pipeline vs Agent (what is agentic and what is not)

| Work | Mode | Why |
|---|---|---|
| Outstanding, days overdue, risk score, priority score, forecast for all customers | **Batch pipeline, no LLM** | Deterministic, cheap, unit-testable, reproducible |
| Daily Collection Queue with a rule-based suggested action (thresholds from config) | **Batch pipeline** | Same input gives the same output; no LLM cost per page load |
| Explain a customer, answer open questions, investigate ("why did this risk rise?", "which overdue accounts are above EGP 100K?") | **Agent** (LLM selects tools, multi-step) | Open-ended; needs tool selection and combination |
| Retrieve policy and cite it | Agent tool | Grounding |
| Read customer memory | Agent tool | Context |
| Draft a message in a chosen tone | Agent tool | Language task |
| Create task, write audit | Agent tool, **blocked until human approval** | Consequential |

**Claim we make:** the system is agentic where open-ended reasoning is needed and deterministic where correctness is needed. We do not call a fixed pipeline an agent.

---

## 3. Technical Differentiators (ranked by value to the rubric)

| # | Differentiator | How we prove it |
|---|---|---|
| D1 | **Tool-grounded numeric integrity.** The LLM never calculates; it calls tools and quotes their output. | Ablation: LLM-only on raw CSV vs tool-grounded; count wrong or fabricated numbers |
| D2 | **Explainable risk and priority.** Every score lists its factors and points. | UI shows factor list; unit tests assert factor sums equal the score |
| D3 | **Policy RAG with citations and honest refusal.** Cites document and section; says "no relevant policy found" or "policies conflict" when true. | RAG eval set includes missing-policy and conflicting-policy cases |
| D4 | **Memory with write rules and decision impact.** Memory changes what the agent recommends and is visible in the UI. | Scenario tests: broken promise changes tone; rejected recommendation is surfaced next time |
| D5 | **Human approval and audit by design.** Approval is enforced at the API, not only the UI. | Test: execute endpoint rejects any recommendation without approved status |
| D6 | **Tenant isolation and injection-aware retrieval.** Tenant filter is part of the vector query; retrieved text is treated as data. | Cross-tenant test; prompt-injection test documents |
| D7 | **AI-assisted import.** LLM proposes column mapping; user confirms before import. | Mapping accuracy on messy sample files |

---

## 4. Memory Design

| Memory | Written by | Confirmed by | Used for | How it changes decisions |
|---|---|---|---|---|
| Conversation memory | System (messages) | n/a | Follow-ups in the same thread | Last N turns plus a running summary injected into the agent |
| Customer notes | Collector | The author | Context and semantic recall ("what did we agree last time?") | Agent cites the note; shown in UI |
| Promise outcomes | Collector records the promise; system marks kept or broken from payments | Rule plus collector | Risk factor and message tone | Broken promise adds risk points and escalates tone |
| Recommendation outcomes | Approver (approve, edit, reject, with reason) | Human decision | Calibration | A rejected recommendation with a reason is surfaced next time; approval rate is a KPI |
| Contact preferences (channel, contact person) | Collector | The author | Message drafting | Draft uses preferred channel and contact |

**Write rules**
1. No LLM-inferred facts are stored as memory. Only human-authored or rule-derived events.
2. Every memory has author, timestamp, and source.
3. Memory is tenant-scoped and editable or deletable by the Finance Manager.
4. The UI shows which memories were used ("Used: note by Ahmed, 12 Oct").
5. Memory text is untrusted input to the LLM (see D6).

---

## 5. Evaluation Plan (the strongest technical claim)

Targets are goals to aim for, not results. We report actual results in the README and slides, including failures.

| Eval | Size | What it measures | Target |
|---|---|---|---|
| **Agent eval** | ~40 cases | Correct customer resolution, correct tool selection, numeric fidelity (every number in the answer matches a tool output), "I don't have enough data" when data is missing | 0 fabricated numbers; tool selection >= 90% |
| **RAG eval** | ~30 queries over ~20 policy docs | Retrieval recall@k, citation accuracy, groundedness, correct "no policy found" and "conflict" behavior (documents include deliberately conflicting sections) | Citation accuracy >= 90% |
| **Recommendation eval** | ~30 labeled customers | Agreement with a rule-based baseline; blind usefulness rating by team members | Report agreement and ratings honestly |
| **Safety tests** | ~10 tests | Prompt injection in a policy or note must not trigger actions; cross-tenant retrieval returns nothing; no external send without approval; PII minimized in prompts | All pass |
| **Ablation (headline slide)** | Same questions, two setups | (a) LLM with raw CSV pasted vs (b) tool-grounded system: numeric error rate | Show the gap |

---

## 6. What We Claim and What We Do Not (validation honesty)

| Topic | We claim | We do not claim |
|---|---|---|
| Data | Pipeline correctness and rule behavior on synthetic data with realistic patterns | Predictive accuracy on real distributors |
| Risk score | Explainable, rule-based, configurable weights | A trained ML model |
| Forecast | Expected cash with a range and a confidence label; backtest harness (time-split) exists | Guaranteed cash; accuracy proven on real data |
| Arabic drafts | Tone options, reviewed by native speakers on the team | Validated by real collectors |
| Policies | Retrieved and cited from provided documents | Legal or credit-decision authority |

The backtest harness runs on synthetic data now and is ready to rerun on real data later.

---

## 7. Key Architecture Decisions (ADR-style)

| ID | Decision | Reason | Trade-off |
|---|---|---|---|
| ADR-1 | Deterministic engine separate from the LLM | Correctness and testability | Less "magic" in the demo |
| ADR-2 | pgvector in the same PostgreSQL | One datastore, tenant filter in the same query, less infrastructure | Less scalable than a dedicated vector DB |
| ADR-3 | One orchestrator with grouped tools | Simpler to build, test, defend | Fewer "agents" to point at |
| ADR-4 | Approval enforced at the API | UI bugs cannot bypass it | More backend code |
| ADR-5 | Append-only audit log of recommendations, approvals, tool calls | Traceability | Storage growth |
| ADR-6 | Multilingual embedding model | Policies and notes may be Arabic or mixed | Must test Arabic retrieval quality |

---

## 8. Mapping to the Rubric (technical criteria)

| Criterion | Weight | Evidence we show |
|---|---:|---|
| System Architecture | 20% | Layered diagram, pipeline vs agent split, ADR table, tenant isolation, audit |
| RAG & Memory | 15% | Cited retrieval, refusal behavior, memory table with write rules, RAG eval results |
| Code Quality | 15% | Modular layout, typed schemas, tests on risk/priority/overdue/forecast/tenant isolation, README, `.env.example`, no secrets |
| UI & Dashboard | 15% | Queue, customer profile, AI panel showing reasons, policy citation, used memories, approve/edit/reject |

---

## 9. Build Priority (highest score per hour)

1. Receivables engine plus unit tests
2. Synthetic data generator (reliable, late, chronic, partial, broken-promise patterns)
3. CSV import plus instant Receivables Health Report
4. Risk and priority with factor lists
5. Queue and Customer Profile UI
6. Policy RAG with citations and refusal behavior
7. Agent tools, approval gate, audit log
8. Memory (conversation, notes, promise and recommendation outcomes)
9. Eval harness and ablation (do not leave to the last day)
10. Forecast (simple, with range)
11. README, diagrams, demo video

---

## 10. Technical Risks

| Risk | Mitigation |
|---|---|
| Arabic retrieval quality is weak | Multilingual embeddings; test with Arabic and mixed queries; keep policy chunks small and titled |
| LLM ignores tool outputs or invents numbers | Structured tool outputs; post-check that every number in the answer appears in tool results |
| Prompt injection through notes or documents | Treat retrieved text as data; strip instructions; no tool can execute without approval |
| Scope creep | Follow the build priority; cut forecast sophistication first |
| Messy Excel formats | LLM-assisted mapping plus validation plus preview |
| Synthetic data too clean | Inject noise: missing fields, duplicates, partial payments, format errors |

---

## 11. Technical Decisions

**Resolved** (see `Tahseel_AI_Decision_Log.md`, section C): OpenRouter behind an `LLMClient` interface with per-task model config, fallback, and cost logging; plain tool-calling loop; multilingual embedding model run locally (to be chosen after an Arabic retrieval test); collector notes embedded; three roles; full Arabic and English UI; production-minded delivery.

**Still open:** the exact OpenRouter models (after tool-calling and Arabic tests) and the exact embedding model.

### Original questions (superseded)

1. LLM provider and model for the demo (and a cheaper model for mapping and drafts?)
2. Plain tool-calling loop vs LangGraph
3. Embedding model with good Arabic support
4. Whether to embed collector notes (recommended) or use recent-N retrieval only
