#!/usr/bin/env python3
"""
Headline Scorer

Score headline effectiveness against a 5-criteria rubric and generate
alternative copy suggestions across benefit, problem, and social proof axes.

Usage:
    python headline_scorer.py --headline "Marketing Automation Software"
    python headline_scorer.py --headline "Marketing Automation Software" --audience "B2B marketers" --json
"""

import argparse
import json
import sys
import re


CRITERIA = [
    {"key": "communicates_value", "label": "Communicates core value", "max": 2},
    {"key": "specific", "label": "Specific (numbers, outcomes)", "max": 2},
    {"key": "addresses_audience", "label": "Addresses target audience", "max": 2},
    {"key": "matches_traffic", "label": "Matches traffic source", "max": 2},
    {"key": "emotional_logical_hook", "label": "Emotional or logical hook", "max": 2},
]

WEAK_WORDS = [
    "innovative", "revolutionary", "powerful", "cutting-edge", "next-generation",
    "world-class", "best-in-class", "state-of-the-art", "leading", "premier",
    "ultimate", "advanced", "seamless", "robust", "scalable",
]

STRONG_SIGNALS = {
    "numbers": r'\d+',
    "percentages": r'\d+%',
    "time_savings": r'\d+\s*(hour|minute|day|week|month)',
    "money": r'\$\d+',
    "audience_words": r'(for|your|you)',
    "outcome_words": r'(save|grow|increase|reduce|boost|generate|get|build|start|achieve)',
    "specificity": r'(without|in \d|within)',
}


def score_headline(headline: str, audience: str, traffic_source: str) -> dict:
    """Score headline effectiveness."""
    headline_lower = headline.lower()
    word_count = len(headline.split())

    scores = {}
    analysis = []

    # --- Criterion 1: Communicates core value ---
    has_outcome = bool(re.search(STRONG_SIGNALS["outcome_words"], headline_lower))
    has_benefit = any(w in headline_lower for w in ["save", "grow", "increase", "reduce", "get", "free"])
    if has_outcome and has_benefit:
        scores["communicates_value"] = 2
        analysis.append({"criterion": "Core value", "score": 2, "note": "Clear benefit/outcome communicated"})
    elif has_outcome or has_benefit:
        scores["communicates_value"] = 1
        analysis.append({"criterion": "Core value", "score": 1, "note": "Partial -- outcome implied but not explicit"})
    else:
        scores["communicates_value"] = 0
        analysis.append({"criterion": "Core value", "score": 0, "note": "No clear benefit -- reads as a product description"})

    # --- Criterion 2: Specific ---
    has_number = bool(re.search(STRONG_SIGNALS["numbers"], headline))
    has_specificity = bool(re.search(STRONG_SIGNALS["specificity"], headline_lower))
    weak_count = sum(1 for w in WEAK_WORDS if w in headline_lower)

    if has_number and weak_count == 0:
        scores["specific"] = 2
        analysis.append({"criterion": "Specificity", "score": 2, "note": "Includes concrete numbers/data"})
    elif has_number or has_specificity:
        scores["specific"] = 1
        analysis.append({"criterion": "Specificity", "score": 1, "note": "Somewhat specific"})
    else:
        scores["specific"] = 0
        note = f"Generic. Weak words found: {', '.join(w for w in WEAK_WORDS if w in headline_lower)}" if weak_count > 0 else "Generic -- no numbers or specifics"
        analysis.append({"criterion": "Specificity", "score": 0, "note": note})

    # --- Criterion 3: Addresses audience ---
    has_audience = bool(re.search(STRONG_SIGNALS["audience_words"], headline_lower))
    if audience != "general" and audience.lower().split()[0] in headline_lower:
        scores["addresses_audience"] = 2
        analysis.append({"criterion": "Audience", "score": 2, "note": "Explicitly addresses target audience"})
    elif has_audience:
        scores["addresses_audience"] = 1
        analysis.append({"criterion": "Audience", "score": 1, "note": "Implies audience with 'you/your'"})
    else:
        scores["addresses_audience"] = 0
        analysis.append({"criterion": "Audience", "score": 0, "note": "No audience targeting"})

    # --- Criterion 4: Traffic source match ---
    if traffic_source == "paid-search":
        # Paid search needs exact keyword match
        scores["matches_traffic"] = 1  # Can't verify without keyword
        analysis.append({"criterion": "Traffic match", "score": 1, "note": "Verify headline matches paid search keywords"})
    elif traffic_source == "paid-social":
        # Social needs hook
        if "?" in headline or any(w in headline_lower for w in ["stop", "tired", "why", "how"]):
            scores["matches_traffic"] = 2
            analysis.append({"criterion": "Traffic match", "score": 2, "note": "Good hook for social traffic"})
        else:
            scores["matches_traffic"] = 0
            analysis.append({"criterion": "Traffic match", "score": 0, "note": "Social traffic needs a stronger hook (question, pain point)"})
    else:
        scores["matches_traffic"] = 1
        analysis.append({"criterion": "Traffic match", "score": 1, "note": "Organic/email/referral -- moderate match assumed"})

    # --- Criterion 5: Hook ---
    has_question = "?" in headline
    has_emotion = any(w in headline_lower for w in ["stop", "never", "finally", "imagine", "tired", "hate", "love"])
    has_logic = has_number

    if (has_emotion or has_question) and has_logic:
        scores["emotional_logical_hook"] = 2
        analysis.append({"criterion": "Hook", "score": 2, "note": "Both emotional and logical elements"})
    elif has_emotion or has_question or has_logic:
        scores["emotional_logical_hook"] = 1
        analysis.append({"criterion": "Hook", "score": 1, "note": "One type of hook present"})
    else:
        scores["emotional_logical_hook"] = 0
        analysis.append({"criterion": "Hook", "score": 0, "note": "No emotional or logical hook"})

    total = sum(scores.values())
    max_total = 10

    if total >= 8:
        grade = "STRONG"
    elif total >= 6:
        grade = "ADEQUATE"
    elif total >= 4:
        grade = "NEEDS IMPROVEMENT"
    else:
        grade = "REWRITE NEEDED"

    # Length assessment
    if word_count <= 8:
        length_assessment = "Good -- concise"
    elif word_count <= 12:
        length_assessment = "Acceptable"
    else:
        length_assessment = "Too long -- trim to under 10 words"

    # Weak words found
    weak_found = [w for w in WEAK_WORDS if w in headline_lower]

    return {
        "headline": headline,
        "audience": audience,
        "traffic_source": traffic_source,
        "total_score": total,
        "max_score": max_total,
        "grade": grade,
        "word_count": word_count,
        "length_assessment": length_assessment,
        "weak_words_found": weak_found,
        "scores": scores,
        "analysis": analysis,
        "alternatives": _generate_alternatives(headline, audience),
        "recommendations": _generate_recommendations(total, analysis, weak_found),
    }


