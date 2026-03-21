#!/usr/bin/env python3
"""
Audience Sizer

Estimates target audience size and recommends budget based on
platform, targeting criteria, and campaign objectives.

Usage:
    python audience_sizer.py --platform linkedin --targeting "CMOs at SaaS companies 50-500 employees"
    python audience_sizer.py --file targeting.json --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Rough audience sizing by platform (estimates for targeting guidance)
PLATFORM_AUDIENCES = {
    "linkedin": {
        "total_users": 1_000_000_000,
        "monthly_active": 310_000_000,
        "avg_cpc": 8.0,
        "min_audience": 20_000,
        "ideal_audience_conversion": (50_000, 500_000),
        "ideal_audience_awareness": (100_000, 1_000_000),
    },
    "meta": {
        "total_users": 3_000_000_000,
        "monthly_active": 2_100_000_000,
        "avg_cpc": 1.5,
        "min_audience": 10_000,
        "ideal_audience_conversion": (100_000, 2_000_000),
        "ideal_audience_awareness": (500_000, 10_000_000),
    },
    "google_search": {
        "total_users": 4_300_000_000,
        "monthly_active": 4_300_000_000,
        "avg_cpc": 3.5,
        "min_audience": 0,
        "ideal_audience_conversion": (1_000, 50_000),
        "ideal_audience_awareness": (10_000, 500_000),
    },
    "tiktok": {
        "total_users": 1_500_000_000,
        "monthly_active": 1_200_000_000,
        "avg_cpc": 0.8,
        "min_audience": 10_000,
        "ideal_audience_conversion": (100_000, 5_000_000),
        "ideal_audience_awareness": (500_000, 20_000_000),
    },
}

# LinkedIn audience estimates by criteria
LINKEDIN_SEGMENTS = {
    "c_suite": 15_000_000,
    "vp_director": 45_000_000,
    "manager": 80_000_000,
    "individual_contributor": 170_000_000,
    "saas": 25_000_000,
    "fintech": 5_000_000,
    "healthcare": 30_000_000,
    "enterprise_1000_plus": 40_000_000,
    "mid_market_200_1000": 60_000_000,
    "smb_50_200": 80_000_000,
    "startup_under_50": 100_000_000,
    "us_only": 0.25,
    "eu_only": 0.22,
    "uk_only": 0.08,
}

SENIORITY_KEYWORDS = {
    "c-suite": "c_suite", "ceo": "c_suite", "cto": "c_suite", "cmo": "c_suite", "cfo": "c_suite",
    "vp": "vp_director", "director": "vp_director", "head of": "vp_director",
    "manager": "manager",
}

INDUSTRY_KEYWORDS = {
    "saas": "saas", "software": "saas", "fintech": "fintech", "finance": "fintech",
    "healthcare": "healthcare", "health": "healthcare",
}

SIZE_KEYWORDS = {
    "enterprise": "enterprise_1000_plus", "large": "enterprise_1000_plus",
    "mid-market": "mid_market_200_1000", "midmarket": "mid_market_200_1000",
    "smb": "smb_50_200", "small": "smb_50_200",
    "startup": "startup_under_50",
}

GEO_KEYWORDS = {
    "us": "us_only", "united states": "us_only", "america": "us_only",
    "eu": "eu_only", "europe": "eu_only",
    "uk": "uk_only", "united kingdom": "uk_only",
}


def estimate_audience(platform: str, targeting: str) -> dict:
    platform_data = PLATFORM_AUDIENCES.get(platform, PLATFORM_AUDIENCES["linkedin"])
    lower = targeting.lower()

    # Parse targeting description
    detected = {"seniority": [], "industry": [], "size": [], "geo": []}

    for kw, seg in SENIORITY_KEYWORDS.items():
        if kw in lower:
            detected["seniority"].append(seg)
    for kw, seg in INDUSTRY_KEYWORDS.items():
        if kw in lower:
            detected["industry"].append(seg)
    for kw, seg in SIZE_KEYWORDS.items():
        if kw in lower:
            detected["size"].append(seg)
    for kw, seg in GEO_KEYWORDS.items():
        if kw in lower:
            detected["geo"].append(seg)

    # Estimate size (rough approximation)
    if platform == "linkedin":
        base = platform_data["monthly_active"]
        # Apply filters
        if detected["seniority"]:
            seg = detected["seniority"][0]
            base = min(base, LINKEDIN_SEGMENTS.get(seg, base))
        if detected["industry"]:
            seg = detected["industry"][0]
            base = min(base, LINKEDIN_SEGMENTS.get(seg, base))
        if detected["size"]:
            seg = detected["size"][0]
            size_val = LINKEDIN_SEGMENTS.get(seg, base)
            base = min(base, size_val)
        if detected["geo"]:
            seg = detected["geo"][0]
            geo_pct = LINKEDIN_SEGMENTS.get(seg, 1)
            if isinstance(geo_pct, float):
                base = int(base * geo_pct)

        # Cross-filter reduction (multiple criteria narrow further)
        filters_applied = sum(1 for v in detected.values() if v)
        if filters_applied >= 3:
            base = int(base * 0.15)
        elif filters_applied == 2:
            base = int(base * 0.3)

        estimated_size = base
    else:
        # Generic estimation
        base = platform_data["monthly_active"]
        filters = sum(1 for v in detected.values() if v)
        reduction = max(0.001, 0.1 ** max(filters - 1, 0) * 0.01)
        estimated_size = int(base * reduction)

    # Budget recommendations
    avg_cpc = platform_data["avg_cpc"]
    min_daily = round(avg_cpc * 20, 2)  # 20 clicks/day minimum for learning
    recommended_daily = round(avg_cpc * 50, 2)  # 50 clicks/day for optimization
    monthly_min = round(min_daily * 30, 2)
    monthly_recommended = round(recommended_daily * 30, 2)

    # Audience size assessment
    ideal_conv = platform_data["ideal_audience_conversion"]
    ideal_aware = platform_data["ideal_audience_awareness"]

    if estimated_size < platform_data["min_audience"]:
        size_assessment = "too_narrow"
    elif estimated_size < ideal_conv[0]:
        size_assessment = "narrow"
    elif estimated_size <= ideal_conv[1]:
        size_assessment = "good_for_conversion"
    elif estimated_size <= ideal_aware[1]:
        size_assessment = "good_for_awareness"
    else:
        size_assessment = "broad"

    recs = []
    if size_assessment == "too_narrow":
        recs.append(f"Audience too small for {platform}. Minimum: {platform_data['min_audience']:,}. Broaden targeting.")
    elif size_assessment == "narrow":
        recs.append("Audience is narrow. Good for highly targeted conversion campaigns.")
    elif size_assessment == "broad":
        recs.append("Audience is very broad. Add targeting layers to improve relevance.")

    recs.append(f"Minimum budget: ${monthly_min:,.0f}/month ({min_daily:.0f}/day) for basic learning.")
    recs.append(f"Recommended: ${monthly_recommended:,.0f}/month ({recommended_daily:.0f}/day) for optimization.")

    return {
        "platform": platform,
        "targeting_description": targeting,
        "detected_criteria": {k: v for k, v in detected.items() if v},
        "estimated_audience_size": estimated_size,
        "size_assessment": size_assessment,
        "budget": {
            "avg_cpc": avg_cpc,
            "min_daily": min_daily,
            "recommended_daily": recommended_daily,
            "min_monthly": monthly_min,
            "recommended_monthly": monthly_recommended,
        },
        "recommendations": recs,
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 55, "  AUDIENCE SIZER", "=" * 55]
    lines.append(f"\n  Platform: {result['platform'].replace('_', ' ').title()}")
    lines.append(f"  Targeting: {result['targeting_description']}")
    lines.append(f"  Detected: {json.dumps(result['detected_criteria'])}")
    lines.append(f"\n  Estimated Audience: {result['estimated_audience_size']:,}")
    lines.append(f"  Assessment: {result['size_assessment'].replace('_', ' ').title()}")

    b = result["budget"]
    lines.append(f"\n  Budget Estimates (avg CPC: ${b['avg_cpc']}):")
    lines.append(f"    Minimum: ${b['min_daily']}/day (${b['min_monthly']:,.0f}/month)")
    lines.append(f"    Recommended: ${b['recommended_daily']}/day (${b['recommended_monthly']:,.0f}/month)")

    lines.append(f"\n  Recommendations:")
    for r in result["recommendations"]:
        lines.append(f"    > {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Estimate audience size and budget for paid ads.")
    parser.add_argument("--platform", "-p", default="linkedin", choices=list(PLATFORM_AUDIENCES.keys()))
    parser.add_argument("--targeting", "-t", help="Targeting description")
    parser.add_argument("--file", "-f", help="JSON file with targeting config")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    if args.file:
        try:
            data = json.loads(Path(args.file).read_text())
            result = estimate_audience(data.get("platform", "linkedin"), data.get("targeting", ""))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.targeting:
        result = estimate_audience(args.platform, args.targeting)
    else:
        parser.print_help()
        sys.exit(1)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
