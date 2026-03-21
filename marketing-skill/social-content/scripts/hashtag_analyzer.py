#!/usr/bin/env python3
"""
Hashtag Analyzer

Analyzes hashtag usage in social media posts, scores relevance,
and recommends optimal hashtag strategy per platform.

Usage:
    python hashtag_analyzer.py "#marketing #growth #startup"
    python hashtag_analyzer.py --file post.txt --platform instagram --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

PLATFORM_LIMITS = {
    "linkedin": {"max": 5, "optimal": (3, 5), "note": "3-5 hashtags. Algorithm deprioritizes posts with 10+."},
    "twitter": {"max": 3, "optimal": (1, 2), "note": "1-2 hashtags. More than 3 looks spammy."},
    "instagram": {"max": 30, "optimal": (3, 5), "note": "3-5 relevant hashtags in 2026. Algorithm change reduced hashtag importance."},
    "tiktok": {"max": 5, "optimal": (3, 5), "note": "3-5 relevant hashtags. Mix niche and trending."},
    "facebook": {"max": 5, "optimal": (1, 3), "note": "1-3 hashtags maximum. Low impact on reach."},
}

# Common overly broad hashtags (low value due to saturation)
BROAD_HASHTAGS = {
    "marketing", "business", "success", "motivation", "entrepreneur",
    "startup", "innovation", "technology", "leadership", "growth",
    "digital", "strategy", "mindset", "goals", "hustle", "love",
    "instagood", "photooftheday", "followme", "follow4follow",
    "like4like", "likeforlike", "tbt", "instadaily", "picoftheday",
}

# Industry/niche hashtag patterns
NICHE_PATTERNS = [
    re.compile(r"#(saas|b2b|b2c|d2c|defi|fintech|healthtech|edtech|martech|proptech)", re.IGNORECASE),
    re.compile(r"#(\w+tips|\w+advice|\w+strategy|\w+hacks)", re.IGNORECASE),
    re.compile(r"#(\w+community|\w+life|\w+world)", re.IGNORECASE),
]

BRANDED_PATTERN = re.compile(r"#([A-Z][a-z]+[A-Z]|[a-z]+[A-Z])", re.IGNORECASE)


def extract_hashtags(text: str) -> list:
    return re.findall(r"#(\w+)", text)


def analyze_hashtag(tag: str) -> dict:
    lower = tag.lower()
    result = {
        "hashtag": f"#{tag}",
        "length": len(tag),
        "type": "standard",
        "quality": "medium",
        "issues": [],
    }

    # Check if too broad
    if lower in BROAD_HASHTAGS:
        result["type"] = "broad"
        result["quality"] = "low"
        result["issues"].append("Overly broad -- high competition, low discovery value")

    # Check if niche
    for pattern in NICHE_PATTERNS:
        if pattern.match(f"#{tag}"):
            result["type"] = "niche"
            result["quality"] = "high"
            break

    # Check if branded
    if BRANDED_PATTERN.match(tag):
        result["type"] = "branded"
        result["quality"] = "medium"

    # Length checks
    if len(tag) > 30:
        result["issues"].append("Too long -- hard to read and remember")
        result["quality"] = "low"
    elif len(tag) < 3:
        result["issues"].append("Too short -- likely too generic")
        result["quality"] = "low"

    # All caps
    if tag.isupper() and len(tag) > 3:
        result["issues"].append("ALL CAPS looks spammy")

    return result


def analyze_hashtags(text: str, platform: str = "linkedin") -> dict:
    tags = extract_hashtags(text)
    platform_config = PLATFORM_LIMITS.get(platform, PLATFORM_LIMITS["linkedin"])

    tag_analyses = [analyze_hashtag(t) for t in tags]

    # Count by quality
    quality_dist = {"high": 0, "medium": 0, "low": 0}
    type_dist = {"broad": 0, "niche": 0, "branded": 0, "standard": 0}
    for ta in tag_analyses:
        quality_dist[ta["quality"]] += 1
        type_dist[ta["type"]] += 1

    # Score
    score = 100
    issues = []
    recommendations = []

    # Count check
    count = len(tags)
    opt_min, opt_max = platform_config["optimal"]
    if count == 0:
        score -= 20
        issues.append("No hashtags found. Add 3-5 relevant hashtags for discoverability.")
    elif count < opt_min:
        score -= 10
        recommendations.append(f"Add {opt_min - count} more relevant hashtags (optimal: {opt_min}-{opt_max}).")
    elif count > platform_config["max"]:
        score -= 20
        issues.append(f"Too many hashtags ({count}). {platform.title()} optimal is {opt_min}-{opt_max}.")
    elif count > opt_max:
        score -= 5
        recommendations.append(f"Consider reducing to {opt_min}-{opt_max} hashtags for best results.")

    # Quality check
    if quality_dist["low"] > quality_dist["high"]:
        score -= 15
        issues.append("More broad/generic hashtags than niche ones. Replace generic tags with niche alternatives.")

    if type_dist["broad"] > 2:
        score -= 10
        recommendations.append("Replace broad hashtags (e.g., #marketing) with specific alternatives (e.g., #b2bmarketing).")

    # Duplicate check
    seen = set()
    dupes = []
    for t in tags:
        if t.lower() in seen:
            dupes.append(t)
        seen.add(t.lower())
    if dupes:
        score -= 10
        issues.append(f"Duplicate hashtags: {', '.join(dupes)}")

    # Mix recommendation
    if type_dist["niche"] == 0 and count > 0:
        recommendations.append("Add niche/industry-specific hashtags for targeted discovery.")
    if type_dist["branded"] == 0 and count > 2:
        recommendations.append("Consider adding a branded hashtag for community building.")

    if not recommendations and score >= 80:
        recommendations.append("Hashtag strategy looks solid.")

    score = max(0, min(100, score))

    return {
        "platform": platform,
        "platform_note": platform_config["note"],
        "hashtag_count": count,
        "optimal_range": f"{opt_min}-{opt_max}",
        "score": score,
        "grade": "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F",
        "quality_distribution": quality_dist,
        "type_distribution": type_dist,
        "hashtags": tag_analyses,
        "issues": issues,
        "recommendations": recommendations,
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 55, "  HASHTAG ANALYZER", "=" * 55]
    lines.append(f"\n  Platform: {result['platform'].title()} | Count: {result['hashtag_count']} (optimal: {result['optimal_range']})")
    lines.append(f"  Score: {result['score']}/100 ({result['grade']})")
    lines.append(f"  Note: {result['platform_note']}")

    if result["hashtags"]:
        lines.append(f"\n  Hashtag Analysis:")
        for h in result["hashtags"]:
            q_icon = {"high": "+", "medium": "~", "low": "-"}
            issues = f" -- {'; '.join(h['issues'])}" if h["issues"] else ""
            lines.append(f"    [{q_icon.get(h['quality'], '?')}] {h['hashtag']} ({h['type']}, {h['quality']}){issues}")

    if result["issues"]:
        lines.append(f"\n  Issues:")
        for i in result["issues"]:
            lines.append(f"    ! {i}")

    if result["recommendations"]:
        lines.append(f"\n  Recommendations:")
        for r in result["recommendations"]:
            lines.append(f"    > {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze hashtag strategy for social media posts.")
    parser.add_argument("text", nargs="?", help="Text containing hashtags")
    parser.add_argument("--file", "-f", help="File containing post text")
    parser.add_argument("--platform", "-p", default="linkedin", choices=list(PLATFORM_LIMITS.keys()))
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    if args.file:
        try:
            text = Path(args.file).read_text()
        except FileNotFoundError:
            print(f"Error: {args.file} not found", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        sys.exit(1)

    result = analyze_hashtags(text, args.platform)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