def _generate_alternatives(headline: str, audience: str) -> list:
    """Generate headline alternative frameworks."""
    return [
        {
            "axis": "Outcome-focused",
            "template": f"[Specific outcome with number] for {audience if audience != 'general' else '[your audience]'}",
            "example": "Generate 3X More Qualified Leads Without Adding Headcount",
        },
        {
            "axis": "Problem-focused",
            "template": "Stop [pain point] Because [root cause]",
            "example": "Stop Losing Leads Because Your Team Can't Follow Up Fast Enough",
        },
        {
            "axis": "Social proof",
            "template": "How [number]+ [audience] [achieve outcome]",
            "example": "How 2,000+ Marketing Teams Hit Their Pipeline Targets",
        },
    ]


def _generate_recommendations(score: int, analysis: list, weak_words: list) -> list:
    """Generate recommendations."""
    recs = []
    if score < 6:
        recs.append({
            "priority": "HIGH",
            "recommendation": "Headline scores below 6/10 -- rewrite recommended. Focus on a specific, measurable outcome.",
        })
    if weak_words:
        recs.append({
            "priority": "MEDIUM",
            "recommendation": f"Remove vague superlatives: {', '.join(weak_words)}. Replace with specific numbers or outcomes.",
        })

    low_scores = [a for a in analysis if a["score"] == 0]
    for ls in low_scores[:2]:
        recs.append({
            "priority": "HIGH",
            "recommendation": f"Fix: {ls['criterion']} -- {ls['note']}",
        })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"HEADLINE SCORER: {result['grade']} ({result['total_score']}/{result['max_score']})")
    lines.append("=" * 60)

    lines.append(f"\nHeadline: \"{result['headline']}\"")
    lines.append(f"Audience: {result['audience']}")
    lines.append(f"Traffic Source: {result['traffic_source']}")
    lines.append(f"Word Count: {result['word_count']} ({result['length_assessment']})")

    if result["weak_words_found"]:
        lines.append(f"Weak Words: {', '.join(result['weak_words_found'])}")

    lines.append(f"\n--- Criteria Scores ---")
    for a in result["analysis"]:
        lines.append(f"  {a['criterion']:<20} {a['score']}/2  {a['note']}")

    lines.append(f"\n--- Alternative Frameworks ---")
    for alt in result["alternatives"]:
        lines.append(f"\n  [{alt['axis']}]")
        lines.append(f"  Template: {alt['template']}")
        lines.append(f"  Example:  \"{alt['example']}\"")

    if result["recommendations"]:
        lines.append(f"\n--- Recommendations ---")
        for r in result["recommendations"]:
            lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score headline effectiveness and generate copy alternatives."
    )
    parser.add_argument("--headline", required=True, help="The headline text to score")
    parser.add_argument("--audience", default="general", help="Target audience description")
    parser.add_argument("--traffic-source", default="organic",
                        choices=["organic", "paid-search", "paid-social", "email", "referral"],
                        help="Primary traffic source")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    result = score_headline(args.headline, args.audience, args.traffic_source)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
