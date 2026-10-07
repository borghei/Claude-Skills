#!/usr/bin/env python3
"""Create, update and validate the local log of LinkedIn comments you have left.

The log is a JSON file on your own disk. This tool adds a comment you posted,
records a reply you saw (from the post's author, from someone else, or your
own answer), closes a thread, and checks the file's structure. It is the only
writer the thread tracker needs. Offline: it never fetches, posts or scrapes.

Usage:
    python3 thread_log.py init --log my_threads.json --owner "Your Name"
    python3 thread_log.py add --log my_threads.json --post-author "Ilse Vandermeer" \
        --topic "Dropping the kickoff call" --comment "The enterprise split..." --tier priority
    python3 thread_log.py event --log my_threads.json --id T-003 --who author \
        --note "Asked whether we kept the call for regulated accounts"
    python3 thread_log.py close --log my_threads.json --id T-003 --reason "Settled"
    python3 thread_log.py validate --log assets/sample_thread_log.json --format json

Exit codes:
    0  change written (or shown with --dry-run), or log valid
    1  gate failed: validate found structural problems in the log
    2  bad input: missing or unreadable file, invalid JSON, unknown id, bad timestamp
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

WHO = ("author", "other", "me")
TIERS = ("priority", "standard")


def fail(message: str) -> None:
    """Print an actionable input error to stderr and exit with status 2."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def parse_time(value: Any) -> datetime:
    """Parse an ISO 8601 timestamp into an aware datetime; raise ValueError if bad."""
    parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def stamp(value: Optional[str]) -> str:
    """Return a validated ISO timestamp from a flag, or the current UTC time."""
    if value is None:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    try:
        return parse_time(value).isoformat()
    except ValueError:
        fail(f"--at is not an ISO 8601 timestamp: '{value}'. "
             f"Use a form like 2026-10-05T09:30:00+00:00.")
    return ""


