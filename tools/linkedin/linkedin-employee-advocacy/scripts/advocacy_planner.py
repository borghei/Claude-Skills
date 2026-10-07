#!/usr/bin/env python3
"""Turn a team roster into a weekly advocacy cadence matrix and flag governance gaps.

Reads a roster JSON (programme goal, governance answers, members with role
family, seniority, posting habit, time budget and topics). Produces a
per-person weekly plan sized to each person's time, a topic coverage map, a
review-load estimate and a list of governance and roster findings. Offline:
it plans from the file you supply and posts nothing.

Usage:
    python3 advocacy_planner.py --input roster.json
    python3 advocacy_planner.py --input roster.json --week 6 --format json
    python3 advocacy_planner.py --input roster.json --fail-on blocker

Exit codes:
    0  plan produced (and no finding at or above --fail-on, if given)
    1  a finding at or above --fail-on exists
    2  bad input: file missing, not valid JSON, or a roster field is invalid
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from advocacy_rules import (  # noqa: E402
    FAMILY_BASE, GOAL_EMPHASIS, MINUTES, SENIORITY_FACTOR, SEVERITY_RANK,
    check_governance, finding, fit_to_budget, minutes_for, stage_for, target_cadence)

EXPERIENCE = ("new", "occasional", "regular")


def fail(message: str) -> None:
    """Print an actionable error to stderr and exit with the bad-input code."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def load_roster(path: Path) -> Dict[str, Any]:
    """Load and validate the roster JSON, exiting with guidance on failure."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"roster not found: {path}. Start from assets/roster_template.json.")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {path}: {exc}")
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON (line {exc.lineno}): {exc.msg}")
    if not isinstance(data, dict) or not isinstance(data.get("members"), list) or not data["members"]:
        fail("roster must be a JSON object with a non-empty 'members' array. "
             "See assets/sample_roster.json for the expected shape.")
    for index, member in enumerate(data["members"], 1):
        if not isinstance(member, dict) or not str(member.get("name") or "").strip():
            fail(f"member {index} needs a 'name'.")
        label = member["name"]
        for key, allowed in (("role_family", tuple(FAMILY_BASE)), ("seniority", tuple(SENIORITY_FACTOR)),
                             ("experience", EXPERIENCE)):
            if str(member.get(key) or "").lower() not in allowed:
                fail(f"member '{label}': {key} is {member.get(key)!r}; use one of: " + ", ".join(allowed))
        hours = member.get("hours_per_week")
        if not isinstance(hours, (int, float)) or isinstance(hours, bool) or hours < 0:
            fail(f"member '{label}': hours_per_week must be a number of hours, zero or more.")
    return data


def plan_member(member: Dict[str, Any], week: int, minutes: Dict[str, int]) -> Dict[str, Any]:
    """Build one member's weekly row from role, stage and time budget."""
    family, seniority = member["role_family"].lower(), member["seniority"].lower()
    weeks = int(member.get("weeks_in_programme", week))
    stage = stage_for(member["experience"].lower(), weeks)
    wanted = target_cadence(family, seniority, stage)
    budget = int(round(float(member["hours_per_week"]) * 60))
    cadence, trimmed = fit_to_budget(wanted, budget, minutes)
    return {"name": member["name"], "role_family": family, "seniority": seniority, "stage": stage,
            "posts": cadence["posts"], "comments": int(cadence["comments"]),
            "reshares": int(cadence["reshares"]), "minutes": minutes_for(cadence, minutes),
            "budget_minutes": budget, "trimmed_to_budget": trimmed,
            "topics": [str(t).strip().lower() for t in member.get("topics") or [] if str(t).strip()],
            "restricted_role": bool(member.get("restricted_role")),
            "pre_publication_check": bool(member.get("pre_publication_check"))}


