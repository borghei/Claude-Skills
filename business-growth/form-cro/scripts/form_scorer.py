#!/usr/bin/env python3
"""
Form Scorer

Score a form against CRO best practices across field count, field types,
CTA quality, mobile readiness, and trust signals.

Usage:
    python form_scorer.py form_config.json
    python form_scorer.py form_config.json --json
"""

import argparse
import json
import sys


FIELD_TYPE_PENALTIES = {
    "email": 0,
    "first_name": 2,
    "last_name": 3,
    "phone": 8,
    "company": 4,
    "company_size": 4,
    "job_title": 4,
    "industry": 3,
    "message": 6,
    "budget": 10,
    "custom": 4,
}

ENRICHABLE_FIELDS = ["company", "company_size", "industry", "job_title"]


def score_form(data: dict) -> dict:
    """Score form against CRO best practices."""
    form = data.get("form", {})
    fields = form.get("fields", [])
    cta = form.get("cta", {})
    form_type = form.get("type", "lead_capture")
    has_mobile_optimization = form.get("mobile_optimized", False)
    trust_signals = form.get("trust_signals", [])
    is_multi_step = form.get("multi_step", False)
    has_validation = form.get("inline_validation", False)

    # --- Field Analysis ---
    field_count = len(fields)
    total_abandonment_cost = 0
    field_analysis = []
    enrichable_count = 0

    for f in fields:
        ftype = f.get("type", "custom")
        required = f.get("required", True)
        penalty = FIELD_TYPE_PENALTIES.get(ftype, 4)
        is_enrichable = ftype in ENRICHABLE_FIELDS

        if is_enrichable:
            enrichable_count += 1

        field_analysis.append({
            "field": f.get("label", ftype),
            "type": ftype,
            "required": required,
            "estimated_drop_pct": penalty,
            "enrichable": is_enrichable,
            "recommendation": "Remove (enrichable post-submission)" if is_enrichable and required else
                              "Keep" if penalty <= 3 else
                              "Consider removing" if penalty >= 6 else "Review necessity",
        })
        if required:
            total_abandonment_cost += penalty

    # --- Scoring Dimensions ---
    scores = {}

    # Field count score (max 25)
    if field_count <= 3:
        scores["field_count"] = 25
    elif field_count <= 5:
        scores["field_count"] = 20
    elif field_count <= 7:
        scores["field_count"] = 12
    else:
        scores["field_count"] = max(0, 25 - (field_count - 3) * 3)

    # CTA quality (max 20)
    cta_score = 0
    cta_text = cta.get("text", "Submit")
    cta_checks = []

    if cta_text.lower() != "submit":
        cta_score += 5
        cta_checks.append({"check": "Not generic 'Submit'", "passed": True})
    else:
        cta_checks.append({"check": "Not generic 'Submit'", "passed": False})

    if any(w in cta_text.lower() for w in ["my", "your", "free", "get", "start", "download"]):
        cta_score += 5
        cta_checks.append({"check": "Uses value-oriented language", "passed": True})
    else:
        cta_checks.append({"check": "Uses value-oriented language", "passed": False})

    if len(cta_text.split()) <= 5:
        cta_score += 5
        cta_checks.append({"check": "Under 5 words", "passed": True})
    else:
        cta_checks.append({"check": "Under 5 words", "passed": False})

    if cta.get("high_contrast", False):
        cta_score += 5
        cta_checks.append({"check": "High contrast button", "passed": True})
    else:
        cta_checks.append({"check": "High contrast button", "passed": False})

    scores["cta_quality"] = cta_score

    # Mobile readiness (max 20)
    mobile_score = 0
    mobile_checks = []

    if has_mobile_optimization:
        mobile_score += 8
        mobile_checks.append({"check": "Mobile-optimized layout", "passed": True})
    else:
        mobile_checks.append({"check": "Mobile-optimized layout", "passed": False})

    if form.get("single_column", True):
        mobile_score += 4
        mobile_checks.append({"check": "Single-column layout", "passed": True})
    else:
        mobile_checks.append({"check": "Single-column layout", "passed": False})

    if form.get("keyboard_types", False):
        mobile_score += 4
        mobile_checks.append({"check": "Correct keyboard types (email, tel)", "passed": True})
    else:
        mobile_checks.append({"check": "Correct keyboard types (email, tel)", "passed": False})

    if form.get("touch_targets_44px", False):
        mobile_score += 4
        mobile_checks.append({"check": "44px+ touch targets", "passed": True})
    else:
        mobile_checks.append({"check": "44px+ touch targets", "passed": False})

    scores["mobile_readiness"] = mobile_score

    # Trust signals (max 15)
    trust_score = min(15, len(trust_signals) * 5)
    scores["trust_signals"] = trust_score

    # Validation UX (max 10)
    validation_score = 0
    if has_validation:
        validation_score += 5
    if form.get("error_messages_inline", False):
        validation_score += 5
    scores["validation_ux"] = validation_score

    # Multi-step bonus (max 10)
    if is_multi_step and field_count > 5:
        scores["multi_step"] = 10
    elif not is_multi_step and field_count <= 5:
        scores["multi_step"] = 10
    elif is_multi_step and field_count <= 5:
        scores["multi_step"] = 5  # Unnecessary multi-step
    else:
        scores["multi_step"] = 0  # Should be multi-step but isn't

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

    return {
        "form_type": form_type,
        "total_score": total_score,
        "max_score": max_score,
        "grade": grade,
        "scores": scores,
        "field_analysis": field_analysis,
        "field_summary": {
            "total_fields": field_count,
            "enrichable_fields": enrichable_count,
            "estimated_total_abandonment_pct": min(80, total_abandonment_cost),
        },
        "cta_checks": cta_checks,
        "mobile_checks": mobile_checks,
        "trust_signals_present": trust_signals,
        "recommendations": _generate_recommendations(scores, field_analysis, field_count, is_multi_step),
    }


