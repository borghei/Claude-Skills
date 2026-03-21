#!/usr/bin/env python3
"""
pSEO Data Pipeline Validator

Validates data quality for programmatic SEO page generation. Checks
completeness, uniqueness, minimum content richness, and staleness
against configurable rules.

Usage:
    python data_validator.py --file data.csv --json
    python data_validator.py --file data.csv --rules rules.json
    python data_validator.py --file data.csv --min-fields 5 --min-words 300
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter


def load_csv(filepath):
    """Load CSV data."""
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def load_rules(filepath):
    """Load validation rules from JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)


def check_completeness(rows, required_fields=None):
    """Check data completeness."""
    if not rows:
        return {"pass": False, "detail": "No data rows found"}

    all_fields = list(rows[0].keys())
    if required_fields is None:
        required_fields = all_fields

    issues = []
    field_fill_rates = {}

    for field in required_fields:
        filled = sum(1 for row in rows if row.get(field, '').strip())
        rate = round(filled / len(rows) * 100, 1)
        field_fill_rates[field] = rate

        if rate < 100:
            severity = "Critical" if rate < 50 else "High" if rate < 80 else "Medium"
            issues.append({
                "type": "incomplete_field",
                "field": field,
                "severity": severity,
                "fill_rate": rate,
                "detail": f"Field '{field}' is {rate}% complete ({filled}/{len(rows)} rows)",
            })

    return {
        "total_rows": len(rows),
        "total_fields": len(all_fields),
        "field_fill_rates": field_fill_rates,
        "issues": issues,
    }


def check_uniqueness(rows, key_fields=None):
    """Check for duplicate records."""
    if not rows or not key_fields:
        # Default: use all fields for duplicate detection
        key_fields = list(rows[0].keys()) if rows else []

    issues = []
    seen = Counter()

    for i, row in enumerate(rows):
        key = tuple(row.get(f, '').strip().lower() for f in key_fields)
        seen[key] += 1

    duplicates = {k: v for k, v in seen.items() if v > 1}
    dup_count = sum(v - 1 for v in duplicates.values())

    if dup_count > 0:
        issues.append({
            "type": "duplicate_records",
            "severity": "High",
            "count": dup_count,
            "detail": f"{dup_count} duplicate records found across {len(duplicates)} unique keys",
        })

    return {
        "unique_records": len(seen),
        "duplicate_count": dup_count,
        "duplicate_groups": len(duplicates),
        "issues": issues,
    }


def check_content_richness(rows, min_words=300, text_fields=None):
    """Check content richness per record."""
    if not rows:
        return {"issues": []}

    if text_fields is None:
        # Auto-detect text-heavy fields
        text_fields = []
        for field in rows[0].keys():
            avg_len = sum(len(str(row.get(field, ''))) for row in rows[:10]) / min(len(rows), 10)
            if avg_len > 50:
                text_fields.append(field)

    issues = []
    thin_records = 0
    word_counts = []

    for i, row in enumerate(rows):
        total_words = 0
        for field in (text_fields or rows[0].keys()):
            value = str(row.get(field, ''))
            total_words += len(value.split())

        word_counts.append(total_words)
        if total_words < min_words:
            thin_records += 1

    avg_words = round(sum(word_counts) / max(len(word_counts), 1))
    thin_pct = round(thin_records / len(rows) * 100, 1)

    if thin_records > 0:
        severity = "Critical" if thin_pct > 30 else "High" if thin_pct > 10 else "Medium"
        issues.append({
            "type": "thin_content",
            "severity": severity,
            "count": thin_records,
            "percentage": thin_pct,
            "detail": f"{thin_records} records ({thin_pct}%) have fewer than {min_words} total words",
        })

    return {
        "average_word_count": avg_words,
        "min_word_count": min(word_counts) if word_counts else 0,
        "max_word_count": max(word_counts) if word_counts else 0,
        "thin_records": thin_records,
        "thin_percentage": thin_pct,
        "text_fields_detected": text_fields,
        "issues": issues,
    }