def roster_findings(rows: List[Dict[str, Any]], skipped: List[str], programme: Dict[str, Any],
                    minutes: Dict[str, int]) -> List[Dict[str, str]]:
    """Derive findings from the planned matrix: consent, topics, load, concentration."""
    out: List[Dict[str, str]] = []
    for name in skipped:
        out.append(finding("RS-01", "blocker", name, "Listed on the roster without opting in",
                           "opted_in is not true; excluded from the plan",
                           "Ask the person. Until they say yes, they are not in the programme."))
    topic_owners: Dict[str, List[str]] = {}
    for row in rows:
        for topic in row["topics"]:
            topic_owners.setdefault(topic, []).append(row["name"])
        if not row["topics"]:
            out.append(finding("RS-05", "warning", row["name"], "No topics of their own",
                               "topics is empty",
                               "Agree two or three subjects this person knows first-hand."))
        if row["restricted_role"] and not row["pre_publication_check"]:
            out.append(finding("RS-06", "blocker", row["name"],
                               "Regulated or restricted role with no pre-publication check",
                               "restricted_role is true, pre_publication_check is not",
                               "Route this person's posts about the business through the named specialist first."))
        if row["stage"] == "steady" and row["posts"] == 0:
            out.append(finding("RS-07", "warning", row["name"],
                               "Time budget cannot carry any original posts",
                               f"{row['budget_minutes']} minutes a week",
                               "Either agree more time or plan this person as comment-only on purpose."))
    for topic, owners in sorted(topic_owners.items()):
        if len(owners) >= 3:
            out.append(finding("RS-02", "warning", topic, "Topic is crowded",
                               f"{len(owners)} people: " + ", ".join(owners),
                               "Split it by angle (customer view, build view, market view) or reassign."))
    total_posts = sum(r["posts"] for r in rows)
    if len(rows) >= 4 and total_posts:
        top = max(rows, key=lambda r: r["posts"])
        if top["posts"] / total_posts > 0.4:
            out.append(finding("RS-03", "warning", top["name"], "One person carries most of the output",
                               f"{top['posts']} of {total_posts} weekly posts",
                               "Spread the load; a programme that depends on one voice ends when they are away."))
    share = float(programme.get("review_share_estimate", 0.25))
    load = total_posts * share * minutes["review"]
    capacity = float(programme.get("reviewer_hours_per_week") or 0) * 60
    if load > capacity:
        out.append(finding("RS-04", "warning", "review queue", "Estimated review load exceeds reviewer time",
                           f"about {load:.0f} minutes a week against {capacity:.0f} available",
                           "Add reviewer time, narrow the triggers, or lower the cadence."))
    goal = str(programme.get("goal") or "").lower()
    wanted = GOAL_EMPHASIS.get(goal, ())
    if wanted and not any(r["role_family"] in wanted for r in rows):
        out.append(finding("RS-08", "warning", "roster", f"No voice from the roles a '{goal}' goal depends on",
                           "none of: " + ", ".join(wanted),
                           "Invite at least one person from those roles, or change the stated goal."))
    return out


def build_plan(roster: Dict[str, Any], week: int, minutes: Dict[str, int]) -> Dict[str, Any]:
    """Plan every opted-in member and assemble the programme report."""
    programme = roster.get("programme") if isinstance(roster.get("programme"), dict) else {}
    governance = programme.get("governance") if isinstance(programme.get("governance"), dict) else {}
    members = roster["members"]
    skipped = [m["name"] for m in members if m.get("opted_in") is not True]
    rows = [plan_member(m, week, minutes) for m in members if m.get("opted_in") is True]
    findings = check_governance(governance) + roster_findings(rows, skipped, programme, minutes)
    findings.sort(key=lambda f: (SEVERITY_RANK[f["severity"]], f["id"], f["subject"]))
    topics: Dict[str, List[str]] = {}
    for row in rows:
        for topic in row["topics"]:
            topics.setdefault(topic, []).append(row["name"])
    total_posts = sum(r["posts"] for r in rows)
    share = float(programme.get("review_share_estimate", 0.25))
    return {
        "programme": programme.get("name", "unnamed programme"),
        "goal": programme.get("goal", "unspecified"), "week": week,
        "members_planned": len(rows), "members_not_opted_in": skipped,
        "totals": {"posts": total_posts, "comments": sum(r["comments"] for r in rows),
                   "reshares": sum(r["reshares"] for r in rows),
                   "hours": round(sum(r["minutes"] for r in rows) / 60, 1),
                   "review_minutes_estimate": round(total_posts * share * minutes["review"])},
        "assumptions": {"minutes": minutes, "review_share_estimate": share},
        "matrix": rows, "topic_coverage": dict(sorted(topics.items())),
        "counts": {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_RANK},
        "findings": findings}


