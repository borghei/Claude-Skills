#!/usr/bin/env python3
"""Lint a skill package against the 11-pattern skill-authoring standard.

Checks frontmatter, description budget, SKILL.md length, required sections,
anti-pattern count, confidence tagging, structure, script line counts, and
stdlib-only imports, emitting a per-pattern pass/fail report.

Usage:
  python3 skill_lint.py --skill engineering/write-a-skill --format json
  python3 skill_lint.py --skill <dir> --rules assets/sample_lint_rules.json --strict
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_RULES: Dict[str, Any] = {
    "description_max_chars": 240, "skill_md_max_lines": 500, "reference_max_lines": 800,
    "script_min_lines": 150, "script_max_lines": 300, "min_anti_patterns": 3,
    "required_frontmatter": ["name", "description", "license"],
    "required_metadata": ["version", "author", "category", "domain", "updated", "tags"],
    "required_sections": ["when to use", "workflow", "anti-pattern", "files"],
    "generative_markers": ["clarify first"],
}

CONFIDENCE_TAGS = ("[PROVEN]", "[RECOMMENDED]", "[EXPERIMENTAL]")
STOP_RULE_HINT = "if the user says"
SEVERITY_ORDER = {"error": 0, "warn": 1, "info": 2}


@dataclass
class Finding:
    """A single lint result tied to one authoring pattern."""

    pattern: str
    severity: str
    message: str


def load_rules(path: Optional[str]) -> Dict[str, Any]:
    """Return the default rule set, overlaid with an optional JSON rules file."""
    rules = dict(DEFAULT_RULES)
    if not path:
        return rules
    try:
        overrides = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: rules file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: rules file is not valid JSON ({path}): {exc}")
    if not isinstance(overrides, dict):
        raise SystemExit("error: rules file must contain a JSON object")
    rules.update(overrides)
    return rules


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], int]:
    """Parse the leading YAML frontmatter block into a dict of scalars and lists.

    Handles the subset of YAML used by skill packages: flat scalars, folded
    (``>``) blocks, one level of nesting under ``metadata``, inline ``[a, b]``
    lists, and dash lists. Returns the mapping and the line the body starts on.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, 0
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), -1)
    if end == -1:
        return {}, 0

    data: Dict[str, Any] = {}
    parent: Optional[str] = None
    key: Optional[str] = None
    folded: Optional[List[str]] = None

    def flush() -> None:
        if key is not None and folded is not None:
            target = data.setdefault(parent, {}) if parent else data
            target[key] = " ".join(part.strip() for part in folded).strip()

    for raw in lines[1:end]:
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()

        if folded is not None:
            if indent > 0 and not stripped.startswith("- "):
                folded.append(stripped)
                continue
            flush()
            folded = None

        if stripped.startswith("- "):
            item = stripped[2:].strip().strip("'\"")
            target = data.setdefault(parent, {}) if parent and key else data
            existing = target.get(key)
            target[key] = existing + [item] if isinstance(existing, list) else [item]
            continue
        if ":" not in stripped:
            continue

        name, _, value = stripped.partition(":")
        name, value = name.strip(), value.strip()
        if indent == 0:
            parent = None
        if value in (">", "|"):
            key, folded = name, []
            continue
        if value == "":
            if indent == 0:
                parent, key = name, None
                data.setdefault(name, {})
            else:
                key = name
                data.setdefault(parent, {})[name] = []
            continue
        parsed: Any = value.strip("'\"")
        if parsed.startswith("[") and parsed.endswith("]"):
            parsed = [p.strip().strip("'\"") for p in parsed[1:-1].split(",") if p.strip()]
        (data.setdefault(parent, {}) if parent and indent > 0 else data)[name] = parsed
        key, folded = name, None
    flush()
    return data, end + 1


def check_frontmatter(fm: Dict[str, Any], folder: str, rules: Dict[str, Any]) -> List[Finding]:
    """Validate frontmatter fields, naming, and the description token budget."""
    out: List[Finding] = []
    if not fm:
        return [Finding("P2", "error", "SKILL.md has no parseable YAML frontmatter block")]
    meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    for scope, block, names in (("frontmatter", fm, rules["required_frontmatter"]),
                                ("metadata", meta, rules["required_metadata"])):
        for field_name in names:
            if not block.get(field_name):
                out.append(Finding("P2", "error", f"{scope} missing required field: {field_name}"))
    if fm.get("name") and fm["name"] != folder:
        out.append(Finding("P2", "error", f"name '{fm['name']}' does not match folder '{folder}'"))

    desc, limit = str(fm.get("description") or ""), rules["description_max_chars"]
    if len(desc) > limit:
        out.append(Finding("P1", "error", f"description is {len(desc)} chars (budget {limit})"))
    if desc and "use when" not in desc.lower():
        out.append(Finding("P1", "warn", "description has no 'Use when ...' trigger clause"))
    readable = folder.replace("-", " ")
    if "-" in folder and readable in desc.lower()[:60]:
        out.append(Finding("P1", "warn", "description restates the skill name — spend those tokens on triggers"))
    return out


