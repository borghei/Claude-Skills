#!/usr/bin/env python3
"""Brand Architecture Analyzer - Evaluate and recommend brand architecture models.

Analyzes brand portfolio data to recommend optimal architecture (Branded House,
House of Brands, Endorsed, Hybrid) based on portfolio overlap, audience
similarity, and strategic objectives.

Usage:
    python brand_architecture_analyzer.py portfolio.json
    python brand_architecture_analyzer.py portfolio.json --json
    python brand_architecture_analyzer.py --demo
"""

import argparse
import json
import sys


ARCHITECTURE_MODELS = {
    "branded_house": {
        "name": "Branded House (Monolithic)",
        "description": "Single master brand across all products. Sub-brands are extensions.",
        "examples": "Google, Apple, Virgin, FedEx",
        "pros": [
            "Maximum brand equity transfer to new products",
            "Lower marketing costs (one brand to build)",
            "Clear brand recognition across portfolio",
            "Easier cross-selling between products",
        ],
        "cons": [
            "Brand damage affects entire portfolio",
            "Limited ability to target diverse segments",
            "New products constrained by master brand positioning",
            "Difficult to divest individual products",
        ],
        "best_when": [
            "Products share target audience",
            "Strong master brand equity exists",
            "Products reinforce the same brand promise",
            "Company wants to maximize brand efficiency",
        ],
    },
    "house_of_brands": {
        "name": "House of Brands (Pluralistic)",
        "description": "Independent brands with no visible parent connection.",
        "examples": "P&G (Tide, Pampers, Gillette), Unilever (Dove, Axe)",
        "pros": [
            "Each brand targets specific segments precisely",
            "Brand failures are contained",
            "Allows competing in same category with multiple brands",
            "Easy to acquire and divest brands",
        ],
        "cons": [
            "Highest marketing cost (build each brand separately)",
            "No equity transfer between brands",
            "Requires deep marketing expertise per brand",
            "Risk of internal brand cannibalization",
        ],
        "best_when": [
            "Products serve very different audiences",
            "Brands need distinct identities",
            "Acquisitions with strong existing brand equity",
            "Risk isolation is critical",
        ],
    },
    "endorsed": {
        "name": "Endorsed Brands",
        "description": "Sub-brands with visible parent brand endorsement.",
        "examples": "Marriott (Courtyard by Marriott), Nestle (KitKat by Nestle)",
        "pros": [
            "Sub-brands get credibility from parent",
            "Each brand has own identity within parent framework",
            "Balanced equity transfer",
            "Parent brand strengthened by successful sub-brands",
        ],
        "cons": [
            "Complex brand management requirements",
            "Parent brand partially exposed to sub-brand issues",
            "Endorsement relationship must be clear and consistent",
            "Higher cost than branded house, lower than house of brands",
        ],
        "best_when": [
            "Products need own identity but benefit from parent credibility",
            "Entering new categories adjacent to core",
            "Acquisitions that should maintain identity but gain parent trust",
        ],
    },
    "hybrid": {
        "name": "Hybrid Architecture",
        "description": "Mix of branded house, endorsed, and independent brands.",
        "examples": "Amazon (Prime, AWS, Whole Foods), Microsoft (Office, LinkedIn, GitHub)",
        "pros": [
            "Flexibility to optimize per product/market",
            "Can evolve architecture as portfolio changes",
            "Best of multiple approaches",
        ],
        "cons": [
            "Most complex to manage",
            "Risk of brand confusion if not well-governed",
            "Requires clear decision framework for new additions",
        ],
        "best_when": [
            "Portfolio spans diverse markets",
            "Mix of organic and acquired brands",
            "Different products at different lifecycle stages",
        ],
    },
}