def render(report: Dict[str, Any], fmt: str) -> None:
    """Print the plan as JSON or as a text matrix with findings."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Advocacy plan: {report['programme']}   goal: {report['goal']}   week {report['week']}")
    totals = report["totals"]
    print(f"Planned members: {report['members_planned']}   weekly: {totals['posts']} posts, "
          f"{totals['comments']} comments, {totals['reshares']} reshares, {totals['hours']} h")
    print("=" * 96)
    print(f"{'name':<20}{'role':<17}{'level':<8}{'stage':<9}{'posts':>6}{'cmts':>6}{'reshr':>6}"
          f"{'min':>6}{'budget':>8}  note")
    for row in report["matrix"]:
        note = "trimmed to budget" if row["trimmed_to_budget"] else ""
        print(f"{row['name'][:19]:<20}{row['role_family'][:16]:<17}{row['seniority']:<8}{row['stage']:<9}"
              f"{row['posts']:>6}{row['comments']:>6}{row['reshares']:>6}{row['minutes']:>6}"
              f"{row['budget_minutes']:>8}  {note}")
    print("-" * 96)
    print("posts 0.5 = one a fortnight. Minutes use the time model in --help; tune it to your team.")
    print(f"Review queue estimate: {totals['review_minutes_estimate']} minutes a week "
          f"(assumes {report['assumptions']['review_share_estimate']:.0%} of posts trip a trigger).")
    print("\nTopic coverage")
    for topic, owners in report["topic_coverage"].items():
        print(f"  {topic:<34} {', '.join(owners)}")
    counts = report["counts"]
    print(f"\nFindings: {counts['blocker']} blocker, {counts['warning']} warning")
    for item in report["findings"]:
        print(f"[{item['severity'].upper():<7}] {item['id']}  {item['subject']}: {item['problem']}")
        print(f"          evidence: {item['evidence']}")
        print(f"          fix: {item['fix']}")
    if not report["findings"]:
        print("  None. Re-read the charter with the team before launch anyway.")


def main() -> None:
    """Parse arguments, build the plan, print it and apply the gate."""
    parser = argparse.ArgumentParser(
        description="Turn a team roster into a weekly advocacy cadence matrix and flag "
                    "governance gaps. Offline: reads only the file you supply.",
        epilog="Exit codes: 0 plan produced, 1 finding at or above --fail-on, 2 bad input.")
    parser.add_argument("--input", required=True, help="Path to the roster JSON.")
    parser.add_argument("--week", type=int, default=None,
                        help="Programme week to plan for; sets each member's stage unless the "
                             "member has weeks_in_programme (default: programme.week, else 1).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--minutes-per-post", type=int, default=MINUTES["post"],
                        help="Minutes to write and publish one original post (default: %(default)s).")
    parser.add_argument("--minutes-per-comment", type=int, default=MINUTES["comment"],
                        help="Minutes per considered comment (default: %(default)s).")
    parser.add_argument("--fail-on", choices=list(SEVERITY_RANK), default=None,
                        help="Exit 1 if any finding at or above this severity exists.")
    args = parser.parse_args()

    roster = load_roster(Path(args.input))
    programme = roster.get("programme") if isinstance(roster.get("programme"), dict) else {}
    week = args.week if args.week is not None else programme.get("week", 1)
    if not isinstance(week, int) or isinstance(week, bool) or week < 1:
        fail("week must be a whole number of 1 or more (check --week and programme.week).")
    if args.minutes_per_post < 1 or args.minutes_per_comment < 1:
        fail("--minutes-per-post and --minutes-per-comment must be 1 or more.")
    minutes = {**MINUTES, "post": args.minutes_per_post, "comment": args.minutes_per_comment}
    try:
        report = build_plan(roster, week, minutes)
    except (TypeError, ValueError, AttributeError) as exc:
        fail(f"a roster field has the wrong type ({exc}). Compare with assets/roster_template.json.")
    render(report, args.format)
    if args.fail_on:
        limit = SEVERITY_RANK[args.fail_on]
        if any(SEVERITY_RANK[f["severity"]] <= limit for f in report["findings"]):
            sys.exit(1)


if __name__ == "__main__":
    main()
