# Project Status

**Last updated:** 2 November 2026
**Phase:** Documentation and design are done except two LMS items. The team system is ready. Next: bring the team in, share the tasks, and start building.

## Done

- Idea, scope, tiers, and non-goals (`docs/foundation/Tahseel_AI_Final_Concept.md`)
- 38 decisions with reasons (`docs/governance/Tahseel_AI_Decision_Log.md`, D1 to D38)
- Detailed specification: scoring formulas, a 19-table data model, API, and acceptance criteria (`docs/technical/Tahseel_AI_PRD.md`, version 1.1)
- Technical strength case, memory design, evaluation plan, and security (`docs/technical/Tahseel_AI_Technical_Strength.md`)
- Business case with evidence labels, verified sources, competitors, stakeholder analysis, ROI model, and validation plan (`docs/business/Tahseel_AI_Business_Strength.md`)
- Multi-sector design (`docs/architecture/Tahseel_AI_Adaptability_Strategy.md`)
- Final pitch, slide skeleton, 12-step demo script, and Q&A (`docs/presentation/Tahseel_AI_Final_Pitch.md`)
- A full review of every file against the others (`docs/governance/Tahseel_AI_Consistency_Ledger.md`)
- Five of the six parts of the LMS documentation, in `docs/lms/parts/`: Literature Review, Requirements and Stakeholders, System Architecture, Database Design, UI/UX Design
- Diagrams in `docs/diagrams/`: the ERD, the architecture, the request flow, the deployment, the navigation flow, the stakeholder map, and ten wireframes in English and Arabic
- The team system: `CONTRIBUTING.md`, the guides and the 50-task backlog in `docs/team/`, the GitHub forms and labels in `.github/`, and `tools/team_tools.py`

## Next

1. Bring the team in: share `docs/team/ONBOARDING.md`, then each person fills their row in `docs/team/skills.csv` and sends it as a pull request. Fix names, roles, and the Team Leader in `TEAM.md`
2. Set up GitHub (task T-001): the repository `tahseel-ai`, branch protection on `main`, the team as collaborators, the project board, and the labels (`bash .github/labels.sh`)
3. Share the work: `python tools/team_tools.py suggest`, review and adjust `assignments.csv`, then create the issues in waves (`docs/team/TASK_ASSIGNMENT.md`)
4. Finish the LMS documentation: the Project Planning part (T-090) from the backlog and the assignments, then assemble the PDF (T-091)
5. Build in the order of the backlog: Core tasks first, then Should, then Delivery. The cut order is in the Decision Log, section E
6. Slides, demo video, and the evaluation results, with real numbers from the demo and the evaluation

## Open items

| Item | Detail |
|---|---|
| Announced dates | `LMS_Requirements.md` lists the dates as announced. Confirm with the Technical Instructor whether the first stage (19 Oct) was submitted and whether any extension exists |
| Team Leader | Who submits on the LMS |
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

## Files changed in the last session (2 November 2026)

Decisions added: D37 (team workflow and skills-based assignment) and D38 (AI use policy for contributors).

Added: `CONTRIBUTING.md`; in `docs/team/`: `README.md`, `ONBOARDING.md`, `HOW_TO_WORK_ON_A_TASK.md`, `AI_WORKING_GUIDE.md`, `SKILLS_MATRIX.md`, `TASK_ASSIGNMENT.md`, `skills.csv`, `backlog.csv`, `BACKLOG.md`; `tools/team_tools.py`, `tools/README.md`, `tools/examples/skills.example.csv`; in `.github/`: the task form, the pull request template, and `labels.sh`; the LMS parts 02 to 06 and the diagrams listed above.

Updated: `docs/governance/Tahseel_AI_Decision_Log.md`, `docs/business/Tahseel_AI_Business_Strength.md`, `README.md`, `CLAUDE.md`, `TEAM.md`, `PROJECT_STATUS.md`.
