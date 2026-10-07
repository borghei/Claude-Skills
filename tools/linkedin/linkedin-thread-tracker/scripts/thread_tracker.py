#!/usr/bin/env python3
"""Report on the local log of LinkedIn comments: replies, follow-ups, dead threads.

Reads the JSON log kept by thread_log.py, works out the state of every thread
(whose turn it is and how long it has been), lists what needs doing today,
names the threads to close, and computes reply rates. Offline: it reads one
local file and never fetches, posts or scrapes.

Usage:
    python3 thread_tracker.py --log assets/sample_thread_log.json \
        --as-of 2026-10-07T09:00:00+00:00
    python3 thread_tracker.py --log my_threads.json --actionable --format json
    python3 thread_tracker.py --log my_threads.json --fail-on-overdue

Exit codes:
    0  report produced
    1  gate failed: --fail-on-overdue set and at least one reply is overdue
    2  bad input: missing or invalid log, bad timestamp, bad threshold
"""

import argparse
import json
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from thread_log import fail, parse_time, problems, read_log  # noqa: E402

# Display order doubles as urgency order.
STATES: List[str] = ["overdue", "your-turn", "lapsed", "watching", "awaiting",
                     "quiet", "settled", "dead", "closed"]
ACTIONABLE = {"overdue", "your-turn", "lapsed"}
HOUSEKEEPING = {"settled", "dead"}
# Heuristic defaults. None of these is a platform rule; tune them with flags.
DEFAULTS: Dict[str, float] = {"reply_due_hours": 24, "lapsed_days": 5, "watch_days": 4,
                              "settle_days": 4, "dead_days": 14, "round_cap": 2}


def classify(thread: Dict[str, Any], as_of: datetime,
             limits: Dict[str, float]) -> Dict[str, Any]:
    """Derive one thread's state, idle time, due time and recommended action."""
    commented = parse_time(thread["commented_at"])
    events = thread.get("events", []) or []
    last = events[-1] if events else None
    last_at = parse_time(last["at"]) if last else commented
    idle = max(0.0, (as_of - last_at).total_seconds() / 3600)
    rounds = sum(1 for e in events if e["who"] == "me")
    author_replies = [e for e in events if e["who"] == "author"]
    last_from = (last.get("name") or ("the author" if last["who"] == "author" else
                                      "you" if last["who"] == "me" else "another commenter")
                 ) if last else "nobody"
    due: Optional[datetime] = None

    if thread.get("closed"):
        state, advice = "closed", f"Closed: {thread['closed'].get('reason', 'no reason given')}."
    elif last is None:
        if idle <= limits["watch_days"] * 24:
            state, advice = "watching", "Nothing to do. Look again at your next check."
        elif idle <= limits["dead_days"] * 24:
            state, advice = "quiet", "No response. Stop checking; do not add a second comment."
        else:
            state, advice = "dead", "Close it. The post is past the point of being read."
    elif last["who"] == "me":
        if idle <= limits["settle_days"] * 24:
            state, advice = "awaiting", "You answered last. Do not reply again until they do."
        else:
            state, advice = "settled", "The exchange has ended. Close it."
    else:
        due = last_at + timedelta(hours=limits["reply_due_hours"])
        closing = " This would be round %d — make it a closing line." % (rounds + 1) \
            if rounds >= limits["round_cap"] else ""
        if idle <= limits["reply_due_hours"]:
            state = "your-turn"
            advice = f"Reply to {last_from} by {due.strftime('%a %d %b %H:%M')}.{closing}"
        elif idle <= limits["lapsed_days"] * 24:
            state = "overdue"
            advice = (f"Reply to {last_from} today; one clause for the delay, "
                      f"then the answer.{closing}")
        elif last["who"] == "author":
            state = "lapsed"
            advice = ("Too late for a public reply to read naturally. Send a short direct "
                      "message that refers to the exchange, or close.")
        else:
            state, advice = "lapsed", "Too late to answer in the thread. Close it."

    first_reply = None
    if author_replies:
        first_reply = round((parse_time(author_replies[0]["at"]) - commented)
                            .total_seconds() / 3600, 1)
    return {"id": thread["id"], "post_author": thread["post_author"],
            "tier": thread.get("tier", "standard"),
            "topic": thread.get("post_topic", ""), "state": state,
            "idle_hours": round(idle, 1), "last_from": last_from,
            "last_note": (last or {}).get("note", ""), "rounds": rounds,
            "due_by": due.isoformat() if due else None,
            "author_replied": bool(author_replies), "anyone_replied":
                any(e["who"] != "me" for e in events),
            "hours_to_author_reply": first_reply,
            "commented_at": commented.isoformat(), "advice": advice}


