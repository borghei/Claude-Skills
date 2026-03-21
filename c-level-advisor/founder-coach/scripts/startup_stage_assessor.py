#!/usr/bin/env python3
"""Startup Stage Assessor - Assess current startup stage and identify founder growth ceiling.

Evaluates company stage based on headcount, ARR, funding, and operational signals.
Maps the founder to their current growth ceiling and provides development recommendations.

Usage:
    python startup_stage_assessor.py --headcount 35 --arr 1200000 --stage series-a
    python startup_stage_assessor.py --headcount 120 --arr 8000000 --stage series-b --has-exec-team --json
"""

import argparse
import json
import sys
from datetime import datetime

CEILINGS = {
    1: {
        "threshold": 15,
        "name": "Ceiling 1: Direct Leadership Limit (~15 people)",
        "problem": "Can't be in every meeting and still think strategically",
        "solution": "Delegate operational decisions, hire first manager",
        "skill_to_build": "Letting go of execution details",
        "signals": [
            "You attend > 80% of meetings in the company",
            "Every decision waits for your input",
            "You are the only person who talks to customers, investors, AND the team",
            "No written processes exist -- everything is in your head"
        ],
        "actions": [
            "Hire your first manager within 60 days",
            "Document top 5 processes you do repeatedly",
            "Delegate one customer-facing responsibility to a team member",
            "Block 4 hours/week for thinking time (not meetings)"
        ]
    },
    2: {
        "threshold": 50,
        "name": "Ceiling 2: Management Layer (~50 people)",
        "problem": "Your personal style creates culture problems at scale",
        "solution": "Hire executive team, evolve leadership style",
        "skill_to_build": "Leading through others, not doing yourself",
        "signals": [
            "New hires don't understand the culture because it was never written down",
            "You micromanage managers because you don't trust their judgment yet",
            "Team coordination requires you as the hub",
            "Hiring is the biggest bottleneck and you are the only interviewer"
        ],
        "actions": [
            "Hire 2-3 executives who complement your archetype blind spots",
            "Define and document company values with leadership team",
            "Implement manager training for new managers",
            "Establish weekly leadership team cadence"
        ]
    },
    3: {
        "threshold": 150,
        "name": "Ceiling 3: Institutional Leadership (~150 people)",
        "problem": "Need a real executive team or you become the permanent blocker",
        "solution": "Build institutional leadership, not personal leadership",
        "skill_to_build": "System design, not personal contribution",
        "signals": [
            "Company cannot function for 2 weeks without you",
            "Executive team defers to you on all cross-functional decisions",
            "Culture is 'what the founder does' not 'what the company does'",
            "Board interactions consume too much of your time"
        ],
        "actions": [
            "Build leadership team that can run company for a quarter without you",
            "Implement company operating system (planning cadence, review rhythm)",
            "Develop succession plan for your role",
            "Focus your time on vision, board, culture, and external narrative"
        ]
    },
    4: {
        "threshold": 500,
        "name": "Ceiling 4: Organizational Architecture (500+ people)",
        "problem": "You are a symbol, not a manager -- and must embrace that",
        "solution": "Focus on vision, board, culture, and external narrative",
        "skill_to_build": "Organizational architecture and external leadership",
        "signals": [
            "Multiple layers between you and execution teams",
            "Your decisions have weeks of ripple effects across the org",
            "External stakeholders (press, analysts, partners) demand significant time",
            "Internal communications must be carefully crafted, not casual"
        ],
        "actions": [
            "Delegate all internal operations to COO/President",
            "Spend 50%+ of time on external: board, investors, partnerships, vision",
            "Build world-class executive team that operates independently",
            "Focus on 2-3 year strategic horizon, not quarterly execution"
        ]
    }
}

STAGES = {
    "pre-seed": {"arr_range": (0, 100000), "headcount_range": (1, 5), "typical_ceiling": 1},
    "seed": {"arr_range": (0, 500000), "headcount_range": (2, 15), "typical_ceiling": 1},
    "series-a": {"arr_range": (500000, 3000000), "headcount_range": (10, 50), "typical_ceiling": 2},
    "series-b": {"arr_range": (3000000, 15000000), "headcount_range": (30, 150), "typical_ceiling": 3},
    "series-c": {"arr_range": (15000000, 50000000), "headcount_range": (80, 300), "typical_ceiling": 3},
    "growth": {"arr_range": (50000000, 999999999), "headcount_range": (200, 5000), "typical_ceiling": 4},
}


