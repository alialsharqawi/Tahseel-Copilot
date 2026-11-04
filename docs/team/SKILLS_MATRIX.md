# Skills Matrix

The skills matrix is how the team knows who can do what, so tasks go to the right people (see `TASK_ASSIGNMENT.md`). Everyone fills in their own row in `docs/team/skills.csv`.

**This is not an evaluation.** Nobody is graded on it, and a low number is not a failing. It is a snapshot of today that helps us give you tasks you can do, tasks you can grow in, and a reviewer who can help. Be honest: a wrong high number leads to a task that is too hard, and a wrong low number leads to wasted skills.

## 1. The levels

| Level | Meaning | In practice |
|---:|---|---|
| 0 | None | I have not used it, or I would not know where to start |
| 1 | Learning | I know the basics and can do it with help or a guide |
| 2 | Can do alone | I can do typical tasks on my own and fix my own mistakes |
| 3 | Can review and teach | I can review someone else's work, handle hard cases, and teach it |

Leave a cell empty if you are not sure; it counts as 0. If you are between two levels, choose the lower one, and mention it in your learning goals.

## 2. The skills

The "Tasks" columns show how many backlog tasks need the skill as a primary skill and as a secondary skill (computed from `backlog.csv`).

| Code | Skill | What it means here | Primary | Secondary |
|---|---|---|---:|---:|
| `GIT` | Git and GitHub workflow | Branches, pull requests, resolving conflicts, protected branches | 3 | 2 |
| `PY` | Python | Writing clean Python, functions, typing, packaging | 19 | 5 |
| `API` | FastAPI and REST API design | Endpoints, validation with Pydantic, status codes, auth in APIs | 8 | 5 |
| `DB` | PostgreSQL, SQL, migrations | Schemas, queries, SQLAlchemy, Alembic, indexes | 5 | 4 |
| `LLM` | LLM integration and prompting | Calling a model, tool calling, structured output, prompt design | 7 | 0 |
| `VEC` | Embeddings, pgvector, retrieval (RAG) | Chunking, embeddings, similarity search, citations | 3 | 0 |
| `EVAL` | Evaluating AI systems | Building test sets, measuring answers, comparing setups honestly | 2 | 0 |
| `FE` | React, Next.js, TypeScript | Components, state, calling an API, building screens | 7 | 0 |
| `UX` | UI and UX design, accessibility, RTL | Layout, wireframes, accessibility, right-to-left design | 5 | 3 |
| `DATA` | Data wrangling and generation | pandas, Excel and CSV files, generating realistic data | 4 | 3 |
| `QA` | Test design and pytest | Writing tests that can fail, edge cases, test data | 5 | 6 |
| `SEC` | Security basics | Authentication, roles, tenant isolation, secrets, injection | 5 | 1 |
| `DEVOPS` | Docker, CI, deployment | Docker Compose, GitHub Actions, HTTPS, environment config | 3 | 1 |
| `DOC` | Technical writing in English | Clear documentation, specifications, README files | 5 | 3 |
| `BIZ` | Business analysis and research | Market research, competitor analysis, interviews, sourcing claims | 2 | 2 |
| `PRES` | Presentation and video | Slides, storytelling, recording a demo | 2 | 1 |
| `AR` | Arabic language (native level) | Reviewing Arabic text for meaning and tone, writing Arabic drafts | 3 | 0 |

## 3. How to fill in your row

Open `docs/team/skills.csv` and fill in your row:

| Column | What to write |
|---|---|
| `member` | Your name (already there; correct it if needed) |
| `github` | Your GitHub username, without the @. Needed to assign you issues |
| `hours_per_week` | Hours you can honestly give to this project each week, for example `8`. Include study and other commitments in your thinking |
| `wants_to_learn` | Skill codes you want to practice, separated by `;`, for example `FE;QA`. Maximum three |
| Skill columns | A number from 0 to 3 for each skill |

Example row:

```text
member,github,hours_per_week,wants_to_learn,GIT,PY,API,DB,LLM,VEC,EVAL,FE,UX,DATA,QA,SEC,DEVOPS,DOC,BIZ,PRES,AR
Sara Ali,saraali,8,VEC;EVAL,2,2,1,1,2,0,0,0,0,2,1,0,0,2,1,1,3
```

Send the change as a pull request (`docs(team): add my skills`). The maintainer reviews it.

## 4. How it is used

- The tool compares each task's required skills with your levels to suggest who should take it.
- If you list a skill under `wants_to_learn` and you are at level 1, you may get a task in it with a stronger reviewer.
- Skills that only one person has at level 2 or more are flagged, so we can pair someone with that person.
- Your hours set how many tasks you are suggested.

## 5. Keeping it up to date

Update your row when you learn something, about every two weeks or after a big task. Growth is the point: a number that never changes means we are not learning. Changes go through a pull request like any other file.

## 6. Privacy

The matrix lives in the team's repository. Do not write anything about yourself that you would not want your teammates to read.
