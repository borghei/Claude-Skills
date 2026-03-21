#!/usr/bin/env python3
"""Stakeholder Mapper - Map stakeholders by influence, interest, and communication needs.

Build and maintain a stakeholder map with influence/interest scoring, communication
frequency recommendations, and engagement strategy. Stored in local JSON for persistence.

Usage:
    python stakeholder_mapper.py add --name "Board of Directors" --influence high --interest high --frequency quarterly
    python stakeholder_mapper.py list
    python stakeholder_mapper.py matrix
    python stakeholder_mapper.py report --json
"""

import argparse
import json
import os
import sys
from datetime import datetime

DEFAULT_STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stakeholder_data.json")

INFLUENCE_LEVELS = {"low": 1, "medium": 2, "high": 3}
INTEREST_LEVELS = {"low": 1, "medium": 2, "high": 3}

QUADRANT_STRATEGIES = {
    "manage_closely": {
        "quadrant": "High Influence / High Interest",
        "strategy": "Manage Closely - key players who need regular, detailed communication",
        "actions": [
            "Engage frequently and proactively",
            "Involve in decision-making where appropriate",
            "Anticipate their concerns and address preemptively",
            "Use face-to-face or video communication"
        ],
        "recommended_frequency": "Weekly or bi-weekly"
    },
    "keep_satisfied": {
        "quadrant": "High Influence / Low Interest",
        "strategy": "Keep Satisfied - powerful but not deeply engaged; keep informed without overwhelming",
        "actions": [
            "Provide executive summaries, not detailed reports",
            "Engage on decisions that affect their domain",
            "Anticipate their needs and proactively address",
            "Minimize effort required from them"
        ],
        "recommended_frequency": "Monthly"
    },
    "keep_informed": {
        "quadrant": "Low Influence / High Interest",
        "strategy": "Keep Informed - engaged supporters who need updates to maintain confidence",
        "actions": [
            "Regular updates through scalable channels",
            "Invite feedback and input",
            "Leverage their enthusiasm for internal advocacy",
            "Provide channels for questions"
        ],
        "recommended_frequency": "Bi-weekly to monthly"
    },
    "monitor": {
        "quadrant": "Low Influence / Low Interest",
        "strategy": "Monitor - minimal effort; keep on radar without over-investing",
        "actions": [
            "Include in broad communications (all-hands, company updates)",
            "Do not require their engagement",
            "Watch for changes in influence or interest",
            "Periodic check-in to reassess positioning"
        ],
        "recommended_frequency": "Quarterly"
    }
}


def get_quadrant(influence, interest):
    inf = INFLUENCE_LEVELS.get(influence, 2)
    int_ = INTEREST_LEVELS.get(interest, 2)
    if inf >= 2 and int_ >= 2:
        return "manage_closely"
    elif inf >= 2 and int_ < 2:
        return "keep_satisfied"
    elif inf < 2 and int_ >= 2:
        return "keep_informed"
    return "monitor"


def load_data(store_path):
    if os.path.exists(store_path):
        with open(store_path, "r") as f:
            return json.load(f)
    return {"stakeholders": [], "next_id": 1}


def save_data(data, store_path):
    with open(store_path, "w") as f:
        json.dump(data, f, indent=2)


def add_stakeholder(data, name, influence, interest, frequency, role="", notes=""):
    quadrant = get_quadrant(influence, interest)
    strategy = QUADRANT_STRATEGIES[quadrant]

    stakeholder = {
        "id": data["next_id"],
        "name": name,
        "role": role,
        "influence": influence,
        "interest": interest,
        "frequency": frequency,
        "quadrant": quadrant,
        "quadrant_label": strategy["quadrant"],
        "strategy": strategy["strategy"],
        "notes": notes,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "last_communication": None
    }
    data["stakeholders"].append(stakeholder)
    data["next_id"] += 1
    return stakeholder


def generate_matrix(data):
    """Generate stakeholder matrix visualization."""
    matrix = {q: [] for q in QUADRANT_STRATEGIES}
    for s in data["stakeholders"]:
        matrix[s["quadrant"]].append({"name": s["name"], "role": s["role"]})
    return matrix


def generate_report(data):
    stakeholders = data["stakeholders"]
    matrix = generate_matrix(data)

    by_quadrant = {}
    for q, names in matrix.items():
        by_quadrant[q] = {
            "label": QUADRANT_STRATEGIES[q]["quadrant"],
            "count": len(names),
            "stakeholders": names,
            "strategy": QUADRANT_STRATEGIES[q]["strategy"],
            "actions": QUADRANT_STRATEGIES[q]["actions"]
        }

    return {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "total_stakeholders": len(stakeholders),
        "by_quadrant": by_quadrant,
        "stakeholders": stakeholders,
        "communication_plan": [
            {
                "name": s["name"],
                "frequency": s["frequency"],
                "quadrant": s["quadrant_label"],
                "last_communication": s["last_communication"] or "Never"
            }
            for s in sorted(stakeholders, key=lambda x: INFLUENCE_LEVELS.get(x["influence"], 0), reverse=True)
        ]
    }


