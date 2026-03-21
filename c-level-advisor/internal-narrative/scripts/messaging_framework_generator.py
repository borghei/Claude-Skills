#!/usr/bin/env python3
"""Messaging Framework Generator - Generate audience translation matrix from core narrative.

Takes a core narrative statement and generates audience-specific messaging for
employees, investors, customers, candidates, and partners.

Usage:
    python messaging_framework_generator.py --narrative "We are shifting from product A to product B"
    python messaging_framework_generator.py --narrative "We missed Q2 targets by 15%" --audiences employees,investors,customers --json
"""

import argparse
import json
import sys
from datetime import datetime

AUDIENCE_LENSES = {
    "employees": {
        "name": "Employees",
        "primary_question": "How does this affect my job, my team, and the company's future?",
        "communication_principles": [
            "Lead with honesty -- employees detect inauthenticity instantly",
            "Explain the 'why' before the 'what'",
            "Address job impact directly if relevant",
            "Provide clear next steps and how they can contribute",
            "Follow up within 48 hours with additional details"
        ],
        "tone": "Direct, honest, empathetic",
        "channel": "All-hands + written follow-up email",
        "timing": "First audience to hear (internal-first rule)",
        "frame_templates": {
            "positive_change": "This positions us for [outcome]. Here is what it means for your work: [specific impact]. Your contribution to this is [role].",
            "negative_change": "Here is what happened: [fact]. Here is why: [honest reason]. Here is the plan: [specific actions]. Here is how you can help: [contribution].",
            "strategic_shift": "We are making this change because [evidence-based reason]. Your work on [previous] matters because [connection]. Going forward, [new direction].",
            "uncertainty": "Here is what we know: [facts]. Here is what we do not know yet: [honest uncertainty]. I will update you by [specific date]."
        }
    },
    "investors": {
        "name": "Investors",
        "primary_question": "What does this mean for the business trajectory and my investment?",
        "communication_principles": [
            "Lead with metrics and business impact",
            "Frame in terms of capital efficiency and growth",
            "Include challenges alongside wins (builds trust)",
            "Make specific asks (intros, advice, decisions needed)",
            "Keep concise -- under 500 words for updates"
        ],
        "tone": "Data-driven, strategic, confident but honest",
        "channel": "Monthly written update + board meeting",
        "timing": "After employees, before external",
        "frame_templates": {
            "positive_change": "[Metric impact]: This drives [financial outcome]. Strategic rationale: [evidence]. Expected timeline: [specific].",
            "negative_change": "[Metric] came in at [actual] vs [target]. Root cause: [analysis]. Recovery plan: [specific actions with timeline]. Ask: [specific help needed].",
            "strategic_shift": "Market signal: [data]. Our response: [strategic move]. Expected impact: [financial projection]. Investment needed: [amount/resources].",
            "uncertainty": "Current position: [metrics]. Scenario range: [base/stress/severe]. Hedges in place: [specific]. Decision point: [date]."
        }
    },
    "customers": {
        "name": "Customers",
        "primary_question": "How does this affect my experience, my product, and my relationship with this company?",
        "communication_principles": [
            "Only communicate what is relevant to their experience",
            "Focus on value and continuity of service",
            "Proactive communication prevents speculation",
            "Provide clear point of contact for questions",
            "Never share internal financial struggles unless directly relevant"
        ],
        "tone": "Professional, reassuring, value-focused",
        "channel": "Email + account manager outreach for key accounts",
        "timing": "After internal alignment, before or alongside external",
        "frame_templates": {
            "positive_change": "We are [change] to better serve you. What this means for you: [specific benefit]. Your current [service/product] [continuity statement].",
            "negative_change": "We are aware of [issue]. Impact to you: [honest assessment]. What we are doing: [fix with timeline]. Your account manager [name] is available for questions.",
            "strategic_shift": "We are focusing on [new direction] because [customer benefit]. This means [positive impact]. Your [existing commitment] remains [unchanged/details].",
            "uncertainty": "We want to keep you informed: [relevant fact]. Your service is [status]. We will update you by [date]. Contact [person] with questions."
        }
    },
    "candidates": {
        "name": "Candidates",
        "primary_question": "Is this a company I want to join? Is it growing, stable, and exciting?",
        "communication_principles": [
            "Narrative must match employee reality (candidates will check)",
            "Highlight decisive leadership and clear direction",
            "Show both ambition and self-awareness",
            "Connect to mission and growth opportunity",
            "Be honest about challenges -- self-aware companies attract talent"
        ],
        "tone": "Energetic, mission-driven, transparent",
        "channel": "Careers page + interview conversations",
        "timing": "Updated within 1 week of major changes",
        "frame_templates": {
            "positive_change": "We are [change] because we see [opportunity]. This creates roles in [areas]. Join us as we [exciting direction].",
            "negative_change": "[Not typically shared externally unless public; if public:] We faced [challenge] and responded by [decisive action]. This is the kind of company that [positive framing of character].",
            "strategic_shift": "We made a strategic decision to focus on [area] based on [evidence]. This is an exciting time to join because [opportunity for candidate].",
            "uncertainty": "[Minimize; focus on vision and what is clear:] Our direction is [clear statement]. We are building [exciting thing] and looking for people who [traits]."
        }
    },
    "partners": {
        "name": "Partners",
        "primary_question": "Does this affect our integration, our joint roadmap, or our business relationship?",
        "communication_principles": [
            "Proactive communication preserves trust",
            "Focus on integration and joint value",
            "Be specific about timeline and technical impacts",
            "Provide clear escalation path for concerns",
            "Schedule business review if change is significant"
        ],
        "tone": "Professional, collaborative, specific",
        "channel": "Direct communication from partnership lead",
        "timing": "After internal, before public announcement",
        "frame_templates": {
            "positive_change": "We are [change]. Impact to our partnership: [specific]. Joint opportunity: [collaboration]. Next step: [meeting/review].",
            "negative_change": "Change affecting our integration: [specific]. Mitigation: [plan]. Timeline: [dates]. Let's schedule a call to discuss: [proposed time].",
            "strategic_shift": "Our strategic focus is shifting to [area]. For our partnership, this means: [impact]. Opportunities: [joint value]. Review meeting: [proposed date].",
            "uncertainty": "We are evaluating [topic]. Potential impact to partnership: [range]. We will share more by [date]. Current commitments: [unchanged/details]."
        }
    }
}


