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

Options for `suggest`: `--weeks N` (planning horizon, default 4) and `--growth` (a small bonus for tasks that match a skill someone wants to learn).
Options for `issues`: `--wave N` (tasks up to wave N), `--tier Core|Should|Delivery`, `--only T-013,T-014`, and `--run`.
Use `--team-dir <folder>` to point the tool at another folder with the two CSV files.

### What `suggest` does

It processes tasks in order (Core first, then by dependency wave, larger first). For each task it scores every member:

- **Fit:** the member's skill levels against the task's skills (primary skills count fully, secondary skills half), from 0 to 1.
- **Load:** a penalty that grows with the hours already given to that member compared with their capacity (hours per week times the horizon).
- **Growth:** a small bonus when the task needs a skill the member wants to learn and already has the basics (level 1), at most two such tasks per member.

It then picks the best member who has at least basic knowledge of every primary skill. When a task needs a skill that the assignee lacks, it suggests a **pair** with the person who has it. The reviewer is the best-fitting other member, balanced by how many reviews each person already has.

The result is a **suggestion**. It also reports the size of the plan against the capacity (tasks marked *over capacity* are the first to defer), the load per member, **skill coverage** (skills only one person can do), and areas touched by only one person.

### Try it without real data

```bash
mkdir /tmp/try && cp docs/team/backlog.csv /tmp/try/
cp tools/examples/skills.example.csv /tmp/try/skills.csv
python tools/team_tools.py --team-dir /tmp/try suggest --weeks 8 --growth
```

The example members are made up. Never use the example file for real decisions.

### Creating issues

Requires the GitHub command line tool (`gh`), logged in (`gh auth login`), and the labels loaded once with `bash .github/labels.sh`. Always do a dry run first. The issue assignee comes from the `github` column in `skills.csv`; if it is empty the issue is created without an assignee.

## Not a replacement for judgment

The tool does not know who is on holiday, who is stuck, or who wants a break from a topic. The maintainer decides, and writes the reason for each change in `decision_note` (Decision Log, D37).
