#!/usr/bin/env python3
"""Founder Wellness Checker - Screen for burnout signals with actionable recommendations.

Evaluates founder wellness across work intensity, sleep, exercise, social connection,
and stress indicators. Maps to Early/Mid/Late burnout stages with specific interventions.

Usage:
    python founder_wellness_checker.py --hours-per-week 65 --sleep-hours 5.5 --exercise-days 1
    python founder_wellness_checker.py --hours-per-week 55 --sleep-hours 7 --exercise-days 3 --has-peer-group --has-coach --json
"""

import argparse
import json
import sys
from datetime import datetime

FACTORS = {
    "work_hours": {
        "name": "Work Intensity",
        "thresholds": {"green": 50, "yellow": 60, "red": 70},
        "direction": "lower_is_better",
        "unit": "hours/week"
    },
    "sleep": {
        "name": "Sleep Quality",
        "thresholds": {"green": 7, "yellow": 6, "red": 5},
        "direction": "higher_is_better",
        "unit": "hours/night"
    },
    "exercise": {
        "name": "Physical Activity",
        "thresholds": {"green": 3, "yellow": 2, "red": 1},
        "direction": "higher_is_better",
        "unit": "days/week"
    },
    "peer_group": {
        "name": "Peer Support",
        "description": "Regular founder peer group or trusted advisor network"
    },
    "professional_support": {
        "name": "Professional Support",
        "description": "Therapist, coach, or similar professional relationship"
    },
    "vacation_days": {
        "name": "Recovery Time",
        "thresholds": {"green": 15, "yellow": 7, "red": 3},
        "direction": "higher_is_better",
        "unit": "days in last 6 months"
    },
    "decision_fatigue": {
        "name": "Decision Fatigue",
        "thresholds": {"green": 3, "yellow": 5, "red": 7},
        "direction": "lower_is_better",
        "unit": "self-rated 1-10"
    }
}

BURNOUT_STAGES = {
    "healthy": {
        "label": "Healthy",
        "description": "Sustainable pace with adequate recovery",
        "color": "GREEN",
        "recommendations": [
            "Maintain current habits -- they are working",
            "Schedule quarterly check-ins to ensure sustainability",
            "Consider helping other founders build similar habits"
        ]
    },
    "early": {
        "label": "Early Warning",
        "description": "Irritability, poor sleep, decisions feel harder than usual",
        "color": "YELLOW",
        "recommendations": [
            "Adjust calendar: protect recovery time this week",
            "Reduce commitments by 20% for the next 2 weeks",
            "Re-establish exercise routine (even 20 min walks count)",
            "Block 'off' hours and communicate them to your team",
            "Schedule 1 social activity unrelated to work this week"
        ]
    },
    "mid": {
        "label": "Mid-Stage Burnout",
        "description": "Physical symptoms, cynicism, priority paralysis, reduced effectiveness",
        "color": "ORANGE",
        "recommendations": [
            "Reduce work hours to < 50 this week (non-negotiable)",
            "Start therapy or coaching if not already active",
            "Delegate 3 responsibilities immediately (use delegation ladder)",
            "Take at least 2 consecutive days off within 2 weeks",
            "Inform a trusted board member or advisor of your state",
            "Audit all commitments and cancel or postpone 30%"
        ]
    },
    "late": {
        "label": "Late-Stage Burnout",
        "description": "Cannot function effectively, decisions stopped, team notices dysfunction",
        "color": "RED",
        "recommendations": [
            "STOP. Get professional support immediately (therapist or doctor)",
            "Inform your co-founder, board chair, or most trusted advisor today",
            "Delegate ALL operational responsibilities for at least 2 weeks",
            "Do not make any major decisions until recovery begins",
            "Consider a structured leave with clear communication to team",
            "This is not weakness -- this is a medical and operational necessity"
        ]
    }
}


