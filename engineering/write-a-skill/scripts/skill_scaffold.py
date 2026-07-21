#!/usr/bin/env python3
"""Scaffold a standard-compliant skill package from a JSON spec.

Writes SKILL.md with every required section stubbed in order, plus references/,
scripts/, and assets/ placeholders. The output lints clean structurally, so the
author only fills in domain content.

Usage:
  python3 skill_scaffold.py --input assets/sample_skill_spec.json --out engineering
  python3 skill_scaffold.py --input assets/sample_skill_spec.json --dry-run --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

REQUIRED_SPEC_FIELDS = ("name", "title", "description", "category", "domain")
MAX_DESCRIPTION_CHARS = 240

STOP_RULE = (
    'Stop rule: ask only the 2-3 that most change the output. If the user says '
    '"just draft it," proceed and list your assumptions at the top of the artifact.'
)


def load_spec(path: str) -> Dict[str, Any]:
    """Read and validate the scaffold spec JSON."""
    try:
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: spec file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: spec is not valid JSON ({path}): {exc}")
    if not isinstance(spec, dict):
        raise SystemExit("error: spec must be a JSON object")
    missing = [f for f in REQUIRED_SPEC_FIELDS if not spec.get(f)]
    if missing:
        raise SystemExit(f"error: spec missing required fields: {', '.join(missing)}")
    if len(str(spec["description"])) > MAX_DESCRIPTION_CHARS:
        raise SystemExit(
            f"error: description is {len(str(spec['description']))} chars; "
            f"trim to {MAX_DESCRIPTION_CHARS} before scaffolding"
        )
    if "use when" not in str(spec["description"]).lower():
        raise SystemExit("error: description needs a 'Use when <trigger>, <trigger>' clause")
    return spec


def render_frontmatter(spec: Dict[str, Any]) -> List[str]:
    """Build the YAML frontmatter block for the new SKILL.md."""
    tags = spec.get("tags") or [spec["domain"], spec["category"]]
    return [
        "---",
        f"name: {spec['name']}",
        "description: >",
        f"  {spec['description']}",
        f"license: {spec.get('license', 'MIT + Commons Clause')}",
        "metadata:",
        f"  version: {spec.get('version', '1.0.0')}",
        f"  author: {spec.get('author', 'borghei')}",
        f"  category: {spec['category']}",
        f"  domain: {spec['domain']}",
        f"  updated: {spec.get('updated', date.today().isoformat())}",
        f"  tags: [{', '.join(str(t) for t in tags)}]",
        "---",
        "",
    ]


def render_body(spec: Dict[str, Any]) -> List[str]:
    """Build the SKILL.md body with all required sections in standard order."""
    generative = bool(spec.get("generative", True))
    scripts: List[str] = list(spec.get("scripts") or ["analyzer.py", "validator.py"])
    lines: List[str] = [
        f"# {spec['title']}",
        "",
        f"TODO: two to three sentences framing what this skill does for {spec['domain']} work,",
        "who reads the output, and what decision it informs.",
        "",
        "## When to use this skill",
        "",
    ]
    for hint in spec.get("use_when") or ["TODO situation"] * 5:
        lines.append(f"- **{hint}**")
    lines += ["", "## Inputs the skill expects", ""]
    for hint in spec.get("inputs") or ["TODO input"] * 4:
        lines.append(f"- {hint}")

    if generative:
        lines += [
            "",
            "## Clarify First",
            "",
            "Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:",
            "",
            "- [ ] **TODO input 1** — why it changes the output",
            "- [ ] **TODO input 2** — why it changes the output",
            "- [ ] **TODO input 3** — why it changes the output",
            "",
            STOP_RULE,
        ]

    lines += ["", "## Workflows", ""]
    for index in range(1, 4):
        script = scripts[min(index - 1, len(scripts) - 1)]
        lines += [
            f"### Workflow {index} — TODO name",
            "",
            "1. TODO first step.",
            "2. TODO second step.",
            "3. TODO third step.",
            "",
            "```bash",
            f"python3 {spec['category']}/{spec['name']}/scripts/{script} \\",
            f"  --input {spec['category']}/{spec['name']}/assets/sample_input.json --format text",
            "```",
            "",
        ]

    lines += [
        "## Decision frameworks",
        "",
        "| Situation | Do this | Threshold |",
        "|-----------|---------|-----------|",
        "| TODO | TODO | TODO real number |",
        "",
        "## Anti-Patterns",
        "",
    ]
    for index in range(1, 4):
        lines += [
            f"### TODO anti-pattern {index}",
            "**Mistake:** TODO what people actually do.",
            "**Why it happens:** TODO the reasonable-sounding root cause.",
            "**Instead:** TODO the specific corrective action.",
            "",
        ]

    lines += ["## Files", "", "| File | Purpose |", "|------|---------|"]
    for script in scripts:
        lines.append(f"| `scripts/{script}` | TODO one-line purpose |")
    lines.append("| `references/TODO.md` | TODO deep knowledge this offloads from SKILL.md |")
    lines.append("| `assets/sample_input.json` | Runnable sample input for the workflows above |")
    lines.append("")
    return lines


def plan_files(spec: Dict[str, Any]) -> Dict[str, str]:
    """Return a mapping of relative path to file content for the scaffolded package."""
    name = spec["name"]
    files: Dict[str, str] = {
        f"{name}/SKILL.md": "\n".join(render_frontmatter(spec) + render_body(spec)),
        f"{name}/references/TODO.md": f"# {spec['title']} — reference\n\nTODO: 300-800 lines of deep domain knowledge.\n",
        f"{name}/assets/sample_input.json": json.dumps({"TODO": "replace with real sample data"}, indent=2) + "\n",
    }
    for script in spec.get("scripts") or ["analyzer.py", "validator.py"]:
        files[f"{name}/scripts/{script}"] = (
            f'#!/usr/bin/env python3\n"""TODO one-line description.\n\nUsage:\n'
            f"  python3 {script} --input sample_input.json --format json\n\"\"\"\n"
        )
    return files


def write_files(files: Dict[str, str], out_dir: str, force: bool) -> List[str]:
    """Write the planned files to disk, refusing to clobber unless forced."""
    written: List[str] = []
    root = Path(out_dir)
    for rel, content in files.items():
        target = root / rel
        if target.exists() and not force:
            raise SystemExit(f"error: {target} already exists (pass --force to overwrite)")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(str(target))
    return written


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the scaffold result as text or JSON."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return
    verb = "would create" if result["dry_run"] else "created"
    print(f"{result['skill']}: {verb} {len(result['files'])} files")
    for path in result["files"]:
        print(f"  {path}")
    if result["dry_run"]:
        print("\ndry run — nothing written. Re-run without --dry-run to scaffold.")
    else:
        print("\nNext: fill every TODO, then run skill_lint.py --skill <path> --strict")


def main() -> None:
    """Parse arguments, build the package plan, and write or preview it."""
    parser = argparse.ArgumentParser(description="Scaffold a standard-compliant skill package.")
    parser.add_argument("--input", required=True, help="JSON spec describing the skill to scaffold")
    parser.add_argument("--out", default=".", help="directory the skill folder is created in (default: .)")
    parser.add_argument("--dry-run", action="store_true", help="print the planned files without writing")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        spec = load_spec(args.input)
        files = plan_files(spec)
        paths = sorted(str(Path(args.out) / rel) for rel in files) if args.dry_run else write_files(files, args.out, args.force)
        output({"skill": spec["name"], "dry_run": args.dry_run, "files": sorted(paths)}, args.format)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not write scaffold: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
