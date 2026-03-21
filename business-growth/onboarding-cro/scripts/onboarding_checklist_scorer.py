#!/usr/bin/env python3
"""
Onboarding Checklist Scorer

Score an onboarding checklist design against best practices: item count,
ordering, quick wins, progress indication, and user experience.

Usage:
    python onboarding_checklist_scorer.py checklist.json
    python onboarding_checklist_scorer.py checklist.json --json
"""

import argparse
import json
import sys


def score_checklist(data: dict) -> dict:
    """Score onboarding checklist against best practices."""
    items = data.get("items", [])
    checklist_config = data.get("config", {})

    if not items:
        return {"error": "No checklist items provided."}

    scores = {}
    checks = []

    # --- Item Count (max 20) ---
    count = len(items)
    if 3 <= count <= 7:
        scores["item_count"] = 20
        checks.append({"check": f"Item count ({count}) is in optimal range (3-7)", "passed": True})
    elif count < 3:
        scores["item_count"] = 10
        checks.append({"check": f"Item count ({count}) is below minimum (3). May not be worth a checklist", "passed": False})
    elif count <= 10:
        scores["item_count"] = 12
        checks.append({"check": f"Item count ({count}) exceeds optimal (3-7). Consider reducing", "passed": False})
    else:
        scores["item_count"] = 5
        checks.append({"check": f"Item count ({count}) is overwhelming (>10). Reduce to 7 max", "passed": False})

    # --- Quick Win First (max 15) ---
    first_item = items[0] if items else {}
    first_minutes = first_item.get("estimated_minutes", 5)
    if first_minutes <= 1:
        scores["quick_win_first"] = 15
        checks.append({"check": "First item completable in <1 minute (quick win)", "passed": True})
    elif first_minutes <= 3:
        scores["quick_win_first"] = 10
        checks.append({"check": f"First item takes {first_minutes} min. Target <1 minute", "passed": False})
    else:
        scores["quick_win_first"] = 5
        checks.append({"check": f"First item takes {first_minutes} min. Too complex for first step", "passed": False})

    # --- Value Ordering (max 15) ---
    # Check if items are ordered by impact (high impact first)
    impacts = [item.get("impact", "medium") for item in items]
    impact_values = {"high": 3, "medium": 2, "low": 1}
    impact_nums = [impact_values.get(i, 2) for i in impacts]

    well_ordered = all(impact_nums[i] >= impact_nums[i + 1] for i in range(len(impact_nums) - 1))
    if well_ordered or (len(items) > 0 and impact_nums[0] == 3):
        scores["value_ordering"] = 15
        checks.append({"check": "Items ordered by value/impact (high-impact first)", "passed": True})
    else:
        scores["value_ordering"] = 8
        checks.append({"check": "Items not optimally ordered by impact. Put highest-value items first", "passed": False})

    # --- Item Quality (max 20) ---
    item_quality_score = 0
    items_with_cta = sum(1 for i in items if i.get("has_cta", False))
    items_with_time = sum(1 for i in items if i.get("estimated_minutes") is not None)
    items_with_rationale = sum(1 for i in items if i.get("rationale"))

    if items_with_cta == len(items):
        item_quality_score += 7
        checks.append({"check": "All items have CTA buttons", "passed": True})
    else:
        checks.append({"check": f"Only {items_with_cta}/{count} items have CTAs. Add action buttons to all", "passed": False})

    if items_with_time == len(items):
        item_quality_score += 7
        checks.append({"check": "All items show estimated time", "passed": True})
    else:
        checks.append({"check": f"Only {items_with_time}/{count} items show time estimates. Add to all", "passed": False})

    if items_with_rationale >= len(items) * 0.7:
        item_quality_score += 6
        checks.append({"check": "Most items explain why (rationale text)", "passed": True})
    else:
        checks.append({"check": f"Only {items_with_rationale}/{count} items have rationale. Explain why each matters", "passed": False})

    scores["item_quality"] = item_quality_score

    # --- UX Features (max 30) ---
    ux_score = 0
    has_progress = checklist_config.get("has_progress_indicator", False)
    has_celebration = checklist_config.get("has_completion_celebration", False)
    is_dismissable = checklist_config.get("is_dismissable", False)
    pre_checks_completed = checklist_config.get("pre_checks_completed", False)
    is_persistent = checklist_config.get("persistent_not_blocking", False)
    allows_back_nav = checklist_config.get("allows_back_navigation", True)

    for feature, label, points in [
        (has_progress, "Progress indicator visible", 6),
        (has_celebration, "Completion celebration (confetti, message)", 5),
        (is_dismissable, "Checklist is dismissable ('I'll do this later')", 5),
        (pre_checks_completed, "Pre-checks already-completed items", 5),
        (is_persistent, "Persistent but non-blocking (sidebar/card, not modal)", 5),
        (allows_back_nav, "Users can revisit previous items", 4),
    ]:
        if feature:
            ux_score += points
            checks.append({"check": label, "passed": True})
        else:
            checks.append({"check": label, "passed": False})

    scores["ux_features"] = ux_score

    total_score = sum(scores.values())
    max_score = 100

    if total_score >= 80:
        grade = "A"
    elif total_score >= 65:
        grade = "B"
    elif total_score >= 50:
        grade = "C"
    elif total_score >= 35:
        grade = "D"
    else:
        grade = "F"

    # Item details
    item_details = []
    for i, item in enumerate(items):
        item_details.append({
            "position": i + 1,
            "label": item.get("label", f"Item {i + 1}"),
            "estimated_minutes": item.get("estimated_minutes"),
            "impact": item.get("impact", "medium"),
            "has_cta": item.get("has_cta", False),
            "has_rationale": bool(item.get("rationale")),
        })

    return {
        "total_score": total_score,
        "max_score": max_score,
        "grade": grade,
        "scores": scores,
        "checks": checks,
        "item_count": count,
        "item_details": item_details,
        "total_estimated_minutes": sum(i.get("estimated_minutes", 0) for i in items),
        "recommendations": _generate_recommendations(scores, checks, count),
    }