def calculate_wellness(hours, sleep, exercise, has_peer_group, has_coach,
                       vacation_days, decision_fatigue):
    scores = {}
    risk_factors = []
    protective_factors = []

    # Work hours
    if hours <= 50:
        scores["work_hours"] = {"score": 9, "status": "green"}
    elif hours <= 60:
        scores["work_hours"] = {"score": 6, "status": "yellow"}
        risk_factors.append(f"Working {hours} hrs/week -- approaching unsustainable")
    elif hours <= 70:
        scores["work_hours"] = {"score": 3, "status": "orange"}
        risk_factors.append(f"Working {hours} hrs/week -- unsustainable pace")
    else:
        scores["work_hours"] = {"score": 1, "status": "red"}
        risk_factors.append(f"Working {hours} hrs/week -- burnout is a when, not if")

    # Sleep
    if sleep >= 7:
        scores["sleep"] = {"score": 9, "status": "green"}
        protective_factors.append("Adequate sleep (7+ hours)")
    elif sleep >= 6:
        scores["sleep"] = {"score": 5, "status": "yellow"}
        risk_factors.append(f"Sleep at {sleep} hrs -- cognitive impairment begins below 7")
    else:
        scores["sleep"] = {"score": 2, "status": "red"}
        risk_factors.append(f"Sleep at {sleep} hrs -- severe cognitive and health impact")

    # Exercise
    if exercise >= 3:
        scores["exercise"] = {"score": 9, "status": "green"}
        protective_factors.append(f"Regular exercise ({exercise} days/week)")
    elif exercise >= 2:
        scores["exercise"] = {"score": 5, "status": "yellow"}
        risk_factors.append("Exercise below recommended minimum (3+ days)")
    elif exercise >= 1:
        scores["exercise"] = {"score": 3, "status": "orange"}
        risk_factors.append("Minimal exercise -- stress relief compromised")
    else:
        scores["exercise"] = {"score": 1, "status": "red"}
        risk_factors.append("No exercise -- critical protective factor missing")

    # Peer group
    if has_peer_group:
        scores["peer_group"] = {"score": 8, "status": "green"}
        protective_factors.append("Active peer support network")
    else:
        scores["peer_group"] = {"score": 3, "status": "orange"}
        risk_factors.append("No peer group -- isolation risk")

    # Professional support
    if has_coach:
        scores["professional_support"] = {"score": 8, "status": "green"}
        protective_factors.append("Professional support (coach/therapist)")
    else:
        scores["professional_support"] = {"score": 4, "status": "yellow"}
        risk_factors.append("No professional support -- the job is isolating")

    # Vacation
    if vacation_days >= 15:
        scores["vacation"] = {"score": 9, "status": "green"}
        protective_factors.append(f"{vacation_days} recovery days in 6 months")
    elif vacation_days >= 7:
        scores["vacation"] = {"score": 5, "status": "yellow"}
        risk_factors.append(f"Only {vacation_days} days off in 6 months -- insufficient recovery")
    else:
        scores["vacation"] = {"score": 2, "status": "red"}
        risk_factors.append(f"Only {vacation_days} days off in 6 months -- no recovery happening")

    # Decision fatigue
    if decision_fatigue <= 3:
        scores["decision_fatigue"] = {"score": 8, "status": "green"}
    elif decision_fatigue <= 5:
        scores["decision_fatigue"] = {"score": 5, "status": "yellow"}
        risk_factors.append("Moderate decision fatigue -- delegate more operational decisions")
    elif decision_fatigue <= 7:
        scores["decision_fatigue"] = {"score": 3, "status": "orange"}
        risk_factors.append("High decision fatigue -- decision quality declining")
    else:
        scores["decision_fatigue"] = {"score": 1, "status": "red"}
        risk_factors.append("Severe decision fatigue -- decisions are being avoided or delayed")

    # Overall wellness score
    total = sum(s["score"] for s in scores.values())
    max_total = len(scores) * 10
    wellness_pct = round(total / max_total * 100)

    # Determine burnout stage
    red_count = sum(1 for s in scores.values() if s["status"] == "red")
    orange_count = sum(1 for s in scores.values() if s["status"] == "orange")

    if red_count >= 3 or (red_count >= 2 and orange_count >= 2):
        stage = "late"
    elif red_count >= 1 or orange_count >= 2:
        stage = "mid"
    elif orange_count >= 1 or len(risk_factors) >= 3:
        stage = "early"
    else:
        stage = "healthy"

    burnout_info = BURNOUT_STAGES[stage]

    return {
        "assessment_date": datetime.now().strftime("%Y-%m-%d"),
        "inputs": {
            "hours_per_week": hours,
            "sleep_hours": sleep,
            "exercise_days": exercise,
            "has_peer_group": has_peer_group,
            "has_professional_support": has_coach,
            "vacation_days_6mo": vacation_days,
            "decision_fatigue": decision_fatigue
        },
        "wellness_score": wellness_pct,
        "burnout_stage": stage,
        "burnout_label": burnout_info["label"],
        "burnout_description": burnout_info["description"],
        "severity": burnout_info["color"],
        "factor_scores": scores,
        "risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "recommendations": burnout_info["recommendations"]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"FOUNDER WELLNESS CHECK")
    print(f"Date: {result['assessment_date']}")
    print(f"{'='*70}\n")

    print(f"WELLNESS SCORE: {result['wellness_score']}%")
    print(f"BURNOUT STAGE:  [{result['severity']}] {result['burnout_label']}")
    print(f"                {result['burnout_description']}\n")

    print("FACTOR SCORES:")
    print("-" * 50)
    status_icons = {"green": "+", "yellow": "~", "orange": "!", "red": "X"}
    for key, data in result["factor_scores"].items():
        icon = status_icons.get(data["status"], "?")
        print(f"  [{icon}] {key:<25s} {data['score']:>2}/10  ({data['status']})")

    if result["risk_factors"]:
        print(f"\nRISK FACTORS ({len(result['risk_factors'])}):")
        for r in result["risk_factors"]:
            print(f"  [!] {r}")

    if result["protective_factors"]:
        print(f"\nPROTECTIVE FACTORS ({len(result['protective_factors'])}):")
        for p in result["protective_factors"]:
            print(f"  [+] {p}")

    print(f"\nRECOMMENDATIONS:")
    print("-" * 50)
    for r in result["recommendations"]:
        print(f"  -> {r}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Screen for founder burnout signals")
    parser.add_argument("--hours-per-week", type=float, required=True, help="Average work hours per week")
    parser.add_argument("--sleep-hours", type=float, required=True, help="Average sleep hours per night")
    parser.add_argument("--exercise-days", type=int, required=True, help="Exercise days per week (0-7)")
    parser.add_argument("--has-peer-group", action="store_true", help="Has active founder peer group")
    parser.add_argument("--has-coach", action="store_true", help="Has therapist, coach, or professional support")
    parser.add_argument("--vacation-days", type=int, default=5, help="Days off in last 6 months")
    parser.add_argument("--decision-fatigue", type=int, default=5, help="Decision fatigue self-rating (1-10)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = calculate_wellness(
        args.hours_per_week, args.sleep_hours, args.exercise_days,
        args.has_peer_group, args.has_coach,
        args.vacation_days, args.decision_fatigue
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
