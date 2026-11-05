# Project Planning and Management

This part answers the LMS requirement to clarify the idea, goals, and scope; set a timeline; distribute tasks and responsibilities; identify risks and how to handle them; and define success metrics. It is assembled from the governed sources: the scope (`docs/foundation/Tahseel_AI_Final_Concept.md`), the product specification (`docs/technical/Tahseel_AI_PRD.md`), the business analysis (`docs/business/Tahseel_AI_Business_Strength.md`, specifically its validation plan and risk sections), the backlog (`docs/team/backlog.csv`, 50 tasks), and the team decisions (`docs/governance/Tahseel_AI_Decision_Log.md`, in particular D29, D34, D37, and D38). When this part summarizes them, the source file is the owner of the detail (D35).

**An honest note on the plan itself.** The milestones below are our proposal, built from the backlog's dependency waves. The binding calendar is the one the instructor sets on the LMS; the first submission (the three dynamic links) went live on 4 November 2026 as confirmed in `PROJECT_STATUS.md`. Team availability (real hours per week per member) is collected in the skills matrix at onboarding, and the plan is revised when those numbers exist.

## 1. The idea and its goals

**One paragraph.** Tahseel AI is a credit-control and receivables assistant for mid-sized Egyptian B2B distributors. It reads the company's own receivables from Excel/ERP exports, tells the finance team **who to call today, why, and what to say** based on payment history and the company's own credit policy, drafts the message, and **records the outcome** so the next day's advice gets better. Every collection action stays under human approval; the system advises at the desk and never contacts a customer by itself.

**Goals.**

1. **Product goal:** move the owner or finance manager from "we chase everyone and forget half" to a daily, explained, policy-grounded action list. Success on the core demo path: aging, explanation, drafting, approval gate, and outcome recording all work end to end.
2. **Learning goal:** demonstrate a complete AI-assisted product workflow — deterministic business logic, retrieval with citations (D9/D21), an agent with tool calls (D12), memory, and a human approval gate (D36) — on realistic synthetic data (D20), with honest measurement.
3. **Business goal (evaluated, not blocking):** the thesis "late follow-up, not customer hostility, is a meaningful share of Egyptian B2B lateness" (hypothesis A8), and the capstone retirement plan for a real-world value discussion.

## 2. Scope: what is in, what can be cut

The scope is structured evidence, not a wish list (from D29 and the Decision Log, section E):

| Tier | Meaning | Examples |
|---|---|---|
| **Core** (41 tasks) | Never cut | Receivables engine with tests, risk explanations, policy RAG with citations, the approval gate, the audit log, memory (notes, promises, outcomes), tenant isolation with its test, the basic evaluation with the ablation |
| **Should** (7 tasks) | Built after the core slice works, in the cut order | Forecast, Health Report, draft check, reminder cap, local-competitor scan |
| **Delivery** (2 tasks) | Scheduled after the core slice works | Deployment, backups-style Operational tasks |

**If time runs short** we cut in the fixed order of Decision Log section E (production polish first, Arabic polish beyond the three core screens, guardrail extras, forecast sophistication, older-note embeddings, Health Report extras) — never the Core list. This is our main schedule-protection mechanism and it is decided in advance, not during a panic.

**Out of scope for the capstone** (from the Final Concept and PRD): automatic contacting of customers by the agent, automatic dispute status changes, late fees or interest computation, replacing the ERP or accounting system, multi-tenant SaaS onboarding.

## 3. Team, roles, and responsibilities

Five members. Names and agreed responsibilities are being finalized at the onboarding kickoff (they will be recorded here and in `TEAM.md`; anything the team agrees on is committed, not only discussed).

| Area of ownership | Approx. share of backlog | Skills code | Notes |
|---|---|---|---|
| **Team Leader — Ali Al-Sharqawi** | LMS deliverables, governance, review, integration | GIT, DOC | Submits on the LMS (confirmed); holds the review/approval gate (D37) |
| Databases and data (ERD, migrations, synthetic data) | ~9 tasks | DB, DATA | — |
| Backend and AI (FastAPI, engine, retrieval, agent) | ~18 tasks | API, AI | strongest-skill pairing for the core engine |
| Frontend (Next.js bilingual dashboards) | ~12 tasks | UI, FRONT | Arabic-first RTL (D6) |
| Docs, QA, and demo materials | ~11 tasks | DOC, QA | evidence labels, evaluation runs, slides |

**The distribution rule (D37):** tasks are assigned by the skills matrix (`docs/team/skills.csv`) using `tools/team_tools.py suggest`, then a person takes the decision, then any override is recorded. One task = one issue = one branch = one pull request; every task has an assignee and a **different** reviewer; a person holds at most two active tasks. Sensitive tasks (security, tenancy, authentication, the approval gate, financial formulas) get a reviewer who can do that skill alone. Learning tasks are allowed with a stronger reviewer. Branch names follow `type/T-id-short-description` (D37, amended), and every member commits under their own account — the collaboration record is part of what is graded (D38).

**AI use policy (D38):** AI is a tutor, not a substitute — each member must be able to explain what they submit; AI-use disclosures appear in pull requests.

## 4. Work plan and timeline

The backlog's dependency waves give the real shape of the plan (sizes: S ≈ half a day, M ≈ 1–2 days, L ≈ 3–5 days; totals from `python tools/team_tools.py backlog`):

