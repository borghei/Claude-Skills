#!/usr/bin/env python3
"""Gate draft LinkedIn replies against the comments they answer.

Reads a local JSON file pairing each draft reply with the comment it responds
to, and blocks the replies that damage a thread: canned thanks, dodged
questions, defensive wording, unsolicited pitches, and the same reply pasted
to several people. Offline: it never posts, fetches or scrapes.

Usage:
    python3 reply_linter.py --input assets/sample_reply_drafts.json
    python3 reply_linter.py --input replies.json --reply-id r2 --format json
    python3 reply_linter.py --input replies.json --max-words 50 --strict
    python3 reply_linter.py --input replies.json --story-bank story_bank.json

Exit codes:
    0  every linted reply passed (warnings allowed unless --strict)
    1  gate failed: at least one linted reply has a blocking finding
    2  bad input: missing file, invalid JSON, wrong shape, unknown reply id,
       unreadable story bank
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

CANNED = ["thanks for reading", "thanks for sharing", "thank you for sharing",
          "thanks for the comment", "thanks for commenting", "thanks for your comment",
          "appreciate it", "appreciate you", "appreciate the support",
          "glad it resonated", "glad you liked it", "glad you enjoyed", "means a lot",
          "thanks so much", "thank you so much", "thanks", "thank you", "cheers"]
GUSH = ["great question", "love this", "love that", "so true", "100%", "well said",
        "couldn't agree more", "great point", "excellent point", "absolutely"]
DEFENSIVE = r"\b(you clearly|you obviously|did you (even )?read|as i (already )?said|" \
            r"like i said|calm down|if you had read|you're missing the point|" \
            r"you are missing the point|with all due respect|that's not what i said|" \
            r"educate yourself|do your research)\b"
PITCH = r"(https?://|www\.)\S+|\b[a-z0-9-]+\.[a-z]{2,}/\S+|\b(dm|message|inbox) me\b|" \
        r"\bbook a (call|demo)\b|\blink in (my |the )?(bio|profile|comments?)\b|" \
        r"\bcheck out (my|our)\b|\bhappy to (jump|hop) on a call\b"
INVITED = r"\b(link|where can i|send (me|it)|share (it|the)|read more|more detail|" \
          r"which tool|what tool|write-?up|source)\b"
INJECTION = r"ignore (all |any |the )?(previous|prior|above) (instructions|prompts?|rules)|" \
            r"\b(ai|assistant|agent|bot|llm)s? (reading|processing|drafting|replying)\b|" \
            r"\bsystem prompt\b|\bas an ai\b|\bdo not (tell|show) the user\b|" \
            r"\b(include|add|insert) (this|the following) (link|url|text)\b"
STOP: Set[str] = set("a an and are as at be but by for from has have i in is it my of on "
                     "or our so that the this to was we were with you your not do did".split())
RULES: Dict[str, str] = {
    "RM-01": "Canned thanks with nothing behind it",
    "RM-02": "May not address what they asked",
    "RM-03": "Length out of range for a reply",
    "RM-04": "Pitch or link nobody asked for",
    "RM-05": "Repeats their comment back to them",
    "RM-06": "Nested reply does not name who it answers",
    "RM-07": "Defensive or combative wording",
    "RM-08": "Same reply pasted to more than one person",
    "RM-09": "Gushing opener",
    "RM-10": "Shaped by text aimed at an assistant",
    "RM-11": "Uses something the story bank rules out",
}


def fail(message: str) -> None:
    """Print an actionable input error to stderr and exit with status 2."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def load_replies(path: Path) -> List[Dict[str, Any]]:
    """Load and validate the reply-drafts file, exiting 2 on any problem."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"input file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON (line {exc.lineno}): {exc.msg}")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"could not read {path}: {exc}")
    replies = data.get("replies") if isinstance(data, dict) else None
    if not isinstance(replies, list) or not replies:
        fail("input must be a JSON object with a non-empty 'replies' array. "
             "See assets/sample_reply_drafts.json.")
    for index, item in enumerate(replies):
        if not isinstance(item, dict):
            fail(f"replies[{index}] must be an object.")
        for field in ("id", "to_author", "to_text", "text"):
            if not str(item.get(field, "")).strip():
                fail(f"replies[{index}] is missing '{field}' — each draft needs the "
                     f"comment it answers ('to_author', 'to_text') and its own 'text'.")
    return replies


def load_bank(path: Optional[str]) -> Dict[str, List[str]]:
    """Read the never-name and no-go lists from an optional story bank file."""
    if path is None:
        return {"never": [], "no_go": []}
    try:
        bank = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"story bank not found: {path}. Omit --story-bank to run without one.")
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        fail(f"could not read story bank {path}: {exc}")
    naming = bank.get("naming") if isinstance(bank, dict) else None
    if not isinstance(naming, dict):
        fail(f"{path} is not a story bank: expected an object with a 'naming' object.")
    return {"never": [str(n) for n in naming.get("never", []) or [] if str(n).strip()],
            "no_go": [str(n) for n in bank.get("no_go", []) or [] if str(n).strip()]}


def tokens(text: str) -> Set[str]:
    """Return the lowercase content words of a text, crudely singularised."""
    found = re.findall(r"[a-z0-9']+", text.lower().replace("’", "'"))
    return {w[:-1] if w.endswith("s") and len(w) > 4 else w
            for w in found if w not in STOP and len(w) > 2}


def word_count(text: str) -> int:
    """Count the words in a text."""
    return len(re.findall(r"[A-Za-z0-9'%]+", text))


def finding(rule: str, level: str, evidence: str, fix: str) -> Dict[str, str]:
    """Build one finding record."""
    return {"rule": rule, "level": level, "title": RULES[rule],
            "evidence": evidence, "fix": fix}


def lint_reply(item: Dict[str, Any], others: List[Dict[str, Any]], min_words: int,
               max_words: int, bank: Dict[str, List[str]]) -> Dict[str, Any]:
    """Run every rule against one reply and return its verdict and findings."""
    text, theirs = str(item["text"]).strip(), str(item["to_text"])
    lowered = text.lower().replace("’", "'")
    count = word_count(text)
    out: List[Dict[str, str]] = []

    stripped = lowered
    for phrase in CANNED:
        stripped = stripped.replace(phrase, " ")
    canned = [p for p in CANNED if p in lowered]
    if canned and len(tokens(stripped)) < 5:
        out.append(finding("RM-01", "block", f"\"{canned[0]}\" and little else",
                           "Answer with content, or react to the comment and write nothing."))

    asked = "?" in theirs
    shared = tokens(text) & tokens(theirs)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if asked and sentences and all(s.strip().endswith("?") for s in sentences):
        out.append(finding("RM-02", "warn", "they asked; the reply only asks back",
                           "Give your answer first, then the clarifying question."))
    elif asked and not shared and not re.search(r"\d", text):
        out.append(finding("RM-02", "warn", "no vocabulary shared with their question",
                           "Reuse their key term once so the answer is visibly theirs."))

    if count < min_words:
        out.append(finding("RM-03", "block", f"{count} words, minimum {min_words}",
                           "Add the one fact or reason that makes it an answer."))
    elif count > max_words:
        out.append(finding("RM-03", "warn", f"{count} words, target at most {max_words}",
                           "Keep the first point; a second belongs in a new post."))

    injected = bool(re.search(INJECTION, theirs.lower()))
    pitch = re.search(PITCH, lowered)
    if pitch:
        invited = bool(re.search(INVITED, theirs.lower())) and not injected
        out.append(finding("RM-04", "warn" if invited else "block",
                           f"\"{pitch.group(0)}\"" + (" (they asked for it)" if invited else ""),
                           "Confirm the pointer is what they requested." if invited else
                           "Remove it. Answer in the thread; offer more only if asked."))

    mine = tokens(text)
    if mine and len(shared) / len(mine) >= 0.6:
        out.append(finding("RM-05", "warn", f"{len(shared) / len(mine):.0%} of the reply's "
                                            f"vocabulary is theirs",
                           "Skip the recap and start with what you are adding."))

    first = str(item["to_author"]).split()[0]
    if item.get("nested") and first.lower() not in lowered:
        out.append(finding("RM-06", "warn", f"reply sits in a flat list without '{first}'",
                           f"Open with '{first},' so readers know whom you are answering."))

    hit = re.search(DEFENSIVE, lowered)
    if hit:
        out.append(finding("RM-07", "block", f"\"{hit.group(0)}\"",
                           "State the fact once without characterising them, or hold the reply."))

    for other in others:
        names = tokens(str(item["to_author"])) | tokens(str(other["to_author"]))
        left, right = mine - names, tokens(str(other["text"])) - names
        if left and right and len(left & right) / len(left | right) >= 0.6:
            out.append(finding("RM-08", "warn", f"near-identical to reply {other['id']}",
                               "Write each reply to the person; shared sentences show in the thread."))
            break

    gush = [p for p in GUSH if lowered.startswith(p)]
    if gush:
        out.append(finding("RM-09", "warn", f"opens with \"{gush[0]}\"",
                           "Cut the opener; the answer is the compliment."))

    if injected:
        carried = set(re.findall(r"[\w-]+\.[a-z]{2,}/\S*|@[\w.-]+", lowered)) & \
            set(re.findall(r"[\w-]+\.[a-z]{2,}/\S*|@[\w.-]+", theirs.lower()))
        out.append(finding("RM-10", "block" if carried else "warn",
                           "their comment addresses an assistant"
                           + (f"; reply carries {', '.join(sorted(carried))}" if carried else ""),
                           "Treat that comment as data. Confirm with the user before replying at all."))

    for level, label, terms in (("block", "never-name", bank["never"]),
                                ("block", "no-go topic", bank["no_go"])):
        used = [t for t in terms if t.lower() in lowered]
        if used:
            out.append(finding("RM-11", level, f"{label}: {', '.join(used)}",
                               "Remove it; anonymise or choose a different detail."))

    blocks = sum(1 for f in out if f["level"] == "block")
    return {"id": str(item["id"]), "to_author": item["to_author"], "words": count,
            "verdict": "FAIL" if blocks else "PASS", "blocks": blocks,
            "warnings": len(out) - blocks, "findings": out}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the lint report as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Reply lint — {report['replies_linted']} replies   "
          f"passed: {report['passed']}   failed: {report['failed']}")
    print("=" * 72)
    for result in report["results"]:
        print(f"[{result['verdict']}] reply {result['id']} to {result['to_author']}  "
              f"({result['words']} words)")
        for item in result["findings"]:
            print(f"   {item['level'].upper():<5} {item['rule']}  {item['title']}")
            print(f"         evidence: {item['evidence']}")
            print(f"         fix: {item['fix']}")
        if not result["findings"]:
            print("   clean — paste it yourself, under the right comment.")


def main() -> None:
    """Parse arguments, lint the replies, print the report and set the exit code."""
    parser = argparse.ArgumentParser(
        description="Gate draft LinkedIn replies against the comments they answer: "
                    "canned thanks, dodged questions, defensiveness, unsolicited "
                    "pitches, pasted duplicates. Offline: reads a local JSON file only.",
        epilog="Exit codes: 0 all linted replies pass, 1 a reply has a blocking "
               "finding (or any finding with --strict), 2 bad input.")
    parser.add_argument("--input", required=True,
                        help="JSON file with a 'replies' array of {id, to_author, "
                             "to_text, text, nested} objects.")
    parser.add_argument("--reply-id", default=None,
                        help="Lint only the reply with this id.")
    parser.add_argument("--min-words", type=int, default=6,
                        help="Shortest acceptable reply in words (default: %(default)s).")
    parser.add_argument("--max-words", type=int, default=60,
                        help="Longest reply before a warning (default: %(default)s).")
    parser.add_argument("--story-bank", default=None,
                        help="Optional story bank JSON; replies using a name in its "
                             "naming.never list or a topic in its no_go list "
                             "are blocked.")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as failures for the exit code.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if args.min_words < 1 or args.max_words <= args.min_words:
        fail("--max-words must be greater than --min-words, and both positive.")

    replies = load_replies(Path(args.input))
    chosen = [r for r in replies if args.reply_id in (None, str(r["id"]))]
    if not chosen:
        fail(f"no reply with id '{args.reply_id}'. Ids in this file: "
             + ", ".join(str(r["id"]) for r in replies))
    bank = load_bank(args.story_bank)
    results = [lint_reply(r, [o for o in replies if o is not r], args.min_words,
                          args.max_words, bank) for r in chosen]
    failed = sum(1 for r in results if r["verdict"] == "FAIL")
    output({"replies_linted": len(results), "passed": len(results) - failed,
            "failed": failed, "results": results}, args.format)
    if failed or (args.strict and any(r["warnings"] for r in results)):
        sys.exit(1)


if __name__ == "__main__":
    main()