def rate(part: int, whole: int) -> Optional[float]:
    """Return part/whole as a percentage rounded to one place, or None when empty."""
    return round(100 * part / whole, 1) if whole else None


def build_report(log: Dict[str, Any], as_of: datetime, limits: Dict[str, float],
                 window_days: int) -> Dict[str, Any]:
    """Classify every thread and assemble states, actions, housekeeping and metrics."""
    rows = [classify(t, as_of, limits) for t in log["threads"]]
    rows.sort(key=lambda r: (STATES.index(r["state"]), r["tier"] != "priority",
                             -r["idle_hours"], r["id"]))
    counts = {state: sum(1 for r in rows if r["state"] == state) for state in STATES}
    cutoff = as_of - timedelta(days=window_days)
    recent = [r for r in rows if parse_time(r["commented_at"]) >= cutoff]
    priority = [r for r in recent if r["tier"] == "priority"]
    waits = [r["hours_to_author_reply"] for r in recent
             if r["hours_to_author_reply"] is not None]
    metrics = {
        "window_days": window_days, "comments_logged": len(recent),
        "author_replied": sum(1 for r in recent if r["author_replied"]),
        "author_reply_rate_pct": rate(sum(1 for r in recent if r["author_replied"]),
                                      len(recent)),
        "any_reply_rate_pct": rate(sum(1 for r in recent if r["anyone_replied"]),
                                   len(recent)),
        "priority_author_reply_rate_pct": rate(
            sum(1 for r in priority if r["author_replied"]), len(priority)),
        "median_hours_to_author_reply": round(statistics.median(waits), 1) if waits else None,
        "replies_you_left_unanswered": counts["lapsed"],
    }
    return {"owner": log.get("owner", "unknown"), "as_of": as_of.isoformat(),
            "threads": len(rows), "counts": counts, "metrics": metrics,
            "close_now": [r["id"] for r in rows if r["state"] in HOUSEKEEPING],
            "rows": rows}


def output(report: Dict[str, Any], fmt: str, actionable: bool) -> None:
    """Print the tracker report as JSON or human-readable text."""
    rows = [r for r in report["rows"] if not actionable or r["state"] in ACTIONABLE]
    if fmt == "json":
        print(json.dumps({**report, "rows": rows}, indent=2, ensure_ascii=False))
        return
    counts, metrics = report["counts"], report["metrics"]
    print(f"Thread tracker — {report['owner']}   as of {report['as_of']}")
    print(f"{report['threads']} threads   "
          + "   ".join(f"{s}: {counts[s]}" for s in STATES if counts[s]))
    print("=" * 78)
    current = ""
    for row in rows:
        if row["state"] != current:
            current = row["state"]
            print(current.upper())
        mark = "*" if row["tier"] == "priority" else " "
        print(f" {mark}{row['id']:<6} {row['post_author']} — {row['topic']}")
        if row["last_from"] == "nobody":
            print(f"         no reply yet; you commented {row['idle_hours']}h ago")
        else:
            print(f"         last turn: {row['last_from']}, {row['idle_hours']}h ago"
                  + (f" — \"{row['last_note']}\"" if row["last_note"] else ""))
        print(f"         do: {row['advice']}")
    if not rows:
        print("Nothing needs a reply.")
    print("-" * 78)
    if report["close_now"]:
        print(f"Close now: {', '.join(report['close_now'])}")

    def show(value: Optional[float], unit: str) -> str:
        """Format a metric that may be absent."""
        return f"{value}{unit}" if value is not None else "n/a"

    print(f"Last {metrics['window_days']} days: {metrics['comments_logged']} comments, "
          f"author replied to {metrics['author_replied']} "
          f"({show(metrics['author_reply_rate_pct'], '%')}); priority tier "
          f"{show(metrics['priority_author_reply_rate_pct'], '%')}; any reply "
          f"{show(metrics['any_reply_rate_pct'], '%')}; median wait for the author "
          f"{show(metrics['median_hours_to_author_reply'], 'h')}; "
          f"replies you never answered: {metrics['replies_you_left_unanswered']}")
    print("* = priority tier")


