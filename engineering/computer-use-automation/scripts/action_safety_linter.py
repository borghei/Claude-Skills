#!/usr/bin/env python3
"""action_safety_linter.py — Lint a planned computer-use action sequence.

Reads a list of planned agent actions (JSON or simple text) and flags
reliability and safety gaps before the agent ever touches a real target:

  - destructive / irreversible verbs (delete, send, pay, submit, purchase...)
    with no confirmation gate
  - state-changing actions with no verification step afterward
  - patterns that trigger blocking native/modal dialogs the agent cannot see
    (file pickers, OS print/save dialogs, downloads)
  - navigation/typing without a preceding fresh-screenshot grounding step

Input formats
-------------
JSON: a list of objects, e.g.
  [{"type": "click", "target": "Delete", "confirmed": false, "verified": false}]

Text: one action per line, "<type> <target>", e.g.
  click Delete
  type  search box
  submit Confirm

Reads from --file or stdin. Standard library only. Supports --json and
human-readable / markdown output.
"""

import argparse
import json
import sys

DESTRUCTIVE_VERBS = {
    "delete", "remove", "send", "pay", "purchase", "buy", "submit", "confirm",
    "transfer", "delete_all", "drop", "wipe", "erase", "deactivate",
    "unsubscribe", "post", "publish", "approve", "cancel", "checkout",
}

# Action types that change state and therefore need a verification observation.
STATE_CHANGING = {
    "click", "type", "submit", "navigate", "drag", "select", "upload",
    "keypress", "press", "scroll_submit", "send",
}

# Verbs / targets that tend to open blocking native dialogs.
DIALOG_TRIGGERS = {
    "upload", "download", "print", "save_as", "saveas", "open_file",
    "file_picker", "choose_file", "browse",
}

# Actions that read screen state (count as verification / grounding).
VERIFY_TYPES = {"screenshot", "observe", "verify", "read", "assert", "wait_for", "check"}

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def load_actions(raw):
    raw = raw.strip()
    if not raw:
        return []
    # Try JSON first.
    if raw[0] in "[{":
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            parsed = [parsed]
        actions = []
        for item in parsed:
            if isinstance(item, str):
                actions.append(parse_text_line(item))
            elif isinstance(item, dict):
                actions.append({
                    "type": str(item.get("type", "")).strip().lower(),
                    "target": str(item.get("target", "")).strip(),
                    "confirmed": bool(item.get("confirmed", False)),
                    "verified": bool(item.get("verified", False)),
                })
            else:
                actions.append({"type": "", "target": str(item), "confirmed": False,
                                 "verified": False})
        return actions
    # Otherwise treat as text lines.
    return [parse_text_line(line) for line in raw.splitlines() if line.strip()]


def parse_text_line(line):
    parts = line.strip().split(None, 1)
    atype = parts[0].strip().lower() if parts else ""
    target = parts[1].strip() if len(parts) > 1 else ""
    return {"type": atype, "target": target, "confirmed": False, "verified": False}


def is_destructive(action):
    blob = (action["type"] + " " + action["target"]).lower()
    for verb in DESTRUCTIVE_VERBS:
        if verb in blob.split() or verb in action["type"]:
            return True
        if verb in blob:
            return True
    return False


def is_dialog_trigger(action):
    blob = (action["type"] + " " + action["target"]).lower()
    return any(t in blob for t in DIALOG_TRIGGERS)


def has_following_verification(actions, idx):
    """True if the action itself is marked verified or a later action reads state
    before the next state-changing action."""
    if actions[idx].get("verified"):
        return True
    for j in range(idx + 1, len(actions)):
        if actions[j]["type"] in VERIFY_TYPES:
            return True
        if actions[j]["type"] in STATE_CHANGING:
            return False  # another state change happened with no read in between
    return False


def has_preceding_grounding(actions, idx):
    """True if a fresh screenshot/observe precedes this action (grounding)."""
    for j in range(idx - 1, -1, -1):
        if actions[j]["type"] in VERIFY_TYPES:
            return True
        if actions[j]["type"] in STATE_CHANGING:
            return False
    return False


