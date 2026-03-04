#!/usr/bin/env python3
"""Prioritization Scorer - Score and rank items using multiple prioritization frameworks.

Supports RICE, ICE, Opportunity Score, MoSCoW, and Weighted Decision Matrix.
Calculates scores, ranks items, and outputs sorted results with explanations.

Usage:
    python prioritization_scorer.py --input items.json --framework rice
    python prioritization_scorer.py --demo --framework ice
    python prioritization_scorer.py --demo --framework opportunity
    python prioritization_scorer.py --demo --framework moscow
    python prioritization_scorer.py --demo --framework weighted
    python prioritization_scorer.py --demo --framework rice --format json

Input JSON formats vary by framework. Use --demo to see examples.

Standard library only. No external dependencies.
"""

import argparse
import json
import sys
import textwrap


# ============================================================
# Framework Implementations
# ============================================================

def score_rice(items: list[dict]) -> list[dict]:
    """Score items using RICE: (Reach * Impact * Confidence) / Effort."""
    results = []
    for item in items:
        name = item.get("name", "Untitled")
        reach = item.get("reach", 0)
        impact = item.get("impact", 0)
        confidence = item.get("confidence", 0)
        effort = item.get("effort", 1)

        if effort <= 0:
            effort = 1  # Avoid division by zero

        # Confidence should be 0-1 range; accept 0-100 and convert
        if confidence > 1:
            confidence = confidence / 100.0

        score = (reach * impact * confidence) / effort

        results.append({
            "name": name,
            "score": round(score, 2),
            "details": {
                "reach": reach,
                "impact": impact,
                "confidence": confidence,
                "effort": effort,
            },
            "formula": f"({reach} * {impact} * {confidence:.2f}) / {effort} = {score:.2f}",
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def score_ice(items: list[dict]) -> list[dict]:
    """Score items using ICE: Impact * Confidence * Ease."""
    results = []
    for item in items:
        name = item.get("name", "Untitled")
        impact = item.get("impact", 0)
        confidence = item.get("confidence", 0)
        ease = item.get("ease", 0)

        score = impact * confidence * ease

        results.append({
            "name": name,
            "score": round(score, 2),
            "details": {
                "impact": impact,
                "confidence": confidence,
                "ease": ease,
            },
            "formula": f"{impact} * {confidence} * {ease} = {score:.2f}",
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def score_opportunity(items: list[dict]) -> list[dict]:
    """Score items using Opportunity Score: Importance * (1 - Satisfaction)."""
    results = []
    for item in items:
        name = item.get("name", "Untitled")
        importance = item.get("importance", 0)
        satisfaction = item.get("satisfaction", 0)

        # Clamp satisfaction to 0-1 range
        if satisfaction > 1:
            satisfaction = satisfaction / 10.0  # Accept 0-10 scale
        satisfaction = max(0, min(1, satisfaction))

        score = importance * (1 - satisfaction)

        results.append({
            "name": name,
            "score": round(score, 2),
            "details": {
                "importance": importance,
                "satisfaction": satisfaction,
                "gap": round(1 - satisfaction, 2),
            },
            "formula": f"{importance} * (1 - {satisfaction:.2f}) = {score:.2f}",
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def score_moscow(items: list[dict]) -> list[dict]:
    """Categorize and sort items using MoSCoW."""
    category_order = {"must": 0, "should": 1, "could": 2, "wont": 3}
    category_labels = {"must": "Must Have", "should": "Should Have", "could": "Could Have", "wont": "Won't Have"}

    results = []
    for item in items:
        name = item.get("name", "Untitled")
        category = item.get("category", "could").lower().replace("'", "").replace(" ", "")

        # Normalize category names
        if category.startswith("must"):
            category = "must"
        elif category.startswith("should"):
            category = "should"
        elif category.startswith("could"):
            category = "could"
        else:
            category = "wont"

        effort = item.get("effort", None)
        order = category_order.get(category, 3)

        results.append({
            "name": name,
            "category": category_labels.get(category, category),
            "sort_order": order,
            "effort": effort,
            "details": {
                "category": category,
                "effort": effort,
            },
        })

    results.sort(key=lambda x: (x["sort_order"], -(x["effort"] or 0)))
    return results


def score_weighted(items: list[dict], criteria: list[dict] | None = None) -> list[dict]:
    """Score items using Weighted Decision Matrix.

    Each item must have a 'scores' dict mapping criterion name to score (1-10).
    Criteria list provides name and weight for each criterion.
    """
    if not criteria:
        criteria = [
            {"name": "customer_impact", "weight": 0.3},
            {"name": "revenue_potential", "weight": 0.25},
            {"name": "feasibility", "weight": 0.25},
            {"name": "strategic_alignment", "weight": 0.2},
        ]

    # Normalize weights
    total_weight = sum(c["weight"] for c in criteria)
    if total_weight > 0:
        for c in criteria:
            c["weight"] = c["weight"] / total_weight

    results = []
    for item in items:
        name = item.get("name", "Untitled")
        scores = item.get("scores", {})

        weighted_total = 0
        score_breakdown = {}
        for c in criteria:
            cname = c["name"]
            raw_score = scores.get(cname, 0)
            weighted_score = raw_score * c["weight"]
            weighted_total += weighted_score
            score_breakdown[cname] = {
                "raw": raw_score,
                "weight": round(c["weight"], 2),
                "weighted": round(weighted_score, 2),
            }

        results.append({
            "name": name,
            "score": round(weighted_total, 2),
            "details": score_breakdown,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


# ============================================================
# Demo Data
# ============================================================

DEMO_DATA = {
    "rice": {
        "items": [
            {"name": "Advanced search", "reach": 5000, "impact": 2, "confidence": 80, "effort": 3},
            {"name": "Mobile app", "reach": 8000, "impact": 3, "confidence": 50, "effort": 8},
            {"name": "SSO integration", "reach": 1200, "impact": 2, "confidence": 90, "effort": 2},
            {"name": "Dashboard redesign", "reach": 6000, "impact": 1, "confidence": 70, "effort": 4},
            {"name": "API rate limiting", "reach": 300, "impact": 3, "confidence": 95, "effort": 1},
        ],
    },
    "ice": {
        "items": [
            {"name": "Advanced search", "impact": 8, "confidence": 7, "ease": 5},
            {"name": "Mobile app", "impact": 9, "confidence": 5, "ease": 3},
            {"name": "SSO integration", "impact": 6, "confidence": 9, "ease": 7},
            {"name": "Dashboard redesign", "impact": 5, "confidence": 6, "ease": 6},
            {"name": "API rate limiting", "impact": 7, "confidence": 9, "ease": 8},
        ],
    },
    "opportunity": {
        "items": [
            {"name": "Finding products quickly", "importance": 9, "satisfaction": 0.3},
            {"name": "Comparing prices", "importance": 7, "satisfaction": 0.8},
            {"name": "Tracking order status", "importance": 8, "satisfaction": 0.6},
            {"name": "Managing returns", "importance": 6, "satisfaction": 0.4},
            {"name": "Saving favorites", "importance": 5, "satisfaction": 0.7},
        ],
    },
    "moscow": {
        "items": [
            {"name": "User authentication", "category": "must", "effort": 3},
            {"name": "Data export", "category": "should", "effort": 2},
            {"name": "Dark mode", "category": "could", "effort": 1},
            {"name": "Payment processing", "category": "must", "effort": 5},
            {"name": "Social login", "category": "could", "effort": 2},
            {"name": "Blockchain integration", "category": "wont", "effort": 8},
            {"name": "Search functionality", "category": "must", "effort": 4},
            {"name": "Email notifications", "category": "should", "effort": 2},
        ],
    },
    "weighted": {
        "items": [
            {
                "name": "Advanced search",
                "scores": {"customer_impact": 9, "revenue_potential": 7, "feasibility": 6, "strategic_alignment": 8},
            },
            {
                "name": "Mobile app",
                "scores": {"customer_impact": 8, "revenue_potential": 9, "feasibility": 4, "strategic_alignment": 7},
            },
            {
                "name": "SSO integration",
                "scores": {"customer_impact": 5, "revenue_potential": 8, "feasibility": 8, "strategic_alignment": 6},
            },
            {
                "name": "Dashboard redesign",
                "scores": {"customer_impact": 7, "revenue_potential": 4, "feasibility": 7, "strategic_alignment": 5},
            },
        ],
        "criteria": [
            {"name": "customer_impact", "weight": 0.3},
            {"name": "revenue_potential", "weight": 0.25},
            {"name": "feasibility", "weight": 0.25},
            {"name": "strategic_alignment", "weight": 0.2},
        ],
    },
}


# ============================================================
# Formatting
# ============================================================

def format_text_report(results: list[dict], framework: str) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"PRIORITIZATION REPORT -- {framework.upper()}")
    lines.append("=" * 60)
    lines.append("")

    if framework == "moscow":
        current_category = None
        for i, r in enumerate(results, 1):
            if r["category"] != current_category:
                current_category = r["category"]
                lines.append(f"  [{current_category}]")
            effort_str = f"  (effort: {r['effort']})" if r.get("effort") is not None else ""
            lines.append(f"    {i}. {r['name']}{effort_str}")
        lines.append("")

        # Summary
        categories = {}
        total_effort = 0
        for r in results:
            cat = r["category"]
            categories[cat] = categories.get(cat, 0) + 1
            if r.get("effort") is not None:
                total_effort += r["effort"]

        lines.append("  Summary:")
        for cat, count in categories.items():
            lines.append(f"    {cat}: {count} items")
        lines.append(f"    Total effort: {total_effort}")

        must_effort = sum(r.get("effort", 0) or 0 for r in results if r.get("category") == "Must Have")
        if total_effort > 0:
            must_pct = (must_effort / total_effort) * 100
            lines.append(f"    Must-Have effort: {must_pct:.0f}% of total", )
            if must_pct > 60:
                lines.append("    [WARN] Must-Haves exceed 60% of effort. Consider reclassifying.")
    else:
        for i, r in enumerate(results, 1):
            lines.append(f"  {i}. {r['name']}")
            lines.append(f"     Score: {r['score']}")
            if "formula" in r:
                lines.append(f"     Formula: {r['formula']}")
            if "details" in r and framework == "weighted":
                for crit, vals in r["details"].items():
                    lines.append(f"       {crit}: {vals['raw']} x {vals['weight']} = {vals['weighted']}")
            lines.append("")

    lines.append("=" * 60)
    lines.append(f"Items ranked: {len(results)}")
    lines.append(f"Framework: {framework.upper()}")
    lines.append("=" * 60)

    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================

SUPPORTED_FRAMEWORKS = ["rice", "ice", "opportunity", "moscow", "weighted"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Score and rank items using prioritization frameworks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Supported frameworks:
              rice         (Reach * Impact * Confidence) / Effort
              ice          Impact * Confidence * Ease
              opportunity  Importance * (1 - Satisfaction)
              moscow       Must/Should/Could/Won't categorization
              weighted     Weighted Decision Matrix with custom criteria

            Examples:
              python prioritization_scorer.py --demo --framework rice
              python prioritization_scorer.py --demo --framework opportunity --format json
              python prioritization_scorer.py --input items.json --framework ice
        """),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--input",
        help="Path to JSON file containing items to score",
    )
    group.add_argument(
        "--demo",
        action="store_true",
        help="Run scoring on built-in demo data for the selected framework",
    )
    parser.add_argument(
        "--framework",
        required=True,
        choices=SUPPORTED_FRAMEWORKS,
        help="Prioritization framework to use",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format: text (default) or json",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Main entry point."""
    args = parse_args(argv)

    if args.demo:
        data = DEMO_DATA.get(args.framework, {})
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.input}: {e}", file=sys.stderr)
            sys.exit(1)

    items = data.get("items", [])
    if not items:
        print("Error: No items found in input data.", file=sys.stderr)
        sys.exit(1)

    # Route to framework
    if args.framework == "rice":
        results = score_rice(items)
    elif args.framework == "ice":
        results = score_ice(items)
    elif args.framework == "opportunity":
        results = score_opportunity(items)
    elif args.framework == "moscow":
        results = score_moscow(items)
    elif args.framework == "weighted":
        criteria = data.get("criteria", None)
        results = score_weighted(items, criteria)
    else:
        print(f"Error: Unknown framework: {args.framework}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text_report(results, args.framework))


if __name__ == "__main__":
    main()
