#!/usr/bin/env python3
"""Signup Field Auditor - Audit signup form fields for friction and reduction opportunities.

Evaluates each field against the "Before First Use" test, identifies enrichment
opportunities, and recommends which fields to keep, defer, or remove.

Usage:
    python signup_field_auditor.py fields.json
    python signup_field_auditor.py fields.json --format json
"""

import argparse
import json
import sys
from typing import Any


# Field classification database
FIELD_DATABASE = {
    "email": {
        "essential": True,
        "reason": "Account identity -- required for authentication",
        "recommendation": "keep",
    },
    "password": {
        "essential": True,
        "reason": "Account security (unless using SSO/magic link)",
        "recommendation": "keep_or_replace",
        "alternative": "Consider magic link or SSO to eliminate password entirely",
    },
    "first_name": {
        "essential": False,
        "reason": "Nice for personalization but not needed before first use",
        "recommendation": "defer",
        "defer_to": "onboarding or profile settings",
        "enrichment": "Can be extracted from SSO provider",
    },
    "last_name": {
        "essential": False,
        "reason": "Rarely needed before first use",
        "recommendation": "defer_or_remove",
        "defer_to": "profile settings or enrich from SSO",
        "enrichment": "Can be extracted from SSO provider",
    },
    "full_name": {
        "essential": False,
        "reason": "Personalization only -- defer or get from SSO",
        "recommendation": "defer",
        "defer_to": "onboarding or SSO auto-fill",
        "enrichment": "SSO providers return full name",
    },
    "company": {
        "essential": False,
        "reason": "Can be enriched from email domain",
        "recommendation": "enrich",
        "enrichment": "Clearbit, Apollo, or email domain lookup",
    },
    "company_name": {
        "essential": False,
        "reason": "Can be enriched from email domain",
        "recommendation": "enrich",
        "enrichment": "Clearbit, Apollo, or email domain lookup",
    },
    "phone": {
        "essential": False,
        "reason": "Rarely needed at signup unless SMS verification required",
        "recommendation": "defer_or_remove",
        "defer_to": "sales qualification or profile",
    },
    "phone_number": {
        "essential": False,
        "reason": "Rarely needed at signup unless SMS verification required",
        "recommendation": "defer_or_remove",
        "defer_to": "sales qualification or profile",
    },
    "job_title": {
        "essential": False,
        "reason": "Used for routing/segmentation but not needed for product use",
        "recommendation": "defer",
        "defer_to": "onboarding (day 3-5) or enrich",
        "enrichment": "LinkedIn API or CSM research",
    },
    "role": {
        "essential": False,
        "reason": "Used for personalization -- collect during onboarding, not signup",
        "recommendation": "defer",
        "defer_to": "onboarding welcome screen",
    },
    "team_size": {
        "essential": False,
        "reason": "Used for provisioning -- only needed for enterprise trials",
        "recommendation": "defer",
        "defer_to": "onboarding or enrich from company data",
        "enrichment": "Company data API",
    },
    "industry": {
        "essential": False,
        "reason": "Used for segmentation -- can be enriched automatically",
        "recommendation": "enrich",
        "enrichment": "Company data API from email domain",
    },
    "how_did_you_hear": {
        "essential": False,
        "reason": "Attribution data -- never needed before first use",
        "recommendation": "remove",
        "alternative": "Use UTM parameters and attribution tracking instead",
    },
    "referral_source": {
        "essential": False,
        "reason": "Attribution data should come from tracking, not user input",
        "recommendation": "remove",
        "alternative": "UTM parameters, referrer header, attribution tools",
    },
    "address": {
        "essential": False,
        "reason": "Not needed unless shipping physical goods at signup",
        "recommendation": "defer_or_remove",
        "defer_to": "billing or shipping flow",
    },
    "country": {
        "essential": False,
        "reason": "Can be determined from IP geolocation",
        "recommendation": "enrich",
        "enrichment": "IP geolocation (on signup)",
    },
    "credit_card": {
        "essential": False,
        "reason": "Reduces signup volume 40-80%; only require if justified by business model",
        "recommendation": "defer",
        "defer_to": "upgrade flow or end of trial",
    },
    "agree_terms": {
        "essential": True,
        "reason": "Legal requirement for terms of service acceptance",
        "recommendation": "keep",
    },
    "consent_marketing": {
        "essential": True,
        "reason": "GDPR requirement -- must be unchecked by default",
        "recommendation": "keep",
    },
}


def audit_field(field: dict) -> dict:
    """Audit a single field."""
    name = field.get("name", "").lower().replace(" ", "_").replace("-", "_")
    label = field.get("label", field.get("name", "Unknown"))
    required = field.get("required", True)

    # Look up in database
    db_entry = FIELD_DATABASE.get(name)

    if db_entry:
        result = {
            "field_name": label,
            "field_key": name,
            "required_in_form": required,
            "essential_for_product": db_entry["essential"],
            "recommendation": db_entry["recommendation"],
            "reason": db_entry["reason"],
        }
        if "defer_to" in db_entry:
            result["defer_to"] = db_entry["defer_to"]
        if "enrichment" in db_entry:
            result["enrichment_option"] = db_entry["enrichment"]
        if "alternative" in db_entry:
            result["alternative"] = db_entry["alternative"]
    else:
        # Unknown field -- flag for review
        result = {
            "field_name": label,
            "field_key": name,
            "required_in_form": required,
            "essential_for_product": False,
            "recommendation": "review",
            "reason": f"Field '{name}' not in standard database -- manually assess if needed before first product use",
        }

    # Friction score (0 = no friction, 10 = maximum friction)
    friction = 0
    if name in ("email", "agree_terms", "consent_marketing"):
        friction = 1
    elif name == "password":
        friction = 3
    elif name in ("first_name", "full_name"):
        friction = 2
    elif name in ("last_name", "company", "company_name"):
        friction = 3
    elif name in ("phone", "phone_number"):
        friction = 5
    elif name in ("job_title", "role", "team_size", "industry"):
        friction = 4
    elif name in ("how_did_you_hear", "referral_source"):
        friction = 4
    elif name in ("credit_card",):
        friction = 8
    elif name in ("address",):
        friction = 7
    else:
        friction = 4

    result["friction_score"] = friction

    return result