| Phase | Approx. calendar (proposal) | Waves | Content | Load |
|---|---|---|---|---|
| **P0 — Kickoff and setup** | 5–8 Nov 2026 | Wave 1 | Board, labels, protection, skills matrix, first PR per member (T-001, T-022 partially) | ~9 person-days |
| **P1 — Plan and documents** | 9–15 Nov 2026 | Wave 2 (this part, T-090; issue assembly) | Project plan, assignments, issues in all waves | ~2 person-days |
| **P2 — Sprint 1: data and groundwork** | 16 Nov → 4 Dec 2026 | Waves 3–4 | Docker (T-003), CI (T-004), model/migrations (T-010), synthetic data (T-020), auth/roles (T-011), engine (T-013) | ~16 person-days |
| **P3 — Sprint 2: the AI slice** | 7–25 Dec 2026 | Waves 5–6 | Retrieval with citations, agent tools and memory, the approval gate, dashboards for aging and the daily queue | ~56 person-days |
| **P4 — Sprint 3: UI, guardrails, polish** | 4–22 Jan 2027 | Waves 7–8 | Bilingual UI, guards, forecast, Health Report, production basics | ~29 person-days |
| **P5 — Evaluation and delivery** | Jan 2027 (instructor calendar) | Waves 9–10 | Evaluation + ablation, slides, demo video, and the final PDF via `tools/build_docs_pdf.py` (T-091) | ~3 person-days |

**Milestone gates** (checked at the end of each phase, evidence in the repo):

1. **Gate 1 (P1):** all 50 issues exist on the board; every member has ≥ 1 merged PR; skills matrix filled.
2. **Gate 2 (P2):** the engine runs against the synthetic dataset; the 19-table schema is migrated; CI green on every PR; the aging tests pass.
3. **Gate 3 (P3):** the 12-step demo path works end to end on the core: aging → explanation with citations → draft → approval → recorded outcome.
4. **Gate 4 (P4):** the cut decision exercised (if needed) with the Core intact; the basic evaluation executed.
5. **Gate 5 (P5):** all LMS deliverables replaced in place (the links stay live); final presentation by the confirmed Team Leader.

The cut order (Decision Log section E) applies at any gate where the remaining work exceeds the remaining time.

**Why dates are honest here:** the wave totals sum to ~115 person-days of estimated work for a five-person team working part-time in parallel; if the real availability from the skills matrix is materially lower, phases shrink by cutting Should/Delivery per the agreed order, **not** by compressing the Core.

## 5. Risks and how we handle them

| Risk | Impact | Likelihood | Mitigation | Evidence label |
|---|---|---|---|---|
| **Part-time availability collapses around exams** | Schedule slips | High | Cut order in advance (D29/section E); at most 2 active tasks per person; weekly 15-min sync; the 48-hour rule (a member silent 2 days gets asked, not blamed) | Plan of record |
| **No real distributor data** | The demo rests on synthetic data | Certain (constraint) | Synthetic generator with realistic patterns (D20), stated as synthetic everywhere (D27); the validation plan probes the real world after the capstone | Sourced (constraint) |
| **LLM/model choice underperforms on Arabic** | Explanations degrade | Medium | Model choice deferred until a tool-calling + Arabic test (D12); fallbacks defined in the Decision Log | To verify |
| **Embedding quality for mixed Arabic/English notes** | Retrieval misses | Medium | Embedding model chosen after the Arabic retrieval test (D16); hybrid retrieval (BM25 + vectors) so keyword hits survive embedding weakness | To verify |
| **RAG retrieval error could mislead a rule** | Wrong advice → trust damage | Medium | Two-layer design: thresholds evaluated by the deterministic engine, RAG only explains and cites (D21); approval gate keeps every action human (D36) | Sourced (design) |
| **Global tools "do it too" / competitor pressure** | Positioning weakens | Low to medium | Positioning is Arabic + Excel-first + policy citations + human approval — verified gap (assumption A9, scan task T-094 rechecks it) | To verify |
| **A member stalls or drops a task** | Dependency blocks | Medium | One task = one branch; two-task cap; the leader reassigns, recorded on the issue; nothing invisible (the audit log, D37) | Plan of record |
| **Grade risk: claims outrun evidence** | Rubric penalties | Medium (mitigated) | Evidence labels on every claim (D19); banned-wording rule D27; the pitch is a demo-voice script only within D39's rails; numbers come from code | Sourced (process) |
| **Key concentration: the Team Leader holds governance** | Slow if he is unavailable | Medium | Each member merges small PRs after review; the Decision Log records overrides; the weekend demo script can be run by any pair with the recorded scenario | To verify |

## 6. Success metrics

**For the capstone (D34-scoring alignment with the rubric):** the graded dimensions are architecture, UI, RAG and memory, code quality, presentation, real-world value, and collaboration (10%). The concrete, checkable targets:

1. **Demo integrity:** the 12-step demo path succeeds end to end, and the numbers shown on screen are the engine's numbers (aging, exposure, risk level, priority ranking are exactly what the deterministic engine computes — verified by unit tests).
2. **Explanation quality:** every policy-based recommendation shows its rule and its source citation; every agent recommendation shows tool calls and costs (D8/D36 vocabulary).
3. **Evaluation (basic, never cut):** ~15 agent cases, ~10 RAG queries (including no-policy and conflicting-policy cases), ~5 safety tests, plus the ablation. We report actual results **including weaknesses** (D29) — the results section is written after the runs, never before.
4. **Collaboration:** every commit under its own human account (D38); review trail visible; each member's first PR merged in week 1 (see §4, Gate 1).
5. **Documentation integrity:** the LMS link suite stays live; the PDF regenerates from source (T-091); the hierarchy rule (D35) holds — nothing new above is contradicted by anything below.

**For the product after the capstone** (from the Business Strength validation plan, we report them as plans, not results): 10 distributor conversations test A8 and the daily-list value; 2–3 free receivables health pilots measure the candidate outcome: days beyond terms moved and collection effort saved; then a pricing test. Kill criteria are written in `Tahseel_AI_Business_Strength.md` §8.
