#!/usr/bin/env python3
"""
regulatory_calendar_generator.py — Build a date-ordered regulatory calendar
from a JSON of regimes, applicable jurisdictions, and known dates.

Reads a JSON of regulatory items (filings, notification windows, renewals,
effective dates, audits); orders by date; computes "days until"; produces
calendar with owner, action, and urgency tag.

Stdlib only. JSON or markdown output.

Usage:
    python3 regulatory_calendar_generator.py --input regulatory_inputs.json
    python3 regulatory_calendar_generator.py --input regulatory_inputs.json --format markdown
    python3 regulatory_calendar_generator.py --input regulatory_inputs.json --horizon-days 365

Input schema:
{
  "as_of": "2026-05-27",
  "org_name": "Acme",
  "items": [
      {
          "id": "REG-001",
          "regime": "EU AI Act",
          "jurisdiction": "EU",
          "item_type": "effective_date",      # filing|notification_window|renewal|effective_date|audit|internal_deadline
          "title": "High-risk AI obligations apply",
          "date": "2027-12-02",
          "owner": "GC + CAIO",
          "action_required": "Complete conformity assessment for in-scope systems",
          "criticality": "high",              # low|medium|high|critical
          "recurring": false,
          "recurrence_months": 0,
          "notes": "Annex III high-risk obligations effective (moved from 2026-08-02 by Reg. 2026/1744)"
      }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


VALID_TYPES = {
    "filing", "notification_window", "renewal", "effective_date",
    "audit", "internal_deadline", "examination",
}


def parse_date(s: str | None) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def days_until(target: date | None, today: date) -> int | None:
    return (target - today).days if target else None


def urgency_for(days: int | None, criticality: str) -> str:
    if days is None:
        return "unknown"
    if days < 0:
        return "overdue"
    crit = criticality.lower()
    if days <= 14:
        return "imminent"
    if days <= 60:
        return "near-term" if crit != "critical" else "imminent"
    if days <= 180:
        return "mid-term" if crit not in ("high", "critical") else "near-term"
    return "long-term"


def expand_recurring(item: dict[str, Any], today: date, horizon: date) -> list[dict[str, Any]]:
    if not item.get("recurring"):
        return [item]
    months = int(item.get("recurrence_months", 0) or 0)
    if months <= 0:
        return [item]
    d = parse_date(item.get("date"))
    if not d:
        return [item]
    out = []
    current = d
    # Skip past dates entirely if first occurrence is older than 30 days
    iterations = 0
    while current <= horizon and iterations < 60:
        if current >= today - timedelta(days=30):
            out.append({**item, "date": current.isoformat()})
        # Approximate month addition
        new_month = current.month + months
        new_year = current.year + (new_month - 1) // 12
        new_month = ((new_month - 1) % 12) + 1
        try:
            current = current.replace(year=new_year, month=new_month)
        except ValueError:
            # Day doesn't exist in target month (e.g., Jan 31 + 1 month)
            current = current.replace(year=new_year, month=new_month, day=28)
        iterations += 1
    return out or [item]


def build_calendar(state: dict[str, Any], horizon_days: int) -> dict[str, Any]:
    as_of_str = state.get("as_of", "")
    today = parse_date(as_of_str) or date.today()
    horizon = today + timedelta(days=horizon_days)
    raw_items = state.get("items", [])

    expanded: list[dict[str, Any]] = []
    for item in raw_items:
        expanded.extend(expand_recurring(item, today, horizon))

    out: list[dict[str, Any]] = []
    overdue: list[dict[str, Any]] = []
    upcoming: list[dict[str, Any]] = []
    by_regime: dict[str, int] = {}

    for it in expanded:
        d = parse_date(it.get("date"))
        days = days_until(d, today)
        crit = (it.get("criticality") or "medium").lower()
        urgency = urgency_for(days, crit)
        itype = it.get("item_type", "filing").lower()
        if itype not in VALID_TYPES:
            itype = "filing"
        row = {
            "id": it.get("id", ""),
            "regime": it.get("regime", ""),
            "jurisdiction": it.get("jurisdiction", ""),
            "item_type": itype,
            "title": it.get("title", ""),
            "date": d.isoformat() if d else "",
            "days_until": days,
            "owner": it.get("owner", "GC"),
            "action_required": it.get("action_required", ""),
            "criticality": crit,
            "urgency": urgency,
            "notes": it.get("notes", ""),
        }
        out.append(row)
        by_regime[row["regime"]] = by_regime.get(row["regime"], 0) + 1
        if days is not None and days < 0:
            overdue.append(row)
        elif d and d <= horizon:
            upcoming.append(row)

    out.sort(key=lambda x: (x["days_until"] if x["days_until"] is not None else 99999))
    upcoming.sort(key=lambda x: x["days_until"] if x["days_until"] is not None else 99999)

    return {
        "as_of": as_of_str,
        "org_name": state.get("org_name", ""),
        "horizon_days": horizon_days,
        "total_items": len(out),
        "overdue_count": len(overdue),
        "by_regime": by_regime,
        "calendar": out,
        "overdue": overdue,
        "upcoming": upcoming,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Regulatory Calendar — {report.get('org_name','(unnamed)')}")
    lines.append(f"_as of {report['as_of']} | horizon {report['horizon_days']} days_\n")
    lines.append(f"Total items: {report['total_items']} | Overdue: {report['overdue_count']}")
    lines.append("\nBy regime: " + ", ".join(f"{k} ({v})" for k, v in sorted(report["by_regime"].items())))
    lines.append("")

    if report["overdue"]:
        lines.append("## Overdue (immediate action)")
        lines.append("| Date | Regime | Item | Owner | Action |")
        lines.append("|------|--------|------|-------|--------|")
        for r in report["overdue"]:
            lines.append(f"| {r['date']} ({r['days_until']}d) | {r['regime']} | "
                        f"{r['title']} | {r['owner']} | {r['action_required']} |")
        lines.append("")

    lines.append("## Upcoming items (date-ordered)")
    lines.append("| Days | Date | Urgency | Regime | Item | Owner |")
    lines.append("|------|------|---------|--------|------|-------|")
    for r in report["upcoming"]:
        lines.append(f"| {r['days_until']} | {r['date']} | {r['urgency']} | {r['regime']} | "
                    f"{r['title']} | {r['owner']} |")
    lines.append("")

    lines.append("## Item detail (top 20 nearest)")
    for r in report["upcoming"][:20]:
        lines.append(f"### {r['title']} ({r['id']})")
        lines.append(f"_{r['regime']} | {r['jurisdiction']} | {r['item_type']} | "
                    f"due {r['date']} ({r['days_until']}d) | urgency: {r['urgency']}_")
        if r["action_required"]:
            lines.append(f"\n**Action:** {r['action_required']}")
        lines.append(f"**Owner:** {r['owner']}")
        if r["notes"]:
            lines.append(f"**Notes:** {r['notes']}")
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build a date-ordered regulatory calendar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON of regulatory items")
    p.add_argument("--horizon-days", type=int, default=365)
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.add_argument("--output", help="Write to file instead of stdout")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        state = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"error: cannot read input: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    report = build_calendar(state, args.horizon_days)
    out = render_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
