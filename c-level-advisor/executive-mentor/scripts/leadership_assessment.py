#!/usr/bin/env python3
"""Leadership Assessment Tool - Score leadership competencies across 8 dimensions using GROW model framework.

Evaluates executives on strategic thinking, communication, delegation, decision quality,
people development, emotional intelligence, execution discipline, and self-awareness.
Produces a competency profile with gap analysis and development recommendations.

Usage:
    python leadership_assessment.py --name "Jane Doe" --role CEO
    python leadership_assessment.py --name "Jane Doe" --role CEO --strategic 8 --communication 6 --delegation 4 --decision 7 --people 5 --eq 7 --execution 8 --self-awareness 6 --json
"""

import argparse
import json
import sys
from datetime import datetime

DIMENSIONS = {
    "strategic": {
        "name": "Strategic Thinking",
        "description": "Ability to set direction, prioritize, and think long-term",
        "grow_goal": "Articulate a clear, falsifiable strategy that the team can execute",
        "grow_reality_questions": [
            "Can 5 people from different teams state your strategy consistently?",
            "Do your resource allocations match your stated priorities?",
            "When did you last change strategy based on new data?"
        ],
        "grow_options": [
            "Schedule weekly protected strategy time (4 hours minimum)",
            "Run quarterly strategy articulation test with team",
            "Create decision journal to track strategic choices and outcomes"
        ]
    },
    "communication": {
        "name": "Communication",
        "description": "Clarity, frequency, and effectiveness of communication across audiences",
        "grow_goal": "Every stakeholder group receives consistent, clear, audience-appropriate messaging",
        "grow_reality_questions": [
            "Do employees learn company news from you or from social media?",
            "Can your direct reports explain your top 3 priorities?",
            "When did you last receive feedback that your message was unclear?"
        ],
        "grow_options": [
            "Implement narrative consistency protocol across audiences",
            "Practice the 7x rule: communicate key messages through 7 channels",
            "Run monthly all-hands with unscreened Q&A"
        ]
    },
    "delegation": {
        "name": "Delegation",
        "description": "Ability to trust, empower, and hold others accountable",
        "grow_goal": "Operate at delegation Level 4-5 for all operational tasks",
        "grow_reality_questions": [
            "What percentage of decisions still require your approval?",
            "Have you delegated the same task 3+ times successfully?",
            "Does your team wait for your input on routine decisions?"
        ],
        "grow_options": [
            "Identify 3 tasks to move up one delegation level this month",
            "Create written decision parameters for each direct report",
            "Track delegation level for top 20 recurring tasks"
        ]
    },
    "decision": {
        "name": "Decision Quality",
        "description": "Speed, accuracy, and framework discipline in decision-making",
        "grow_goal": "Make reversible decisions within 48 hours; irreversible within 2 weeks with full framework",
        "grow_reality_questions": [
            "How many decisions are waiting for you right now?",
            "Do you apply the reversibility test before deciding?",
            "What was your last decision you would undo if you could?"
        ],
        "grow_options": [
            "Implement the Hard Call Decision Framework for all major decisions",
            "Run pre-mortem on every irreversible decision",
            "Create decision log with outcomes tracked at 90 days"
        ]
    },
    "people": {
        "name": "People Development",
        "description": "Investment in growing team capability and building bench strength",
        "grow_goal": "Every direct report has a development plan and receives monthly coaching",
        "grow_reality_questions": [
            "Can you name each direct report's career aspiration?",
            "How many internal promotions happened in the last 12 months?",
            "Who is your successor if you left tomorrow?"
        ],
        "grow_options": [
            "Schedule monthly development conversations with each direct report",
            "Create succession plan for your role and all key positions",
            "Invest in leadership development for your top 3 high-potential people"
        ]
    },
    "eq": {
        "name": "Emotional Intelligence",
        "description": "Self-regulation, empathy, and ability to read and respond to others",
        "grow_goal": "Navigate difficult conversations without defensiveness; read team energy accurately",
        "grow_reality_questions": [
            "When did you last lose your composure in a professional setting?",
            "Can you identify when a team member is struggling before they tell you?",
            "Do people feel safe giving you honest feedback?"
        ],
        "grow_options": [
            "Start a daily reflection practice (5 minutes end of day)",
            "Request honest feedback from 3 trusted peers quarterly",
            "Work with an executive coach on self-regulation"
        ]
    },
    "execution": {
        "name": "Execution Discipline",
        "description": "Ability to turn strategy into operational reality with accountability",
        "grow_goal": "OKR completion rate above 70% with clear accountability at every level",
        "grow_reality_questions": [
            "What percentage of last quarter's goals were completed?",
            "Do you have a weekly review cadence with your team?",
            "When did you last hold someone accountable for a missed commitment?"
        ],
        "grow_options": [
            "Implement weekly leadership review with scorecard metrics",
            "Create clear accountability structure for every major initiative",
            "Track commitments made and kept across the team"
        ]
    },
    "self_awareness": {
        "name": "Self-Awareness",
        "description": "Honest understanding of strengths, blind spots, and impact on others",
        "grow_goal": "Name your top 3 blind spots and have active mitigation strategies",
        "grow_reality_questions": [
            "What do people say about you when you're not in the room?",
            "What feedback have you received more than once?",
            "When did you last run a 360 review?"
        ],
        "grow_options": [
            "Run annual 360 feedback with hard questions",
            "Join a founder/executive peer group for honest feedback",
            "Keep an evidence file: wins, mistakes, and patterns"
        ]
    }
}

