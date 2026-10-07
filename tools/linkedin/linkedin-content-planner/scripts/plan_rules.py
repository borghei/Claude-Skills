#!/usr/bin/env python3
"""Rule data and allocation primitives used by plan_builder.py.

Holds the default limits, the flag catalogue, the two built-in pillar sets
(general and founder), and the two deterministic allocation routines: a
largest-remainder split of slots across shares and a deficit-based picker that
spreads those slots evenly through time. The config loading, calendar maths
and CLI live in plan_builder.py.

Usage:
    python3 plan_rules.py --list-rules
    python3 plan_rules.py --list-rules --format json

Exit codes:
    0  rules printed
    2  bad arguments
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Sequence

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
SEVERITY_RANK = {"error": 0, "warn": 1, "info": 2}

# House heuristics, not platform facts. Every one can be overridden per plan
# under "limits" in the config.
DEFAULT_LIMITS = {
    "max_posts_per_week": 5,
    "max_pillar_share": 50,
    "max_promotional_per_week": 1,
    "max_produced_per_week": 1,
    "max_ask_share": 60,
    "share_tolerance": 15,
}

RULES = {
    "CP-001": ("warn", "Pillar count is outside the workable range of 3 to 5"),
    "CP-002": ("error", "One pillar takes more of the plan than the cap allows"),
    "CP-003": ("error", "Promotional pillar appears too often in one week"),
    "CP-004": ("warn", "Cadence is above the weekly post limit"),
    "CP-005": ("warn", "A pillar received no slots at this plan length"),
    "CP-006": ("warn", "Same pillar on consecutive posts"),
    "CP-007": ("warn", "Same format three posts running"),
    "CP-008": ("warn", "Produced formats do not fit weekly production capacity"),
    "CP-009": ("warn", "One reader ask dominates the plan"),
    "CP-010": ("warn", "Planned share is far from the target share"),
    "CP-011": ("info", "Skip dates removed posting slots"),
    "CP-012": ("warn", "Story bank cannot supply every slot for a pillar"),
    "CP-013": ("info", "No story bank supplied; slots carry no source entry"),
    "CP-014": ("warn", "No conversation day is scheduled"),
    "CP-015": ("warn", "A week has no posts after skip dates"),
}

PILLAR_SETS = {
    "general": [
        {"name": "craft", "share": 35, "ask": "keep",
         "note": "How the work is done, taught from your own cases"},
        {"name": "field-notes", "share": 30, "ask": "reply",
         "note": "First-person episodes: what happened and what changed"},
        {"name": "peers", "share": 20, "ask": "pass-on",
         "note": "Other people's work, questions to the room, credit given"},
        {"name": "offer", "share": 15, "ask": "contact", "promotional": True,
         "note": "What you sell or are hiring for, stated plainly"},
    ],
    "founder": [
        {"name": "market-view", "share": 25, "ask": "reply",
         "note": "For investors and peers: what you believe about the market"},
        {"name": "build-log", "share": 30, "ask": "keep",
         "note": "For future hires: how the team works and what shipped"},
        {"name": "customer-desk", "share": 30, "ask": "contact",
         "note": "For buyers: problems heard first-hand and outcomes"},
        {"name": "ledger", "share": 15, "ask": "pass-on",
         "note": "For all three: a decision, the options rejected, the price"},
    ],
}


def flag(rule_id: str, where: str, evidence: str, action: str) -> Dict[str, Any]:
    """Build one flag record, taking severity and title from RULES."""
    severity, title = RULES[rule_id]
    return {"id": rule_id, "severity": severity, "where": where,
            "title": title, "evidence": evidence, "action": action}


def largest_remainder(shares: Sequence[float], total: int) -> List[int]:
    """Split `total` whole slots across shares so the counts sum exactly.

    Each share gets the floor of its exact quota; leftover slots go to the
    largest fractional remainders, earlier items winning ties.
    """
    whole = sum(shares)
    if whole <= 0 or total <= 0:
        return [0 for _ in shares]
    quotas = [share * total / whole for share in shares]
    counts = [int(q) for q in quotas]
    order = sorted(range(len(shares)), key=lambda i: (-(quotas[i] - counts[i]), i))
    for index in order[: total - sum(counts)]:
        counts[index] += 1
    return counts


def deficit_pick(targets: Sequence[int], given: Sequence[int], position: int,
                 total: int, allowed: Optional[Sequence[int]] = None,
                 avoid: Optional[int] = None) -> Optional[int]:
    """Pick the item that is furthest behind its even-spread schedule.

    `targets` are whole-slot quotas, `given` what each item has received so
    far, `position` the 1-based slot being filled. Items outside `allowed` or
    with no quota left are skipped. `avoid` is passed over when any other
    candidate exists. Ties go to the earlier item. Returns None when nothing
    is eligible.
    """
    candidates = [i for i in range(len(targets))
                  if given[i] < targets[i] and (allowed is None or i in allowed)]
    if not candidates:
        return None
    if avoid is not None and len(candidates) > 1 and avoid in candidates:
        candidates.remove(avoid)
    return max(candidates,
               key=lambda i: (targets[i] * position / total - given[i], -i))


def run_lengths(values: Sequence[Any]) -> List[Dict[str, Any]]:
    """Collapse a sequence into runs: [{'value': v, 'start': i, 'length': n}]."""
    runs: List[Dict[str, Any]] = []
    for index, value in enumerate(values):
        if runs and runs[-1]["value"] == value:
            runs[-1]["length"] += 1
        else:
            runs.append({"value": value, "start": index, "length": 1})
    return runs


def percent(part: int, whole: int) -> float:
    """Return part/whole as a percentage rounded to one decimal place."""
    return round(100.0 * part / whole, 1) if whole else 0.0


def check_plan(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Inspect a built plan and return every imbalance flag, worst first."""
    slots, limits = plan["slots"], plan["limits"]
    pillars, formats = plan["pillars"], plan["formats"]
    total = len(slots)
    out: List[Dict[str, Any]] = []
    if not 3 <= len(pillars) <= 5:
        out.append(flag("CP-001", "config", f"{len(pillars)} pillars",
                        "Merge or split until there are 3 to 5; fewer reads as "
                        "one note, more and no pillar repeats often enough."))
    weeks: Dict[int, List[Dict[str, Any]]] = {w: [] for w in range(1, plan["weeks"] + 1)}
    for slot in slots:
        weeks[slot["week"]].append(slot)
    produced = {f["name"] for f in formats if f.get("produced")}
    for pillar in pillars:
        count = sum(1 for s in slots if s["pillar"] == pillar["name"])
        share = percent(count, total)
        if share > limits["max_pillar_share"]:
            out.append(flag("CP-002", pillar["name"], f"{count}/{total} posts ({share}%)",
                            "Lower this pillar's share or lengthen the plan."))
        if count == 0:
            out.append(flag("CP-005", pillar["name"],
                            f"target {pillar['share']}% of {total} posts rounds to 0",
                            "Raise its share, plan more weeks, or drop the pillar."))
        elif abs(share - pillar["share"]) > limits["share_tolerance"]:
            out.append(flag("CP-010", pillar["name"],
                            f"target {pillar['share']}%, planned {share}%",
                            "Short plans cannot hit fine-grained shares; judge "
                            "the mix over a month, not a week."))
    for number, week in weeks.items():
        where = f"week {number}"
        if not week:
            out.append(flag("CP-015", where, "0 posts", "Move a post into this "
                            "week or accept the gap deliberately."))
        if len(week) > limits["max_posts_per_week"]:
            out.append(flag("CP-004", where, f"{len(week)} posts",
                            "Cut posting days; a cadence you cannot sustain for "
                            "a quarter is worse than a lower one you can."))
        promo = sum(1 for s in week if s["promotional"])
        if promo > limits["max_promotional_per_week"]:
            out.append(flag("CP-003", where, f"{promo} promotional posts",
                            "Lower the promotional pillar's share or extend the plan."))
        made = sum(1 for s in week if s["format"] in produced)
        if made > limits["max_produced_per_week"]:
            out.append(flag("CP-008", where, f"{made} produced-format posts, capacity "
                            f"{limits['max_produced_per_week']}",
                            "Widen the pillar's allowed formats or raise capacity."))
    wanted = sum(c for f, c in zip(formats, plan["format_targets"]) if f.get("produced"))
    got = sum(1 for s in slots if s["format"] in produced)
    if got < wanted:
        out.append(flag("CP-008", "plan", f"mix asks for {wanted} produced posts, "
                        f"capacity allowed {got}",
                        "Lower the produced formats' share or raise "
                        "max_produced_per_week if the time really exists."))
    for run in run_lengths([s["pillar"] for s in slots]):
        if run["length"] >= 2:
            out.append(flag("CP-006", slots[run["start"]]["date"],
                            f"{run['value']} x{run['length']} in a row",
                            "Swap one of the posts with a neighbour."))
    for run in run_lengths([s["format"] for s in slots]):
        if run["length"] >= 3 and len(formats) > 1:
            out.append(flag("CP-007", slots[run["start"]]["date"],
                            f"{run['value']} x{run['length']} in a row",
                            "Change the format of the middle post."))
    asks: Dict[str, int] = {}
    for slot in slots:
        asks[slot["ask"]] = asks.get(slot["ask"], 0) + 1
    for ask, count in asks.items():
        if percent(count, total) > limits["max_ask_share"]:
            out.append(flag("CP-009", "plan", f"'{ask}' on {count}/{total} posts",
                            "Give at least one pillar a different ask."))
    if plan["skipped"]:
        out.append(flag("CP-011", "plan", f"{plan['skipped']} slot(s) removed",
                        "No action; shares are computed on the remaining slots."))
    if not plan["conversation_weekdays"]:
        out.append(flag("CP-014", "config", "conversation_weekdays is empty",
                        "Reserve at least one day a week for commenting on "
                        "other people's posts."))
    if not plan["bank_supplied"]:
        out.append(flag("CP-013", "plan", "no --story-bank given",
                        "Optional: pass a story bank file to bind slots to entries."))
    else:
        for pillar in pillars:
            mine = [s for s in slots if s["pillar"] == pillar["name"]]
            empty = sum(1 for s in mine if not s["entry_id"])
            if empty:
                out.append(flag("CP-012", pillar["name"],
                                f"{empty} of {len(mine)} slots have no ready entry",
                                "Interview for this pillar before the plan starts, "
                                "or shrink its share."))
    out.sort(key=lambda f: (SEVERITY_RANK[f["severity"]], f["id"], f["where"]))
    return out


