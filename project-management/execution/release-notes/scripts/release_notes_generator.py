#!/usr/bin/env python3
"""
Release Notes Generator

Generates formatted release notes from structured JSON input.
Groups entries by category, formats into markdown or JSON output,
and flags entries that may need user-benefit rewriting.

Usage:
    python release_notes_generator.py --input changes.json --product-name "App" --version "2.0.0"
    python release_notes_generator.py --demo --product-name "App" --version "1.0.0"
    python release_notes_generator.py --input changes.json --format json --product-name "App" --version "2.0.0"

Input JSON format:
    {
        "entries": [
            {
                "title": "Dashboard caching",
                "description": "Dashboards now load up to 3x faster",
                "type": "improvement",
                "ticket_id": "PROJ-123"
            }
        ]
    }

Supported types: feature, improvement, bugfix, breaking, deprecation
"""

import argparse
import json
import sys
import re
from datetime import date
from typing import Any

# --- Constants ---

VALID_TYPES = {"feature", "improvement", "bugfix", "breaking", "deprecation"}

CATEGORY_MAP = {
    "feature": "New Features",
    "improvement": "Improvements",
    "bugfix": "Bug Fixes",
    "breaking": "Breaking Changes",
    "deprecation": "Deprecations",
}

CATEGORY_ORDER = ["feature", "improvement", "bugfix", "breaking", "deprecation"]

# Patterns that suggest an entry is too technical and needs rewriting
TECHNICAL_PATTERNS = [
    re.compile(r"\b(refactor|migrat|implement|updat|add|remov|fix)\w*\b", re.IGNORECASE),
    re.compile(r"\b[A-Z][a-z]+[A-Z]\w+\b"),  # CamelCase class names
    re.compile(r"\b\w+_\w+\b"),  # snake_case identifiers
    re.compile(r"\b(API|SDK|CLI|OAuth|SAML|SSO|JWT|gRPC|REST)\b"),
    re.compile(r"\b(null|undefined|exception|handler|module|endpoint|schema)\b", re.IGNORECASE),
]

DEMO_DATA: dict[str, Any] = {
    "entries": [
        {
            "title": "Team Workspaces",
            "description": "Create shared workspaces where your team can collaborate on projects in real time",
            "type": "feature",
            "ticket_id": "PROJ-201",
        },
        {
            "title": "Bulk CSV Import",
            "description": "Import up to 10,000 records at once using the new CSV bulk import tool",
            "type": "feature",
            "ticket_id": "PROJ-198",
        },
        {
            "title": "Faster Dashboard Loading",
            "description": "Dashboards now load up to 3x faster thanks to optimized data retrieval",
            "type": "improvement",
            "ticket_id": "PROJ-187",
        },
        {
            "title": "Improved Search Relevance",
            "description": "Search results now prioritize exact matches and recent items, making it easier to find what you need",
            "type": "improvement",
            "ticket_id": "PROJ-192",
        },
        {
            "title": "Export Date Range Fix",
            "description": "Report exports no longer fail when the selected date range includes days with no data",
            "type": "bugfix",
            "ticket_id": "PROJ-205",
        },
        {
            "title": "Notification Delivery Fix",
            "description": "Email notifications for overdue tasks are now delivered reliably within 5 minutes",
            "type": "bugfix",
            "ticket_id": "PROJ-210",
        },
        {
            "title": "API v2 Migration",
            "description": "The /v1/users endpoint has been replaced by /v2/users. Update your integrations before June 30.",
            "type": "breaking",
            "ticket_id": "PROJ-180",
        },
        {
            "title": "Legacy CSV Import",
            "description": "The single-record CSV import wizard will be removed in v4.0. Use the new bulk import tool instead.",
            "type": "deprecation",
            "ticket_id": "PROJ-199",
        },
    ]
}


def validate_entries(entries: list[dict]) -> list[str]:
    """Validate input entries and return a list of error messages."""
    errors = []
    for i, entry in enumerate(entries):
        if "title" not in entry or not entry["title"].strip():
            errors.append(f"Entry {i}: missing or empty 'title'")
        if "description" not in entry or not entry["description"].strip():
            errors.append(f"Entry {i}: missing or empty 'description'")
        if "type" not in entry:
            errors.append(f"Entry {i}: missing 'type'")
        elif entry["type"] not in VALID_TYPES:
            errors.append(
                f"Entry {i}: invalid type '{entry['type']}'. "
                f"Valid types: {', '.join(sorted(VALID_TYPES))}"
            )
    return errors


def check_technical_language(description: str) -> list[str]:
    """Check if a description contains technical language that may need rewriting."""
    warnings = []
    for pattern in TECHNICAL_PATTERNS:
        matches = pattern.findall(description)
        if matches:
            warnings.append(f"Possible technical language: {', '.join(set(matches))}")
    return warnings