def audit_fields(data: dict) -> dict:
    """Audit all signup form fields."""
    fields = data.get("fields", [])
    signup_type = data.get("signup_type", "free_trial")
    has_sso = data.get("has_sso", False)

    field_results = []
    total_friction = 0
    keep_count = 0
    defer_count = 0
    remove_count = 0
    enrich_count = 0

    for field in fields:
        result = audit_field(field)
        field_results.append(result)
        total_friction += result["friction_score"]

        rec = result["recommendation"]
        if rec in ("keep", "keep_or_replace"):
            keep_count += 1
        elif rec in ("defer", "defer_or_remove"):
            defer_count += 1
        elif rec == "remove":
            remove_count += 1
        elif rec == "enrich":
            enrich_count += 1

    # Minimum viable field set for signup type
    min_fields = {
        "freemium": ["email"],
        "free_trial": ["email", "password"],
        "free_trial_sales_assisted": ["email", "password", "company"],
        "paid": ["email", "password", "credit_card"],
        "waitlist": ["email"],
        "enterprise_trial": ["email", "company", "role"],
    }
    recommended_min = min_fields.get(signup_type, ["email", "password"])
    current_field_names = [f.get("name", "").lower().replace(" ", "_").replace("-", "_") for f in fields]
    excess_fields = len(fields) - len(recommended_min)

    # Overall assessment
    if len(fields) <= len(recommended_min) + 1:
        form_rating = "Excellent"
    elif len(fields) <= len(recommended_min) + 3:
        form_rating = "Good"
    elif len(fields) <= 7:
        form_rating = "Needs Reduction"
    else:
        form_rating = "High Friction"

    # Estimated conversion impact
    # Each unnecessary field reduces conversion by ~5-10%
    unnecessary_count = defer_count + remove_count + enrich_count
    estimated_conversion_lift = unnecessary_count * 7  # ~7% per removed field (conservative)

    return {
        "summary": {
            "total_fields": len(fields),
            "recommended_minimum": len(recommended_min),
            "excess_fields": max(excess_fields, 0),
            "form_rating": form_rating,
            "total_friction_score": total_friction,
            "keep": keep_count,
            "defer": defer_count,
            "remove": remove_count,
            "enrich": enrich_count,
            "has_sso": has_sso,
            "signup_type": signup_type,
            "estimated_conversion_lift_pct": estimated_conversion_lift,
        },
        "recommended_minimum_fields": recommended_min,
        "field_audit": field_results,
        "sso_note": "SSO eliminates email+password fields (name and email come from provider)" if not has_sso else "SSO available -- good",
    }


def format_text(result: dict) -> str:
    """Format audit as human-readable text."""
    lines = []
    s = result["summary"]

    lines.append("=" * 60)
    lines.append("SIGNUP FIELD AUDIT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Form Rating: {s['form_rating']}")
    lines.append(f"Total Fields: {s['total_fields']}  |  Recommended Minimum: {s['recommended_minimum']}  |  Excess: {s['excess_fields']}")
    lines.append(f"Friction Score: {s['total_friction_score']}")
    lines.append(f"SSO Available: {'Yes' if s['has_sso'] else 'No -- adding SSO can boost signups 15-30%'}")
    lines.append(f"Signup Type: {s['signup_type']}")
    lines.append("")
    lines.append(f"Actions: Keep {s['keep']} | Defer {s['defer']} | Remove {s['remove']} | Enrich {s['enrich']}")
    if s["estimated_conversion_lift_pct"] > 0:
        lines.append(f"Estimated Conversion Lift: ~{s['estimated_conversion_lift_pct']}% from removing unnecessary fields")
    lines.append("")

    lines.append(f"Minimum viable: {', '.join(result['recommended_minimum_fields'])}")
    lines.append("")

    lines.append("-" * 60)
    lines.append("FIELD-BY-FIELD AUDIT")
    lines.append("-" * 60)
    for f in result["field_audit"]:
        rec_label = f["recommendation"].upper().replace("_", " ")
        lines.append(f"\n  {f['field_name']} [{rec_label}] (friction: {f['friction_score']}/10)")
        lines.append(f"    Essential: {'Yes' if f['essential_for_product'] else 'No'}")
        lines.append(f"    Reason: {f['reason']}")
        if "defer_to" in f:
            lines.append(f"    Defer to: {f['defer_to']}")
        if "enrichment_option" in f:
            lines.append(f"    Enrichment: {f['enrichment_option']}")
        if "alternative" in f:
            lines.append(f"    Alternative: {f['alternative']}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit signup form fields for friction and reduction opportunities."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with form field configuration",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = audit_fields(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
