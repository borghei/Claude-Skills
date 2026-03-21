#!/usr/bin/env python3
"""Signup Flow Scorer - Score a signup flow against conversion best practices.

Evaluates SSO availability, field count, step count, mobile optimization, error
handling, and post-submit experience. Outputs 0-100 with itemized improvements.

Usage:
    python signup_flow_scorer.py flow.json
    python signup_flow_scorer.py flow.json --format json
"""

import argparse
import json
import sys
from typing import Any


SCORING_WEIGHTS = {
    "authentication": 20,
    "field_count": 20,
    "flow_structure": 15,
    "mobile_optimization": 15,
    "error_handling": 10,
    "post_submit": 10,
    "security_ux": 10,
}


def score_authentication(data: dict) -> tuple[float, list[str]]:
    """Score authentication options (0-1)."""
    score = 0.0
    feedback = []
    auth = data.get("authentication", {})

    # SSO availability
    sso_providers = auth.get("sso_providers", [])
    if len(sso_providers) >= 2:
        score += 0.4
    elif len(sso_providers) == 1:
        score += 0.25
        feedback.append("Add a second SSO option (Google + Microsoft for B2B, Google + Apple for B2C)")
    else:
        feedback.append("No SSO -- adding Google/Apple SSO can increase completion by 15-30%")

    # SSO placement
    if auth.get("sso_above_email_form", False):
        score += 0.2
    elif sso_providers:
        feedback.append("Move SSO buttons above the email form (not below) with 'or' divider")

    # Magic link option
    if auth.get("has_magic_link", False):
        score += 0.1

    # Password-less option available
    if sso_providers or auth.get("has_magic_link", False):
        score += 0.15
    else:
        feedback.append("No password-less option -- consider magic link for lower friction")

    # Branded SSO buttons
    if auth.get("branded_sso_buttons", True) and sso_providers:
        score += 0.15
    elif sso_providers:
        feedback.append("Use official branded button styles for SSO (Google, Apple, Microsoft guidelines)")

    return min(score, 1.0), feedback


def score_field_count(data: dict) -> tuple[float, list[str]]:
    """Score field count (0-1)."""
    score = 0.0
    feedback = []
    fields = data.get("fields", [])
    field_count = len(fields)

    if field_count <= 2:
        score = 1.0
    elif field_count <= 4:
        score = 0.7
        feedback.append(f"{field_count} fields -- consider reducing to email + password (or SSO only)")
    elif field_count <= 6:
        score = 0.4
        feedback.append(f"{field_count} fields is above optimal -- each removed field improves conversion ~7-10%")
    elif field_count <= 8:
        score = 0.2
        feedback.append(f"{field_count} fields creates significant friction -- an 11-field form converts 120% worse than 4 fields")
    else:
        feedback.append(f"{field_count} fields is critically high -- audit each field with 'Before First Use' test")

    # Check for known high-friction fields
    field_names = [f.get("name", "").lower() for f in fields]
    if "phone" in field_names or "phone_number" in field_names:
        score -= 0.1
        feedback.append("Phone number field adds significant friction -- defer unless SMS verification required")
    if "credit_card" in field_names or "payment" in field_names:
        score -= 0.1
        feedback.append("Credit card at signup reduces volume 40-80% -- ensure this is justified")

    return max(min(score, 1.0), 0.0), feedback


def score_flow_structure(data: dict) -> tuple[float, list[str]]:
    """Score flow structure (0-1)."""
    score = 0.0
    feedback = []
    flow = data.get("flow_structure", {})

    steps = flow.get("step_count", 1)
    fields_total = len(data.get("fields", []))

    # Step count appropriateness
    if fields_total <= 4 and steps == 1:
        score += 0.4
    elif fields_total > 4 and 2 <= steps <= 3:
        score += 0.4
    elif steps > 3:
        score += 0.15
        feedback.append(f"{steps} steps is too many -- condense to 2-3 maximum")
    elif fields_total > 4 and steps == 1:
        score += 0.2
        feedback.append("5+ fields on a single step -- consider multi-step to reduce perceived friction")

    # Progress indicator
    if steps > 1:
        if flow.get("has_progress_indicator", False):
            score += 0.2
        else:
            feedback.append("Multi-step form needs a progress indicator ('Step 1 of 3')")

    # Back navigation
    if steps > 1:
        if flow.get("preserves_data_on_back", False):
            score += 0.1
        else:
            feedback.append("Back navigation must preserve entered data (never reset form)")

    # Skip options
    if flow.get("non_essential_steps_skippable", False):
        score += 0.15
    elif steps > 1:
        feedback.append("Add 'Skip for now' on non-essential steps (personalization, team setup)")

    # Account creation is step 1
    if flow.get("account_creation_first_step", True):
        score += 0.15
    else:
        feedback.append("Account creation (email/password) should always be Step 1 -- 60%+ of abandonment happens here if overloaded")

    return min(score, 1.0), feedback


