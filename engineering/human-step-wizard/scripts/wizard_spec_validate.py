#!/usr/bin/env python3
"""Validate a human-step wizard spec (JSON) before it is turned into a bash script.

Catches the mistakes that make a generated wizard unsafe or unusable: duplicate
step ids, variable names that collide with the shell, input patterns that use
PCRE syntax bash's [[ =~ ]] (POSIX ERE) does not understand, checks that use a
value before any step captured it, unquoted expansions of human input, eval,
irreversible steps without a rollback, and secrets captured but never used.

Usage:
  python3 wizard_spec_validate.py --spec ../assets/sample_wizard_spec.json
  python3 wizard_spec_validate.py --spec spec.json --strict --format json

Exit codes:
  0  valid (no errors; no warnings under --strict)
  1  errors found (or warnings under --strict)
  2  usage error (file missing or not JSON)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
VAR_RE = re.compile(r"^[A-Z][A-Z0-9_]{1,63}$")
RESERVED = {"PATH", "HOME", "IFS", "PS1", "PS2", "PS4", "SHELL", "USER", "PWD", "OLDPWD", "TERM", "LANG",
            "UID", "EUID", "PPID", "RANDOM", "SECONDS", "LINENO", "HOSTNAME", "CDPATH", "ENV", "BASH_ENV",
            "SHELLOPTS", "BASHOPTS", "GLOBIGNORE", "TMPDIR", "NO_COLOR"}
RESERVED_PREFIXES = ("BASH_", "WIZARD_", "LD_", "DYLD_", "C_", "GIT_")
AMBIENT = {"HOME", "PATH", "USER", "PWD", "TMPDIR", "SHELL"}
PCRE_ONLY = [(r"\\[dDwWsSbB]", "\\d \\w \\s \\b classes"), (r"\(\?[:=!<]", "(?: ) groups or lookarounds"),
             (r"[*+?}]\?", "non-greedy quantifiers"), (r"\\[AZz]", "\\A \\Z anchors")]
KNOWN_STEP_KEYS = {"id", "title", "instructions", "url", "inputs", "checks", "irreversible", "rollback",
                   "pause", "allow_skip"}
MAX_STEPS = 15


def unquoted_vars(command: str) -> Set[str]:
    """Return variable names expanded outside double quotes (single-quoted text is literal)."""
    found: Set[str] = set()
    in_single = in_double = False
    i = 0
    while i < len(command):
        ch = command[i]
        if ch == "\\" and not in_single:
            i += 2
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "$" and not in_single and not in_double:
            m = re.match(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)", command[i:])
            if m:
                found.add(m.group(1))
        i += 1
    return found


def referenced_vars(command: str) -> Set[str]:
    """Return every $NAME / ${NAME} referenced outside single quotes."""
    stripped = re.sub(r"'[^']*'", "", command)
    return set(re.findall(r"\$\{?([A-Z][A-Z0-9_]*)", stripped))


def validate(spec: Any) -> Dict[str, Any]:
    """Run every rule; return a report with errors and warnings."""
    errors: List[str] = []
    warns: List[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec must be a JSON object"], "warnings": [], "steps": 0}
    for key in ("title", "slug"):
        if not isinstance(spec.get(key), str) or not spec[key].strip():
            errors.append(f"missing top-level '{key}'")
    if isinstance(spec.get("slug"), str) and not ID_RE.match(spec["slug"]):
        errors.append(f"slug '{spec['slug']}' must be lowercase letters, digits and dashes")
    env_file = spec.get("env_file", ".env")
    if not isinstance(env_file, str) or not env_file or env_file.startswith("/") or ".." in env_file.split("/"):
        errors.append("env_file must be a relative path inside the working directory")
    steps = spec.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("'steps' must be a non-empty list")
        steps = []
    if len(steps) > MAX_STEPS:
        warns.append(f"{len(steps)} steps; past {MAX_STEPS} humans lose the thread, split into two wizards")
    if "\x00" in json.dumps(spec):
        errors.append("spec contains a NUL character")

    seen_ids: Set[str] = set()
    captured: Dict[str, int] = {}
    secrets_unused: Dict[str, str] = {}
    all_inputs = {inp.get("name"): n for n, st in enumerate(steps, 1) if isinstance(st, dict)
                  for inp in st.get("inputs") or [] if isinstance(inp, dict)}
    for n, step in enumerate(steps, 1):
        where = f"step {n}"
        if not isinstance(step, dict):
            errors.append(f"{where}: must be an object")
            continue
        sid = step.get("id")
        where = f"step {n} ({sid})"
        if not isinstance(sid, str) or not ID_RE.match(sid):
            errors.append(f"{where}: id must be lowercase letters, digits and dashes (max 40)")
        elif sid in seen_ids:
            errors.append(f"{where}: duplicate step id; resume tracking would skip the second one")
        seen_ids.add(str(sid))
        for unknown in sorted(set(step) - KNOWN_STEP_KEYS):
            warns.append(f"{where}: unknown key '{unknown}' is ignored")
        if not isinstance(step.get("title"), str) or not step["title"].strip():
            errors.append(f"{where}: missing title")
        instr = step.get("instructions")
        if not isinstance(instr, list) or not instr or not all(isinstance(x, str) and x.strip() for x in instr):
            errors.append(f"{where}: instructions must be a non-empty list of strings")
        elif any(len(x) > 300 for x in instr):
            warns.append(f"{where}: an instruction is over 300 characters; one action per line reads better")
        url = step.get("url")
        if url is not None:
            if not isinstance(url, str) or not re.match(r"^https?://\S+$", url):
                errors.append(f"{where}: url must be an http(s) URL without spaces")
            elif url.startswith("http://"):
                warns.append(f"{where}: url is plain http; use https for dashboards that handle credentials")
        if step.get("irreversible") and not str(step.get("rollback") or "").strip():
            errors.append(f"{where}: irreversible step needs a 'rollback' text shown before the human confirms")

        inputs = step.get("inputs") or []
        if not isinstance(inputs, list):
            errors.append(f"{where}: inputs must be a list")
            inputs = []
        for inp in inputs:
            if not isinstance(inp, dict):
                errors.append(f"{where}: each input must be an object")
                continue
            name = inp.get("name")
            if not isinstance(name, str) or not VAR_RE.match(name):
                errors.append(f"{where}: input name {name!r} must be UPPER_SNAKE_CASE (2-64 chars)")
                continue
            if name in RESERVED or name.startswith(RESERVED_PREFIXES):
                errors.append(f"{where}: input name {name} collides with a shell or wizard variable")
            if name in captured:
                errors.append(f"{where}: {name} is already captured in step {captured[name]}")
            if not str(inp.get("prompt") or "").strip():
                errors.append(f"{where}: input {name} needs a prompt")
            if inp.get("store", "env") not in ("env", "none"):
                errors.append(f"{where}: input {name} store must be 'env' or 'none'")
            pattern = inp.get("pattern")
            if pattern is not None:
                try:
                    re.compile(str(pattern))
                except re.error as exc:
                    errors.append(f"{where}: pattern for {name} does not compile: {exc}")
                for rx, label in PCRE_ONLY:
                    if re.search(rx, str(pattern)):
                        errors.append(f"{where}: pattern for {name} uses {label}; bash [[ =~ ]] is POSIX ERE "
                                      "(use [0-9], [A-Za-z0-9_], [[:space:]])")
                if not str(pattern).startswith("^") or not str(pattern).endswith("$"):
                    warns.append(f"{where}: pattern for {name} is unanchored; '^...$' stops partial matches")
            elif inp.get("secret"):
                warns.append(f"{where}: secret {name} has no pattern; a pasted wrong value is only caught later")
            if inp.get("secret") and inp.get("store", "env") == "none":
                secrets_unused[name] = where
            captured[name] = n

        checks = step.get("checks") or []
        if not isinstance(checks, list):
            errors.append(f"{where}: checks must be a list")
            checks = []
        for chk in checks:
            if not isinstance(chk, dict) or not str(chk.get("command") or "").strip():
                errors.append(f"{where}: each check needs a non-empty 'command'")
                continue
            cmd = str(chk["command"])
            if not str(chk.get("description") or "").strip():
                warns.append(f"{where}: check without a description; the human sees the failure, not the intent")
            if re.search(r"(^|[\s;&|(])(eval|source)\s", cmd) or re.search(r"(^|[;&|(]\s*)\.\s", cmd):
                errors.append(f"{where}: check uses eval/source; captured values must never be executed")
            for var in referenced_vars(cmd):
                secrets_unused.pop(var, None)
                if var in captured or var in AMBIENT:
                    continue
                if var in all_inputs:
                    errors.append(f"{where}: check uses ${var} before step {all_inputs[var]} captures it")
                else:
                    warns.append(f"{where}: check uses ${var}, which no step captures; it must already be exported")
            for var in sorted(unquoted_vars(cmd) & set(all_inputs)):
                warns.append(f'{where}: ${var} is unquoted in a check; write "${var}" so spaces or globs stay data')
        if step.get("irreversible") and not checks:
            warns.append(f"{where}: irreversible step without a check; verify the result before moving on")
        if not inputs and not checks and not url and not step.get("pause", True):
            warns.append(f"{where}: no url, input, check or pause; the human cannot act on it")

    for name, where in secrets_unused.items():
        warns.append(f"{where}: secret {name} is neither stored nor used by any check")
    return {"valid": not errors, "errors": errors, "warnings": warns, "steps": len(steps),
            "inputs": sorted(captured), "title": spec.get("title"), "slug": spec.get("slug")}


def load_spec(path: str) -> Any:
    """Read and parse the spec file, exiting 2 on I/O or JSON errors."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: cannot read spec: {exc}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"error: spec is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(2)


def main() -> None:
    """Entry point."""
    p = argparse.ArgumentParser(description="Validate a human-step wizard spec.")
    p.add_argument("--spec", required=True, help="path to the wizard spec JSON")
    p.add_argument("--strict", action="store_true", help="treat warnings as failures")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = p.parse_args()
    report = validate(load_spec(args.spec))
    failed = bool(report["errors"]) or (args.strict and bool(report["warnings"]))
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"Wizard spec: {report.get('title') or '?'} ({report['steps']} steps)")
        for e in report["errors"]:
            print(f"  ERROR  {e}")
        for w in report["warnings"]:
            print(f"  WARN   {w}")
        print(f"\n{len(report['errors'])} errors, {len(report['warnings'])} warnings")
        print("RESULT: FAIL" if failed else "RESULT: PASS")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
