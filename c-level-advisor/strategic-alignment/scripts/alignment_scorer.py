#!/usr/bin/env python3
"""Alignment Scorer - Calculate alignment score across 5 dimensions with trend tracking.

Scores strategy clarity, cascade completeness, conflict resolution, coverage,
and communication effectiveness. Compares to previous score for trend analysis.

Usage:
    python alignment_scorer.py --clarity 8 --cascade 6 --conflicts 7 --coverage 5 --communication 6
    python alignment_scorer.py --clarity 8 --cascade 6 --conflicts 7 --coverage 5 --communication 6 --previous-score 28 --json
"""

import argparse
import json
import sys
from datetime import datetime

DIMENSIONS = {
    "clarity": {
        "name": "Strategy Clarity",
        "question": "Can 5 people from different teams state the strategy consistently?",
        "scoring_guide": {
            "9-10": "All 5 give the same answer with specifics",
            "7-8": "4 of 5 give similar answers",
            "5-6": "3 agree, some confusion on details",
            "3-4": "Only 2 agree, strategy unclear to most",
            "1-2": "No shared understanding of strategy"
        },
        "improvement_actions": {
            "low": [
                "Rewrite strategy as one falsifiable sentence",
                "CEO communicates strategy through 7+ channels over 2 weeks",
                "Re-run 5-person test after 2 weeks"
            ],
            "medium": [
                "Clarify the specific parts causing confusion",
                "Add visual strategy map to all team areas",
                "Include strategy restatement in monthly all-hands"
            ]
        }
    },
    "cascade": {
        "name": "Cascade Completeness",
        "question": "Do all team goals connect to company goals?",
        "scoring_guide": {
            "9-10": "Every team OKR traces to a company OKR with clear impact",
            "7-8": "90%+ connected, minor gaps",
            "5-6": "70-90% connected, some orphan goals",
            "3-4": "50-70% connected, significant orphan goals",
            "1-2": "Most team goals disconnected from company strategy"
        },
        "improvement_actions": {
            "low": [
                "Map every team OKR to a company OKR (connect or cut workshop)",
                "Require parent OKR for every new team goal",
                "Review cascade at start of every quarter"
            ],
            "medium": [
                "Address specific orphan goals identified",
                "Strengthen goal-setting process with cascade template",
                "Quarterly cascade validation review"
            ]
        }
    },
    "conflicts": {
        "name": "Conflict Detection",
        "question": "Have cross-team OKR conflicts been reviewed and resolved?",
        "scoring_guide": {
            "9-10": "All potential conflicts identified and resolved with shared metrics",
            "7-8": "Most conflicts addressed, minor tensions remain",
            "5-6": "Some conflicts identified but not all resolved",
            "3-4": "Known conflicts unaddressed",
            "1-2": "No conflict detection process exists"
        },
        "improvement_actions": {
            "low": [
                "Run cross-functional OKR review to identify conflicts",
                "Create shared metrics for conflicting team pairs",
                "Establish escalation process for unresolved conflicts"
            ],
            "medium": [
                "Review and resolve remaining identified conflicts",
                "Add conflict check to quarterly planning process",
                "Track shared metrics monthly"
            ]
        }
    },
    "coverage": {
        "name": "Coverage",
        "question": "Does each company OKR have explicit team ownership?",
        "scoring_guide": {
            "9-10": "Every company OKR has 2+ teams supporting it with clear ownership",
            "7-8": "Most company OKRs covered, 1 may be light",
            "5-6": "1-2 company OKRs have no team support",
            "3-4": "Multiple company OKRs unsupported",
            "1-2": "Company OKRs exist on paper but no teams actively support them"
        },
        "improvement_actions": {
            "low": [
                "Assign explicit team ownership to every company OKR",
                "Ensure resource allocation matches stated priorities",
                "CEO reviews coverage gaps with leadership team"
            ],
            "medium": [
                "Strengthen support for lightly-covered OKRs",
                "Review resource allocation vs priority ranking",
                "Add coverage check to quarterly planning"
            ]
        }
    },
    "communication": {
        "name": "Communication",
        "question": "Do teams' behaviors reflect the strategy?",
        "scoring_guide": {
            "9-10": "Team decisions and resource allocation clearly reflect strategy",
            "7-8": "Mostly aligned, occasional drift",
            "5-6": "Strategy communicated but not consistently reflected in daily work",
            "3-4": "Significant gap between stated strategy and team behavior",
            "1-2": "Strategy is a document nobody references"
        },
        "improvement_actions": {
            "low": [
                "Increase communication frequency (weekly, not quarterly)",
                "Add skip-level communication to reduce message decay",
                "Show resource proof: money and time follow stated words"
            ],
            "medium": [
                "Vary communication format (written, visual, verbal)",
                "Include strategy connection in team standups",
                "Monthly strategy check-in at all-hands"
            ]
        }
    }
}

