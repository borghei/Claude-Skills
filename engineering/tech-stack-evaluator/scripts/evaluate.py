#!/usr/bin/env python3
"""Command-line entry point for the tech-stack-evaluator modules.

The analysis modules in this folder are libraries; this script loads a JSON input file,
runs one analysis and prints text or JSON. It adds the guard the libraries lack: a weighted
comparison is only as good as its scores, so every category score in `compare` must carry
an `evidence` note (a source, benchmark or measured fact). Scores without evidence are
reported, and the run fails, rather than being laundered into a confident-looking total.

Usage:
  python scripts/evaluate.py compare assets/sample_compare_evidenced.json
  python scripts/evaluate.py compare assets/sample_input_structured.json --format json
  python scripts/evaluate.py tco assets/sample_input_tco.json
  python scripts/evaluate.py ecosystem assets/sample_input_ecosystem.json
  python scripts/evaluate.py parse assets/sample_input_text.json   # free text -> structured request

Exit codes:
  0  analysis ran and (compare) every score has evidence and the winner is clear
  1  compare: one or more scores lack evidence, or the top two are within --margin points
  2  bad input: file missing, invalid JSON, or the expected section is absent
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
import os  # noqa: E402
import importlib.util as _ilu  # noqa: E402


def _sibling(name):
    """Load a sibling script as a module (keeps each script standalone)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = _ilu.spec_from_file_location(name, path)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


EcosystemAnalyzer = _sibling("ecosystem_analyzer").EcosystemAnalyzer
FormatDetector = _sibling("format_detector").FormatDetector
MigrationAnalyzer = _sibling("migration_analyzer").MigrationAnalyzer
SecurityAssessor = _sibling("security_assessor").SecurityAssessor
StackComparator = _sibling("stack_comparator").StackComparator
TCOCalculator = _sibling("tco_calculator").TCOCalculator



SECTIONS = {
    "compare": "comparison",
    "tco": "tco_analysis",
    "ecosystem": "ecosystem",
    "security": "security",
    "migration": "migration",
}
REQUIRED = {
    "compare": ["technologies"],
    "tco": ["initial_costs", "operational_costs"],
    "ecosystem": ["technology"],
    "security": ["technology"],
    "migration": ["source_technology", "target_technology"],
}


def fail(message: str) -> None:
    """Print a one-line error and exit 2."""
    print(f"error: {message}", file=sys.stderr)
    sys.exit(2)


def load_request(path: str) -> Dict[str, Any]:
    """Parse a free-text or JSON request (a file, or a JSON object with an 'input' string)."""
    file = Path(path)
    if not file.is_file():
        fail(f"input file not found: {path}")
    raw = file.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and isinstance(data.get("input"), str):
            raw = data["input"]
    except json.JSONDecodeError:
        pass
    if not raw.strip():
        fail(f"{path} is empty")
    return FormatDetector(raw).parse()


def load_section(path: str, command: str) -> Dict[str, Any]:
    """Load the input file and return the section the command needs."""
    file = Path(path)
    if not file.is_file():
        fail(f"input file not found: {path}")
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {path}: {exc}")
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON (line {exc.lineno}): {exc.msg}")
    if not isinstance(data, dict):
        fail(f"{path} must contain a JSON object")
    section = data.get(SECTIONS[command], data)
    if not isinstance(section, dict):
        fail(f"'{SECTIONS[command]}' must be a JSON object")
    missing = [key for key in REQUIRED[command] if key not in section]
    if missing:
        fail(f"{path}: '{SECTIONS[command]}' is missing {', '.join(missing)}")
    return section


def evidence_gaps(technologies: List[Dict[str, Any]]) -> List[str]:
    """Return 'Tech.category' for every scored category without an evidence note."""
    gaps = []
    for tech in technologies:
        for category in StackComparator.DEFAULT_WEIGHTS:
            entry = tech.get(category)
            if isinstance(entry, dict) and "score" in entry and not str(entry.get("evidence", "")).strip():
                gaps.append(f"{tech.get('name', '?')}.{category}")
    return gaps


