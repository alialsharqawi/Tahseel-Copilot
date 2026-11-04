#!/usr/bin/env python3
"""Team tools for Tahseel AI: skills-based task assignment and GitHub issue preparation.

Subcommands
  check     validate skills.csv and backlog.csv
  backlog   render docs/team/BACKLOG.md from backlog.csv
  suggest   suggest an assignee and a reviewer for every task (a suggestion, not a decision)
  issues    prepare (dry run) or create (--run) GitHub issues with the gh command line tool

Run from the repository root:  python tools/team_tools.py <subcommand> --help
Only the Python standard library is needed.
"""
import argparse
import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEAM_DIR = ROOT / "docs" / "team"

SIZE_HOURS = {"S": 4, "M": 12, "L": 32}  # rough effort, used only to balance load
TIER_RANK = {"Core": 0, "Should": 1, "Delivery": 2}
META_COLUMNS = {"member", "github", "hours_per_week", "wants_to_learn"}
LEVELS = {0: "none", 1: "learning", 2: "can do alone", 3: "can review and teach"}
AREA_NAMES = {"ai": "AI"}  # proper names for the generated headings


def area_heading(a):
    return AREA_NAMES.get(a, a.capitalize())


# ------------------------------------------------------------------ loading
def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_backlog(team_dir):
    rows = read_csv(team_dir / "backlog.csv")
    tasks = {}
    for r in rows:
        if r["id"] in tasks:
            raise SystemExit(f"backlog.csv: duplicate task ID {r['id']}")
        r["primary"] = [s for s in r["skills_primary"].split(";") if s]
        r["secondary"] = [s for s in r["skills_secondary"].split(";") if s]
        r["deps"] = [s for s in r["depends_on"].split(";") if s]
        tasks[r["id"]] = r
    return tasks


def load_skills(team_dir):
    rows = read_csv(team_dir / "skills.csv")
    members = []
    skill_cols = None
    for r in rows:
        if skill_cols is None:
            skill_cols = [c for c in r.keys() if c not in META_COLUMNS]
        levels, filled = {}, False
        for c in skill_cols:
            v = (r.get(c) or "").strip()
            if v != "":
                filled = True
            try:
                n = int(v) if v != "" else 0
            except ValueError:
                raise SystemExit(f"skills.csv: '{v}' is not a number 0-3 (member {r['member']}, skill {c})")
            if n not in LEVELS:
                raise SystemExit(f"skills.csv: level {n} is outside 0-3 (member {r['member']}, skill {c})")
            levels[c] = n
        try:
            hours = float(r.get("hours_per_week") or 8)
        except ValueError:
            raise SystemExit(f"skills.csv: hours_per_week must be a number (member {r['member']})")
        members.append({
            "name": r["member"].strip(), "github": (r.get("github") or "").strip().lstrip("@"),
            "hours": hours, "learn": {s for s in (r.get("wants_to_learn") or "").split(";") if s},
            "levels": levels, "filled": filled,
        })
    return members, skill_cols or []


def compute_waves(tasks):
    """Wave 1 has no dependencies; a task is one wave after its latest dependency."""
    waves, visiting = {}, set()

    def wave(tid):
        if tid in waves:
            return waves[tid]
        if tid in visiting:
            raise SystemExit(f"backlog.csv: dependency cycle involving {tid}")
        visiting.add(tid)
        w = 1 + max([wave(d) for d in tasks[tid]["deps"]] or [0])
        visiting.discard(tid)
        waves[tid] = w
        return w

    for tid in tasks:
        wave(tid)
    return waves


