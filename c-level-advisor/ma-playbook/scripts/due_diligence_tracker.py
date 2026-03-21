#!/usr/bin/env python3
"""Due Diligence Tracker - Track DD items across 8 domains with priority and red flags.

Manage due diligence items for M&A transactions across financial, technical, legal,
people, market, customers, product, and security domains. Tracks status, priority,
and surfaces red flags.

Usage:
    python due_diligence_tracker.py add --domain financial --item "Revenue recognition audit" --priority 1
    python due_diligence_tracker.py list --domain technical
    python due_diligence_tracker.py report --json
"""

import argparse
import json
import os
import sys
from datetime import datetime

DEFAULT_STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dd_data.json")

DOMAINS = {
    "financial": {"name": "Financial", "owner": "CFO", "key_questions": ["Revenue quality?", "Customer concentration?", "Burn rate?", "Deferred revenue?"], "red_flags": ["> 30% from 1 customer", "Declining margins", "Hidden liabilities", "Aggressive revenue recognition"]},
    "technical": {"name": "Technical", "owner": "CTO", "key_questions": ["Code quality?", "Tech debt?", "Architecture fit?", "Security posture?"], "red_flags": ["Monolith with no tests", "No CI/CD", "Critical security gaps", "Key person dependency"]},
    "legal": {"name": "Legal", "owner": "Legal Counsel", "key_questions": ["IP ownership?", "Pending litigation?", "Contract assignability?"], "red_flags": ["Key IP owned by individuals", "Active lawsuits", "Non-assignable contracts"]},
    "people": {"name": "People", "owner": "CHRO", "key_questions": ["Key person risk?", "Culture fit?", "Retention likelihood?"], "red_flags": ["Founders with no lockup", "Team wants to leave", "Culture mismatch"]},
    "market": {"name": "Market", "owner": "CEO/CPO", "key_questions": ["Market position?", "Competitive threats?", "Customer satisfaction?"], "red_flags": ["Declining market share", "Commoditizing market", "Low NPS"]},
    "customers": {"name": "Customers", "owner": "CRO/CPO", "key_questions": ["Churn rate?", "NPS?", "Contract terms?", "Expansion potential?"], "red_flags": ["High churn", "Short contracts", "Declining usage"]},
    "product": {"name": "Product", "owner": "CPO", "key_questions": ["PMF evidence?", "Roadmap alignment?", "Technical overlap?"], "red_flags": ["No retention data", "Divergent roadmap", "Redundant technology"]},
    "security": {"name": "Security", "owner": "CISO", "key_questions": ["Compliance status?", "Incident history?", "Data practices?"], "red_flags": ["No SOC 2", "History of breaches", "Poor data handling"]}
}

PRIORITIES = {1: "Deal-breaker (Week 1-2)", 2: "Valuation impact (Week 2-4)", 3: "Integration planning (Week 3-6)", 4: "Post-close optimization (Week 4-8)"}
STATUSES = ["not-started", "in-progress", "complete", "red-flag", "clear"]


def load_data(store_path):
    if os.path.exists(store_path):
        with open(store_path, "r") as f:
            return json.load(f)
    return {"items": [], "next_id": 1, "deal_name": "", "created": datetime.now().strftime("%Y-%m-%d")}


def save_data(data, store_path):
    with open(store_path, "w") as f:
        json.dump(data, f, indent=2)


def add_item(data, domain, item, priority, assignee="", notes=""):
    dd_item = {
        "id": data["next_id"],
        "domain": domain,
        "item": item,
        "priority": priority,
        "priority_label": PRIORITIES.get(priority, "Unknown"),
        "status": "not-started",
        "assignee": assignee or DOMAINS[domain]["owner"],
        "notes": notes,
        "red_flag": False,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "updated": datetime.now().strftime("%Y-%m-%d")
    }
    data["items"].append(dd_item)
    data["next_id"] += 1
    return dd_item


def update_item(data, item_id, status=None, red_flag=None, notes=None):
    for item in data["items"]:
        if item["id"] == item_id:
            if status:
                item["status"] = status
            if red_flag is not None:
                item["red_flag"] = red_flag
                if red_flag:
                    item["status"] = "red-flag"
            if notes:
                item["notes"] = notes
            item["updated"] = datetime.now().strftime("%Y-%m-%d")
            return item
    return None


