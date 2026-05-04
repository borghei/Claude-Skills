#!/usr/bin/env python3
"""
Email Classifier — classify a CSV of email rows into action buckets.

Usage:
    python email_classifier.py inbox.csv
    python email_classifier.py inbox.csv --json

Expected CSV columns: subject, sender, snippet, received_at (optional)
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path


# Patterns suggesting promotional / marketing emails
PROMO_SENDER_PATTERNS = [
    r"@.*(newsletter|marketing|promo|news)\.",
    r"^(noreply|no-reply|donotreply)@",
    r"@.*(notif|notification|update|info|hello|hi)\.",
]
PROMO_SUBJECT_PATTERNS = [
    r"\b(off|sale|deal|discount|free|save|win|earn|exclusive)\b.*[%$]",
    r"^(re:\s*)?(buy|shop|order|now|today|last chance|don't miss)",
    r"\bunsubscribe\b",
    r"\bnewsletter\b",
    r"\b(weekly|daily|monthly) (digest|roundup|update)\b",
    r"^\[.*\]",  # bracketed prefixes commonly used by lists
]
PROMO_SNIPPET_PATTERNS = [
    r"\bunsubscribe\b",
    r"\bview (online|in browser)\b",
    r"\bmanage (preferences|subscription|email)\b",
    r"\bif you'd like to (stop|opt[- ]?out)\b",
]

# Patterns suggesting receipts / confirmations / archive-worthy
ARCHIVE_SUBJECT_PATTERNS = [
    r"\b(receipt|invoice|order (confirmation|confirmed|placed)|payment (received|confirmed))\b",
    r"\b(thank you for your (order|purchase|payment))\b",
    r"\b(your (booking|reservation|ticket|order|trip|flight) (is )?confirmed)\b",
    r"\b(shipped|delivered|tracking)\b",
    r"^(re:\s*)?statement",
]

# Patterns suggesting reply-now (time-sensitive, named-person, direct address)
REPLY_NOW_SUBJECT_PATTERNS = [
    r"\b(urgent|asap|important|action required|time[- ]sensitive)\b",
    r"\b(deadline|due (today|tomorrow|this week))\b",
    r"\?",  # questions in subject often warrant reply
    r"^re:\s*re:",  # already an active thread
]
REPLY_NOW_SNIPPET_PATTERNS = [
    r"\bcan you (please )?(let me know|confirm|approve|review|sign|share)\b",
    r"\bcould you (please )?",
    r"\b(quick|brief) (question|favor|ask)\b",
    r"\bby (today|tomorrow|EOD|EOW|COB)\b",
]

# Spam / delete patterns
SPAM_PATTERNS = [
    r"\b(viagra|crypto giveaway|prince|inheritance|congratulations you've won)\b",
    r"100% (free|guarantee)",
    r"\bclick here\b.*\bnow\b",
]


def matches(text, patterns):
    if not text:
        return False
    return any(re.search(p, text.lower(), re.IGNORECASE) for p in patterns)


def classify_row(row):
    subject = (row.get("subject") or "").strip()
    sender = (row.get("sender") or "").strip().lower()
    snippet = (row.get("snippet") or "").strip()

    # Spam / delete first
    if matches(subject, SPAM_PATTERNS) or matches(snippet, SPAM_PATTERNS):
        return "delete"

    # Promo / unsubscribe candidates
    is_promo = (
        matches(sender, PROMO_SENDER_PATTERNS)
        or matches(subject, PROMO_SUBJECT_PATTERNS)
        or matches(snippet, PROMO_SNIPPET_PATTERNS)
    )

    # Receipts / archive candidates
    is_archive = matches(subject, ARCHIVE_SUBJECT_PATTERNS)

    # Reply-now signals
    is_reply_now = (
        matches(subject, REPLY_NOW_SUBJECT_PATTERNS)
        or matches(snippet, REPLY_NOW_SNIPPET_PATTERNS)
    )

    # Decision tree
    if is_archive and not is_reply_now:
        return "archive"
    if is_promo and not is_reply_now:
        return "unsubscribe"
    if is_reply_now:
        return "reply_now"
    # Default — informational, named sender
    if "@" in sender and not matches(sender, PROMO_SENDER_PATTERNS):
        return "reply_later"
    return "review"


def domain_of(sender):
    if "@" in sender:
        return sender.split("@", 1)[1].split(">")[0].strip().lower()
    return ""


def process(csv_path):
    rows = []
    with Path(csv_path).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {k.lower().strip(): v for k, v in raw.items()}
            row["bucket"] = classify_row(row)
            rows.append(row)

    buckets = {}
    sender_counts = Counter()
    for row in rows:
        buckets.setdefault(row["bucket"], []).append(row)
        sender_counts[domain_of(row.get("sender", ""))] += 1

    # Top recurring senders for unsubscribe consideration
    top_senders = [
        {"domain": d, "count": c}
        for d, c in sender_counts.most_common(15)
        if d
    ]

    return {
        "total": len(rows),
        "buckets": {k: len(v) for k, v in buckets.items()},
        "top_recurring_senders": top_senders,
        "rows_by_bucket": buckets,
    }


def render_human(result):
    lines = [f"Email Triage — processed {result['total']} emails"]
    lines.append("=" * 60)
    lines.append("")
    lines.append("Action buckets:")
    bucket_order = ["reply_now", "reply_later", "archive", "unsubscribe", "delete", "review"]
    for b in bucket_order:
        count = result["buckets"].get(b, 0)
        if count:
            lines.append(f"  {b:<14} {count}")
    lines.append("")
    lines.append("Top recurring sender domains (unsubscribe candidates if marketing):")
    for s in result["top_recurring_senders"]:
        lines.append(f"  {s['domain']:<35} {s['count']}")
    lines.append("")
    lines.append("Suggested order: reply_now → reply_later → archive → unsubscribe → delete")
    if result["buckets"].get("review", 0) > 0:
        lines.append(f"\n{result['buckets']['review']} email(s) need manual review (couldn't classify confidently)")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Classify a CSV of emails into action buckets.")
    parser.add_argument("csv_path", help="Path to inbox CSV (subject, sender, snippet)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not Path(args.csv_path).exists():
        print(f"Error: file not found: {args.csv_path}", file=sys.stderr)
        return 1

    result = process(args.csv_path)
    if args.json:
        # Strip the heavy rows_by_bucket detail from default JSON; keep summary
        summary = {k: v for k, v in result.items() if k != "rows_by_bucket"}
        summary["sample_per_bucket"] = {
            b: [{"subject": r.get("subject", ""), "sender": r.get("sender", "")} for r in rows[:3]]
            for b, rows in result["rows_by_bucket"].items()
        }
        print(json.dumps(summary, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
