#!/usr/bin/env python3
"""
Interview Scorecard Generator - Generate structured interview scorecards.

Creates competency-based interview scorecards tailored to role and level,
with behavioral interview questions, rating scales, and evaluation criteria.

Usage:
    python interview_scorecard.py --role "Senior Engineer" --level IC3
    python interview_scorecard.py --role "Product Manager" --level IC2 --stage technical --json
    python interview_scorecard.py --role "Sales Manager" --level M1 --competencies leadership,negotiation,analytics

Input: Role name, level, optional stage and custom competencies.

Output: Structured interview scorecard in markdown or JSON format.
"""

import argparse
import json
import sys
from datetime import date


# --- Competency library ---

COMPETENCY_LIBRARY = {
    "technical_depth": {
        "name": "Technical Depth",
        "description": "Demonstrates deep expertise in relevant technical domain",
        "questions": [
            "Describe the most technically challenging project you have worked on. What made it difficult and how did you approach it?",
            "Walk me through a technical decision you made that had significant trade-offs. How did you evaluate the options?",
            "Tell me about a time you had to learn a new technology or framework quickly to deliver a project. What was your approach?",
        ],
        "signals_strong": ["Explains complex concepts clearly", "Demonstrates depth beyond surface level", "Shows awareness of trade-offs and edge cases"],
        "signals_weak": ["Cannot explain past work in detail", "Lacks awareness of alternatives", "Struggles with follow-up questions"],
    },
    "problem_solving": {
        "name": "Problem Solving",
        "description": "Approaches complex problems systematically and creatively",
        "questions": [
            "Describe a complex problem you solved that did not have an obvious solution. Walk me through your approach step by step.",
            "Tell me about a time you identified a problem before anyone else noticed. What did you do?",
            "Give an example of when you had to make a decision with incomplete information. How did you handle the uncertainty?",
        ],
        "signals_strong": ["Breaks problems into components", "Considers multiple approaches", "Uses data to validate assumptions"],
        "signals_weak": ["Jumps to solutions without analysis", "Cannot articulate reasoning", "Relies on single approach"],
    },
    "communication": {
        "name": "Communication",
        "description": "Communicates clearly and adapts style to audience",
        "questions": [
            "Tell me about a time you had to explain a complex idea to a non-technical audience. How did you ensure understanding?",
            "Describe a situation where miscommunication caused a problem. How did you resolve it and what did you learn?",
            "Give an example of how you gave constructive feedback to a peer or direct report.",
        ],
        "signals_strong": ["Adapts communication to audience", "Listens actively", "Structures information clearly"],
        "signals_weak": ["Uses excessive jargon", "Interrupts or talks over others", "Cannot simplify complex ideas"],
    },
    "leadership": {
        "name": "Leadership",
        "description": "Leads teams effectively and drives outcomes through others",
        "questions": [
            "Tell me about a time you led a team through a difficult situation. What was the outcome?",
            "Describe how you have developed someone on your team. What was your approach and what was the result?",
            "Give an example of when you had to make an unpopular decision. How did you handle the pushback?",
        ],
        "signals_strong": ["Empowers team members", "Takes accountability for outcomes", "Develops others proactively"],
        "signals_weak": ["Micromanages", "Avoids difficult decisions", "Takes credit for team work"],
    },
    "collaboration": {
        "name": "Collaboration",
        "description": "Works effectively across teams and functions",
        "questions": [
            "Give an example of a successful cross-functional project you contributed to. What was your role?",
            "Tell me about a time you disagreed with a colleague on an approach. How did you resolve it?",
            "Describe a situation where you had to build alignment across multiple stakeholders with competing priorities.",
        ],
        "signals_strong": ["Seeks input from others", "Builds consensus", "Gives credit to team"],
        "signals_weak": ["Works in isolation", "Cannot compromise", "Creates friction with other teams"],
    },
    "execution": {
        "name": "Execution & Delivery",
        "description": "Delivers results consistently and manages competing priorities",
        "questions": [
            "Tell me about a project where the requirements changed significantly mid-stream. How did you adapt?",
            "Describe a time you had to deliver under a tight deadline. What trade-offs did you make?",
            "Give an example of how you prioritized competing demands when you could not do everything.",
        ],
        "signals_strong": ["Delivers on commitments", "Manages scope effectively", "Communicates blockers early"],
        "signals_weak": ["Misses deadlines without communication", "Cannot prioritize", "Over-commits"],
    },
    "strategic_thinking": {
        "name": "Strategic Thinking",
        "description": "Thinks beyond immediate scope and connects work to business outcomes",
        "questions": [
            "Tell me about a time you identified a strategic opportunity that others had missed. What did you do?",
            "Describe how you have connected your team's work to broader business objectives.",
            "Give an example of a long-term bet you made that paid off. How did you build conviction?",
        ],
        "signals_strong": ["Connects work to business impact", "Thinks in systems", "Anticipates future needs"],
        "signals_weak": ["Focuses only on immediate tasks", "Cannot articulate business context", "Reactive rather than proactive"],
    },
    "customer_focus": {
        "name": "Customer Focus",
        "description": "Puts customer needs at the center of decisions",
        "questions": [
            "Tell me about a time you went above and beyond for a customer or end user.",
            "Describe a decision you made based on customer feedback that changed your team's direction.",
            "Give an example of how you balanced customer requests with technical or business constraints.",
        ],
        "signals_strong": ["References customer impact in decisions", "Seeks direct customer feedback", "Advocates for user experience"],
        "signals_weak": ["Never mentions customers", "Prioritizes internal convenience over user needs", "Cannot describe user impact"],
    },
    "negotiation": {
        "name": "Negotiation",
        "description": "Negotiates effectively to achieve mutually beneficial outcomes",
        "questions": [
            "Describe a negotiation where you achieved a better outcome than expected. What was your strategy?",
            "Tell me about a time you had to negotiate with limited leverage. How did you approach it?",
            "Give an example of a negotiation that did not go well. What would you do differently?",
        ],
        "signals_strong": ["Prepares thoroughly", "Finds creative solutions", "Maintains relationships"],
        "signals_weak": ["Confrontational approach", "Caves too easily", "Cannot articulate value proposition"],
    },
    "analytics": {
        "name": "Analytical Skills",
        "description": "Uses data and analysis to drive decisions",
        "questions": [
            "Tell me about a time you used data to change a decision or strategy.",
            "Describe a situation where the data was ambiguous. How did you reach a conclusion?",
            "Give an example of a metric or dashboard you created that drove a business outcome.",
        ],
        "signals_strong": ["Asks for data before deciding", "Distinguishes correlation from causation", "Builds frameworks for analysis"],
        "signals_weak": ["Relies on gut feeling", "Cherry-picks data", "Cannot interpret basic metrics"],
    },
}