def score_mobile(data: dict) -> tuple[float, list[str]]:
    """Score mobile optimization (0-1)."""
    score = 0.0
    feedback = []
    mobile = data.get("mobile", {})

    if mobile.get("single_column_layout", True):
        score += 0.2
    else:
        feedback.append("Mobile must use single-column layout -- never side-by-side fields")

    if mobile.get("min_touch_target_44px", False):
        score += 0.2
    else:
        feedback.append("All touch targets must be minimum 44px height")

    if mobile.get("appropriate_keyboard_types", False):
        score += 0.2
    else:
        feedback.append("Use type='email', type='tel', type='password' for appropriate mobile keyboards")

    if mobile.get("autofill_support", False):
        score += 0.15
    else:
        feedback.append("Enable browser auto-fill with standard field names (autocomplete attribute)")

    if mobile.get("sticky_cta", False):
        score += 0.15
    else:
        feedback.append("Pin 'Create Account' button to bottom of viewport on mobile")

    if mobile.get("no_captcha_or_invisible", True):
        score += 0.1
    else:
        feedback.append("Use invisible reCAPTCHA on mobile -- visual CAPTCHA kills mobile conversion")

    return min(score, 1.0), feedback


def score_error_handling(data: dict) -> tuple[float, list[str]]:
    """Score error handling (0-1)."""
    score = 0.0
    feedback = []
    errors = data.get("error_handling", {})

    if errors.get("inline_validation", False):
        score += 0.3
    else:
        feedback.append("Add inline validation (real-time feedback as user types, not just on submit)")

    if errors.get("password_checklist_realtime", False):
        score += 0.2
    else:
        feedback.append("Show password requirements as a real-time checklist that checks off as user types")

    if errors.get("existing_email_helpful_message", False):
        score += 0.2
    else:
        feedback.append("'Email already registered' error should include [Log in] and [Reset password] links")

    if errors.get("network_error_preserves_data", False):
        score += 0.15
    else:
        feedback.append("Network errors must preserve form data with a 'Try again' button")

    if errors.get("rate_limiting_message", False):
        score += 0.15
    else:
        feedback.append("Rate limiting should show clear message with wait time, not a generic error")

    return min(score, 1.0), feedback


def score_post_submit(data: dict) -> tuple[float, list[str]]:
    """Score post-submit experience (0-1)."""
    score = 0.0
    feedback = []
    post = data.get("post_submit", {})

    if post.get("auto_login", False):
        score += 0.35
    else:
        feedback.append("Auto-login after signup is critical -- never force a separate login")

    if post.get("welcome_screen", False):
        score += 0.2
    else:
        feedback.append("Show a welcome screen with clear next step, not a blank dashboard")

    if post.get("immediate_confirmation_email", False):
        score += 0.15

    verify = post.get("email_verification_strategy", "")
    if verify in ("deferred", "gate_specific_features"):
        score += 0.3
    elif verify == "immediate_required":
        feedback.append("Requiring email verification before any use kills activation -- defer to 24-48 hours")
    else:
        score += 0.15

    return min(score, 1.0), feedback


def score_security_ux(data: dict) -> tuple[float, list[str]]:
    """Score security UX (0-1)."""
    score = 0.0
    feedback = []
    security = data.get("security_ux", {})

    if security.get("password_show_hide_toggle", False):
        score += 0.3
    else:
        feedback.append("Add show/hide password toggle")

    if security.get("password_strength_indicator", False):
        score += 0.3
    else:
        feedback.append("Add password strength indicator")

    if security.get("sso_failure_fallback", False):
        score += 0.2
    else:
        feedback.append("SSO failure should show 'Try again' + 'Use email instead' options, not a generic error")

    if security.get("https_visible", True):
        score += 0.2

    return min(score, 1.0), feedback


def score_flow(data: dict) -> dict:
    """Score complete signup flow."""
    scorers = {
        "authentication": score_authentication,
        "field_count": score_field_count,
        "flow_structure": score_flow_structure,
        "mobile_optimization": score_mobile,
        "error_handling": score_error_handling,
        "post_submit": score_post_submit,
        "security_ux": score_security_ux,
    }

    total = 0.0
    components = {}

    for key, scorer_fn in scorers.items():
        raw_score, feedback = scorer_fn(data)
        weight = SCORING_WEIGHTS[key]
        weighted = raw_score * weight
        total += weighted

        components[key] = {
            "raw_score_pct": round(raw_score * 100, 1),
            "weight": weight,
            "weighted_score": round(weighted, 1),
            "feedback": feedback,
        }

    rating = "Excellent" if total >= 80 else "Good" if total >= 60 else "Needs Improvement" if total >= 40 else "Poor"

    return {
        "total_score": round(total, 1),
        "rating": rating,
        "max_possible": 100,
        "components": components,
    }


def format_text(result: dict) -> str:
    """Format score as human-readable text."""
    lines = []

    lines.append("=" * 60)
    lines.append("SIGNUP FLOW SCORE")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Total Score: {result['total_score']}/100  ({result['rating']})")
    lines.append("")

    for key, comp in result["components"].items():
        label = key.replace("_", " ").title()
        lines.append(f"{label}: {comp['raw_score_pct']}% (weight: {comp['weight']}pts -> {comp['weighted_score']}pts)")
        for fb in comp["feedback"]:
            lines.append(f"  - {fb}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Score signup flow against conversion best practices."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with signup flow configuration",
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

    result = score_flow(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
