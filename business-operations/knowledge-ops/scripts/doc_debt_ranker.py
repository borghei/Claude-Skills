#!/usr/bin/env python3
"""Rank documentation debt into a prioritised remediation backlog.

Usage:
    python3 doc_debt_ranker.py --input kb.json --as-of 2026-07-21 [--top 10]
                               [--format text|json]

Input JSON shape: the same inventory consumed by kb_health_auditor.py.
Each issue is scored on value (traffic x criticality x severity) and effort,
then bucketed into do-now / schedule / batch / drop.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Any, Dict, List

TIER_SLA = {"critical": (90, 120), "core": (180, 270),
            "reference": (365, 540), "archive": (None, None)}
TIER_WEIGHT = {"critical": 4.0, "core": 2.5, "reference": 1.0, "archive": 0.1}

# issue kind -> (severity weight, effort in hours)
ISSUE_PROFILE: Dict[str, Any] = {
    "stale": (3.0, 3.0),
    "review_overdue": (1.2, 1.0),
    "no_owner": (2.5, 0.25),
    "alias_owner": (1.5, 0.25),
    "duplicate": (2.2, 2.0),
    "orphan": (1.4, 0.5),
    "thin": (1.0, 2.5),
    "no_date": (1.8, 0.25),
}

ISSUE_FIX = {
    "stale": "Owner reviews and re-dates, or archives",
    "review_overdue": "Owner confirms still-accurate; no rewrite expected",
    "no_owner": "Assign a named person (not a team alias)",
    "alias_owner": "Replace the team alias with a named person",
    "duplicate": "Merge into the most-linked path; redirect the losers",
    "orphan": "Link from the correct hub, or delete if traffic is zero",
    "thin": "Expand to answer the question it claims to answer, or merge upward",
    "no_date": "Backfill the last-updated date from version history",
}

ALIAS_HINTS = ("team", "group", "squad", "helpdesk", "support", "ops", "desk")


def parse_date(value: str, field: str) -> date:
    """Parse an ISO-8601 date string, raising a clear error on bad input."""
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD), got: {value!r}")


def collect_issues(docs: List[Dict[str, Any]], as_of: date) -> List[Dict[str, Any]]:
    """Derive the full list of remediation issues from the inventory."""
    titles = Counter(str(d.get("title", "")).strip().lower() for d in docs
                     if str(d.get("title", "")).strip())
    inbound: Dict[str, int] = defaultdict(int)
    known = {str(d.get("path", "")) for d in docs if d.get("path")}
    for doc in docs:
        for target in (doc.get("links_to") or []):
            if str(target) in known and str(target) != str(doc.get("path", "")):
                inbound[str(target)] += 1

    issues: List[Dict[str, Any]] = []
    for doc in docs:
        path = str(doc.get("path", "(no path)"))
        tier = str(doc.get("tier", "reference")).lower()
        if tier not in TIER_SLA:
            tier = "reference"
        views = int(doc.get("views_90d", 0) or 0)
        owner = str(doc.get("owner", "")).strip()
        kinds: List[str] = []

        raw_updated = str(doc.get("updated", "")).strip()
        sla_days, stale_days = TIER_SLA[tier]
        if not raw_updated:
            kinds.append("no_date")
        elif stale_days is not None:
            age = (as_of - parse_date(raw_updated, f"{path} updated")).days
            if age > stale_days:
                kinds.append("stale")
            elif age > sla_days:
                kinds.append("review_overdue")

        if not owner:
            kinds.append("no_owner")
        elif any(h in owner.lower() for h in ALIAS_HINTS) or "@" in owner:
            kinds.append("alias_owner")

        if titles.get(str(doc.get("title", "")).strip().lower(), 0) > 1:
            kinds.append("duplicate")
        if inbound.get(path, 0) == 0 and tier != "archive":
            kinds.append("orphan")
        if int(doc.get("word_count", 0) or 0) < 250 and tier != "archive":
            kinds.append("thin")

        for kind in kinds:
            severity, effort = ISSUE_PROFILE[kind]
            # Traffic is log-ish: cap its influence so one popular page cannot
            # dominate the whole backlog.
            traffic_factor = 1.0 + min(views, 1000) / 250.0
            value = round(severity * TIER_WEIGHT[tier] * traffic_factor, 2)
            issues.append({
                "path": path, "title": doc.get("title", ""), "tier": tier,
                "views_90d": views, "issue": kind, "fix": ISSUE_FIX[kind],
                "value": value, "effort_hours": effort,
                "ratio": round(value / effort, 2),
            })
    return issues


def bucket(issue: Dict[str, Any]) -> str:
    """Assign an issue to a scheduling bucket from its value and effort."""
    if issue["value"] >= 12 and issue["effort_hours"] <= 1.0:
        return "do-now"
    if issue["value"] >= 12:
        return "schedule"
    if issue["effort_hours"] <= 1.0:
        return "batch"
    if issue["value"] < 4:
        return "drop"
    return "schedule"


def rank(docs: List[Dict[str, Any]], as_of: date, top: int) -> Dict[str, Any]:
    """Build the ranked documentation-debt backlog."""
    if not docs:
        raise ValueError("inventory contains no documents")
    issues = collect_issues(docs, as_of)
    for issue in issues:
        issue["bucket"] = bucket(issue)

    def sort_key(issue: Dict[str, Any]) -> Any:
        # A stale critical-tier doc is an incident risk, not a backlog item.
        # It jumps the ratio queue regardless of how expensive the fix is.
        urgent = 0 if (issue["tier"] == "critical"
                       and issue["issue"] in ("stale", "no_date")) else 1
        return (urgent, -issue["ratio"], -issue["value"], issue["path"])

    issues.sort(key=sort_key)

    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        buckets[issue["bucket"]].append(issue)

    sprint = [i for i in issues if i["bucket"] != "drop"][:max(top, 1)]
    return {
        "as_of": as_of.isoformat(),
        "total_issues": len(issues),
        "total_effort_hours": round(sum(i["effort_hours"] for i in issues), 1),
        "bucket_counts": {k: len(v) for k, v in sorted(buckets.items())},
        "bucket_effort_hours": {k: round(sum(i["effort_hours"] for i in v), 1)
                                for k, v in sorted(buckets.items())},
        "sprint": sprint,
        "sprint_effort_hours": round(sum(i["effort_hours"] for i in sprint), 1),
        "droppable_effort_saved_hours": round(
            sum(i["effort_hours"] for i in buckets.get("drop", [])), 1),
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the backlog as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    print(f"Documentation debt backlog as of {result['as_of']}")
    print(f"  {result['total_issues']} issues, "
          f"{result['total_effort_hours']}h total effort")
    print("  buckets: " + "  ".join(
        f"{k}={v} ({result['bucket_effort_hours'][k]}h)"
        for k, v in result["bucket_counts"].items()))
    print(f"  dropping low-value work saves {result['droppable_effort_saved_hours']}h")

    print(f"\nNext sprint ({len(result['sprint'])} items, "
          f"{result['sprint_effort_hours']}h):")
    for i, issue in enumerate(result["sprint"], 1):
        print(f"  {i:>2}. [{issue['bucket']:>8}] {issue['issue']}  {issue['path']}")
        print(f"      {issue['tier']}, {issue['views_90d']} views | "
              f"value={issue['value']} effort={issue['effort_hours']}h "
              f"ratio={issue['ratio']}")
        print(f"      fix: {issue['fix']}")


def main() -> None:
    """Parse arguments, rank the backlog, and emit it."""
    parser = argparse.ArgumentParser(
        description="Rank documentation debt into a prioritised remediation backlog.")
    parser.add_argument("--input", required=True,
                        help="Path to a JSON inventory with a 'docs' array")
    parser.add_argument("--as-of", required=True,
                        help="Reference date as YYYY-MM-DD; required so runs are reproducible")
    parser.add_argument("--top", type=int, default=10,
                        help="How many items to pull into the next sprint (default: 10)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)

    try:
        as_of = parse_date(args.as_of, "--as-of")
        docs = payload.get("docs")
        if not isinstance(docs, list):
            raise ValueError("input JSON must contain a 'docs' array")
        result = rank(docs, as_of, args.top)
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output(result, args.format)


if __name__ == "__main__":
    main()
