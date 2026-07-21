#!/usr/bin/env python3
"""Detect overlapping SaaS tools and rank consolidation candidates.

Usage:
    python3 tool_overlap_detector.py --input spend.json [--format text|json]

Input JSON shape: the same dataset consumed by license_utilization_analyzer.py.
Tools sharing a 'category' are treated as overlapping; the survivor is chosen by
usage and criticality, not by cost alone.
"""

import argparse
import json
import sys
from collections import defaultdict
from typing import Any, Dict, List

CRITICALITY_RANK = {"critical": 3, "core": 2, "reference": 1}

# Categories where holding several tools is normal rather than wasteful.
TOLERANT_CATEGORIES = {"developer-tools", "security"}

# Umbrella labels that are not substitution sets. A wiki and a chat tool are
# both "collaboration" and are not remotely interchangeable, so a consolidation
# recommendation drawn from such a label is an artefact of the tagging.
BROAD_CATEGORIES = {"collaboration", "productivity", "other", "misc",
                    "general", "software", "saas", "operations"}

# Realistic share of a displaced tool's cost actually recovered after
# migration effort, data export, and retained read-only access.
NET_RECOVERY_RATE = 0.80


def survivor_score(tool: Dict[str, Any]) -> float:
    """Score a tool's claim to be the survivor of a consolidation."""
    purchased = int(tool.get("seats_purchased", 0) or 0)
    active = int(tool.get("seats_active_30d", 0) or 0)
    crit = CRITICALITY_RANK.get(str(tool.get("criticality", "core")).lower(), 2)
    util = (active / purchased) if purchased else 0.0
    # Active users dominate: displacing 200 real users costs far more than
    # the licence difference ever saves.
    return round(active * 1.0 + util * 50.0 + crit * 40.0, 2)


def migration_effort(tool: Dict[str, Any]) -> str:
    """Estimate the effort of displacing a tool from its footprint."""
    active = int(tool.get("seats_active_30d", 0) or 0)
    crit = str(tool.get("criticality", "core")).lower()
    if crit == "critical" or active > 150:
        return "high"
    if active > 40:
        return "medium"
    return "low"


