# Working with AI on Your Tasks

AI tools can make you much faster. They can also make you confidently wrong. This guide shows how to get the speed without the risk. The rules behind it are in `CONTRIBUTING.md` (section 11) and the Decision Log (D38).

## 1. Principles

1. **You are responsible for everything you submit.** "The AI wrote it" is not a reason for a bug, a wrong number, or a leaked secret.
2. **Treat the AI like a fast junior colleague.** It works quickly, it knows a lot, it does not know our project, and it sometimes makes things up. You supervise.
3. **If the AI and the docs disagree, the docs win.** The PRD, the Decision Log, and the Final Concept are the source of truth (Decision Log, D35). Do not let an AI "improve" a formula or a rule. If you think a document is wrong, raise it; do not code around it.
4. **Do not submit what you cannot explain.** If a reviewer asks "why is it done this way?" you must be able to answer.
5. **Learn while you use it.** Ask the AI to explain, not only to produce. The goal is that you grow, not that a file appears.

## 2. Set up a session

- **One task per session.** Start a fresh conversation for each task. Long mixed conversations drift and forget.
- **Give the AI the project's context.** In Claude Code, `CLAUDE.md` is read automatically. For other tools, paste it at the start. It contains the non-negotiable rules.
- **Give it the task:** paste the issue (goal, acceptance criteria, "read first").
- **Give it the relevant files,** not the whole repository: the document that owns the topic (for example PRD section 11 for the risk score) and the code you are changing.
- **Tell it what you want first:** "Do not write code yet. Summarize the task in your own words and ask me questions."

## 3. Working with AI, step by step

These steps match `HOW_TO_WORK_ON_A_TASK.md`.

| Step | How to use AI | What you still do yourself |
|---|---|---|
| Understand | Ask it to restate the task, list unclear points, and name the files involved | Read the sources; decide what is unclear |
| Plan | Ask for a plan in small steps and for the risks | Cut the plan down; check it against the acceptance criteria |
| Implement | Ask for one small step at a time; ask for tests first when there is a formula | Read every line; run it; keep the change inside the task |
| Test | Ask it to propose edge cases and to write tests | Check that each test can fail; compare with the formulas |
| Review | Ask it to review your diff for bugs, missing cases, and rule violations | Decide which comments are right |
| Document | Ask it to draft the change description and doc updates | Check that every statement and number is true |

## 4. What to give it, and what never to give it

**Fine to give:**
- The task, the project documents, the code you are changing, error messages and logs (after removing secrets), synthetic data.

**Never give:**
- **Secrets:** API keys, passwords, tokens, the contents of `.env`. If you need a key to test something, use a throwaway key with a spending limit.
- **Real customer or personal data.** Our data is synthetic, and it stays that way.
- Someone else's private messages or files without their permission.

If you pasted a secret by mistake: tell the maintainer at once. The key must be replaced.

## 4a. Prompts you can copy

Replace the parts in angle brackets.

**Understand the task**
```text
Here is my task and the documents it refers to. Do not write code yet.
1) Restate the goal and the acceptance criteria in your own words.
2) List anything unclear or missing.
3) List the files I will probably change.
<paste the issue and the relevant document sections>
```

**Plan**
```text
Propose a plan in at most 7 small steps, each testable on its own. For each step, say
what I can check to know it worked. Point out the riskiest step.
```

**Implement from a formula**
```text
Implement <function> exactly as specified below. Do not change or "improve" the formula.
If something is ambiguous, ask me instead of guessing. Add type hints. Write the
unit tests first, including these edge cases: <list>.
<paste the formula from the PRD>
```

**Write tests**
```text
Write pytest tests for <function>. Include normal cases, boundaries, and invalid input.
Each test must be able to fail. Do not weaken a test to make it pass.
```

**Review my change**
```text
Review this diff against the acceptance criteria and these rules: numbers come from code,
no secrets, tenant filter on every query, approval enforced at the API.
List problems by severity, and say how you would test each one. Do not rewrite the code.
<paste git diff>
```

**Debug**
```text
This test fails with <error>. Here is the code and the test. Explain the most likely
cause first, and tell me how to confirm it, before suggesting a fix.
```

**Explain**
```text
Explain this code to me as if I were new to <topic>. Then give me three questions
to check that I understood it.
```

**Documentation**
```text
Draft the documentation for this change in plain English with short sentences.
Use only facts that appear in the code or in the documents I pasted. Mark anything
you are not sure about with [to verify].
```

