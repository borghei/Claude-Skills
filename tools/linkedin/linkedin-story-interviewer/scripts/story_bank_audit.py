#!/usr/bin/env python3
"""Validate a story bank file, report coverage per pillar, list what to ask next.

Reads a story bank JSON file (format in references/story-bank-format.md),
checks every entry against the bank's own naming and no-go lists, counts
draft-ready material per pillar and per kind, and turns the gaps into an
agenda of questions for the next interview session. Works on a local file
only; nothing is sent anywhere.

Usage:
    python3 story_bank_audit.py --input story_bank.json
    python3 story_bank_audit.py --input story_bank.json --format json
    python3 story_bank_audit.py --input story_bank.json \
        --min-per-pillar 4 --today 2026-10-07 --fail-on blocker

Exit codes:
    0  audit completed (and no finding reached the --fail-on level)
    1  gate failed: a finding at or above --fail-on exists
    2  bad input: file missing, unreadable, not JSON, or not a story bank
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, NoReturn

sys.path.insert(0, str(Path(__file__).resolve().parent))
from story_bank_rules import (  # noqa: E402
    FOLLOW_UPS, KINDS, SEVERITY_RANK, TENSION_KINDS, entry_text, finding,
    has_anchor, is_ignored, mentions, missing_fields, soft_hits, valid_when,
    word_count)


def fail(message: str) -> NoReturn:
    """Print an actionable error to stderr and exit with the bad-input code."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def load_bank(path: Path) -> Dict[str, Any]:
    """Load the bank file and confirm it has the top-level shape of a bank."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"story bank not found: {path}. Copy assets/story_bank_template.json "
             "to start one.")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {path}: {exc}")
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON (line {exc.lineno}, column {exc.colno}): "
             f"{exc.msg}")
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        fail("a story bank is a JSON object with an 'entries' array. See "
             "assets/sample_story_bank.json for the expected shape.")
    if not isinstance(data.get("pillars"), list) or not data["pillars"]:
        fail("the bank declares no 'pillars'. Add a list of two to five pillar "
             "names so coverage can be measured.")
    if any(not isinstance(e, dict) for e in data["entries"]):
        fail("every item in 'entries' must be a JSON object.")
    return data


def parse_day(value: str, flag: str) -> date:
    """Parse a YYYY-MM-DD string, exiting with guidance when it is malformed."""
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        fail(f"{flag} must be a date in YYYY-MM-DD form, got '{value}'.")


def check_entry(entry: Dict[str, Any], bank: Dict[str, Any],
                seen: Dict[str, int]) -> List[Dict[str, Any]]:
    """Run every per-entry rule and return the findings for one entry."""
    out: List[Dict[str, Any]] = []
    eid = str(entry.get("id") or "").strip()
    label = eid or f"<entry {seen['_index']}>"
    naming = bank.get("naming") if isinstance(bank.get("naming"), dict) else {}
    text = entry_text(entry)
    detail = str(entry.get("detail") or "")

    for name in mentions(text, naming.get("never", []) or []):
        out.append(finding("SB-001", label, f"contains '{name}'",
                           "Rewrite the entry without the name, or move the name "
                           "to ask_first after getting consent."))
    for topic in mentions(text, bank.get("no_go", []) or []):
        out.append(finding("SB-002", label, f"contains '{topic}'",
                           "Remove the entry or cut the subject out of it; a "
                           "draft will reuse whatever the bank holds."))
    if not eid or seen.get(eid, 0) > 1:
        out.append(finding("SB-010", label, f"id='{eid}'",
                           "Give every entry a unique id such as S-014."))
    kind = entry.get("kind")
    if kind not in KINDS:
        out.append(finding("SB-011", label, f"kind='{kind}'",
                           f"Use one of: {', '.join(KINDS)}."))
    stray = [p for p in entry.get("pillars", []) or [] if p not in bank["pillars"]]
    if stray or not entry.get("pillars"):
        out.append(finding("SB-012", label, f"pillars={entry.get('pillars')}",
                           "File the entry under at least one declared pillar: "
                           f"{', '.join(map(str, bank['pillars']))}."))
    if not valid_when(entry.get("when")):
        out.append(finding("SB-013", label, f"when='{entry.get('when')}'",
                           "Ask which month. Use YYYY, YYYY-MM or YYYY-MM-DD."))
    absent = missing_fields(entry)
    if absent:
        out.append(finding("SB-014", label, f"{kind} without {', '.join(absent)}",
                           "Ask for the missing part or mark the entry soft."))
    figure = entry.get("figure")
    if isinstance(figure, dict) and figure.get("value") and not (
            figure.get("measures") and figure.get("basis")):
        out.append(finding("SB-015", label, f"figure.value='{figure.get('value')}'",
                           "Record what the number counts and how it was "
                           "measured; a bare number cannot be defended."))
    soft = soft_hits(text)
    if entry.get("status") == "ready" and soft and not has_anchor(detail):
        out.append(finding("SB-020", label, f"soft wording: {', '.join(soft)}",
                           "Press once for the number or the month, then set "
                           "status to soft if none exists."))
    if word_count(detail) < 12:
        out.append(finding("SB-021", label, f"{word_count(detail)} words of detail",
                           "Ask what happened next and who else was there."))
    if not str(entry.get("words") or "").strip():
        out.append(finding("SB-022", label, "words is empty",
                           "Next time they phrase this vividly, write it down "
                           "exactly as said."))
    if entry.get("naming") not in ("clear", "ask", "anonymise"):
        out.append(finding("SB-023", label, f"naming='{entry.get('naming')}'",
                           "Ask whether the people and companies in this entry "
                           "can be named."))
    used = entry.get("used_in") or []
    if isinstance(used, list) and len(used) > 1:
        out.append(finding("SB-032", label, f"used {len(used)} times",
                           "Retire it or find a new angle; readers notice reruns."))
    return out


def coverage(bank: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Count ready and unused material for each pillar, broken down by kind."""
    table: Dict[str, Dict[str, Any]] = {}
    for pillar in bank["pillars"]:
        row = {"ready": 0, "soft": 0, "unused": 0, "kinds": {k: 0 for k in KINDS}}
        for entry in bank["entries"]:
            if pillar not in (entry.get("pillars") or []):
                continue
            if entry.get("status") != "ready":
                row["soft"] += 1
                continue
            row["ready"] += 1
            if not entry.get("used_in"):
                row["unused"] += 1
            if entry.get("kind") in KINDS:
                row["kinds"][entry["kind"]] += 1
        table[str(pillar)] = row
    return table