# --- Default competency sets by role type ---

ROLE_COMPETENCIES = {
    "engineer": ["technical_depth", "problem_solving", "communication", "collaboration", "execution"],
    "manager": ["leadership", "communication", "strategic_thinking", "execution", "collaboration"],
    "product": ["strategic_thinking", "communication", "customer_focus", "analytics", "collaboration"],
    "sales": ["negotiation", "communication", "customer_focus", "execution", "analytics"],
    "design": ["customer_focus", "communication", "collaboration", "problem_solving", "execution"],
    "data": ["technical_depth", "analytics", "problem_solving", "communication", "execution"],
    "default": ["problem_solving", "communication", "collaboration", "execution", "strategic_thinking"],
}

# --- Competency weights by level ---

LEVEL_WEIGHTS = {
    "IC1": {"technical_depth": 40, "problem_solving": 25, "communication": 20, "collaboration": 15},
    "IC2": {"technical_depth": 35, "problem_solving": 25, "communication": 20, "collaboration": 20},
    "IC3": {"technical_depth": 30, "problem_solving": 25, "communication": 20, "collaboration": 15, "leadership": 10},
    "IC4": {"technical_depth": 25, "problem_solving": 20, "communication": 20, "strategic_thinking": 20, "leadership": 15},
    "IC5": {"technical_depth": 20, "strategic_thinking": 25, "leadership": 20, "communication": 20, "problem_solving": 15},
    "M1": {"leadership": 30, "communication": 25, "execution": 20, "collaboration": 15, "strategic_thinking": 10},
    "M2": {"leadership": 25, "strategic_thinking": 25, "communication": 20, "execution": 15, "collaboration": 15},
    "VP": {"strategic_thinking": 30, "leadership": 30, "communication": 20, "execution": 20},
}

STAGES = ["phone_screen", "technical", "behavioral", "final", "hiring_manager"]

RATING_SCALE = {
    1: "Does Not Meet - No evidence of competency; significant concerns",
    2: "Partially Meets - Limited evidence; below expectations for level",
    3: "Meets Expectations - Solid evidence; appropriate for level",
    4: "Exceeds Expectations - Strong evidence; above level expectations",
    5: "Exceptional - Outstanding evidence; role-model level performance",
}


