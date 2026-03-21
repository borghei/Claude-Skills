#!/usr/bin/env python3
"""Event Schema Checker - Validate analytics event names and parameters against a taxonomy.

Checks event names follow naming conventions (snake_case, noun_verb),
validates required parameters per event type, and detects PII leaks.

Usage:
    python event_schema_checker.py events.json
    python event_schema_checker.py events.json --json
    python event_schema_checker.py --generate-schema > schema.json
"""

import argparse
import json
import re
import sys


# Default SaaS event schema
DEFAULT_SCHEMA = {
    "naming_rules": {
        "case": "snake_case",
        "pattern": "noun_verb",
        "allowed_verbs": [
            "started", "completed", "failed", "viewed", "clicked",
            "submitted", "selected", "created", "updated", "deleted",
            "cancelled", "renewed", "opened", "closed", "sent",
            "received", "activated", "deactivated", "requested",
            "downloaded", "uploaded", "connected", "disconnected",
        ],
    },
    "events": {
        "signup_started": {"required_params": [], "optional_params": ["method", "source"]},
        "signup_completed": {"required_params": ["method"], "optional_params": ["user_id", "plan_name"]},
        "trial_started": {"required_params": ["plan_name"], "optional_params": ["user_id"]},
        "onboarding_step_completed": {"required_params": ["step_name", "step_number"], "optional_params": ["user_id"]},
        "feature_activated": {"required_params": ["feature_name"], "optional_params": ["user_id"]},
        "plan_selected": {"required_params": ["plan_name", "billing_period"], "optional_params": ["value", "currency"]},
        "checkout_started": {"required_params": ["value", "currency", "plan_name"], "optional_params": []},
        "checkout_completed": {"required_params": ["value", "currency", "transaction_id"], "optional_params": ["plan_name"]},
        "subscription_renewed": {"required_params": ["value", "plan_name"], "optional_params": ["currency"]},
        "subscription_cancelled": {"required_params": ["cancel_reason", "plan_name"], "optional_params": []},
        "pricing_viewed": {"required_params": [], "optional_params": ["source"]},
        "demo_requested": {"required_params": [], "optional_params": ["source"]},
        "form_submitted": {"required_params": ["form_name"], "optional_params": ["form_location"]},
        "content_downloaded": {"required_params": ["content_name"], "optional_params": ["content_type"]},
        "video_started": {"required_params": ["video_title"], "optional_params": []},
        "video_completed": {"required_params": ["video_title"], "optional_params": ["percent_watched"]},
    },
    "global_params": {
        "required_when_authenticated": ["user_id"],
        "required_with_value": ["currency"],
    },
}

# PII detection patterns
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
    "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
}

PII_PARAM_NAMES = {
    "email", "mail", "e_mail", "user_email", "customer_email",
    "phone", "phone_number", "mobile", "telephone",
    "name", "first_name", "last_name", "full_name", "customer_name",
    "address", "street", "city", "zip", "postal_code",
    "ssn", "social_security", "tax_id",
    "credit_card", "card_number", "cvv", "expiry",
    "password", "secret", "token",
}


def check_naming_convention(event_name):
    """Check if event name follows snake_case noun_verb convention."""
    issues = []

    # Check snake_case
    if event_name != event_name.lower():
        issues.append({
            "type": "naming",
            "severity": "error",
            "message": f"Event '{event_name}' is not lowercase snake_case",
            "suggestion": event_name.lower(),
        })

    if "-" in event_name:
        issues.append({
            "type": "naming",
            "severity": "error",
            "message": f"Event '{event_name}' uses hyphens instead of underscores",
            "suggestion": event_name.replace("-", "_"),
        })

    if " " in event_name:
        issues.append({
            "type": "naming",
            "severity": "error",
            "message": f"Event '{event_name}' contains spaces",
            "suggestion": event_name.replace(" ", "_").lower(),
        })

    # Check camelCase
    if re.match(r"^[a-z]+[A-Z]", event_name):
        issues.append({
            "type": "naming",
            "severity": "error",
            "message": f"Event '{event_name}' appears to be camelCase",
            "suggestion": re.sub(r"([A-Z])", r"_\1", event_name).lower(),
        })

    # Check noun_verb pattern (last segment should be a verb)
    parts = event_name.lower().split("_")
    if len(parts) < 2:
        issues.append({
            "type": "naming",
            "severity": "warning",
            "message": f"Event '{event_name}' should follow noun_verb pattern (e.g., 'form_submitted')",
        })

    return issues


def check_pii(params):
    """Check event parameters for potential PII."""
    issues = []

    for key, value in params.items():
        # Check param name
        if key.lower() in PII_PARAM_NAMES:
            issues.append({
                "type": "pii",
                "severity": "error",
                "message": f"Parameter name '{key}' likely contains PII. Remove or hash before sending.",
                "param": key,
            })

        # Check param value for PII patterns
        if isinstance(value, str):
            for pii_type, pattern in PII_PATTERNS.items():
                if pattern.search(value):
                    issues.append({
                        "type": "pii",
                        "severity": "error",
                        "message": f"Parameter '{key}' value appears to contain {pii_type}: '{value[:20]}...'",
                        "param": key,
                        "pii_type": pii_type,
                    })

    return issues


