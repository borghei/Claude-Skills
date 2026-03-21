#!/usr/bin/env python3
"""Context Completeness Checker - Audit marketing context document for gaps.

Checks a marketing context document for completeness across all required
sections, flags missing or thin sections, and scores overall readiness.

Usage:
    python context_completeness_checker.py context.md
    python context_completeness_checker.py context.json --json
"""

import argparse
import json
import re
import sys


REQUIRED_SECTIONS = {
    "product_overview": {
        "weight": 10,
        "required_fields": ["description", "category", "product_type", "business_model", "pricing"],
        "min_words": 50,
    },
    "target_audience": {
        "weight": 10,
        "required_fields": ["company_type", "decision_makers", "primary_use_case", "jobs_to_be_done"],
        "min_words": 75,
    },
    "buyer_personas": {
        "weight": 8,
        "required_fields": ["title", "role_in_purchase", "what_they_care_about", "language_they_use"],
        "min_words": 100,
    },
    "problems_pain_points": {
        "weight": 9,
        "required_fields": ["core_challenge", "why_current_solutions_fail", "cost_of_problem"],
        "min_words": 75,
    },
    "competitive_landscape": {
        "weight": 8,
        "required_fields": ["direct_competitors", "secondary_competitors"],
        "min_words": 75,
    },
    "differentiation": {
        "weight": 9,
        "required_fields": ["key_differentiators", "how_we_solve_differently", "why_customers_choose_us"],
        "min_words": 50,
    },
    "objections": {
        "weight": 7,
        "required_fields": ["objection", "response"],
        "min_words": 50,
    },
    "customer_language": {
        "weight": 8,
        "required_fields": ["how_they_describe_problem", "how_they_describe_solution"],
        "min_words": 50,
    },
    "brand_voice": {
        "weight": 7,
        "required_fields": ["tone", "communication_style", "personality"],
        "min_words": 40,
    },
    "proof_points": {
        "weight": 7,
        "required_fields": ["key_metrics", "testimonials"],
        "min_words": 40,
    },
    "content_seo_context": {
        "weight": 5,
        "required_fields": ["target_keywords"],
        "min_words": 30,
    },
    "goals": {
        "weight": 5,
        "required_fields": ["primary_goal", "key_conversion_action"],
        "min_words": 30,
    },
}

# Patterns to detect sections in markdown
SECTION_PATTERNS = {
    "product_overview": [r"product\s+overview", r"what\s+(it|we)\s+(is|do|are)"],
    "target_audience": [r"target\s+audience", r"ideal\s+customer", r"icp"],
    "buyer_personas": [r"persona", r"buyer\s+profile"],
    "problems_pain_points": [r"problems?", r"pain\s+points?", r"challenges?"],
    "competitive_landscape": [r"competitive?\s+landscape", r"competitors?"],
    "differentiation": [r"differenti", r"unique\s+(value|approach)"],
    "objections": [r"objections?", r"anti.?persona"],
    "customer_language": [r"customer\s+language", r"verbatim"],
    "brand_voice": [r"brand\s+voice", r"tone\s+(and|&)\s+voice"],
    "proof_points": [r"proof\s+points?", r"testimonial", r"social\s+proof"],
    "content_seo_context": [r"content\s+(&|and)\s+seo", r"keywords?"],
    "goals": [r"goals?", r"objectives?", r"kpis?"],
}


def check_markdown(filepath):
    """Check a markdown context document for completeness."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    sections_found = {}
    content_lower = content.lower()

    for section, patterns in SECTION_PATTERNS.items():
        found = False
        section_content = ""
        for pattern in patterns:
            match = re.search(pattern, content_lower)
            if match:
                found = True
                # Extract content after the heading until next heading
                pos = match.start()
                next_heading = re.search(r"\n#{1,3}\s", content[pos + 10:])
                if next_heading:
                    section_content = content[pos:pos + 10 + next_heading.start()]
                else:
                    section_content = content[pos:]
                break

        word_count = len(section_content.split()) if section_content else 0
        min_words = REQUIRED_SECTIONS[section]["min_words"]

        sections_found[section] = {
            "found": found,
            "word_count": word_count,
            "meets_minimum": word_count >= min_words,
            "min_words": min_words,
        }

    return _compile_results(sections_found)


def check_json(filepath):
    """Check a JSON context document for completeness."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections_found = {}
    data_lower = {k.lower().replace(" ", "_"): v for k, v in data.items()}

    for section, config in REQUIRED_SECTIONS.items():
        # Check if section key exists
        section_data = data_lower.get(section, data_lower.get(section.replace("_", ""), None))
        found = section_data is not None

        if found and isinstance(section_data, dict):
            word_count = sum(len(str(v).split()) for v in section_data.values())
        elif found and isinstance(section_data, str):
            word_count = len(section_data.split())
        elif found and isinstance(section_data, list):
            word_count = sum(len(str(item).split()) for item in section_data)
        else:
            word_count = 0

        min_words = config["min_words"]
        sections_found[section] = {
            "found": found,
            "word_count": word_count,
            "meets_minimum": word_count >= min_words,
            "min_words": min_words,
        }

    return _compile_results(sections_found)


