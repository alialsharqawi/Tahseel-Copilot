# Tahseel AI — Decision Log

**Purpose:** A record of every major fork we faced, what we chose, what we did not choose, and why. It can be turned directly into the "Design Decisions" section of the documentation.

**Final goals every decision serves**
1. **Highest possible score on the capstone rubric:** System Architecture 20%, UI & Dashboard 15%, RAG & Memory 15%, Code Quality 15%, Presentation 15%, Real-World Value 10%, Team Collaboration 10%.
2. **A project that can continue as a product and a service** without claims we cannot prove.

**Origin tags:** `[Ali]` decided by Ali or taken from the PRD. `[Proposed]` proposed by Claude and accepted in discussion. `[Delegated]` Ali asked Claude to decide; Ali can override.

Companions: `Tahseel_AI_Final_Concept.md`, `Tahseel_AI_Technical_Strength.md`, `Tahseel_AI_Business_Strength.md`, `Tahseel_AI_Final_Pitch.md`.

---

## A. Product and Scope

### D1. The problem we solve `[Ali]`
- **Chosen:** Receivables collection and credit control for Egyptian B2B distributors.
- **Not chosen:** invoice generator, generic financial chatbot, autonomous debt collector, payments wallet.
- **Why:** The pain is real, tied to cash, and measurable (DSO, collection rate, collector time). A chatbot or invoice tool has no differentiation. A collector or wallet carries legal and trust risk and sits outside capstone scope.

### D2. Size of the MVP `[Proposed]`
- **Chosen:** A reduced MVP that still runs the full demo flow end to end.
- **Not chosen:** The full PRD (14 features, 5 agents, reranking, Celery, 5 roles, 500 customers and 5,000 invoices).
- **Why:** The rubric rewards architecture, quality, and a working story more than feature count. A smaller product that works beats a larger one that is half broken.

### D3. Human approval `[Ali]`
- **Chosen:** AI recommends and drafts, a human approves, and the rule is enforced at the API.
- **Not chosen:** Automatic sending of WhatsApp or email messages.
- **Why:** Collection messages affect relationships and can have legal weight. Trust matters more than automation at this stage. API-level enforcement means a UI bug cannot bypass it.

### D4. Differentiation bets in the MVP `[Proposed]`
- **Chosen:** Relationship-aware recommendations (sales rep note and customer tier), and an instant Receivables Health Report on first upload.
- **Deferred to roadmap:** Cheque-aware collections.
- **Why:** The first two are cheap to build and help both the demo and future sales. Sources conflict on how common post-dated cheques are, and we cannot verify it now, so we do not build on it yet.

---

## B. AI and Architecture

### D5. Who calculates the numbers `[Proposed]`
- **Chosen:** Hybrid. Deterministic, tested code computes outstanding, overdue days, risk, priority, and forecast. The LLM explains, retrieves policy, drafts, and answers questions by calling tools.
- **Not chosen:** (a) LLM does everything, (b) rules only with no LLM.
- **Why:** (a) risks invented numbers nobody can verify. (b) is not an AI product and forfeits RAG and agent credit. The hybrid gives trust and AI together.

### D6. Pipeline vs agent `[Proposed]`
- **Chosen:** The daily queue is a batch pipeline. The agent handles open-ended investigation, policy-grounded explanations, drafting, and gated task creation.
- **Not chosen:** Everything as an agent, or everything as a pipeline.
- **Why:** The queue must be fast, predictable, and testable. The agent's value is in questions a fixed flow cannot answer. This keeps the word "agentic" honest.

### D7. Number of agents `[Proposed]`
- **Chosen:** One orchestrator with grouped tools.
- **Not chosen:** Five separate agents as in the PRD.
- **Why:** Simpler to build, test, and defend. Most of the five would have been functions with agent names.

### D8. Risk and forecast method `[Ali, from PRD]`
- **Chosen:** Weighted, explainable rules for risk; probability-based forecast with a range and a confidence label.
- **Not chosen:** A trained ML model.
- **Why:** There is no real data to train on, and explainability matters more than accuracy we cannot prove. ML comes when real data exists.