def _generate_recommendations(scores: dict, fields: list, count: int, multi_step: bool) -> list:
    """Generate prioritized recommendations."""
    recs = []
    if scores["field_count"] < 15:
        removable = [f for f in fields if f["enrichable"] and f["required"]]
        if removable:
            names = ", ".join(f["field"] for f in removable[:3])
            recs.append({"priority": "HIGH", "area": "Field count",
                         "recommendation": f"Remove enrichable fields: {names}. These can be populated post-submission."})
    if scores["cta_quality"] < 15:
        recs.append({"priority": "HIGH", "area": "CTA",
                     "recommendation": "Replace generic CTA with value-specific copy (e.g., 'Get My Report' instead of 'Submit')."})
    if scores["mobile_readiness"] < 12:
        recs.append({"priority": "HIGH", "area": "Mobile",
                     "recommendation": "Implement mobile optimization: single column, 44px touch targets, correct keyboard types."})
    if scores["trust_signals"] < 10:
        recs.append({"priority": "MEDIUM", "area": "Trust",
                     "recommendation": "Add trust signals near the form: privacy assurance, security badges, or testimonial."})
    if count > 5 and not multi_step:
        recs.append({"priority": "MEDIUM", "area": "Structure",
                     "recommendation": "Convert to multi-step form. Capture email in step 1, qualifying info in step 2."})
    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"FORM CRO SCORE: {result['grade']} ({result['total_score']}/{result['max_score']})")
    lines.append("=" * 60)

    lines.append(f"\nForm Type: {result['form_type']}")
    lines.append(f"Fields: {result['field_summary']['total_fields']} ({result['field_summary']['enrichable_fields']} enrichable)")
    lines.append(f"Est. Abandonment: {result['field_summary']['estimated_total_abandonment_pct']}%")

    lines.append(f"\n--- Dimension Scores ---")
    for dim, score in result["scores"].items():
        lines.append(f"  {dim:<20} {score:>3}")

    lines.append(f"\n--- Field Analysis ---")
    lines.append(f"  {'Field':<20} {'Type':<15} {'Drop%':>6} {'Enrichable':>10} {'Action'}")
    for f in result["field_analysis"]:
        lines.append(f"  {f['field']:<20} {f['type']:<15} {f['estimated_drop_pct']:>5d}% {'Yes' if f['enrichable'] else 'No':>10} {f['recommendation']}")

    lines.append(f"\n--- CTA Checks ---")
    for c in result["cta_checks"]:
        status = "[PASS]" if c["passed"] else "[FAIL]"
        lines.append(f"  {status} {c['check']}")

    lines.append(f"\n--- Recommendations ---")
    for r in result["recommendations"]:
        lines.append(f"[{r['priority']}] {r['area']}: {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score a form against CRO best practices."
    )
    parser.add_argument("input_file", help="JSON file with form configuration")
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

    result = score_form(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
