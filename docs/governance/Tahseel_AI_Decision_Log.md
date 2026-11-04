# Tahseel AI — Decision Log

**Purpose:** A record of every major fork we faced, what we chose, what we did not choose, and why. It can be turned directly into the "Design Decisions" section of the documentation.

**Status:** Last updated 2 November 2026 (consolidation round: D28 to D36; team workflow: D37 and D38). When a decision was changed later, its entry carries an "Amended by" line. A decision is only changed by editing or amending it here (see D35).

**Final goals every decision serves**
1. **Highest possible score on the capstone rubric:** System Architecture 20%, UI & Dashboard 15%, RAG & Memory 15%, Code Quality 15%, Presentation 15%, Real-World Value 10%, Team Collaboration 10%.
2. **A project that can continue as a product and a service** without claims we cannot prove.

**Origin tags:** `[Ali]` decided by Ali or taken from the PRD. `[Proposed]` proposed by Claude and accepted in discussion. `[Delegated]` Ali asked Claude to decide; Ali can override.

**Companions:** `Tahseel_AI_Final_Concept.md` (scope), `Tahseel_AI_PRD.md` (detailed specification), `Tahseel_AI_Technical_Strength.md`, `Tahseel_AI_Business_Strength.md`, `Tahseel_AI_Final_Pitch.md`, and `CONTRIBUTING.md` (how we work). Which document owns which topic is defined in D35.

---

## A. Product and Scope

### D1. The problem we solve `[Ali]`
- **Chosen:** Receivables collection and credit control for Egyptian B2B distributors.
- **Not chosen:** invoice generator, generic financial chatbot, autonomous debt collector, payments wallet.
- **Why:** The pain is real, tied to cash, and measurable (days beyond terms, DSO, collection rate, collector time). A chatbot or invoice tool has no differentiation. A collector or wallet carries legal and trust risk and sits outside capstone scope.

### D2. Size of the MVP `[Proposed]`
- **Chosen:** A reduced MVP that still runs the full demo flow end to end.
- **Not chosen:** The full PRD (14 features, 5 agents, reranking, Celery, 5 roles, 500 customers and 5,000 invoices).
- **Why:** The rubric rewards architecture, quality, and a working story more than feature count. A smaller product that works beats a larger one that is half broken.
- **Amended by D29 (31 Oct 2026):** the MVP is organized in three tiers (Core, Should, Delivery) so the cut order has a clear basis.

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
- **Chosen:** The Collection Queue (rebuilt every day) is a batch pipeline. The agent handles open-ended investigation, policy-grounded explanations, drafting, and gated task creation.
- **Not chosen:** Everything as an agent, or everything as a pipeline.
- **Why:** The queue must be fast, predictable, and testable. The agent's value is in questions a fixed flow cannot answer. This keeps the word "agentic" honest.
- **Clarified by D36 (31 Oct 2026):** the queue shows a rule-based suggested action; the agent shows a recommendation.

### D7. Number of agents `[Proposed]`
- **Chosen:** One orchestrator with grouped tools.
- **Not chosen:** Five separate agents as in the PRD.
- **Why:** Simpler to build, test, and defend. Most of the five would have been functions with agent names.

### D8. Risk and forecast method `[Ali, from PRD]`
- **Chosen:** Weighted, explainable rules for risk; probability-based forecast with a range and a confidence label.
- **Not chosen:** A trained ML model.
- **Why:** There is no real data to train on, and explainability matters more than accuracy we cannot prove. ML comes when real data exists.
- **Amended by D34 (31 Oct 2026):** default weights are fixed and exposure moves out of the risk score.

### D9. RAG design `[Proposed]`
- **Chosen:** Vector search in pgvector with metadata filters, citations, honest refusal, and broader sources (policies, contracts, collector notes, message templates).
- **Not chosen:** Hybrid search with reranking, a separate vector database, policies only.
- **Why:** A few pages of policy fit in a prompt, so RAG would have had no justification. Reranking is a later upgrade. pgvector in the same database keeps the tenant filter in one query and reduces infrastructure.
- **Amended by D21 (30 Oct 2026):** hard thresholds and escalation triggers move to structured rules evaluated by code; RAG explains and cites.