def generate_report(data):
    items = data["items"]
    total = len(items)

    by_domain = {}
    for d_key, d_info in DOMAINS.items():
        domain_items = [i for i in items if i["domain"] == d_key]
        completed = len([i for i in domain_items if i["status"] in ("complete", "clear")])
        red_flags = [i for i in domain_items if i["red_flag"]]
        by_domain[d_key] = {
            "name": d_info["name"],
            "total": len(domain_items),
            "completed": completed,
            "completion_pct": round(completed / len(domain_items) * 100) if domain_items else 0,
            "red_flags": len(red_flags),
            "red_flag_items": [{"id": r["id"], "item": r["item"]} for r in red_flags]
        }

    by_priority = {}
    for p, label in PRIORITIES.items():
        p_items = [i for i in items if i["priority"] == p]
        completed = len([i for i in p_items if i["status"] in ("complete", "clear")])
        by_priority[p] = {"label": label, "total": len(p_items), "completed": completed}

    all_red_flags = [i for i in items if i["red_flag"]]
    overall_completion = round(len([i for i in items if i["status"] in ("complete", "clear")]) / total * 100) if total else 0

    deal_status = "ON TRACK"
    if len(all_red_flags) > 0:
        p1_flags = [f for f in all_red_flags if f["priority"] == 1]
        if p1_flags:
            deal_status = "AT RISK - Deal-breaker red flags identified"
        else:
            deal_status = "CAUTION - Red flags identified (non-deal-breaker)"

    return {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "deal_name": data.get("deal_name", ""),
        "overall_completion": overall_completion,
        "deal_status": deal_status,
        "total_items": total,
        "red_flags_count": len(all_red_flags),
        "by_domain": by_domain,
        "by_priority": by_priority,
        "red_flags": [{"id": f["id"], "domain": f["domain"], "item": f["item"], "priority": f["priority"], "notes": f["notes"]} for f in all_red_flags],
        "items": items
    }