def classify_narrative(narrative):
    """Classify the narrative type based on content signals."""
    lower = narrative.lower()
    if any(word in lower for word in ["missed", "failed", "loss", "decline", "below", "reduction", "layoff", "cut"]):
        return "negative_change"
    if any(word in lower for word in ["shifting", "pivot", "moving", "transitioning", "restructuring", "changing direction"]):
        return "strategic_shift"
    if any(word in lower for word in ["uncertain", "evaluating", "exploring", "don't know", "investigating"]):
        return "uncertainty"
    return "positive_change"


def generate_framework(narrative, audiences):
    """Generate messaging framework from core narrative."""
    narrative_type = classify_narrative(narrative)

    translations = []
    for aud_key in audiences:
        if aud_key not in AUDIENCE_LENSES:
            continue
        lens = AUDIENCE_LENSES[aud_key]
        template = lens["frame_templates"].get(narrative_type, lens["frame_templates"]["positive_change"])

        translations.append({
            "audience": lens["name"],
            "key": aud_key,
            "primary_question": lens["primary_question"],
            "recommended_tone": lens["tone"],
            "channel": lens["channel"],
            "timing": lens["timing"],
            "message_template": template,
            "principles": lens["communication_principles"]
        })

    # Consistency reminders
    consistency_checks = [
        "Verify: all audiences receive the same underlying facts",
        "Verify: no audience learns about this from a different audience first",
        "Verify: tone differences reflect audience needs, not different facts",
        "Verify: metrics cited are consistent across all communications",
        "Verify: timeline commitments are the same everywhere"
    ]

    return {
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "core_narrative": narrative,
        "narrative_type": narrative_type,
        "audiences": len(translations),
        "translation_matrix": translations,
        "consistency_checks": consistency_checks,
        "communication_sequence": [
            {"order": 1, "audience": "Employees", "timing": "First (internal-first rule)"},
            {"order": 2, "audience": "Board/Investors", "timing": "Same day or next day"},
            {"order": 3, "audience": "Partners", "timing": "Before public announcement"},
            {"order": 4, "audience": "Customers", "timing": "Before or with public announcement"},
            {"order": 5, "audience": "Candidates/Public", "timing": "After all stakeholders informed"}
        ]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"MESSAGING FRAMEWORK")
    print(f"Generated: {result['generated_date']}")
    print(f"{'='*70}\n")

    print(f"CORE NARRATIVE: {result['core_narrative']}")
    print(f"TYPE: {result['narrative_type'].replace('_', ' ').title()}\n")

    for t in result["translation_matrix"]:
        print(f"\n--- {t['audience'].upper()} ---")
        print(f"  They ask: {t['primary_question']}")
        print(f"  Tone: {t['recommended_tone']}")
        print(f"  Channel: {t['channel']}")
        print(f"  Timing: {t['timing']}")
        print(f"\n  Message Template:")
        print(f"    {t['message_template']}")
        print(f"\n  Principles:")
        for p in t["principles"]:
            print(f"    - {p}")

    print(f"\nCOMMUNICATION SEQUENCE:")
    for s in result["communication_sequence"]:
        print(f"  {s['order']}. {s['audience']} ({s['timing']})")

    print(f"\nCONSISTENCY CHECKS:")
    for c in result["consistency_checks"]:
        print(f"  [ ] {c}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Generate audience translation matrix from core narrative")
    parser.add_argument("--narrative", required=True, help="Core narrative statement")
    parser.add_argument("--audiences", default="employees,investors,customers,candidates,partners",
                        help="Comma-separated audiences")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    audiences = [a.strip().lower() for a in args.audiences.split(",")]
    result = generate_framework(args.narrative, audiences)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
