#!/usr/bin/env python3
"""Team tools for Tahseel AI: skill-weighted, full-participation assignment and GitHub issue preparation.

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
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEAM_DIR = ROOT / "docs" / "team"

# Relative complexity, NOT hours. Used only to balance the size of tasks across members.
SIZE_WEIGHT = {"S": 1, "M": 2, "L": 3}
TIER_RANK = {"Core": 0, "Should": 1, "Delivery": 2}
META_COLUMNS = {"member", "github", "wants_to_learn"}
LEGACY_COLUMNS = {"hours_per_week"}  # ignored if an old copy of skills.csv still has it
LEVELS = {0: "none", 1: "learning", 2: "can do alone", 3: "can review and teach"}
AREA_NAMES = {"ai": "AI"}  # proper names for the generated headings

# Tasks where a mistake is expensive. The reviewer should be able to do the
# primary skill alone (level 2 or more), as required by D37.
HIGH_RISK_TASKS = {"T-011", "T-012", "T-014", "T-015", "T-049", "T-050", "T-072"}
RISK_SKILLS = {"SEC"}


def area_heading(a):
    return AREA_NAMES.get(a, a.capitalize())


def clamp(value, low, high):
    return max(low, min(high, value))


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
            skill_cols = [c for c in r.keys() if c not in META_COLUMNS and c not in LEGACY_COLUMNS]
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
        name = (r.get("member") or "").strip()
        if not name:
            raise SystemExit("skills.csv: a row has no member name")
        members.append({
            "name": name,
            "github": (r.get("github") or "").strip().lstrip("@"),
            "learn": {s for s in (r.get("wants_to_learn") or "").split(";") if s},
            "levels": levels,
            "filled": filled,
        })
    if not members:
        raise SystemExit("skills.csv: no members found")
    names = [m["name"] for m in members]
    if len(names) != len(set(names)):
        raise SystemExit("skills.csv: duplicate member names")
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
        if t["size"] not in SIZE_WEIGHT:
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
    warnings = []
    if (team / "skills.csv").exists():
        members, skill_cols = load_skills(team)
        known = set(skill_cols)
        for t in tasks.values():
            for s in t["primary"] + t["secondary"]:
                if s not in known:
                    errors.append(f"{t['id']}: skill {s} is not a column in skills.csv")
        for m in members:
            if not m["github"]:
                warnings.append(f"skills.csv: {m['name']} has no GitHub username; the issue cannot be assigned")
        filled = sum(1 for m in members if m["filled"])
        msg += f"; skills.csv: {len(members)} members, {filled} with skills filled in"
        if any("hours_per_week" in r for r in read_csv(team / "skills.csv")):
            msg += " (legacy hours_per_week column ignored; remove it)"
    print(msg)
    if warnings:
        print("\n".join("WARNING " + w for w in warnings))
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
           "**Size** is a relative complexity label, not a time estimate: S is small, M is medium, L is large. "
           "The assignment tool uses weights 1, 2, and 3 only to balance complexity across the team.", "",
           "**Wave** shows the order imposed by dependencies. Wave 1 tasks can start now; later waves wait for their dependencies.", "",
           "**Participation** (D41): every member is expected to take a meaningful share of the plan and work across waves. "
           "No weekly-hours or capacity model is used.", ""]
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


def missing_primary(member, task):
    return [c for c in task["primary"] if member["levels"].get(c, 0) == 0]


def is_high_risk(task):
    return task["id"] in HIGH_RISK_TASKS or bool(set(task["primary"]) & RISK_SKILLS)


def rebalance_assignments(tasks, members, result, waves, fair_weight, assigned_weight,
                          assigned_count, member_waves):
    """Move tasks from members above the fair share to a member who is far below it.

    This is a safety net for the greedy pass. It never moves a task to someone
    with no basic knowledge of every primary skill, and it keeps the fit loss small.
    """
    by_name = {m["name"]: m for m in members}
    for _ in range(len(tasks) * 2):
        under = [m for m in members
                 if assigned_count[m["name"]] == 0 or assigned_weight[m["name"]] < 0.85 * fair_weight]
        if not under:
            break
        under_m = min(under, key=lambda m: (assigned_weight[m["name"]], assigned_count[m["name"]]))
        best = None
        for tid, r in result.items():
            donor = r["assignee"]
            if donor == under_m["name"] or r.get("pair_with"):
                continue
            if assigned_weight[donor] <= fair_weight * 1.05:
                continue
            t = tasks[tid]
            weight = SIZE_WEIGHT[t["size"]]
            if assigned_weight[under_m["name"]] + weight > fair_weight * 1.1:
                continue
            if min_primary(under_m, t) < 1:
                continue
            loss = fit_score(by_name[donor], t) - fit_score(under_m, t)
            if best is None or loss < best[0]:
                best = (loss, tid, donor)
        if best is None:
            break
        _, tid, donor = best
        weight = SIZE_WEIGHT[tasks[tid]["size"]]
        result[tid]["assignee"] = under_m["name"]
        assigned_weight[donor] -= weight
        assigned_count[donor] -= 1
        assigned_weight[under_m["name"]] += weight
        assigned_count[under_m["name"]] += 1
        member_waves[under_m["name"]].add(waves[tid])
    # Recompute wave coverage after all moves.
    for name in member_waves:
        member_waves[name].clear()
    for tid, r in result.items():
        member_waves[r["assignee"]].add(waves[tid])


def rebalance_overloaded(tasks, members, result, waves, fair_weight, max_weight, max_count,
                         assigned_weight, assigned_count, member_waves, locked=None):
    """Move non-forced tasks away from a member who is above the cap.

    A task is forced when no other member has basic knowledge of every primary
    skill. Forced tasks stay with their owner; the rest move to an eligible
    member who is below the cap, preferring someone below the fair share and
    the smallest fit loss. Tasks in ``locked`` (for example a security pairing)
    are never moved.
    """
    by_name = {m["name"]: m for m in members}
    locked = locked or set()
    for _ in range(len(tasks) * 2):
        over = [m for m in members
                if assigned_weight[m["name"]] > max_weight or assigned_count[m["name"]] > max_count]
        if not over:
            break
        donor_m = max(over, key=lambda m: (assigned_weight[m["name"]], assigned_count[m["name"]]))
        donor = donor_m["name"]
        candidates = []
        for tid, r in result.items():
            if r["assignee"] != donor or tid in locked:
                continue
            t = tasks[tid]
            weight = SIZE_WEIGHT[t["size"]]
            for m in members:
                if m["name"] == donor:
                    continue
                if min_primary(m, t) < 1:
                    continue
                if assigned_weight[m["name"]] + weight > max_weight:
                    continue
                if assigned_count[m["name"]] + 1 > max_count:
                    continue
                under_fair = assigned_weight[m["name"]] < fair_weight
                loss = fit_score(donor_m, t) - fit_score(m, t)
                candidates.append((not under_fair, loss, -(fair_weight - assigned_weight[m["name"]]), tid, m["name"]))
        if not candidates:
            break
        _, _, _, tid, recipient = min(candidates)
        weight = SIZE_WEIGHT[tasks[tid]["size"]]
        result[tid]["assignee"] = recipient
        assigned_weight[donor] -= weight
        assigned_count[donor] -= 1
        assigned_weight[recipient] += weight
        assigned_count[recipient] += 1
        member_waves[recipient].add(waves[tid])
    for name in member_waves:
        member_waves[name].clear()
    for tid, r in result.items():
        member_waves[r["assignee"]].add(waves[tid])


def pair_sole_expert_tasks(tasks, members, result, waves, fair_weight,
                           assigned_weight, assigned_count, member_waves):
    """Turn a task with only one strong member into a paired task.

    When the only member who can do a task's primary skills alone is also its
    assignee, move the task to another member who has at least the basics, and
    let the strong member review it. This spreads knowledge, gives the strong
    member a review instead of all the work, and removes the review deadlock.
    The pair is flagged in the report so the risk is visible.

    A non-sensitive task stays with the strong member while that member is at or
    below a fair share of the plan; otherwise the strong member would end up
    with reviews only. Sensitive tasks are always paired.
    """
    by_name = {m["name"]: m for m in members}
    for tid, t in tasks.items():
        assignee = by_name[result[tid]["assignee"]]
        if min_primary(assignee, t) < 2:
            continue
        if not is_high_risk(t) and assigned_weight[assignee["name"]] <= fair_weight:
            continue
        other_strong = [m for m in members
                        if m["name"] != assignee["name"] and min_primary(m, t) >= 2]
        if other_strong:
            continue
        candidates = [m for m in members
                      if m["name"] != assignee["name"]
                      and any(m["levels"].get(c, 0) >= 1 for c in t["primary"])]
        if not candidates:
            continue
        new = max(candidates, key=lambda m: (fit_score(m, t), -assigned_weight[m["name"]]))
        weight = SIZE_WEIGHT[t["size"]]
        result[tid]["assignee"] = new["name"]
        result[tid]["pair_with"] = assignee["name"]
        assigned_weight[assignee["name"]] -= weight
        assigned_count[assignee["name"]] -= 1
        assigned_weight[new["name"]] += weight
        assigned_count[new["name"]] += 1
        member_waves[new["name"]].add(waves[tid])
    for name in member_waves:
        member_waves[name].clear()
    for tid, r in result.items():
        member_waves[r["assignee"]].add(waves[tid])


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
    if len(members) < 2:
        raise SystemExit("skills.csv needs at least two members so every task has a different reviewer.")
    waves = compute_waves(tasks)
    by_name = {m["name"]: m for m in members}

    total_weight = sum(SIZE_WEIGHT[t["size"]] for t in tasks.values())
    fair_weight = total_weight / len(members)
    target_count = len(tasks) / len(members)
    # No one should run away with the plan. A member may go a little above the
    # fair share, but not above this cap unless a task has no other eligible member.
    max_count = max(1, int(target_count * 1.2 + 0.999))
    max_weight = fair_weight * 1.25
    assigned_weight = {m["name"]: 0 for m in members}
    assigned_count = {m["name"]: 0 for m in members}
    member_waves = {m["name"]: set() for m in members}
    learning = {m["name"]: 0 for m in members}
    learning_owner = {}
    result = {}

    order = sorted(tasks.values(),
                   key=lambda t: (TIER_RANK[t["tier"]], waves[t["id"]], -SIZE_WEIGHT[t["size"]], t["id"]))
    for t in order:
        weight = SIZE_WEIGHT[t["size"]]
        scored = []
        for idx, m in enumerate(members):
            f = fit_score(m, t)
            minp = min_primary(m, t)
            # Positive when the member is below a fair share of task count and complexity.
            gap_weight = clamp((fair_weight - assigned_weight[m["name"]]) / max(fair_weight, 1), -0.6, 1.0)
            gap_count = clamp((target_count - assigned_count[m["name"]]) / max(target_count, 1), -0.6, 1.0)
            participation = 0.95 * gap_weight + 0.30 * gap_count
            # Small bonus for a member who has no task in this wave yet: spread work across waves.
            wave_bonus = 0.06 if waves[t["id"]] not in member_waves[m["name"]] else 0.0
            is_learning = False
            if args.growth and minp == 1 and (set(t["primary"]) & m["learn"]) and learning[m["name"]] < 2:
                is_learning = True
            growth = 0.10 if is_learning else 0.0
            at_cap = assigned_count[m["name"]] >= max_count or assigned_weight[m["name"]] >= max_weight
            scored.append((minp >= 1, not at_cap, f + participation + wave_bonus + growth, -idx, f, m, is_learning))
        # Prefer an eligible member who is not at the cap. If every eligible member is at the
        # cap, allow one of them (a task must still be assigned). If nobody is eligible, take
        # the best fit and flag it later.
        pool = [s for s in scored if s[0] and s[1]]
        if not pool:
            pool = [s for s in scored if s[0]]
        if not pool:
            pool = scored
        best = max(pool, key=lambda s: (s[2], s[3]))
        _, _, _, _, f, assignee, is_learning = best
        name = assignee["name"]
        result[t["id"]] = {"assignee": name, "reviewer": "", "fit": round(f, 2), "flags": [], "pair_with": ""}
        if is_learning:
            learning[name] += 1
            learning_owner[t["id"]] = name
        assigned_weight[name] += weight
        assigned_count[name] += 1
        member_waves[name].add(waves[t["id"]])

    rebalance_assignments(tasks, members, result, waves, fair_weight,
                          assigned_weight, assigned_count, member_waves)
    rebalance_overloaded(tasks, members, result, waves, fair_weight, max_weight, max_count,
                         assigned_weight, assigned_count, member_waves)
    pair_sole_expert_tasks(tasks, members, result, waves, fair_weight,
                           assigned_weight, assigned_count, member_waves)
    locked = {tid for tid, r in result.items() if r.get("pair_with")}
    rebalance_overloaded(tasks, members, result, waves, fair_weight, max_weight, max_count,
                         assigned_weight, assigned_count, member_waves, locked=locked)
    # The cap pass can move a task back to the only strong member.
    # Pair it once more, then leave the final distribution alone.
    pair_sole_expert_tasks(tasks, members, result, waves, fair_weight,
                           assigned_weight, assigned_count, member_waves)

    # Recompute the flags against the final assignee, then choose reviewers.
    for tid, t in tasks.items():
        r = result[tid]
        assignee = by_name[r["assignee"]]
        flags = []
        if tid in learning_owner and learning_owner[tid] == r["assignee"]:
            flags.append("learning task: pair with the reviewer")
        if min_primary(assignee, t) == 1:
            flags.append("stretch: the assignee is still learning a primary skill; pair with the reviewer")
        missing = missing_primary(assignee, t)
        if r.get("pair_with"):
            risky = sorted(set(t["primary"] + t["secondary"]) & RISK_SKILLS)
            paired_on = ", ".join(missing or risky) if (missing or risky) else "the primary skill"
            flags.append(f"paired with {r['pair_with']} on {paired_on}; {r['pair_with']} reviews and can do it alone")
        elif missing:
            flags.append(f"NO MATCH: the assignee has no knowledge of {', '.join(missing)}; pair with someone who does")
        r["flags"] = flags
        r["fit"] = round(fit_score(assignee, t), 2)

    reviews = {m["name"]: 0 for m in members}
    for tid, t in tasks.items():
        assignee = by_name[result[tid]["assignee"]]
        if result[tid].get("pair_with"):
            reviewer_name = result[tid]["pair_with"]
            result[tid]["reviewer"] = reviewer_name
            reviews[reviewer_name] += 1
            continue
        missing = missing_primary(assignee, t)
        high_risk = is_high_risk(t)
        candidates = []
        for idx, m in enumerate(members):
            if m["name"] == assignee["name"]:
                continue
            minp = min_primary(m, t)
            covers_missing = all(m["levels"].get(c, 0) > 0 for c in missing) if missing else True
            strong = minp >= 2
            strong_enough = strong if high_risk else True
            # Spread reviews: a strong reviewer should not review everything.
            score = fit_score(m, t) - 0.12 * reviews[m["name"]]
            candidates.append((strong_enough, covers_missing, strong, score, -idx, m))
        if not candidates:
            continue
        candidates.sort(key=lambda c: (c[0], c[1], c[2], c[3], c[4]), reverse=True)
        best = candidates[0]
        reviewer = best[5]
        result[tid]["reviewer"] = reviewer["name"]
        reviews[reviewer["name"]] += 1
        if high_risk and not best[2]:
            result[tid]["flags"].append("high-risk review: the reviewer is below level 2 in a primary skill")
        elif not best[2]:
            result[tid]["flags"].append("no strong reviewer: ask someone outside the team or pair on the review")

    # write the editable assignment file
    with open(team / "assignments.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "title", "wave", "tier", "size", "assignee", "reviewer", "fit", "flags", "decision_note"])
        for t in sorted(tasks.values(), key=lambda t: (waves[t["id"]], TIER_RANK[t["tier"]], t["id"])):
            r = result[t["id"]]
            w.writerow([t["id"], t["title"], waves[t["id"]], t["tier"], t["size"], r["assignee"], r["reviewer"],
                        r["fit"], "; ".join(r["flags"]), ""])

    md = ["# Assignment suggestion", "",
          "Generated by `python tools/team_tools.py suggest`. **This is a suggestion, not a decision.** The maintainer reviews it, "
          "changes `assignments.csv` where needed (and notes why in `decision_note`), and then creates the issues.", "",
          "Parameters: growth bonus " + ("on" if args.growth else "off") + ". "
          "Fit is a number from 0 to 1 built from each member's skill levels (primary skills count fully, secondary skills half). "
          "It describes how well a task matches current skills. It is not a rating of a person.", "",
          "**No hourly capacity model.** Size is a relative complexity label (S=1, M=2, L=3), not a time estimate. "
          "The tool balances task count and complexity, and gives every member a meaningful share of the plan. "
          "The calendar is set by the **15 December 2026** defense; the team works flexibly and uses AI assistance.", "",
          "**Review load (D42):** Ali accepts a higher review share as team leader. "
          "Skill fit takes priority over equal review counts; manual decisions are recorded in `assignments.csv`.", "",
          f"**Plan shape:** {len(tasks)} tasks, {total_weight} complexity points. "
          f"Target per member: about {target_count:.1f} tasks / {fair_weight:.1f} points.", ""]
    for wv in range(1, max(waves.values()) + 1):
        rows = [t for t in tasks.values() if waves[t["id"]] == wv]
        if not rows:
            continue
        md += [f"## Wave {wv}", "", "| Task | Title | Tier | Size | Assignee | Reviewer | Fit | Notes |",
               "|---|---|---|---|---|---|---|---|"]
        for t in sorted(rows, key=lambda t: (TIER_RANK[t["tier"]], t["id"])):
            r = result[t["id"]]
            notes = "; ".join(r["flags"])
            md.append(f"| {t['id']} | {t['title']} | {t['tier']} | {t['size']} | {r['assignee']} | "
                      f"{r['reviewer']} | {r['fit']} | {notes} |")
        md.append("")

    md += ["## Participation per member", "",
           "| Member | Tasks | S | M | L | Complexity | Share | Waves covered | Reviews |",
           "|---|---|---|---|---|---|---|---|---|"]
    for m in members:
        name = m["name"]
        mine = [t for t in tasks.values() if result[t["id"]]["assignee"] == name]
        c = {s: sum(1 for t in mine if t["size"] == s) for s in "SML"}
        share = 100 * assigned_weight[name] / total_weight if total_weight else 0
        md.append(f"| {name} | {len(mine)} | {c['S']} | {c['M']} | {c['L']} | {assigned_weight[name]} | "
                  f"{share:.1f}% | {len(member_waves[name])} | {reviews[name]} |")
    md += ["", "Complexity points are relative (S=1, M=2, L=3). They are not hours.", ""]

    thin = [m for m in members
            if assigned_count[m["name"]] == 0 or assigned_weight[m["name"]] < 0.5 * fair_weight]
    single_wave = [m for m in members if len(member_waves[m["name"]]) < 2]
    md += ["## Full-participation check", ""]
    if not thin and not single_wave:
        md.append("Every member has a meaningful share of the plan and works across at least two waves.")
    else:
        if thin:
            md.append("Under-participating members (less than half the fair complexity share or no tasks): " +
                      ", ".join(m["name"] for m in thin) + ". Move a task to them in `assignments.csv` or check their skills.")
        if single_wave:
            md.append("Members with tasks in only one wave: " + ", ".join(m["name"] for m in single_wave) +
                      ". Spread at least one task into another wave where they have basic knowledge.")
    md.append("")

    md += ["## Skill coverage", "",
           "A skill that only one person can do alone is a risk: that person becomes a bottleneck and a single point of failure.", "",
           "| Skill | Members at level 2 or more | Members at level 3 | Tasks needing it (primary) | Note |",
           "|---|---|---|---|---|"]
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
    thin_areas = [a for a, s in areas.items() if len({x for x in s if x}) < 2]
    md += ["## Shared knowledge", ""]
    md.append("Every area has at least two people touching it (an assignee and a reviewer)." if not thin_areas else
              "Areas touched by only one person (a risk if that person is away): " + ", ".join(thin_areas) + ".")
    md.append("")

    attention = [(tid, r["flags"]) for tid, r in result.items()
                 if any("NO MATCH" in f or "high-risk" in f or "no strong reviewer" in f or "paired with" in f
                        for f in r["flags"])]
    if attention:
        md += ["## Tasks that need attention", ""]
        for tid, flags in attention:
            md.append(f"- {tid}: {'; '.join(flags)}")
        md.append("")
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
- Task ID: {t['id']}  |  Tier: {t['tier']}  |  Size (relative complexity): {t['size']}  |  Wave: {wave}
- Skills: {skills}
- Depends on (task IDs, see the titles): {deps}
- Assignee: {assignee or 'to assign'}  |  Reviewer: {reviewer or 'to assign'}

## How to work on this task
- Step by step: `docs/team/HOW_TO_WORK_ON_A_TASK.md`. Rules: `CONTRIBUTING.md`.
- Working with AI: `docs/team/AI_WORKING_GUIDE.md`. Tip for this task: {t['ai_tip']}
- Stuck? Comment on this issue and tag the reviewer. Time-box experiments.
- Every member contributes (D41). If this task does not fit your current focus, say so in the issue; the maintainer will rebalance.

## Definition of done
- [ ] Acceptance criteria met and tested
- [ ] Tests pass and the CI check is green
- [ ] Docs updated (and the Decision Log, if a decision changed)
- [ ] No secrets, no real customer data
- [ ] Pull request reviewed and merged; `PROJECT_STATUS.md` updated if the status changed
"""