def build_agenda(bank: Dict[str, Any], table: Dict[str, Dict[str, Any]],
                 minimum: int) -> List[Dict[str, str]]:
    """Turn coverage gaps into an ordered list of questions for the next session."""
    agenda: List[Dict[str, str]] = []
    for pillar, row in table.items():
        if row["ready"] < minimum:
            agenda.append({
                "gap": f"pillar '{pillar}' has {row['ready']} ready "
                       f"entries, target {minimum}",
                "ask": FOLLOW_UPS["pillar"].format(pillar=pillar)})
        if row["ready"] and not any(row["kinds"][k] for k in TENSION_KINDS):
            agenda.append({
                "gap": f"pillar '{pillar}' holds only wins (no reversal, cost or stance)",
                "ask": FOLLOW_UPS["reversal"]})
    ready_kinds = {e.get("kind") for e in bank["entries"] if e.get("status") == "ready"}
    for kind in KINDS:
        if kind not in ready_kinds:
            agenda.append({"gap": f"no ready entry of kind '{kind}'",
                           "ask": FOLLOW_UPS[kind]})
    for entry in bank["entries"]:
        soft = soft_hits(entry_text(entry))
        if entry.get("status") != "ready" or (soft and not has_anchor(str(entry.get("detail") or ""))):
            key = "soft" if soft else "unfinished"
            agenda.append({"gap": f"{entry.get('id', '<no id>')} is soft",
                           "ask": FOLLOW_UPS[key].format(
                               phrase=soft[0] if soft else "",
                               entry=entry.get("id", "that entry"))})
    return agenda