def read_log(path: Path) -> Dict[str, Any]:
    """Read the log file, exiting 2 when it is missing, unreadable or not JSON."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"log not found: {path}. Create one with: thread_log.py init "
             f"--log {path} --owner \"Your Name\"")
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON (line {exc.lineno}): {exc.msg}")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"could not read {path}: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("threads"), list):
        fail(f"{path} must be a JSON object with a 'threads' array. "
             f"See assets/thread_log_template.json.")
    return data


def problems(log: Dict[str, Any]) -> List[str]:
    """Return every structural problem found in the log, as readable sentences."""
    found: List[str] = []
    seen: set = set()
    for index, thread in enumerate(log["threads"]):
        if not isinstance(thread, dict):
            found.append(f"threads[{index}] is not an object")
            continue
        tid = str(thread.get("id") or f"threads[{index}]")
        for field in ("id", "post_author", "commented_at", "comment"):
            if not str(thread.get(field, "")).strip():
                found.append(f"{tid}: missing '{field}'")
        if tid in seen:
            found.append(f"{tid}: id used more than once")
        seen.add(tid)
        if thread.get("tier", "standard") not in TIERS:
            found.append(f"{tid}: tier must be one of {', '.join(TIERS)}")
        try:
            last = parse_time(thread.get("commented_at"))
        except ValueError:
            found.append(f"{tid}: commented_at is not an ISO 8601 timestamp")
            continue
        events = thread.get("events", [])
        if not isinstance(events, list):
            found.append(f"{tid}: 'events' must be an array")
            continue
        for number, event in enumerate(events, start=1):
            if not isinstance(event, dict) or event.get("who") not in WHO:
                found.append(f"{tid} event {number}: 'who' must be one of {', '.join(WHO)}")
                continue
            try:
                when = parse_time(event.get("at"))
            except ValueError:
                found.append(f"{tid} event {number}: 'at' is not an ISO 8601 timestamp")
                continue
            if when < last:
                found.append(f"{tid} event {number}: earlier than the entry before it")
            last = when
        closed = thread.get("closed")
        if closed is not None and (not isinstance(closed, dict)
                                   or not str(closed.get("reason", "")).strip()):
            found.append(f"{tid}: 'closed' needs a 'reason'")
    return found


def write_log(path: Path, log: Dict[str, Any]) -> None:
    """Write the log atomically so an interrupted run cannot truncate it."""
    temp = path.with_suffix(path.suffix + ".tmp")
    try:
        temp.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        os.replace(temp, path)
    except OSError as exc:
        fail(f"could not write {path}: {exc}")


def find_thread(log: Dict[str, Any], tid: str) -> Dict[str, Any]:
    """Return the thread with the given id, exiting 2 when it does not exist."""
    for thread in log["threads"]:
        if isinstance(thread, dict) and str(thread.get("id")) == tid:
            return thread
    known = ", ".join(str(t.get("id")) for t in log["threads"][-8:] if isinstance(t, dict))
    fail(f"no thread with id '{tid}'. Most recent ids: {known or 'none'}")
    return {}


def apply(args: argparse.Namespace) -> Dict[str, Any]:
    """Carry out the chosen subcommand and return a result record."""
    path = Path(args.log)
    if args.command == "init":
        if path.exists():
            fail(f"{path} already exists; init will not overwrite a log.")
        log: Dict[str, Any] = {"owner": args.owner, "threads": []}
        if not args.dry_run:
            write_log(path, log)
        return {"action": "init", "log": str(path), "written": not args.dry_run,
                "detail": f"empty log for {args.owner}"}

    log = read_log(path)
    if args.command == "validate":
        issues = problems(log)
        return {"action": "validate", "log": str(path), "written": False,
                "threads": len(log["threads"]), "problems": issues,
                "detail": "log is valid" if not issues else f"{len(issues)} problem(s)"}

    if args.command == "add":
        numbers = [int(str(t.get("id", ""))[2:]) for t in log["threads"]
                   if isinstance(t, dict) and re.fullmatch(r"[0-9]+", str(t.get("id", ""))[2:])]
        tid = f"T-{max(numbers, default=0) + 1:03d}"
        thread = {"id": tid, "post_author": args.post_author, "tier": args.tier,
                  "post_topic": args.topic, "post_ref": args.ref or "",
                  "commented_at": stamp(args.at), "comment": args.comment, "events": []}
        log["threads"].append(thread)
        detail = f"{tid}: comment on {args.post_author}'s post logged"
    elif args.command == "event":
        thread = find_thread(log, args.id)
        if thread.get("closed"):
            fail(f"{args.id} is closed ({thread['closed'].get('reason')}). "
                 f"Remove its 'closed' entry by hand to reopen it.")
        event = {"at": stamp(args.at), "who": args.who, "note": args.note}
        if args.name:
            event["name"] = args.name
        thread.setdefault("events", []).append(event)
        detail = f"{args.id}: recorded a turn by {args.name or args.who}"
    else:
        thread = find_thread(log, args.id)
        thread["closed"] = {"at": stamp(args.at), "reason": args.reason}
        detail = f"{args.id}: closed — {args.reason}"

    issues = problems(log)
    if issues:
        fail(f"that change would leave the log invalid: {issues[0]}. Nothing written.")
    if not args.dry_run:
        write_log(path, log)
    return {"action": args.command, "log": str(path), "written": not args.dry_run,
            "detail": detail, "thread": thread}


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the result of a subcommand as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    status = "written" if result["written"] else "not written"
    if result["action"] == "validate":
        status = f"{result['threads']} threads checked"
    print(f"{result['action']}: {result['detail']}  [{status}]  {result['log']}")
    for issue in result.get("problems", []):
        print(f"  PROBLEM  {issue}")


def main() -> None:
    """Parse arguments, run the subcommand, print the result and set the exit code."""
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--log", required=True, help="Path to the local thread log (JSON).")
    common.add_argument("--at", default=None,
                        help="ISO 8601 time of the action (default: now, UTC).")
    common.add_argument("--dry-run", action="store_true",
                        help="Show the change without writing the file.")
    common.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser = argparse.ArgumentParser(
        description="Maintain the local log of comments you left on LinkedIn. "
                    "Offline: edits one JSON file on your disk and nothing else.",
        epilog="Exit codes: 0 done or valid, 1 validate found problems, 2 bad input.")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")
    init = sub.add_parser("init", parents=[common], help="Create an empty log.")
    init.add_argument("--owner", required=True, help="Your display name.")
    add = sub.add_parser("add", parents=[common], help="Log a comment you posted.")
    add.add_argument("--post-author", required=True, help="Whose post you commented on.")
    add.add_argument("--topic", required=True, help="What the post was about, in a few words.")
    add.add_argument("--comment", required=True, help="The text of your comment.")
    add.add_argument("--tier", choices=TIERS, default="standard",
                     help="priority for people you most want a reply from (default: standard).")
    add.add_argument("--ref", default=None,
                     help="Free-text pointer to the post for your own use; never opened.")
    event = sub.add_parser("event", parents=[common], help="Record a turn in a thread.")
    event.add_argument("--id", required=True, help="Thread id, for example T-003.")
    event.add_argument("--who", required=True, choices=WHO,
                       help="author = the post's author replied; other = someone else "
                            "replied; me = you answered.")
    event.add_argument("--name", default=None, help="Name of the person, when who=other.")
    event.add_argument("--note", required=True, help="What was said, in a line.")
    close = sub.add_parser("close", parents=[common], help="Close a thread.")
    close.add_argument("--id", required=True, help="Thread id, for example T-003.")
    close.add_argument("--reason", required=True, help="Why it is finished.")
    sub.add_parser("validate", parents=[common], help="Check the log's structure.")
    args = parser.parse_args()

    result = apply(args)
    output(result, args.format)
    if result.get("problems"):
        sys.exit(1)


if __name__ == "__main__":
    main()