def lint(actions):
    findings = []

    def add(idx, sev, code, msg):
        if idx is not None:
            label = ("%s %s" % (actions[idx]["type"], actions[idx]["target"])).strip()
        else:
            label = "(sequence)"
        findings.append({
            "index": idx,
            "action": label,
            "severity": sev,
            "code": code,
            "message": msg,
        })

    grounded_at_start = False
    if actions and actions[0]["type"] in VERIFY_TYPES:
        grounded_at_start = True

    for i, a in enumerate(actions):
        destructive = is_destructive(a)

        if destructive and not a.get("confirmed"):
            add(i, "high", "no-confirmation-gate",
                "Destructive/irreversible action has no confirmation gate "
                "(set confirmed=true once a human/explicit gate approves it).")

        if a["type"] in STATE_CHANGING and not has_following_verification(actions, i):
            sev = "high" if destructive else "medium"
            add(i, sev, "missing-verification",
                "State-changing action is not verified — add a screenshot/observe "
                "step afterward to confirm the expected change actually happened.")

        if is_dialog_trigger(a):
            add(i, "medium", "blocking-dialog",
                "Action likely opens a blocking native/modal dialog (file picker, "
                "print/save, download) the agent cannot see or dismiss — prefer a "
                "flow that keeps state on the page.")

        if a["type"] in {"click", "type", "drag", "submit"} and not has_preceding_grounding(actions, i):
            add(i, "low", "no-grounding",
                "Action is not grounded on a fresh screenshot/observe — re-capture "
                "the current screen before acting to avoid stale-layout misclicks.")

    if actions and not grounded_at_start:
        add(0, "low", "no-initial-screenshot",
            "Sequence does not start with a screenshot/observe — ground the first "
            "action in the current screen state.")

    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]],
                                 f["index"] if f["index"] is not None else -1))
    return findings


def summarize(findings):
    counts = {"high": 0, "medium": 0, "low": 0}
    for f in findings:
        counts[f["severity"]] += 1
    risk = "high" if counts["high"] else "medium" if counts["medium"] else \
        "low" if counts["low"] else "clean"
    return counts, risk


def render_human(actions, findings, counts, risk, markdown=False):
    h1 = "## " if markdown else ""
    bullet = "- " if markdown else "  - "
    lines = []
    lines.append("%sAction Safety Lint Report" % h1)
    lines.append("")
    lines.append("Actions analyzed : %d" % len(actions))
    lines.append("Overall risk     : %s" % risk.upper())
    lines.append("Findings         : %d high, %d medium, %d low"
                 % (counts["high"], counts["medium"], counts["low"]))
    lines.append("")
    if not findings:
        lines.append("No issues found. Still dry-run in a sandbox before any real target.")
        return "\n".join(lines)
    lines.append("%sFindings" % ("### " if markdown else ""))
    for f in findings:
        loc = "#%d" % f["index"] if f["index"] is not None else "seq"
        lines.append("%s[%s] %s (%s): %s"
                     % (bullet, f["severity"].upper(), loc + " " + f["action"],
                        f["code"], f["message"]))
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(
        description="Lint a planned computer-use action sequence for safety/reliability gaps."
    )
    p.add_argument("--file", help="Path to JSON or text action list (default: stdin)")
    p.add_argument("--format", choices=["text", "markdown"], default="text",
                   help="Human-readable output format")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = p.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            raw = fh.read()
    else:
        raw = sys.stdin.read()

    try:
        actions = load_actions(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write("error: could not parse actions: %s\n" % exc)
        sys.exit(2)

    findings = lint(actions)
    counts, risk = summarize(findings)

    if args.json:
        print(json.dumps({
            "actions_analyzed": len(actions),
            "overall_risk": risk,
            "counts": counts,
            "findings": findings,
        }, indent=2))
    else:
        print(render_human(actions, findings, counts, risk,
                           markdown=(args.format == "markdown")))

    sys.exit(1 if counts["high"] else 0)


if __name__ == "__main__":
    main()