def check_staleness(rows, date_fields=None, max_age_days=90):
    """Check data freshness."""
    if not rows:
        return {"issues": []}

    if date_fields is None:
        # Auto-detect date fields
        date_fields = []
        for field in rows[0].keys():
            if any(d in field.lower() for d in ['date', 'updated', 'modified', 'created', 'time']):
                date_fields.append(field)

    if not date_fields:
        return {
            "date_fields_found": [],
            "issues": [{
                "type": "no_date_fields",
                "severity": "Medium",
                "detail": "No date fields detected — cannot assess data freshness",
            }],
        }

    issues = []
    now = datetime.now()
    threshold = now - timedelta(days=max_age_days)
    stale_count = 0
    date_formats = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]

    for row in rows:
        for field in date_fields:
            val = str(row.get(field, '')).strip()
            if not val:
                continue

            parsed = None
            for fmt in date_formats:
                try:
                    parsed = datetime.strptime(val[:19], fmt)
                    break
                except ValueError:
                    continue

            if parsed and parsed < threshold:
                stale_count += 1
                break

    if stale_count > 0:
        stale_pct = round(stale_count / len(rows) * 100, 1)
        issues.append({
            "type": "stale_data",
            "severity": "High" if stale_pct > 20 else "Medium",
            "count": stale_count,
            "percentage": stale_pct,
            "detail": f"{stale_count} records ({stale_pct}%) have dates older than {max_age_days} days",
        })

    return {
        "date_fields_found": date_fields,
        "stale_records": stale_count,
        "max_age_days": max_age_days,
        "issues": issues,
    }


def calculate_overall(completeness, uniqueness, richness, staleness):
    """Calculate overall data quality score."""
    all_issues = (
        completeness.get("issues", []) +
        uniqueness.get("issues", []) +
        richness.get("issues", []) +
        staleness.get("issues", [])
    )

    score = 100
    for issue in all_issues:
        if issue["severity"] == "Critical":
            score -= 20
        elif issue["severity"] == "High":
            score -= 10
        elif issue["severity"] == "Medium":
            score -= 5

    return max(0, score)


def main():
    parser = argparse.ArgumentParser(
        description="Validate data quality for pSEO page generation"
    )
    parser.add_argument("--file", required=True, help="CSV data file to validate")
    parser.add_argument("--rules", help="JSON rules file for custom validation")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--min-fields", type=int, help="Minimum populated fields per record")
    parser.add_argument("--min-words", type=int, default=300, help="Minimum words per record (default: 300)")
    parser.add_argument("--max-age", type=int, default=90, help="Max data age in days (default: 90)")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    rows = load_csv(fp)
    if not rows:
        print("Error: No data rows found", file=sys.stderr)
        sys.exit(1)

    # Custom rules
    required_fields = None
    key_fields = None
    text_fields = None
    if args.rules:
        rules_fp = Path(args.rules)
        if rules_fp.exists():
            rules = load_rules(rules_fp)
            required_fields = rules.get("required_fields")
            key_fields = rules.get("key_fields")
            text_fields = rules.get("text_fields")

    completeness = check_completeness(rows, required_fields)
    uniqueness = check_uniqueness(rows, key_fields)
    richness = check_content_richness(rows, args.min_words, text_fields)
    staleness = check_staleness(rows, max_age_days=args.max_age)
    overall_score = calculate_overall(completeness, uniqueness, richness, staleness)

    grade = "A" if overall_score >= 85 else "B" if overall_score >= 70 else "C" if overall_score >= 55 else "D" if overall_score >= 40 else "F"

    result = {
        "file": str(fp),
        "total_records": len(rows),
        "overall_score": overall_score,
        "grade": grade,
        "completeness": completeness,
        "uniqueness": uniqueness,
        "content_richness": richness,
        "staleness": staleness,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*55}")
        print(f"  DATA QUALITY SCORE: {overall_score}/100 (Grade: {grade})")
        print(f"{'='*55}")
        print(f"  File: {fp} | Records: {len(rows)}")

        all_issues = (
            completeness.get("issues", []) +
            uniqueness.get("issues", []) +
            richness.get("issues", []) +
            staleness.get("issues", [])
        )

        print(f"\n  Completeness: {len(completeness.get('issues', []))} issues")
        print(f"  Uniqueness: {uniqueness.get('duplicate_count', 0)} duplicates")
        print(f"  Content: avg {richness.get('average_word_count', 0)} words, {richness.get('thin_records', 0)} thin records")
        print(f"  Freshness: {staleness.get('stale_records', 0)} stale records")

        if all_issues:
            print(f"\n  Issues ({len(all_issues)}):")
            for issue in all_issues:
                print(f"    [{issue['severity']}] {issue['detail']}")

        print()


if __name__ == "__main__":
    main()
