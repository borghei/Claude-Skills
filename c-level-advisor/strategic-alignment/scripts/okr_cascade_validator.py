#!/usr/bin/env python3
"""OKR Cascade Validator - Validate team OKRs connect to company OKRs.

Detects orphan goals (no parent), conflicting goals, and coverage gaps.
Reads OKRs from CSV files or inline input.

Usage:
    python okr_cascade_validator.py --company-okrs company_okrs.csv --team-okrs team_okrs.csv
    python okr_cascade_validator.py --company "Reach 5M ARR by Q4" --company "NPS above 40" --team "Sales:Close 50 new logos:Reach 5M ARR by Q4" --team "Eng:Ship HIPAA feature:Reach 5M ARR by Q4" --team "Marketing:Generate 1000 MQLs:" --json
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime


def load_csv_okrs(filepath, okr_type):
    """Load OKRs from CSV. Expected columns depend on type."""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    okrs = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if okr_type == "company":
                okrs.append({
                    "id": row.get("id", f"C{len(okrs)+1}"),
                    "objective": row.get("objective", row.get("okr", ""))
                })
            else:
                okrs.append({
                    "team": row.get("team", "Unknown"),
                    "objective": row.get("objective", row.get("okr", "")),
                    "parent": row.get("parent", row.get("company_okr", "")).strip()
                })
    return okrs


def validate(company_okrs, team_okrs):
    """Validate cascade: orphans, conflicts, coverage gaps."""
    company_objectives = {c["objective"]: c for c in company_okrs}

    # Detect orphans (team OKRs with no parent or parent not matching any company OKR)
    orphans = []
    connected = []
    for t in team_okrs:
        if not t["parent"] or t["parent"] not in company_objectives:
            orphans.append({
                "team": t["team"],
                "objective": t["objective"],
                "stated_parent": t["parent"] or "None",
                "issue": "No valid parent company OKR" if not t["parent"] else f"Parent '{t['parent']}' not found in company OKRs"
            })
        else:
            connected.append(t)

    # Detect coverage gaps (company OKRs with no team OKRs supporting them)
    coverage = {}
    for c in company_okrs:
        supporting = [t for t in connected if t["parent"] == c["objective"]]
        coverage[c["objective"]] = {
            "company_okr": c["objective"],
            "supporting_teams": [t["team"] for t in supporting],
            "support_count": len(supporting),
            "gap": len(supporting) == 0
        }

    gaps = [c for c in coverage.values() if c["gap"]]

    # Detect potential conflicts (multiple teams working on same parent with potentially conflicting approaches)
    conflicts = []
    by_parent = {}
    for t in connected:
        if t["parent"] not in by_parent:
            by_parent[t["parent"]] = []
        by_parent[t["parent"]].append(t)

    # Simple conflict detection: teams with opposing optimization targets
    conflict_pairs = [
        (["new logos", "new customers", "acquisition", "volume"], ["NPS", "retention", "satisfaction", "quality"]),
        (["ship fast", "velocity", "speed", "launch"], ["security", "compliance", "audit", "quality"]),
        (["reduce cost", "efficiency", "cut", "savings"], ["hire", "invest", "expand", "grow"]),
    ]

    for parent, teams in by_parent.items():
        if len(teams) >= 2:
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    t1_lower = teams[i]["objective"].lower()
                    t2_lower = teams[j]["objective"].lower()
                    for signal_a, signal_b in conflict_pairs:
                        t1_has_a = any(s in t1_lower for s in signal_a)
                        t1_has_b = any(s in t1_lower for s in signal_b)
                        t2_has_a = any(s in t2_lower for s in signal_a)
                        t2_has_b = any(s in t2_lower for s in signal_b)
                        if (t1_has_a and t2_has_b) or (t1_has_b and t2_has_a):
                            conflicts.append({
                                "parent_okr": parent,
                                "team_1": teams[i]["team"],
                                "objective_1": teams[i]["objective"],
                                "team_2": teams[j]["team"],
                                "objective_2": teams[j]["objective"],
                                "resolution": "Create shared metric that both teams own"
                            })

    # Alignment score
    total_team_okrs = len(team_okrs)
    orphan_pct = len(orphans) / total_team_okrs * 100 if total_team_okrs > 0 else 0
    coverage_pct = sum(1 for c in coverage.values() if not c["gap"]) / len(coverage) * 100 if coverage else 0

    cascade_score = 10
    cascade_score -= len(orphans) * 1.5
    cascade_score -= len(gaps) * 2
    cascade_score -= len(conflicts) * 1
    cascade_score = max(0, min(10, cascade_score))

    return {
        "validation_date": datetime.now().strftime("%Y-%m-%d"),
        "company_okrs_count": len(company_okrs),
        "team_okrs_count": total_team_okrs,
        "cascade_score": round(cascade_score, 1),
        "cascade_health": "HEALTHY" if cascade_score >= 7 else "NEEDS WORK" if cascade_score >= 4 else "BROKEN",
        "orphans": {
            "count": len(orphans),
            "percentage": round(orphan_pct, 1),
            "items": orphans
        },
        "coverage": {
            "fully_covered": sum(1 for c in coverage.values() if not c["gap"]),
            "gaps": len(gaps),
            "details": list(coverage.values()),
            "gap_items": gaps
        },
        "conflicts": {
            "count": len(conflicts),
            "items": conflicts
        },
        "recommendations": generate_recommendations(orphans, gaps, conflicts)
    }


def generate_recommendations(orphans, gaps, conflicts):
    recs = []
    if orphans:
        recs.append(f"ORPHANS: {len(orphans)} team OKR(s) have no valid parent. Connect each to a company OKR or cut the work.")
        for o in orphans[:3]:
            recs.append(f"  -> {o['team']}: '{o['objective']}' -- assign a parent company OKR")
    if gaps:
        recs.append(f"GAPS: {len(gaps)} company OKR(s) have no team support. Assign explicit team ownership.")
        for g in gaps[:3]:
            recs.append(f"  -> '{g['company_okr']}' -- no team assigned")
    if conflicts:
        recs.append(f"CONFLICTS: {len(conflicts)} potential goal conflict(s) detected between teams.")
        for c in conflicts[:3]:
            recs.append(f"  -> {c['team_1']} vs {c['team_2']}: create shared metric")
    if not recs:
        recs.append("No issues detected. Cascade looks healthy.")
    return recs


def print_human(result):
    print(f"\n{'='*70}")
    print(f"OKR CASCADE VALIDATION")
    print(f"Date: {result['validation_date']}")
    print(f"Company OKRs: {result['company_okrs_count']}  |  Team OKRs: {result['team_okrs_count']}")
    print(f"{'='*70}\n")

    print(f"CASCADE SCORE: {result['cascade_score']}/10 ({result['cascade_health']})\n")

    # Orphans
    o = result["orphans"]
    print(f"ORPHAN GOALS: {o['count']} ({o['percentage']}% of team OKRs)")
    if o["items"]:
        for item in o["items"]:
            print(f"  [!] {item['team']}: {item['objective']}")
            print(f"       Issue: {item['issue']}")

    # Coverage
    c = result["coverage"]
    print(f"\nCOVERAGE: {c['fully_covered']}/{c['fully_covered'] + c['gaps']} company OKRs have team support")
    for d in c["details"]:
        status = "+" if not d["gap"] else "!"
        teams = ", ".join(d["supporting_teams"]) if d["supporting_teams"] else "NO TEAMS ASSIGNED"
        print(f"  [{status}] {d['company_okr'][:50]}")
        print(f"       Supported by: {teams}")

    # Conflicts
    cf = result["conflicts"]
    if cf["items"]:
        print(f"\nCONFLICTS: {cf['count']}")
        for item in cf["items"]:
            print(f"  [!] {item['team_1']} ({item['objective_1'][:30]}...) vs {item['team_2']} ({item['objective_2'][:30]}...)")
            print(f"       Resolution: {item['resolution']}")

    print(f"\nRECOMMENDATIONS:")
    for r in result["recommendations"]:
        print(f"  {r}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Validate OKR cascade: orphans, conflicts, coverage gaps")
    parser.add_argument("--company-okrs", help="CSV file with company OKRs (columns: id, objective)")
    parser.add_argument("--team-okrs", help="CSV file with team OKRs (columns: team, objective, parent)")
    parser.add_argument("--company", action="append", help="Inline company OKR (multiple allowed)")
    parser.add_argument("--team", action="append", help="Inline team OKR as 'team:objective:parent_okr' (multiple allowed)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    company_okrs = []
    team_okrs = []

    if args.company_okrs and args.team_okrs:
        company_okrs = load_csv_okrs(args.company_okrs, "company")
        team_okrs = load_csv_okrs(args.team_okrs, "team")
    elif args.company and args.team:
        for i, c in enumerate(args.company):
            company_okrs.append({"id": f"C{i+1}", "objective": c.strip()})
        for t_str in args.team:
            parts = t_str.split(":")
            if len(parts) >= 2:
                team_okrs.append({
                    "team": parts[0].strip(),
                    "objective": parts[1].strip(),
                    "parent": parts[2].strip() if len(parts) > 2 else ""
                })
    else:
        print("Error: Provide either --company-okrs/--team-okrs CSV files or --company/--team inline", file=sys.stderr)
        sys.exit(1)

    result = validate(company_okrs, team_okrs)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