### D10. Memory `[Proposed]`
- **Chosen:** Two kinds of memory. **Customer memory** (long term): collector notes, promises and their outcomes, recommendation outcomes, contact preferences, dispute status. **Conversation memory** (short term): the chat turns of a thread, used so follow-up questions work. Customer memory stores only human-authored or rule-derived events.
- **Not chosen:** No memory, conversation memory only, or memory generated by the LLM.
- **Why:** "RAG & Memory" is 15% of the rubric and the PRD had no memory. LLM-generated memory can persist wrong inferences, which breaks the trust thesis.
- **Extended by D23 (30 Oct 2026):** human-set dispute status and original-versus-edited drafts are stored as human-confirmed events.
- **Amended by D28 (31 Oct 2026):** the "human-authored or rule-derived only" rule applies to customer memory. Conversation memory is context, never a source of facts, and nothing moves from it into customer memory unless a human saves it.

### D11. Evaluation as a headline strength `[Proposed]`
- **Chosen:** Agent, RAG, recommendation, and safety evals, plus an ablation of LLM-only vs tool-grounded answers.
- **Not chosen:** Showing features only.
- **Why:** The first doubt from reviewers will be "does the AI hallucinate?" A measured answer beats a verbal one. We report real results, including weaknesses.
- **Clarified by D29 (31 Oct 2026):** a basic eval with the ablation is in the Core tier and is never cut; the full plan is a stretch.

---

## C. Stack and Delivery

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
- **Chosen:** Owner, Finance Manager, Collector, enforced server-side. "Collector" is the role name used in the product and the code; "collection officer" is the job title.
- **Not chosen:** One admin role; five roles.
- **Why:** Three roles demonstrate least privilege and the approval flow at low cost, and they fit the policy example "over 30 days overdue requires Finance Manager review". Sales Manager and Viewer move to the roadmap.
- **Extended by D30 (31 Oct 2026):** the matrix below includes the rows added by later decisions.

| Capability | Owner | Finance Manager | Collector |
|---|:---:|:---:|:---:|
| Import data, manage policies and documents | yes | yes | no |
| See all customers | yes | yes | assigned only |
| Approve routine message drafts | yes | yes | yes (assigned customers) |
| Approve recommendations flagged "requires manager review" | yes | yes | no |
| Assign tasks | yes | yes | no |
| View audit log | yes | yes | no |
| Record notes, promises, and call outcomes (D30) | yes | yes | yes (assigned customers) |
| Set an invoice to `disputed` (D30) | yes | yes | yes (assigned customers) |
| Clear a `disputed` status (D30) | yes | yes | no |
| Override the reminder cap (D30) | yes | yes | no |
| Confirm or edit `policy_rules` (D30) | yes | yes | no |
| Edit `tenant_settings` (D30) | yes | yes | no |
| Edit or delete a memory entry, as a soft delete recorded in the audit log (D30) | yes | yes | no |
| Executive dashboard and cash forecast (D30) | yes | yes | no |
| Manage users and roles (D30) | yes | no | no |

### D16. Notes in memory: embed them `[Delegated]`
- **Chosen:** Embed collector notes in pgvector. Always include the most recent notes, and add semantic recall for older ones.
- **Not chosen:** Recent-N retrieval only.
- **Why:** Questions such as "what did we agree last time?" span long histories. It also extends RAG beyond policies, and the cost is small once the ingestion pipeline exists.
- **Embedding model:** a multilingual model that handles Arabic, run locally in the container (for example the multilingual-e5 family or BGE-M3), or an embeddings API if one is confirmed. Test Arabic and mixed-language retrieval before committing.
- **Schema (clarified 31 Oct 2026):** notes are short, so the embedding is a column on `customer_notes`. `document_chunks` is only for policy and contract documents.

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
- **Clarified by D29 (31 Oct 2026):** the "basics" that survive the first cut are Docker Compose, environment-based config, migrations, the seed script, the health-check endpoint, and CI running lint and tests. Per-run LLM cost logging is built together with the agent (D12). Everything else on this checklist is "polish" and sits in the Delivery tier.

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
- **Clarified (31 Oct 2026):** the evidence labels are Sourced, Indicative, Hypothesis, Assumption, and To verify (defined in the Glossary).

