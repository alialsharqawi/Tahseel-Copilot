# Tahseel AI — Consistency Ledger

**Purpose:** The findings of the full review of the repository (31 October 2026) and what happened to each one.
**Status:** Last updated 4 November 2026 (post-LMS design parts 02-06, team framework, and repository governance). Decisions that resolve findings are in `Tahseel_AI_Decision_Log.md`, section G (D28 to D36) and section H (D37 to D38).

**How to read it.** Every finding has a number. Numbers 53 and 76 were never used, so the ledger has 96 findings.

| Status | Meaning | Count |
|---|---|---:|
| Done | Applied in the consolidated files, LMS documentation parts, and team framework | 81 |
| Archived | Content folded into the canonical files; the file moves to `docs/archive/` when `archive_docs.sh` is run | 7 |
| Deferred | Waits for team skills/capacity inputs (`skills.csv`) or final LMS PDF assembly | 2 |
| Closed | Needs no action | 4 |
| Open | Still to verify (assumptions/market claims tracked in task T-094) | 2 |

## Still open or deferred

| # | Finding | Why it waits |
|---|---|---|
| 3 | TEAM has only placeholders; Team Collaboration is judged from commit history | Framework ready in `docs/team/`; awaits team members filling capacity and ratings in `skills.csv` |
| 34 | Origin tags (`[Ali]`, `[Delegated]`) in the version submitted to the LMS | Keep in the log; strip from the compiled LMS PDF copy |
| 93 | Claims still unchecked: VAT threshold, job posting, cheque sources, a local-competitor scan | Labeled To verify; tracked as backlog task T-094 |
| 95 | Whether global tools offer policy citations or factor-level explanations is not verified | Assumption A9; listed as To verify; tracked in task T-094 |

## All findings

