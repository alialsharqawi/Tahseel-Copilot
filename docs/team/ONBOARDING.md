# Onboarding: Start Here

Welcome. This page gets you from zero to your first task. Reading it takes about 15 minutes; the reading path takes about 90 minutes more.

## 1. What we are building (in one minute)

**Tahseel AI** helps Egyptian distributors collect overdue invoices. Every morning it tells the collection team **which customers to chase, why, and exactly what to say**.

It reads the receivables data (from an Excel or CSV file), ranks the customers, explains each score, finds the relevant rule in the company's own credit policy, remembers past notes and promises, recommends the next action, and drafts a message in Arabic. **A person approves everything. Nothing is sent automatically.**

It is our DEPI graduation project, graded on seven things: System Architecture 20%, UI & Dashboard 15%, RAG & Memory 15%, Code Quality 15%, Presentation 15%, Real-World Value 10%, Team Collaboration 10%.

**The five ideas to remember**
1. **Numbers come from tested code,** never from the AI model.
2. **The AI never invents policy.** It cites a rule or a document passage, or says none was found.
3. **A human approves,** enforced in the API.
4. **Memory is written only by people or rules,** never by the AI.
5. **We are honest.** Our data is synthetic, and we never claim real customers, pilots, or results we do not have.

## 2. The demo we are building toward

1. Upload a receivables file (mapping, validation, preview).
2. The dashboard and a Health Report appear.
3. The Collection Queue ranks the customers, each with a suggested action.
4. Open a customer: invoices, promises, the risk score with every factor.
5. Ask the agent: "What should we do with this customer?"
6. The agent calls tools and finds the policy rule and passage.
7. It recommends an action, with reasons and a citation.
8. Generate an Arabic draft and choose a tone.
9. A person edits and approves it.
10. A task is created and the audit log is written.
11. The collector records the call result and a promise.
12. A follow-up question in the chat uses what was recorded.

The screens are in `docs/diagrams/wireframes/` (English and Arabic).

## 3. Where we are

**Done (documentation and design)**
- The idea, the scope, and the tiers: Core, Should, Delivery (`docs/foundation/Tahseel_AI_Final_Concept.md`).
- **38 decisions** with reasons (`docs/governance/Tahseel_AI_Decision_Log.md`).
- The detailed specification: formulas, 19 database tables, API, acceptance criteria (`docs/technical/Tahseel_AI_PRD.md`).
- The technical trust design, the business case with evidence labels, and the multi-sector design.
- The pitch, the 12-step demo script, and the slide skeleton.
- A full review of all files against each other, with every finding tracked (`docs/governance/Tahseel_AI_Consistency_Ledger.md`).
- Five of the six parts of the LMS documentation: Literature Review, Requirements and Stakeholders, System Architecture, Database Design, UI/UX Design (`docs/lms/parts/`), with the diagrams in `docs/diagrams/`.
- This team system: backlog, skills matrix, task assignment, and these guides.

**Not done yet**
- **No code.** The whole product is still to build.
- The LMS part "Project Planning and Management", and assembling the documentation PDF.
- The slides, the demo video, and the evaluation results.
- Any contact with real distributors. Everything about users is still a hypothesis.

**The plan is bigger than our time.** The backlog (`docs/team/BACKLOG.md`) is 50 tasks. If time runs short we cut in a fixed order (Decision Log, section E): the Core tier is never cut.

## 4. How we work together

- Tasks live as **GitHub issues**, taken from the backlog. Each has acceptance criteria, files to read, skills, size, and a reviewer.
- The maintainer gives tasks according to **skills** (`docs/team/TASK_ASSIGNMENT.md`). You fill in your row in `skills.csv` first.
- **One task = one issue = one branch = one pull request.** Every pull request is reviewed by someone else.
- We commit **under our own accounts.** The history is graded as evidence of collaboration.
- AI tools are welcome, with rules (`docs/team/AI_WORKING_GUIDE.md`).

The rules are in `CONTRIBUTING.md`; the walk-through is in `docs/team/HOW_TO_WORK_ON_A_TASK.md`.