### D20. Data for the demo `[Proposed]`
- **Chosen:** Synthetic data with realistic patterns (about 120 customers, 1,500 invoices) and a backtest harness.
- **Not chosen:** Waiting for real data, or presenting synthetic results as real.
- **Why:** No access to distributors right now. Synthetic data proves the pipeline works, not predictive accuracy, and we say so openly.
- **Clarified (31 Oct 2026):** demo numbers in documents and slides come from the generator, not typed by hand. The 500 customers and 5,000 invoices in the PRD are superseded. The backtest harness belongs to the forecast (it is cut together with forecast sophistication).

---

## E. Cut Order and Open Decisions

**If time runs short, cut in this order (first to go first)**
1. Production polish beyond the basics (monitoring extras, backups, rate-limit tuning). The basics are defined in D17.
2. Arabic polish beyond the three core screens (keep the structure and strings).
3. Guardrail extras: the draft check and the reminder cap (keep the human-set `disputed` status).
4. Forecast sophistication (keep a simple version with a range).
5. Embedding of older notes (fall back to recent-N).
6. Health Report extras (keep aging and top accounts).

**Never cut:** the receivables engine with tests, risk explanations, policy RAG with citations, the approval gate, the audit log, basic memory including the way to record notes, promises, and outcomes, tenant isolation with its test, and a basic eval with the ablation (see D29).

**Open decisions**
- Pick the specific OpenRouter models after the tool-calling and Arabic tests (D12).
- Choose the embedding model after an Arabic retrieval test (D16).

Deadlines, the Team Leader, placeholders to fill, and other to-do items are tracked in `PROJECT_STATUS.md`, not here.

---

## F. Reconciliation Decisions (30 October 2026)

**Context:** Six documents written in separate sessions were compared with this log. Ali asked for the right resolution to be applied. Every entry below is tagged `[Delegated]`; Ali can override any of them. The working notes of that comparison are archived (see D31). Clarifications made on 31 October 2026 are marked.

### D21. Two-layer policy design `[Delegated]` (amends D9)
- **Chosen:**
  - Layer 1: structured policy rules (thresholds, grace periods, escalation triggers, limits) stored in tenant configuration (`policy_rules`) and evaluated by the deterministic engine. Each rule links to its source document and section and is confirmed by a Finance Manager. In the MVP rules are entered manually or loaded by the seed script. Extracting rules from documents with LLM help is a roadmap item (clarified 31 Oct 2026).
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
  - A human sets an invoice to `disputed`. The agent may flag a suspected dispute from collector notes (the MVP does not ingest customer replies). Disputed invoices leave the ranked queue, appear in a separate Disputed list, pause follow-up, and alert the manager (clarified 31 Oct 2026).
  - A configurable cap on reminders per customer per period; drafts beyond the cap need manager override. The cap counts approved drafts and logged contacts, because the system never sends anything itself (clarified 31 Oct 2026).
  - A rule-based check on drafts (no legal threats, no forbidden phrases), with tone driven by customer tier.
  - The original and edited text of each draft, with the reason for edits or rejection, are stored as recommendation outcomes.
- **Not chosen:** Automatic dispute detection that changes status without a human; legal claims about consumer-protection law; automatic learning from edits.
- **Why:** Cheap to build, strong in the demo, and consistent with "customer memory stores only human-confirmed events".

