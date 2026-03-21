#!/usr/bin/env python3
"""Paywall Copy Scorer - Score paywall screen copy against proven conversion patterns.

Evaluates headline structure, benefit clarity, CTA strength, social proof presence,
escape hatch quality, and dark-pattern risk. Outputs a 0-100 score with itemized feedback.

Usage:
    python paywall_copy_scorer.py copy.json
    python paywall_copy_scorer.py copy.json --format json
"""

import argparse
import json
import re
import sys
from typing import Any


# Scoring weights (total = 100)
SCORING_WEIGHTS = {
    "headline": 20,
    "benefits": 20,
    "cta": 15,
    "social_proof": 10,
    "escape_hatch": 15,
    "price_clarity": 10,
    "dark_pattern_check": 10,
}

DARK_PATTERN_PHRASES = [
    "no, i don't want to",
    "no thanks, i prefer to",
    "i don't need",
    "i hate saving",
    "i'll pay full price",
    "no, i want to miss out",
    "i don't like",
]

STRONG_CTA_PATTERNS = [
    r"^(start|get|upgrade|unlock|try|continue|claim|activate)",
    r"(free|trial|pro|premium|plan)",
]

WEAK_CTA_PATTERNS = [
    r"^(submit|click here|buy now|purchase|pay)",
]

BENEFIT_SIGNAL_WORDS = [
    "save", "unlock", "unlimited", "faster", "more", "better",
    "increase", "reduce", "automate", "grow", "access",
]


def score_headline(headline: str) -> tuple[float, list[str]]:
    """Score headline quality (0-1)."""
    score = 0.0
    feedback = []

    if not headline:
        return 0.0, ["Missing headline -- this is the most important copy element"]

    words = headline.split()
    word_count = len(words)

    # Length check (6-12 words ideal)
    if 6 <= word_count <= 12:
        score += 0.3
    elif 4 <= word_count <= 15:
        score += 0.15
        feedback.append(f"Headline is {word_count} words -- ideal is 6-12 words")
    else:
        feedback.append(f"Headline is {word_count} words -- too {'short' if word_count < 4 else 'long'} (target 6-12)")

    # Benefit/outcome focus
    lower = headline.lower()
    has_benefit = any(word in lower for word in BENEFIT_SIGNAL_WORDS)
    if has_benefit:
        score += 0.3
    else:
        feedback.append("Headline lacks benefit/outcome language -- use words like 'unlock', 'save', 'unlimited'")

    # Value proposition pattern (e.g., "Unlock X to Y")
    if " to " in lower or " for " in lower or " with " in lower:
        score += 0.2
    else:
        feedback.append("Consider 'Unlock [Feature] to [Benefit]' pattern for stronger value framing")

    # Not generic
    generic_phrases = ["upgrade now", "go premium", "buy now", "subscribe"]
    if any(phrase in lower for phrase in generic_phrases):
        score -= 0.1
        feedback.append("Headline is generic -- make it specific to the value the user will get")
    else:
        score += 0.2

    return min(max(score, 0.0), 1.0), feedback


def score_benefits(benefits: list[str]) -> tuple[float, list[str]]:
    """Score benefit list quality (0-1)."""
    score = 0.0
    feedback = []

    if not benefits:
        return 0.0, ["Missing benefit list -- include 3-5 specific benefits"]

    count = len(benefits)

    # Count check (3-5 ideal)
    if 3 <= count <= 5:
        score += 0.3
    elif count < 3:
        score += 0.1
        feedback.append(f"Only {count} benefits listed -- aim for 3-5")
    else:
        score += 0.15
        feedback.append(f"{count} benefits listed -- more than 5 reduces scanability")

    # Specificity check
    specific_count = 0
    for benefit in benefits:
        if any(char.isdigit() for char in benefit):
            specific_count += 1
        elif any(word in benefit.lower() for word in BENEFIT_SIGNAL_WORDS):
            specific_count += 1

    specificity_ratio = specific_count / count if count > 0 else 0
    if specificity_ratio >= 0.6:
        score += 0.4
    elif specificity_ratio >= 0.3:
        score += 0.2
        feedback.append("Some benefits are vague -- add numbers or specific outcomes")
    else:
        feedback.append("Benefits lack specificity -- use concrete numbers and outcomes")

    # Outcome vs feature check
    feature_words = ["includes", "comes with", "has", "features"]
    outcome_words = ["save", "reduce", "increase", "automate", "unlock", "get"]
    outcome_count = sum(1 for b in benefits if any(w in b.lower() for w in outcome_words))
    feature_count = sum(1 for b in benefits if any(w in b.lower() for w in feature_words))

    if outcome_count > feature_count:
        score += 0.3
    elif outcome_count == feature_count and outcome_count > 0:
        score += 0.2
    else:
        feedback.append("Benefits read as features -- rewrite as outcomes (what the user achieves, not what the product has)")

    return min(max(score, 0.0), 1.0), feedback


