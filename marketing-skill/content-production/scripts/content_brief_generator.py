#!/usr/bin/env python3
"""
Content Brief Generator for Production

Generates production-ready content briefs with keyword targets, audience
definition, recommended structure, competitive research prompts, and
SEO requirements. Designed for the content production pipeline.

Usage:
    python content_brief_generator.py --keyword "cloud cost optimization"
    python content_brief_generator.py --keyword "SEO audit" --audience "CTOs" --json
    python content_brief_generator.py --keyword "best CRM" --format comparison
"""

import argparse
import json
import re
import sys


def classify_intent(keyword):
    """Classify search intent."""
    kw = keyword.lower()
    if re.search(r'\b(what is|how to|guide|tutorial|explain|learn|overview)\b', kw):
        return "informational"
    if re.search(r'\b(best|top|review|vs|compare|alternative|tool|software)\b', kw):
        return "commercial"
    if re.search(r'\b(buy|price|pricing|discount|free trial|sign up|download)\b', kw):
        return "transactional"
    return "informational"


FORMAT_SPECS = {
    "guide": {
        "name": "Comprehensive Guide",
        "word_count": "1,800-2,500",
        "h2_count": "5-7",
        "sections": [
            "What is [topic] (definition)",
            "Why [topic] matters",
            "How to [topic] (step-by-step)",
            "Best practices",
            "Common mistakes to avoid",
            "Tools and resources",
            "FAQ",
        ],
    },
    "comparison": {
        "name": "Comparison / Buyer's Guide",
        "word_count": "2,000-3,000",
        "h2_count": "6-8",
        "sections": [
            "Overview of options",
            "Evaluation criteria",
            "Detailed comparison (table)",
            "Pros and cons per option",
            "Best for [use case 1]",
            "Best for [use case 2]",
            "Pricing comparison",
            "Our recommendation",
        ],
    },
    "listicle": {
        "name": "List Article",
        "word_count": "1,500-2,000",
        "h2_count": "7-12",
        "sections": [
            "Introduction (why this list matters)",
            "[Item 1] — description + use case",
            "[Item 2] — description + use case",
            "[Item N] — description + use case",
            "How to choose the right one",
            "FAQ",
        ],
    },
    "how_to": {
        "name": "How-To Tutorial",
        "word_count": "1,200-2,000",
        "h2_count": "5-8",
        "sections": [
            "What you need before starting",
            "Step 1: [action]",
            "Step 2: [action]",
            "Step N: [action]",
            "Common issues and fixes",
            "Next steps",
        ],
    },
}


def generate_brief(keyword, audience=None, content_format=None):
    """Generate a production-ready content brief."""
    intent = classify_intent(keyword)

    if content_format is None:
        format_map = {
            "informational": "guide",
            "commercial": "comparison",
            "transactional": "how_to",
        }
        content_format = format_map.get(intent, "guide")

    spec = FORMAT_SPECS.get(content_format, FORMAT_SPECS["guide"])

    return {
        "brief_type": "production",
        "keyword": keyword,
        "intent": intent,
        "audience": audience or "[Define target reader: role, seniority, industry]",
        "format": spec["name"],
        "target_word_count": spec["word_count"],
        "structure": {
            "h1": f"[Compelling title with '{keyword}' front-loaded, under 60 chars]",
            "target_h2_count": spec["h2_count"],
            "sections": spec["sections"],
        },
        "seo_requirements": {
            "primary_keyword": keyword,
            "secondary_keywords": [
                f"{keyword} guide",
                f"{keyword} best practices",
                f"how to {keyword}",
                f"{keyword} examples",
                f"{keyword} {str(2026)}",
            ],
            "keyword_in_h1": True,
            "keyword_in_first_100_words": True,
            "keyword_in_2_plus_h2s": True,
            "meta_title": f"Under 60 chars with '{keyword}'",
            "meta_description": "140-160 chars with keyword + value prop + hook",
            "url_slug": f"/{keyword.lower().replace(' ', '-')}",
            "internal_links": "3-5 to related content",
            "external_links": "2-3 to authoritative sources",
            "schema": "Article (minimum), FAQPage if FAQ included",
        },
        "quality_requirements": {
            "readability": "Flesch Reading Ease 60-70",
            "max_paragraph_length": "4 sentences",
            "images": "1 per 500 words",
            "active_voice": "80%+ of sentences",
            "no_ai_filler_words": True,
            "sources_required": "3-5 credible, citable sources",
        },
        "competitive_research": {
            "task": f"Analyze top 5 ranking pages for '{keyword}'",
            "record_per_competitor": [
                "URL, format, word count",
                "Key angle or unique perspective",
                "What they cover well",
                "What they miss (your opportunity)",
            ],
        },
        "production_timeline": {
            "brief_review": "Day 0",
            "research_and_outline": "Days 1-2",
            "first_draft": "Days 3-5",
            "editorial_review": "Days 6-7",
            "revisions": "Day 8",
            "seo_optimization": "Day 9",
            "final_review_and_staging": "Day 10",
            "publish": "Day 11",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Generate production content briefs")
    parser.add_argument("--keyword", required=True)
    parser.add_argument("--audience", help="Target audience")
    parser.add_argument("--format", choices=list(FORMAT_SPECS.keys()), help="Content format")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    brief = generate_brief(args.keyword, args.audience, args.format)

    if args.json:
        print(json.dumps(brief, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  CONTENT BRIEF: {args.keyword}")
        print(f"{'='*60}")
        print(f"  Format: {brief['format']} | Intent: {brief['intent']}")
        print(f"  Word count: {brief['target_word_count']}")
        print(f"  Audience: {brief['audience']}")

        print(f"\n  Structure ({brief['structure']['target_h2_count']} H2s):")
        print(f"  H1: {brief['structure']['h1']}")
        for i, s in enumerate(brief["structure"]["sections"], 1):
            print(f"  H2.{i}: {s}")

        print(f"\n  SEO Requirements:")
        print(f"  - Meta title: {brief['seo_requirements']['meta_title']}")
        print(f"  - URL: {brief['seo_requirements']['url_slug']}")
        print(f"  - Internal links: {brief['seo_requirements']['internal_links']}")
        print(f"  - Schema: {brief['seo_requirements']['schema']}")

        print(f"\n  Timeline:")
        for stage, day in brief["production_timeline"].items():
            print(f"  - {stage.replace('_', ' ').title()}: {day}")

        print()


if __name__ == "__main__":
    main()
