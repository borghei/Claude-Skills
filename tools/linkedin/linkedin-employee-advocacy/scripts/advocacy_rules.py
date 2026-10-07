#!/usr/bin/env python3
"""Cadence tables and governance rules behind the employee advocacy planner.

Holds the starting weekly cadence per role family, the seniority and stage
factors, the time model, the goal-to-role emphasis map and the governance rule
catalogue. Every number is a planning default to be tuned against the team's
own history, not an industry statistic. Run directly to print the tables.

Usage:
    python3 advocacy_rules.py --list-rules
    python3 advocacy_rules.py --list-rules --format json

Exit codes:
    0  tables printed
    2  bad arguments
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Tuple

SEVERITY_RANK: Dict[str, int] = {"blocker": 0, "warning": 1}

# Steady-state weekly starting points for a senior member of each role family:
# (original posts, comments on other people's posts, reshares with a comment).
FAMILY_BASE: Dict[str, Tuple[float, int, int]] = {
    "founder": (2.0, 10, 1),
    "executive": (1.0, 8, 1),
    "marketing": (2.0, 8, 1),
    "sales": (1.0, 12, 1),
    "customer_success": (1.0, 6, 1),
    "people": (1.0, 6, 1),
    "product": (1.0, 4, 1),
    "engineering": (1.0, 4, 0),
    "design": (1.0, 4, 0),
    "other": (0.5, 3, 0),
}

SENIORITY_FACTOR: Dict[str, float] = {"junior": 0.5, "mid": 0.75, "senior": 1.0, "lead": 1.0}

# Stage scales the steady-state numbers: (posts, comments, reshares).
STAGE_FACTOR: Dict[str, Tuple[float, float, float]] = {
    "listen": (0.0, 0.5, 0.0),
    "starter": (0.5, 0.75, 1.0),
    "steady": (1.0, 1.0, 1.0),
}

# Minutes per action. Assumptions; override from the planner's command line.
MINUTES: Dict[str, int] = {"post": 40, "comment": 4, "reshare": 8, "review": 10}

# Role families whose voices matter most for each programme goal.
GOAL_EMPHASIS: Dict[str, Tuple[str, ...]] = {
    "pipeline": ("sales", "customer_success", "founder", "marketing"),
    "hiring": ("engineering", "product", "design", "people"),
    "reputation": ("founder", "executive", "marketing"),
    "category": ("founder", "product", "engineering", "marketing"),
}

# id -> (severity, governance key, value that passes, problem, fix)
GOVERNANCE: Dict[str, Tuple[str, str, Any, str, str]] = {
    "GV-01": ("blocker", "voluntary", True,
              "Participation is not stated as voluntary",
              "Write it into the charter: joining, pausing and leaving are the employee's choice."),
    "GV-02": ("blocker", "performance_linked", False,
              "Posting is tied to performance review, targets or pay",
              "Remove the link. Recognise contribution; never score people on their personal accounts."),
    "GV-03": ("blocker", "company_holds_credentials", False,
              "The company holds or uses employees' account credentials",
              "Stop. Each person posts from their own account, themselves, or not at all."),
    "GV-04": ("blocker", "disclosure_guidance", True,
              "No guidance on disclosing the employment relationship",
              "Add a one-line rule and examples; confirm the wording with counsel for your jurisdictions."),
    "GV-05": ("blocker", "identical_copy_allowed", False,
              "Shared copy may be pasted verbatim across accounts",
              "Share facts, links and angles. Each person writes their own words or reshares with a comment."),
    "GV-06": ("blocker", "scripted_engagement", False,
              "Staff are told when to react to or comment on colleagues' posts",
              "Drop the engagement rota. Colleagues may respond when they have something to say."),
    "GV-07": ("blocker", "restricted_topics_list", True,
              "No written list of topics that need a check before posting",
              "List the triggers (customer names, unreleased work, financial figures, legal matters) and who checks each."),
    "GV-08": ("warning", "review_triggers_defined", True,
              "Review is not limited to defined triggers",
              "Review only posts that trip a trigger; everything else publishes without a queue."),
    "GV-09": ("warning", "opt_out_path", True,
              "No documented way to pause or leave",
              "Name the person to tell and state that no reason is needed."),
    "GV-10": ("warning", "incident_pause_rule", True,
              "No rule for pausing during an incident",
              "Define who can call a pause, what it covers and who gives the all-clear."),
    "GV-11": ("warning", "offboarding_rule", True,
              "No rule for what happens when someone leaves the company",
              "State it: the account and its audience stay with the person; programme materials do not."),
    "GV-12": ("warning", "ai_drafting_rule", True,
              "No rule on drafting tools",
              "Say what is allowed: tools may help draft, the person owns and checks every word they publish."),
}


def finding(rule_id: str, severity: str, subject: str, problem: str,
            evidence: str, fix: str) -> Dict[str, str]:
    """Build a governance or roster finding record."""
    return {"id": rule_id, "severity": severity, "subject": subject,
            "problem": problem, "evidence": evidence, "fix": fix}


def check_governance(gov: Dict[str, Any]) -> List[Dict[str, str]]:
    """Compare a programme's governance answers with the rule catalogue."""
    out: List[Dict[str, str]] = []
    for rule_id, (severity, key, passing, problem, fix) in GOVERNANCE.items():
        value = gov.get(key)
        if value is passing:
            continue
        evidence = f"{key} is {'unanswered' if value is None else json.dumps(value)}"
        out.append(finding(rule_id, severity, "programme", problem, evidence, fix))
    hours = gov.get("review_turnaround_hours")
    if not isinstance(hours, (int, float)) or isinstance(hours, bool) or hours > 24:
        out.append(finding(
            "GV-13", "warning", "programme",
            "Review turnaround is longer than one working day or not set",
            f"review_turnaround_hours is {json.dumps(hours)}",
            "Commit to a same-day answer; a missed deadline escalates to the owner, it does not publish."))
    if not str(gov.get("owner") or "").strip():
        out.append(finding(
            "GV-14", "warning", "programme", "No named programme owner",
            "owner is blank",
            "Name one person who answers questions, handles escalations and can call a pause."))
    return out