def run_compare(section: Dict[str, Any], margin: float) -> Tuple[Dict[str, Any], int]:
    techs = section["technologies"]
    if not isinstance(techs, list) or len(techs) < 2:
        fail("'technologies' must list at least two candidates")
    result = StackComparator(section).compare_technologies(techs)
    totals = sorted(((v["weighted_total"], k) for k, v in result["technologies"].items()), reverse=True)
    gap = round(totals[0][0] - totals[1][0], 1)
    gaps = evidence_gaps(techs)
    verdict = "CLEAR"
    if gaps:
        verdict = "UNSUPPORTED"
    elif gap < margin:
        verdict = "TOO_CLOSE"
    result.update({"verdict": verdict, "score_gap": gap, "unsupported_scores": gaps})
    return result, 0 if verdict == "CLEAR" else 1


def run_other(command: str, section: Dict[str, Any]) -> Dict[str, Any]:
    if command == "tco":
        return TCOCalculator(section).generate_tco_summary()
    if command == "ecosystem":
        return EcosystemAnalyzer(section).generate_ecosystem_report()
    if command == "security":
        return SecurityAssessor(section).generate_security_report()
    return MigrationAnalyzer(section).generate_migration_plan()


def render_compare(result: Dict[str, Any]) -> str:
    lines = ["Weighted comparison", "-" * 40]
    ranked = sorted(result["technologies"].items(), key=lambda kv: kv[1]["weighted_total"], reverse=True)
    for name, data in ranked:
        lines.append(f"  {name:<20} {data['weighted_total']:6.1f}   strengths: {', '.join(data['strengths']) or '-'}")
    lines.append(f"Score gap: {result['score_gap']} points   Verdict: {result['verdict']}")
    if result["verdict"] == "CLEAR":
        lines.append(f"Recommendation: {result['recommendation']}")
    elif result["verdict"] == "TOO_CLOSE":
        lines.append("No recommendation: the gap is within the margin; decide on constraints the scores do not capture.")
    else:
        lines.append("No recommendation: these scores have no evidence attached:")
        lines += [f"  - {item}" for item in result["unsupported_scores"]]
    return "\n".join(lines)


def render_generic(result: Any, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(result, dict):
        out = []
        for key, value in result.items():
            if isinstance(value, (dict, list)):
                out.append(f"{pad}{key}:")
                out.append(render_generic(value, indent + 1))
            else:
                out.append(f"{pad}{key}: {value}")
        return "\n".join(out)
    if isinstance(result, list):
        return "\n".join(f"{pad}- {item}" if not isinstance(item, (dict, list))
                         else render_generic(item, indent) for item in result)
    return f"{pad}{result}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tech-stack evaluation from a JSON input file.")
    parser.add_argument("command", choices=sorted(SECTIONS) + ["parse"], help="analysis to run")
    parser.add_argument("input", help="JSON input file (see assets/ for each shape)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    parser.add_argument("--margin", type=float, default=5.0,
                        help="compare: minimum score gap (points) for a clear winner (default 5)")
    args = parser.parse_args()

    if args.command == "parse":
        result = load_request(args.input)
        print(json.dumps(result, indent=2) if args.format == "json" else render_generic(result))
        return
    section = load_section(args.input, args.command)
    code = 0
    try:
        if args.command == "compare":
            result, code = run_compare(section, args.margin)
        else:
            result = run_other(args.command, section)
    except (TypeError, ValueError, KeyError, AttributeError, ZeroDivisionError) as exc:
        fail(f"input has the wrong shape for '{args.command}': {exc}")

    if args.format == "json":
        print(json.dumps(result, indent=2, default=str))
    elif args.command == "compare":
        print(render_compare(result))
    else:
        print(render_generic(result))
    sys.exit(code)


if __name__ == "__main__":
    main()
