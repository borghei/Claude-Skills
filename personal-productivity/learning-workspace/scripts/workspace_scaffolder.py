#!/usr/bin/env python3
"""Validate a learning-workspace spec and scaffold the workspace files from it.

The spec names the topic, the real-world reason for learning it, observable
success criteria, session constraints, prior knowledge, a module list with
dependencies, and starting resources. The tool gates the spec first (a vague
"why", unobservable success criteria, broken module dependencies) and only
writes files when the spec passes. Nothing is overwritten without --force.

Usage:
    python3 workspace_scaffolder.py --input assets/sample_workspace_spec.json
    python3 workspace_scaffolder.py --input spec.json --output-dir ~/learn/stats
    python3 workspace_scaffolder.py --input spec.json --output-dir ws --force --format json

Exit codes: 0 spec valid (and files written if --output-dir), 1 spec failed the
gate, 2 unreadable input, bad arguments, or files exist without --force.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

VAGUE_WHY = re.compile(r"^\s*(to\s+)?(understand|learn( about)?|know( more)?( about)?|get better at|be familiar with)\b",
                       re.IGNORECASE)
UNOBSERVABLE = re.compile(r"\b(understand|know|be familiar|appreciate|grasp|be comfortable|learn)\b", re.IGNORECASE)
MAX_MODULES = 12


class InputError(Exception):
    """Raised when the spec cannot be read or has the wrong shape."""


def load_spec(path: Path) -> Dict[str, Any]:
    """Read the spec JSON and check its top-level shape."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise InputError(f"spec not found: {path}")
    except json.JSONDecodeError as exc:
        raise InputError(f"spec is not valid JSON ({path}): {exc}")
    if not isinstance(data, dict):
        raise InputError("spec must be a JSON object")
    for key in ("modules", "success", "resources", "prior_knowledge"):
        if key in data and not isinstance(data[key], list):
            raise InputError(f"'{key}' must be a list")
    return data


