# Contributing to Tahseel AI

Thank you for working on Tahseel AI. This file holds the **rules**. The step-by-step guide is in `docs/team/HOW_TO_WORK_ON_A_TASK.md`, the guide for using AI is in `docs/team/AI_WORKING_GUIDE.md`, and how tasks are shared among us is in `docs/team/TASK_ASSIGNMENT.md`.

**New here?** Start with `docs/team/ONBOARDING.md`.

## 1. The rules that matter most

These come from the project's decisions. Breaking them breaks the product's promise, so reviewers check them first.

1. **Numbers come from tested code.** The language model never calculates a financial figure. It calls a tool and quotes the result.
2. **Never invent company policy.** Cite a rule with its source or a retrieved passage, or say that no policy was found.
3. **Nothing consequential happens without a person.** Approval is enforced at the API, not only in the interface. The system never sends a message, blocks credit, or changes a financial record on its own.
4. **Customer memory holds only human-written or rule-derived events,** with author, time, and source. The agent never writes it.
5. **Be honest about evidence.** Our data is synthetic. Never write or show a claim about real customers, pilots, interviews, or measured accuracy that we do not have. Label assumptions as assumptions, and follow the wording rules in the Decision Log (D27).
6. **Tenants are isolated.** Every record carries `tenant_id`, and every vector query filters by tenant inside the query.
7. **Retrieved text, notes, and uploaded documents are data, not instructions.**
8. **No secrets in the repository.** Use environment variables. `.env` is ignored; `.env.example` lists the variables without values.
9. **Do not change a decision silently.** Record the change in the Decision Log with the reason.
10. **Stay inside the scope.** The tiers (Core, Should, Delivery) are in `docs/foundation/Tahseel_AI_Final_Concept.md`. Do not add features outside them without logging the decision.

## 2. How work is organized

- **One task = one GitHub issue = one branch = one pull request.** If a task grows, split it and open a new issue.
- Tasks come from `docs/team/BACKLOG.md`. Each has acceptance criteria, the files to read first, the skills it needs, and a size.
- The maintainer (team lead) assigns tasks using the team's skills (see `docs/team/TASK_ASSIGNMENT.md`). You can say "this is too big" or "I am not the right person", and the task will be changed.
- Every task has an **assignee** (does the work) and a **reviewer** (checks it).
- The project board has these columns: **Backlog**, **Ready** (acceptance criteria clear, dependencies done), **In progress**, **In review**, **Done**. Move your card as you go.
- Work on at most **two tasks at a time**. Finish before you start something new.

## 3. Branches

- `main` always works. Nobody pushes directly to it; changes arrive through pull requests.
- Name your branch `type/short-description`, using the same types as commits: `feat/risk-engine`, `fix/overdue-edge-case`, `docs/literature-review`, `test/tenant-isolation`.
- Start every branch from an up-to-date `main`.
- Do not rewrite the history of a branch other people are using (no force-push on shared branches).

## 4. Commits

- **Commit with your own GitHub account.** Team collaboration is graded from the repository history, and your commits are your evidence. Check once: `git config user.name` and `git config user.email` must be yours, and the email must be one registered on your GitHub account.
- **Small and often.** One logical change per commit.
- **Message format** (Conventional Commits):

