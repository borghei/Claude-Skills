#!/usr/bin/env python3
"""
Schema Markup Validator

Validates JSON-LD structured data for completeness, required fields,
rich result eligibility, and common errors. Supports both standalone
JSON-LD files and HTML pages with embedded schema.

Usage:
    python schema_validator.py --file schema.json
    python schema_validator.py --html page.html --json
    python schema_validator.py --file schema.json --verbose
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Required and recommended fields per schema type (Google 2026 requirements)
SCHEMA_REQUIREMENTS = {
    "Article": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["dateModified", "image", "publisher", "description"],
        "rich_result": True,
    },
    "FAQPage": {
        "required": ["mainEntity"],
        "recommended": [],
        "rich_result": True,
        "nested_checks": {
            "mainEntity": {
                "type": "Question",
                "required": ["name", "acceptedAnswer"],
            }
        },
    },
    "HowTo": {
        "required": ["name", "step"],
        "recommended": ["image", "totalTime", "description"],
        "rich_result": True,
        "nested_checks": {
            "step": {
                "type": "HowToStep",
                "required": ["name", "text"],
            }
        },
    },
    "Product": {
        "required": ["name", "image"],
        "recommended": ["description", "offers", "aggregateRating", "review"],
        "rich_result": True,
        "nested_checks": {
            "offers": {
                "type": "Offer",
                "required": ["price", "priceCurrency"],
            }
        },
    },
    "Organization": {
        "required": ["name", "url"],
        "recommended": ["logo", "sameAs", "description", "contactPoint"],
        "rich_result": False,
    },
    "Person": {
        "required": ["name"],
        "recommended": ["url", "sameAs", "jobTitle", "image"],
        "rich_result": False,
    },
    "LocalBusiness": {
        "required": ["name", "address"],
        "recommended": ["telephone", "openingHoursSpecification", "geo", "image", "url"],
        "rich_result": True,
    },
    "BreadcrumbList": {
        "required": ["itemListElement"],
        "recommended": [],
        "rich_result": True,
    },
    "VideoObject": {
        "required": ["name", "description", "thumbnailUrl", "uploadDate"],
        "recommended": ["duration", "contentUrl", "embedUrl"],
        "rich_result": True,
    },
    "Event": {
        "required": ["name", "startDate", "location"],
        "recommended": ["endDate", "description", "image", "offers", "organizer"],
        "rich_result": True,
    },
    "WebSite": {
        "required": ["name", "url"],
        "recommended": ["potentialAction"],
        "rich_result": False,
    },
    "Course": {
        "required": ["name", "description", "provider"],
        "recommended": ["offers", "hasCourseInstance"],
        "rich_result": True,
    },
    "SoftwareApplication": {
        "required": ["name", "operatingSystem"],
        "recommended": ["offers", "aggregateRating", "applicationCategory"],
        "rich_result": True,
    },
    "Review": {
        "required": ["itemReviewed", "reviewRating", "author"],
        "recommended": ["datePublished", "reviewBody"],
        "rich_result": True,
    },
    "JobPosting": {
        "required": ["title", "description", "datePosted", "hiringOrganization"],
        "recommended": ["validThrough", "employmentType", "jobLocation", "baseSalary"],
        "rich_result": True,
    },
    "Dataset": {
        "required": ["name", "description"],
        "recommended": ["url", "creator", "license", "distribution"],
        "rich_result": True,
    },
}


def extract_jsonld_from_html(html):
    """Extract JSON-LD blocks from HTML."""
    blocks = []
    pattern = r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>'
    matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
    for match in matches:
        try:
            data = json.loads(match.strip())
            blocks.append(data)
        except json.JSONDecodeError as e:
            blocks.append({"_parse_error": str(e), "_raw": match.strip()[:200]})
    return blocks


def validate_schema_block(schema, path="root"):
    """Validate a single schema block."""
    issues = []

    # Check for parse errors
    if "_parse_error" in schema:
        return [{
            "type": "json_parse_error",
            "severity": "Critical",
            "path": path,
            "detail": f"JSON parse error: {schema['_parse_error']}",
        }]

    # Check @context
    context = schema.get("@context", "")
    if "schema.org" not in str(context):
        issues.append({
            "type": "missing_context",
            "severity": "Critical",
            "path": path,
            "detail": "Missing @context with schema.org",
        })

    # Handle @graph
    if "@graph" in schema:
        for i, item in enumerate(schema["@graph"]):
            issues.extend(validate_schema_block(item, f"{path}.@graph[{i}]"))
        return issues

    # Get type
    schema_type = schema.get("@type", "")
    if not schema_type:
        issues.append({
            "type": "missing_type",
            "severity": "Critical",
            "path": path,
            "detail": "Missing @type property",
        })
        return issues

    # Look up requirements
    reqs = SCHEMA_REQUIREMENTS.get(schema_type)
    if not reqs:
        issues.append({
            "type": "unknown_type",
            "severity": "Low",
            "path": path,
            "detail": f"Type '{schema_type}' not in validation rules — may still be valid schema.org",
        })
        return issues

    # Check required fields
    for field in reqs["required"]:
        value = schema.get(field)
        if value is None or value == "" or value == []:
            issues.append({
                "type": "missing_required",
                "severity": "Critical",
                "path": f"{path}.{field}",
                "detail": f"Required field '{field}' is missing for {schema_type}",
            })

    # Check recommended fields
    for field in reqs["recommended"]:
        value = schema.get(field)
        if value is None or value == "" or value == []:
            issues.append({
                "type": "missing_recommended",
                "severity": "Medium",
                "path": f"{path}.{field}",
                "detail": f"Recommended field '{field}' is missing for {schema_type}",
            })

    # Check nested types
    if "nested_checks" in reqs:
        for field, nested_req in reqs["nested_checks"].items():
            value = schema.get(field)
            if value:
                items = value if isinstance(value, list) else [value]
                for i, item in enumerate(items):
                    if isinstance(item, dict):
                        for req_field in nested_req.get("required", []):
                            if not item.get(req_field):
                                issues.append({
                                    "type": "missing_nested_required",
                                    "severity": "High",
                                    "path": f"{path}.{field}[{i}].{req_field}",
                                    "detail": f"Required nested field '{req_field}' missing in {nested_req['type']}",
                                })

    # Common content checks
    if "datePublished" in schema and "dateModified" in schema:
        dp = schema["datePublished"]
        dm = schema["dateModified"]
        if dp and dm and str(dm) < str(dp):
            issues.append({
                "type": "date_error",
                "severity": "High",
                "path": f"{path}",
                "detail": f"dateModified ({dm}) is before datePublished ({dp})",
            })

    # Check for empty strings
    for key, value in schema.items():
        if key.startswith("@"):
            continue
        if value == "":
            issues.append({
                "type": "empty_value",
                "severity": "Medium",
                "path": f"{path}.{key}",
                "detail": f"Field '{key}' has empty string value — use real content or remove",
            })

    # Check image URLs are absolute
    for img_field in ["image", "thumbnailUrl", "logo"]:
        img = schema.get(img_field)
        if isinstance(img, str) and img and not img.startswith(("http://", "https://")):
            issues.append({
                "type": "relative_url",
                "severity": "High",
                "path": f"{path}.{img_field}",
                "detail": f"Image URL is relative: '{img}' — must be absolute",
            })
        elif isinstance(img, dict):
            url = img.get("url", "")
            if url and not url.startswith(("http://", "https://")):
                issues.append({
                    "type": "relative_url",
                    "severity": "High",
                    "path": f"{path}.{img_field}.url",
                    "detail": f"Image URL is relative: '{url}' — must be absolute",
                })

    return issues


def score_schema(issues, schema_type):
    """Calculate schema quality score 0-100."""
    if not schema_type:
        return 0

    severity_weights = {"Critical": 20, "High": 10, "Medium": 5, "Low": 2}
    total_penalty = sum(severity_weights.get(i["severity"], 0) for i in issues)
    score = max(0, 100 - total_penalty)
    return score


def main():
    parser = argparse.ArgumentParser(
        description="Validate JSON-LD structured data"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="JSON-LD file to validate")
    group.add_argument("--html", help="HTML file to extract and validate schema from")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", action="store_true", help="Show all check details")
    args = parser.parse_args()

    schemas = []

    if args.file:
        fp = Path(args.file)
        if not fp.exists():
            print(f"Error: {fp} not found", file=sys.stderr)
            sys.exit(1)
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            schemas = [data] if not isinstance(data, list) else data
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.html:
        fp = Path(args.html)
        if not fp.exists():
            print(f"Error: {fp} not found", file=sys.stderr)
            sys.exit(1)
        html = fp.read_text(encoding="utf-8", errors="replace")
        schemas = extract_jsonld_from_html(html)
        if not schemas:
            if args.json:
                print(json.dumps({"error": "No JSON-LD blocks found in HTML"}, indent=2))
            else:
                print("\n  No JSON-LD structured data found in the HTML file.\n")
            sys.exit(0)

    results = []
    for i, schema in enumerate(schemas):
        schema_type = schema.get("@type", "unknown")
        issues = validate_schema_block(schema)
        score = score_schema(issues, schema_type)
        reqs = SCHEMA_REQUIREMENTS.get(schema_type, {})

        results.append({
            "index": i,
            "type": schema_type,
            "score": score,
            "rich_result_eligible": reqs.get("rich_result", False),
            "issues": issues,
            "issue_count": len(issues),
            "critical_count": sum(1 for x in issues if x["severity"] == "Critical"),
            "passed": all(x["severity"] not in ("Critical",) for x in issues),
        })

    output = {
        "source": args.file or args.html,
        "schema_blocks": len(results),
        "results": results,
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  SCHEMA VALIDATION — {len(results)} block(s)")
        print(f"{'='*60}")

        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            rich = " (rich result eligible)" if r["rich_result_eligible"] else ""
            print(f"\n  Block #{r['index'] + 1}: {r['type']}{rich}")
            print(f"  Score: {r['score']}/100 [{status}]")
            print(f"  Issues: {r['issue_count']} (Critical: {r['critical_count']})")

            if r["issues"] and (args.verbose or r["critical_count"] > 0):
                for issue in r["issues"]:
                    print(f"    [{issue['severity']}] {issue['path']}: {issue['detail']}")

        total_pass = sum(1 for r in results if r["passed"])
        print(f"\n  Overall: {total_pass}/{len(results)} blocks passed validation")
        print()


if __name__ == "__main__":
    main()