def slugify(text: str) -> str:
    """Return a lowercase dash-case slug for file names."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:48] or "lesson"


def find_cycle(modules: List[Dict[str, Any]]) -> List[str]:
    """Return one dependency cycle among modules as a list of ids, or []."""
    graph = {m.get("id"): list(m.get("depends_on") or []) for m in modules}
    state: Dict[str, int] = {}
    stack: List[str] = []

    def visit(node: str) -> List[str]:
        state[node] = 1
        stack.append(node)
        for dep in graph.get(node, []):
            if dep not in graph:
                continue
            if state.get(dep) == 1:
                return stack[stack.index(dep):] + [dep]
            if state.get(dep) is None:
                found = visit(dep)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return []

    for node in sorted(graph, key=str):
        if state.get(node) is None:
            found = visit(node)
            if found:
                return [str(n) for n in found]
    return []


def validate(spec: Dict[str, Any]) -> List[Dict[str, str]]:
    """Gate the spec and return findings with severity error or warn."""
    out: List[Dict[str, str]] = []

    def add(sev: str, field: str, msg: str) -> None:
        out.append({"severity": sev, "field": field, "message": msg})

    if not str(spec.get("topic", "")).strip():
        add("error", "topic", "no topic named")
    why = str(spec.get("why", "")).strip()
    if not why:
        add("error", "why", "no reason for learning — every lesson is chosen against it")
    elif VAGUE_WHY.match(why) and len(why.split()) < 12:
        add("error", "why", f"'{why}' restates the topic; name the outcome that changes when you have the skill")
    success = [str(s) for s in spec.get("success") or []]
    if not success:
        add("error", "success", "no success criteria — there is no way to tell when the mission is done")
    for i, crit in enumerate(success, 1):
        if UNOBSERVABLE.search(crit):
            add("error", f"success[{i}]", f"'{crit}' is not observable; describe something you could be watched doing")
    modules = spec.get("modules") or []
    if not modules:
        add("error", "modules", "no modules — the curriculum is empty")
    ids = [m.get("id") for m in modules if isinstance(m, dict)]
    if len(ids) != len(set(ids)):
        add("error", "modules", "duplicate module ids")
    for m in modules:
        if not isinstance(m, dict) or not m.get("id") or not m.get("title"):
            add("error", "modules", f"module missing id or title: {m!r}")
            continue
        if not str(m.get("outcome", "")).strip():
            add("error", f"modules.{m['id']}", "no outcome — a module must end in something you can do")
        for dep in m.get("depends_on") or []:
            if dep not in ids:
                add("error", f"modules.{m['id']}", f"depends on unknown module '{dep}'")
    cycle = find_cycle([m for m in modules if isinstance(m, dict)])
    if cycle:
        add("error", "modules", "dependency cycle: " + " -> ".join(cycle))
    if len(modules) > MAX_MODULES:
        add("warn", "modules", f"{len(modules)} modules; past {MAX_MODULES} the plan outruns the feedback")
    resources = spec.get("resources") or []
    if not resources:
        add("warn", "resources", "no resources — lessons will lean on unverified recall")
    elif not any(r.get("trust") == "primary" for r in resources if isinstance(r, dict)):
        add("warn", "resources", "no primary-source resource; ground lessons in one before teaching from memory")
    if not any(r.get("kind") == "community" for r in resources if isinstance(r, dict)):
        add("warn", "resources", "no community listed — practice against real people is where judgment forms")
    cons = spec.get("constraints") or {}
    if not cons.get("minutes_per_session"):
        add("warn", "constraints", "no session length; lessons default to 25 minutes")
    return out


def render_files(spec: Dict[str, Any]) -> Dict[str, str]:
    """Build the workspace file contents keyed by relative path."""
    topic = spec.get("topic", "Untitled topic")
    cons = spec.get("constraints") or {}
    minutes = cons.get("minutes_per_session", 25)
    modules = spec.get("modules") or []
    success = "\n".join(f"- [ ] {s}" for s in spec.get("success") or [])
    prior = "\n".join(f"- {p}" for p in spec.get("prior_knowledge") or []) or "- None stated yet"
    mission = (f"# Mission: {topic}\n\n## Why\n{spec.get('why', '')}\n\n## Success looks like\n{success}\n\n"
               f"## Constraints\n- Session length: {minutes} min\n"
               f"- Sessions per week: {cons.get('sessions_per_week', 'not set')}\n"
               f"- Target date: {cons.get('deadline', 'none')}\n\n## Prior knowledge (claimed)\n{prior}\n\n"
               "## Mission changes\n| Date | Change | Why |\n|---|---|---|\n")
    rows = "\n".join(f"| {m.get('id')} | {m.get('title')} | {m.get('outcome', '')} | "
                     f"{', '.join(m.get('depends_on') or []) or '-'} | todo |" for m in modules)
    curriculum = (f"# Curriculum: {topic}\n\nOrdered by dependency. One module spans several lessons; "
                  "a module is done when its outcome has been shown, not covered.\n\n"
                  f"| Module | Title | Outcome (observable) | Needs | Status |\n|---|---|---|---|---|\n{rows}\n")
    res_rows = "\n".join(f"| {r.get('title')} | {r.get('kind', '')} | {r.get('trust', '')} | "
                         f"{r.get('url', '')} | {r.get('use_for', '')} |"
                         for r in spec.get("resources") or [] if isinstance(r, dict))
    resources = (f"# Resources: {topic}\n\n| Title | Kind | Trust | Link | Use for |\n|---|---|---|---|---|\n"
                 f"{res_rows}\n")
    record = {"topic": topic, "mission": spec.get("why", ""),
              "modules": [{"id": m.get("id"), "title": m.get("title"), "status": "todo",
                           "depends_on": m.get("depends_on") or []} for m in modules],
              "sessions": [], "items": [], "misconceptions": []}
    first = modules[0] if modules else {"title": "orientation", "outcome": ""}
    lesson = (f"# Lesson 0001: {first.get('title')}\n\nModule: {first.get('id', '-')} | Planned: {minutes} min\n\n"
              f"## Win for this lesson\n{first.get('outcome', '')}\n\n## Warm-up (retrieval, no notes)\n- \n\n"
              "## Core idea\n\n## Worked example\n\n## Practice (with feedback)\n1. \n2. \n3. \n\n"
              "## Exit check\n- Explain-back:\n- Transfer question:\n\n## Primary source\n- \n\n"
              "## Record after the lesson\n- Items introduced:\n- Misconceptions surfaced:\n")
    return {
        "MISSION.md": mission, "CURRICULUM.md": curriculum, "RESOURCES.md": resources,
        "GLOSSARY.md": f"# Glossary: {topic}\n\n| Term | Meaning in this workspace | First lesson |\n|---|---|---|\n",
        "NOTES.md": "# Notes\n\nTeaching preferences, constraints and working notes.\n",
        "learning-record.json": json.dumps(record, indent=2) + "\n",
        f"lessons/0001-{slugify(str(first.get('title')))}.md": lesson,
    }


def write_files(files: Dict[str, str], out_dir: Path, force: bool) -> List[str]:
    """Write files under out_dir, refusing to clobber existing ones unless forced."""
    clashes = [rel for rel in files if (out_dir / rel).exists()]
    if clashes and not force:
        raise InputError("refusing to overwrite existing files (use --force): " + ", ".join(sorted(clashes)))
    for rel, body in files.items():
        target = out_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return sorted(files)


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Learning workspace spec: {report['topic']}  [{'PASS' if report['passed'] else 'FAIL'}]")
    for f in report["findings"]:
        print(f"  [{f['severity']:5}] {f['field']}: {f['message']}")
    if not report["findings"]:
        print("  spec clean")
    label = "Written" if report["written"] else ("Would write" if report["passed"] else "Not written (spec failed)")
    print(f"{label} ({len(report['files'])} files){': ' + report['output_dir'] if report['written'] else ''}")
    for rel in report["files"]:
        print(f"  {rel}")


def main() -> None:
    """Parse arguments, gate the spec, and scaffold when it passes."""
    parser = argparse.ArgumentParser(description="Validate a learning-workspace spec and scaffold its files.")
    parser.add_argument("--input", required=True, help="workspace spec JSON")
    parser.add_argument("--output-dir", help="directory to scaffold into (omit for a dry run)")
    parser.add_argument("--force", action="store_true", help="overwrite files that already exist")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    try:
        spec = load_spec(Path(args.input))
        findings = validate(spec)
        passed = not any(f["severity"] == "error" for f in findings)
        files = render_files(spec)
        written = False
        if passed and args.output_dir:
            write_files(files, Path(args.output_dir).expanduser(), args.force)
            written = True
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    except OSError as exc:
        print(f"error: could not write workspace: {exc}", file=sys.stderr)
        sys.exit(2)
    report = {"topic": spec.get("topic", ""), "passed": passed, "findings": findings,
              "files": sorted(files), "written": written, "output_dir": args.output_dir or ""}
    output(report, args.format)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