def analyze_portfolio(data):
    """Analyze brand portfolio and recommend architecture."""
    brands = data.get("brands", data.get("products", []))
    parent_brand = data.get("parent_brand", data.get("master_brand", "Parent"))

    # Calculate overlap metrics
    all_audiences = set()
    audience_overlap = 0
    total_pairs = 0
    category_diversity = set()
    price_range = []

    for brand in brands:
        audiences = set(brand.get("audiences", []))
        all_audiences.update(audiences)
        category_diversity.add(brand.get("category", "unknown"))
        if "price_tier" in brand:
            price_range.append(brand["price_tier"])

    # Calculate pairwise audience overlap
    for i, a in enumerate(brands):
        for j, b in enumerate(brands):
            if i < j:
                a_audiences = set(a.get("audiences", []))
                b_audiences = set(b.get("audiences", []))
                if a_audiences and b_audiences:
                    overlap = len(a_audiences & b_audiences) / len(a_audiences | b_audiences)
                    audience_overlap += overlap
                    total_pairs += 1

    avg_overlap = (audience_overlap / total_pairs) if total_pairs > 0 else 0

    # Score each architecture model
    scores = {}

    # Branded House score
    bh_score = 50
    bh_score += avg_overlap * 30  # High overlap favors branded house
    bh_score -= len(category_diversity) * 5  # Many categories penalizes
    bh_score += 10 if len(brands) <= 5 else -5  # Smaller portfolio favors
    scores["branded_house"] = max(0, min(100, bh_score))

    # House of Brands score
    hob_score = 50
    hob_score -= avg_overlap * 30  # Low overlap favors house of brands
    hob_score += len(category_diversity) * 5
    hob_score += 10 if len(brands) > 5 else -5
    scores["house_of_brands"] = max(0, min(100, hob_score))

    # Endorsed score
    end_score = 60  # Generally safe middle ground
    end_score += 5 if 0.3 < avg_overlap < 0.7 else -10
    end_score += 5 if 2 <= len(category_diversity) <= 4 else -5
    scores["endorsed"] = max(0, min(100, end_score))

    # Hybrid score
    hyb_score = 40
    hyb_score += len(brands) * 2  # Larger portfolios favor hybrid
    hyb_score += len(category_diversity) * 3
    hyb_score += 10 if len(price_range) > 0 and len(set(price_range)) > 2 else 0
    scores["hybrid"] = max(0, min(100, hyb_score))

    # Determine recommendation
    recommended = max(scores, key=scores.get)

    # Brand-level recommendations
    brand_recommendations = []
    for brand in brands:
        brand_audiences = set(brand.get("audiences", []))
        # Check overlap with other brands
        overlaps = []
        for other in brands:
            if other.get("name") != brand.get("name"):
                other_audiences = set(other.get("audiences", []))
                if brand_audiences and other_audiences:
                    o = len(brand_audiences & other_audiences) / len(brand_audiences | other_audiences)
                    overlaps.append(o)
        avg_brand_overlap = sum(overlaps) / len(overlaps) if overlaps else 0

        if avg_brand_overlap > 0.6:
            rec = "branded_house"
        elif avg_brand_overlap < 0.2:
            rec = "independent"
        else:
            rec = "endorsed"

        brand_recommendations.append({
            "brand": brand.get("name", "unknown"),
            "category": brand.get("category", "unknown"),
            "audience_overlap": round(avg_brand_overlap, 2),
            "recommendation": rec,
        })

    return {
        "portfolio_metrics": {
            "total_brands": len(brands),
            "categories": list(category_diversity),
            "category_count": len(category_diversity),
            "average_audience_overlap": round(avg_overlap, 2),
            "total_unique_audiences": len(all_audiences),
        },
        "architecture_scores": {k: round(v, 1) for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)},
        "recommended_model": recommended,
        "model_details": ARCHITECTURE_MODELS[recommended],
        "brand_level_recommendations": brand_recommendations,
        "all_models": {k: ARCHITECTURE_MODELS[k] for k in ARCHITECTURE_MODELS},
    }


def get_demo_data():
    return {
        "parent_brand": "TechCorp",
        "brands": [
            {"name": "TechCorp Analytics", "category": "analytics", "audiences": ["data_teams", "product_managers", "executives"], "price_tier": "mid"},
            {"name": "TechCorp Cloud", "category": "infrastructure", "audiences": ["developers", "devops", "ctos"], "price_tier": "high"},
            {"name": "DataViz Pro", "category": "visualization", "audiences": ["data_teams", "analysts", "executives"], "price_tier": "mid"},
            {"name": "QuickDeploy", "category": "devtools", "audiences": ["developers", "devops"], "price_tier": "low"},
        ],
    }


def format_report(analysis):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 65)
    lines.append("BRAND ARCHITECTURE ANALYSIS")
    lines.append("=" * 65)

    pm = analysis["portfolio_metrics"]
    lines.append(f"Brands:              {pm['total_brands']}")
    lines.append(f"Categories:          {', '.join(pm['categories'])}")
    lines.append(f"Audience overlap:    {pm['average_audience_overlap']:.0%}")
    lines.append("")

    lines.append("--- ARCHITECTURE MODEL SCORES ---")
    for model, score in analysis["architecture_scores"].items():
        label = ARCHITECTURE_MODELS[model]["name"]
        bar = "#" * int(score / 5) + "." * (20 - int(score / 5))
        rec = " <-- RECOMMENDED" if model == analysis["recommended_model"] else ""
        lines.append(f"  {label:<35} [{bar}] {score:.0f}{rec}")
    lines.append("")

    rec_model = analysis["model_details"]
    lines.append(f"--- RECOMMENDED: {rec_model['name']} ---")
    lines.append(f"Description: {rec_model['description']}")
    lines.append(f"Examples: {rec_model['examples']}")
    lines.append("")
    lines.append("Pros:")
    for pro in rec_model["pros"]:
        lines.append(f"  + {pro}")
    lines.append("Cons:")
    for con in rec_model["cons"]:
        lines.append(f"  - {con}")
    lines.append("")

    lines.append("--- BRAND-LEVEL RECOMMENDATIONS ---")
    for br in analysis["brand_level_recommendations"]:
        lines.append(f"  {br['brand']}: {br['recommendation']} (overlap: {br['audience_overlap']:.0%})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze and recommend brand architecture models")
    parser.add_argument("input", nargs="?", help="JSON file with brand portfolio data")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = analyze_portfolio(data)

    if args.json_output:
        print(json.dumps(analysis, indent=2, default=str))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