def detect_role_type(role: str) -> str:
    """Detect role type from role name."""
    role_lower = role.lower()
    for key in ROLE_COMPETENCIES:
        if key in role_lower:
            return key
    if any(w in role_lower for w in ["software", "backend", "frontend", "fullstack", "devops", "sre", "infrastructure", "platform"]):
        return "engineer"
    if any(w in role_lower for w in ["director", "vp", "head of", "lead"]):
        return "manager"
    if any(w in role_lower for w in ["product", "pm"]):
        return "product"
    if any(w in role_lower for w in ["account", "sales", "bd", "business development"]):
        return "sales"
    if any(w in role_lower for w in ["ux", "ui", "design"]):
        return "design"
    if any(w in role_lower for w in ["data", "analytics", "ml", "machine learning"]):
        return "data"
    return "default"


def get_competencies(role: str, level: str, custom: list = None) -> list:
    """Get competencies for the role and level."""
    if custom:
        comp_keys = []
        for c in custom:
            c_clean = c.strip().lower().replace(" ", "_")
            if c_clean in COMPETENCY_LIBRARY:
                comp_keys.append(c_clean)
            else:
                # Create a basic custom competency
                COMPETENCY_LIBRARY[c_clean] = {
                    "name": c.strip().title(),
                    "description": f"Demonstrates proficiency in {c.strip().lower()}",
                    "questions": [f"Tell me about your experience with {c.strip().lower()}."],
                    "signals_strong": ["Provides specific examples", "Shows depth of knowledge"],
                    "signals_weak": ["Cannot provide examples", "Surface-level understanding"],
                }
                comp_keys.append(c_clean)
        return comp_keys

    role_type = detect_role_type(role)
    return ROLE_COMPETENCIES.get(role_type, ROLE_COMPETENCIES["default"])


def get_weights(level: str, competencies: list) -> dict:
    """Get competency weights for the level."""
    level_upper = level.upper()
    base_weights = LEVEL_WEIGHTS.get(level_upper, {})

    weights = {}
    total_assigned = 0
    for comp in competencies:
        if comp in base_weights:
            weights[comp] = base_weights[comp]
            total_assigned += base_weights[comp]

    remaining = 100 - total_assigned
    unweighted = [c for c in competencies if c not in weights]
    if unweighted:
        per_comp = remaining // len(unweighted)
        for c in unweighted:
            weights[c] = per_comp

    # Normalize to 100%
    total = sum(weights.values())
    if total > 0 and total != 100:
        factor = 100 / total
        weights = {k: round(v * factor) for k, v in weights.items()}

    return weights


def build_scorecard(role: str, level: str, stage: str, competencies: list) -> dict:
    """Build the complete scorecard."""
    weights = get_weights(level, competencies)

    comp_details = []
    for comp_key in competencies:
        comp = COMPETENCY_LIBRARY[comp_key]
        comp_details.append({
            "key": comp_key,
            "name": comp["name"],
            "description": comp["description"],
            "weight": weights.get(comp_key, 20),
            "questions": comp["questions"],
            "signals_strong": comp["signals_strong"],
            "signals_weak": comp["signals_weak"],
        })

    return {
        "role": role,
        "level": level,
        "stage": stage,
        "date": date.today().isoformat(),
        "competencies": comp_details,
        "rating_scale": RATING_SCALE,
        "instructions": {
            "before_interview": [
                "Review the candidate's resume and any prior interview notes",
                "Prepare 1-2 follow-up questions per competency",
                "Clear 15 minutes after the interview for note-taking",
            ],
            "during_interview": [
                "Ask behavioral questions using STAR format (Situation, Task, Action, Result)",
                "Take brief notes on specific examples and evidence",
                "Rate each competency independently before discussing with other interviewers",
            ],
            "after_interview": [
                "Complete all ratings within 24 hours while memory is fresh",
                "Provide specific behavioral evidence for each rating",
                "Submit scorecard before the debrief to prevent anchoring bias",
            ],
        },
    }