| # | Finding | Files | Resolution | Status |
|---:|---|---|---|---|
| 1 | README status stale ("No code yet", "six extra documents") | README | Rewritten; status points to PROJECT_STATUS | Done |
| 2 | LMS wants Database Design and UI/UX Design; no dedicated files; `diagrams` and `lms` folders empty | LMS_Requirements, README | Implemented in `docs/lms/parts/` (04_System_Architecture, 05_Database_Design, 06_UI_UX_Design) with 10 bilingual wireframes and diagrams in `docs/diagrams/` | Done |
| 3 | TEAM has only placeholders; Team Collaboration is judged from commit history | TEAM, docs/team | Framework ready in `docs/team/`; awaits member PRs for `skills.csv` | Deferred |
| 4 | Documentation language policy unclear (Arabic files vs English rule) | CLAUDE, README, Log | D24 clarified: every document is in English | Done |
| 5 | "Memory" mixed conversation turns with human-confirmed events | Glossary, CLAUDE | D28: two kinds of memory with a scoped write rule | Done |
| 6 | Glossary missing roles and project terms | Glossary | About 20 terms added or corrected | Done |
| 7 | Queue had several names | Glossary, README, Final_Concept | Collection Queue everywhere ("daily" only describes the rhythm) | Closed |
| 8 | `_private` must be git-ignored | README | Confirmed by the team: it is in `.gitignore` | Closed |
| 9 | CLAUDE reading order omitted LMS_Requirements | CLAUDE | Added | Done |
| 10 | Final_Concept's old open questions said "English UI" | Final_Concept | Section removed; D14 is the source | Done |
| 11 | Final_Concept still mentioned LangGraph | Final_Concept | Removed; D13 | Done |
| 12 | Conversation memory treated as Memory without a rule | Final_Concept | D28 applied | Done |
| 13 | Submission date inside the concept file | Final_Concept | Removed; the date lives in LMS_Requirements | Done |
| 14 | Production practices listed as must-have but built after the core | Final_Concept, Log | Delivery tier; basics defined (D17, D29) | Done |
| 15 | 19 must-haves with no priority tiers | Final_Concept | Core, Should, Delivery (D29) | Done |
| 16 | Exposure counted twice; collection probability and urgency undefined | Final_Concept, PRD | D34 scoring specification | Done |
| 17 | Risk weights fixed in text but configurable per tenant | Final_Concept, PRD | Default weights 30/25/25/20 in `tenant_settings` | Done |
| 18 | Out-of-scope lists differed between Final_Concept and README | Final_Concept, README | One list in Final_Concept; README copies it | Done |
| 19 | Success criteria missed the toggle, Health Report, guardrails, eval, memory writes | Final_Concept | Added, with tier marks | Done |
| 20 | Final_Concept status "Draft" was stale | Final_Concept | Status and date updated | Done |
| 21 | Note embeddings had no table | Final_Concept, PRD | Embedding column on `customer_notes` (D16) | Done |
| 22 | D10 contradicted itself | Log | Amended by D28 | Done |
| 23 | Reconciliation_Notes stale and partly inaccurate | Reconciliation_Notes | Replaced by the Decision Log section F and this ledger; moved to the archive | Archived |
| 24 | Permission matrix lacked later capabilities; no `assigned_collector` | Log, PRD | D30 | Done |
| 25 | D21 mentioned LLM extraction of rules (extra scope) | Log | Manual or seeded rules in the MVP; extraction is roadmap | Done |
| 26 | D23 mentioned customer replies; the cap had no unit | Log | Notes only; the cap counts approved drafts and logged contacts | Done |
| 27 | "Basics" in the cut order undefined | Log | Defined in D17 and D29 | Done |
| 28 | Evaluation absent from the concept file | Final_Concept | C14 and success criteria | Done |
| 29 | Deadline open item sat in the Decision Log | Log | Moved to PROJECT_STATUS and LMS_Requirements | Done |
| 30 | Log had no update date; section C heading was time-relative | Log | Status line and neutral headings | Done |
| 31 | README tree root and `docs/archive` missing | README | Fixed | Done |
| 32 | Reconciliation claimed documents were updated; some were not | Several | Verified file by file; fixed in the consolidation | Closed |
| 33 | Sweep for rejected wording in all files | All | Run on every live file on 31 Oct; archived files are not swept | Done |
| 34 | Origin tags (`[Ali]`, `[Delegated]`) in the version submitted to the LMS | Log | Keep in the log; strip from the LMS copy | Deferred |
| 35 | Raw files carried rejected claims and CLAUDE pointed to them | CLAUDE, raw files | CLAUDE no longer points to them; D31 archives them | Archived |
| 36 | Core_Challenges: 13 contradictions with decisions | Core_Challenges | Approved content now in Technical_Strength section 8; roadmap in Final_Concept | Archived |
| 37 | Validation_Critique: sources claimed but unchecked; claims without labels | Validation_Critique | Value framing now in Business_Strength with labels | Archived |
| 38 | Grill session: answers contradicted D3, D21, D23, D27 | Institutional_Grill_Session | Corrected Q&A now in Final_Pitch | Archived |
| 39 | Roadmap scattered over several files | Final_Concept, Log | One roadmap in Final_Concept section 12 | Done |
| 40 | Glossary lacked Days Beyond Terms, Hypothesis, Evidence label | Glossary | Added | Done |
| 41 | Success-based pricing had no baseline | Business_Strength | Baseline requirement added | Done |
| 42 | Stakeholder map needed for the LMS Stakeholder Analysis | Idea_Evaluation, Business_Strength, docs/lms | Implemented in `docs/lms/parts/03_Requirements_and_Stakeholders.md` and `docs/diagrams/stakeholder_map.*` | Done |
| 43 | Idea_Evaluation: rejected wording; ETA and WhatsApp claims | Idea_Evaluation | Useful content merged; moved to the archive | Archived |
| 44 | Market_Validation: "Independent" label, unsourced claims, competitors as facts | Market_Validation | Tone list moved to Final_Concept and PRD; moved to the archive | Archived |
| 45 | Odoo "postings" vs "one posting" | Business_Strength | Corrected to one posting, anecdotal | Done |
| 46 | Weak competitor sources | Business_Strength | Vendor pages and marketplace listings checked on 31 Oct | Done |
| 47 | VAT threshold single-sourced; "why now" not tied to the MVP | Business_Strength | Labeled To verify; why-now labeled as a hypothesis | Done |
| 48 | Validation phases 2 and 3 empty; core hypothesis missing | Business_Strength | Phases filled; assumptions A8 and A9; new risks | Done |
| 49 | Evidence labels undefined | Glossary, Business_Strength | Five labels defined and applied | Done |
| 50 | ROI arithmetic and KPI | Business_Strength | Arithmetic checked (correct); KPI per D32 | Done |
| 51 | Roadmap held credit-limit analytics while the concept file listed it as out of scope | Business_Strength, Final_Concept | Out of scope for the capstone; roadmap, validate first | Done |
| 52 | Stakeholder map must become an LMS document (D33) | Business_Strength, docs/lms | Implemented in `docs/lms/parts/03_Requirements_and_Stakeholders.md` | Done |
| 54 | Tone list existed only in Market_Validation | Final_Concept, PRD, Adaptability | Formal, friendly, firm added | Done |
| 55 | FCIB and Allianz figures unchecked | Business_Strength | Both opened on 31 Oct; figures confirmed with caveats | Done |
| 56 | PRD scoring ambiguities | PRD | Sections 11 and 12 rewritten (D34) | Done |
| 57 | PRD conflicts with the Decision Log | PRD | Banner and a table of superseded statements (D35) | Done |
| 58 | PRD schema gaps | PRD | 19 tables with fields; statuses defined | Done |
| 59 | No way to write customer memory; API gaps | PRD, Final_Concept | C7, AC-009, and the missing endpoints | Done |
| 60 | Action vocabulary; queue action vs agent recommendation | PRD, Final_Concept | D36 | Done |
| 61 | Days beyond terms and DSO missing from dashboard and tools | PRD, Final_Concept | Portfolio KPIs tool and dashboard items | Done |
| 62 | PRD 8-week plan assumed interviews | PRD | Marked as a proposal; the real plan comes with the LMS Project Planning | Done |
| 63 | PRD examples contradicted each other | PRD | One consistent example; demo numbers come from the generator | Done |
| 64 | Technical_Strength numbering collided with decision numbers | Technical_Strength | T1 to T8 | Done |
| 65 | Audit write blocked until approval; LLM summary stored; "calibration"; memory deletion | Technical_Strength | Corrected (D28, ADR-5) | Done |
| 66 | Cut-order conflict (forecast first or production polish first) | Technical_Strength, Log | Technical_Strength points to Log section E | Done |
| 67 | Build priority incomplete | Technical_Strength | 13 steps in tier order | Done |
| 68 | Evaluation size too large; present-tense claims without code | Technical_Strength | Basic and full tiers; claims phrased as plan | Done |
| 69 | No security section; ADRs missing | Technical_Strength | Section 8 and ADR-9 to ADR-12 | Done |
| 70 | Adaptability still held R1, R2, R3; truncated pillar 5 | Adaptability_Strategy | Rewritten; pillar 5 written from scratch | Done |
| 71 | Canonical schema did not match the tables | Adaptability_Strategy | Mapped to the PRD data model | Done |
| 72 | Adaptability: installments, rejected wording, demo idea | Adaptability_Strategy | Fixed; two-profile demo kept as a stretch | Done |
| 73 | LMS: two different documentation lists; Guidelines file missing | LMS_Requirements | Working structure documented as an assumption; the question is in PROJECT_STATUS | Done |
| 74 | LMS_Requirements: scattered open items, references by number, stale status | LMS_Requirements | Rewritten; references by name | Done |
| 75 | "Collector" vs "Collection Officer" | Glossary, Final_Concept | Role vs job title | Done |
| 77 | Final_Pitch decided the ablation result in advance | Final_Pitch | Placeholder for the measured result | Done |
| 78 | Final_Pitch used the past tense with no code | Final_Pitch | Conditional wording and status line | Done |
| 79 | Final_Pitch: operational claims without labels; the Arabic text was stronger than the English | Final_Pitch | Softened and aligned | Done |
| 80 | Final_Pitch described competitors more strongly than the sources | Final_Pitch | Verified wording | Done |
| 81 | Final_Pitch memory and hallucination wording | Final_Pitch | Per D28 and D27 | Done |
| 82 | Final_Pitch "do not say" list incomplete | Final_Pitch | Extended | Done |
| 83 | Final_Pitch demo incomplete; three versions of the flow | Final_Pitch | One 12-step flow plus extra moments | Done |
| 84 | Final_Pitch slides and Q&A lacked adaptability, bilingual UI, engineering practice | Final_Pitch | Added | Done |
| 85 | Final_Pitch header; short Arabic version | Final_Pitch | Header updated | Done |
| 86 | Original Pitch.md not reviewed in detail | Pitch | Archived by decision | Closed |
| 87 | PROJECT_STATUS stale | PROJECT_STATUS | Rewritten | Done |
| 88 | PROJECT_STATUS lacked a files-changed list; README had a duplicate status | PROJECT_STATUS, README | Fixed | Done |
| 89 | Ownership of open items and of the demo flow | Log | D35 ownership table | Done |
| 90 | FCIB caveats: age, small sample, respondents appear to be suppliers selling into Egypt | Business_Strength, Final_Pitch | Recorded; pitch wording adjusted | Done |
| 91 | Allianz wording ("may"); "Growing businesses"; the SME-failure claim is not on the page | Business_Strength, Log | Corrected; D27 extended | Done |
| 92 | Neither main source tests the "suppliers forget" mechanism | Business_Strength | Assumption A8 and interview questions 9 and 10 | Done |
| 93 | Claims still unchecked: VAT threshold, job posting, cheque sources, a local-competitor scan | Business_Strength | Labeled To verify; listed in PROJECT_STATUS | Open |
| 94 | Global tools already prioritize, forecast, and track calls; our edge is not the queue itself | Business_Strength, Final_Pitch | Positioning and Q&A rewritten | Done |
| 95 | Whether global tools offer policy citations or factor-level explanations is not verified | Business_Strength | Assumption A9; listed as To verify | Open |
| 96 | Line items are not modeled (invoice-level only) | Adaptability_Strategy | Recorded as a design choice | Done |
| 97 | The queue ranks overdue accounts only; a PRD sentence implied pre-due invoices | PRD | Sentence reworded | Done |
| 98 | README and CLAUDE name files that the archive script moves | README, CLAUDE | Legacy raw files archived to `docs/archive/`; canonical references in README and CLAUDE updated | Done |
