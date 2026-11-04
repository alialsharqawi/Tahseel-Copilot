# Tahseel AI

> **Every morning, Tahseel tells a distributor's collection team which customers to chase, why, and exactly what to say.**

DEPI graduation project (LMS assignment: "DEPI GradProject"). Team of five.

---

## In plain language

Egyptian distributors sell to other businesses on credit. Their finance teams track unpaid invoices in Excel, ERP exports, and WhatsApp, with little support in deciding who to call each day.

Tahseel reads the receivables data, scores each customer's risk and explains the score, finds the relevant rule and clause in the company's own credit policy, remembers past notes and promises, recommends the next action, and drafts an Arabic message. A human approves everything. Nothing is sent automatically.

---

## Status

Documentation is consolidated (31 October 2026). **No code yet.** The current status, next steps, and open items are in `PROJECT_STATUS.md`.

---

## Where each file lives

```text
tahseel-ai/
├── README.md, CONTRIBUTING.md, CLAUDE.md, LMS_Requirements.md, TEAM.md, PROJECT_STATUS.md, GLOSSARY.md
├── docs/
│   ├── foundation/
│   │   └── Tahseel_AI_Final_Concept.md          scope, tiers, demo flow, architecture, roadmap
│   ├── governance/
│   │   ├── Tahseel_AI_Decision_Log.md           every decision: chosen, not chosen, why
│   │   └── Tahseel_AI_Consistency_Ledger.md     findings from the consolidation review and their status
│   ├── technical/
│   │   ├── Tahseel_AI_PRD.md                    detailed specification: formulas, schema, API, acceptance criteria
│   │   └── Tahseel_AI_Technical_Strength.md     trust design, memory, evaluation plan, security
│   ├── architecture/
│   │   └── Tahseel_AI_Adaptability_Strategy.md  serving many sectors: canonical schema, adapters, configuration
│   ├── business/
│   │   └── Tahseel_AI_Business_Strength.md      evidence, stakeholders, competitors, ROI, validation plan
│   ├── presentation/
│   │   └── Tahseel_AI_Final_Pitch.md            pitch, slide skeleton, demo script, Q&A
│   ├── team/                                    backlog, skills matrix, task assignment, onboarding, AI guide
│   ├── lms/parts/                               the parts of the documentation submitted to the LMS
│   ├── diagrams/                                ERD, architecture, wireframes
│   └── archive/                                 superseded raw material, kept for history; not requirements
├── .github/                                     task form, pull request template, label script
├── tools/                                       team_tools.py: skills-based assignment and issue creation
└── _private/                                    git-ignored: screenshots and personal references
```

`CLAUDE.md` is for AI assistants working in this repository.

---

## Start here: reading order (about 20 minutes)

| Order | File | Why read it |
|---:|---|---|
| 1 | `README.md` (this file) | The big picture and the 12 key facts below |
| 2 | `LMS_Requirements.md` | What we must submit and how we are graded |
| 3 | `docs/foundation/Tahseel_AI_Final_Concept.md` | Exact scope: what we build, in which tier, what we do not, the demo flow |
| 4 | `docs/governance/Tahseel_AI_Decision_Log.md` | Every major choice: what we chose, what we rejected, and why |
| 5 | `docs/technical/Tahseel_AI_Technical_Strength.md` | How the design earns trust; memory design; evaluation plan; security |
| 6 | `docs/business/Tahseel_AI_Business_Strength.md` | Evidence for the problem, stakeholders, competitors, value model, validation plan |
| 7 | `docs/technical/Tahseel_AI_PRD.md` | The detailed specification: risk and priority formulas, data model, API, acceptance criteria |
| 8 | `docs/architecture/Tahseel_AI_Adaptability_Strategy.md` | How one platform serves different sectors through configuration |
| 9 | `docs/presentation/Tahseel_AI_Final_Pitch.md` | The pitch, slide skeleton, demo script, likely questions and answers |
| Anytime | `GLOSSARY.md`, `TEAM.md`, `PROJECT_STATUS.md` | Terms, people, and current status |
| New to the team | `docs/team/ONBOARDING.md`, then `CONTRIBUTING.md` | How to get started and how we work |

When two documents disagree, the higher one in the hierarchy wins: Decision Log, then Final Concept, then PRD, then the strength documents, then the pitch (Decision Log, D35).

---

## The 12 things everyone on the team must know

1. **Problem:** collection decisions are made from spreadsheets and memory. We turn receivables data into a ranked daily action list.
2. **Users:** the Collector uses it daily, the Finance Manager approves and oversees, the Owner sees the summary.
3. **Numbers come from tested code, never from the LLM.** The LLM explains, drafts messages, and answers questions by calling tools.
4. **The Collection Queue is a pipeline. The agent is for investigation** and open questions.
5. **Risk is a transparent weighted-rules score, not machine learning.** Every score lists its reasons.
6. **Policy is two layers:** structured rules evaluated by code, and cited document passages for explanation. If no relevant policy exists, the system says so.
7. **Customer memory stores only human-authored or rule-derived events** (notes, promises, decisions). Conversation memory is short-term context and never a source of facts.
8. **A human approves before anything consequential happens,** enforced at the API level.
9. **We use synthetic data and never claim real customers, pilots, or interviews.** Every business claim carries an evidence label.
10. **Stack:** Next.js, FastAPI, PostgreSQL with pgvector, OpenRouter for LLM access, Docker.
11. **The UI is fully Arabic (RTL) and fully English,** with a language toggle.
12. **We aim for production quality** (HTTPS, CI, logging, tests), but only after the core demo flow works.

One framing to keep in mind: **Tahseel does not prevent lateness. It is designed to shorten it and reduce forgetting** (a hypothesis we will test).

---

## Not doing (non-goals for the capstone)

Payments or wallets, automatic credit blocking, automatic WhatsApp or email sending, legal advice, a trained ML risk model, ERP or CRM integrations (only the CSV/Excel adapter is built), credit-limit recommendations. Cheque tracking and other later ideas are on the roadmap in `Final_Concept`, section 12.

---

## Working principles

- **Honesty first.** If we did not do or measure it, we do not claim it. Label assumptions as assumptions.
- **Decisions go in the Decision Log.** If you change a decision, add or edit its entry.
- **Update `PROJECT_STATUS.md`** when something is finished, blocked, or newly decided.
- **Everyone commits under their own GitHub account.** Team collaboration is graded on the repository history.
- **If a document contradicts the Decision Log, flag it** and resolve it in the log rather than leaving both.
- **Each topic has one owner file;** other files link to it instead of repeating it (D35).
- **Work through issues and pull requests,** with a reviewer, as described in `CONTRIBUTING.md` (D37).

---

## Quick start

Not runnable yet: there is no code. This section will hold the setup and run instructions when the code starts.

## Planned code layout (once coding starts)

```text
backend/  frontend/  data/  evals/  deploy/
```