def _compile_results(sections_found):
    """Compile analysis results from section findings."""
    total_weight = sum(REQUIRED_SECTIONS[s]["weight"] for s in REQUIRED_SECTIONS)
    earned_weight = 0
    missing = []
    thin = []
    complete = []

    for section, result in sections_found.items():
        weight = REQUIRED_SECTIONS[section]["weight"]
        if not result["found"]:
            missing.append({"section": section, "weight": weight})
        elif not result["meets_minimum"]:
            earned_weight += weight * 0.5
            thin.append({
                "section": section,
                "word_count": result["word_count"],
                "min_words": result["min_words"],
                "weight": weight,
            })
        else:
            earned_weight += weight
            complete.append({"section": section, "weight": weight})

    score = (earned_weight / max(total_weight, 1)) * 100

    # Readiness assessment
    if score >= 80 and not missing:
        readiness = "READY"
        message = "Context is comprehensive. Ready for marketing execution."
    elif score >= 60:
        readiness = "MOSTLY READY"
        message = "Core context exists. Fill gaps before major campaigns."
    elif score >= 40:
        readiness = "PARTIAL"
        message = "Significant gaps remain. Complete critical sections first."
    else:
        readiness = "NOT READY"
        message = "Major sections missing. Build context before marketing work."

    # Priority order for missing sections (by weight)
    priority_order = sorted(missing + thin, key=lambda x: x["weight"], reverse=True)

    return {
        "score": round(score, 1),
        "readiness": readiness,
        "message": message,
        "sections": sections_found,
        "complete": complete,
        "thin": thin,
        "missing": missing,
        "priority_to_fill": [p["section"] for p in priority_order],
        "stats": {
            "total_sections": len(REQUIRED_SECTIONS),
            "complete": len(complete),
            "thin": len(thin),
            "missing": len(missing),
        },
    }


def format_report(analysis):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("MARKETING CONTEXT COMPLETENESS CHECK")
    lines.append("=" * 60)
    lines.append(f"Score:       {analysis['score']:.0f}/100")
    lines.append(f"Readiness:   {analysis['readiness']}")
    lines.append(f"Assessment:  {analysis['message']}")
    lines.append(f"Sections:    {analysis['stats']['complete']}/{analysis['stats']['total_sections']} complete, "
                 f"{analysis['stats']['thin']} thin, {analysis['stats']['missing']} missing")
    lines.append("")

    # Section status
    lines.append("--- SECTION STATUS ---")
    for section, data in analysis["sections"].items():
        label = section.replace("_", " ").title()
        if not data["found"]:
            lines.append(f"  [MISSING]  {label}")
        elif not data["meets_minimum"]:
            lines.append(f"  [THIN]     {label} ({data['word_count']}/{data['min_words']} words)")
        else:
            lines.append(f"  [OK]       {label} ({data['word_count']} words)")
    lines.append("")

    # Priority
    if analysis["priority_to_fill"]:
        lines.append("--- FILL PRIORITY ---")
        for i, section in enumerate(analysis["priority_to_fill"], 1):
            lines.append(f"  {i}. {section.replace('_', ' ').title()}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit marketing context document for gaps")
    parser.add_argument("input", help="Markdown (.md) or JSON (.json) context file")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    args = parser.parse_args()

    try:
        if args.input.endswith(".json"):
            analysis = check_json(args.input)
        else:
            analysis = check_markdown(args.input)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))

    sys.exit(0 if analysis["readiness"] in ("READY", "MOSTLY READY") else 1)


if __name__ == "__main__":
    main()