### D24. Documentation language `[Delegated]`
- **Chosen:** English for every document in the repository, the LMS documentation, code, and README. Arabic appears only in the product UI, the message drafts, and the spoken version of the pitch.
- **Not chosen:** Arabic-only or fully bilingual documents.
- **Why:** Engineering convention, matches the LMS wording and the rubric; bilingual documents would double the effort.
- **Revisit if:** the instructor's Documentation Guidelines require Arabic.
- **Clarified 31 Oct 2026:** the earlier line that kept the Arabic notes as reference is removed. Every document is now in English.

### D25. One canonical business document `[Delegated]`
- **Chosen:** `Business_Strength` is the single business source of truth. Useful content from `Market_Validation` and `Idea_Evaluation` is merged into it with evidence labels, and those two files move to `docs/archive/` (see D31). The honest value framing from `Validation_Critique` and the best questions from the Grill session are merged into the business file and the pitch. The stakeholder content is preserved (D33).
- **Not chosen:** Keeping several overlapping business documents.
- **Why:** Overlapping files drift apart, and a reviewer would find contradictions.

### D26. Project name `[Delegated]`
- **Chosen:** **Tahseel AI** as the official name for the LMS sheet, slides, and documents. The GitHub repository is named `tahseel-ai`; the local folder name does not matter.
- **Not chosen:** Tahseel Copilot (it describes the product type, not the name).
- **Why:** Every document already uses Tahseel AI. One name everywhere.

### D27. Wording rules for claims `[Delegated]`
These rules apply to every document, slide, and AI answer.

| Do not say | Say instead |
|---|---|
| A self-assigned score such as "9.5 out of 10" | Omit it |
| "100% tested", "100% deterministic" | "Core calculations are computed by code and covered by automated tests" |
| "Hallucination is eliminated" | "Numeric hallucination is reduced by construction and measured in an ablation" |
| "End-to-end encryption" | "TLS in transit and encryption at rest (a deployment setting)" |
| An absolute promise that third-party model providers never train on data | "We rely on provider data policies and will restrict providers before using real data. The demo uses synthetic data" |
| "Payback in 14 days", "zero setup fee" | "Pricing is a hypothesis to test" |
| "Human approval transfers liability" | "Human review and an audit trail" |
| "Late payment is the number one cause of SME failure" (no source in our research) | Omit unless sourced |
| Feature claims about competitors we did not review | "To verify", or "per their public pages" |
| "The AI stops follow-up automatically on disputes" | "A human sets the dispute status; the system then pauses follow-up" |
| "We built and tested..." before it has happened | State the real status, or "[to confirm]" |
| A result stated before it is measured (for example the ablation) | "[measured result]" |
| "Smaller buyers tend to pay selectively" | "Smaller enterprises may pay selectively" (the wording of the Allianz Trade source) |
| "Egypt averages 42 days beyond terms" as if it described domestic distributors | "In the FCIB survey (Aug 2023, small sample), respondents report an average of 42 days beyond terms for Egypt. The respondents appear to be credit professionals selling into Egypt" |
| "Tahseel reduces forgetting and shortens lateness" as a fact | "Designed to shorten lateness and reduce forgetting (hypothesis to validate)" |
| "ETA compliance", "real-time e-invoice validation" | "ETA adapter is on the roadmap" |
| "The AI learns", "predictive model", "automatic recalibration" | "The system stores human decisions as context; it does not retrain or change weights" |
| "Reaches the retailer directly through WhatsApp or SMS" | "Prepares drafts; a human sends them" |
| "Strictly", "absolute", or "never" applied to security or draft behavior | State the specific control and its limits |

### Existing decisions confirmed by the reconciliation (no change)
- pgvector stays; Chroma and Qdrant are not used (D9).
- Three roles stay; a Sales sign-off step is roadmap (D15).
- No ML and no automatic risk re-calibration (D8, D10).
- Drafts only; a human sends (D3).
- Pricing remains a hypothesis.
- OCR receipt reconciliation and a field-collector app are roadmap hypotheses.
- No liability claims.

The roadmap is kept in one place: `Tahseel_AI_Final_Concept.md`, section 12.

