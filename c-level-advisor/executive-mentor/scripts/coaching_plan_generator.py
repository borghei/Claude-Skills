#!/usr/bin/env python3
"""Coaching Plan Generator - Generate structured 90-day executive coaching plans.

Creates a phased coaching plan based on identified development gaps, company stage,
and GROW model principles. Outputs weekly milestones, accountability checkpoints,
and success metrics.

Usage:
    python coaching_plan_generator.py --gaps delegation,communication --stage series-a
    python coaching_plan_generator.py --gaps strategic,execution,people --stage seed --intensity high --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

GAP_PLANS = {
    "delegation": {
        "name": "Delegation Mastery",
        "phases": [
            {
                "phase": 1, "name": "Awareness & Audit", "weeks": "1-3",
                "activities": [
                    "Audit all tasks you touch weekly; categorize as strategic vs. operational",
                    "Map current delegation levels for top 20 recurring tasks",
                    "Identify 5 tasks to delegate first (use priority order: recurring ops first)"
                ],
                "milestone": "Delegation audit complete with 5 tasks identified for delegation",
                "accountability": "Share audit results with coach or peer; review weekly"
            },
            {
                "phase": 2, "name": "Practice & Trust Building", "weeks": "4-8",
                "activities": [
                    "Delegate 3 tasks at Level 3 (propose solution, you decide)",
                    "Write context documents for each delegated task",
                    "Resist the urge to take back tasks when quality dips initially",
                    "Conduct weekly check-ins on delegated tasks (15 min max)"
                ],
                "milestone": "3 tasks successfully delegated at Level 3 with written parameters",
                "accountability": "Track decision quality of delegated tasks; compare to your own"
            },
            {
                "phase": 3, "name": "Scale & Elevate", "weeks": "9-13",
                "activities": [
                    "Promote 2 tasks from Level 3 to Level 4 (decide and inform)",
                    "Identify 3 new tasks for delegation at Level 2-3",
                    "Measure time freed and redirect to strategic work",
                    "Document delegation framework for your direct reports to cascade"
                ],
                "milestone": "5+ tasks at Level 3-4; 4+ hours/week freed for strategic work",
                "accountability": "Calendar audit shows measurable shift from execution to strategy"
            }
        ],
        "success_metrics": [
            "Time spent on operational tasks reduced by 30%+",
            "At least 5 tasks operating at delegation Level 3 or higher",
            "Direct reports report increased autonomy in anonymous feedback",
            "No task taken back after delegation (barring genuine emergency)"
        ]
    },
    "communication": {
        "name": "Communication Excellence",
        "phases": [
            {
                "phase": 1, "name": "Baseline & Awareness", "weeks": "1-3",
                "activities": [
                    "Run 5-person articulation test: ask 5 team members your top priority",
                    "Audit last month's communications for consistency across audiences",
                    "Identify your communication weak spot: frequency, clarity, or audience adaptation"
                ],
                "milestone": "Communication baseline score established; primary gap identified",
                "accountability": "Share articulation test results with leadership team"
            },
            {
                "phase": 2, "name": "Build the System", "weeks": "4-8",
                "activities": [
                    "Write core narrative document (one paragraph, single source of truth)",
                    "Create audience translation matrix for 3 key audiences",
                    "Redesign all-hands format with 15-min unscreened Q&A",
                    "Establish monthly investor update on fixed schedule"
                ],
                "milestone": "Core narrative documented; all-hands redesigned; first improved investor update sent",
                "accountability": "Run contradiction detection before each major communication"
            },
            {
                "phase": 3, "name": "Reinforce & Measure", "weeks": "9-13",
                "activities": [
                    "Re-run 5-person test; compare to baseline",
                    "Collect Q&A quality metrics from all-hands (number of real questions)",
                    "Solicit feedback on communication clarity from 3 direct reports",
                    "Refine narrative based on feedback and business changes"
                ],
                "milestone": "5-person test score improved by 2+ points; Q&A engagement up",
                "accountability": "Quarterly communication effectiveness review scheduled"
            }
        ],
        "success_metrics": [
            "5-person articulation test score 8/10 or higher",
            "All-hands Q&A produces 5+ substantive questions per session",
            "Investor updates sent consistently on same date each month",
            "Zero narrative contradictions caught by stakeholders"
        ]
    },
    "strategic": {
        "name": "Strategic Clarity",
        "phases": [
            {
                "phase": 1, "name": "Strategy Audit", "weeks": "1-3",
                "activities": [
                    "Write your strategy in one sentence; test if it is falsifiable",
                    "Review resource allocation: does spend match stated priorities?",
                    "Identify where strategy is aspirational vs. operational"
                ],
                "milestone": "One-sentence strategy that is specific enough to be wrong",
                "accountability": "Share with board member or advisor for challenge"
            },
            {
                "phase": 2, "name": "Cascade & Validate", "weeks": "4-8",
                "activities": [
                    "Map strategy to team-level OKRs; identify orphans and conflicts",
                    "Block 4+ hours/week for strategic thinking (non-negotiable)",
                    "Run pre-mortem on top strategic bet",
                    "Schedule monthly strategy review with leadership team"
                ],
                "milestone": "Strategy cascaded to all teams; no orphan goals; pre-mortem complete",
                "accountability": "Strategic thinking time actually protected on calendar"
            },
            {
                "phase": 3, "name": "Decision Quality", "weeks": "9-13",
                "activities": [
                    "Start decision journal: record major decisions with reasoning",
                    "Review 90-day-old decisions for outcome quality",
                    "Apply stress test protocol to one assumption per week",
                    "Conduct quarterly strategy review with full team"
                ],
                "milestone": "Decision journal active; one strategy assumption stress-tested weekly",
                "accountability": "Quarterly strategy review scheduled and executed"
            }
        ],
        "success_metrics": [
            "Strategy articulable in one sentence by CEO and all direct reports",
            "4+ hours/week of protected strategic thinking time maintained",
            "Decision journal shows improving outcome quality over 90 days",
            "Pre-mortem conducted before every major strategic commitment"
        ]
    },
    "decision": {
        "name": "Decision Excellence",
        "phases": [
            {
                "phase": 1, "name": "Decision Audit", "weeks": "1-3",
                "activities": [
                    "List all pending decisions; apply reversibility test to each",
                    "Identify decisions delayed > 2 weeks; decide or delegate within 48 hours",
                    "Start decision log: decision, reasoning, expected outcome, date"
                ],
                "milestone": "Decision backlog cleared; decision log started",
                "accountability": "Zero decisions pending > 2 weeks without explicit reason"
            },
            {
                "phase": 2, "name": "Framework Adoption", "weeks": "4-8",
                "activities": [
                    "Apply Hard Call Framework to next irreversible decision",
                    "Use 10/10/10 analysis for emotionally difficult decisions",
                    "Practice stakeholder impact mapping before major announcements",
                    "Review decision log weekly; identify patterns"
                ],
                "milestone": "Hard Call Framework used for 2+ major decisions",
                "accountability": "Decision log reviewed weekly with coach or peer"
            },
            {
                "phase": 3, "name": "Speed & Quality", "weeks": "9-13",
                "activities": [
                    "Measure average decision cycle time; target < 48 hours for reversible",
                    "Review 90-day outcomes of logged decisions",
                    "Teach decision framework to direct reports for cascaded use",
                    "Define decision rights matrix for team"
                ],
                "milestone": "Decision cycle time within targets; framework cascaded to team",
                "accountability": "Decision quality metrics tracked quarterly"
            }
        ],
        "success_metrics": [
            "Reversible decisions made within 48 hours consistently",
            "Decision log shows > 70% positive outcome rate at 90-day review",
            "Hard Call Framework applied to all irreversible decisions",
            "Direct reports can make decisions independently within defined parameters"
        ]
    },
    "people": {
        "name": "People Leadership",
        "phases": [
            {
                "phase": 1, "name": "Know Your Team", "weeks": "1-3",
                "activities": [
                    "Conduct development conversation with each direct report",
                    "Document career aspirations and growth areas for each person",
                    "Identify your top 3 retention risks and their motivations"
                ],
                "milestone": "Development profile complete for every direct report",
                "accountability": "Can name each person's top career goal from memory"
            },
            {
                "phase": 2, "name": "Develop & Invest", "weeks": "4-8",
                "activities": [
                    "Create development plan for each direct report with specific milestones",
                    "Schedule monthly coaching sessions (30 min each)",
                    "Identify one stretch assignment per direct report this quarter",
                    "Start tracking internal promotion pipeline"
                ],
                "milestone": "Development plans active; monthly coaching cadence established",
                "accountability": "Monthly coaching sessions completed (no cancellations)"
            },
            {
                "phase": 3, "name": "Build Bench Strength", "weeks": "9-13",
                "activities": [
                    "Draft succession plan for your role and 2 key positions",
                    "Evaluate internal promotion readiness for each direct report",
                    "Provide specific, behavioral feedback weekly (not just in reviews)",
                    "Measure team engagement and compare to baseline"
                ],
                "milestone": "Succession plan documented; engagement trending up",
                "accountability": "Succession readiness at Level 2+ for your role"
            }
        ],
        "success_metrics": [
            "Every direct report has active development plan with milestones",
            "Monthly coaching sessions maintained with 90%+ completion rate",
            "At least one internal promotion within 6 months",
            "eNPS improves by 10+ points in next engagement survey"
        ]
    },
    "eq": {
        "name": "Emotional Intelligence",
        "phases": [
            {
                "phase": 1, "name": "Self-Assessment", "weeks": "1-3",
                "activities": [
                    "Identify your emotional triggers in professional settings",
                    "Start end-of-day reflection practice (5 minutes)",
                    "Ask 3 trusted peers: 'How do I show up under stress?'"
                ],
                "milestone": "Trigger map documented; daily reflection habit started",
                "accountability": "Reflection journal maintained for 21 consecutive days"
            },
            {
                "phase": 2, "name": "Regulate & Empathize", "weeks": "4-8",
                "activities": [
                    "Practice pause-before-response in next 3 difficult conversations",
                    "Conduct skip-level 1:1s focused on listening (not solving)",
                    "Seek coaching or therapy for self-regulation skill building",
                    "Practice naming emotions in real-time ('I notice I feel...')"
                ],
                "milestone": "No composure losses in professional settings; 3 skip-level 1:1s completed",
                "accountability": "Ask direct reports if conversations feel more open"
            },
            {
                "phase": 3, "name": "Lead with EQ", "weeks": "9-13",
                "activities": [
                    "Run 360 feedback focused on EQ dimensions",
                    "Practice reading room energy in meetings and adjusting approach",
                    "Model vulnerability by sharing one mistake or learning with team",
                    "Build EQ into your leadership assessment of others"
                ],
                "milestone": "360 feedback shows EQ improvement; team reports increased psychological safety",
                "accountability": "EQ 360 scores as new baseline for next cycle"
            }
        ],
        "success_metrics": [
            "Zero reported composure losses in 90-day period",
            "360 feedback EQ scores improve by 1+ point",
            "Team psychological safety survey improves",
            "Difficult conversations handled without defensiveness (peer-validated)"
        ]
    },
    "execution": {
        "name": "Execution Discipline",
        "phases": [
            {
                "phase": 1, "name": "Baseline & Cadence", "weeks": "1-3",
                "activities": [
                    "Calculate current OKR completion rate for last 2 quarters",
                    "Establish weekly leadership review meeting (1 hour, scorecard-driven)",
                    "Define top 3 metrics every team should track weekly"
                ],
                "milestone": "OKR completion baseline established; weekly review started",
                "accountability": "Weekly review meeting held every week (zero skips)"
            },
            {
                "phase": 2, "name": "Accountability Systems", "weeks": "4-8",
                "activities": [
                    "Create accountability matrix: every initiative has one owner",
                    "Implement commitment tracking (promises made vs. kept)",
                    "Address one missed commitment directly each week",
                    "Remove one standing meeting that does not produce outcomes"
                ],
                "milestone": "Accountability matrix live; commitment tracking operational",
                "accountability": "Commitment completion rate tracked weekly"
            },
            {
                "phase": 3, "name": "Sustainable Execution", "weeks": "9-13",
                "activities": [
                    "Measure OKR completion rate and compare to baseline",
                    "Cascade execution cadence to team-level leaders",
                    "Document standard operating procedures for top 5 processes",
                    "Conduct retrospective on execution system effectiveness"
                ],
                "milestone": "OKR completion > 70%; execution cadence cascaded to teams",
                "accountability": "Quarterly execution retrospective scheduled"
            }
        ],
        "success_metrics": [
            "OKR completion rate above 70%",
            "Weekly review meeting maintained for 13 consecutive weeks",
            "Commitment completion rate above 85%",
            "Cross-functional initiative completion > 80% on time"
        ]
    },
    "self_awareness": {
        "name": "Self-Awareness Development",
        "phases": [
            {
                "phase": 1, "name": "Honest Assessment", "weeks": "1-3",
                "activities": [
                    "Run anonymous 360 feedback with 5 hard questions",
                    "Ask direct reports: 'What should I stop doing?'",
                    "Identify top 3 blind spots from feedback patterns"
                ],
                "milestone": "360 complete; top 3 blind spots documented",
                "accountability": "Share blind spots with coach or trusted peer"
            },
            {
                "phase": 2, "name": "Active Mitigation", "weeks": "4-8",
                "activities": [
                    "Create specific mitigation strategy for each blind spot",
                    "Join executive peer group for external honest feedback",
                    "Start evidence file: document wins, mistakes, and patterns",
                    "Practice separating 'I feel' from 'the facts are'"
                ],
                "milestone": "Mitigation strategies active for all 3 blind spots; peer group joined",
                "accountability": "Evidence file updated weekly; peer group attended monthly"
            },
            {
                "phase": 3, "name": "Continuous Growth", "weeks": "9-13",
                "activities": [
                    "Re-run 360 feedback to measure improvement on blind spots",
                    "Conduct honest self-review: what changed and what didn't?",
                    "Set next quarter's development focus based on evidence",
                    "Model self-awareness by sharing learnings with team"
                ],
                "milestone": "360 scores improved on identified blind spots; next development area selected",
                "accountability": "Annual self-awareness development cycle established"
            }
        ],
        "success_metrics": [
            "Can name top 3 blind spots with specific mitigation strategies",
            "360 feedback scores improve on targeted dimensions",
            "Evidence file maintained with weekly entries",
            "Peer group feedback shows increasing self-awareness"
        ]
    }
}

INTENSITY_MULTIPLIERS = {"low": 0.7, "medium": 1.0, "high": 1.3}


def generate_plan(gaps, stage, intensity, start_date):
    plans = []
    for gap in gaps:
        gap_key = gap.strip().lower().replace("-", "_").replace(" ", "_")
        if gap_key not in GAP_PLANS:
            print(f"Warning: Unknown gap '{gap}'. Available: {', '.join(GAP_PLANS.keys())}", file=sys.stderr)
            continue
        plans.append(GAP_PLANS[gap_key])

    if not plans:
        print("Error: No valid gaps provided.", file=sys.stderr)
        sys.exit(1)

    weekly_schedule = []
    for week in range(1, 14):
        week_start = start_date + timedelta(weeks=week - 1)
        week_activities = []
        for plan in plans:
            for phase in plan["phases"]:
                week_range = phase["weeks"].split("-")
                w_start, w_end = int(week_range[0]), int(week_range[1])
                if w_start <= week <= w_end:
                    week_activities.append({
                        "plan": plan["name"],
                        "phase": phase["name"],
                        "focus": phase["activities"][min(week - w_start, len(phase["activities"]) - 1)]
                    })
        weekly_schedule.append({
            "week": week,
            "start_date": week_start.strftime("%Y-%m-%d"),
            "activities": week_activities
        })

    return {
        "plan_generated": datetime.now().strftime("%Y-%m-%d"),
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": (start_date + timedelta(weeks=13)).strftime("%Y-%m-%d"),
        "company_stage": stage,
        "intensity": intensity,
        "development_areas": [p["name"] for p in plans],
        "plans": plans,
        "weekly_schedule": weekly_schedule,
        "checkpoints": [
            {"week": 3, "type": "Phase 1 Review", "action": "Review Phase 1 milestones for all development areas"},
            {"week": 8, "type": "Phase 2 Review", "action": "Review Phase 2 milestones; adjust intensity if needed"},
            {"week": 13, "type": "Final Review", "action": "Assess all success metrics; plan next 90-day cycle"}
        ]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"90-DAY COACHING PLAN")
    print(f"Generated: {result['plan_generated']}")
    print(f"Period: {result['start_date']} to {result['end_date']}")
    print(f"Stage: {result['company_stage']}  |  Intensity: {result['intensity']}")
    print(f"{'='*70}\n")

    print(f"DEVELOPMENT AREAS: {', '.join(result['development_areas'])}\n")

    for plan in result["plans"]:
        print(f"\n--- {plan['name'].upper()} ---")
        for phase in plan["phases"]:
            print(f"\n  Phase {phase['phase']}: {phase['name']} (Weeks {phase['weeks']})")
            for act in phase["activities"]:
                print(f"    - {act}")
            print(f"    Milestone: {phase['milestone']}")
            print(f"    Accountability: {phase['accountability']}")

        print(f"\n  Success Metrics:")
        for m in plan["success_metrics"]:
            print(f"    [ ] {m}")

    print(f"\nCHECKPOINTS")
    print("-" * 40)
    for cp in result["checkpoints"]:
        print(f"  Week {cp['week']:>2}: {cp['type']} - {cp['action']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Generate structured 90-day executive coaching plan")
    parser.add_argument("--gaps", required=True, help="Comma-separated development gaps (e.g., delegation,communication,strategic,decision,people,eq,execution,self_awareness)")
    parser.add_argument("--stage", default="series-a", help="Company stage (seed, series-a, series-b, series-c)")
    parser.add_argument("--intensity", default="medium", choices=["low", "medium", "high"], help="Coaching intensity")
    parser.add_argument("--start-date", default=None, help="Start date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else datetime.now()
    gaps = [g.strip() for g in args.gaps.split(",")]
    result = generate_plan(gaps, args.stage, args.intensity, start_date)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