### D9. RAG design `[Proposed]`
- **Chosen:** Vector search in pgvector with metadata filters, citations, honest refusal, and broader sources (policies, contracts, collector notes, message templates).
- **Not chosen:** Hybrid search with reranking, a separate vector database, policies only.
- **Why:** A few pages of policy fit in a prompt, so RAG would have had no justification. Reranking is a later upgrade. pgvector in the same database keeps the tenant filter in one query and reduces infrastructure.
- **Amended by D21 (30 Oct 2026):** hard thresholds and escalation triggers move to structured rules evaluated by code; RAG explains and cites.

### D10. Memory `[Proposed]`
- **Chosen:** Conversation memory plus customer memory (notes, promise outcomes, recommendation outcomes). Only human-authored or rule-derived events are stored.
- **Not chosen:** No memory, conversation memory only, or memory generated by the LLM.
- **Why:** "RAG & Memory" is 15% of the rubric and the PRD had no memory. LLM-generated memory can persist wrong inferences, which breaks the trust thesis.
- **Extended by D23 (30 Oct 2026):** human-set dispute status and original-versus-edited drafts are stored as human-confirmed events.

### D11. Evaluation as a headline strength `[Proposed]`
- **Chosen:** Agent, RAG, recommendation, and safety evals, plus an ablation of LLM-only vs tool-grounded answers.
- **Not chosen:** Showing features only.
- **Why:** The first doubt from reviewers will be "does the AI hallucinate?" A measured answer beats a verbal one. We report real results, including weaknesses.

---

## C. Stack and Delivery (decisions made in the latest round)

### D12. LLM provider: OpenRouter `[Ali]`
- **Chosen:** OpenRouter, so we can switch between models freely.
- **Not chosen:** A single provider's API.
- **Why:** One interface, many models, easy cost and quality comparison, and a fallback option.
- **How we manage the risks**
  - Wrap it behind our own `LLMClient` interface; model IDs per task live in config (a stronger model for the agent, a cheaper one for column mapping and drafts).
  - Tool-calling and structured-output support varies by model. Before pinning a model, test it on tool calls, schema adherence, Arabic quality, latency, and cost.
  - Configure a fallback model, timeouts, and retries.
  - Set a spending limit and log token usage per agent run in `agent_runs`.
  - Demo data is synthetic. Before any real data is used, review the provider data-retention and routing settings.

### D13. Orchestration: plain tool-calling loop `[Delegated]`
- **Chosen:** A thin, hand-written tool-calling loop using the OpenAI-style tool schema, with a clear state diagram in the documentation.
- **Not chosen:** LangGraph.
- **Why:** With OpenRouter and multiple models, the common denominator is OpenAI-style tool calling. A plain loop has fewer dependencies, is easier to test and debug, and lets us log and gate every tool call. The documentation can still present the flow as a state machine. LangGraph can be added later if flows grow.

### D14. UI language: full Arabic (RTL) and full English `[Ali]`
- **Chosen:** Complete bilingual UI with a language toggle.
- **Not chosen:** English UI with Arabic drafts only.
- **Why:** Egyptian finance teams work in Arabic, which strengthens Real-World Value and UI scoring.
- **Implementation rules**
  - All strings in translation dictionaries from day one (for example with `next-intl`); never hard-code text.
  - Use CSS logical properties so the layout mirrors cleanly in RTL.
  - Western digits by default for finance figures, with `Intl` formatting for EGP and dates.
  - The agent answers in the UI language. Message drafts default to Arabic, with tone options.
  - Machine-translate first, then have a native speaker review.
- **Cost:** Real extra effort. See the cut order in section E.

### D15. Roles: three roles `[Delegated]`
- **Chosen:** Owner, Finance Manager, Collector, enforced server-side.
- **Not chosen:** One admin role; five roles.
- **Why:** Three roles demonstrate least privilege and the approval flow at low cost, and they fit the policy example "over 30 days overdue requires Finance Manager review". Sales Manager and Viewer move to the roadmap.

| Capability | Owner | Finance Manager | Collector |
|---|:---:|:---:|:---:|
| Import data, manage policies and documents | yes | yes | no |
| See all customers | yes | yes | assigned only |
| Approve routine message drafts | yes | yes | yes (assigned customers) |
| Approve recommendations flagged "requires manager review" | yes | yes | no |
| Assign tasks | yes | yes | no |
| View audit log | yes | yes | no |