def group_entries(entries: list[dict]) -> dict[str, list[dict]]:
    """Group entries by their type category."""
    groups: dict[str, list[dict]] = {t: [] for t in CATEGORY_ORDER}
    for entry in entries:
        entry_type = entry["type"]
        groups[entry_type].append(entry)
    return groups


def format_markdown(
    groups: dict[str, list[dict]],
    product_name: str,
    version: str,
    release_date: str,
    warnings: dict[str, list[str]],
) -> str:
    """Format grouped entries as markdown release notes."""
    lines = []
    lines.append(f"# {product_name} v{version} Release Notes")
    lines.append("")
    lines.append(f"**Release Date:** {release_date}")
    lines.append("")
    lines.append("---")

    for entry_type in CATEGORY_ORDER:
        entries = groups[entry_type]
        if not entries:
            continue

        lines.append("")
        category_name = CATEGORY_MAP[entry_type]
        lines.append(f"## {category_name}")
        lines.append("")

        if entry_type == "breaking":
            lines.append("> **Action Required:** The following changes require updates on your end.")
            lines.append("")
        elif entry_type == "deprecation":
            lines.append("> **Planned Removal:** The following features will be removed in a future release.")
            lines.append("")

        for entry in entries:
            ticket = f" ({entry['ticket_id']})" if entry.get("ticket_id") else ""
            lines.append(f"- **{entry['title']}** -- {entry['description']}{ticket}")

        lines.append("")

    # Append rewriting warnings if any
    warning_entries = {k: v for k, v in warnings.items() if v}
    if warning_entries:
        lines.append("---")
        lines.append("")
        lines.append("## Rewriting Suggestions")
        lines.append("")
        lines.append("The following entries may contain technical language. Consider rewriting to focus on user benefit.")
        lines.append("")
        for title, title_warnings in warning_entries.items():
            lines.append(f"- **{title}**")
            for w in title_warnings:
                lines.append(f"  - {w}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**Full changelog:** [link]")
    lines.append("**Questions?** [support link or contact]")
    lines.append("")

    return "\n".join(lines)


def format_json(
    groups: dict[str, list[dict]],
    product_name: str,
    version: str,
    release_date: str,
    warnings: dict[str, list[str]],
) -> str:
    """Format grouped entries as JSON output."""
    output = {
        "product_name": product_name,
        "version": version,
        "release_date": release_date,
        "categories": {},
        "rewriting_suggestions": {},
    }

    for entry_type in CATEGORY_ORDER:
        entries = groups[entry_type]
        if entries:
            output["categories"][CATEGORY_MAP[entry_type]] = [
                {
                    "title": e["title"],
                    "description": e["description"],
                    "ticket_id": e.get("ticket_id", ""),
                }
                for e in entries
            ]

    warning_entries = {k: v for k, v in warnings.items() if v}
    if warning_entries:
        output["rewriting_suggestions"] = warning_entries

    return json.dumps(output, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate formatted release notes from structured JSON input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Input JSON format:\n"
            '  { "entries": [\n'
            '    { "title": "...", "description": "...", "type": "feature", "ticket_id": "PROJ-1" }\n'
            "  ]}\n\n"
            "Supported types: feature, improvement, bugfix, breaking, deprecation\n\n"
            "Examples:\n"
            '  %(prog)s --input changes.json --product-name "Acme" --version "2.0.0"\n'
            '  %(prog)s --demo --product-name "Acme" --version "1.0.0"\n'
            '  %(prog)s --input changes.json --format json --product-name "Acme" --version "2.0.0"'
        ),
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Path to JSON file containing release entries",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with built-in demo data",
    )
    parser.add_argument(
        "--product-name",
        type=str,
        required=True,
        help="Product name for the release notes header",
    )
    parser.add_argument(
        "--version",
        type=str,
        required=True,
        help="Version string (e.g., 2.5.0)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format: 'text' for markdown (default), 'json' for structured JSON",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Release date in YYYY-MM-DD format (defaults to today)",
    )

    args = parser.parse_args()

    if not args.input and not args.demo:
        parser.error("Provide --input <file> or --demo")

    # Load data
    if args.demo:
        data = DEMO_DATA
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

    entries = data.get("entries", [])
    if not entries:
        print("Error: No entries found in input data.", file=sys.stderr)
        sys.exit(1)

    # Validate
    errors = validate_entries(entries)
    if errors:
        print("Validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # Check for technical language
    warnings: dict[str, list[str]] = {}
    for entry in entries:
        entry_warnings = check_technical_language(entry["description"])
        if entry_warnings:
            warnings[entry["title"]] = entry_warnings

    # Group and format
    groups = group_entries(entries)
    release_date = args.date or date.today().isoformat()

    if args.format == "json":
        output = format_json(groups, args.product_name, args.version, release_date, warnings)
    else:
        output = format_markdown(groups, args.product_name, args.version, release_date, warnings)

    print(output)


if __name__ == "__main__":
    main()