def print_matrix_human(matrix):
    print(f"\n{'='*70}")
    print(f"STAKEHOLDER MATRIX")
    print(f"{'='*70}\n")

    print(f"                    HIGH INTEREST          LOW INTEREST")
    print(f"                  +-----------------------+-----------------------+")
    manage = [s["name"] for s in matrix.get("manage_closely", [])]
    satisfy = [s["name"] for s in matrix.get("keep_satisfied", [])]
    print(f"  HIGH INFLUENCE  | MANAGE CLOSELY        | KEEP SATISFIED        |")
    for i in range(max(len(manage), len(satisfy), 1)):
        m = manage[i] if i < len(manage) else ""
        s = satisfy[i] if i < len(satisfy) else ""
        print(f"                  | {m:<21s} | {s:<21s} |")
    print(f"                  +-----------------------+-----------------------+")
    inform = [s["name"] for s in matrix.get("keep_informed", [])]
    monitor = [s["name"] for s in matrix.get("monitor", [])]
    print(f"  LOW INFLUENCE   | KEEP INFORMED         | MONITOR               |")
    for i in range(max(len(inform), len(monitor), 1)):
        inf = inform[i] if i < len(inform) else ""
        mon = monitor[i] if i < len(monitor) else ""
        print(f"                  | {inf:<21s} | {mon:<21s} |")
    print(f"                  +-----------------------+-----------------------+")
    print()


def print_report_human(report):
    print(f"\n{'='*70}")
    print(f"STAKEHOLDER MAP REPORT - {report['report_date']}")
    print(f"Total Stakeholders: {report['total_stakeholders']}")
    print(f"{'='*70}\n")

    for q_key, q_data in report["by_quadrant"].items():
        if q_data["count"] > 0:
            print(f"\n{q_data['label']} ({q_data['count']})")
            print(f"  Strategy: {q_data['strategy']}")
            for s in q_data["stakeholders"]:
                print(f"    - {s['name']}" + (f" ({s['role']})" if s["role"] else ""))

    print(f"\nCOMMUNICATION PLAN:")
    print("-" * 60)
    for cp in report["communication_plan"]:
        print(f"  {cp['name']:<25s} {cp['frequency']:<12s} Last: {cp['last_communication']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Map stakeholders by influence and interest")
    subparsers = parser.add_subparsers(dest="command")

    add_p = subparsers.add_parser("add", help="Add stakeholder")
    add_p.add_argument("--name", required=True)
    add_p.add_argument("--influence", required=True, choices=["low", "medium", "high"])
    add_p.add_argument("--interest", required=True, choices=["low", "medium", "high"])
    add_p.add_argument("--frequency", default="monthly", choices=["weekly", "bi-weekly", "monthly", "quarterly", "annually"])
    add_p.add_argument("--role", default="")
    add_p.add_argument("--notes", default="")
    add_p.add_argument("--json", action="store_true")
    add_p.add_argument("--store", default=DEFAULT_STORE)

    list_p = subparsers.add_parser("list", help="List stakeholders")
    list_p.add_argument("--json", action="store_true")
    list_p.add_argument("--store", default=DEFAULT_STORE)

    matrix_p = subparsers.add_parser("matrix", help="Show stakeholder matrix")
    matrix_p.add_argument("--json", action="store_true")
    matrix_p.add_argument("--store", default=DEFAULT_STORE)

    report_p = subparsers.add_parser("report", help="Full stakeholder report")
    report_p.add_argument("--json", action="store_true")
    report_p.add_argument("--store", default=DEFAULT_STORE)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    data = load_data(args.store)

    if args.command == "add":
        s = add_stakeholder(data, args.name, args.influence, args.interest, args.frequency, args.role, args.notes)
        save_data(data, args.store)
        if args.json:
            print(json.dumps(s, indent=2))
        else:
            print(f"Stakeholder #{s['id']} added: {s['name']} -> {s['quadrant_label']}")

    elif args.command == "list":
        if args.json:
            print(json.dumps(data["stakeholders"], indent=2))
        else:
            for s in data["stakeholders"]:
                print(f"  #{s['id']} {s['name']:<25s} Inf:{s['influence']:<6s} Int:{s['interest']:<6s} -> {s['quadrant_label']}")

    elif args.command == "matrix":
        matrix = generate_matrix(data)
        if args.json:
            print(json.dumps(matrix, indent=2))
        else:
            print_matrix_human(matrix)

    elif args.command == "report":
        report = generate_report(data)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_report_human(report)


if __name__ == "__main__":
    main()
