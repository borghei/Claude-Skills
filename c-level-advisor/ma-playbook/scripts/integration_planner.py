#!/usr/bin/env python3
"""Integration Planner - Generate 100-day post-acquisition integration plan.

Creates a phased integration plan with milestones, owners, and status tracking.
Supports three integration modes: absorb, preserve, and hybrid.

Usage:
    python integration_planner.py --mode absorb --target-name "AcquiredCo" --headcount 25
    python integration_planner.py --mode hybrid --target-name "TargetCo" --headcount 50 --has-product-overlap --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

INTEGRATION_MODES = {
    "absorb": {
        "name": "Full Absorption",
        "description": "Fully integrate acquired company into acquirer operations",
        "when": "Product overlap, same ICP, maximum synergy potential",
        "risk": "Loss of acquired team culture and key talent",
        "timeline": "Aggressive: 60-90 days for core integration"
    },
    "preserve": {
        "name": "Preserve Independence",
        "description": "Acquired company operates independently with shared backend",
        "when": "Different market/product, brand value, minimal overlap",
        "risk": "Missed synergies, coordination overhead",
        "timeline": "Gradual: 6-12 months for selective integration"
    },
    "hybrid": {
        "name": "Hybrid Integration",
        "description": "Shared backend and infrastructure, independent product and GTM",
        "when": "Complementary products, shared customer base, distinct brands",
        "risk": "Complexity in execution, unclear boundaries",
        "timeline": "Moderate: 90-120 days for core, ongoing for product"
    }
}


def generate_plan(mode, target_name, headcount, has_product_overlap, start_date):
    mode_info = INTEGRATION_MODES[mode]

    phases = []

    # Phase 1: Stabilize (Days 0-30)
    phase1_items = [
        {"item": f"CEO welcome communication to {target_name} team", "owner": "CEO", "day": 0, "priority": "critical", "status": "not-started"},
        {"item": "Customer communication (if acquisition is public)", "owner": "CMO + CRO", "day": 0, "priority": "critical", "status": "not-started"},
        {"item": "Key person 1:1 meetings (schedule within 48 hours)", "owner": "CHRO + CEO", "day": 1, "priority": "critical", "status": "not-started"},
        {"item": "Systems access granted to acquired team", "owner": "CTO", "day": 1, "priority": "critical", "status": "not-started"},
        {"item": "Reporting structure clarified and communicated", "owner": "COO", "day": 1, "priority": "critical", "status": "not-started"},
        {"item": "Compensation and benefits confirmed for all acquired employees", "owner": "CHRO", "day": 3, "priority": "critical", "status": "not-started"},
        {"item": "Integration lead appointed and introduced", "owner": "CEO", "day": 1, "priority": "critical", "status": "not-started"},
        {"item": "Retention bonuses executed for key personnel", "owner": "CHRO", "day": 7, "priority": "high", "status": "not-started"},
        {"item": "Customer success outreach to top 20 accounts", "owner": "CRO", "day": 7, "priority": "high", "status": "not-started"},
        {"item": "IT security audit of acquired systems", "owner": "CISO", "day": 14, "priority": "high", "status": "not-started"},
        {"item": "Cultural integration assessment initiated", "owner": "CHRO", "day": 14, "priority": "medium", "status": "not-started"},
        {"item": "Weekly integration standup established", "owner": "Integration Lead", "day": 7, "priority": "high", "status": "not-started"},
    ]
    phases.append({"phase": 1, "name": "Stabilize", "days": "0-30", "focus": "Retain people, retain customers, establish communication", "items": phase1_items})

    # Phase 2: Integrate (Days 30-60)
    phase2_items = [
        {"item": "IT systems integration plan finalized", "owner": "CTO", "day": 30, "priority": "high", "status": "not-started"},
        {"item": "Tool consolidation plan (identify overlapping tools)", "owner": "CTO + COO", "day": 35, "priority": "medium", "status": "not-started"},
        {"item": "Process mapping: identify redundant and complementary processes", "owner": "COO", "day": 35, "priority": "medium", "status": "not-started"},
        {"item": "Combined org chart finalized and communicated", "owner": "CHRO", "day": 40, "priority": "high", "status": "not-started"},
        {"item": "Unified customer support model defined", "owner": "CRO", "day": 40, "priority": "high", "status": "not-started"},
        {"item": "Financial systems integration (billing, reporting)", "owner": "CFO", "day": 45, "priority": "high", "status": "not-started"},
        {"item": "Email, Slack, and communication platform migration", "owner": "CTO", "day": 45, "priority": "medium", "status": "not-started"},
        {"item": "Brand and marketing alignment decision", "owner": "CMO", "day": 50, "priority": "medium", "status": "not-started"},
    ]

    if has_product_overlap and mode != "preserve":
        phase2_items.append({"item": "Product overlap analysis and roadmap consolidation", "owner": "CPO", "day": 35, "priority": "high", "status": "not-started"})
        phase2_items.append({"item": "Customer migration plan for overlapping products", "owner": "CPO + CRO", "day": 50, "priority": "high", "status": "not-started"})

    phases.append({"phase": 2, "name": "Integrate", "days": "30-60", "focus": "Systems alignment, process merge, team unification", "items": phase2_items})

    # Phase 3: Optimize (Days 60-90)
    phase3_items = [
        {"item": "Cross-sell campaign to combined customer base", "owner": "CRO + CMO", "day": 60, "priority": "high", "status": "not-started"},
        {"item": "Combined product roadmap published", "owner": "CPO", "day": 65, "priority": "high", "status": "not-started"},
        {"item": "Headcount optimization (if planned)", "owner": "CHRO + COO", "day": 70, "priority": "medium", "status": "not-started"},
        {"item": "Vendor contract consolidation", "owner": "CFO + COO", "day": 75, "priority": "medium", "status": "not-started"},
        {"item": "Combined OKRs for next quarter defined", "owner": "COO", "day": 80, "priority": "high", "status": "not-started"},
        {"item": "Integration success metrics assessed", "owner": "Integration Lead", "day": 85, "priority": "high", "status": "not-started"},
    ]
    phases.append({"phase": 3, "name": "Optimize", "days": "60-90", "focus": "Synergy realization, combined roadmap, efficiency gains", "items": phase3_items})

    # Phase 4: Accelerate (Days 90-100)
    phase4_items = [
        {"item": "Joint GTM strategy launched", "owner": "CRO + CMO", "day": 90, "priority": "high", "status": "not-started"},
        {"item": "Integration retrospective conducted", "owner": "Integration Lead", "day": 95, "priority": "high", "status": "not-started"},
        {"item": "100-day integration report to board", "owner": "CEO", "day": 100, "priority": "critical", "status": "not-started"},
        {"item": "Transition from integration to BAU operations", "owner": "COO", "day": 100, "priority": "high", "status": "not-started"},
    ]
    phases.append({"phase": 4, "name": "Accelerate", "days": "90-100", "focus": "Scale combined capabilities, transition to business-as-usual", "items": phase4_items})

    # Calculate all item dates
    total_items = 0
    for phase in phases:
        for item in phase["items"]:
            item["target_date"] = (start_date + timedelta(days=item["day"])).strftime("%Y-%m-%d")
            total_items += 1

    # Success metrics
    success_metrics = [
        {"metric": "Key person retention", "target": ">= 90% at 100 days", "owner": "CHRO"},
        {"metric": "Customer retention", "target": "Zero churn attributable to integration", "owner": "CRO"},
        {"metric": "Systems integrated", "target": "Core systems unified by Day 60", "owner": "CTO"},
        {"metric": "Revenue synergies initiated", "target": "First cross-sell campaign live by Day 60", "owner": "CRO"},
        {"metric": "Employee engagement", "target": "eNPS survey at Day 90 >= baseline", "owner": "CHRO"},
        {"metric": "Customer satisfaction", "target": "NPS maintained or improved at Day 90", "owner": "CPO"},
    ]

    return {
        "plan_date": datetime.now().strftime("%Y-%m-%d"),
        "target_company": target_name,
        "headcount": headcount,
        "integration_mode": mode_info["name"],
        "mode_description": mode_info["description"],
        "mode_risk": mode_info["risk"],
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": (start_date + timedelta(days=100)).strftime("%Y-%m-%d"),
        "total_items": total_items,
        "phases": phases,
        "success_metrics": success_metrics,
        "critical_first_week": [i for phase in phases for i in phase["items"] if i["day"] <= 7]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"100-DAY INTEGRATION PLAN: {result['target_company']}")
    print(f"Mode: {result['integration_mode']}")
    print(f"Period: {result['start_date']} to {result['end_date']}")
    print(f"{'='*70}\n")

    print(f"Headcount: {result['headcount']}")
    print(f"Risk: {result['mode_risk']}")
    print(f"Total Items: {result['total_items']}\n")

    for phase in result["phases"]:
        print(f"\n--- PHASE {phase['phase']}: {phase['name'].upper()} (Days {phase['days']}) ---")
        print(f"Focus: {phase['focus']}")
        for item in sorted(phase["items"], key=lambda x: x["day"]):
            priority_marker = "!" if item["priority"] == "critical" else "*" if item["priority"] == "high" else " "
            print(f"  [{priority_marker}] Day {item['day']:>3}  {item['owner']:<20s}  {item['item']}")

    print(f"\nSUCCESS METRICS:")
    print("-" * 60)
    for m in result["success_metrics"]:
        print(f"  {m['metric']:<30s} Target: {m['target']:<35s} Owner: {m['owner']}")

    print(f"\nCRITICAL FIRST WEEK:")
    for i in sorted(result["critical_first_week"], key=lambda x: x["day"]):
        print(f"  Day {i['day']}: {i['item']} ({i['owner']})")
    print()


def main():
    parser = argparse.ArgumentParser(description="Generate 100-day post-acquisition integration plan")
    parser.add_argument("--mode", required=True, choices=list(INTEGRATION_MODES.keys()), help="Integration mode")
    parser.add_argument("--target-name", required=True, help="Acquired company name")
    parser.add_argument("--headcount", type=int, required=True, help="Acquired company headcount")
    parser.add_argument("--has-product-overlap", action="store_true", help="Product overlap exists")
    parser.add_argument("--start-date", default=None, help="Integration start date (YYYY-MM-DD)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else datetime.now()
    result = generate_plan(args.mode, args.target_name, args.headcount, args.has_product_overlap, start_date)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