def main() -> None:
    """Print the flag catalogue, default limits and built-in pillar sets."""
    parser = argparse.ArgumentParser(
        description="Show the flags, default limits and built-in pillar sets "
                    "used by plan_builder.py.",
        epilog="Exit codes: 0 rules printed, 2 bad arguments.")
    parser.add_argument("--list-rules", action="store_true",
                        help="Print the catalogue (required; the module has "
                             "no other action).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if not args.list_rules:
        print("ERROR: nothing to do. Pass --list-rules, or run "
              "plan_builder.py --input <config.json> to build a plan.",
              file=sys.stderr)
        sys.exit(2)
    if args.format == "json":
        print(json.dumps({
            "rules": {k: {"severity": v[0], "title": v[1]} for k, v in RULES.items()},
            "default_limits": DEFAULT_LIMITS, "pillar_sets": PILLAR_SETS,
        }, indent=2))
        return
    print("Content plan flags")
    print("=" * 72)
    for rule_id, (severity, title) in RULES.items():
        print(f"{rule_id}  [{severity:<5}] {title}")
    print("\nDefault limits (heuristics; override under 'limits' in the config)")
    for key, value in DEFAULT_LIMITS.items():
        print(f"  {key:<26} {value}")
    for name, pillars in PILLAR_SETS.items():
        print(f"\nBuilt-in pillar set: {name}")
        for pillar in pillars:
            promo = "  [promotional]" if pillar.get("promotional") else ""
            print(f"  {pillar['name']:<14} {pillar['share']:>3}%  ask={pillar['ask']:<8}"
                  f" {pillar['note']}{promo}")


if __name__ == "__main__":
    main()
