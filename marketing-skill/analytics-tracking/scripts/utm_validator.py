#!/usr/bin/env python3
"""UTM Parameter Validator - Validate UTM parameters for consistency and best practices.

Checks URLs or UTM parameter sets against naming conventions, detects common
mistakes (mixed case, spaces, missing required params), and reports violations.

Usage:
    python utm_validator.py urls.csv
    python utm_validator.py urls.csv --json
    python utm_validator.py --url "https://example.com?utm_source=Google&utm_medium=CPC"
"""

import argparse
import csv
import json
import re
import sys
from urllib.parse import urlparse, parse_qs


VALID_MEDIUMS = {
    "cpc", "ppc", "email", "social", "organic", "referral", "display",
    "affiliate", "video", "podcast", "sms", "push", "qr", "print",
    "partner", "retargeting", "native", "cpm", "cpa", "cpl",
}

VALID_SOURCES = {
    "google", "facebook", "meta", "linkedin", "twitter", "x", "instagram",
    "youtube", "tiktok", "bing", "reddit", "pinterest", "newsletter",
    "email", "partner", "direct", "referral", "quora", "snapchat",
}

REQUIRED_PARAMS = {"utm_source", "utm_medium", "utm_campaign"}
ALL_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"}


def extract_utms_from_url(url):
    """Extract UTM parameters from a URL string."""
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        params = parse_qs(parsed.query)
        utms = {}
        for key in ALL_PARAMS:
            if key in params:
                utms[key] = params[key][0]
        return utms
    except Exception:
        return {}


def validate_utms(utms, row_id=None):
    """Validate a set of UTM parameters and return issues found."""
    issues = []
    label = f"Row {row_id}" if row_id else "URL"

    # Check required params
    for param in REQUIRED_PARAMS:
        if param not in utms or not utms[param].strip():
            issues.append({
                "severity": "error",
                "param": param,
                "issue": f"Missing required parameter: {param}",
                "label": label,
            })

    for param, value in utms.items():
        # Check for uppercase characters
        if value != value.lower():
            issues.append({
                "severity": "error",
                "param": param,
                "value": value,
                "issue": f"Contains uppercase characters (should be lowercase): '{value}'",
                "suggestion": value.lower(),
                "label": label,
            })

        # Check for spaces
        if " " in value:
            issues.append({
                "severity": "error",
                "param": param,
                "value": value,
                "issue": f"Contains spaces: '{value}'",
                "suggestion": value.replace(" ", "-"),
                "label": label,
            })

        # Check for special characters (allow hyphens, underscores, dots)
        if re.search(r"[^a-zA-Z0-9\-_.]", value.replace(" ", "")):
            issues.append({
                "severity": "warning",
                "param": param,
                "value": value,
                "issue": f"Contains special characters: '{value}'",
                "label": label,
            })

        # Check for common encoding issues
        if "%" in value and not re.match(r".*%[0-9a-fA-F]{2}.*", value):
            issues.append({
                "severity": "warning",
                "param": param,
                "value": value,
                "issue": f"Contains percent sign that may not be URL-encoded: '{value}'",
                "label": label,
            })

    # Validate utm_medium against known values
    if "utm_medium" in utms:
        medium = utms["utm_medium"].lower().strip()
        if medium and medium not in VALID_MEDIUMS:
            issues.append({
                "severity": "warning",
                "param": "utm_medium",
                "value": utms["utm_medium"],
                "issue": f"Non-standard medium: '{medium}'. Consider using one of: {', '.join(sorted(VALID_MEDIUMS))}",
                "label": label,
            })

    # Validate utm_source against known values
    if "utm_source" in utms:
        source = utms["utm_source"].lower().strip()
        if source and source not in VALID_SOURCES:
            issues.append({
                "severity": "info",
                "param": "utm_source",
                "value": utms["utm_source"],
                "issue": f"Custom source: '{source}'. Ensure this is intentional and documented.",
                "label": label,
            })

    # Check utm_campaign naming pattern
    if "utm_campaign" in utms:
        campaign = utms["utm_campaign"]
        if campaign and not re.match(r"^[a-z0-9][a-z0-9\-_.]*$", campaign.lower()):
            issues.append({
                "severity": "warning",
                "param": "utm_campaign",
                "value": campaign,
                "issue": f"Campaign name may not follow naming convention: '{campaign}'",
                "label": label,
            })

    # Check for utm_term on non-search mediums
    if "utm_term" in utms and "utm_medium" in utms:
        medium = utms["utm_medium"].lower()
        if medium not in ("cpc", "ppc", "paid-search", "search"):
            issues.append({
                "severity": "info",
                "param": "utm_term",
                "value": utms["utm_term"],
                "issue": f"utm_term is typically used for paid search only, but medium is '{medium}'",
                "label": label,
            })

    return issues