def score_cta(cta: str) -> tuple[float, list[str]]:
    """Score CTA button text quality (0-1)."""
    score = 0.0
    feedback = []

    if not cta:
        return 0.0, ["Missing CTA -- every paywall needs a clear primary action button"]

    lower = cta.lower().strip()
    words = cta.split()

    # Length (2-5 words ideal)
    if 2 <= len(words) <= 5:
        score += 0.3
    else:
        feedback.append(f"CTA is {len(words)} words -- aim for 2-5 words")

    # Strong action verb
    if any(re.search(pattern, lower) for pattern in STRONG_CTA_PATTERNS):
        score += 0.4
    elif any(re.search(pattern, lower) for pattern in WEAK_CTA_PATTERNS):
        score += 0.1
        feedback.append("CTA uses weak verb -- 'Start Pro Plan' converts better than 'Buy Now' or 'Submit'")
    else:
        score += 0.2
        feedback.append("CTA could be more action-oriented -- start with a verb like 'Start', 'Get', 'Unlock'")

    # Specificity (mentions plan or benefit)
    if any(word in lower for word in ["pro", "premium", "plan", "trial", "free"]):
        score += 0.3
    else:
        feedback.append("CTA should mention the plan name or benefit (e.g., 'Start Pro Plan' not just 'Upgrade')")

    return min(max(score, 0.0), 1.0), feedback


def score_social_proof(social_proof: str) -> tuple[float, list[str]]:
    """Score social proof element (0-1)."""
    score = 0.0
    feedback = []

    if not social_proof:
        feedback.append("Missing social proof -- add a line like 'Join 5,000+ teams on Pro'")
        return 0.0, feedback

    lower = social_proof.lower()

    # Has numbers
    if any(char.isdigit() for char in social_proof):
        score += 0.5
    else:
        feedback.append("Social proof lacks numbers -- '5,000+ teams' is more compelling than 'many teams'")

    # Has social context
    social_words = ["teams", "companies", "users", "customers", "professionals", "people", "businesses"]
    if any(word in lower for word in social_words):
        score += 0.3
    else:
        feedback.append("Add who uses the product (teams, companies, professionals)")

    # Credibility
    if any(word in lower for word in ["join", "trusted", "loved", "rated", "chosen"]):
        score += 0.2

    return min(max(score, 0.0), 1.0), feedback


def score_escape_hatch(escape_hatch: str) -> tuple[float, list[str]]:
    """Score escape hatch / decline text (0-1)."""
    score = 0.0
    feedback = []

    if not escape_hatch:
        feedback.append("Missing escape hatch -- always provide 'Not now' or 'Maybe later' option")
        return 0.0, feedback

    lower = escape_hatch.lower().strip()

    # Check for dark patterns
    for phrase in DARK_PATTERN_PHRASES:
        if phrase in lower:
            feedback.append(f"DARK PATTERN: '{escape_hatch}' uses shame language -- replace with neutral text")
            return 0.0, feedback

    # Neutral and respectful
    neutral_options = ["not now", "maybe later", "no thanks", "skip", "i'll skip", "remind me later", "close"]
    if any(opt in lower for opt in neutral_options):
        score += 0.7
    else:
        score += 0.3
        feedback.append("Decline text should be clearly neutral: 'Not now', 'Maybe later', 'No thanks'")

    # Readable length
    if len(escape_hatch.split()) <= 4:
        score += 0.3
    else:
        feedback.append("Keep decline text short (3-4 words max)")

    return min(max(score, 0.0), 1.0), feedback


def score_price_clarity(price_display: str) -> tuple[float, list[str]]:
    """Score price display clarity (0-1)."""
    score = 0.0
    feedback = []

    if not price_display:
        feedback.append("Missing price display -- show the price clearly before the CTA")
        return 0.0, feedback

    # Has actual price
    if re.search(r'\$[\d,]+', price_display) or re.search(r'[\d,]+\s*(\/|per)\s*(month|mo|year|yr)', price_display):
        score += 0.5
    else:
        feedback.append("Price display should include the actual dollar amount")

    # Has billing period
    if any(word in price_display.lower() for word in ["month", "mo", "year", "yr", "annual", "weekly"]):
        score += 0.3
    else:
        feedback.append("Include billing period (per month, per year)")

    # Annual savings shown
    if any(word in price_display.lower() for word in ["save", "free", "off", "discount"]):
        score += 0.2
    else:
        feedback.append("Show annual savings to encourage longer commitments ('Save 20%' or '2 months free')")

    return min(max(score, 0.0), 1.0), feedback