def main() -> None:
    """Parse arguments, build the report, print it and apply the optional gate."""
    parser = argparse.ArgumentParser(
        description="Report on the local log of LinkedIn comments you left: who "
                    "replied, which follow-ups are due or overdue, which threads "
                    "to close. Offline: reads one local JSON file.",
        epilog="Exit codes: 0 report produced, 1 --fail-on-overdue and a reply is "
               "overdue, 2 bad input. Thresholds are heuristics; tune them.")
    parser.add_argument("--log", required=True, help="Path to the local thread log (JSON).")
    parser.add_argument("--as-of", default=None,
                        help="ISO 8601 time to report from (default: now, UTC). "
                             "Pass it for reproducible output.")
    parser.add_argument("--reply-due-hours", type=float, default=DEFAULTS["reply_due_hours"],
                        help="Hours you allow yourself to answer a reply (default: %(default)g).")
    parser.add_argument("--lapsed-days", type=float, default=DEFAULTS["lapsed_days"],
                        help="Days after which an unanswered reply is past a public "
                             "answer (default: %(default)g).")
    parser.add_argument("--watch-days", type=float, default=DEFAULTS["watch_days"],
                        help="Days to keep checking a comment with no reply (default: %(default)g).")
    parser.add_argument("--settle-days", type=float, default=DEFAULTS["settle_days"],
                        help="Days of silence after your answer before the thread "
                             "counts as finished (default: %(default)g).")
    parser.add_argument("--dead-days", type=float, default=DEFAULTS["dead_days"],
                        help="Days after which an unanswered comment is dead (default: %(default)g).")
    parser.add_argument("--window-days", type=int, default=30,
                        help="Look-back window for the reply-rate metrics (default: %(default)s).")
    parser.add_argument("--actionable", action="store_true",
                        help="Show only threads that need something from you.")
    parser.add_argument("--fail-on-overdue", action="store_true",
                        help="Exit 1 when any reply is overdue.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()

    limits = dict(DEFAULTS, reply_due_hours=args.reply_due_hours,
                  lapsed_days=args.lapsed_days, watch_days=args.watch_days,
                  settle_days=args.settle_days, dead_days=args.dead_days)
    if min(limits.values()) <= 0 or args.window_days <= 0:
        fail("every threshold must be greater than zero.")
    if limits["reply_due_hours"] >= limits["lapsed_days"] * 24 \
            or limits["watch_days"] >= limits["dead_days"]:
        fail("thresholds are out of order: --reply-due-hours must be shorter than "
             "--lapsed-days, and --watch-days shorter than --dead-days.")
    try:
        as_of = parse_time(args.as_of) if args.as_of else datetime.now(timezone.utc)
    except ValueError:
        fail(f"--as-of is not an ISO 8601 timestamp: '{args.as_of}'. "
             f"Use a form like 2026-10-07T09:00:00+00:00.")

    log = read_log(Path(args.log))
    issues = problems(log)
    if issues:
        fail(f"the log has {len(issues)} structural problem(s), first: {issues[0]}. "
             f"Run thread_log.py validate --log {args.log} for the full list.")
    report = build_report(log, as_of, limits, args.window_days)
    output(report, args.format, args.actionable)
    if args.fail_on_overdue and report["counts"]["overdue"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
