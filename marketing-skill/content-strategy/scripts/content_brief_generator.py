#!/usr/bin/env python3
"""
Content Brief Generator

Generates structured content briefs from keyword and topic inputs.
Includes target audience, search intent classification, recommended
structure, word count guidance, and internal linking suggestions.

Usage:
    python content_brief_generator.py --keyword "cloud cost optimization"
    python content_brief_generator.py --keyword "SEO audit checklist" --audience "marketing managers" --json
    python content_brief_generator.py --keyword "best CRM for startups" --funnel consideration
"""

import argparse
import json
import re
import sys


INTENT_PATTERNS = {
    "informational": r'\b(what is|how to|guide|tutorial|explain|definition|overview|learn)\b',
    "commercial": r'\b(best|top|review|comparison|vs|alternative|software|tool|platform)\b',
    "transactional": r'\b(buy|price|pricing|discount|free trial|download|sign up)\b',
    "navigational": r'\b(login|docs|documentation|support|contact)\b',
}

CONTENT_STRUCTURES = {
    "informational": {
        "format": "Comprehensive Guide",
        "word_count": "1,500-2,500",
        "sections": [
            "Definition and overview",
            "Why it matters",
            "Key components or steps",
            "Best practices",
            "Common mistakes",
            "Tools and resources",
            "FAQ",
        ],
    },
    "commercial": {
        "format": "Comparison / Buyer's Guide",
        "word_count": "2,000-3,000",
        "sections": [
            "Overview of the category",
            "Key evaluation criteria",
            "Detailed comparison (table format)",
            "Pros and cons of each option",
            "Best for specific use cases",
            "Pricing comparison",
            "Recommendation and verdict",
        ],
    },
    "transactional": {
        "format": "Product-Focused Landing Content",
        "word_count": "800-1,500",
        "sections": [
            "Problem statement",
            "Solution overview",
            "Key features and benefits",
            "Social proof (testimonials, case studies)",
            "Pricing and plans",
            "Getting started steps",
            "FAQ",
        ],
    },
    "navigational": {
        "format": "Resource Page",
        "word_count": "500-1,000",
        "sections": [
            "Direct answer or resource",
            "Quick navigation links",
            "Related resources",
        ],
    },
}

FUNNEL_GUIDANCE = {
    "awareness": {
        "reader_mindset": "I have a problem or question but don't know solutions yet",
        "content_goal": "Educate and attract — establish your expertise",
        "cta": "Newsletter signup, related content, or resource download",
        "tone": "Educational, helpful, non-promotional",
    },
    "consideration": {
        "reader_mindset": "I know my options and I'm evaluating them",
        "content_goal": "Build trust and differentiate your solution",
        "cta": "Demo request, free trial, or case study download",
        "tone": "Authoritative, balanced, evidence-based",
    },
    "decision": {
        "reader_mindset": "I'm ready to choose — convince me this is the right one",
        "content_goal": "Remove objections and drive conversion",
        "cta": "Sign up, purchase, or contact sales",
        "tone": "Confident, specific, proof-heavy",
    },
}


def classify_intent(keyword):
    """Classify search intent."""
    kw = keyword.lower()
    scores = {}
    for intent, pattern in INTENT_PATTERNS.items():
        scores[intent] = len(re.findall(pattern, kw))
    if max(scores.values()) == 0:
        return "informational"
    return max(scores, key=scores.get)


def estimate_word_count(intent, funnel):
    """Estimate target word count."""
    base = CONTENT_STRUCTURES[intent]["word_count"]
    if funnel == "awareness":
        return base  # Standard
    elif funnel == "consideration":
        return f"{base} (lean toward upper range for depth)"
    else:
        return "800-1,500 (concise, action-oriented)"


def generate_brief(keyword, audience=None, funnel=None):
    """Generate a complete content brief."""
    intent = classify_intent(keyword)
    if funnel is None:
        funnel_map = {
            "informational": "awareness",
            "commercial": "consideration",
            "transactional": "decision",
            "navigational": "awareness",
        }
        funnel = funnel_map[intent]

    structure = CONTENT_STRUCTURES[intent]
    funnel_guide = FUNNEL_GUIDANCE.get(funnel, FUNNEL_GUIDANCE["awareness"])

    brief = {
        "keyword": keyword,
        "intent": intent,
        "funnel_stage": funnel,
        "target": {
            "primary_keyword": keyword,
            "secondary_keywords": [
                f"{keyword} guide",
                f"{keyword} examples",
                f"how to {keyword}",
                f"best {keyword}",
                f"{keyword} tips",
            ],
            "search_intent": intent,
        },
        "audience": {
            "profile": audience or "[Define: role, seniority, industry]",
            "reader_mindset": funnel_guide["reader_mindset"],
            "awareness_level": funnel.capitalize(),
        },
        "content_spec": {
            "format": structure["format"],
            "target_word_count": estimate_word_count(intent, funnel),
            "tone": funnel_guide["tone"],
            "cta": funnel_guide["cta"],
            "content_goal": funnel_guide["content_goal"],
        },
        "structure": {
            "h1": f"[Working Title] — include '{keyword}'",
            "sections": structure["sections"],
        },
        "requirements": {
            "internal_links": "3-5 links to related content",
            "external_links": "2-3 links to authoritative sources",
            "images": "1 per 500 words minimum",
            "schema_markup": "Article schema at minimum; FAQPage if FAQ section included",
            "meta_title": f"Under 60 chars, includes '{keyword}'",
            "meta_description": "140-160 chars with keyword and clear value proposition",
        },
        "seo_checklist": [
            f"Primary keyword in H1, first 100 words, and 2+ H2s",
            "Keyword density 0.5-2.5%",
            "All images have descriptive alt text",
            "URL slug is short, keyword-first, no stop words",
            "Heading hierarchy: H1 > H2 > H3 (no skips)",
        ],
        "competitive_research": {
            "instruction": f"Analyze top 5 ranking pages for '{keyword}'",
            "what_to_record": [
                "Content format and angle",
                "Word count and depth",
                "What they cover well",
                "What they miss (your gap to fill)",
            ],
        },
    }

    return brief


def main():
    parser = argparse.ArgumentParser(description="Generate content briefs")
    parser.add_argument("--keyword", required=True, help="Target keyword")
    parser.add_argument("--audience", help="Target audience description")
    parser.add_argument("--funnel", choices=["awareness", "consideration", "decision"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    brief = generate_brief(args.keyword, args.audience, args.funnel)

    if args.json:
        print(json.dumps(brief, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  CONTENT BRIEF: {args.keyword}")
        print(f"{'='*60}")
        print(f"  Intent: {brief['intent']} | Funnel: {brief['funnel_stage']}")
        print(f"  Format: {brief['content_spec']['format']}")
        print(f"  Word Count: {brief['content_spec']['target_word_count']}")
        print(f"  Tone: {brief['content_spec']['tone']}")
        print(f"  CTA: {brief['content_spec']['cta']}")

        print(f"\n  Audience:")
        print(f"    Profile: {brief['audience']['profile']}")
        print(f"    Mindset: {brief['audience']['reader_mindset']}")

        print(f"\n  Recommended Structure:")
        print(f"    H1: {brief['structure']['h1']}")
        for i, section in enumerate(brief["structure"]["sections"], 1):
            print(f"    H2 {i}: {section}")

        print(f"\n  SEO Checklist:")
        for item in brief["seo_checklist"]:
            print(f"    [ ] {item}")

        print(f"\n  Secondary Keywords:")
        for kw in brief["target"]["secondary_keywords"]:
            print(f"    - {kw}")

        print()


if __name__ == "__main__":
    main()