def audit(bank: Dict[str, Any], path: Path, minimum: int, today: date,
          stale_days: int) -> Dict[str, Any]:
    """Run the whole audit and assemble the report."""
    seen: Dict[str, int] = {}
    for entry in bank["entries"]:
        key = str(entry.get("id") or "").strip()
        seen[key] = seen.get(key, 0) + 1
    findings: List[Dict[str, Any]] = []
    for index, entry in enumerate(bank["entries"], start=1):
        seen["_index"] = index
        findings.extend(check_entry(entry, bank, seen))
    updated = str(bank.get("updated") or "")
    stamp = date.fromisoformat(updated) if valid_when(updated) and len(updated) == 10 else None
    if stamp is None or not 0 <= (today - stamp).days <= stale_days:
        findings.append(finding(
            "SB-030", "<bank>", f"updated='{updated}'",
            "Run a short session on what changed: new role, shipped work, "
            "anything you no longer believe."))
    if is_ignored(path) is False:
        findings.append(finding(
            "SB-031", "<bank>", f"{path.name} is inside a git working tree",
            "Add the file to .gitignore or keep it outside the repository; it "
            "holds named people and private figures."))
    findings.sort(key=lambda f: (SEVERITY_RANK[f["severity"]], f["id"], f["entry"]))
    table = coverage(bank)
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_RANK}
    thin = [p for p, row in table.items() if row["ready"] < minimum]
    verdict = f"draftable, but thin in: {', '.join(thin)}" if thin else "ready to draft from"
    if counts["blocker"]:
        verdict = "not safe to draft from: resolve the blockers first"
    return {
        "owner": bank.get("owner", "unknown"), "updated": updated,
        "sessions": bank.get("sessions", 0), "entries": len(bank["entries"]),
        "ready_entries": sum(1 for e in bank["entries"] if e.get("status") == "ready"),
        "min_per_pillar": minimum, "verdict": verdict, "counts": counts,
        "coverage": table, "findings": findings,
        "agenda": build_agenda(bank, table, minimum),
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or as a human-readable summary."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Story bank audit: {report['owner']} "
          f"(updated {report['updated'] or 'never'}, {report['sessions']} sessions)")
    print(f"Entries: {report['entries']} total, {report['ready_entries']} ready   "
          f"Verdict: {report['verdict']}")
    print("Findings: " + ", ".join(f"{n} {s}" for s, n in report["counts"].items()))
    print("=" * 72)
    print(f"{'Pillar':<18}{'ready':>6}{'unused':>8}{'soft':>6}  kinds present")
    for pillar, row in report["coverage"].items():
        kinds = ", ".join(f"{k}:{n}" for k, n in row["kinds"].items() if n) or "none"
        mark = "  <-- thin" if row["ready"] < report["min_per_pillar"] else ""
        print(f"{pillar:<18}{row['ready']:>6}{row['unused']:>8}{row['soft']:>6}  "
              f"{kinds}{mark}")
    print("-" * 72)
    for item in report["findings"]:
        print(f"[{item['severity'].upper():<7}] {item['id']}  {item['entry']}: "
              f"{item['title']}\n          evidence: {item['evidence']}"
              f"\n          do: {item['action']}")
    print("-" * 72)
    print("Next session agenda (ask one at a time, in this order):")
    for number, item in enumerate(report["agenda"], start=1):
        print(f"{number:>2}. {item['gap']}\n    ask: {item['ask']}")
    if not report["agenda"]:
        print("    Nothing outstanding. Re-audit after the next role or project change.")


def main() -> None:
    """Parse arguments, audit the bank, print the report, apply the gate."""
    parser = argparse.ArgumentParser(
        description="Validate a story bank file, report coverage per pillar "
                    "and list the gaps to interview for.",
        epilog="Exit codes: 0 audit completed, 1 a finding reached --fail-on, "
               "2 bad input.")
    parser.add_argument("--input", required=True,
                        help="Path to the story bank JSON file.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--min-per-pillar", type=int, default=3,
                        help="Ready entries a pillar needs to stop being thin "
                             "(default: 3).")
    parser.add_argument("--stale-days", type=int, default=180,
                        help="Days since 'updated' before the bank is stale "
                             "(default: 180).")
    parser.add_argument("--today", default=None,
                        help="Reference date YYYY-MM-DD for the staleness check "
                             "(default: system date); pass it for stable output.")
    parser.add_argument("--fail-on", choices=["blocker", "fix"], default=None,
                        help="Exit 1 if any finding at or above this level exists.")
    args = parser.parse_args()
    if args.min_per_pillar < 1 or args.stale_days < 1:
        fail("--min-per-pillar and --stale-days must be 1 or greater.")
    today = parse_day(args.today, "--today") if args.today else date.today()
    path = Path(args.input)
    bank = load_bank(path)
    try:
        report = audit(bank, path, args.min_per_pillar, today, args.stale_days)
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        fail(f"{path} has a field of the wrong type ({exc}). Compare it with "
             "assets/story_bank_template.json.")
    output(report, args.format)
    if args.fail_on:
        limit = SEVERITY_RANK[args.fail_on]
        if any(SEVERITY_RANK[f["severity"]] <= limit for f in report["findings"]):
            sys.exit(1)


if __name__ == "__main__":
    main()
