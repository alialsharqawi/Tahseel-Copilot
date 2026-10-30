# Project Status

**Last updated:** 30 October 2026
**Phase:** Foundation complete. Reconciling added documents, preparing LMS documents, then build.

## Done

- Idea, scope, and non-goals defined (`docs/foundation/Tahseel_AI_Final_Concept.md`)
- 20 decisions recorded with reasons (`docs/governance/Tahseel_AI_Decision_Log.md`)
- Technical strength case, memory design, and evaluation plan (`docs/technical/Tahseel_AI_Technical_Strength.md`)
- Business case with evidence labels, ROI model, and validation plan (`docs/business/Tahseel_AI_Business_Strength.md`)
- Final pitch, slide skeleton, demo script, and Q&A (`docs/presentation/Tahseel_AI_Final_Pitch.md`)
- LMS requirements and rubric transcribed (`LMS_Requirements.md`)
- Repository structure organized; README and CLAUDE.md for team and AI assistants
- Six additional documents added (adaptability, idea evaluation, market validation, core challenges and trust, grill session, validation critique) and reviewed

## In progress: reconciliation

The six added documents conflict with the Decision Log in places and contain unsupported claims. Details and recommended resolutions are in `docs/governance/Tahseel_AI_Reconciliation_Notes.md` (items R1 to R18, all pending). Proposed log amendments D21 to D25 await Ali's confirmation.

## Next

1. Confirm the reconciliation resolutions, then amend the Decision Log and the affected documents
2. Confirm the open items below (deadline, Team Leader, name, documentation language)
3. Create the GitHub repository (one repo for the team) and agree roles in `TEAM.md`
4. Produce the LMS documentation PDF:
   - Project Planning & Management (needs a real plan with owners and dates)
   - Literature Review (expand from the competitor table)
   - Stakeholder Analysis and Requirements
   - System Architecture (drawn diagram)
   - Database Design (ERD)
   - UI/UX Design (wireframes in Arabic and English)
5. Build, in this order: repo skeleton and Docker Compose, receivables engine with tests, synthetic data generator, import and Health Report, risk and priority, queue and customer profile UI, policy RAG with citations, agent tools with approval and audit, memory, evaluation and ablation, forecast, deployment
6. Presentation PDF and demo video, with real numbers from the demo and the evaluation

## Open items

| Item | Detail |
|---|---|
| Real deadline | LMS shows Sat 31 Oct 2026, 12:00 AM. The first notice said 19 Oct 2026. Confirm with the Technical Instructor which applies and whether there is an extension |
| Project Documentation Guidelines file | Sent earlier to the groups. Get a copy and add it to the repo |
| Team Leader | Who submits on the LMS |
| Project name | Folder is named Tahseel-Copilot; documents say Tahseel AI. Pick one for the LMS sheet, the repo, and the slides |
| Documentation language | The added documents are Arabic; the rest is English. Decide for the LMS PDF (D24) |
| Team roles and GitHub usernames | See `TEAM.md` |
| OpenRouter models | Choose after testing tool calling, structured output, and Arabic quality |
| Embedding model | Choose after an Arabic and mixed-language retrieval test |
| Truncated file | `Tahseel_AI_Adaptability_Strategy.md` ends mid-sentence; re-export it |

## Known gaps in the material

- No ERD, drawn architecture diagram, or wireframes yet
- Literature review is a short competitor table, not a full review
- Project plan has no real dates or owners
- Pitch placeholders still need real demo and evaluation numbers
- Some claims in the added documents are unsourced or unverified (see R14)

## Constraints to remember

- No access to real distributors. Data is synthetic and we never claim real customers or pilots.
- The project will continue after the capstone as a product and a service, and the business side is graded too.
- Cut order if time runs short is in the Decision Log, section E.