def print_report_human(report):
    print(f"\n{'='*70}")
    print(f"DUE DILIGENCE REPORT" + (f" - {report['deal_name']}" if report["deal_name"] else ""))
    print(f"Date: {report['report_date']}")
    print(f"{'='*70}\n")

    print(f"STATUS: {report['deal_status']}")
    print(f"Overall Completion: {report['overall_completion']}% ({report['total_items']} items)")
    print(f"Red Flags: {report['red_flags_count']}\n")

    print("BY DOMAIN:")
    print("-" * 60)
    for d_key, d_data in report["by_domain"].items():
        if d_data["total"] > 0:
            bar = "#" * (d_data["completion_pct"] // 10) + "." * (10 - d_data["completion_pct"] // 10)
            flag_indicator = f" [!{d_data['red_flags']} RED FLAGS]" if d_data["red_flags"] else ""
            print(f"  {d_data['name']:<15s} [{bar}] {d_data['completion_pct']:>3}% ({d_data['completed']}/{d_data['total']}){flag_indicator}")

    print("\nBY PRIORITY:")
    for p, p_data in report["by_priority"].items():
        if p_data["total"] > 0:
            print(f"  P{p}: {p_data['label']:<35s} {p_data['completed']}/{p_data['total']} complete")

    if report["red_flags"]:
        print(f"\nRED FLAGS ({report['red_flags_count']}):")
        print("-" * 60)
        for f in report["red_flags"]:
            print(f"  [!] P{f['priority']} {f['domain']}: {f['item']}")
            if f["notes"]:
                print(f"      Notes: {f['notes']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Track M&A due diligence items")
    subparsers = parser.add_subparsers(dest="command")

    add_p = subparsers.add_parser("add", help="Add DD item")
    add_p.add_argument("--domain", required=True, choices=list(DOMAINS.keys()))
    add_p.add_argument("--item", required=True, help="DD item description")
    add_p.add_argument("--priority", type=int, required=True, choices=[1,2,3,4])
    add_p.add_argument("--assignee", default="")
    add_p.add_argument("--notes", default="")
    add_p.add_argument("--json", action="store_true")
    add_p.add_argument("--store", default=DEFAULT_STORE)

    update_p = subparsers.add_parser("update", help="Update DD item")
    update_p.add_argument("--id", type=int, required=True)
    update_p.add_argument("--status", choices=STATUSES)
    update_p.add_argument("--red-flag", action="store_true")
    update_p.add_argument("--notes", default="")
    update_p.add_argument("--json", action="store_true")
    update_p.add_argument("--store", default=DEFAULT_STORE)

    list_p = subparsers.add_parser("list", help="List DD items")
    list_p.add_argument("--domain", choices=list(DOMAINS.keys()))
    list_p.add_argument("--priority", type=int, choices=[1,2,3,4])
    list_p.add_argument("--json", action="store_true")
    list_p.add_argument("--store", default=DEFAULT_STORE)

    report_p = subparsers.add_parser("report", help="Full DD report")
    report_p.add_argument("--json", action="store_true")
    report_p.add_argument("--store", default=DEFAULT_STORE)

    init_p = subparsers.add_parser("init", help="Initialize DD tracker with standard items")
    init_p.add_argument("--deal-name", required=True)
    init_p.add_argument("--json", action="store_true")
    init_p.add_argument("--store", default=DEFAULT_STORE)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    data = load_data(args.store)

    if args.command == "init":
        data["deal_name"] = args.deal_name
        # Add standard DD items
        standard_items = [
            ("financial", "Revenue recognition verification", 1),
            ("financial", "Customer concentration analysis", 1),
            ("financial", "Cash position and burn rate verification", 1),
            ("financial", "Liability inventory (known and contingent)", 1),
            ("financial", "Cohort retention analysis", 2),
            ("technical", "Code quality and architecture review", 2),
            ("technical", "Tech debt assessment", 2),
            ("technical", "Security posture evaluation", 1),
            ("technical", "CI/CD and deployment practices", 3),
            ("legal", "IP ownership verification", 1),
            ("legal", "Pending litigation review", 1),
            ("legal", "Contract assignability assessment", 2),
            ("legal", "Employee agreement review", 2),
            ("people", "Key person risk assessment", 1),
            ("people", "Culture compatibility evaluation", 3),
            ("people", "Retention plan for critical talent", 2),
            ("people", "Org structure and compensation review", 3),
            ("market", "Market position assessment", 2),
            ("market", "Competitive landscape analysis", 2),
            ("customers", "Churn rate and NPS verification", 2),
            ("customers", "Contract terms review", 2),
            ("product", "PMF evidence review", 2),
            ("product", "Roadmap alignment assessment", 3),
            ("security", "Compliance certification status", 2),
            ("security", "Incident history review", 2),
        ]
        for domain, item, priority in standard_items:
            add_item(data, domain, item, priority)
        save_data(data, args.store)
        if args.json:
            print(json.dumps({"deal_name": args.deal_name, "items_created": len(standard_items)}, indent=2))
        else:
            print(f"DD tracker initialized for '{args.deal_name}' with {len(standard_items)} standard items")

    elif args.command == "add":
        item = add_item(data, args.domain, args.item, args.priority, args.assignee, args.notes)
        save_data(data, args.store)
        if args.json:
            print(json.dumps(item, indent=2))
        else:
            print(f"DD item #{item['id']} added: [{args.domain}] {args.item}")

    elif args.command == "update":
        item = update_item(data, args.id, args.status, args.red_flag if args.red_flag else None, args.notes)
        if item:
            save_data(data, args.store)
            if args.json:
                print(json.dumps(item, indent=2))
            else:
                print(f"DD item #{item['id']} updated: {item['status']}" + (" [RED FLAG]" if item["red_flag"] else ""))
        else:
            print(f"Error: Item #{args.id} not found", file=sys.stderr)
            sys.exit(1)

    elif args.command == "list":
        items = data["items"]
        if args.domain:
            items = [i for i in items if i["domain"] == args.domain]
        if args.priority:
            items = [i for i in items if i["priority"] == args.priority]
        if args.json:
            print(json.dumps(items, indent=2))
        else:
            for i in items:
                flag = "[!]" if i["red_flag"] else "   "
                print(f"  {flag} #{i['id']:>3} P{i['priority']} [{i['domain']:<10s}] {i['status']:<12s} {i['item']}")

    elif args.command == "report":
        report = generate_report(data)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_report_human(report)


if __name__ == "__main__":
    main()