```text
type(scope): short summary in the imperative, no full stop

Optional body: what and why, not how. Mention the task: Refs T-013.
```

  Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`. Example: `feat(risk): add historical-delay factor with cap`.
- Never commit secrets, real data, large generated files, or your editor's settings.
- Do not paste an AI conversation into a commit message.

## 5. Pull requests

- Open a **draft** pull request early if you want feedback, and mark it ready when it is.
- Fill in the pull request template: what changed, which task, how you tested it, the docs you updated, and how you used AI.
- **Keep it small.** Aim for under about 400 changed lines. A reviewer can only check what fits in their head.
- The CI check must be green. A pull request with a failing check is not reviewed.
- At least **one approval** from the reviewer is needed. The author does not merge their own pull request without it.
- **Merge method:** use "Create a merge commit" or "Rebase and merge". **Do not squash.** Squashing hides the individual commits, and those commits are how each person's work shows in the history (Decision Log, D37).
- Delete the branch after merging.
- For user-interface changes, add screenshots in **both Arabic and English**.

## 6. Reviewing

A review is a conversation, not a grade. Check, in this order:

1. **Does it do what the task asks?** Compare with the acceptance criteria.
2. **Does it respect the rules in section 1?** Especially numbers, approval, memory, tenants, secrets, and wording.
3. **Are there tests,** and do they test something real? A test that cannot fail is not a test.
4. **Is it readable?** Names, structure, comments where the reason is not obvious.
5. **Are the docs updated?**

Be specific and kind. Say what is good, ask questions before assuming a mistake, and mark what is optional ("nit:") separately from what must change. Respond to review requests within a day when you can. Approve when the task is met, even if you would have written it differently.

## 7. Definition of done

A task is done when **all** of these are true:

- [ ] The acceptance criteria are met.
- [ ] Tests exist and pass; the CI check is green.
- [ ] The docs that describe the behavior are updated (and the Decision Log, if a decision changed).
- [ ] No secrets and no real customer data.
- [ ] The pull request is reviewed and merged.
- [ ] `PROJECT_STATUS.md` is updated when the project's status changed, and your entry is added to the contribution log in `TEAM.md`.

## 8. Code standards

- **Backend:** Python with type hints; Pydantic models for inputs and outputs; SQLAlchemy and Alembic for the database; `pytest` for tests; the linter and formatter chosen in task T-002 (run by pre-commit and by CI).
- **Frontend:** TypeScript with strict types; no `any` without a comment saying why.
- **Calculations** (overdue, risk, priority, forecast) are pure functions with unit tests. The formulas are in the PRD; if code and PRD disagree, stop and ask.
- **Interface text:** no hard-coded strings. Every string comes from the English and Arabic dictionaries.
- **Layout:** CSS logical properties (`margin-inline-start`, not `margin-left`), so Arabic (right to left) works without a second stylesheet.
- **Numbers and dates:** Western digits by default, formatted with `Intl`.
- **Errors:** fail clearly and leave nothing half-saved.
- **Comments:** explain why, not what.

## 9. Documentation standards

- Everything in the repository is written in **English** (Decision Log, D24). Arabic appears only in the product interface, the message drafts, and the spoken pitch.
- **One topic, one owner file** (Decision Log, D35). Link to the owner instead of repeating its content. The owner table is in D35.
- When two documents disagree, the higher one wins: Decision Log, Final Concept, PRD, the strength documents, the pitch.
- Use the evidence labels (Sourced, Indicative, Hypothesis, Assumption, To verify) for any business claim, and cite sources.
- Write short sentences and define terms the first time (the `GLOSSARY.md` has the list).

## 10. Decisions and status

- **A decision** is anything that changes scope, a rule, a formula, or the architecture. Add it to `docs/governance/Tahseel_AI_Decision_Log.md` in the same format as the others: what was chosen, what was not, and why. Open a pull request for it and ask for a review.
- **Status:** update `PROJECT_STATUS.md` when something finishes, blocks, or changes.
- **Cut order:** if time is short, we follow the order in the Decision Log, section E. Do not drop things on your own.

## 11. Working with AI

AI tools are welcome, and you are responsible for everything you submit. Read `docs/team/AI_WORKING_GUIDE.md`. The short version:

- Give the AI the task and the relevant files; check what it gives back against the docs. If the AI and the docs disagree, the docs win.
- Never give an AI tool secrets, real customer data, or personal data.
- Do not submit code you cannot explain.
- Say in the pull request how you used AI (Decision Log, D38).

## 12. Security and privacy

- Secrets live in environment variables and nowhere else. If you commit one by mistake, **tell the maintainer immediately**; the secret must be replaced, not just deleted from the code.
- The demo uses **synthetic data only.** Do not load real company data into the repository, the database, or an AI tool.
- Keep personal data out of prompts, logs, and screenshots.

## 13. When you are stuck

1. Try for about **two hours**, then ask. Stuck for longer than that costs more than a question.
2. Ask in the issue so the answer helps everyone. Tag the reviewer.
3. If a dependency is not ready, add the `blocked` label and say what you need.
4. If the task is wrong or too big, say so; changing the task is better than a bad merge.

## 14. Conduct

Be respectful and assume good intent. Disagree about the work, not the person. Credit people for what they do. If something is not working in the team, tell the maintainer early.