ROLE_WEIGHT_PROFILES = {
    "ceo": {"strategic": 1.3, "communication": 1.2, "delegation": 1.2, "decision": 1.1, "people": 1.0, "eq": 1.0, "execution": 0.9, "self_awareness": 1.1},
    "cto": {"strategic": 1.1, "communication": 0.9, "delegation": 1.0, "decision": 1.2, "people": 1.0, "eq": 0.9, "execution": 1.3, "self_awareness": 1.0},
    "coo": {"strategic": 1.0, "communication": 1.0, "delegation": 1.1, "decision": 1.1, "people": 1.1, "eq": 0.9, "execution": 1.4, "self_awareness": 0.9},
    "cfo": {"strategic": 1.1, "communication": 1.0, "delegation": 0.9, "decision": 1.3, "people": 0.9, "eq": 0.9, "execution": 1.2, "self_awareness": 1.0},
    "cro": {"strategic": 1.0, "communication": 1.3, "delegation": 1.1, "decision": 1.1, "people": 1.1, "eq": 1.1, "execution": 1.1, "self_awareness": 0.9},
    "cpo": {"strategic": 1.2, "communication": 1.1, "delegation": 1.0, "decision": 1.2, "people": 1.0, "eq": 1.0, "execution": 1.1, "self_awareness": 1.0},
    "vp": {"strategic": 1.0, "communication": 1.1, "delegation": 1.2, "decision": 1.0, "people": 1.2, "eq": 1.0, "execution": 1.2, "self_awareness": 0.9},
    "founder": {"strategic": 1.2, "communication": 1.0, "delegation": 1.3, "decision": 1.1, "people": 0.9, "eq": 1.0, "execution": 1.0, "self_awareness": 1.2},
}


def get_traffic_light(score):
    if score >= 7:
        return "GREEN"
    elif score >= 4:
        return "YELLOW"
    return "RED"