def assess(headcount, arr, stage, has_exec_team, has_documented_processes, founder_in_meetings_pct):
    # Determine current ceiling
    current_ceiling = 1
    for ceiling_num, ceiling_data in CEILINGS.items():
        if headcount <= ceiling_data["threshold"]:
            current_ceiling = ceiling_num
            break
    else:
        current_ceiling = 4

    # Determine approaching ceiling
    approaching = current_ceiling
    for ceiling_num, ceiling_data in CEILINGS.items():
        if headcount >= ceiling_data["threshold"] * 0.7:
            approaching = ceiling_num
            if ceiling_num < 4:
                approaching = ceiling_num + 1

    ceiling_data = CEILINGS[current_ceiling]

    # Stage alignment check
    stage_info = STAGES.get(stage, STAGES["seed"])
    arr_aligned = stage_info["arr_range"][0] <= arr <= stage_info["arr_range"][1]
    headcount_aligned = stage_info["headcount_range"][0] <= headcount <= stage_info["headcount_range"][1]

    # Risk signals
    risks = []
    if founder_in_meetings_pct > 70 and headcount > 15:
        risks.append("Founder in too many meetings for company size -- delegation gap")
    if not has_exec_team and headcount > 30:
        risks.append("No executive team at 30+ headcount -- approaching Ceiling 2 without leaders")
    if not has_documented_processes and headcount > 15:
        risks.append("No documented processes -- knowledge is trapped in founder's head")
    if not arr_aligned:
        risks.append(f"ARR ${arr:,} is outside expected range for {stage} (${stage_info['arr_range'][0]:,}-${stage_info['arr_range'][1]:,})")
    if not headcount_aligned:
        risks.append(f"Headcount {headcount} is outside expected range for {stage} ({stage_info['headcount_range'][0]}-{stage_info['headcount_range'][1]})")

    # Readiness score
    readiness_score = 10
    if not has_exec_team and current_ceiling >= 2:
        readiness_score -= 3
    if not has_documented_processes:
        readiness_score -= 2
    if founder_in_meetings_pct > 60:
        readiness_score -= 2
    if len(risks) > 2:
        readiness_score -= 2
    readiness_score = max(1, readiness_score)

    return {
        "assessment_date": datetime.now().strftime("%Y-%m-%d"),
        "company_metrics": {
            "headcount": headcount,
            "arr": arr,
            "funding_stage": stage,
            "has_exec_team": has_exec_team,
            "has_documented_processes": has_documented_processes,
            "founder_meeting_percentage": founder_in_meetings_pct
        },
        "current_ceiling": {
            "number": current_ceiling,
            "name": ceiling_data["name"],
            "problem": ceiling_data["problem"],
            "solution": ceiling_data["solution"],
            "skill_to_build": ceiling_data["skill_to_build"]
        },
        "ceiling_signals": ceiling_data["signals"],
        "recommended_actions": ceiling_data["actions"],
        "stage_alignment": {
            "arr_aligned": arr_aligned,
            "headcount_aligned": headcount_aligned,
            "expected_arr_range": f"${stage_info['arr_range'][0]:,} - ${stage_info['arr_range'][1]:,}",
            "expected_headcount_range": f"{stage_info['headcount_range'][0]} - {stage_info['headcount_range'][1]}"
        },
        "risks": risks,
        "readiness_score": readiness_score,
        "readiness_label": "Ready" if readiness_score >= 7 else "Preparing" if readiness_score >= 4 else "At Risk"
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"STARTUP STAGE ASSESSMENT")
    print(f"Date: {result['assessment_date']}")
    print(f"{'='*70}\n")

    m = result["company_metrics"]
    print(f"COMPANY: {m['headcount']} people | ${m['arr']:,} ARR | {m['funding_stage']}")
    print(f"Exec Team: {'Yes' if m['has_exec_team'] else 'No'} | Documented Processes: {'Yes' if m['has_documented_processes'] else 'No'}")
    print(f"Founder in meetings: {m['founder_meeting_percentage']}%\n")

    c = result["current_ceiling"]
    print(f"CURRENT CEILING: {c['name']}")
    print(f"  Problem:  {c['problem']}")
    print(f"  Solution: {c['solution']}")
    print(f"  Skill:    {c['skill_to_build']}\n")

    print("SIGNALS TO WATCH:")
    for s in result["ceiling_signals"]:
        print(f"  - {s}")

    print("\nRECOMMENDED ACTIONS:")
    for a in result["recommended_actions"]:
        print(f"  [ ] {a}")

    sa = result["stage_alignment"]
    print(f"\nSTAGE ALIGNMENT:")
    print(f"  ARR: {'Aligned' if sa['arr_aligned'] else 'MISALIGNED'} (expected: {sa['expected_arr_range']})")
    print(f"  Headcount: {'Aligned' if sa['headcount_aligned'] else 'MISALIGNED'} (expected: {sa['expected_headcount_range']})")

    if result["risks"]:
        print(f"\nRISKS ({len(result['risks'])}):")
        for r in result["risks"]:
            print(f"  [!] {r}")

    print(f"\nREADINESS: {result['readiness_score']}/10 ({result['readiness_label']})")
    print()


def main():
    parser = argparse.ArgumentParser(description="Assess startup stage and founder growth ceiling")
    parser.add_argument("--headcount", type=int, required=True, help="Current headcount")
    parser.add_argument("--arr", type=float, required=True, help="Annual recurring revenue in dollars")
    parser.add_argument("--stage", required=True, choices=list(STAGES.keys()), help="Funding stage")
    parser.add_argument("--has-exec-team", action="store_true", help="Has executive team in place")
    parser.add_argument("--has-documented-processes", action="store_true", help="Has documented processes")
    parser.add_argument("--founder-meeting-pct", type=int, default=60, help="Percentage of meetings founder attends")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = assess(
        args.headcount, args.arr, args.stage,
        args.has_exec_team, args.has_documented_processes,
        args.founder_meeting_pct
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