---

## G. Consolidation Decisions (31 October 2026)

**Context:** A full review of all repository files found contradictions between documents and gaps in the specification. The decisions below resolve them. Every entry is tagged `[Delegated]`; Ali can override any of them. The full list of findings and their status is in `Tahseel_AI_Consistency_Ledger.md`.

### D28. Memory terminology and write rule `[Delegated]` (amends D10)
- **Chosen:**
  - **Customer memory** (long term) holds notes, promises and outcomes, recommendation outcomes, contact preferences, dispute status, and original-versus-edited drafts. Only human-authored or rule-derived events are stored. Each entry has author, timestamp, and source. A Finance Manager or Owner can edit or delete an entry; deletion is a soft delete recorded in the append-only audit log.
  - **Conversation memory** (short term) holds the chat turns of a thread (the last N turns, optionally a running summary written by the LLM and labeled AI-generated). It exists only so follow-up questions work. It is never a source of facts, and nothing moves from it into customer memory unless a human saves it (for example by turning a finding into a note).
  - The agent never writes to customer memory. Humans write through the UI and the API.
- **Not chosen:** Renaming conversation memory so it is no longer "memory" (it would weaken the link to the "RAG & Memory" rubric line and confuse the vocabulary); letting the LLM write to customer memory.
- **Why:** D10 stated one rule for two different things, which contradicted itself. Scoping the rule keeps the trust thesis and keeps the conversation feature.

### D29. Scope tiers, cut order, and eval tiers `[Delegated]` (amends D2 and section E)
- **Chosen:**
  - **Core** (the demo cannot run without it; never cut): import, receivables engine, risk with factors, priority and the Collection Queue, policy RAG with citations, memory, recording notes and promises and call outcomes, the agent, drafts, the approval gate, tasks and audit log, the three core screens, tenant isolation with roles, and the basic eval with the ablation.
  - **Should** (built after the core slice; the cut order applies): simple forecast, relationship-aware recommendations, Health Report, bilingual UI polish (the string-dictionary structure from day one is not optional), two-layer policy rules, tenant configuration, lite guardrails.
  - **Delivery** (scheduled after the core slice works): production practices and the public HTTPS deployment. If the Core slice is not complete, deployment is skipped and the recorded demo is used.
  - The capability list of each tier lives in `Tahseel_AI_Final_Concept.md`, section 3. The cut order is section E of this log.
  - **Basic eval (never cut):** about 15 agent cases, about 10 RAG queries (including no-policy and conflicting-policy cases), about 5 safety tests (injection, cross-tenant, no send without approval), and the LLM-only versus tool-grounded ablation. The larger plan in `Technical_Strength` is a stretch.
- **Not chosen:** One flat "must have" list of 19 items; leaving "basics" undefined.
- **Why:** When everything is must-have, the label stops guiding decisions. Tiers make the cut order mechanical.

### D30. Permissions matrix completed `[Delegated]` (extends D15)
- **Chosen:** The three-role model stays. The matrix in D15 now includes the rows required by D21 to D23 and D28 (recording memory, setting and clearing `disputed`, overriding the reminder cap, confirming rules, editing settings, editing memory, the executive dashboard, managing users). Customers carry `assigned_collector`, the field that makes "assigned only" enforceable.
- **Not chosen:** Leaving the new capabilities without an owner role.
- **Why:** A Collector setting `disputed` only reduces contact and alerts the manager, so it is safe. Clearing it, overriding the cap, and changing rules or settings change how the system behaves, so they stay with managers.

### D31. Raw and superseded documents are archived `[Delegated]` (extends D25)
- **Chosen:** After their approved content is extracted into the canonical files, these move to `docs/archive/`: `Core_Challenges_And_Trust`, `Validation_Critique`, `Institutional_Grill_Session`, `Idea_Evaluation`, `Market_Validation`, `Reconciliation_Notes`, and the original `Pitch`. Each gets a banner: *"Superseded raw material. Not requirements. It may contain claims the Decision Log rejected. See D31."* AI assistants and readers must not treat anything in `docs/archive/` as a requirement.
- **Not chosen:** Deleting them (history has value); leaving them in place (two sources of truth, and claims we rejected stay in the main folders).
- **Why:** The archived files contain statements that conflict with D3, D8, D10, D21, D23, and D27. Keeping them next to live documents invites copying those statements back.