def _generate_recommendations(scores: dict, checks: list, count: int) -> list:
    """Generate recommendations."""
    recs = []
    failed = [c for c in checks if not c["passed"]]

    for f in failed[:5]:
        priority = "HIGH" if "CTA" in f["check"] or "count" in f["check"] else "MEDIUM"
        recs.append({
            "priority": priority,
            "recommendation": f["check"],
        })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"ONBOARDING CHECKLIST SCORE: {result['grade']} ({result['total_score']}/{result['max_score']})")
    lines.append("=" * 60)

    lines.append(f"\nItems: {result['item_count']}")
    lines.append(f"Total Est. Time: {result['total_estimated_minutes']} minutes")

    lines.append(f"\n--- Dimension Scores ---")
    for dim, score in result["scores"].items():
        lines.append(f"  {dim:<20} {score:>3}")

    lines.append(f"\n--- Checklist Audit ---")
    for c in result["checks"]:
        status = "[PASS]" if c["passed"] else "[FAIL]"
        lines.append(f"  {status} {c['check']}")

    lines.append(f"\n--- Item Details ---")
    for item in result["item_details"]:
        mins = f"{item['estimated_minutes']}min" if item["estimated_minutes"] else "?"
        lines.append(f"  {item['position']}. {item['label']:<30} {mins:>6} {item['impact']:>8} CTA:{'Y' if item['has_cta'] else 'N'}")

    if result["recommendations"]:
        lines.append(f"\n--- Recommendations ---")
        for r in result["recommendations"]:
            lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score an onboarding checklist design against best practices."
    )
    parser.add_argument("input_file", help="JSON file with checklist items and properties")
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

    result = score_checklist(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