# ------------------------------------------------------------------ check
def cmd_check(args):
    team = Path(args.team_dir)
    tasks = load_backlog(team)
    errors = []
    for tid, t in tasks.items():
        if t["size"] not in SIZE_HOURS:
            errors.append(f"{tid}: size must be S, M, or L")
        if t["tier"] not in TIER_RANK:
            errors.append(f"{tid}: tier must be Core, Should, or Delivery")
        if not t["primary"]:
            errors.append(f"{tid}: needs at least one primary skill")
    unknown_deps = {d for t in tasks.values() for d in t["deps"] if d not in tasks}
    if unknown_deps:
        errors.extend(f"{tid}: depends on unknown task {d}"
                      for tid, t in tasks.items() for d in t["deps"] if d in unknown_deps)
        errors.append("waves not computed: fix the unknown dependencies above")
    else:
        compute_waves(tasks)  # also raises on a dependency cycle
    msg = f"backlog.csv: {len(tasks)} tasks"
    if (team / "skills.csv").exists():
        members, skill_cols = load_skills(team)
        known = set(skill_cols)
        for t in tasks.values():
            for s in t["primary"] + t["secondary"]:
                if s not in known:
                    errors.append(f"{t['id']}: skill {s} is not a column in skills.csv")
        filled = sum(1 for m in members if m["filled"])
        msg += f"; skills.csv: {len(members)} members, {filled} with skills filled in"
    print(msg)
    if errors:
        print("\n".join("ERROR " + e for e in errors))
        return 1
    print("OK")
    return 0


# ------------------------------------------------------------------ backlog rendering
def cmd_backlog(args):
    team = Path(args.team_dir)
    tasks = load_backlog(team)
    waves = compute_waves(tasks)
    areas = []
    for t in tasks.values():
        if t["area"] not in areas:
            areas.append(t["area"])
    out = ["# Backlog", "",
           "Generated from `backlog.csv` by `python tools/team_tools.py backlog`. Edit the CSV, not this file.", "",
           "**Tiers** (Decision Log, D29): Core is never cut; Should is built after the core slice, in the cut order; "
           "Delivery is scheduled after the core slice works.", "",
           "**Size** is a rough effort guess used only to balance the load: S about half a day, M one to two days, "
           "L three to five days.", "",
           "**Wave** shows the order imposed by dependencies. Wave 1 tasks can start now; later waves wait for their dependencies.", ""]
    counts = {k: sum(1 for t in tasks.values() if t["tier"] == k) for k in TIER_RANK}
    out.append(f"**{len(tasks)} tasks:** {counts['Core']} Core, {counts['Should']} Should, {counts['Delivery']} Delivery.")
    out.append("")
    for a in areas:
        out += [f"## {area_heading(a)}", "", "| ID | Task | Tier | Skills | Size | Wave | Depends on |", "|---|---|---|---|---|---|---|"]
        for t in tasks.values():
            if t["area"] != a:
                continue
            skills = ", ".join(t["primary"]) + (f" (also {', '.join(t['secondary'])})" if t["secondary"] else "")
            out.append(f"| {t['id']} | {t['title']} | {t['tier']} | {skills} | {t['size']} | {waves[t['id']]} | {', '.join(t['deps']) or '-'} |")
        out.append("")
    out += ["## Acceptance criteria and AI tips", "",
            "Each task's acceptance criteria and the references to read first are in `backlog.csv` and are copied into the GitHub issue.", ""]
    (team / "BACKLOG.md").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {team / 'BACKLOG.md'}")
    return 0


# ------------------------------------------------------------------ suggestion
def fit_score(member, task):
    items = [(c, 1.0) for c in task["primary"]] + [(c, 0.5) for c in task["secondary"]]
    num = sum(w * member["levels"].get(c, 0) for c, w in items)
    den = 3 * sum(w for _, w in items)
    return num / den


def min_primary(member, task):
    return min(member["levels"].get(c, 0) for c in task["primary"])