def check_body(body: str, rules: Dict[str, Any], line_count: int) -> List[Finding]:
    """Validate SKILL.md length, required sections, anti-patterns, and tagging."""
    out: List[Finding] = []
    lowered = body.lower()
    if line_count > rules["skill_md_max_lines"]:
        out.append(Finding("P3", "error", f"SKILL.md is {line_count} lines (max {rules['skill_md_max_lines']})"))
    for section in rules["required_sections"]:
        if section not in lowered:
            out.append(Finding("P8", "error", f"missing required section: '{section}'"))
    anti = len(re.findall(r"^\*\*Mistake:\*\*", body, re.MULTILINE))
    if anti < rules["min_anti_patterns"]:
        out.append(Finding("P5", "error", f"{anti} anti-patterns found (minimum {rules['min_anti_patterns']})"))
    if not any(tag in body for tag in CONFIDENCE_TAGS):
        out.append(Finding("P6", "warn", "no confidence tags ([PROVEN]/[RECOMMENDED]/[EXPERIMENTAL])"))
    if any(m in lowered for m in rules["generative_markers"]) and STOP_RULE_HINT not in lowered:
        out.append(Finding("P11", "error", "Clarify First section present but the stop rule is missing"))
    if not re.search(r"```bash", body):
        out.append(Finding("P8", "warn", "no runnable bash block — workflows should invoke a script"))
    for match in re.finditer(r"(?<![\"'`])see the [a-z0-9/-]+ skill", lowered):
        out.append(Finding("P9", "error", f"cross-skill dependency in prose: '{match.group(0)}'"))
    return out


def check_scripts(skill: Path, rules: Dict[str, Any]) -> List[Finding]:
    """Validate every script for line count, argparse, formats, and stdlib-only imports."""
    out: List[Finding] = []
    scripts = sorted((skill / "scripts").glob("*.py"))
    if not scripts:
        out.append(Finding("P7", "warn", "no scripts/ — skills without tools rarely clear the quality bar"))
        return out
    stdlib = getattr(sys, "stdlib_module_names", frozenset())
    for script in scripts:
        text = script.read_text(encoding="utf-8", errors="replace")
        count = len(text.splitlines())
        if count < rules["script_min_lines"]:
            out.append(Finding("P7", "warn", f"{script.name}: {count} lines (under {rules['script_min_lines']})"))
        if count > rules["script_max_lines"]:
            out.append(Finding("P7", "error", f"{script.name}: {count} lines (over {rules['script_max_lines']})"))
        for token, severity, label in (("argparse", "error", "no argparse CLI"),
                                       ("--format", "warn", "no --format flag (text/json required)"),
                                       ('__name__ == "__main__"', "error", "missing __main__ guard")):
            if token not in text:
                out.append(Finding("P7", severity, f"{script.name}: {label}"))
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            out.append(Finding("P7", "error", f"{script.name}: syntax error at line {exc.lineno}"))
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots = [node.module.split(".")[0]]
            else:
                continue
            for root in roots:
                if stdlib and root not in stdlib:
                    out.append(Finding("P7", "error", f"{script.name}: non-stdlib import '{root}'"))
    return out


def check_structure(skill: Path, rules: Dict[str, Any]) -> List[Finding]:
    """Validate package layout, reference length, and asset presence."""
    out: List[Finding] = []
    out += [Finding("P8", "warn", f"no {d}/ directory") for d in ("references", "assets") if not (skill / d).is_dir()]
    for ref in sorted((skill / "references").glob("*.md")):
        count = len(ref.read_text(encoding="utf-8", errors="replace").splitlines())
        if count > rules["reference_max_lines"]:
            out.append(Finding("P3", "error", f"references/{ref.name}: {count} lines (max {rules['reference_max_lines']})"))
    if (skill / "assets").is_dir() and not any((skill / "assets").glob("sample_*.json")):
        out.append(Finding("P8", "warn", "assets/ has no sample_*.json — workflows are not runnable as written"))
    for nested in skill.iterdir():
        if not nested.is_dir() or nested.name.startswith((".", "__")):
            continue
        if any(c.is_dir() and not c.name.startswith((".", "__")) for c in nested.iterdir()):
            out.append(Finding("P8", "warn", f"{nested.name}/ has nested subdirectories — keep each directory flat"))
    return out


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
    parser.add_argument("--skill", required=True, help="path to the skill folder containing SKILL.md")
    parser.add_argument("--rules", help="optional JSON file overriding the default thresholds")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()
    try:
        report = lint_skill(args.skill, load_rules(args.rules))
        output(report, args.format)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not read skill package: {exc}", file=sys.stderr)
        sys.exit(1)
    failed = not report["passed"] or (args.strict and report["warnings"] > 0)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
