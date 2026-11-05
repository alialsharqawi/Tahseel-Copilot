# How to Work on a Task

A step-by-step guide from receiving a task to merging it. The rules are in `CONTRIBUTING.md`; this file is the practical walk-through, with commands and tips. The guide for using AI during these steps is in `AI_WORKING_GUIDE.md`.

## One-time setup

```bash
# 1. Tell git who you are. This must be YOUR account: your commits are your evidence.
git config --global user.name  "Your Name"
git config --global user.email "the-email-registered-on-your-github-account"

# 2. Get the repository
git clone https://github.com/alialsharqawi/Tahseel-Copilot.git
cd Tahseel-Copilot

# 3. Check that it works
git status
```

Check that the email in step 1 is one of the emails on your GitHub account (GitHub, Settings, Emails). Commits made with another email are not linked to you.

## The steps

### 1. Receive and understand the task

You get a GitHub issue. Read it all: the goal, the **acceptance criteria**, the **files to read first**, the skills, the size, and the **definition of done**.

- Read the files listed under "Read first" before writing anything.
- Write the acceptance criteria in your own words. If you cannot, you do not understand the task yet.
- **Ask questions in the issue now.** A question at the start costs five minutes; a wrong guess costs a day.
- Say "this is too big" or "I am not the right person" if it is true. The task will change.
- Move your card to **In progress**.

### 2. Make a plan

Before coding, write a short plan in a comment on the issue: the steps, the files you will touch, and how you will test it. Three to seven lines is enough. If the plan has more than seven steps, the task is probably too big; ask to split it.

### 3. Create a branch

```bash
git switch main
git pull
git switch -c feat/short-description     # for example feat/risk-engine
```

Use `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, or `ci` as the type.

### 4. Work in small steps

- Do one small thing, check it, then commit. Commit at least once for each step in your plan.
- For code that calculates something, **write the test first** from the formula in the PRD, then the code. The test is your proof.
- Keep your work inside the task. If you notice something else, open a new issue; do not fix it in this branch.
- Run the project's checks often (tests, lint). Fix problems when they are small.

```bash
git add path/to/file other/file             # add files on purpose; avoid "git add ."
git status                                  # check what you are about to commit
git commit -m "feat(risk): add historical-delay factor with cap"
```

Never add `.env`, keys, or real data. If `git status` shows something you did not expect, find out why before committing.

### 5. Test it for real

- Run the tests. Run them again after your last change.
- Try the feature yourself, including the cases that should fail (wrong role, empty data, another tenant).
- For a screen, open it in **English and Arabic** and check that the layout works in both directions.
- Compare with the acceptance criteria one by one and tick them off in the issue.

### 6. Update the docs

If your change affects how something behaves, update the document that **owns** that topic (see the owner table in the Decision Log, D35). If you changed a decision, formula, or scope, add it to the Decision Log. Do not copy text into several files.

### 7. Keep your branch up to date

```bash
git fetch origin
git rebase origin/main       # or: git merge origin/main
```

If git reports a conflict, do not panic and do not delete lines at random. Open the conflicting files, read both sides, keep what both changes need, then:

```bash
git add path/to/fixed/file
git rebase --continue
```

If you are stuck, `git rebase --abort` returns you to where you started. Ask for help.

### 8. Open a pull request

```bash
git push -u origin feat/short-description
```

Then open the pull request on GitHub and fill in the template. A good pull request:

- **Title:** the same style as a commit: `feat(risk): add historical-delay factor`.
- **What and why** in two or three sentences, and `Closes #<issue number>`.
- **How you tested it,** with the commands and what you saw.
- **Screenshots** for screens, in both languages.
- **AI use:** what you used it for and what you checked yourself.
- **Small:** if it is much more than about 400 changed lines, split it.

Open it as a **draft** if you want early feedback. Mark it **ready for review** when you are happy with it, and move the card to **In review**.

### 9. Respond to the review

- Read every comment. Reply to each one, even with just "done".
- If you disagree, explain why and ask. A good reason is welcome.
- Change what was asked, push again, and say what changed.
- Do not take comments personally; they are about the code.

### 10. Merge and finish

- After the approval and a green check, merge with **"Create a merge commit"** or **"Rebase and merge"**. Do not squash.
- Delete the branch.
- Move the card to **Done** and close the issue (the `Closes` line does it).
- Add one line to the contribution log in `TEAM.md`.
- Update `PROJECT_STATUS.md` if the project's status changed.
- Tell the next person if your task unblocks theirs.

## Tips

**Time.** Try for about two hours, then ask. Time-box experiments. Finish one task before starting the next.

**Commits.** A good commit message says what changed and why, in the imperative: "add", not "added". A message like "fix stuff" tells nobody anything.

**Tests.** A test must be able to fail. After writing one, change the code on purpose and check that the test fails.

**Names.** A clear name is better than a comment. If you need a comment to say what something is, rename it.

**Arabic.** Machine-written Arabic is a draft. Have a native speaker review it.

**Numbers.** If you type a number into a document or a slide, ask where it came from. The answer must be the code, the generator, or the evaluation, never your memory.

**Secrets.** If you commit a secret by mistake, tell the maintainer at once. Deleting it from the next commit does not remove it from the history; the key must be replaced.

## Useful commands

```bash
git status                       # what changed
git log --oneline -10            # the last ten commits
git diff                         # what you changed, not yet staged
git diff --staged                # what you are about to commit
git switch -                     # go back to the previous branch
git restore path/to/file         # throw away your changes to one file (careful: it cannot be undone)
git stash / git stash pop        # put changes aside and bring them back
git commit --amend               # fix the last commit (only before you push)
git revert <commit>              # undo a commit by adding a new one (safe after you push)
```

## Common problems

| Problem | What to do |
|---|---|
| "I committed with the wrong email" | Tell the maintainer before you push. Fix the config (step "One-time setup") and ask how to fix the commit |
| "I committed to `main` by mistake" | Do not push. Create a branch from where you are (`git switch -c fix/name`), then ask how to reset `main` |
| "My branch is far behind `main`" | `git fetch origin` and `git rebase origin/main`, step 7 |
| "The CI check fails but it works on my machine" | Read the log of the check; the difference is usually an environment variable, a version, or a file that is not committed |
| "The review is taking too long" | Remind the reviewer in the pull request after a day; then tell the maintainer |
| "I do not understand a decision in the docs" | Read the Decision Log entry for it; if it is still unclear, ask in the issue |