def check_schema_compliance(event_name, params, schema):
    """Check if event parameters match the expected schema."""
    issues = []
    events = schema.get("events", {})

    if event_name not in events:
        issues.append({
            "type": "schema",
            "severity": "info",
            "message": f"Event '{event_name}' is not in the defined schema. This may be intentional.",
        })
        return issues

    event_def = events[event_name]

    # Check required params
    for req_param in event_def.get("required_params", []):
        if req_param not in params:
            issues.append({
                "type": "schema",
                "severity": "error",
                "message": f"Event '{event_name}' missing required parameter: '{req_param}'",
                "param": req_param,
            })

    # Check for unknown params
    known_params = set(event_def.get("required_params", []) + event_def.get("optional_params", []))
    known_params.update(schema.get("global_params", {}).get("required_when_authenticated", []))
    known_params.update(["currency", "value"])  # Common global params

    for key in params:
        if key not in known_params:
            issues.append({
                "type": "schema",
                "severity": "info",
                "message": f"Event '{event_name}' has undocumented parameter: '{key}'",
                "param": key,
            })

    # Check value/currency pairing
    global_params = schema.get("global_params", {})
    if "value" in params and "currency" not in params:
        if "currency" in global_params.get("required_with_value", []):
            issues.append({
                "type": "schema",
                "severity": "error",
                "message": f"Event '{event_name}' has 'value' without 'currency'",
            })

    return issues


def validate_events(events_data, schema=None):
    """Validate a list of events against naming conventions and schema."""
    if schema is None:
        schema = DEFAULT_SCHEMA

    all_issues = []
    event_counts = {}

    for i, event in enumerate(events_data):
        event_name = event.get("event", event.get("name", ""))
        params = event.get("params", event.get("parameters", {}))

        if not event_name:
            all_issues.append({
                "type": "structure",
                "severity": "error",
                "message": f"Event at index {i} has no event name",
                "event_index": i,
            })
            continue

        # Track event counts for duplicate detection
        event_counts[event_name] = event_counts.get(event_name, 0) + 1

        # Naming convention checks
        naming_issues = check_naming_convention(event_name)
        for issue in naming_issues:
            issue["event"] = event_name
            issue["event_index"] = i
        all_issues.extend(naming_issues)

        # PII checks
        pii_issues = check_pii(params)
        for issue in pii_issues:
            issue["event"] = event_name
            issue["event_index"] = i
        all_issues.extend(pii_issues)

        # Schema compliance checks
        schema_issues = check_schema_compliance(event_name, params, schema)
        for issue in schema_issues:
            issue["event"] = event_name
            issue["event_index"] = i
        all_issues.extend(schema_issues)

    return all_issues, event_counts


def format_report(all_issues, event_counts, total_events):
    """Format human-readable report."""
    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]
    infos = [i for i in all_issues if i["severity"] == "info"]

    lines = []
    lines.append("=" * 60)
    lines.append("EVENT SCHEMA VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append(f"Events checked:  {total_events}")
    lines.append(f"Unique events:   {len(event_counts)}")
    lines.append(f"Errors:          {len(errors)}")
    lines.append(f"Warnings:        {len(warnings)}")
    lines.append(f"Info:            {len(infos)}")
    lines.append("")

    if errors:
        lines.append("--- ERRORS ---")
        for issue in errors:
            event_label = issue.get("event", "unknown")
            lines.append(f"  [{event_label}] {issue['message']}")
            if "suggestion" in issue:
                lines.append(f"    Suggestion: {issue['suggestion']}")
        lines.append("")

    if warnings:
        lines.append("--- WARNINGS ---")
        for issue in warnings:
            event_label = issue.get("event", "unknown")
            lines.append(f"  [{event_label}] {issue['message']}")
        lines.append("")

    if infos:
        lines.append("--- INFO ---")
        for issue in infos:
            event_label = issue.get("event", "unknown")
            lines.append(f"  [{event_label}] {issue['message']}")
        lines.append("")

    pii_count = len([i for i in all_issues if i.get("type") == "pii"])
    if pii_count > 0:
        lines.append(f"PII ALERT: {pii_count} potential PII violations detected!")
        lines.append("")

    score = max(0, 100 - (len(errors) * 10) - (len(warnings) * 3) - (len(infos) * 1))
    lines.append(f"Schema Compliance Score: {score}/100")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate analytics event names and parameters against a taxonomy"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="JSON file containing events array",
    )
    parser.add_argument(
        "--schema",
        help="Custom schema JSON file (default: built-in SaaS schema)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--generate-schema",
        action="store_true",
        help="Print the default schema as JSON for customization",
    )
    args = parser.parse_args()

    if args.generate_schema:
        print(json.dumps(DEFAULT_SCHEMA, indent=2))
        sys.exit(0)

    if not args.input:
        parser.print_help()
        sys.exit(1)

    # Load events
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    events = data if isinstance(data, list) else data.get("events", [])

    # Load custom schema
    schema = DEFAULT_SCHEMA
    if args.schema:
        try:
            with open(args.schema, "r", encoding="utf-8") as f:
                schema = json.load(f)
        except Exception as e:
            print(f"Error loading schema: {e}", file=sys.stderr)
            sys.exit(1)

    all_issues, event_counts = validate_events(events, schema)

    if args.json_output:
        result = {
            "total_events": len(events),
            "unique_events": len(event_counts),
            "event_counts": event_counts,
            "total_issues": len(all_issues),
            "errors": len([i for i in all_issues if i["severity"] == "error"]),
            "warnings": len([i for i in all_issues if i["severity"] == "warning"]),
            "info": len([i for i in all_issues if i["severity"] == "info"]),
            "pii_violations": len([i for i in all_issues if i.get("type") == "pii"]),
            "score": max(
                0,
                100
                - len([i for i in all_issues if i["severity"] == "error"]) * 10
                - len([i for i in all_issues if i["severity"] == "warning"]) * 3
                - len([i for i in all_issues if i["severity"] == "info"]) * 1,
            ),
            "issues": all_issues,
        }
        print(json.dumps(result, indent=2))
    else:
        print(format_report(all_issues, event_counts, len(events)))

    sys.exit(1 if any(i["severity"] == "error" for i in all_issues) else 0)


if __name__ == "__main__":
    main()
