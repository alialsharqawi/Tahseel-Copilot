# Tahseel AI

> **Every morning, Tahseel tells a distributor's collection team which customers to chase, why, and exactly what to say.**

DEPI graduation project (LMS assignment: "DEPI GradProject"). Team of five.

---

## In plain language

Egyptian distributors sell to other businesses on credit. Their finance teams track unpaid invoices in Excel, ERP exports, and WhatsApp, and decide who to call each day mostly by feel.

Tahseel reads the receivables data, scores each customer's risk and explains the score, finds the relevant clause in the company's own credit policy, remembers past notes and promises, recommends the next action, and drafts an Arabic message. A human approves everything. Nothing is sent automatically.

---

## Status

Foundation phase is done: idea, scope, decisions, business case, pitch. **No code yet.**
Six extra documents were added later and are being reconciled with the Decision Log. See `PROJECT_STATUS.md` and `docs/governance/Tahseel_AI_Reconciliation_Notes.md`.

---

## Where each file lives

```text
Tahseel-Copilot/
├── README.md, CLAUDE.md, LMS_Requirements.md, TEAM.md, PROJECT_STATUS.md, GLOSSARY.md
├── docs/
│   ├── foundation/
│   │   └── Tahseel_AI_Final_Concept.md          exact MVP scope, demo flow, architecture, data model
│   ├── governance/
│   │   ├── Tahseel_AI_Decision_Log.md           every decision: chosen, not chosen, why
│   │   ├── Tahseel_AI_Reconciliation_Notes.md   conflicts between added documents and the log
│   │   ├── Tahseel_AI_Core_Challenges_And_Trust.md     trust, security, learning, disputes, field collection (Arabic)
│   │   ├── Tahseel_AI_Institutional_Grill_Session.md   hard investor, credit, and security questions with answers (Arabic)
│   │   └── Tahseel_AI_Validation_Critique.md           "is lateness just normal?" and the honest value framing (Arabic)
│   ├── technical/
│   │   ├── Tahseel_AI_Technical_Strength.md     trust design, memory, evaluation plan
│   │   └── Tahseel_AI_PRD.md                    original PRD, wider than the MVP
│   ├── architecture/
│   │   └── Tahseel_AI_Adaptability_Strategy.md  serving many sectors: canonical schema, adapters, tenant config (Arabic, file is cut off)
│   ├── business/
│   │   ├── Tahseel_AI_Business_Strength.md      evidence, ROI model, competitors, validation plan
│   │   ├── Tahseel_AI_Idea_Evaluation.md        target customer and stakeholder map (Arabic)
│   │   └── Tahseel_AI_Market_Validation.md      market evidence and positioning (Arabic, to merge into Business_Strength)
│   ├── presentation/
│   │   ├── Tahseel_AI_Final_Pitch.md            pitch, slide skeleton, demo script, Q&A
│   │   └── Tahseel_AI_Pitch.md                  original pitch
│   ├── lms/                                     what gets submitted
│   └── diagrams/                                ERD, architecture, wireframes
└── _private/                                    git-ignored: screenshots and personal references
```

`CLAUDE.md` is for AI assistants working in this repository.

---

## Start here: reading order (about 20 minutes)

| Order | File | Why read it |
|---:|---|---|
| 1 | `README.md` (this file) | The big picture and the 12 key facts below |
| 2 | `LMS_Requirements.md` | What we must submit, the deadline, and how we are graded |
| 3 | `docs/foundation/Tahseel_AI_Final_Concept.md` | Exact scope: what we build, what we do not, the demo flow, architecture |
| 4 | `docs/governance/Tahseel_AI_Decision_Log.md` | Every major choice: what we chose, what we rejected, and why |
| 5 | `docs/governance/Tahseel_AI_Reconciliation_Notes.md` | Where the later documents disagree with the log, and the proposed fixes |
| 6 | `docs/technical/Tahseel_AI_Technical_Strength.md` | How the technical design earns trust; memory design; evaluation plan |
| 7 | `docs/business/Tahseel_AI_Business_Strength.md` | Evidence for the problem, value model, competitors, validation plan |
| 8 | `docs/presentation/Tahseel_AI_Final_Pitch.md` | The pitch, slide skeleton, demo script, likely questions and answers |
| 9 | `docs/technical/Tahseel_AI_PRD.md` and `docs/presentation/Tahseel_AI_Pitch.md` | The original product definition: full data model, API, risk weights, RAG pipeline. The Final Concept narrows it |
| Anytime | `GLOSSARY.md`, `TEAM.md`, `PROJECT_STATUS.md` | Terms, people, and current status |

---

## The 12 things everyone on the team must know

1. **Problem:** collection decisions are made from spreadsheets and memory. We turn receivables data into a ranked daily action list.
2. **Users:** the Collection Officer uses it daily, the Finance Manager approves and oversees, the Owner sees the summary.
3. **Numbers come from tested code, never from the LLM.** The LLM explains, retrieves policy, drafts messages, and answers questions by calling tools.
4. **The daily queue is a pipeline. The agent is for investigation** and open questions.
5. **Risk is a transparent weighted-rules score, not machine learning.** Every score lists its reasons.
6. **RAG is cited.** If no relevant policy exists, the system says so. It never invents policy.
7. **Memory stores only human-confirmed events** (notes, promises, decisions), not AI guesses.
8. **A human approves before anything consequential happens,** enforced at the API level.
9. **We use synthetic data and never claim real customers, pilots, or interviews.** Every business claim carries an evidence label.
10. **Stack:** Next.js, FastAPI, PostgreSQL with pgvector, OpenRouter for LLM access, Docker.
11. **The UI is fully Arabic (RTL) and fully English,** with a language toggle.
12. **We aim for production quality** (HTTPS, CI, logging, tests), but only after the core demo flow works.

One framing to keep in mind: **Tahseel does not prevent lateness. It shortens it and reduces forgetting.**

---

## Not doing (non-goals)

Payments or wallets, automatic credit blocking, automatic WhatsApp or email sending, legal advice, a trained ML risk model, ERP or CRM integrations, cheque tracking (deferred until validated).

---

## Working principles

- **Honesty first.** If we did not do or measure it, we do not claim it. Label assumptions as assumptions.
- **Decisions go in the Decision Log.** If you change a decision, add or edit its entry.
- **Update `PROJECT_STATUS.md`** when something is finished, blocked, or newly decided.
- **Everyone commits under their own GitHub account.** Team collaboration is graded on the repository history.
- **If a document contradicts the Decision Log, flag it** and resolve it in the log rather than leaving both.

---

## Planned code layout (once coding starts)

```text
backend/  frontend/  data/  evals/  deploy/
```