def round_half(value: float) -> float:
    """Round to the nearest half so 0.5 can mean one post a fortnight."""
    return round(value * 2) / 2


def stage_for(experience: str, weeks: int) -> str:
    """Pick a member's stage from prior posting habit and weeks in the programme."""
    if experience == "regular":
        return "steady"
    if experience == "occasional":
        return "starter" if weeks < 3 else "steady"
    if weeks < 2:
        return "listen"
    return "starter" if weeks < 6 else "steady"


def target_cadence(family: str, seniority: str, stage: str) -> Dict[str, float]:
    """Return the weekly posts, comments and reshares before any time cap."""
    posts, comments, reshares = FAMILY_BASE[family]
    level = SENIORITY_FACTOR[seniority]
    f_posts, f_comments, f_reshares = STAGE_FACTOR[stage]
    planned_posts = round_half(posts * level * f_posts)
    if stage != "listen" and posts * level * f_posts > 0:
        planned_posts = max(0.5, planned_posts)
    return {"posts": planned_posts,
            "comments": float(max(1, round(comments * level * f_comments))),
            "reshares": float(round(reshares * f_reshares))}


def minutes_for(cadence: Dict[str, float], minutes: Dict[str, int]) -> int:
    """Estimate the weekly minutes a cadence costs under the time model."""
    return int(round(cadence["posts"] * minutes["post"]
                     + cadence["comments"] * minutes["comment"]
                     + cadence["reshares"] * minutes["reshare"]))


def fit_to_budget(cadence: Dict[str, float], budget_minutes: int,
                  minutes: Dict[str, int]) -> Tuple[Dict[str, float], bool]:
    """Trim a cadence until it fits the member's weekly time budget.

    Reshares go first, then posts in half steps, then comments, because a
    comment habit is the cheapest part to keep. Returns the trimmed cadence and
    whether anything was cut.
    """
    plan = dict(cadence)
    trimmed = False
    while minutes_for(plan, minutes) > budget_minutes:
        trimmed = True
        if plan["reshares"] > 0:
            plan["reshares"] -= 1
        elif plan["posts"] > 0:
            plan["posts"] -= 0.5
        elif plan["comments"] > 1:
            plan["comments"] -= 1
        else:
            break
    return plan, trimmed


def list_rules(fmt: str) -> None:
    """Print the cadence tables and the governance catalogue."""
    rules = [{"id": rid, "severity": r[0], "key": r[1], "passes_when": r[2],
              "problem": r[3], "fix": r[4]} for rid, r in GOVERNANCE.items()]
    if fmt == "json":
        print(json.dumps({"family_base": FAMILY_BASE, "seniority_factor": SENIORITY_FACTOR,
                          "stage_factor": STAGE_FACTOR, "minutes": MINUTES,
                          "goal_emphasis": GOAL_EMPHASIS, "governance": rules}, indent=2))
        return
    print("Steady-state weekly starting points (senior member)")
    print("=" * 72)
    print(f"  {'role family':<18}{'posts':>6}{'comments':>10}{'reshares':>10}")
    for family, (posts, comments, reshares) in FAMILY_BASE.items():
        print(f"  {family:<18}{posts:>6}{comments:>10}{reshares:>10}")
    print("\nSeniority factor: " + ", ".join(f"{k} x{v}" for k, v in SENIORITY_FACTOR.items()))
    print("Stage factor (posts, comments, reshares): "
          + ", ".join(f"{k} {v}" for k, v in STAGE_FACTOR.items()))
    print("Minutes per action: " + ", ".join(f"{k} {v}" for k, v in MINUTES.items()))
    print("\nGovernance rules")
    print("=" * 72)
    for rule in rules:
        print(f"{rule['id']}  [{rule['severity']:<7}] {rule['problem']}")
        print(f"       passes when {rule['key']} = {json.dumps(rule['passes_when'])}")
        print(f"       fix: {rule['fix']}")
    print("GV-13  [warning] review_turnaround_hours missing or above 24")
    print("GV-14  [warning] owner is blank")


def main() -> None:
    """Parse arguments and print the tables."""
    parser = argparse.ArgumentParser(
        description="Print the cadence tables and governance rules used by advocacy_planner.py.",
        epilog="Exit codes: 0 tables printed, 2 bad arguments.")
    parser.add_argument("--list-rules", action="store_true",
                        help="Print cadence defaults, the time model and every governance rule.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if not args.list_rules:
        parser.print_help(sys.stderr)
        print("\nERROR: nothing to do. Pass --list-rules.", file=sys.stderr)
        sys.exit(2)
    list_rules(args.format)


if __name__ == "__main__":
    main()