def format_markdown(scorecard: dict) -> str:
    """Format scorecard as markdown."""
    lines = []
    lines.append(f"# Interview Scorecard: {scorecard['role']} ({scorecard['level']})")
    lines.append("")
    lines.append(f"**Stage:** {scorecard['stage'].replace('_', ' ').title()}")
    lines.append(f"**Date:** {scorecard['date']}")
    lines.append(f"**Interviewer:** ____________________")
    lines.append(f"**Candidate:** ____________________")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Rating Scale")
    lines.append("")
    for rating, desc in scorecard["rating_scale"].items():
        lines.append(f"- **{rating}** - {desc}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Competency Ratings")
    lines.append("")
    lines.append("| Competency | Weight | Rating (1-5) | Evidence |")
    lines.append("|------------|--------|:------------:|----------|")
    for comp in scorecard["competencies"]:
        lines.append(f"| {comp['name']} | {comp['weight']}% | ____ | |")
    lines.append("")
    lines.append("**Weighted Score:** ______ / 5.0")
    lines.append("")

    lines.append("---")
    lines.append("")
    for comp in scorecard["competencies"]:
        lines.append(f"## {comp['name']} ({comp['weight']}%)")
        lines.append(f"*{comp['description']}*")
        lines.append("")
        lines.append("### Suggested Questions")
        for q in comp["questions"]:
            lines.append(f"- {q}")
        lines.append("")
        lines.append("### Strong Signals")
        for s in comp["signals_strong"]:
            lines.append(f"- {s}")
        lines.append("")
        lines.append("### Weak Signals")
        for s in comp["signals_weak"]:
            lines.append(f"- {s}")
        lines.append("")
        lines.append(f"**Rating:** ____ / 5")
        lines.append(f"**Evidence:** ")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Overall Assessment")
    lines.append("")
    lines.append("**Recommendation:**")
    lines.append("- [ ] Strong Hire")
    lines.append("- [ ] Hire")
    lines.append("- [ ] No Hire")
    lines.append("- [ ] Strong No Hire")
    lines.append("")
    lines.append("**Key Strengths:**")
    lines.append("1. ")
    lines.append("2. ")
    lines.append("")
    lines.append("**Key Concerns:**")
    lines.append("1. ")
    lines.append("2. ")
    lines.append("")

    lines.append("## Interview Instructions")
    lines.append("")
    for phase, instructions in scorecard["instructions"].items():
        lines.append(f"### {phase.replace('_', ' ').title()}")
        for inst in instructions:
            lines.append(f"- {inst}")
        lines.append("")

    return "\n".join(lines)


def format_human(scorecard: dict) -> str:
    """Format scorecard for terminal output."""
    lines = []
    lines.append("=" * 65)
    lines.append(f"INTERVIEW SCORECARD: {scorecard['role']} ({scorecard['level']})")
    lines.append("=" * 65)
    lines.append(f"  Stage: {scorecard['stage'].replace('_', ' ').title()}")
    lines.append(f"  Date:  {scorecard['date']}")
    lines.append("")

    lines.append("-" * 65)
    lines.append("COMPETENCIES")
    lines.append("-" * 65)
    lines.append(f"  {'Competency':<30} {'Weight':>8}")
    lines.append(f"  {'-'*30} {'-'*8}")
    for comp in scorecard["competencies"]:
        lines.append(f"  {comp['name']:<30} {comp['weight']:>7}%")

    lines.append("")
    lines.append("-" * 65)
    lines.append("QUESTIONS BY COMPETENCY")
    lines.append("-" * 65)
    for comp in scorecard["competencies"]:
        lines.append(f"\n  [{comp['name']}]")
        for i, q in enumerate(comp["questions"], 1):
            lines.append(f"    {i}. {q}")

    lines.append("")
    lines.append("-" * 65)
    lines.append("RATING SCALE")
    lines.append("-" * 65)
    for rating, desc in scorecard["rating_scale"].items():
        lines.append(f"  {rating} = {desc}")

    lines.append("")
    lines.append("Use --json for machine-readable output or pipe to a file for the full markdown scorecard.")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate structured interview scorecards for a given role and level."
    )
    parser.add_argument("--role", required=True, help="Role title (e.g., 'Senior Engineer', 'Product Manager')")
    parser.add_argument("--level", required=True, help="Level code (IC1-IC5, M1-M2, VP)")
    parser.add_argument("--stage", default="behavioral", choices=STAGES, help="Interview stage (default: behavioral)")
    parser.add_argument("--competencies", default=None, help="Comma-separated list of competencies to override defaults")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--markdown", action="store_true", help="Output as full markdown scorecard")
    args = parser.parse_args()

    custom_comps = args.competencies.split(",") if args.competencies else None
    competencies = get_competencies(args.role, args.level, custom_comps)
    scorecard = build_scorecard(args.role, args.level, args.stage, competencies)

    if args.json:
        print(json.dumps(scorecard, indent=2))
    elif args.markdown:
        print(format_markdown(scorecard))
    else:
        print(format_human(scorecard))


if __name__ == "__main__":
    main()