def check_dark_patterns(data: dict) -> tuple[float, list[str]]:
    """Check for dark patterns across all copy (0-1, where 1 = no dark patterns)."""
    score = 1.0
    feedback = []

    # Check decline text
    decline = data.get("escape_hatch", "").lower()
    for phrase in DARK_PATTERN_PHRASES:
        if phrase in decline:
            score -= 0.5
            feedback.append(f"Shame language in decline text: '{data.get('escape_hatch')}'")
            break

    # Check for hidden close
    if data.get("close_button_visible") is False:
        score -= 0.3
        feedback.append("Close button is hidden or hard to find -- this is a dark pattern")

    # Check for fake urgency
    if data.get("has_countdown_timer") and not data.get("countdown_is_genuine"):
        score -= 0.3
        feedback.append("Countdown timer resets or is not tied to a real deadline -- fake urgency destroys trust")

    # Check for confusing plan selection
    if data.get("pre_selected_most_expensive"):
        score -= 0.2
        feedback.append("Pre-selecting the most expensive plan without justification feels manipulative")

    if not feedback:
        feedback.append("No dark patterns detected")

    return max(score, 0.0), feedback


def score_paywall_copy(data: dict) -> dict:
    """Score complete paywall copy configuration."""
    scores = {}
    all_feedback = {}

    # Score each component
    hl_score, hl_feedback = score_headline(data.get("headline", ""))
    scores["headline"] = hl_score
    all_feedback["headline"] = hl_feedback

    ben_score, ben_feedback = score_benefits(data.get("benefits", []))
    scores["benefits"] = ben_score
    all_feedback["benefits"] = ben_feedback

    cta_score, cta_feedback = score_cta(data.get("cta", ""))
    scores["cta"] = cta_score
    all_feedback["cta"] = cta_feedback

    sp_score, sp_feedback = score_social_proof(data.get("social_proof", ""))
    scores["social_proof"] = sp_score
    all_feedback["social_proof"] = sp_feedback

    eh_score, eh_feedback = score_escape_hatch(data.get("escape_hatch", ""))
    scores["escape_hatch"] = eh_score
    all_feedback["escape_hatch"] = eh_feedback

    pc_score, pc_feedback = score_price_clarity(data.get("price_display", ""))
    scores["price_clarity"] = pc_score
    all_feedback["price_clarity"] = pc_feedback

    dp_score, dp_feedback = check_dark_patterns(data)
    scores["dark_pattern_check"] = dp_score
    all_feedback["dark_pattern_check"] = dp_feedback

    # Calculate weighted total
    total_score = 0.0
    component_scores = {}
    for key, weight in SCORING_WEIGHTS.items():
        weighted = scores.get(key, 0) * weight
        total_score += weighted
        component_scores[key] = {
            "raw_score": round(scores.get(key, 0) * 100, 1),
            "weight": weight,
            "weighted_score": round(weighted, 1),
            "feedback": all_feedback.get(key, []),
        }

    # Rating
    if total_score >= 80:
        rating = "Excellent"
    elif total_score >= 60:
        rating = "Good"
    elif total_score >= 40:
        rating = "Needs Improvement"
    else:
        rating = "Poor"

    return {
        "total_score": round(total_score, 1),
        "rating": rating,
        "component_scores": component_scores,
        "max_possible": 100,
    }


def format_text(result: dict) -> str:
    """Format copy score as human-readable text."""
    lines = []

    lines.append("=" * 60)
    lines.append("PAYWALL COPY SCORE")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Total Score: {result['total_score']}/100  ({result['rating']})")
    lines.append("")

    lines.append("-" * 40)
    lines.append("COMPONENT SCORES")
    lines.append("-" * 40)

    for key, comp in result["component_scores"].items():
        label = key.replace("_", " ").title()
        lines.append(f"\n{label}: {comp['raw_score']}% (weight: {comp['weight']}pts -> {comp['weighted_score']}pts)")
        for fb in comp["feedback"]:
            lines.append(f"  - {fb}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Score paywall screen copy against proven conversion patterns."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with paywall copy elements",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = score_paywall_copy(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