## 5. Your setup checklist

- [ ] A GitHub account, and you have accepted the invitation to the repository
- [ ] `git` installed, with your name and the email registered on your GitHub account (`git config --global user.name`, `git config --global user.email`)
- [ ] The repository cloned
- [ ] Python 3.11 or newer, and Node.js 20 or newer (versions will be fixed in task T-002; ask the maintainer)
- [ ] Docker installed (Docker Desktop, or Docker Engine and the Compose plugin)
- [ ] An editor you like (for example VS Code)
- [ ] An AI tool, if you want one (read the AI guide first)
- [ ] Your row in `docs/team/skills.csv` filled in and sent as a pull request

Do not worry if something does not work yet; the first tasks create the project skeleton. Write down what you tried and ask.

## 6. Reading path

Read in this order. Times are rough.

| Order | File | Why | Time |
|---:|---|---|---:|
| 1 | `README.md` | The big picture and the 12 key facts | 5 min |
| 2 | `docs/foundation/Tahseel_AI_Final_Concept.md` | Exactly what we build, in which tier, and the demo flow | 20 min |
| 3 | `GLOSSARY.md` | The terms (skim now, return when a word is unclear) | 5 min |
| 4 | `docs/governance/Tahseel_AI_Decision_Log.md` | Why things are the way they are. Read D1 to D17 and D28 to D38 first | 20 min |
| 5 | `CONTRIBUTING.md` | The rules | 10 min |
| 6 | Your area (table below) | What you need for your tasks | 30 min |

**By area**

| If your tasks are in | Read |
|---|---|
| Backend and data | `docs/technical/Tahseel_AI_PRD.md` (sections 10 to 21), `docs/lms/parts/05_Database_Design.md` |
| AI (agent, RAG, memory) | `docs/technical/Tahseel_AI_Technical_Strength.md`, PRD sections 13 to 15, `docs/architecture/Tahseel_AI_Adaptability_Strategy.md` |
| Frontend and design | `docs/lms/parts/06_UI_UX_Design.md`, the wireframes in `docs/diagrams/wireframes/` |
| Testing and evaluation | Technical Strength section 5, PRD sections 26 and 30, `docs/lms/parts/03_Requirements_and_Stakeholders.md` |
| Documentation, business, presentation | `docs/business/Tahseel_AI_Business_Strength.md`, `docs/lms/parts/02_Literature_Review.md`, `docs/presentation/Tahseel_AI_Final_Pitch.md`, `LMS_Requirements.md` |
| DevOps | `docs/lms/parts/04_System_Architecture.md` (section 8), Decision Log D17 |

## 7. Your first week

| When | What |
|---|---|
| Day 1 | Read sections 1 to 3 here and the first four files in the reading path. Do the setup checklist |
| Day 1 or 2 | Fill in your skills row and send the pull request. Tell the maintainer your real hours per week |
| Day 2 | Read your area. Write down your questions |
| Day 2 or 3 | You get your first task. Read it, ask questions in the issue, then follow `HOW_TO_WORK_ON_A_TASK.md` |
| End of the week | Your first pull request is in review. Add yourself to the contribution log in `TEAM.md` |

Tasks without dependencies (wave 1 in the backlog) can start right away, for example the sample policy documents, the slides, and the competitor scan.

## 8. Questions you may have

**Can I use AI?** Yes, with rules. Read `docs/team/AI_WORKING_GUIDE.md`, and say how you used it in your pull request.

**What if I do not know the skill a task needs?** Say so. The task can change, or you can be paired with someone. Learning tasks are allowed.

**What if the docs contradict each other?** Tell the maintainer. The higher one wins (Decision Log, D35): the Decision Log, then the Final Concept, then the PRD, then the strength documents, then the pitch.

**Where do I write down a decision?** In the Decision Log, through a pull request (`CONTRIBUTING.md`, section 10).

**Who do I ask?** Ask in the issue first, so the answer helps others. If it is urgent or personal, ask the maintainer.

**What is not allowed?** Secrets in the repository, real customer data anywhere, claims we cannot support, and submitting code you cannot explain.
