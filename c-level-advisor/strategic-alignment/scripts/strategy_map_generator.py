#!/usr/bin/env python3
"""Strategy Map Generator - Generate balanced scorecard strategy map.

Creates a strategy map linking financial, customer, internal process, and
learning & growth perspectives following Kaplan & Norton's balanced scorecard framework.

Usage:
    python strategy_map_generator.py --objective "Win mid-market healthcare in DACH" --financial "5M ARR by Q4" --customer "NPS > 40" --process "Ship workflow automation" --learning "Hire 3 healthcare domain experts"
    python strategy_map_generator.py --objective "Become category leader" --financial "10M ARR,positive unit economics" --customer "NPS > 50,NRR > 120%" --process "Deploy PLG motion,reduce onboarding time 50%" --learning "Hire VP Product,build data team" --json
"""

import argparse
import json
import sys
from datetime import datetime

PERSPECTIVES = {
    "financial": {
        "name": "Financial Perspective",
        "question": "To succeed financially, how should we appear to our shareholders?",
        "typical_objectives": ["Revenue growth", "Profitability improvement", "Capital efficiency", "Unit economics"],
        "typical_metrics": ["ARR/MRR", "Gross margin", "Burn multiple", "LTV/CAC ratio", "Revenue per employee"]
    },
    "customer": {
        "name": "Customer Perspective",
        "question": "To achieve our vision, how should we appear to our customers?",
        "typical_objectives": ["Customer satisfaction", "Retention", "Market share", "Value delivery"],
        "typical_metrics": ["NPS", "NRR", "CSAT", "Churn rate", "Time to value", "Customer lifetime value"]
    },
    "process": {
        "name": "Internal Process Perspective",
        "question": "To satisfy shareholders and customers, what business processes must we excel at?",
        "typical_objectives": ["Product delivery", "Operational efficiency", "Innovation", "Quality"],
        "typical_metrics": ["Deploy frequency", "Cycle time", "Feature adoption", "MTTR", "OKR completion rate"]
    },
    "learning": {
        "name": "Learning & Growth Perspective",
        "question": "To achieve our vision, how will we sustain our ability to change and improve?",
        "typical_objectives": ["Talent development", "Knowledge management", "Culture", "Technology enablement"],
        "typical_metrics": ["eNPS", "Internal promotion rate", "Training hours", "Time to fill", "Innovation pipeline"]
    }
}


def generate_map(objective, financial, customer, process, learning):
    """Generate strategy map with linkages between perspectives."""
    perspectives = []

    for key, items_str in [("financial", financial), ("customer", customer), ("process", process), ("learning", learning)]:
        items = [i.strip() for i in items_str.split(",") if i.strip()]
        info = PERSPECTIVES[key]
        perspectives.append({
            "perspective": info["name"],
            "key": key,
            "question": info["question"],
            "objectives": items,
            "suggested_metrics": info["typical_metrics"]
        })

    # Generate linkages (how lower perspectives enable upper ones)
    linkages = []

    learning_objs = [i.strip() for i in learning.split(",") if i.strip()]
    process_objs = [i.strip() for i in process.split(",") if i.strip()]
    customer_objs = [i.strip() for i in customer.split(",") if i.strip()]
    financial_objs = [i.strip() for i in financial.split(",") if i.strip()]

    # Learning -> Process
    for l_obj in learning_objs:
        for p_obj in process_objs:
            linkages.append({
                "from_perspective": "Learning & Growth",
                "from_objective": l_obj,
                "to_perspective": "Internal Process",
                "to_objective": p_obj,
                "hypothesis": f"Investing in '{l_obj}' enables us to '{p_obj}'"
            })

    # Process -> Customer
    for p_obj in process_objs:
        for c_obj in customer_objs:
            linkages.append({
                "from_perspective": "Internal Process",
                "from_objective": p_obj,
                "to_perspective": "Customer",
                "to_objective": c_obj,
                "hypothesis": f"Excelling at '{p_obj}' drives '{c_obj}'"
            })

    # Customer -> Financial
    for c_obj in customer_objs:
        for f_obj in financial_objs:
            linkages.append({
                "from_perspective": "Customer",
                "from_objective": c_obj,
                "to_perspective": "Financial",
                "to_objective": f_obj,
                "hypothesis": f"Achieving '{c_obj}' leads to '{f_obj}'"
            })

    # Validation questions
    validation = [
        "Does every Learning objective enable at least one Process objective?",
        "Does every Process objective drive at least one Customer objective?",
        "Does every Customer objective contribute to at least one Financial objective?",
        "Are there Financial objectives with no clear path from lower perspectives?",
        "Is the strategy map simple enough to explain in 5 minutes?"
    ]

    return {
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "strategic_objective": objective,
        "perspectives": perspectives,
        "linkages": linkages,
        "total_objectives": sum(len(p["objectives"]) for p in perspectives),
        "validation_questions": validation,
        "implementation_notes": [
            "Review strategy map quarterly -- update as strategy evolves",
            "Each objective should have 1-2 measurable KPIs",
            "Assign an owner for each objective",
            "Use this map as the basis for OKR cascade to teams",
            "Combine with OKR cascade validator for full alignment check"
        ]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"STRATEGY MAP")
    print(f"Objective: {result['strategic_objective']}")
    print(f"Date: {result['generated_date']}")
    print(f"{'='*70}\n")

    # Visual map (top to bottom)
    for p in result["perspectives"]:
        print(f"  {'='*60}")
        print(f"  {p['perspective'].upper()}")
        print(f"  Question: {p['question']}")
        print(f"  {'='*60}")
        for obj in p["objectives"]:
            print(f"  | {obj}")
        print(f"  Suggested metrics: {', '.join(p['suggested_metrics'][:4])}")
        print(f"          |")
        print(f"          v")

    print(f"\nLINKAGES ({len(result['linkages'])} connections):")
    print("-" * 60)
    for l in result["linkages"]:
        print(f"  {l['from_perspective']} -> {l['to_perspective']}")
        print(f"    {l['hypothesis']}")

    print(f"\nVALIDATION QUESTIONS:")
    for v in result["validation_questions"]:
        print(f"  [ ] {v}")

    print(f"\nIMPLEMENTATION:")
    for n in result["implementation_notes"]:
        print(f"  -> {n}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Generate balanced scorecard strategy map")
    parser.add_argument("--objective", required=True, help="Strategic objective (one sentence)")
    parser.add_argument("--financial", required=True, help="Financial perspective objectives (comma-separated)")
    parser.add_argument("--customer", required=True, help="Customer perspective objectives (comma-separated)")
    parser.add_argument("--process", required=True, help="Internal process objectives (comma-separated)")
    parser.add_argument("--learning", required=True, help="Learning & growth objectives (comma-separated)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = generate_map(args.objective, args.financial, args.customer, args.process, args.learning)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
