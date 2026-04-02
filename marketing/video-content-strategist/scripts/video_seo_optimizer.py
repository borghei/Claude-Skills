#!/usr/bin/env python3
"""
Video SEO Optimizer

Optimizes video titles, descriptions, and tags for platform-specific SEO.
Analyzes existing metadata and provides optimization recommendations with
improved alternatives.

Expected JSON input with video details: title, description, tags, platform, topic

Usage:
    python video_seo_optimizer.py video_data.json
    python video_seo_optimizer.py video_data.json --platform youtube
    python video_seo_optimizer.py video_data.json --format json
    python video_seo_optimizer.py video_data.json --batch
"""

import argparse
import json
import re
import sys
import string
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple


PLATFORM_LIMITS = {
    "youtube": {"title_max": 100, "title_optimal": 60, "desc_max": 5000, "tags_max_chars": 500, "tags_max_count": 30},
    "tiktok": {"title_max": 150, "title_optimal": 80, "desc_max": 2200, "tags_max_chars": 300, "tags_max_count": 10},
    "linkedin": {"title_max": 150, "title_optimal": 70, "desc_max": 3000, "tags_max_chars": 200, "tags_max_count": 5},
}

# Common power words that drive clicks
POWER_WORDS = {
    "curiosity": ["secret", "hidden", "revealed", "truth", "shocking", "surprising", "unexpected"],
    "urgency": ["now", "today", "immediately", "urgent", "before", "deadline", "limited"],
    "value": ["free", "ultimate", "complete", "proven", "guaranteed", "essential", "must-know"],
    "numbers": ["top", "best", "worst", "first", "last", "only"],
    "how_to": ["how", "why", "what", "when", "guide", "tutorial", "step", "tips", "tricks"],
}

# Stop words to identify keyword density
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "shall", "should", "may", "might", "must", "can",
    "could", "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
    "and", "but", "or", "nor", "not", "so", "yet", "both", "either", "neither", "each", "every",
    "this", "that", "these", "those", "i", "me", "my", "you", "your", "he", "she", "it", "we",
    "they", "them", "his", "her", "its", "our", "their",
}


def analyze_title(title: str, platform: str) -> Dict[str, Any]:
    """Analyze title for SEO effectiveness."""
    limits = PLATFORM_LIMITS.get(platform, PLATFORM_LIMITS["youtube"])
    issues = []
    score = 70  # Base score

    # Length check
    length = len(title)
    if length > limits["title_max"]:
        issues.append(f"Title exceeds maximum ({length}/{limits['title_max']} chars) - will be truncated")
        score -= 20
    elif length > limits["title_optimal"]:
        issues.append(f"Title may be truncated on mobile ({length}/{limits['title_optimal']} optimal chars)")
        score -= 5
    elif length < 20:
        issues.append("Title is very short - may lack keyword coverage")
        score -= 10

    # Power words
    title_lower = title.lower()
    found_power = []
    for category, words in POWER_WORDS.items():
        for word in words:
            if word in title_lower:
                found_power.append({"word": word, "category": category})
    if found_power:
        score += min(15, len(found_power) * 5)
    else:
        issues.append("No power words found - consider adding curiosity or value triggers")
        score -= 5

    # Number presence
    has_number = bool(re.search(r'\d', title))
    if has_number:
        score += 5
    else:
        issues.append("No numbers in title - titles with numbers get 36% more clicks")

    # ALL CAPS check
    words = title.split()
    caps_words = sum(1 for w in words if w.isupper() and len(w) > 1)
    if caps_words > len(words) * 0.5:
        issues.append("Excessive ALL CAPS - use sparingly for emphasis (1-2 words max)")
        score -= 10

    # Keyword front-loading
    # First 5 words should contain primary topic
    first_five = " ".join(words[:5]).lower()

    # Question format detection
    is_question = title.strip().endswith("?") or title_lower.startswith(("how", "why", "what", "when", "where"))

    return {
        "title": title,
        "length": length,
        "optimal_length": limits["title_optimal"],
        "max_length": limits["title_max"],
        "has_number": has_number,
        "is_question": is_question,
        "power_words": found_power,
        "caps_words": caps_words,
        "issues": issues,
        "score": max(0, min(100, score)),
    }


