# Tools

## team_tools.py: skills-based assignment

A small command line tool for the maintainer. It uses only the Python standard library (Python 3.9 or newer). Run it from the repository root.

```bash
python tools/team_tools.py <command> [options]
```

| Command | What it does |
|---|---|
| `check` | Validates `docs/team/backlog.csv` and `docs/team/skills.csv`: sizes, tiers, dependencies (no unknown tasks, no cycles), skill codes, and levels 0 to 3 |
| `backlog` | Writes `docs/team/BACKLOG.md` from `backlog.csv`, with the dependency waves |
| `suggest` | Suggests an assignee and a reviewer for every task and writes `docs/team/assignments.csv` and `docs/team/ASSIGNMENT_SUGGESTION.md` |
| `issues` | Prints (dry run) or creates (`--run`) one GitHub issue per task, with labels, assignee, and the standard body |

Options for `suggest`: `--growth` (a small bonus for tasks that match a skill someone wants to learn).
Options for `issues`: `--wave N` (tasks up to wave N), `--tier Core|Should|Delivery`, `--only T-013,T-014`, and `--run`.
Use `--team-dir <folder>` to point the tool at another folder with the two CSV files.
Run the focused issue-body formatting test with `python -m unittest tools.test_team_tools`.
Run the synthetic policy corpus validation with `python -m unittest tools.test_policy_corpus`.

## build_docs_pdf.py: the LMS documentation PDF

Builds one PDF from the Markdown parts in `docs/lms/parts/` and **overwrites `Tahseel_Project_Documentation_v1.pdf` in the repository root.** The LMS submission links to that file, so never rename or move it.

```bash
pip install markdown                      # plus ONE of: pip install weasyprint, or a Chrome / Chromium / Brave browser
python tools/build_docs_pdf.py --check                  # list the parts and check the images; build nothing
python tools/build_docs_pdf.py --output /tmp/try.pdf    # a trial build that does not touch the real PDF
python tools/build_docs_pdf.py                          # overwrite the root PDF (the old one is backed up to _private/pdf_backups)
```

The cover, the contents, and the pages come from the parts, in order. Wide diagrams and the wireframes get landscape pages. Always open the result and check it before you commit it.

### What `suggest` does

It processes tasks in order (Core first, then by dependency wave, larger first). For each task it scores every member:

- **Fit:** the member's skill levels against the task's skills (primary skills count fully, secondary skills half), from 0 to 1.
- **Participation:** a bonus for a member who is below a fair share of the plan's task count and complexity, so work does not pile up on a few people.
- **Wave coverage:** a small bonus when the task would give the member work in a wave they do not have yet.
- **Growth:** a small bonus when the task needs a skill the member wants to learn and already has the basics (level 1), at most two such tasks per member.

It then picks the best member who has at least basic knowledge of every primary skill, and keeps anyone from going far above a fair share unless no one else is eligible. A rebalancing pass moves work to an under-participating member, and a second pass handles sensitive tasks where the only strong reviewer is also the natural assignee: the task is **paired**, another member does it, and the strong member reviews.

The reviewer is the best-fitting other member, balanced by how many reviews each person already has. Sensitive tasks keep a reviewer at level 2 or more.

The result is a **suggestion**. It reports **participation per member** (tasks, sizes, complexity, share, waves, reviews), a **full-participation check**, **skill coverage** (skills only one person can do), areas touched by only one person, and the tasks that need attention.

There is **no hourly capacity model**. Size is relative complexity (S=1, M=2, L=3), not a time estimate. The calendar is the fixed 15 December 2026 defense.

### Try it without real data

```bash
mkdir /tmp/try && cp docs/team/backlog.csv /tmp/try/
cp tools/examples/skills.example.csv /tmp/try/skills.csv
python tools/team_tools.py --team-dir /tmp/try suggest --growth
```

The example members are made up. Never use the example file for real decisions.

### Creating issues

Requires the GitHub command line tool (`gh`), logged in (`gh auth login`), and the labels loaded once with `bash .github/labels.sh`. Always do a dry run first. The issue assignee comes from the `github` column in `skills.csv`; if it is empty the issue is created without an assignee. With `--run`, the tool reads the existing issues first and skips any task ID that already has one, so a re-run does not create duplicates.

## Not a replacement for judgment

The tool does not know who is on holiday, who is stuck, or who wants a break from a topic. The maintainer decides, and writes the reason for each change in `decision_note` (Decision Log, D37).
