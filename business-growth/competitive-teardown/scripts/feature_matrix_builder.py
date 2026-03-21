#!/usr/bin/env python3
"""
Feature Matrix Builder

Build a feature comparison matrix from structured feature data. Calculates
per-category and overall coverage scores for each competitor.

Usage:
    python feature_matrix_builder.py features.json
    python feature_matrix_builder.py features.json --json
"""

import argparse
import json
import sys


COVERAGE_SCORES = {
    "full": 5,
    "partial": 3,
    "basic": 2,
    "planned": 1,
    "missing": 0,
}


def build_matrix(data: dict) -> dict:
    """Build feature comparison matrix."""
    products = data.get("products", [])
    categories = data.get("categories", [])

    if not products or not categories:
        return {"error": "Products and categories are required."}

    product_names = [p.get("name", f"Product {i+1}") for i, p in enumerate(products)]

    # Build matrix
    matrix_rows = []
    category_scores = {name: {} for name in product_names}
    overall_scores = {name: {"total": 0, "max": 0} for name in product_names}

    for cat in categories:
        cat_name = cat.get("name", "Unknown")
        features = cat.get("features", [])
        cat_rows = []

        for feat in features:
            feat_name = feat.get("name", "Unknown")
            row = {"feature": feat_name, "category": cat_name, "scores": {}, "notes": feat.get("notes", "")}

            for i, product in enumerate(products):
                name = product_names[i]
                product_features = product.get("features", {})
                cat_features = product_features.get(cat_name, {})
                coverage = cat_features.get(feat_name, "missing").lower()
                score = COVERAGE_SCORES.get(coverage, 0)

                row["scores"][name] = {
                    "coverage": coverage,
                    "score": score,
                }
                overall_scores[name]["total"] += score
                overall_scores[name]["max"] += 5

            cat_rows.append(row)
        matrix_rows.append({"category": cat_name, "features": cat_rows})

        # Calculate category scores
        for name in product_names:
            cat_total = sum(r["scores"][name]["score"] for r in cat_rows)
            cat_max = len(cat_rows) * 5
            pct = (cat_total / cat_max * 100) if cat_max > 0 else 0
            category_scores[name][cat_name] = {
                "score": cat_total,
                "max": cat_max,
                "percentage": round(pct, 1),
            }

    # Overall coverage
    overall_coverage = {}
    for name in product_names:
        total = overall_scores[name]["total"]
        max_score = overall_scores[name]["max"]
        pct = (total / max_score * 100) if max_score > 0 else 0
        overall_coverage[name] = {
            "total_score": total,
            "max_score": max_score,
            "coverage_pct": round(pct, 1),
        }

    # Differentiators (features where only one product has "full")
    differentiators = {name: [] for name in product_names}
    gaps = {name: [] for name in product_names}

    for cat_data in matrix_rows:
        for feat in cat_data["features"]:
            full_products = [n for n in product_names if feat["scores"][n]["coverage"] == "full"]
            missing_products = [n for n in product_names if feat["scores"][n]["coverage"] == "missing"]

            if len(full_products) == 1:
                differentiators[full_products[0]].append(
                    f"{feat['category']}: {feat['feature']}"
                )
            for name in missing_products:
                if any(feat["scores"][n]["coverage"] in ("full", "partial") for n in product_names if n != name):
                    gaps[name].append(f"{feat['category']}: {feat['feature']}")

    return {
        "products": product_names,
        "matrix": matrix_rows,
        "category_scores": category_scores,
        "overall_coverage": overall_coverage,
        "differentiators": differentiators,
        "gaps": {k: v[:10] for k, v in gaps.items()},
    }


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("FEATURE COMPARISON MATRIX")
    lines.append("=" * 70)

    names = result["products"]

    # Overall coverage
    lines.append(f"\n--- Overall Coverage ---")
    for name in names:
        ov = result["overall_coverage"][name]
        bar = "#" * int(ov["coverage_pct"] / 5)
        lines.append(f"  {name:<25} {ov['total_score']:>3}/{ov['max_score']}  ({ov['coverage_pct']:>5.1f}%)  {bar}")

    # Category scores
    lines.append(f"\n--- Category Scores ---")
    header = f"{'Category':<20}"
    for name in names:
        header += f" {name[:15]:>15}"
    lines.append(header)

    if result["matrix"]:
        for cat_data in result["matrix"]:
            cat = cat_data["category"]
            row = f"{cat:<20}"
            for name in names:
                cs = result["category_scores"][name].get(cat, {})
                row += f" {cs.get('percentage', 0):>13.1f}%"
            lines.append(row)

    # Feature matrix
    for cat_data in result["matrix"]:
        lines.append(f"\n--- {cat_data['category']} ---")
        header = f"  {'Feature':<25}"
        for name in names:
            header += f" {name[:12]:>12}"
        lines.append(header)

        for feat in cat_data["features"]:
            row = f"  {feat['feature']:<25}"
            for name in names:
                coverage = feat["scores"][name]["coverage"]
                row += f" {coverage:>12}"
            lines.append(row)

    # Differentiators
    lines.append(f"\n--- Unique Differentiators ---")
    for name in names:
        diffs = result["differentiators"][name]
        if diffs:
            lines.append(f"  {name}:")
            for d in diffs[:5]:
                lines.append(f"    + {d}")

    # Gaps
    lines.append(f"\n--- Key Gaps ---")
    for name in names:
        g = result["gaps"][name]
        if g:
            lines.append(f"  {name}:")
            for gap in g[:5]:
                lines.append(f"    - {gap}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Build a feature comparison matrix from structured feature data."
    )
    parser.add_argument("input_file", help="JSON file with feature comparison data")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    result = build_matrix(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