### D32. The value metric `[Delegated]`
- **Chosen:** The primary metric is **average days beyond terms**: how many days payments arrive after their due date (paid invoices in the period; unpaid overdue invoices are measured to today and shown separately). The exact formula is in the PRD. **DSO** stays as the conversion unit in the ROI model (days of DSO reduction become cash released) and is shown as a secondary KPI.
- **Not chosen:** DSO as the headline KPI.
- **Why:** DSO is moved by sales volume and by payment terms, so it is a noisy measure of collection effectiveness. Days beyond terms isolates lateness, which is what the product targets.

### D33. Stakeholder analysis is preserved `[Delegated]` (extends D25)
- **Chosen:** The personas and stakeholder map in `Idea_Evaluation` are merged into `Business_Strength`, section 3, and expanded: Owner, Finance Manager, Collector, Sales Manager and reps (influencers, not product users), the person who exports the data, the distributor's own customers (affected but not users), and reviewers or auditors. The LMS "Stakeholder Analysis" document is produced from that section. All needs and pain points carry the label Hypothesis until interviews happen.
- **Not chosen:** Archiving `Idea_Evaluation` without preserving the map.
- **Why:** The LMS assignment requires a Stakeholder Analysis, and this is our only source for it.

### D34. Scoring specification `[Delegated]` (amends D8)
- **Chosen:**
  - **Risk score (0 to 100)** estimates how likely a customer is to pay late, from behavior only. Default weights: days overdue 30, historical delay 25, broken promises 25, recent behavior 20 (total 100). The weights live in `tenant_settings` and can be changed per tenant (D22). The PRD's earlier weights were examples.
  - **Exposure leaves the risk score.** The amount owed enters only the priority.
  - **Priority** = normalize(Risk x Overdue Exposure x Urgency). Overdue exposure is the sum of a customer's overdue unpaid amounts. Urgency is defined in the PRD from days overdue and the nearest promise or due date. Every factor is shown.
  - **Collection probability** (the chance a payment arrives within a window, from the customer's history) is used only by the forecast, not by the priority.
  - Risk levels apply after the score is rounded to an integer: Low 0 to 30, Medium 31 to 60, High 61 to 80, Critical 81 to 100.
  - Examples and tests use the new defaults.
- **Not chosen:** Keeping exposure inside risk and again in priority (it counts twice); multiplying risk by collection probability (probability falls as risk rises, so the product pushes the riskiest accounts down the queue).
- **Why:** One clear meaning per number makes the score explainable and testable, which is the point of D8.

### D35. Document hierarchy and ownership `[Delegated]`
- **Chosen:** When two documents disagree, the higher one wins and the lower one is fixed: (1) this Decision Log, (2) `Final_Concept` (scope), (3) `PRD` (details for in-scope items only), (4) `Technical_Strength`, `Business_Strength`, and `Adaptability_Strategy`, (5) `Final_Pitch`, which never introduces a claim that is not in the files above it. Each topic has one owner file; every other file links to it instead of repeating it.

| Topic | Owner |
|---|---|
| Decisions and the cut order | `Decision_Log` |
| Scope, tiers, non-goals, roadmap, demo flow steps | `Final_Concept` |
| Formulas, schema fields, API, acceptance criteria | `PRD` |
| Technical trust, ADRs, memory rules, evaluation, security | `Technical_Strength` |
| Evidence, stakeholders, competitors, ROI, go-to-market, validation | `Business_Strength` |
| Multi-sector design (schema, adapters, configuration) | `Adaptability_Strategy` |
| Terms | `GLOSSARY` |
| LMS requirements and announced deadlines | `LMS_Requirements` |
| Status, open items, next steps | `PROJECT_STATUS` |
| Pitch, Q&A, demo script | `Final_Pitch` |
| People and roles | `TEAM` |
| Rules for AI assistants | `CLAUDE.md` |
| How we work: rules, review, commits | `CONTRIBUTING.md` |
| Task steps, assignment system, skills, backlog, AI use by contributors | `docs/team/` (`HOW_TO_WORK_ON_A_TASK.md`, `TASK_ASSIGNMENT.md`, `SKILLS_MATRIX.md`, `backlog.csv`, `AI_WORKING_GUIDE.md`) |
| Overview and links | `README` |

- **Not chosen:** Several documents restating the same facts.
- **Why:** Duplicated facts drift. The review found most contradictions where a fact was written in more than one place.

### D36. Action vocabulary `[Delegated]`
- **Chosen:** The recommended actions are CALL, WHATSAPP (a draft for a human to send), EMAIL (a draft for a human to send), WAIT, ESCALATE_TO_MANAGER, and TALK_TO_SALES_REP (for strategic accounts, before any contact). `REVIEW_CREDIT_TERMS` is removed from the MVP because credit decisions are out of scope. The Collection Queue shows a **suggested action** computed by rules (no LLM). The agent panel shows a **recommendation** with reasons and citations. When the two differ, the UI shows both and says why.
- **Not chosen:** One unlabeled action field with two possible authors.
- **Why:** Users should always know whether an action came from a rule or from the agent.

---

## H. Team Workflow Decisions (2 November 2026)

**Context:** The team is growing from one person doing the documentation to five people building. These decisions set how work is shared and checked. Both entries are tagged `[Delegated]`; Ali can override either.

### D37. Team workflow and skills-based assignment `[Delegated]`
- **Chosen:**
  - Work is organized as GitHub issues taken from a backlog (`docs/team/backlog.csv`) on a project board with the columns Backlog, Ready, In progress, In review, and Done. One task is one issue, one branch, and one pull request.
  - The maintainer assigns tasks using a skills matrix (`docs/team/skills.csv`) and a suggestion tool (`tools/team_tools.py`). The tool suggests; a person decides and records any override. It balances skill fit, growth, load, shared knowledge, and dependency order.
  - Every task has an assignee and a different reviewer. A person has at most two active tasks. Tasks in security, tenancy, authentication, the approval gate, or financial formulas get a reviewer who can do that skill alone. Learning tasks are allowed with a stronger reviewer, and a task that needs two different skills is paired or split.
  - `main` is protected. A merge needs one approval and a passing check. Merges use a merge commit or a rebase, **not a squash**.
- **Not chosen:** assigning by availability only; letting everyone pick freely (skills and load end up unbalanced); a tool that assigns automatically (it cannot know who is away or who wants to grow); squash merges (they hide the individual commits that are the evidence for Team Collaboration).
- **Why:** The rubric grades Team Collaboration from the repository history, and the product's quality depends on the right person doing each part. The process is light enough to follow and it makes work and reviews visible.

### D38. AI use policy for contributors `[Delegated]`
- **Chosen:**
  - AI tools are allowed for any task. The author is responsible for what they submit and must be able to explain it.
  - An AI tool never receives secrets, real customer data, or personal data. If an AI answer and a project document disagree, the document wins (D35).
  - Work in sensitive areas (authentication, tenant isolation, the approval gate, audit permissions, prompt injection) gets a second careful review.
  - Every pull request states how AI was used: the tool, what it was used for, and what the author verified.
  - An AI agent does not push to `main`, merge, or change repository settings. A person makes each commit, under their own account.
- **Not chosen:** banning AI (it would not be followed and would remove a real benefit); unrestricted use without disclosure (the reviewer cannot tell where to look harder).
- **Why:** AI makes people faster and makes confident mistakes. The product's central promise is that numbers and policy statements can be checked, so the team's own process has to be checkable too.
