# Project Planning and Management

This part answers the LMS requirement to clarify the idea, goals, and scope; set a timeline; distribute tasks and responsibilities; identify risks and how to handle them; and define success metrics. It is assembled from the governed sources: the scope (`docs/foundation/Tahseel_AI_Final_Concept.md`), the product specification (`docs/technical/Tahseel_AI_PRD.md`), the business analysis (`docs/business/Tahseel_AI_Business_Strength.md`, specifically its validation plan and risk sections), the backlog (`docs/team/backlog.csv`, 53 tasks), and the team decisions (`docs/governance/Tahseel_AI_Decision_Log.md`, in particular D29, D34, D37–D38, and D40–D42). When this part summarizes them, the source file is the owner of the detail (D35).

**Plan basis.** The delivery plan is organized into four dependency-ordered phases mapped to the backlog waves. Each phase ends with a demoable gate. The team works flexibly and with AI assistance, so the plan does not use weekly-hour or person-day estimates. Progress is tracked by gate evidence and the agreed cut order, not by hours.

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

Five members. The concrete per-task assignments are in `docs/team/assignments.csv`, generated from the skills matrix by `tools/team_tools.py suggest`; the table below records what each person brings, not a fixed silo. Every member takes a meaningful share of the plan and works across waves (D41).

| Member | GitHub | Skills at level 2 or more | Main contribution |
|---|---|---|---|
| **Ali Al-Sharqawi** (Team Leader) | `alialsharqawi` | All skills at level 3 | Product direction and scope, governance, LMS planning, integration, and critical-path reviews; pairs on trust-critical tasks |
| Fatma Eissa | `FatmaEissa` | PY, LLM, VEC, EVAL, DATA, DOC, BIZ, PRES, AR | Backend and AI modules, evaluation, and selected API/DevOps tasks with reviewers |
| Mariam | `Mariam-abd-elhady` | PY, FE, DATA, AR | Frontend and data modules; pairs on LLM, retrieval, and evaluation |
| Zainab Hazem | `ZainabHazem-sys` | PY, UX, DATA, PRES, AR | Repository and data foundation, UX, and Arabic review; builds LLM, retrieval, and API skills through reviewed tasks |
| Alaa | `alaasamy331-droid` | PY, DATA, PRES, AR | Synthetic data, forecast, evaluation, documentation, and presentation; builds UX, API, and frontend skills through reviewed tasks |

**The distribution rule (D37, amended by D41):** tasks are assigned by the skills matrix (`docs/team/skills.csv`) using `tools/team_tools.py suggest`, then a person takes the decision, then any override is recorded. The tool balances task count and relative complexity across every member, gives everyone a meaningful share and work across waves, and balances reviews. One task = one issue = one branch = one pull request; every task has an assignee and a **different** reviewer; a person holds at most two tasks in progress at once. Sensitive tasks (security, tenancy, authentication, the approval gate, financial formulas) get a reviewer who can do that skill alone. When the only strong reviewer is also the natural assignee, the task is paired: another member does it and the strong member reviews. Learning tasks are allowed with a stronger reviewer. Branch names follow `type/T-id-short-description` (D37, amended), and every member commits under their own account — the collaboration record is part of what is graded (D38).

**How to read the workload split.** The role table describes focus areas, not a ranking of effort. Task count alone is not workload: the 53-task plan assigns Ali 9 tasks / 21 relative-complexity points (17.4%), Fatma 15 / 34 (28.1%), Mariam 14 / 35 (28.9%), Zainab 9 / 16 (13.2%), and Alaa 6 / 15 (12.4%). These points are complexity labels, not hours, and describe planned ownership rather than completed output.

**Team Leader's contribution.** Ali's project direction, governance, LMS planning, and assigned reviews are additional to his owner-point share. T-090 is complete; his remaining ownership includes T-040, T-042, T-091, and T-095 (Core), plus T-066, T-051, T-096, and T-097 (Should). Six of his pull requests are merged (#1–#4, #10, and #11), and D42 assigns him as reviewer on 34 of the 53 tasks. T-051 is flagged for a strong independent reviewer if it is implemented.

**AI use policy (D38):** AI is a tutor, not a substitute — each member must be able to explain what they submit; AI-use disclosures appear in pull requests.

## 4. Work plan and phases

The backlog's dependency waves give the real shape of the plan. Size labels are relative complexity (S < M < L), not time estimates; the tool uses them only to balance work across the team.

| Phase | Waves | Content | Gate evidence |
|---|---|---|---|
| **P1 — Setup and data foundation** | Waves 1–4 | Board, protection, skills matrix, assignments and issues; project plan; repository skeleton (T-002), Docker (T-003), CI (T-004), schema and migrations (T-010), synthetic data (T-020), auth and roles (T-011), overdue and risk engine (T-013) | All 53 issues exist; PR #69 merged T-002's repository skeleton, PR #72 merged T-003, PR #73 merged T-022, and PR #74 merged T-004; the remaining P1 work has a demoable synthetic-data and engine gate |
| **P2 — The AI slice** | Waves 5–6 | Retrieval with citations, agent tools and memory, the approval gate, dashboards for aging and the daily queue | The 12-step demo path works end to end on the Core: aging → explanation with citations → draft → approval → recorded outcome |
| **P3 — Integration and guardrails** | Waves 7–8 | Bilingual UI, guards, forecast, Health Report, production basics | The bilingual demo runs without a manual step; the approval gate and tenant isolation are enforced at the API |
| **P4 — Evaluation and delivery** | Waves 9–10 | Evaluation and the LLM-only ablation, slides, demo video, and the final PDF via `tools/build_docs_pdf.py` (T-091) | Evaluation results are in; all LMS deliverables are replaced in place; final presentation by the confirmed Team Leader |

**Milestone gates.** Each phase ends with the gate above, and the evidence stays in the repository. If a gate is not met, use the cut order in the Decision Log (section E) and keep the Core intact.

**Why this plan is honest:** it follows the actual dependency waves, does not assume weekly hours or person-days, and protects the Core through demoable gates and an agreed cut order.

## 5. Risks and how we handle them

| Risk | Impact | Likelihood | Mitigation | Evidence label |
|---|---|---|---|---|
| **Availability drops around exams or other commitments** | A dependency may stall | High | Cut order in advance (D29/section E); at most 2 active tasks per person; a short weekly sync; the leader checks in early, surfaces blockers, and rebalances openly on the issue | Plan of record |
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
4. **Collaboration:** every commit under its own human account (D38); review trail visible; every member contributes a reviewed pull request (see §4, Gate 1).
5. **Documentation integrity:** the LMS link suite stays live; the PDF regenerates from source (T-091); the hierarchy rule (D35) holds — nothing new above is contradicted by anything below.

**For the product after the capstone** (from the Business Strength validation plan, we report them as plans, not results): 10 distributor conversations test A8 and the daily-list value; 2–3 free receivables health pilots measure the candidate outcome: days beyond terms moved and collection effort saved; then a pricing test. Kill criteria are written in `Tahseel_AI_Business_Strength.md` §8.
