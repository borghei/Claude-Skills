#!/usr/bin/env python3
"""
Invoice Categorizer — categorize a CSV of invoices/receipts, detect duplicates,
produce monthly totals per category and per vendor.

Usage:
    python invoice_categorizer.py receipts.csv
    python invoice_categorizer.py receipts.csv --rules my-rules.json
    python invoice_categorizer.py receipts.csv --json
"""

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


DEFAULT_RULES_PATH = Path(__file__).resolve().parent.parent / "assets" / "category_rules.json"


def load_rules(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"rules": []}


def parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%m-%d-%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(s):
    if s is None:
        return 0.0
    cleaned = re.sub(r"[^\d.\-]", "", str(s))
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def categorize(vendor, description, rules):
    haystack = f"{vendor or ''} {description or ''}".lower()
    for rule in rules.get("rules", []):
        for keyword in rule.get("match", []):
            if keyword.lower() in haystack:
                return {
                    "category": rule.get("category", "uncategorized"),
                    "tax_bucket": rule.get("tax_bucket", ""),
                }
    return {"category": "uncategorized", "tax_bucket": ""}


def detect_duplicates(rows, day_window=3):
    """Pairs of rows with same vendor + same amount within `day_window` days."""
    suspect = []
    by_key = defaultdict(list)
    for row in rows:
        key = ((row.get("vendor") or "").strip().lower(), round(row.get("amount", 0.0), 2))
        by_key[key].append(row)
    for (vendor, amt), items in by_key.items():
        if len(items) < 2 or amt == 0:
            continue
        items_sorted = sorted([i for i in items if i.get("date_obj")], key=lambda r: r["date_obj"])
        for i in range(len(items_sorted) - 1):
            a, b = items_sorted[i], items_sorted[i + 1]
            delta = (b["date_obj"] - a["date_obj"]).days
            if delta <= day_window:
                suspect.append({
                    "vendor": vendor,
                    "amount": amt,
                    "first": str(a["date_obj"]),
                    "second": str(b["date_obj"]),
                    "delta_days": delta,
                })
    return suspect


def process(csv_path, rules):
    rows = []
    with Path(csv_path).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {k.lower().strip(): v for k, v in raw.items()}
            row["amount"] = parse_amount(row.get("amount"))
            row["date_obj"] = parse_date(row.get("date"))
            cat = categorize(row.get("vendor"), row.get("description"), rules)
            row["category"] = cat["category"]
            row["tax_bucket"] = cat["tax_bucket"]
            rows.append(row)

    by_category = defaultdict(float)
    by_vendor = defaultdict(float)
    by_month = defaultdict(lambda: defaultdict(float))
    uncategorized = []

    for row in rows:
        amt = row["amount"]
        by_category[row["category"]] += amt
        by_vendor[(row.get("vendor") or "").strip()] += amt
        if row["date_obj"]:
            month_key = row["date_obj"].strftime("%Y-%m")
            by_month[month_key][row["category"]] += amt
        if row["category"] == "uncategorized":
            uncategorized.append({
                "date": str(row["date_obj"]) if row["date_obj"] else "",
                "vendor": row.get("vendor", ""),
                "description": row.get("description", ""),
                "amount": amt,
            })

    duplicates = detect_duplicates(rows)

    return {
        "totals_by_category": [
            {"category": c, "total": round(t, 2)}
            for c, t in sorted(by_category.items(), key=lambda kv: -kv[1])
        ],
        "totals_by_vendor": [
            {"vendor": v, "total": round(t, 2)}
            for v, t in sorted(by_vendor.items(), key=lambda kv: -kv[1])[:25]
        ],
        "totals_by_month": {
            m: [{"category": c, "total": round(t, 2)} for c, t in sorted(cats.items(), key=lambda kv: -kv[1])]
            for m, cats in sorted(by_month.items())
        },
        "uncategorized": uncategorized,
        "duplicates_suspected": duplicates,
        "row_count": len(rows),
    }


def render_human(result):
    lines = []
    lines.append(f"Processed {result['row_count']} rows")
    lines.append("")
    lines.append("Totals by category:")
    for entry in result["totals_by_category"]:
        lines.append(f"  {entry['category']:<24} {entry['total']:>10.2f}")
    lines.append("")
    lines.append("Top vendors:")
    for entry in result["totals_by_vendor"][:10]:
        lines.append(f"  {(entry['vendor'] or '(blank)')[:30]:<32}{entry['total']:>10.2f}")
    if result["totals_by_month"]:
        lines.append("")
        lines.append("By month:")
        for month, cats in result["totals_by_month"].items():
            month_total = sum(c["total"] for c in cats)
            lines.append(f"  {month}: {month_total:>10.2f}")
    if result["uncategorized"]:
        lines.append("")
        lines.append(f"Uncategorized ({len(result['uncategorized'])}) — add rules for these:")
        for row in result["uncategorized"][:10]:
            lines.append(f"  {row['date']:<12}{row['vendor'][:24]:<26}{row['amount']:>10.2f}  {row['description'][:40]}")
        if len(result["uncategorized"]) > 10:
            lines.append(f"  … and {len(result['uncategorized']) - 10} more")
    if result["duplicates_suspected"]:
        lines.append("")
        lines.append(f"Suspected duplicates ({len(result['duplicates_suspected'])}):")
        for d in result["duplicates_suspected"]:
            lines.append(f"  {d['vendor'][:24]:<26}{d['amount']:>10.2f}  {d['first']} ↔ {d['second']} ({d['delta_days']}d)")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Categorize a CSV of invoices/receipts.")
    parser.add_argument("csv_path", help="Path to receipts CSV (date,vendor,description,amount)")
    parser.add_argument("--rules", default=str(DEFAULT_RULES_PATH), help="Path to category_rules.json")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable")
    args = parser.parse_args()

    if not Path(args.csv_path).exists():
        print(f"Error: file not found: {args.csv_path}", file=sys.stderr)
        return 1

    rules = load_rules(args.rules)
    result = process(args.csv_path, rules)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
