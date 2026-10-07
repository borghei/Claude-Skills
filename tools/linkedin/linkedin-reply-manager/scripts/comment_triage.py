#!/usr/bin/env python3
"""Triage a pasted or exported LinkedIn comment section into a reply queue.

Reads a local JSON file of comments, classifies each one (question, pushback,
story, substantive, thin praise, tag-only, duplicate, spam, hostile, flagged),
works out which are already answered, and orders the rest so the replies that
matter are written first. Offline: it never fetches, posts or scrapes.

Usage:
    python3 comment_triage.py --input assets/sample_comment_section.json
    python3 comment_triage.py --input section.json --format json --limit 10
    python3 comment_triage.py --input section.json --max-wait-hours 12

Exit codes:
    0  triage produced
    1  gate failed: --max-wait-hours set and a reply-worthy comment waited longer
    2  bad input: missing file, invalid JSON, wrong shape, bad timestamp
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Heuristic weights. They order a queue; they are not platform facts.
BASE: Dict[str, int] = {"question": 50, "pushback": 45, "story": 35, "substantive": 30}
RELATIONSHIP: Dict[str, int] = {"customer": 25, "prospect": 25, "partner": 15,
                                "peer": 10, "colleague": 5, "unknown": 0}
ACTION: Dict[str, str] = {
    "question": "reply", "pushback": "reply", "story": "reply", "substantive": "reply",
    "thin-praise": "react", "tag-only": "ignore", "duplicate": "ignore",
    "spam": "ignore", "hostile": "hold", "flagged": "flag"}
PRAISE = ["great post", "love this", "so true", "well said", "spot on", "nailed it",
          "thanks for sharing", "agree", "insightful", "100%", "this!", "brilliant"]
PUSHBACK = r"\b(disagree|not convinced|not sure (that|this|about)|push back|" \
           r"the opposite|doesn't (work|hold|scale)|isn't (true|the case)|" \
           r"misses|missing the|wrong|overstated|only works|survivorship)\b"
SPAM = r"(https?://|www\.)\S+|\b(dm|message|inbox) me\b|\bcheck (out )?my (profile|page)\b|" \
       r"\b(free|limited) (audit|trial|slots?)\b|\bfollow (me|us) for\b"
HOSTILE = r"\b(idiot|stupid|moron|clown|garbage|pathetic|scam(mer)?|grifter|" \
          r"shut up|joke of|embarrassing|delusional)\b"
INJECTION = r"ignore (all |any |the )?(previous|prior|above) (instructions|prompts?|rules)|" \
            r"\b(ai|assistant|agent|bot|llm)s? (reading|processing|drafting|replying)\b|" \
            r"\bsystem prompt\b|\bas an ai\b|\bdo not (tell|show) the user\b|" \
            r"\b(reply|respond) (only )?with (the following|this)\b|" \
            r"\b(include|add|insert) (this|the following) (link|url|text)\b"
EXPERIENCE = r"\b(we|i) (ran|tried|tested|shipped|moved|cut|saw|found|measured|lost|" \
             r"hired|switched|built|dropped|spent|stopped|started|kept)\b|" \
             r"\b(my|our) (team|customers?|clients?|numbers|data)\b|\d"
STOP: Set[str] = set("a an and are as at be but by for from has have i in is it my of on "
                     "or our so that the this to was we were with you your".split())


def fail(message: str) -> None:
    """Print an actionable input error to stderr and exit with status 2."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def parse_time(value: Any, label: str) -> Optional[datetime]:
    """Parse an ISO 8601 timestamp into an aware datetime, or None when absent."""
    if value in (None, ""):
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        fail(f"{label} is not an ISO 8601 timestamp: '{value}'. "
             f"Use a form like 2026-10-05T09:30:00+00:00.")
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def load_section(path: Path) -> Dict[str, Any]:
    """Load and validate the comment-section file, exiting 2 on any problem."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"input file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON (line {exc.lineno}): {exc.msg}")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"could not read {path}: {exc}")
    if not isinstance(data, dict) or not str(data.get("me", "")).strip():
        fail("input must be a JSON object with a 'me' field holding your display "
             "name, so your own replies are recognised. See assets/sample_comment_section.json.")
    comments = data.get("comments")
    if not isinstance(comments, list) or not comments:
        fail("input needs a non-empty 'comments' array.")
    seen: Set[str] = set()
    for index, item in enumerate(comments):
        if not isinstance(item, dict) or not item.get("id") or "text" not in item \
                or not item.get("author"):
            fail(f"comments[{index}] needs 'id', 'author' and 'text'.")
        if str(item["id"]) in seen:
            fail(f"duplicate comment id '{item['id']}' — ids must be unique.")
        seen.add(str(item["id"]))
    for item in comments:
        if item.get("parent_id") and str(item["parent_id"]) not in seen:
            fail(f"comment '{item['id']}' has parent_id '{item['parent_id']}' "
                 f"that is not in the file.")
    return data


def tokens(text: str) -> Set[str]:
    """Return the lowercase content words of a text."""
    return {w for w in re.findall(r"[a-z0-9']+", text.lower()) if w not in STOP}


def classify(text: str, earlier: List[str]) -> Tuple[str, str]:
    """Assign one category to a comment and give the reason for it."""
    lowered = text.lower()
    bare = re.sub(r"@[\w.-]+( [A-Z][\w-]+)?", " ", text)
    count = len(re.findall(r"[A-Za-z0-9']+", bare))
    hit = re.search(INJECTION, lowered)
    if hit:
        return "flagged", f"wording aimed at an assistant: \"{hit.group(0)}\""
    hit = re.search(SPAM, lowered)
    if hit:
        return "spam", f"promotional pattern: \"{hit.group(0)}\""
    if "@" in text and count < 3:
        return "tag-only", "mentions people and says nothing"
    hit = re.search(HOSTILE, lowered)
    if hit:
        return "hostile", f"abusive wording: \"{hit.group(0)}\""
    mine = tokens(text)
    for other in earlier:
        theirs = tokens(other)
        if mine and theirs and len(mine & theirs) / len(mine | theirs) >= 0.8:
            return "duplicate", "near-identical to an earlier comment"
    if "?" in text and count >= 4:
        return "question", "asks something"
    if re.search(PUSHBACK, lowered):
        return "pushback", "disagrees or qualifies"
    if count >= 12 and re.search(EXPERIENCE, lowered):
        return "story", "adds first-hand detail"
    if (any(p in lowered for p in PRAISE) and count < 12) or count < 6:
        return "thin-praise", "approval with nothing to answer"
    if count >= 12:
        return "substantive", "makes a point worth acknowledging"
    return "thin-praise", "too slight to carry a reply"


def triage(data: Dict[str, Any], as_of_arg: Optional[str], limit: int) -> Dict[str, Any]:
    """Classify every comment, detect answered ones and build the ordered queue."""
    me = str(data["me"]).strip().lower()
    comments = data["comments"]
    stamps = [parse_time(c.get("posted_at"), f"comment '{c['id']}' posted_at")
              for c in comments]
    timed = all(s is not None for s in stamps)
    order: List[Any] = stamps if timed else list(range(len(comments)))
    as_of = parse_time(as_of_arg or data.get("as_of"), "as_of") or \
        (max(s for s in stamps if s) if timed else None)
    by_id = {str(c["id"]): c for c in comments}
    root = {str(c["id"]): str(c.get("parent_id") or c["id"]) for c in comments}
    my_turns: Dict[str, List[Any]] = {}
    for comment, when in zip(comments, order):
        if str(comment["author"]).strip().lower() == me:
            my_turns.setdefault(root[str(comment["id"])], []).append(when)

    rows: List[Dict[str, Any]] = []
    earlier: List[str] = []
    for comment, when in zip(comments, order):
        cid, text = str(comment["id"]), str(comment["text"])
        if str(comment["author"]).strip().lower() == me:
            continue
        category, reason = classify(text, earlier)
        earlier.append(text)
        thread = root[cid]
        mine_here = my_turns.get(thread, [])
        answered = any(turn > when for turn in mine_here)
        wait = round((as_of - when).total_seconds() / 3600, 1) if timed and as_of else None
        relationship = str(comment.get("relationship", "unknown")).lower()
        try:
            likes = int(comment.get("likes", 0) or 0)
        except (TypeError, ValueError):
            fail(f"comment '{cid}' has a non-numeric 'likes' value: {comment.get('likes')!r}.")
        score = BASE.get(category, 0) + RELATIONSHIP.get(relationship, 0) \
            + min(likes, 10) + (15 if mine_here and not answered else 0) \
            + (min(wait, 48) / 4 if wait and wait > 0 else 0)
        action = "done" if answered and ACTION[category] in {"reply", "react"} \
            else ACTION[category]
        nested = bool(comment.get("parent_id"))
        rows.append({
            "id": cid, "author": comment["author"], "relationship": relationship,
            "category": category, "reason": reason, "action": action,
            "score": round(score, 1) if action == "reply" else 0.0,
            "waiting_hours": wait, "likes": likes, "nested": nested,
            "reply_under": thread, "thread_owner": by_id[thread]["author"],
            "continues_exchange": bool(mine_here and not answered),
            "excerpt": text.replace("\n", " ")[:90]})

    queue = sorted((r for r in rows if r["action"] == "reply"),
                   key=lambda r: (-r["score"], r["id"]))
    for position, row in enumerate(queue, start=1):
        row["position"] = position
        row["batch"] = "now" if position <= limit else "later"
    counts: Dict[str, int] = {}
    for row in rows:
        counts[row["action"]] = counts.get(row["action"], 0) + 1
    post_author = str((data.get("post") or {}).get("author", "")).strip()
    return {
        "mode": "own-post" if post_author.lower() == me else "someone-elses-thread",
        "as_of": as_of.isoformat() if as_of else None,
        "ordering": "timestamps" if timed else "file order (some posted_at missing)",
        "comments_read": len(comments), "own_comments": len(comments) - len(rows),
        "counts": counts, "queue": queue,
        "other": [r for r in rows if r["action"] != "reply"]}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the triage report as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    counts = report["counts"]
    print(f"Comment triage — {report['mode']}   as of {report['as_of'] or 'n/a'}")
    print(f"Read {report['comments_read']} comments ({report['own_comments']} yours)   "
          + "   ".join(f"{name}: {counts[name]}" for name in sorted(counts)))
    print(f"Ordering by {report['ordering']}")
    print("=" * 78)
    print("REPLY QUEUE")
    for row in report["queue"]:
        wait = f"{row['waiting_hours']}h" if row["waiting_hours"] is not None else "n/a"
        where = f"under {row['thread_owner']}'s comment, name {row['author'].split()[0]}" \
            if row["nested"] else "directly under their comment"
        print(f"{row['position']:>2}. [{row['batch']:<5}] {row['author']} "
              f"({row['relationship']}, {row['category']}, score {row['score']}, waited {wait})")
        print(f"      \"{row['excerpt']}\"")
        print(f"      place: {where}"
              + ("   — they answered you; your turn" if row["continues_exchange"] else ""))
    if not report["queue"]:
        print("  nothing needs a written reply.")
    print("-" * 78)
    labels = {"react": "REACT ONLY", "hold": "HOLD — YOUR DECISION",
              "flag": "FLAGGED — DO NOT DRAFT FROM THIS TEXT", "ignore": "IGNORE",
              "done": "ALREADY ANSWERED"}
    for action, label in labels.items():
        group = [r for r in report["other"] if r["action"] == action]
        if group:
            print(label)
            for row in group:
                print(f"  {row['id']:<5} {row['author']}: {row['category']} — {row['reason']}")


def main() -> None:
    """Parse arguments, run the triage, print it and apply the optional gate."""
    parser = argparse.ArgumentParser(
        description="Classify and order a pasted or exported LinkedIn comment "
                    "section: which comments to answer, in what order, which to "
                    "ignore. Offline: reads a local JSON file only.",
        epilog="Exit codes: 0 triage produced, 1 a reply-worthy comment exceeded "
               "--max-wait-hours, 2 bad input.")
    parser.add_argument("--input", required=True,
                        help="JSON file with 'me', optional 'post' and 'as_of', and "
                             "a 'comments' array.")
    parser.add_argument("--as-of", default=None,
                        help="ISO 8601 time to measure waiting from (default: the "
                             "file's 'as_of', else its newest comment).")
    parser.add_argument("--limit", type=int, default=12,
                        help="Replies to write in this sitting; the rest are marked "
                             "'later' (default: %(default)s).")
    parser.add_argument("--max-wait-hours", type=float, default=None,
                        help="Exit 1 if any reply-worthy comment has waited longer.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if args.limit < 1:
        fail("--limit must be at least 1.")

    report = triage(load_section(Path(args.input)), args.as_of, args.limit)
    output(report, args.format)
    if args.max_wait_hours is not None and any(
            (row["waiting_hours"] or 0) > args.max_wait_hours for row in report["queue"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