def parse_csv(filepath):
    """Parse a CSV file containing URLs or UTM parameters."""
    entries = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = [h.lower().strip() for h in (reader.fieldnames or [])]

        for i, row in enumerate(reader, start=2):
            row_lower = {k.lower().strip(): v for k, v in row.items()}

            if "url" in row_lower:
                utms = extract_utms_from_url(row_lower["url"])
                entries.append({"row": i, "source": row_lower["url"], "utms": utms})
            else:
                utms = {}
                for param in ALL_PARAMS:
                    if param in row_lower and row_lower[param]:
                        utms[param] = row_lower[param]
                    # Also check without utm_ prefix
                    short = param.replace("utm_", "")
                    if short in row_lower and row_lower[short]:
                        utms[param] = row_lower[short]
                entries.append({"row": i, "source": "csv_row", "utms": utms})

    return entries


def format_report(all_issues, total_checked):
    """Format a human-readable report."""
    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]
    infos = [i for i in all_issues if i["severity"] == "info"]

    lines = []
    lines.append("=" * 60)
    lines.append("UTM VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append(f"URLs/rows checked: {total_checked}")
    lines.append(f"Errors:   {len(errors)}")
    lines.append(f"Warnings: {len(warnings)}")
    lines.append(f"Info:     {len(infos)}")
    lines.append("")

    if errors:
        lines.append("--- ERRORS (must fix) ---")
        for issue in errors:
            lines.append(f"  [{issue['label']}] {issue['issue']}")
            if "suggestion" in issue:
                lines.append(f"    Suggestion: {issue['suggestion']}")
        lines.append("")

    if warnings:
        lines.append("--- WARNINGS (should fix) ---")
        for issue in warnings:
            lines.append(f"  [{issue['label']}] {issue['issue']}")
            if "suggestion" in issue:
                lines.append(f"    Suggestion: {issue['suggestion']}")
        lines.append("")

    if infos:
        lines.append("--- INFO (review) ---")
        for issue in infos:
            lines.append(f"  [{issue['label']}] {issue['issue']}")
        lines.append("")

    if not all_issues:
        lines.append("All UTM parameters pass validation checks.")

    # Summary
    score = max(0, 100 - (len(errors) * 15) - (len(warnings) * 5) - (len(infos) * 1))
    lines.append(f"UTM Quality Score: {score}/100")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate UTM parameters for consistency and best practices"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="CSV file with URLs or UTM parameters",
    )
    parser.add_argument(
        "--url",
        help="Single URL to validate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results in JSON format",
    )
    args = parser.parse_args()

    if not args.input and not args.url:
        parser.print_help()
        sys.exit(1)

    all_issues = []
    total_checked = 0

    if args.url:
        utms = extract_utms_from_url(args.url)
        issues = validate_utms(utms, row_id="single")
        all_issues.extend(issues)
        total_checked = 1
    elif args.input:
        try:
            entries = parse_csv(args.input)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)

        for entry in entries:
            issues = validate_utms(entry["utms"], row_id=entry["row"])
            all_issues.extend(issues)
            total_checked += 1

    if args.json_output:
        result = {
            "total_checked": total_checked,
            "total_issues": len(all_issues),
            "errors": len([i for i in all_issues if i["severity"] == "error"]),
            "warnings": len([i for i in all_issues if i["severity"] == "warning"]),
            "info": len([i for i in all_issues if i["severity"] == "info"]),
            "score": max(
                0,
                100
                - len([i for i in all_issues if i["severity"] == "error"]) * 15
                - len([i for i in all_issues if i["severity"] == "warning"]) * 5
                - len([i for i in all_issues if i["severity"] == "info"]) * 1,
            ),
            "issues": all_issues,
        }
        print(json.dumps(result, indent=2))
    else:
        print(format_report(all_issues, total_checked))

    sys.exit(1 if any(i["severity"] == "error" for i in all_issues) else 0)


if __name__ == "__main__":
    main()
