# Project Status

**Last updated:** 4 November 2026
**Phase:** Documentation baseline, system architecture, database design, bilingual wireframes, team framework, and repository legal/security standards are complete. Next: team onboarding kickoff, skills matrix completion, Project Planning (T-090), and Sprint 1 (Core Engine).

## Done

- Idea, scope, tiers, and non-goals (`docs/foundation/Tahseel_AI_Final_Concept.md`)
- 38 decisions with reasons (`docs/governance/Tahseel_AI_Decision_Log.md`, D1 to D38)
- Detailed specification: scoring formulas, a 19-table data model, API, and acceptance criteria (`docs/technical/Tahseel_AI_PRD.md`, version 1.1)
- Technical strength case, memory design, evaluation plan, and security (`docs/technical/Tahseel_AI_Technical_Strength.md`)
- Business case with evidence labels, verified sources, competitors, stakeholder analysis, ROI model, and validation plan (`docs/business/Tahseel_AI_Business_Strength.md`)
- Multi-sector design (`docs/architecture/Tahseel_AI_Adaptability_Strategy.md`)
- Final pitch, slide skeleton, 12-step demo script, and Q&A (`docs/presentation/Tahseel_AI_Final_Pitch.md`)
- Full review and audit of repository consistency (`docs/governance/Tahseel_AI_Consistency_Ledger.md`: 81 Done, 2 Deferred, 2 Open)
- Five of the six parts of the LMS documentation in `docs/lms/parts/`: Literature Review, Requirements and Stakeholders, System Architecture, Database Design, UI/UX Design
- Diagrams in `docs/diagrams/`: the ERD, the architecture, the request flow, the deployment, the navigation flow, the stakeholder map, and ten wireframes in English and Arabic
- The team system: `CONTRIBUTING.md`, the guides and the 50-task backlog in `docs/team/`, the GitHub forms and labels in `.github/`, and `tools/team_tools.py`
- Legal and security infrastructure: proprietary academic license (`LICENSE`) and vulnerability policy (`.github/SECURITY.md`)

## Next

1. Bring the team in: share `docs/team/ONBOARDING.md`, then each person fills their row in `docs/team/skills.csv` and sends it as a pull request. Fix names, roles, and the Team Leader in `TEAM.md`
2. Set up GitHub (task T-001): the repository `Tahseel-Copilot` (D26 as amended), branch protection on `main`, the team as collaborators, the project board, and the labels (`bash .github/labels.sh`)
3. Share the work: `python tools/team_tools.py suggest`, review and adjust `assignments.csv`, then create the issues in waves (`docs/team/TASK_ASSIGNMENT.md`)
4. Finish the LMS documentation: the Project Planning part (T-090) from the backlog and the assignments, then assemble the PDF (T-091) replacing `Tahseel_Project_Documentation_v1.pdf` in the root directory so the submitted LMS documentation link automatically reflects the final document
5. Build in the order of the backlog: Core tasks first, then Should, then Delivery. The cut order is in the Decision Log, section E
6. Slides, demo video, and the evaluation results, with real numbers from the demo and the evaluation (updating the live Canva presentation link submitted on the LMS)

## Open items

| Item | Detail |
|---|---|
| Team roles, skills, and GitHub usernames | `TEAM.md` and `docs/team/skills.csv` |
| Project Documentation Guidelines | We do not have a copy. We work from an assumed structure (`LMS_Requirements.md`, section 3). Ask the instructor for it if possible |
| OpenRouter models | Choose after testing tool calling, structured output, and Arabic quality (D12) |
| Embedding model | Choose after an Arabic and mixed-language retrieval test (D16) |
| Business claims marked "To verify" | The VAT threshold, the Odoo job posting, the cheque sources, and a proper local-competitor scan (task T-094) |
| Pitch placeholders | Replace the bracketed items in `Final_Pitch` with real demo and evaluation numbers |
| Size estimates in the backlog | The S, M, and L guesses are rough. Compare them with reality after the first tasks and adjust |

## Known gaps in the material

- **No code yet.** The whole product is still to build
- The LMS part "Project Planning and Management" and the documentation PDF are not done
- No evaluation results, slides, or demo video yet
- The core business hypothesis (that a meaningful share of lateness comes from late follow-up, A8) is untested
- Whether global collection tools offer policy citations or factor-level explanations is not verified
- The documentation structure for the LMS is an assumption
- The backlog is larger than a few weeks of part-time work. If time is short, follow the cut order

## Constraints to remember

- No access to real distributors. Data is synthetic and we never claim real customers or pilots.
- The project will continue after the capstone as a product and a service, and the business side is graded too.
- The cut order if time runs short is in the Decision Log, section E.

## Files changed in the last session (4 November 2026)

- Added repository legal and security infrastructure: `LICENSE` (sole proprietary academic evaluation license) and `.github/SECURITY.md` (enterprise vulnerability disclosure SLA and contact).
- Audited and updated `docs/governance/Tahseel_AI_Consistency_Ledger.md`: closed findings #2, #42, #52, and #98 as Done (81 total Done, 2 Deferred, 2 Open).
- Synchronized reading orders, companion file trees, and project phases across `README.md`, `CLAUDE.md`, `docs/governance/Tahseel_AI_Decision_Log.md`, and `PROJECT_STATUS.md`.

## Review round 2 applied (4 November 2026, same day)

A second full review (Decision-Log-as-baseline) found 21 actionable defects; all approved fixes were applied:

- **D26 amended:** the official repository name is `Tahseel-Copilot` (the submitted LMS link is immutable); all references aligned (`LMS_Requirements.md`, `README.md`, this file, `docs/team/HOW_TO_WORK_ON_A_TASK.md`).
- **D39 added (Ali):** `Final_Pitch.md` is officially a demo-voice presentation script — the story of the completed product on stage, drafted before the build as the destination to build toward. Safety rails: framing note in the header, bracketed results only, plan-voice lines convert to past tense when the work exists, and D27 still applies outside the demo narrative.
- **`Final_Pitch.md`:** removed past-tense build/test claims (D27), rebuilt the demo script as the canonical 12 steps (including recording the call outcome), added the adaptability / bilingual UI / engineering-practice Q&A rows, aligned the competitor answer with the Business Strength positioning, added a Status header line, applied hedge wording throughout.
- **`LICENSE`** corrected to Digital Egypt Pioneers Initiative (DEPI); **`SECURITY.md`** aligned with D15 roles, the D36 action vocabulary, and D27 wording.
- **ERD** (`erd.dot`, `erd.svg`, re-rendered `erd.png`) now shows the `embedding` column on `customer_notes` and `document_chunks` (D16).
- **`backlog.csv`:** the rule-based draft check moved from Core T-048 to Should T-051 per the cut order; `BACKLOG.md` regenerated.
- **`tools/team_tools.py`:** duplicate-ID detection, clean dependency-error output, graceful missing/empty `skills.csv`, "AI" heading fix, no hardcoded paths — verified by running all subcommands and failure cases.
- **`.gitignore`:** `.env` (per CLAUDE rule 8), Python, and Node exclusions added before code starts. **PR template:** reviewer-approval line added (D37).
- Full round-2 record: `docs/governance/Tahseel_AI_Consistency_Ledger.md`, section "Review round 2" (R1 to R17, all Done).