### D16. Notes in memory: embed them `[Delegated]`
- **Chosen:** Embed collector notes in pgvector. Always include the most recent notes, and add semantic recall for older ones.
- **Not chosen:** Recent-N retrieval only.
- **Why:** Questions such as "what did we agree last time?" span long histories. It also extends RAG beyond policies, and the cost is small once the ingestion pipeline exists.
- **Embedding model:** a multilingual model that handles Arabic, run locally in the container (for example the multilingual-e5 family or BGE-M3), or an embeddings API if one is confirmed. Test Arabic and mixed-language retrieval before committing.

### D17. Delivery: production-minded `[Ali]`
- **Chosen:** Build and deploy as close to production as time allows.
- **Not chosen:** Local recorded demo only.
- **Why:** A live HTTPS URL supports Presentation, and production practices lift Architecture, Code Quality, and Real-World Value. Deployment is not its own rubric line, so it is scheduled after the core vertical slice works; a recorded demo stays as a fallback.
- **Production checklist**
  - Docker Compose, HTTPS reverse proxy (automatic TLS), environment-based config, secrets outside the repo
  - Database migrations, seed script, health-check endpoint
  - Structured logging, error handling, request validation, rate limiting
  - GitHub Actions CI running lint and tests
  - Backups noted in the README, least-privilege database user
  - LLM timeouts, retries, fallback model, per-run cost logging
  - README with setup, architecture diagram, and demo instructions

---

## D. Business and Evidence

### D18. Positioning the idea `[Proposed]`
- **Chosen:** Outcome-first one-liner for speaking ("tells a collection team which customers to chase, why, and what to say"), and a longer version for documentation.
- **Not chosen:** The technical "agentic copilot" phrasing as the opening.
- **Why:** Reviewers hear the first sentence first. Technical terms belong in the architecture section.

### D19. Proving the business case without customers `[Proposed]`
- **Chosen:** Desk research with an evidence label on every claim, an ROI model with explicit assumptions, and a validation plan.
- **Not chosen:** Market-size numbers and claims without sources, or implying pilots.
- **Why:** Honesty survives questioning, and Ali plans to continue the project, so the validation plan is the first post-capstone step.

### D20. Data for the demo `[Proposed]`
- **Chosen:** Synthetic data with realistic patterns (about 120 customers, 1,500 invoices) and a backtest harness.
- **Not chosen:** Waiting for real data, or presenting synthetic results as real.
- **Why:** No access to distributors right now. Synthetic data proves the pipeline works, not predictive accuracy, and we say so openly.

---

## E. Cut Order and Open Items

**If time runs short, cut in this order (first to go first)**
1. Production polish beyond the basics (monitoring extras, backups)
2. Arabic polish beyond the three core screens (keep the structure and strings)
3. Forecast sophistication (keep a simple version with a range)
4. Embedding of older notes (fall back to recent-N)
5. Health Report extras (keep aging and top accounts)

**Never cut:** the receivables engine with tests, risk explanations, policy RAG with citations, the approval gate, the audit log, basic memory, a basic eval with the ablation.

**Open items**
- Confirm the real submission deadline. The LMS page shows 31 Oct 2026, 12:00 AM; check whether an extension exists.
- Pick the specific OpenRouter models after the tool-calling and Arabic tests (D12).
- Choose the embedding model after an Arabic retrieval test (D16).
- Replace pitch placeholders with real demo and eval numbers.

---

## F. Reconciliation Decisions (30 October 2026)

**Context:** Six documents written in separate sessions were compared with this log (details in `Tahseel_AI_Reconciliation_Notes.md`). Ali asked for the right resolution to be applied. Every entry below is tagged `[Delegated]`; Ali can override any of them.

### D21. Two-layer policy design `[Delegated]` (amends D9)
- **Chosen:**
  - Layer 1: structured policy rules (thresholds, grace periods, escalation triggers, limits) stored in tenant configuration (`policy_rules`) and evaluated by the deterministic engine. Each rule links to its source document and section and is confirmed by a Finance Manager (entered manually, or extracted with LLM help and then confirmed).
  - Layer 2: document RAG for explanation, citation, and unstructured policy text.
  - The agent receives the triggered rules plus the retrieved passages and cites both.
- **Not chosen:** RAG only (a retrieval error or an outdated passage could change a decision); rules only (loses explanations and unstructured policy).
- **Why:** Hard thresholds must not depend on semantic search. Thresholds become configurable without code changes, and we have a clean answer to "what if the vector search retrieves the wrong policy".
- **Boundary:** Rules flag and recommend. They never block shipping or credit automatically (D3 and the non-goals).