def analyse_category(category: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Assess one category for redundancy and pick a survivor and displacements."""
    ranked = sorted(tools, key=lambda t: -survivor_score(t))
    survivor = ranked[0]
    displaced = ranked[1:]

    candidates: List[Dict[str, Any]] = []
    for tool in displaced:
        cost = float(tool.get("annual_cost", 0) or 0)
        blocked = not bool(tool.get("has_alternative", True))
        effort = migration_effort(tool)
        candidates.append({
            "tool": tool.get("name", "(unnamed)"),
            "annual_cost": round(cost, 2),
            "seats_active_30d": int(tool.get("seats_active_30d", 0) or 0),
            "criticality": tool.get("criticality", "core"),
            "migration_effort": effort,
            "net_annual_recovery": round(cost * NET_RECOVERY_RATE, 2) if not blocked else 0.0,
            "blocked": blocked,
            "note": ("Marked has_alternative=false: capability is not covered by the "
                     "survivor. Verify before consolidating."
                     if blocked else
                     f"Migrate {tool.get('seats_active_30d', 0)} active users to "
                     f"{survivor.get('name')} ({effort} effort)."),
        })

    tolerant = category in TOLERANT_CATEGORIES
    broad = category in BROAD_CATEGORIES
    recovery = sum(c["net_annual_recovery"] for c in candidates)
    if broad:
        # Do not claim savings from an umbrella label; re-tag first.
        recovery = 0.0
        for cand in candidates:
            cand["net_annual_recovery"] = 0.0
        recommendation = (
            f"'{category}' is an umbrella label, not a substitution set. Re-tag these "
            "tools by the job they do (chat, knowledge-base, whiteboard, ...) and "
            "re-run. No recovery is claimed from this grouping.")
    elif tolerant:
        recommendation = ("Multiple tools are normal in this category. Consolidate only "
                          "if the overlap is genuine rather than adjacent.")
        recovery = round(recovery * 0.5, 2)
    elif not candidates:
        recommendation = "Single tool. No consolidation available."
    elif all(c["blocked"] for c in candidates):
        recommendation = ("Overlap is nominal - every alternative is marked as covering "
                          "capability the survivor does not. Re-verify the category tagging.")
    else:
        recommendation = (f"Consolidate onto {survivor.get('name')} and displace "
                          f"{len([c for c in candidates if not c['blocked']])} tool(s).")

    return {
        "category": category,
        "tool_count": len(tools),
        "category_spend": round(sum(float(t.get("annual_cost", 0) or 0) for t in tools), 2),
        "survivor": survivor.get("name", "(unnamed)"),
        "survivor_rationale": (
            f"{survivor.get('seats_active_30d', 0)} active users, "
            f"{survivor.get('criticality', 'core')} criticality - highest displacement cost"),
        "displacement_candidates": candidates,
        "net_annual_recovery": round(recovery, 2),
        "multi_tool_tolerated": tolerant,
        "umbrella_category": broad,
        "recommendation": recommendation,
    }


def analyse(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Group the portfolio by category and assess each for redundancy."""
    tools = payload.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ValueError("input JSON must contain a non-empty 'tools' array")

    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for tool in tools:
        grouped[str(tool.get("category", "other")).lower()].append(tool)

    overlaps = [analyse_category(cat, group) for cat, group in sorted(grouped.items())
                if len(group) > 1]
    overlaps.sort(key=lambda o: -o["net_annual_recovery"])

    total_spend = sum(float(t.get("annual_cost", 0) or 0) for t in tools)
    recovery = sum(o["net_annual_recovery"] for o in overlaps)

    return {
        "currency": payload.get("currency", "USD"),
        "tool_count": len(tools),
        "category_count": len(grouped),
        "overlapping_categories": len(overlaps),
        "total_annual_spend": round(total_spend, 2),
        "net_annual_recovery": round(recovery, 2),
        "recovery_pct_of_spend": round(100.0 * recovery / total_spend, 1) if total_spend else 0.0,
        "single_tool_categories": sorted(c for c, g in grouped.items() if len(g) == 1),
        "overlaps": overlaps,
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the overlap analysis as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    cur = result["currency"]
    print(f"Tool overlap across {result['tool_count']} tools in "
          f"{result['category_count']} categories")
    print(f"  overlapping categories: {result['overlapping_categories']}")
    print(f"  net recoverable: {cur} {result['net_annual_recovery']:,.0f} "
          f"({result['recovery_pct_of_spend']}% of {cur} "
          f"{result['total_annual_spend']:,.0f} spend)")
    print(f"  (net of an assumed {int((1 - NET_RECOVERY_RATE) * 100)}% migration and "
          "retained-access cost)")

    if not result["overlaps"]:
        print("\nNo categories hold more than one tool.")
        return

    print("\nOverlaps:")
    for ov in result["overlaps"]:
        tags = ""
        if ov["umbrella_category"]:
            tags = "  [UMBRELLA LABEL - re-tag before acting]"
        elif ov["multi_tool_tolerated"]:
            tags = "  [multi-tool tolerated]"
        print(f"\n  {ov['category']} - {ov['tool_count']} tools, "
              f"{cur} {ov['category_spend']:,.0f}/yr{tags}")
        print(f"    survivor: {ov['survivor']} ({ov['survivor_rationale']})")
        for cand in ov["displacement_candidates"]:
            flag = " [BLOCKED]" if cand["blocked"] else ""
            print(f"    displace: {cand['tool']}{flag}  {cur} {cand['annual_cost']:,.0f}/yr, "
                  f"{cand['seats_active_30d']} active, {cand['migration_effort']} effort")
            print(f"              recovery {cur} {cand['net_annual_recovery']:,.0f} - "
                  f"{cand['note']}")
        print(f"    -> {ov['recommendation']}")

    if result["single_tool_categories"]:
        print(f"\nSingle-tool categories (no overlap): "
              f"{', '.join(result['single_tool_categories'])}")


def main() -> None:
    """Parse arguments, run the overlap analysis, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Detect overlapping SaaS tools and rank consolidation candidates.")
    parser.add_argument("--input", required=True,
                        help="Path to a JSON file with a 'tools' array including 'category'")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)

    try:
        result = analyse(payload)
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output(result, args.format)


if __name__ == "__main__":
    main()
