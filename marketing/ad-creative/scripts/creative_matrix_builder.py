#!/usr/bin/env python3
"""
Creative Matrix Builder

Generates a cross-platform creative testing matrix from a
creative brief, producing ad copy variations organized by
hook type and funnel stage.

Usage:
    python creative_matrix_builder.py brief.json
    python creative_matrix_builder.py brief.json --json
    python creative_matrix_builder.py --sample
"""

import argparse
import json
import sys
from pathlib import Path

HOOK_TYPES = ["benefit", "curiosity", "social_proof", "problem_agitation", "urgency"]
FUNNEL_STAGES = ["awareness", "consideration", "decision"]

PLATFORM_SPECS = {
    "google": {"headline": 30, "description": 90},
    "meta": {"headline": 40, "description": 125},
    "linkedin": {"headline": 70, "description": 150},
}

CTA_BY_STAGE = {
    "awareness": ["Learn More", "See How It Works", "Watch Demo"],
    "consideration": ["Start Free Trial", "Compare Plans", "Get Started"],
    "decision": ["Buy Now", "Start My Plan", "Claim Your Spot"],
}

SAMPLE = {
    "product": "ChurnGuard",
    "value_proposition": "Reduce SaaS churn by 30% with predictive analytics",
    "target_audience": "VP of Customer Success at B2B SaaS companies",
    "key_benefit": "Reduce churn 30%",
    "proof_point": "Used by 400+ SaaS teams including Stripe and Notion",
    "pain_point": "Losing customers without knowing why",
    "platforms": ["google", "meta", "linkedin"],
    "funnel_stages": ["consideration", "decision"],
}


def build_matrix(brief: dict) -> dict:
    product = brief.get("product", "[Product]")
    benefit = brief.get("key_benefit", "improve results")
    proof = brief.get("proof_point", "trusted by leading companies")
    pain = brief.get("pain_point", "current challenges")
    audience = brief.get("target_audience", "teams")
    platforms = brief.get("platforms", ["google", "meta"])
    stages = brief.get("funnel_stages", ["consideration"])

    matrix = []

    for stage in stages:
        ctas = CTA_BY_STAGE.get(stage, CTA_BY_STAGE["consideration"])

        for hook_type in HOOK_TYPES:
            # Generate copy per hook type
            if hook_type == "benefit":
                headline_base = f"{benefit}"
                body_base = f"{product} helps {audience.split()[-1]}s {benefit.lower()}. {proof}."
            elif hook_type == "curiosity":
                headline_base = f"Why Your Team Is Still {pain.split()[0]}ing"
                body_base = f"Most teams don't know why they {pain.lower()}. {product} shows you exactly what's happening."
            elif hook_type == "social_proof":
                headline_base = f"{proof.split('by')[-1].strip() if 'by' in proof else proof}"
                body_base = f"{proof}. See why they chose {product} to {benefit.lower()}."
            elif hook_type == "problem_agitation":
                headline_base = f"Still {pain}?"
                body_base = f"{pain.capitalize()} costs more than you think. {product}: {benefit.lower()} in weeks."
            elif hook_type == "urgency":
                headline_base = f"{benefit} — Start This Week"
                body_base = f"Every week without {product} means lost revenue. {proof}."
            else:
                continue

            for platform in platforms:
                specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["google"])
                h_max = specs["headline"]
                d_max = specs["description"]

                # Truncate to spec
                headline = headline_base[:h_max]
                body = body_base[:d_max]

                entry = {
                    "hook_type": hook_type,
                    "funnel_stage": stage,
                    "platform": platform,
                    "headline": headline,
                    "headline_chars": f"{len(headline)}/{h_max}",
                    "body": body,
                    "body_chars": f"{len(body)}/{d_max}",
                    "cta": ctas[0],
                    "within_limits": len(headline) <= h_max and len(body) <= d_max,
                }
                matrix.append(entry)

    # Summary
    total = len(matrix)
    by_platform = {}
    by_hook = {}
    for m in matrix:
        by_platform[m["platform"]] = by_platform.get(m["platform"], 0) + 1
        by_hook[m["hook_type"]] = by_hook.get(m["hook_type"], 0) + 1

    return {
        "brief": brief,
        "total_variants": total,
        "by_platform": by_platform,
        "by_hook_type": by_hook,
        "matrix": matrix,
        "testing_plan": [
            "Run each variant for 7-14 days minimum.",
            "Need 1,000+ impressions per variant for significance.",
            "Test one variable at a time per ad set.",
            "Promote winners, pause bottom 20% performers weekly.",
            "Document winning patterns for the creative playbook.",
        ],
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 75, "  CREATIVE MATRIX BUILDER", "=" * 75]
    b = result["brief"]
    lines.append(f"\n  Product: {b.get('product', '?')} | Audience: {b.get('target_audience', '?')}")
    lines.append(f"  Variants Generated: {result['total_variants']}")
    lines.append(f"  Platforms: {json.dumps(result['by_platform'])} | Hooks: {json.dumps(result['by_hook_type'])}")

    current_stage = ""
    for m in result["matrix"]:
        if m["funnel_stage"] != current_stage:
            current_stage = m["funnel_stage"]
            lines.append(f"\n  --- {current_stage.upper()} STAGE ---")

        lines.append(f"\n  [{m['hook_type']}] {m['platform'].upper()}")
        lines.append(f"    H: \"{m['headline']}\" [{m['headline_chars']}]")
        lines.append(f"    B: \"{m['body'][:80]}...\" [{m['body_chars']}]")
        lines.append(f"    CTA: {m['cta']}")

    lines.append(f"\n  Testing Plan:")
    for t in result["testing_plan"]:
        lines.append(f"    > {t}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Build cross-platform ad creative testing matrix.")
    parser.add_argument("file", nargs="?")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    if args.sample:
        brief = SAMPLE
    elif args.file:
        try:
            brief = json.loads(Path(args.file).read_text())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    result = build_matrix(brief)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
