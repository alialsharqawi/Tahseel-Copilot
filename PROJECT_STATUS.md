# Project Status

**Last updated:** 31 October 2026
**Phase:** Documentation consolidated. Next: apply the consolidated files, prepare the LMS documents, then build.

## Done

- Idea, scope, tiers, and non-goals defined (`docs/foundation/Tahseel_AI_Final_Concept.md`)
- 36 decisions recorded with reasons (`docs/governance/Tahseel_AI_Decision_Log.md`, D1 to D36)
- Detailed specification with scoring formulas, a 21-table data model, API, and acceptance criteria (`docs/technical/Tahseel_AI_PRD.md`, version 1.1)
- Technical strength case, memory design, evaluation plan, and security (`docs/technical/Tahseel_AI_Technical_Strength.md`)
- Business case with evidence labels, verified sources, competitor check, stakeholder analysis, ROI model, and validation plan (`docs/business/Tahseel_AI_Business_Strength.md`)
- Multi-sector design (`docs/architecture/Tahseel_AI_Adaptability_Strategy.md`)
- Final pitch, slide skeleton, 12-step demo script, and Q&A (`docs/presentation/Tahseel_AI_Final_Pitch.md`)
- LMS requirements and rubric transcribed (`LMS_Requirements.md`)
- Full review of every file against the others; the findings are in `docs/governance/Tahseel_AI_Consistency_Ledger.md`
- Raw documents from separate sessions folded into the canonical files; they move to `docs/archive/` (D31)

## Next

1. Replace the repository files with the consolidated versions, then run `archive_docs.sh` to move the superseded files to `docs/archive/`
2. Create the GitHub repository `tahseel-ai` (one repo for the team) and agree roles in `TEAM.md`
3. Produce the LMS documentation PDF, using the working structure in `LMS_Requirements.md`:
   - Project Planning & Management (needs a real plan with owners and dates)
   - Literature Review (expand from the competitor landscape)
   - Requirements Gathering, including the Stakeholder Analysis
   - System Architecture (drawn diagram)
   - Database Design (ERD from the PRD data model)
   - UI/UX Design (wireframes in Arabic and English)
4. Build in the order in `Technical_Strength`, section 10: repo skeleton and delivery basics; data model, auth, tenant scoping and roles; receivables engine with tests; synthetic data generator; import and Health Report; risk, priority, and suggested actions; queue and customer profile UI with the forms to record notes and promises; policy RAG with rules; agent tools with approval and audit; memory; basic evaluation and ablation; then the Should tier in the cut order; then deployment
5. Presentation PDF and demo video, with real numbers from the demo and the evaluation

## Open items

| Item | Detail |
|---|---|
| Announced dates | `LMS_Requirements.md` lists the dates as announced. Confirm with the Technical Instructor whether the first stage (19 Oct) was submitted and whether any extension exists |
| Team Leader | Who submits on the LMS |
| Team roles and GitHub usernames | See `TEAM.md` |
| Project Documentation Guidelines | We do not have a copy. We work from an assumed structure (`LMS_Requirements.md`, section 3). Ask the instructor for it if possible |
| OpenRouter models | Choose after testing tool calling, structured output, and Arabic quality (D12) |
| Embedding model | Choose after an Arabic and mixed-language retrieval test (D16) |
| Business claims marked "To verify" | The VAT threshold, the Odoo job posting, the cheque sources, and a proper local-competitor scan (`Business_Strength`) |
| Pitch placeholders | Replace the bracketed items in `Final_Pitch` with real demo and evaluation numbers |

## Known gaps in the material

- No ERD, drawn architecture diagram, or wireframes yet
- The literature review is a competitor table, not yet a full review
- The project plan has no real dates or owners
- The core business hypothesis (that a meaningful share of lateness comes from late follow-up, A8) is untested
- Whether global collection tools offer policy citations or factor-level explanations is not verified
- The documentation structure for the LMS is an assumption
- There is no code yet

## Constraints to remember

- No access to real distributors. Data is synthetic and we never claim real customers or pilots.
- The project will continue after the capstone as a product and a service, and the business side is graded too.
- The cut order if time runs short is in the Decision Log, section E.

## Files changed in the last session (31 October 2026)

Decisions added: D28 to D36 (memory rule, tiers, permissions, archive, value metric, stakeholders, scoring, hierarchy, actions).

Updated: `docs/governance/Tahseel_AI_Decision_Log.md`, `GLOSSARY.md`, `docs/foundation/Tahseel_AI_Final_Concept.md`, `docs/technical/Tahseel_AI_PRD.md`, `docs/technical/Tahseel_AI_Technical_Strength.md`, `docs/business/Tahseel_AI_Business_Strength.md`, `docs/architecture/Tahseel_AI_Adaptability_Strategy.md`, `docs/presentation/Tahseel_AI_Final_Pitch.md`, `LMS_Requirements.md`, `README.md`, `CLAUDE.md`, `PROJECT_STATUS.md`, `TEAM.md`.

Added: `docs/governance/Tahseel_AI_Consistency_Ledger.md`, `archive_docs.sh`.

Archived (by the script): `Core_Challenges_And_Trust`, `Validation_Critique`, `Institutional_Grill_Session`, `Reconciliation_Notes`, `Idea_Evaluation`, `Market_Validation`, and the original `Pitch`.