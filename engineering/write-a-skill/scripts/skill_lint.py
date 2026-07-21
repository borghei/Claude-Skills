#!/usr/bin/env python3
"""Lint a skill package against the 11-pattern skill-authoring standard.

Checks frontmatter, description budget, SKILL.md length, required sections,
anti-pattern count, confidence tagging, structure, script line counts, and
permitted imports, emitting a per-pattern pass/fail report.
Document-side checks live in the sibling module ``lint_checks.py``.

Usage:
  python3 skill_lint.py --skill engineering/write-a-skill --format json
  python3 skill_lint.py --skill <dir> --rules assets/sample_lint_rules.json --strict
  python3 skill_lint.py --selftest
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from lint_checks import (DEFAULT_RULES, SEVERITY_ORDER, Finding, check_body, check_frontmatter,
                         check_structure, load_rules, parse_frontmatter)

MAIN_GUARD = '__name__ == "__main__"'
CLI_CHECKS = (("argparse", "error", "no argparse CLI"),
              ("--format", "warn", "no --format flag (text/json required)"),
              (MAIN_GUARD, "error", "missing __main__ guard"))

SELFTEST_FILES = {
    "tool.py": ('"""Fixture tool."""\nimport argparse\nimport helper\n\n\ndef run(name: str) -> str:\n'
                '    """Return a shout."""\n    return helper.shout(name)\n\n\n'
                'if __name__ == "__main__":\n    argparse.ArgumentParser().parse_args()  # --format\n'),
    "helper.py": ('"""Fixture helper library with no CLI."""\nimport json\n\n\ndef shout(name: str) -> str:\n'
                  '    """Return the name uppercased."""\n    return json.dumps(name.upper())\n'),
    "rogue.py": '"""Fixture importing a third-party package."""\nimport requests\n',
    "reacher.py": '"""Fixture reaching into another skill."""\nfrom ...other_skill.scripts import util\n',
}
SELFTEST_CASES = (
    ("sibling helper import is not a dependency", "tool.py: non-stdlib import 'helper'", False),
    ("helper needs no argparse CLI", "helper.py: no argparse CLI", False),
    ("helper needs no __main__ guard", "helper.py: missing __main__ guard", False),
    ("helper is exempt from the line floor", "helper.py: 7 lines (under", False),
    ("entry-point tool still hits the line floor", "tool.py: 12 lines (under", True),
    ("third-party import still errors", "rogue.py: non-stdlib import 'requests'", True),
    ("cross-skill import still errors", "reacher.py: relative import", True),
)


def module_imports(tree: ast.Module) -> Tuple[List[str], List[str]]:
    """Return imported root module names and relative imports that leave scripts/."""
    roots: List[str] = []
    escapes: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots += [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level > 1:
                escapes.append("." * node.level + (node.module or ""))
            elif node.module:
                roots.append(node.module.split(".")[0])
    return roots, escapes


def check_scripts(skill: Path, rules: Dict[str, Any]) -> List[Finding]:
    """Validate scripts for size, CLI shape, and permitted imports.

    A module that a sibling script imports and that carries no ``__main__`` guard
    is a local helper library rather than a user-invoked tool, so Pattern 7's CLI
    requirements do not apply to it. Modules resolving to a ``.py`` file in the
    skill's own scripts/ directory are permitted under Pattern 9; anything else
    that is not standard library remains an error.
    """
    out: List[Finding] = []
    scripts = sorted((skill / "scripts").glob("*.py"))
    if not scripts:
        return [Finding("P7", "warn", "no scripts/ — skills without tools rarely clear the quality bar")]
    stdlib = getattr(sys, "stdlib_module_names", frozenset())
    local = {script.stem for script in scripts}
    texts = {script: script.read_text(encoding="utf-8", errors="replace") for script in scripts}
    trees: Dict[Path, Optional[ast.Module]] = {}
    for script in scripts:
        try:
            trees[script] = ast.parse(texts[script])
        except SyntaxError as exc:
            out.append(Finding("P7", "error", f"{script.name}: syntax error at line {exc.lineno}"))
            trees[script] = None
    helpers = {root for script, tree in trees.items() if tree
               for root in module_imports(tree)[0] if root in local and root != script.stem}

    for script in scripts:
        text = texts[script]
        count = len(text.splitlines())
        is_helper = script.stem in helpers and MAIN_GUARD not in text
        # The floor exists to catch thin-wrapper *tools* that add nothing a user
        # could not do by hand. A helper is sized by the thing it holds — a
        # complete 75-line rule table is not missing functionality. The ceiling
        # still applies: an oversized helper should be split like anything else.
        if count < rules["script_min_lines"] and not is_helper:
            out.append(Finding("P7", "warn", f"{script.name}: {count} lines (under {rules['script_min_lines']})"))
        if count > rules["script_max_lines"]:
            out.append(Finding("P7", "error", f"{script.name}: {count} lines (over {rules['script_max_lines']})"))
        for token, severity, label in (() if is_helper else CLI_CHECKS):
            if token not in text:
                out.append(Finding("P7", severity, f"{script.name}: {label}"))
        tree = trees[script]
        if tree is None:
            continue
        roots, escapes = module_imports(tree)
        out += [Finding("P9", "error", f"{script.name}: relative import '{esc}' leaves the skill directory")
                for esc in escapes]
        for root in roots:
            if stdlib and root not in stdlib and root not in local:
                out.append(Finding("P7", "error", f"{script.name}: non-stdlib import '{root}'"))
    return out


def run_selftest() -> Dict[str, Any]:
    """Lint a throwaway fixture package to prove helper handling stays precise."""
    with tempfile.TemporaryDirectory() as tmp:
        scripts = Path(tmp) / "scripts"
        scripts.mkdir(parents=True)
        for name, body in SELFTEST_FILES.items():
            (scripts / name).write_text(body, encoding="utf-8")
        # Collect every severity: some behaviour under test (the line floor, the
        # --format flag) is reported as a warning, and filtering to errors here
        # would silently make those cases unfalsifiable.
        found = [f.message for f in check_scripts(Path(tmp), DEFAULT_RULES)]
    cases = [{"case": label, "expected": expected, "passed": any(needle in m for m in found) == expected}
             for label, needle, expected in SELFTEST_CASES]
    passed = all(case["passed"] for case in cases)
    return {"skill": "selftest", "path": "<temp fixture>", "passed": passed,
            "errors": sum(1 for case in cases if not case["passed"]), "warnings": 0,
            "findings": [{"pattern": "P7", "severity": "error" if not c["passed"] else "info",
                          "message": f"{c['case']}: {'ok' if c['passed'] else 'REGRESSED'}"} for c in cases]}


def lint_skill(skill_path: str, rules: Dict[str, Any]) -> Dict[str, Any]:
    """Run every pattern check against a skill folder and return a structured report."""
    skill = Path(skill_path)
    if not skill.is_dir():
        raise SystemExit(f"error: not a directory: {skill_path}")
    doc = skill / "SKILL.md"
    if not doc.is_file():
        raise SystemExit(f"error: no SKILL.md in {skill_path}")
    text = doc.read_text(encoding="utf-8", errors="replace")
    fm, body_start = parse_frontmatter(text)
    body = "\n".join(text.splitlines()[body_start:])

    findings: List[Finding] = []
    findings += check_frontmatter(fm, skill.name, rules)
    findings += check_body(body, rules, len(text.splitlines()))
    findings += check_scripts(skill, rules)
    findings += check_structure(skill, rules)
    findings.sort(key=lambda f: (SEVERITY_ORDER[f.severity], f.pattern))

    errors = sum(1 for f in findings if f.severity == "error")
    return {
        "skill": skill.name, "path": str(skill), "passed": errors == 0, "errors": errors,
        "warnings": sum(1 for f in findings if f.severity == "warn"),
        "findings": [asdict(f) for f in findings],
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the lint report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    status = "PASS" if report["passed"] else "FAIL"
    print(f"{status}  {report['skill']}  ({report['errors']} errors, {report['warnings']} warnings)")
    if not report["findings"]:
        print("  clean — every pattern check passed")
        return
    for item in report["findings"]:
        print(f"  [{item['severity']:5}] {item['pattern']}  {item['message']}")


def main() -> None:
    """Parse arguments, lint the skill, and exit non-zero on any error finding."""
    parser = argparse.ArgumentParser(description="Lint a skill package against the authoring standard.")
    parser.add_argument("--skill", help="path to the skill folder containing SKILL.md")
    parser.add_argument("--rules", help="optional JSON file overriding the default thresholds")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--selftest", action="store_true", help="lint built-in fixtures instead of a skill folder")
    args = parser.parse_args()
    if not args.skill and not args.selftest:
        parser.error("one of --skill or --selftest is required")
    try:
        report = run_selftest() if args.selftest else lint_skill(args.skill, load_rules(args.rules))
        output(report, args.format)
    except OSError as exc:
        print(f"error: could not read skill package: {exc}", file=sys.stderr)
        sys.exit(1)
    failed = not report["passed"] or (args.strict and report["warnings"] > 0)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
