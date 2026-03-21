#!/usr/bin/env python3
"""Resource Allocator - Analyze and optimize resource allocation across projects.

Reads resource allocation data and identifies over-allocation, conflicts,
utilization gaps, and produces rebalancing recommendations.

Usage:
    python resource_allocator.py --resources resources.json
    python resource_allocator.py --resources resources.json --json
    python resource_allocator.py --example
"""

import argparse
import json
import sys
from collections import defaultdict


def load_data(path: str) -> dict:
    """Load resource data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def analyze_resources(data: dict) -> dict:
    """Analyze resource allocation and identify conflicts."""
    program = data.get("program", "Unknown")
    resources = data.get("resources", [])
    projects = data.get("projects", [])

    # Build allocation map: person -> list of allocations
    person_allocations = defaultdict(list)
    project_allocations = defaultdict(list)

    for alloc in data.get("allocations", []):
        person = alloc.get("person", "Unknown")
        project = alloc.get("project", "Unknown")
        pct = alloc.get("allocation_pct", 0)
        role = alloc.get("role", "Team Member")
        period = alloc.get("period", "Current")

        person_allocations[person].append({
            "project": project,
            "allocation_pct": pct,
            "role": role,
            "period": period,
        })
        project_allocations[project].append({
            "person": person,
            "allocation_pct": pct,
            "role": role,
        })

    # Person-level analysis
    person_results = []
    over_allocated = []
    under_allocated = []

    for person, allocs in person_allocations.items():
        total_pct = sum(a["allocation_pct"] for a in allocs)
        project_count = len(allocs)

        status = "Balanced"
        if total_pct > 100:
            status = "Over-Allocated"
            over_allocated.append({"person": person, "total_pct": total_pct, "projects": project_count})
        elif total_pct < 50:
            status = "Under-Utilized"
            under_allocated.append({"person": person, "total_pct": total_pct, "projects": project_count})
        elif total_pct < 70:
            status = "Available Capacity"

        # Context switching penalty
        switching_penalty = 0
        if project_count >= 4:
            switching_penalty = 40
        elif project_count == 3:
            switching_penalty = 20
        elif project_count == 2:
            switching_penalty = 10
        effective_capacity = max(0, total_pct - switching_penalty)

        person_results.append({
            "person": person,
            "total_allocation_pct": total_pct,
            "effective_capacity_pct": effective_capacity,
            "project_count": project_count,
            "context_switching_penalty_pct": switching_penalty,
            "status": status,
            "allocations": allocs,
        })

    person_results.sort(key=lambda x: x["total_allocation_pct"], reverse=True)

    # Project-level analysis
    project_results = []
    for proj_name in set(a["project"] for allocs in person_allocations.values() for a in allocs):
        allocs = project_allocations.get(proj_name, [])
        total_fte = sum(a["allocation_pct"] for a in allocs) / 100
        headcount = len(allocs)
        roles = list(set(a["role"] for a in allocs))

        project_results.append({
            "project": proj_name,
            "total_fte": round(total_fte, 1),
            "headcount": headcount,
            "roles": roles,
            "team": [{"person": a["person"], "pct": a["allocation_pct"], "role": a["role"]} for a in allocs],
        })

    project_results.sort(key=lambda x: x["total_fte"], reverse=True)

    # Summary metrics
    total_people = len(person_allocations)
    total_fte = sum(p["total_allocation_pct"] for p in person_results) / 100
    avg_utilization = sum(p["total_allocation_pct"] for p in person_results) / total_people if total_people > 0 else 0
    avg_projects_per_person = sum(p["project_count"] for p in person_results) / total_people if total_people > 0 else 0

    # Recommendations
    recs = []
    if over_allocated:
        for oa in over_allocated:
            recs.append(f"{oa['person']} is at {oa['total_pct']}% across {oa['projects']} projects. Reduce allocation to <=100% to prevent burnout and quality issues.")
    if under_allocated:
        names = [ua["person"] for ua in under_allocated]
        recs.append(f"Under-utilized: {', '.join(names)}. Consider reallocating to projects with resource gaps.")

    high_switching = [p for p in person_results if p["context_switching_penalty_pct"] >= 20]
    if high_switching:
        for hs in high_switching:
            recs.append(f"{hs['person']} works on {hs['project_count']} projects (effective capacity: {hs['effective_capacity_pct']}%). Consolidate to max 2 projects for productivity.")

    if avg_utilization > 95:
        recs.append("Team is near full utilization with no slack. Add buffer capacity (aim for 80-85% utilization) to absorb unplanned work.")

    if not recs:
        recs.append("Resource allocation looks balanced. Review monthly to catch emerging conflicts early.")

    return {
        "program": program,
        "summary": {
            "total_people": total_people,
            "total_fte": round(total_fte, 1),
            "avg_utilization_pct": round(avg_utilization, 1),
            "avg_projects_per_person": round(avg_projects_per_person, 1),
            "over_allocated_count": len(over_allocated),
            "under_utilized_count": len(under_allocated),
        },
        "people": person_results,
        "projects": project_results,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    """Print human-readable resource allocation report."""
    s = result["summary"]
    print(f"\nResource Allocation: {result['program']}")
    print("=" * 70)
    print(f"People: {s['total_people']}  |  Total FTE: {s['total_fte']}  |  Avg Utilization: {s['avg_utilization_pct']:.0f}%")
    print(f"Avg Projects/Person: {s['avg_projects_per_person']:.1f}  |  Over-allocated: {s['over_allocated_count']}  |  Under-utilized: {s['under_utilized_count']}")

    print(f"\nPerson Allocation:")
    print(f"  {'Person':<20} {'Total':>6} {'Effective':>10} {'Projects':>9} {'Status'}")
    print(f"  {'-'*20} {'-'*6} {'-'*10} {'-'*9} {'-'*15}")
    for p in result["people"]:
        print(f"  {p['person']:<20} {p['total_allocation_pct']:>5}% {p['effective_capacity_pct']:>9}% {p['project_count']:>9} {p['status']}")

    print(f"\nProject Staffing:")
    for proj in result["projects"]:
        print(f"  {proj['project']}: {proj['total_fte']:.1f} FTE ({proj['headcount']} people)")
        for member in proj["team"]:
            print(f"    - {member['person']}: {member['pct']}% ({member['role']})")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    """Print example resource data JSON."""
    example = {
        "program": "Digital Transformation",
        "allocations": [
            {"person": "Alice Chen", "project": "API Migration", "allocation_pct": 80, "role": "Tech Lead"},
            {"person": "Alice Chen", "project": "Frontend Rebuild", "allocation_pct": 20, "role": "Advisor"},
            {"person": "Bob Martinez", "project": "Frontend Rebuild", "allocation_pct": 100, "role": "Engineer"},
            {"person": "Carol Davis", "project": "API Migration", "allocation_pct": 50, "role": "Engineer"},
            {"person": "Carol Davis", "project": "Analytics Platform", "allocation_pct": 50, "role": "Engineer"},
            {"person": "Carol Davis", "project": "DevOps Modernization", "allocation_pct": 30, "role": "Consultant"},
            {"person": "Dave Wilson", "project": "Analytics Platform", "allocation_pct": 40, "role": "Data Engineer"},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and optimize resource allocation across projects."
    )
    parser.add_argument("--resources", type=str, help="Path to resource allocation JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example resource data and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.resources:
        parser.error("--resources is required (use --example to see the expected format)")

    data = load_data(args.resources)
    result = analyze_resources(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