def assess(name, role, scores):
    role_key = role.lower().replace(" ", "")
    weights = ROLE_WEIGHT_PROFILES.get(role_key, {k: 1.0 for k in DIMENSIONS})

    results = []
    total_weighted = 0.0
    total_weight = 0.0

    for dim_key, dim_info in DIMENSIONS.items():
        score = scores.get(dim_key, 5.0)
        weight = weights.get(dim_key, 1.0)
        weighted_score = score * weight
        total_weighted += weighted_score
        total_weight += weight
        traffic = get_traffic_light(score)

        results.append({
            "dimension": dim_info["name"],
            "key": dim_key,
            "score": score,
            "weight": round(weight, 2),
            "weighted_score": round(weighted_score, 2),
            "traffic_light": traffic,
            "grow_goal": dim_info["grow_goal"],
            "grow_reality_questions": dim_info["grow_reality_questions"],
            "grow_options": dim_info["grow_options"]
        })

    overall = round(total_weighted / total_weight, 1) if total_weight > 0 else 0
    results.sort(key=lambda x: x["score"])

    top_gaps = [r for r in results if r["score"] < 7][:3]
    top_strengths = sorted(results, key=lambda x: -x["score"])[:3]

    return {
        "assessment_date": datetime.now().strftime("%Y-%m-%d"),
        "executive": name,
        "role": role,
        "overall_score": overall,
        "overall_traffic_light": get_traffic_light(overall),
        "dimensions": results,
        "top_strengths": [{"dimension": s["dimension"], "score": s["score"]} for s in top_strengths],
        "top_gaps": [{"dimension": g["dimension"], "score": g["score"], "grow_goal": g["grow_goal"]} for g in top_gaps],
        "priority_development_area": top_gaps[0]["dimension"] if top_gaps else "None identified",
        "recommended_grow_session": {
            "goal": top_gaps[0]["grow_goal"] if top_gaps else "Maintain current strengths",
            "reality_questions": top_gaps[0]["grow_reality_questions"] if top_gaps else [],
            "options": top_gaps[0]["grow_options"] if top_gaps else [],
            "will": "Define one specific action from the options above, with a deadline within 30 days"
        }
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"LEADERSHIP ASSESSMENT - {result['executive']} ({result['role']})")
    print(f"Date: {result['assessment_date']}")
    print(f"Overall: {result['overall_score']}/10 [{result['overall_traffic_light']}]")
    print(f"{'='*70}\n")

    print("DIMENSION SCORES")
    print("-" * 60)
    for d in sorted(result["dimensions"], key=lambda x: -x["score"]):
        bar = "#" * int(d["score"]) + "." * (10 - int(d["score"]))
        print(f"  [{d['traffic_light']:6s}] {d['dimension']:<25s} {d['score']:>4.1f}  {bar}  (weight: {d['weight']})")

    print(f"\nTOP STRENGTHS")
    print("-" * 40)
    for s in result["top_strengths"]:
        print(f"  + {s['dimension']}: {s['score']}/10")

    print(f"\nDEVELOPMENT GAPS")
    print("-" * 40)
    for g in result["top_gaps"]:
        print(f"  - {g['dimension']}: {g['score']}/10")
        print(f"    Goal: {g['grow_goal']}")

    print(f"\nPRIORITY: {result['priority_development_area']}")

    grow = result["recommended_grow_session"]
    print(f"\nRECOMMENDED GROW SESSION")
    print("-" * 40)
    print(f"  Goal:    {grow['goal']}")
    print(f"  Reality: (ask these questions)")
    for q in grow["reality_questions"]:
        print(f"           - {q}")
    print(f"  Options:")
    for o in grow["options"]:
        print(f"           - {o}")
    print(f"  Will:    {grow['will']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Leadership Assessment Tool - Score leadership competencies across 8 dimensions"
    )
    parser.add_argument("--name", required=True, help="Executive name")
    parser.add_argument("--role", required=True, help="Role (CEO, CTO, COO, CFO, CRO, CPO, VP, Founder)")
    parser.add_argument("--strategic", type=float, default=5.0, help="Strategic thinking score (1-10)")
    parser.add_argument("--communication", type=float, default=5.0, help="Communication score (1-10)")
    parser.add_argument("--delegation", type=float, default=5.0, help="Delegation score (1-10)")
    parser.add_argument("--decision", type=float, default=5.0, help="Decision quality score (1-10)")
    parser.add_argument("--people", type=float, default=5.0, help="People development score (1-10)")
    parser.add_argument("--eq", type=float, default=5.0, help="Emotional intelligence score (1-10)")
    parser.add_argument("--execution", type=float, default=5.0, help="Execution discipline score (1-10)")
    parser.add_argument("--self-awareness", type=float, default=5.0, help="Self-awareness score (1-10)", dest="self_awareness")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    for attr in ["strategic", "communication", "delegation", "decision", "people", "eq", "execution", "self_awareness"]:
        val = getattr(args, attr)
        if val < 1 or val > 10:
            print(f"Error: {attr} score must be between 1 and 10", file=sys.stderr)
            sys.exit(1)

    scores = {
        "strategic": args.strategic,
        "communication": args.communication,
        "delegation": args.delegation,
        "decision": args.decision,
        "people": args.people,
        "eq": args.eq,
        "execution": args.execution,
        "self_awareness": args.self_awareness
    }

    result = assess(args.name, args.role, scores)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