def existing_issue_ids():
    """Return the task IDs that already have an issue, so a re-run does not create duplicates."""
    try:
        out = subprocess.run(
            ["gh", "issue", "list", "--state", "all", "--limit", "500", "--json", "title"],
            capture_output=True, text=True, check=True,
        ).stdout
        ids = set()
        for item in json.loads(out):
            match = re.match(r"\[(T-\d+)\]", item.get("title", ""))
            if match:
                ids.add(match.group(1))
        return ids
    except Exception as exc:  # gh missing, not logged in, or a network error
        print(f"warning: could not read existing issues ({exc}); duplicates are possible")
        return set()


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
    existing = existing_issue_ids() if args.run else set()
    created = skipped = 0
    for t in sorted(selected, key=lambda t: (waves[t["id"]], t["id"])):
        if t["id"] in existing:
            print(f"skipping {t['id']}: an issue already exists")
            skipped += 1
            continue
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
            created += 1
        else:
            print(f"--- {title}\n    labels: {', '.join(labels)}\n    assignee: {user or '(none: ' + (assignee or 'unassigned') + ' has no github username in skills.csv)'}\n    reviewer: {reviewer or '-'}")
    if not args.run:
        print(f"\nDry run: {len(selected)} issues. Add --run to create them (needs the gh command line tool, logged in).")
    else:
        print(f"\nCreated {created} issues; skipped {skipped} that already existed.")
    return 0


# ------------------------------------------------------------------ main
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--team-dir", default=str(DEFAULT_TEAM_DIR), help="folder with skills.csv and backlog.csv (default: docs/team)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="validate the CSV files").set_defaults(fn=cmd_check)
    sub.add_parser("backlog", help="render BACKLOG.md").set_defaults(fn=cmd_backlog)
    s = sub.add_parser("suggest", help="suggest assignees and reviewers")
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