SCORE_INTERPRETATION = [
    {"range": "45-50", "status": "Excellent", "action": "Maintain. Quarterly check sufficient."},
    {"range": "35-44", "status": "Good", "action": "Address specific weak areas in next OKR cycle."},
    {"range": "20-34", "status": "Misalignment Costing You", "action": "Immediate attention. Workshop within 2 weeks."},
    {"range": "0-19", "status": "Strategic Drift", "action": "Crisis-level intervention. CEO-led realignment."}
]


def score_alignment(scores, previous_score=None):
    total = sum(scores.values())

    dimension_results = []
    for dim_key, score in scores.items():
        dim_info = DIMENSIONS[dim_key]
        level = "low" if score < 5 else "medium"
        actions = dim_info["improvement_actions"].get(level, [])

        dimension_results.append({
            "dimension": dim_info["name"],
            "key": dim_key,
            "score": score,
            "question": dim_info["question"],
            "scoring_guide": dim_info["scoring_guide"],
            "improvement_actions": actions if score < 8 else []
        })

    # Determine status
    if total >= 45:
        status = "Excellent"
        action = "Maintain. Quarterly check sufficient."
    elif total >= 35:
        status = "Good"
        action = "Address specific weak areas in next OKR cycle."
    elif total >= 20:
        status = "Misalignment Costing You"
        action = "Immediate attention. Workshop within 2 weeks."
    else:
        status = "Strategic Drift"
        action = "Crisis-level intervention. CEO-led realignment."

    # Trend
    trend = None
    if previous_score is not None:
        delta = total - previous_score
        if delta > 2:
            trend = {"direction": "IMPROVING", "delta": delta, "previous": previous_score}
        elif delta < -2:
            trend = {"direction": "DECLINING", "delta": delta, "previous": previous_score}
        else:
            trend = {"direction": "STABLE", "delta": delta, "previous": previous_score}

    # Weakest dimension
    weakest = min(dimension_results, key=lambda d: d["score"])
    strongest = max(dimension_results, key=lambda d: d["score"])

    return {
        "assessment_date": datetime.now().strftime("%Y-%m-%d"),
        "total_score": total,
        "max_score": 50,
        "status": status,
        "recommended_action": action,
        "trend": trend,
        "dimensions": dimension_results,
        "weakest": {"dimension": weakest["dimension"], "score": weakest["score"]},
        "strongest": {"dimension": strongest["dimension"], "score": strongest["score"]},
        "priority_improvements": [d for d in dimension_results if d["score"] < 7],
        "score_interpretation": SCORE_INTERPRETATION
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"STRATEGIC ALIGNMENT SCORE")
    print(f"Date: {result['assessment_date']}")
    print(f"{'='*70}\n")

    print(f"TOTAL: {result['total_score']}/{result['max_score']} ({result['status']})")

    if result["trend"]:
        t = result["trend"]
        arrow = "^" if t["direction"] == "IMPROVING" else "v" if t["direction"] == "DECLINING" else "="
        print(f"Trend: {arrow} {t['direction']} ({'+' if t['delta'] > 0 else ''}{t['delta']} from {t['previous']})")

    print(f"Action: {result['recommended_action']}\n")

    print("DIMENSIONS:")
    print("-" * 60)
    for d in sorted(result["dimensions"], key=lambda x: -x["score"]):
        bar = "#" * d["score"] + "." * (10 - d["score"])
        print(f"  {d['dimension']:<25s} {d['score']:>2}/10  [{bar}]")

    print(f"\nStrongest: {result['strongest']['dimension']} ({result['strongest']['score']}/10)")
    print(f"Weakest:   {result['weakest']['dimension']} ({result['weakest']['score']}/10)")

    if result["priority_improvements"]:
        print(f"\nPRIORITY IMPROVEMENTS:")
        for d in result["priority_improvements"]:
            print(f"\n  {d['dimension']} ({d['score']}/10):")
            for a in d["improvement_actions"]:
                print(f"    -> {a}")

    print(f"\nSCORE GUIDE:")
    for si in result["score_interpretation"]:
        print(f"  {si['range']:<8s} {si['status']:<30s} {si['action']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Calculate strategic alignment score across 5 dimensions")
    parser.add_argument("--clarity", type=int, required=True, help="Strategy clarity (1-10)")
    parser.add_argument("--cascade", type=int, required=True, help="Cascade completeness (1-10)")
    parser.add_argument("--conflicts", type=int, required=True, help="Conflict detection/resolution (1-10)")
    parser.add_argument("--coverage", type=int, required=True, help="OKR coverage (1-10)")
    parser.add_argument("--communication", type=int, required=True, help="Communication effectiveness (1-10)")
    parser.add_argument("--previous-score", type=int, default=None, help="Previous total score for trend comparison")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    for attr in ["clarity", "cascade", "conflicts", "coverage", "communication"]:
        val = getattr(args, attr)
        if val < 1 or val > 10:
            print(f"Error: {attr} must be between 1 and 10", file=sys.stderr)
            sys.exit(1)

    scores = {
        "clarity": args.clarity,
        "cascade": args.cascade,
        "conflicts": args.conflicts,
        "coverage": args.coverage,
        "communication": args.communication
    }

    result = score_alignment(scores, args.previous_score)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
