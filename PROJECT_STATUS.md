# Project Status

**Last updated:** 23 November 2026
**Phase:** Documentation baseline is complete. The team skills matrix and all 53 skill-weighted assignments are ready; all 53 task issues are on the project board, with 48 open and 5 closed, and the open issues are assigned to D40 phase milestones by wave. Next: finish and merge the T-002 skeleton PR (#69), then start the Core vertical slice. **Final defense: Tuesday, 15 December 2026.**

## Done

- Repository skeleton for T-002: `backend/`, `frontend/`, `data/`, `evals/`, and `deploy/` directories; `.env.example`; `.pre-commit-config.yaml`; and expanded `.gitignore` protections
- Idea, scope, tiers, and non-goals (`docs/foundation/Tahseel_AI_Final_Concept.md`)
- 42 decisions with reasons (`docs/governance/Tahseel_AI_Decision_Log.md`, D1 to D42)
- Detailed specification: scoring formulas, a 19-table data model, API, and acceptance criteria (`docs/technical/Tahseel_AI_PRD.md`, version 1.1)
- Technical strength case, memory design, evaluation plan, and security (`docs/technical/Tahseel_AI_Technical_Strength.md`)
- Business case with evidence labels, verified sources, competitors, stakeholder analysis, ROI model, and validation plan (`docs/business/Tahseel_AI_Business_Strength.md`)
- Multi-sector design (`docs/architecture/Tahseel_AI_Adaptability_Strategy.md`)
- Final pitch, slide skeleton, 12-step demo script, and Q&A (`docs/presentation/Tahseel_AI_Final_Pitch.md`)
- Full review and audit of repository consistency (`docs/governance/Tahseel_AI_Consistency_Ledger.md`: 81 Done, 2 Deferred, 2 Open)
- Six parts of the LMS documentation in `docs/lms/parts/`, including Project Planning and Management
- Diagrams in `docs/diagrams/`: the ERD, the architecture, the request flow, the deployment, the navigation flow, the stakeholder map, and ten wireframes in English and Arabic
- The team system: `CONTRIBUTING.md`, the guides and the 53-task backlog in `docs/team/`, the GitHub forms and labels in `.github/`, and `tools/team_tools.py`
- The filled skills matrix (`docs/team/skills.csv`) and the skill-weighted assignment suggestion (`docs/team/ASSIGNMENT_SUGGESTION.md`, `docs/team/assignments.csv`)
- GitHub setup: branch protection on `main`, all five collaborators, the project board, the labels, and one issue per backlog task (53 issues; 48 open and 5 closed: T-001, T-090, T-091, T-094, T-095); all 53 task issues are on the board, with open tasks assigned to phase milestones by wave
- Legal and security infrastructure: proprietary academic license (`LICENSE`) and vulnerability policy (`.github/SECURITY.md`)

## Next

1. Finish and merge the T-002 skeleton PR (#69), then start T-003 (Docker Compose with pgvector, backend, frontend, and health check) and T-004 (CI: lint and tests on every pull request)
2. Build the Core vertical slice in wave order: data foundation, then the AI slice, then integration and guardrails
3. Slides, demo video, and the evaluation results, with real numbers from the demo and the evaluation (updating the live Canva presentation link submitted on the LMS)

## Open items

| Item | Detail |
|---|---|
| Project Documentation Guidelines | We do not have a copy. We work from an assumed structure (`LMS_Requirements.md`, section 3). Ask the instructor for it if possible |
| OpenRouter models | Choose after testing tool calling, structured output, and Arabic quality (D12) |
| Embedding model | Choose after an Arabic and mixed-language retrieval test (D16) |
| Strong independent reviewer | T-051 has no strong independent reviewer in the current skills matrix. Pair it or add a qualified reviewer before approval if it is built; otherwise cut it in the agreed order. |
| Business claims marked "To verify" | The VAT threshold, the Odoo job posting, the cheque sources, and a proper local-competitor scan (task T-094) |
| Pitch placeholders | Replace the bracketed items in `Final_Pitch` with real demo and evaluation numbers |
| Size labels in the backlog | S, M, and L are relative complexity, not time. Adjust them only if a task turns out to be mislabeled |

## Known gaps in the material

- **No code yet.** The whole product is still to build
- No evaluation results, slides, or demo video yet
- The core business hypothesis (that a meaningful share of lateness comes from late follow-up, A8) is untested
- Whether global collection tools offer policy citations or factor-level explanations is not verified
- The documentation structure for the LMS is an assumption
- The 15 December plan has no buffer. If a gate slips, cut Should or Delivery in the agreed order and keep the Core intact

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

## Follow-ups and bookkeeping (5 November 2026)

These came from a second AI critique (run against a stale `main`) and were re-verified against the current repository before applying — anything already fixed was left alone, and nothing in the governance history was rewritten:

- **D37 amended (approved by Ali):** branch names follow `type/T-id-short-description` (`feat/T-014-risk-engine`, `docs/T-094-competitor-scan`, …) — recorded in the Decision Log, with the same wording adopted in `CONTRIBUTING.md` and `docs/team/HOW_TO_WORK_ON_A_TASK.md`.
- **LMS PDF build tool adopted:** `tools/build_docs_pdf.py` — builds one PDF from `docs/lms/parts/`, overwrites the root `Tahseel_Project_Documentation_v1.pdf` in place (the LMS link is immutable), and needs `pip install markdown` plus weasyprint or a browser (a trial build was verified end to end).
- **`tools/README.md`** documents the PDF build tool's modes and limitations (`--check`, trial `--output`, backup in `_private/pdf_backups/`, landscape pages for wireframes and wide diagrams).
- **Backlog made real:** T-001 rewritten after the repository was created (protection itself, collaborators, and board columns rather than creation), and T-091 now points to the build tool instead of a "script in the repository history". `BACKLOG.md` regenerated; the reachability check passed then ("50 tasks … OK").
- **Clone URL placeholder `<organization-or-owner>`** replaced with the real owner `alialsharqawi` in `docs/team/HOW_TO_WORK_ON_A_TASK.md`.
- Historical runs of the old code name stay in the Decision Log amendment and Consistency Ledger on purpose; no blind global replaces were applied.

## T-090 written and T-091 executed (5 November 2026, same day)

- **T-090 (Part 01, Project Planning and Management):** written as `docs/lms/parts/01_Project_Planning_and_Management.md` (PR #10, merged `21fe732f`): idea and goals, tiered scope with the cut order as the schedule-protection rule, skills-based team structure, a 6-phase plan mapping the backlog's dependency waves (superseded on 21 November 2026 by the 15 December plan, D40), a risk register with evidence labels, and success metrics split between capstone targets and post-capstone plans.
- **T-091 (documentation PDF):** rebuilt `Tahseel_Project_Documentation_v1.pdf` in the repository root from all six parts with `python tools/build_docs_pdf.py` (the previous PDF backed up under `_private/pdf_backups/`). The LMS link keeps pointing at the same root file.
- **Governance note:** the Team Leader delegated merges for these two PRs in the working session; the authorization is recorded as a comment on each PR, and both merges used merge commits (no squash, D37).

## Deadline reset and full-participation assignments (21 November 2026)

- **Hard deadline:** the final defense is **Tuesday, 15 December 2026**. The plan is resequenced backwards from that date in four short phases, each ending with a demoable gate (D40).
- **Weekly-hours model removed:** `hours_per_week`, the 15-hour assumption, capacity caps, and person-day estimates are gone from `skills.csv`, the tool, and every document. Size labels remain as relative complexity only (S=1, M=2, L=3).
- **Full participation:** D41 (amending D37) makes every member take a meaningful share of the plan and work across waves. Skill levels decide fit, not participation. Reviews are spread where skill fit permits; D42 records Ali's accepted higher review share. A task whose only strong member is also the natural assignee remains flagged unless it can be paired.
- **Review-load exception (D42):** Ali accepted a higher review share as team leader. T-060, T-062, and T-073 are paired with members who have basic skills, and Ali reviews them. T-051 remains assigned to Ali and flagged for a strong independent reviewer if built.
- **Tool refactor:** `tools/team_tools.py` now balances task count and complexity, rewards wave coverage and learning, pairs sole-expert tasks, enforces a soft cap, and skips issues that already exist.
- **Assignments generated and reviewed:** `docs/team/assignments.csv` and `docs/team/ASSIGNMENT_SUGGESTION.md`. Every member has tasks in at least four waves. After the D42 pairings, the permanent T-091 reassignment, and the three team-support tasks, task shares are Ali 17.4%, Fatma 28.1%, Mariam 28.9%, Zainab 13.2%, and Alaa 12.4%; Ali reviews 34 of 53 tasks.
- **T-001 closed:** branch protection on `main` verified (`true`), all five collaborators present, board and labels loaded.
- **Issues created and synced:** 45 new issues (#16 to #60). The five that already existed (#5 to #9) were skipped during creation; the three that were open at the time (#6/T-022, #8/T-092, and #9/T-094) have since been assigned and their owner/reviewer details synced to the current plan. Five issues are now closed: #5/T-001, #7/T-090, #9/T-094, #17/T-091, and #61/T-095. T-002 is issue #16.
- **D42 pairings applied on GitHub:** #20/T-060 is assigned to Fatma and reviewed by Ali; #41/T-062 and #59/T-073 are assigned to Mariam and reviewed by Ali. T-051/#53 remains a Should task and needs a strong independent reviewer if it is built.
- **GitHub tracking sync (22 November 2026):** created the four D40 phase milestones; the original 48 open issues were assigned by wave (P1: 12, P2: 19, P3: 15, P4: 2). Added #61/T-095, #62/T-097, and #63/T-096 to P1 and the project board. At that time, the 51 open issues had milestone counts P1: 15, P2: 19, P3: 15, P4: 2; #17/T-091 was In progress, #61/T-095 was In review, and the other 49 were in Backlog. #5/T-001 and #7/T-090 were Done. The board contained 56 items, including the three related pull requests. No individual issue deadlines were added. Since then, #9/T-094, #17/T-091, and #61/T-095 have closed; the current counts are in the phase line above.
- **Files changed:** `docs/team/skills.csv`, `docs/team/backlog.csv`, `docs/team/BACKLOG.md`, `docs/team/assignments.csv`, `docs/team/ASSIGNMENT_SUGGESTION.md`, `docs/team/SKILLS_MATRIX.md`, `docs/team/TASK_ASSIGNMENT.md`, `docs/team/ONBOARDING.md`, `docs/team/README.md`, `docs/team/team-brief-whatsapp.html`, `docs/team/ai-coding-agents-guide.html`, `docs/governance/Tahseel_AI_Decision_Log.md`, `docs/governance/Tahseel_AI_Consistency_Ledger.md`, `docs/lms/parts/01_Project_Planning_and_Management.md`, `docs/technical/Tahseel_AI_PRD.md`, `tools/team_tools.py`, `tools/test_team_tools.py`, `tools/README.md`, `tools/examples/skills.example.csv`, `PROJECT_STATUS.md`, `README.md`, `LMS_Requirements.md`, `TEAM.md`.

## LMS documentation refresh (22 November 2026)

- Part 01 now presents four dependency-ordered phases with demoable gates instead of calendar ranges or person-day estimates.
- Its team section explains relative-complexity ownership, Ali's planning and review contributions, and his current assigned tasks; the assignment record now reflects Ali's permanent ownership of T-091.
- Part 02 no longer displays research-access timestamps. Publication years and source citations remain intact.
- `Tahseel_Project_Documentation_v1.pdf` was rebuilt from all six parts; its cover omits the generated date and now fits on one page, with the contents starting on page two.
- The PDF cover now includes all five documented team display names, identifies Ali as Team Leader, and uses a forest-green and gold palette. Mariam and Alaa remain display names until their full names are confirmed in `TEAM.md`.

## Team coding-agent guide refreshed (22 November 2026)

- `docs/team/ai-coding-agents-guide.html` now compares Copilot Free, Codex Free, Google Antigravity, Gemini API, OpenCode, OpenRouter free models, Cline, and local Ollama.
- It distinguishes monthly, weekly, model-specific daily, and local usage instead of presenting every product as a daily free quota; official quota links are included.
- Added a safe fallback handoff: save state, stop the current agent, and never let multiple agents edit the same branch at once.
- Roo Code was not recommended because its public GitHub repository is archived.

## Team brief refreshed (22 November 2026)

- The standalone WhatsApp brief reflects the current owners for T-091 and T-095 through T-097, the updated 53-task distribution, and the verified wave dependencies.

## GitHub upload preparation (22 November 2026)

- Fixed `tools/team_tools.py` so generated issue bodies close the secondary-skills parenthesis; corrected the existing bodies on #17 and #61–#63.
- Added a focused regression test and documented its command in `tools/README.md`.
- Live GitHub verification (22 November 2026): all 53 task issues were tracked; the 51 open issues at that time matched the local owner/reviewer assignments and phase milestones by dependency wave (P1–P4: 15, 19, 15, and 2); the board had 56 items, #17 was In progress, #61 and PR #64 were In review, the other 49 open tasks were in Backlog, and closed #5 and #7 were Done.
- Validation passed: `python -m unittest tools.test_team_tools` (1 test), `python tools/team_tools.py check` (53 tasks, 5 members), `python tools/build_docs_pdf.py --check` (6 parts, 0 image warnings), and `git -c core.whitespace=cr-at-eol diff --check`. An isolated suggestion smoke test generated 53 unique tasks with distinct reviewers without changing the approved records. The refreshed PDF was rebuilt to 61 pages and visually reviewed page by page.
- Commit `85af153` was authored under Ali's account and pushed on `docs/T-095-team-assignment-records`; PR #64 was open, requested Fatma's review, and was on the board In review. No checks are reported for the PR, and no workflow files are configured on `main`. The rebuilt T-091 PDF, builder, and source-part changes remain unstaged to keep PRs separate; T-091 should follow T-095 because its planning part references the new assignment register. Other task groups remain unstaged/untracked; the board screenshot is kept out of PR scope unless intentionally selected.