def cmd_suggest(args):
    team = Path(args.team_dir)
    tasks = load_backlog(team)
    if not (team / "skills.csv").exists():
        raise SystemExit(f"skills.csv not found in {team}. Everyone fills in their row first "
                         "(see docs/team/SKILLS_MATRIX.md); then run this command again.")
    members, skill_cols = load_skills(team)
    if not any(m["filled"] for m in members):
        raise SystemExit("skills.csv has no skill levels yet. Everyone fills in their row first "
                         "(put a level from 0 to 3 under every skill column in skills.csv).")
    waves = compute_waves(tasks)
    weeks = args.weeks
    load = {m["name"]: 0.0 for m in members}
    reviews = {m["name"]: 0 for m in members}
    learning = {m["name"]: 0 for m in members}
    result = {}

    order = sorted(tasks.values(), key=lambda t: (TIER_RANK[t["tier"]], waves[t["id"]], -SIZE_HOURS[t["size"]], t["id"]))
    for t in order:
        hours = SIZE_HOURS[t["size"]]
        scored = []
        for idx, m in enumerate(members):
            f, minp = fit_score(m, t), min_primary(m, t)
            cap = max(m["hours"] * weeks, 1)
            adj = f - 0.35 * (load[m["name"]] / cap)
            is_learning = False
            if args.growth and minp == 1 and (set(t["primary"]) & m["learn"]) and learning[m["name"]] < 2:
                adj += 0.12
                is_learning = True
            scored.append((minp >= 1, adj, -idx, f, m, is_learning))
        eligible = [s for s in scored if s[0]]
        best = max(eligible, key=lambda s: (s[1], s[2])) if eligible else max(scored, key=lambda s: (s[3] - 0.35 * load[s[4]["name"]] / max(s[4]["hours"] * weeks, 1), s[2]))
        _, _, _, f, assignee, is_learning = best
        flags = []
        minp = min_primary(assignee, t)

        # a primary skill nobody in the assignee's seat covers: look for a partner who does
        missing = [c for c in t["primary"] if assignee["levels"].get(c, 0) == 0]
        partner = None
        if missing:
            cands = [(sum(m["levels"].get(c, 0) for c in missing), -i, m) for i, m in enumerate(members) if m["name"] != assignee["name"]]
            cands = [c for c in cands if c[0] > 0]
            if cands:
                partner = max(cands, key=lambda c: (c[0], c[1]))[2]
                flags.append(f"pair with {partner['name']} for {', '.join(missing)}, or split the task between you")
            else:
                flags.append(f"NO MATCH: nobody has any knowledge of {', '.join(missing)}; plan training or outside help")

        # reviewer: the partner if there is one, else the best-fitting other member (balanced by review count)
        reviewer = partner
        if reviewer is None:
            others = [(min_primary(m, t) >= 2, fit_score(m, t) - 0.06 * reviews[m["name"]], -i, m)
                      for i, m in enumerate(members) if m["name"] != assignee["name"]]
            if others:
                others.sort(key=lambda s: (s[0], s[1], s[2]), reverse=True)
                reviewer = others[0][3]
                if not others[0][0]:
                    flags.append("no strong reviewer: ask someone outside the team or pair on the review")
        if is_learning:
            learning[assignee["name"]] += 1
            flags.append("learning task: pair with the reviewer")
        elif minp == 1:
            flags.append("stretch: the assignee is still learning a primary skill; pair with the reviewer")
        if load[assignee["name"]] + hours > assignee["hours"] * weeks:
            flags.append("over capacity: first to defer if time is short")
        load[assignee["name"]] += hours
        if reviewer:
            reviews[reviewer["name"]] += 1
        result[t["id"]] = {"assignee": assignee["name"], "reviewer": reviewer["name"] if reviewer else "",
                           "fit": round(f, 2), "flags": "; ".join(flags)}

    # write the editable assignment file
    with open(team / "assignments.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "title", "wave", "tier", "size", "assignee", "reviewer", "fit", "flags", "decision_note"])
        for t in sorted(tasks.values(), key=lambda t: (waves[t["id"]], TIER_RANK[t["tier"]], t["id"])):
            r = result[t["id"]]
            w.writerow([t["id"], t["title"], waves[t["id"]], t["tier"], t["size"], r["assignee"], r["reviewer"], r["fit"], r["flags"], ""])

    total_h = sum(SIZE_HOURS[t["size"]] for t in tasks.values())
    total_cap = sum(m["hours"] * weeks for m in members)
    md = ["# Assignment suggestion", "",
          "Generated by `python tools/team_tools.py suggest`. **This is a suggestion, not a decision.** The maintainer reviews it, "
          "changes `assignments.csv` where needed (and notes why in `decision_note`), and then creates the issues.", "",
          f"Parameters: planning horizon {weeks:g} weeks; growth bonus {'on' if args.growth else 'off'}. "
          "Fit is a number from 0 to 1 built from each member's skill levels (primary skills count fully, secondary skills half). "
          "It describes how well a task matches current skills. It is not a rating of a person.", "",
          f"**Size of the plan:** about {total_h} estimated hours against a capacity of about {int(total_cap)} hours in the horizon "
          f"({total_h / total_cap:.1f} times the capacity). " +
          ("The plan fits." if total_h <= total_cap else
           "The plan is larger than the capacity: tasks flagged *over capacity* are the first to defer, following the cut order in the Decision Log, section E."), ""]
    for wv in range(1, max(waves.values()) + 1):
        rows = [t for t in tasks.values() if waves[t["id"]] == wv]
        if not rows:
            continue
        md += [f"## Wave {wv}", "", "| Task | Title | Tier | Size | Assignee | Reviewer | Fit | Notes |", "|---|---|---|---|---|---|---|---|"]
        for t in sorted(rows, key=lambda t: (TIER_RANK[t["tier"]], t["id"])):
            r = result[t["id"]]
            md.append(f"| {t['id']} | {t['title']} | {t['tier']} | {t['size']} | {r['assignee']} | {r['reviewer']} | {r['fit']} | {r['flags']} |")
        md.append("")
    md += ["## Load per member", "", "| Member | Tasks | S | M | L | Estimated hours | Capacity in horizon | Reviews |", "|---|---|---|---|---|---|---|---|"]
    for m in members:
        mine = [t for t in tasks.values() if result[t["id"]]["assignee"] == m["name"]]
        c = {s: sum(1 for t in mine if t["size"] == s) for s in "SML"}
        md.append(f"| {m['name']} | {len(mine)} | {c['S']} | {c['M']} | {c['L']} | {int(load[m['name']])} | {int(m['hours'] * weeks)} | {reviews[m['name']]} |")
    md += ["", "Estimated hours come from rough size guesses (S 4, M 12, L 32).", ""]
    avg_rev = sum(reviews.values()) / max(len(members), 1)
    heavy = [m["name"] for m in members if avg_rev and reviews[m["name"]] > 1.5 * avg_rev]
    if heavy:
        md += ["Review load is uneven (" + ", ".join(heavy) + " review much more than average). Spread reviews where another member has at least basic knowledge, "
               "and let strong reviewers focus on the risky tasks (security, tenancy, finance formulas).", ""]

    md += ["## Skill coverage", "", "A skill that only one person can do alone is a risk: that person becomes a bottleneck and a single point of failure.", "",
           "| Skill | Members at level 2 or more | Members at level 3 | Tasks needing it (primary) | Note |", "|---|---|---|---|---|"]
    for c in skill_cols:
        n2 = [m["name"] for m in members if m["levels"].get(c, 0) >= 2]
        n3 = [m["name"] for m in members if m["levels"].get(c, 0) >= 3]
        need = sum(1 for t in tasks.values() if c in t["primary"])
        note = ""
        if need and len(n2) == 0:
            note = "NOBODY can do this alone: training or outside help"
        elif need and len(n2) == 1:
            note = "one person only: pair someone with them"
        md.append(f"| {c} | {len(n2)} | {len(n3)} | {need} | {note} |")
    md.append("")

    areas = {}
    for t in tasks.values():
        areas.setdefault(t["area"], set()).update([result[t["id"]]["assignee"], result[t["id"]]["reviewer"]])
    thin = [a for a, s in areas.items() if len({x for x in s if x}) < 2]
    md += ["## Shared knowledge", ""]
    md.append("Every area has at least two people touching it (an assignee and a reviewer)." if not thin else
              "Areas touched by only one person (a risk if that person is away): " + ", ".join(thin) + ".")
    md.append("")
    warn = [(tid, r["flags"]) for tid, r in result.items() if "NO MATCH" in r["flags"]]
    if warn:
        md += ["## Tasks that need attention", ""] + [f"- {tid}: {fl}" for tid, fl in warn] + [""]
    (team / "ASSIGNMENT_SUGGESTION.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {team / 'assignments.csv'} and {team / 'ASSIGNMENT_SUGGESTION.md'}")
    return 0


# ------------------------------------------------------------------ issues
def issue_body(t, assignee, reviewer, wave):
    skills = ", ".join(t["primary"]) + (f" (also: {', '.join(t['secondary'])})" if t["secondary"] else "")
    deps = ", ".join(t["deps"]) if t["deps"] else "none"
    return f"""## Goal
{t['title']}

## Acceptance criteria
{t['acceptance']}

## Read first
{t['refs']}

## Details
- Task ID: {t['id']}  |  Tier: {t['tier']}  |  Size: {t['size']}  |  Wave: {wave}
- Skills: {skills}
- Depends on (task IDs, see the titles): {deps}
- Assignee: {assignee or 'to assign'}  |  Reviewer: {reviewer or 'to assign'}

## How to work on this task
- Step by step: `docs/team/HOW_TO_WORK_ON_A_TASK.md`. Rules: `CONTRIBUTING.md`.
- Working with AI: `docs/team/AI_WORKING_GUIDE.md`. Tip for this task: {t['ai_tip']}
- Stuck for more than two hours? Comment on this issue and tag the reviewer.

## Definition of done
- [ ] Acceptance criteria met and tested
- [ ] Tests pass and the CI check is green
- [ ] Docs updated (and the Decision Log, if a decision changed)
- [ ] No secrets, no real customer data
- [ ] Pull request reviewed and merged; `PROJECT_STATUS.md` updated if the status changed
"""


def cmd_issues(args):
    team = Path(args.team_dir)
    tasks = load_backlog(team)
    waves = compute_waves(tasks)
    members, _ = load_skills(team) if (team / "skills.csv").exists() else ([], [])
    gh = {m["name"]: m["github"] for m in members}
    assign = {}
    if (team / "assignments.csv").exists():
        for r in read_csv(team / "assignments.csv"):
            assign[r["id"]] = (r["assignee"], r["reviewer"])
    selected = [t for t in tasks.values()
                if (not args.wave or waves[t["id"]] <= args.wave)
                and (not args.tier or t["tier"].lower() == args.tier.lower())
                and (not args.only or t["id"] in args.only.split(","))]
    if not selected:
        print("no tasks selected")
        return 1
    for t in sorted(selected, key=lambda t: (waves[t["id"]], t["id"])):
        assignee, reviewer = assign.get(t["id"], ("", ""))
        user = gh.get(assignee, "")
        labels = [f"area:{t['area']}", f"tier:{t['tier'].lower()}", f"size:{t['size']}", f"wave:{waves[t['id']]}"] + [f"skill:{s}" for s in t["primary"]]
        title = f"[{t['id']}] {t['title']}"
        body = issue_body(t, assignee, reviewer, waves[t["id"]])
        cmd = ["gh", "issue", "create", "--title", title, "--body", body, "--label", ",".join(labels)]
        if user:
            cmd += ["--assignee", user]
        if args.run:
            print("creating", title)
            subprocess.run(cmd, check=True)
        else:
            print(f"--- {title}\n    labels: {', '.join(labels)}\n    assignee: {user or '(none: ' + (assignee or 'unassigned') + ' has no github username in skills.csv)'}\n    reviewer: {reviewer or '-'}")
    if not args.run:
        print(f"\nDry run: {len(selected)} issues. Add --run to create them (needs the gh command line tool, logged in).")
    return 0


# ------------------------------------------------------------------ main
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--team-dir", default=str(DEFAULT_TEAM_DIR), help="folder with skills.csv and backlog.csv (default: docs/team)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="validate the CSV files").set_defaults(fn=cmd_check)
    sub.add_parser("backlog", help="render BACKLOG.md").set_defaults(fn=cmd_backlog)
    s = sub.add_parser("suggest", help="suggest assignees and reviewers")
    s.add_argument("--weeks", type=float, default=4, help="planning horizon in weeks (default 4)")
    s.add_argument("--growth", action="store_true", help="give a small bonus to tasks that match a skill a member wants to learn")
    s.set_defaults(fn=cmd_suggest)
    i = sub.add_parser("issues", help="prepare or create GitHub issues")
    i.add_argument("--wave", type=int, help="only tasks up to this wave")
    i.add_argument("--tier", help="Core, Should, or Delivery")
    i.add_argument("--only", help="comma-separated task IDs")
    i.add_argument("--run", action="store_true", help="really create the issues (default is a dry run)")
    i.set_defaults(fn=cmd_issues)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:  # for example when the output is piped into "head"
        try:
            sys.stderr.close()
        except Exception:
            pass
        sys.exit(0)