### D22. Adaptability: canonical schema, adapters, tenant configuration `[Delegated]`
- **Chosen:** All engine logic runs on a canonical data schema (customers, invoices, payments, payment terms, history). Import goes through an adapter interface; the MVP implements only the CSV/Excel adapter. Thresholds, risk weights, grace periods, escalation triggers, reminder cap, and tone defaults live in `tenant_settings`, never in code.
- **Not chosen:** Building Odoo, SAP, or ETA adapters now; hard-coded thresholds.
- **Why:** Shows multi-sector design without paying for integrations. Odoo and ETA adapters stay on the roadmap.

### D23. Lite guardrails in the MVP `[Delegated]` (extends D10)
- **Chosen:**
  - A human sets an invoice to `disputed`. The agent may flag a suspected dispute from notes or replies. Disputed invoices pause follow-up and alert the manager.
  - A configurable cap on reminders per customer per period; drafts beyond the cap need manager override.
  - A rule-based check on drafts (no legal threats, no forbidden phrases), with tone driven by customer tier.
  - The original and edited text of each draft, with the reason for edits or rejection, are stored as recommendation outcomes.
- **Not chosen:** Automatic dispute detection that changes status without a human; legal claims about consumer-protection law; automatic learning from edits.
- **Why:** Cheap to build, strong in the demo, and consistent with "memory stores only human-confirmed events".

### D24. Documentation language `[Delegated]`
- **Chosen:** English for the LMS documentation, code, and README. Arabic for the product UI and message drafts. An Arabic spoken version of the pitch. The Arabic notes stay in the repository as reference.
- **Not chosen:** Arabic-only or fully bilingual documents.
- **Why:** Engineering convention, matches the LMS wording and the rubric; bilingual documents would double the effort.
- **Revisit if:** the instructor's Documentation Guidelines require Arabic.

### D25. One canonical business document `[Delegated]`
- **Chosen:** `Business_Strength` is the single business source of truth. Useful content from `Market_Validation` and `Idea_Evaluation` is merged into it with evidence labels, and those two files move to `docs/archive/`. The honest value framing from `Validation_Critique` and the best questions from the Grill session are merged into the business file and the pitch.
- **Not chosen:** Keeping several overlapping business documents.
- **Why:** Overlapping files drift apart, and a reviewer would find contradictions.

### D26. Project name `[Delegated]`
- **Chosen:** **Tahseel AI** as the official name for the LMS sheet, slides, and documents. The GitHub repository is named `tahseel-ai`; the local folder name does not matter.
- **Not chosen:** Tahseel Copilot (it describes the product type, not the name).
- **Why:** Every document already uses Tahseel AI. One name everywhere.

### D27. Wording rules for claims `[Delegated]`

| Do not say | Say instead |
|---|---|
| A self-assigned score such as "9.5 out of 10" | Omit it |
| "100% tested" | "Core calculations are covered by automated tests" |
| "Hallucination is eliminated" | "Numeric hallucination is reduced by construction and measured in an ablation" |
| "End-to-end encryption" | "TLS in transit and encryption at rest (a deployment setting)" |
| An absolute promise that third-party model providers never train on data | "We rely on provider data policies and will restrict providers before using real data. The demo uses synthetic data" |
| "Payback in 14 days", "zero setup fee" | "Pricing is a hypothesis to test" |
| "Human approval transfers liability" | "Human review and an audit trail" |
| "Late payment is the number one cause of SME failure" (no source in our research) | Omit unless sourced |
| Feature claims about competitors we did not review | "To verify" |
| "The AI stops follow-up automatically on disputes" | "A human sets the dispute status; the system then pauses follow-up" |

### Existing decisions confirmed by the reconciliation (no change)
- pgvector stays; Chroma and Qdrant are not used (D9).
- Three roles stay; a Sales sign-off step is roadmap (D15).
- No ML and no automatic risk re-calibration (D8, D10).
- Drafts only; a human sends (D3).
- Pricing remains a hypothesis.
- OCR receipt reconciliation and a field-collector app are roadmap hypotheses.
- No liability claims.

**Roadmap only:** Odoo and ETA adapters, Sales approval step, risk re-calibration from outcomes, send-time pattern learning, OCR receipt reconciliation, field-collector app, cheque tracking.