**Arabic text**
```text
Review this Arabic interface text for meaning, tone, and consistency with the glossary.
List every change and say why. A native speaker on the team will make the final decision.
```

## 5. Check what it gives you

Before you commit anything the AI produced:

- [ ] **Run it.** Code that was not run is a guess.
- [ ] **Read every line.** Look for things you did not ask for: extra files, changed settings, new dependencies, deleted tests.
- [ ] **Check the facts.** Function names, library versions, and options are sometimes invented. Open the official documentation for anything you do not recognize.
- [ ] **Check numbers and formulas against the docs,** not against the AI's explanation.
- [ ] **Check that the tests can fail.** AI sometimes writes tests that always pass, or "fixes" a failing test by changing the test.
- [ ] **Check the sensitive areas twice,** with a second person: authentication and roles, the tenant filter, the approval gate, the audit log permissions, and anything about prompt injection.
- [ ] **Check the rules in `CONTRIBUTING.md` section 1.**
- [ ] **Check the wording** in anything you write: no claims we cannot support (Decision Log, D27).
- [ ] **Check sources.** If the AI cites a source, a paper, or a link, open it and confirm it exists and says that.
- [ ] **Check licensing.** Do not paste large pieces of someone else's code or text. Write in your own words and cite.

## 6. What AI does well and badly in this project

| Good for | Be careful with |
|---|---|
| Boilerplate: models, schemas, endpoints, configuration files | Our formulas and rules: it may "improve" them |
| Test cases and edge cases | Security and tenancy: it can produce code that looks right and leaks data |
| Explaining unfamiliar code or libraries | Library versions and APIs: it may invent them |
| First drafts of documents, comments, and commit messages | Numbers and sources: it may invent them |
| Reviewing a diff for missed cases | Arabic tone and meaning: needs a native reviewer |
| Generating sample inputs and attack documents for tests | Anything that must be exact: money, dates, permissions |

## 7. Rules specific to this project

- **The product never lets the model calculate.** The same goes for you: do not ask the AI to compute a number that goes into a document, a slide, or a test's expected value. Take it from the code, the generator, or the evaluation.
- **No invented evidence.** In documents, slides, and the pitch, every figure and every source must be real and checked. We use evidence labels. If the AI gives you a statistic, find the source yourself.
- **Synthetic data only,** in every prompt and every file.
- **AI-written Arabic is a draft** until a native speaker reviews it.
- **Do not let an AI agent push to `main`,** merge, or change repository settings. It may help you prepare a commit; you check the diff and make the commit under your own account.
- **Never ask the AI to write the commit history, the contribution log, or the issue comments as if you did the work.** Your history is your evidence.

## 8. Say how you used AI (pull requests)

In every pull request, fill in the "AI use" section (Decision Log, D38):

```text
AI use: <tool and model, or "none">
Used for: <for example: first draft of the tests, explanation of pgvector, review of my diff>
I verified: <what you ran and checked yourself>
```

This is not a confession and nobody is penalized for using AI. It helps the reviewer know where to look harder, and it keeps our work honest.

## 9. Common problems

| Symptom | What to do |
|---|---|
| The AI changes files you did not ask about | Stop. `git diff`, keep what you want, `git restore` the rest. Tell it to touch only the named file |
| It says "done" but never ran anything | Run it yourself. Ask it for the exact command to run and the expected output |
| It loops on the same error | Stop. Restate the error and the code in a fresh session, or ask a person |
| It rewrote a test to make it pass | Revert the test change. The test is the specification |
| It cites a function, option, or paper that you cannot find | Assume it is invented until you find it in the official documentation |
| It gives a long answer you do not follow | Ask for a smaller step, or ask it to explain the first paragraph only |
| The answer contradicts a project document | Follow the document. If you think the document is wrong, tell the maintainer |
| You feel you are accepting code you do not understand | Stop and ask it to explain, or ask a teammate. That is a signal, not a delay |

## 10. Using Claude Code or another coding agent

- Start it from the repository root so it reads `CLAUDE.md`.
- Ask for a plan, approve it, then let it work in small steps.
- Review with `git diff` after each step. Do not accept a large change you have not read.
- Do not give it permission to run destructive commands (`rm -rf`, force-push, resetting history) or to read your `.env`.
- Run the tests yourself before you commit.

## 11. Sharing what works

If you find a prompt or a habit that works well, tell the team. If an AI tool gave a confidently wrong answer about our project, tell the team too. Both help everyone.