def analyze_description(description: str, platform: str, keywords: List[str] = None) -> Dict[str, Any]:
    """Analyze description for SEO effectiveness."""
    limits = PLATFORM_LIMITS.get(platform, PLATFORM_LIMITS["youtube"])
    issues = []
    score = 70

    length = len(description)
    word_count = len(description.split())

    if length > limits["desc_max"]:
        issues.append(f"Description exceeds limit ({length}/{limits['desc_max']} chars)")
        score -= 15
    elif word_count < 50:
        issues.append("Description is thin - aim for 150-300 words for SEO value")
        score -= 10
    elif word_count >= 150:
        score += 10

    # First 2-3 lines check (visible without expanding)
    lines = description.strip().split("\n")
    first_lines = " ".join(lines[:3])
    if len(first_lines) < 50:
        issues.append("First 2-3 lines are too short - this is the visible preview")
        score -= 5

    # Keyword density
    if keywords:
        desc_lower = description.lower()
        for kw in keywords:
            count = desc_lower.count(kw.lower())
            if count == 0:
                issues.append(f"Keyword '{kw}' not found in description")
                score -= 5
            elif count >= 5:
                issues.append(f"Keyword '{kw}' may be over-stuffed ({count} occurrences)")
                score -= 3

    # Has timestamps (YouTube)
    has_timestamps = bool(re.search(r'\d{1,2}:\d{2}', description))
    if platform == "youtube" and not has_timestamps:
        issues.append("No timestamps found - add chapter markers for longer videos")
    elif has_timestamps:
        score += 5

    # Has links/CTA
    has_links = "http" in description or "www." in description
    has_cta = any(cta in description.lower() for cta in ["subscribe", "follow", "sign up", "download", "click", "link"])

    if not has_cta:
        issues.append("No call-to-action found in description")

    return {
        "length": length,
        "word_count": word_count,
        "has_timestamps": has_timestamps,
        "has_links": has_links,
        "has_cta": has_cta,
        "issues": issues,
        "score": max(0, min(100, score)),
    }


def analyze_tags(tags: List[str], platform: str) -> Dict[str, Any]:
    """Analyze tags for SEO effectiveness."""
    limits = PLATFORM_LIMITS.get(platform, PLATFORM_LIMITS["youtube"])
    issues = []
    score = 70

    if not tags:
        return {"count": 0, "issues": ["No tags provided"], "score": 20}

    total_chars = sum(len(t) for t in tags)
    count = len(tags)

    if count > limits["tags_max_count"]:
        issues.append(f"Too many tags ({count}/{limits['tags_max_count']} max)")
        score -= 10
    elif count < 5:
        issues.append(f"Too few tags ({count}) - aim for 10-20 for YouTube")
        score -= 10

    if total_chars > limits["tags_max_chars"]:
        issues.append(f"Total tag characters exceed limit ({total_chars}/{limits['tags_max_chars']})")
        score -= 10

    # Tag length analysis
    short_tags = [t for t in tags if len(t.split()) == 1]
    long_tail = [t for t in tags if len(t.split()) >= 3]

    if not long_tail:
        issues.append("No long-tail tags - add 3+ word phrases for specific search queries")
        score -= 5
    else:
        score += 5

    # Duplicate check
    normalized = [t.lower().strip() for t in tags]
    dupes = [t for t, c in Counter(normalized).items() if c > 1]
    if dupes:
        issues.append(f"Duplicate tags found: {', '.join(dupes)}")
        score -= 5

    return {
        "count": count,
        "total_chars": total_chars,
        "max_chars": limits["tags_max_chars"],
        "short_tags": len(short_tags),
        "long_tail_tags": len(long_tail),
        "duplicates": dupes,
        "issues": issues,
        "score": max(0, min(100, score)),
    }


