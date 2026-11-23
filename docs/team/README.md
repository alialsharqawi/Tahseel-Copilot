# Team Folder

Everything about how the team works together. New here? Start with `ONBOARDING.md`.

| File | What it is | Who uses it |
|---|---|---|
| `ONBOARDING.md` | What the project is, where we are, setup checklist, reading path, first week | Every new member |
| `../../CONTRIBUTING.md` | The rules: branches, commits, pull requests, review, definition of done | Everyone |
| `HOW_TO_WORK_ON_A_TASK.md` | Step by step from receiving a task to merging it, with commands and tips | Everyone doing a task |
| `AI_WORKING_GUIDE.md` | How to work with AI tools on a task: prompts, checks, rules | Everyone |
| `ai-coding-agents-guide.html` | Visual guide to the team's coding agents, quota differences, and safe handoffs | Everyone using a coding agent |
| `team-brief-whatsapp.html` | Evergreen team guide with project context, role areas, workflow, safety rules, and contribution shares | Everyone |
| `team-now.html` | Live view of recommended next tasks, dependency readiness, and blocker owners | Everyone |
| `SKILLS_MATRIX.md` | The skills, the 0 to 3 levels, and how to fill in your row | Everyone (once, then updates) |
| `skills.csv` | The team's skills, GitHub usernames, and learning goals | Each person edits their own row |
| `backlog.csv` | The tasks: area, tier, skills, size, dependencies, acceptance criteria | The maintainer |
| `BACKLOG.md` | The backlog in a readable form (generated from `backlog.csv`) | Everyone |
| `TASK_ASSIGNMENT.md` | How tasks are shared by skills, and the rules of the system | The maintainer, and anyone curious |
| `ASSIGNMENT_SUGGESTION.md`, `assignments.csv` | The tool's suggestion and the maintainer's final choices (created when the tool is run) | The maintainer |

Download `team-now.html` from the repository and open it in a browser with internet access. It refreshes public GitHub issue data and the task CSVs; use the project board for the current In progress and In review status.

## The maintainer's routine

```bash
python tools/team_tools.py check                    # validate the files
python tools/team_tools.py backlog                  # refresh BACKLOG.md after editing backlog.csv
python tools/team_tools.py suggest --growth   # suggest assignments
# review ASSIGNMENT_SUGGESTION.md, edit assignments.csv
python tools/team_tools.py issues --wave 1          # dry run
python tools/team_tools.py issues --wave 1 --run    # create the issues
```

More in `tools/README.md`.
