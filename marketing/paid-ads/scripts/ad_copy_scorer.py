#!/usr/bin/env python3
"""
Ad Copy Scorer

Scores ad copy against platform specs, compliance rules,
and conversion best practices for Google, Meta, LinkedIn, TikTok.

Usage:
    python ad_copy_scorer.py --headline "Cut churn by 30%" --description "See how 1200 SaaS teams reduced churn" --platform google
    python ad_copy_scorer.py --file ads.json --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

PLATFORM_SPECS = {
    "google": {"headline_max": 30, "description_max": 90, "headlines_needed": 15, "descriptions_needed": 4},
    "meta": {"headline_max": 40, "description_max": 125, "headlines_needed": 5, "descriptions_needed": 5},
    "linkedin": {"headline_max": 70, "description_max": 150, "headlines_needed": 1, "descriptions_needed": 1},
    "twitter": {"headline_max": 70, "description_max": 280, "headlines_needed": 1, "descriptions_needed": 1},
    "tiktok": {"headline_max": 100, "description_max": 100, "headlines_needed": 1, "descriptions_needed": 1},
}

REJECTION_TRIGGERS = {
    "google": [
        (re.compile(r"\b[A-Z]{4,}\b"), "ALL CAPS (except standard acronyms)"),
        (re.compile(r"[!]{2,}|[?]{2,}"), "Excessive punctuation"),
        (re.compile(r"#1|best in class|industry.leading|guaranteed", re.IGNORECASE), "Unsubstantiated superlatives"),
        (re.compile(r"click here", re.IGNORECASE), "'Click here' is prohibited"),
    ],
    "meta": [
        (re.compile(r"(are you|do you)\s+(overweight|depressed|lonely|struggling)", re.IGNORECASE), "Personal attribute assumption"),
        (re.compile(r"[!]{2,}"), "Excessive exclamation marks"),
    ],
    "linkedin": [
        (re.compile(r"click.?bait|you won't believe", re.IGNORECASE), "Clickbait language prohibited"),
    ],
}

SPAM_WORDS = ["free", "guarantee", "act now", "limited time", "urgent", "winner", "cash", "earn money", "risk-free"]

STRONG_CTA_PATTERNS = [
    re.compile(r"(start|get|try|see|book|create|build|discover|join|unlock)\s", re.IGNORECASE),
]
WEAK_CTA_PATTERNS = [
    re.compile(r"(submit|click here|learn more|contact us|send)\b", re.IGNORECASE),
]


def score_ad(headline: str, description: str, platform: str, cta: str = "") -> dict:
    specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["google"])
    result = {
        "platform": platform,
        "headline": headline,
        "description": description,
        "cta": cta,
        "scores": {},
        "compliance": [],
        "issues": [],
        "suggestions": [],
    }

    score = 100

    # Length checks
    h_len = len(headline)
    d_len = len(description)
    h_max = specs["headline_max"]
    d_max = specs["description_max"]

    if h_len <= h_max:
        result["scores"]["headline_length"] = f"{h_len}/{h_max} chars"
    else:
        result["scores"]["headline_length"] = f"{h_len}/{h_max} chars (OVER)"
        result["issues"].append(f"Headline exceeds {h_max} char limit by {h_len - h_max} chars.")
        score -= 20

    if d_len <= d_max:
        result["scores"]["description_length"] = f"{d_len}/{d_max} chars"
    else:
        result["scores"]["description_length"] = f"{d_len}/{d_max} chars (OVER)"
        result["issues"].append(f"Description exceeds {d_max} char limit by {d_len - d_max} chars.")
        score -= 20

    # Compliance checks
    rejections = REJECTION_TRIGGERS.get(platform, [])
    combined = f"{headline} {description}"
    for pattern, reason in rejections:
        if pattern.search(combined):
            result["compliance"].append({"status": "REJECT", "reason": reason})
            score -= 15

    if not result["compliance"]:
        result["compliance"].append({"status": "PASS", "reason": "No rejection triggers detected"})

    # Spam words
    lower_combined = combined.lower()
    found_spam = [w for w in SPAM_WORDS if w in lower_combined]
    if found_spam:
        result["issues"].append(f"Spam trigger words: {', '.join(found_spam)}")
        score -= len(found_spam) * 5

    # Specificity check
    has_number = bool(re.search(r"\d+", combined))
    has_specific_claim = bool(re.search(r"\d+%|\d+x|\$\d+|\d+ (hours|days|weeks|minutes|teams|companies|customers)", combined, re.IGNORECASE))
    if has_specific_claim:
        result["scores"]["specificity"] = "high"
        result["suggestions"].append("Good: Specific claims with numbers are more compelling.")
    elif has_number:
        result["scores"]["specificity"] = "medium"
    else:
        result["scores"]["specificity"] = "low"
        result["suggestions"].append("Add specific numbers or metrics for stronger credibility.")
        score -= 8

    # CTA analysis
    if cta:
        is_strong = any(p.search(cta) for p in STRONG_CTA_PATTERNS)
        is_weak = any(p.search(cta) for p in WEAK_CTA_PATTERNS)
        if is_strong:
            result["scores"]["cta_strength"] = "strong"
        elif is_weak:
            result["scores"]["cta_strength"] = "weak"
            result["suggestions"].append("Strengthen CTA: use action verb + what they get (e.g., 'Start free trial').")
            score -= 5
        else:
            result["scores"]["cta_strength"] = "neutral"

    # Headline quality
    starts_with_benefit = bool(re.match(r"(Cut|Reduce|Save|Get|Build|Ship|Hire|Grow|Increase|Boost|Stop|Automate)", headline, re.IGNORECASE))
    if starts_with_benefit:
        result["suggestions"].append("Good: Headline leads with a benefit.")
    else:
        result["suggestions"].append("Consider leading headline with an action verb or benefit.")
        score -= 3

    result["overall_score"] = max(0, min(100, score))
    result["grade"] = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F"

    return result


def format_human(results: list) -> str:
    lines = ["\n" + "=" * 60, "  AD COPY SCORER", "=" * 60]
    for r in results:
        lines.append(f"\n  Platform: {r['platform'].title()} | Score: {r['overall_score']}/100 ({r['grade']})")
        lines.append(f"  Headline: \"{r['headline']}\" [{r['scores']['headline_length']}]")
        lines.append(f"  Description: \"{r['description'][:60]}...\" [{r['scores']['description_length']}]")
        if r["cta"]:
            lines.append(f"  CTA: \"{r['cta']}\" [{r['scores'].get('cta_strength', 'N/A')}]")

        for c in r["compliance"]:
            icon = "+" if c["status"] == "PASS" else "X"
            lines.append(f"    [{icon}] {c['reason']}")

        for i in r["issues"]:
            lines.append(f"    ! {i}")
        for s in r["suggestions"]:
            lines.append(f"    > {s}")
        lines.append("-" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score ad copy for platform compliance and conversion potential.")
    parser.add_argument("--headline", "-H")
    parser.add_argument("--description", "-d")
    parser.add_argument("--cta", default="")
    parser.add_argument("--platform", "-p", default="google", choices=list(PLATFORM_SPECS.keys()))
    parser.add_argument("--file", "-f", help="JSON file with multiple ads")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    results = []
    if args.file:
        try:
            data = json.loads(Path(args.file).read_text())
            ads = data if isinstance(data, list) else [data]
            for ad in ads:
                results.append(score_ad(ad.get("headline", ""), ad.get("description", ""), ad.get("platform", "google"), ad.get("cta", "")))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.headline and args.description:
        results.append(score_ad(args.headline, args.description, args.platform, args.cta))
    else:
        parser.print_help()
        sys.exit(1)

    if args.json_output:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    else:
        print(format_human(results))


if __name__ == "__main__":
    main()