def optimize_video(video: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Run full optimization analysis on a video."""
    title = video.get("title", "")
    description = video.get("description", "")
    tags = video.get("tags", [])
    keywords = video.get("keywords", [])

    title_analysis = analyze_title(title, platform)
    desc_analysis = analyze_description(description, platform, keywords)
    tags_analysis = analyze_tags(tags, platform)

    # Overall score
    overall_score = (
        title_analysis["score"] * 0.40
        + desc_analysis["score"] * 0.35
        + tags_analysis["score"] * 0.25
    )

    # Aggregate recommendations
    all_issues = []
    all_issues.extend([{"area": "title", "issue": i} for i in title_analysis["issues"]])
    all_issues.extend([{"area": "description", "issue": i} for i in desc_analysis["issues"]])
    all_issues.extend([{"area": "tags", "issue": i} for i in tags_analysis["issues"]])

    return {
        "video_id": video.get("video_id", ""),
        "title": title,
        "platform": platform,
        "title_analysis": title_analysis,
        "description_analysis": desc_analysis,
        "tags_analysis": tags_analysis,
        "overall_score": round(overall_score, 1),
        "total_issues": len(all_issues),
        "issues": all_issues,
    }


def print_human(results: List[Dict[str, Any]]) -> None:
    """Print optimization results in human-readable format."""
    for result in results:
        print("=" * 70)
        print(f"  Video SEO Analysis - {result['platform'].upper()}")
        print("=" * 70)
        print(f"\n  Title: {result['title']}")
        print(f"  Overall SEO Score: {result['overall_score']}/100")

        # Title
        ta = result["title_analysis"]
        print(f"\n  --- Title Analysis (Score: {ta['score']}/100) ---")
        print(f"  Length: {ta['length']}/{ta['optimal_length']} optimal chars")
        print(f"  Has Number: {'Yes' if ta['has_number'] else 'No'}")
        print(f"  Question Format: {'Yes' if ta['is_question'] else 'No'}")
        if ta["power_words"]:
            pw = ", ".join(f"{p['word']} ({p['category']})" for p in ta["power_words"])
            print(f"  Power Words: {pw}")

        # Description
        da = result["description_analysis"]
        print(f"\n  --- Description Analysis (Score: {da['score']}/100) ---")
        print(f"  Word Count: {da['word_count']}")
        print(f"  Timestamps: {'Yes' if da['has_timestamps'] else 'No'}")
        print(f"  Links: {'Yes' if da['has_links'] else 'No'}")
        print(f"  CTA: {'Yes' if da['has_cta'] else 'No'}")

        # Tags
        tg = result["tags_analysis"]
        print(f"\n  --- Tags Analysis (Score: {tg['score']}/100) ---")
        print(f"  Tag Count: {tg['count']}")
        print(f"  Long-tail Tags: {tg.get('long_tail_tags', 0)}")

        # Issues
        if result["issues"]:
            print(f"\n  --- Issues ({result['total_issues']}) ---")
            for item in result["issues"]:
                print(f"  [{item['area']:>11}] {item['issue']}")

        print()


def main():
    parser = argparse.ArgumentParser(
        description="Optimize video titles, descriptions, and tags for platform SEO"
    )
    parser.add_argument("file", help="JSON file with video data")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument("--platform", choices=["youtube", "tiktok", "linkedin"],
                        default="youtube", help="Target platform (default: youtube)")
    parser.add_argument("--batch", action="store_true",
                        help="Process multiple videos (expects 'videos' array in JSON)")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.batch:
        videos = data.get("videos", [])
    else:
        videos = [data]

    if not videos:
        print("Error: No video data found", file=sys.stderr)
        sys.exit(1)

    results = [optimize_video(v, args.platform) for v in videos]

    if args.format == "json":
        print(json.dumps({"results": results} if len(results) > 1 else results[0], indent=2))
    else:
        print_human(results)


if __name__ == "__main__":
    main()
