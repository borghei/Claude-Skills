#!/usr/bin/env python3
"""Command-line entry point for the tdd-guide modules.

Subcommands:
  coverage  Parse an LCOV / Istanbul JSON / Cobertura XML report, list files below the
            threshold with uncovered lines, and exit 1 when any gap remains (a CI gate).
  generate  Turn a requirements JSON (user stories, acceptance criteria, error and edge
            cases) into a framework-specific test file of stubs to fill in.
  quality   Score an existing test file: assertion density, isolation, naming, smells.

Usage:
  python scripts/tdd.py coverage assets/sample_coverage_report.lcov --threshold 80
  python scripts/tdd.py coverage assets/sample_coverage_gaps.lcov --format json
  python scripts/tdd.py generate assets/sample_input_python.json --module discount
  python scripts/tdd.py quality path/to/test_file.py

Exit codes: 0 ok (coverage: every file meets the threshold), 1 coverage gaps found,
2 bad input (missing or unreadable file, unknown report format, invalid JSON).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict


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


CoverageAnalyzer = _sibling("coverage_analyzer").CoverageAnalyzer
FormatDetector = _sibling("format_detector").FormatDetector
MetricsCalculator = _sibling("metrics_calculator").MetricsCalculator
TestFramework = _sibling("test_generator").TestFramework
TestGenerator = _sibling("test_generator").TestGenerator


def fail(message: str) -> None:
    """Print a one-line error and exit 2."""
    print(f"error: {message}", file=sys.stderr)
    sys.exit(2)


def read_text(path: str) -> str:
    file = Path(path)
    if not file.is_file():
        fail(f"file not found: {path}")
    try:
        text = file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {path}: {exc}")
    if not text.strip():
        fail(f"{path} is empty")
    return text


def cmd_coverage(args: argparse.Namespace) -> int:
    content = read_text(args.report)
    fmt = FormatDetector().detect_coverage_format(content)
    if fmt == "unknown":
        fail(f"{args.report}: not an LCOV, Istanbul JSON or Cobertura XML report")
    analyzer = CoverageAnalyzer()
    try:
        analyzer.parse_coverage_report(content, fmt)
    except (ValueError, KeyError, TypeError) as exc:
        fail(f"{args.report}: could not parse {fmt} report: {exc}")
    if not analyzer.coverage_data:
        fail(f"{args.report}: report contains no file entries")
    summary = analyzer.calculate_summary()
    gaps = analyzer.identify_gaps(threshold=args.threshold)
    result = {"format": fmt, "threshold": args.threshold, "summary": summary,
              "gaps": gaps, "recommendations": analyzer.generate_recommendations()}
    if args.format == "json":
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"Coverage ({fmt}): lines {summary['line_coverage']}%  branches "
              f"{summary['branch_coverage']}%  functions {summary['function_coverage']}%")
        if not gaps:
            print(f"All files meet the {args.threshold}% threshold.")
        for gap in gaps:
            print(f"\n  {gap.get('file')}  [{gap.get('priority', '?')}]")
            for key in ("line_coverage", "branch_coverage", "function_coverage"):
                if key in gap:
                    print(f"    {key.replace('_', ' ')}: {gap[key]}%")
            lines = gap.get("uncovered_lines") or []
            if lines:
                shown = ", ".join(str(n) for n in lines[:15])
                print(f"    uncovered lines: {shown}{' ...' if len(lines) > 15 else ''}")
        for rec in result["recommendations"][:5]:
            print(f"  - [{rec.get('priority', '')}] {rec.get('message', rec.get('recommendation', rec))}")
    return 1 if gaps else 0


def load_json(path: str) -> Dict[str, Any]:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON (line {exc.lineno}): {exc.msg}")
    if not isinstance(data, dict):
        fail(f"{path} must contain a JSON object")
    return data


def cmd_generate(args: argparse.Namespace) -> int:
    data = load_json(args.input)
    framework = (args.framework or data.get("framework") or "").lower()
    try:
        fw = TestFramework(framework)
    except ValueError:
        fail(f"unknown framework '{framework}'; use one of {', '.join(f.value for f in TestFramework)}")
    requirements = data.get("requirements")
    if not isinstance(requirements, dict):
        fail(f"{args.input}: expected a 'requirements' object (user_stories, acceptance_criteria, api_specs)")
    language = data.get("language") or ("python" if fw == TestFramework.PYTEST else
                                        "java" if fw == TestFramework.JUNIT else "typescript")
    generator = TestGenerator(framework=fw, language=language)
    cases = generator.generate_from_requirements(requirements)
    if not cases:
        fail(f"{args.input}: no test cases could be derived from the requirements")
    code = generator.generate_test_file(args.module, cases)
    if args.output:
        Path(args.output).write_text(code, encoding="utf-8")
        print(f"wrote {len(cases)} test stubs to {args.output}", file=sys.stderr)
    elif args.format == "json":
        print(json.dumps({"framework": fw.value, "test_cases": cases, "code": code}, indent=2, default=str))
    else:
        print(code)
    return 0


def cmd_quality(args: argparse.Namespace) -> int:
    code = read_text(args.test_file)
    metrics = MetricsCalculator().calculate_test_quality(code)
    if args.format == "json":
        print(json.dumps(metrics, indent=2, default=str))
    else:
        for key, value in metrics.items():
            print(f"{key}: {json.dumps(value, default=str) if isinstance(value, (dict, list)) else value}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="TDD helpers: coverage gaps, test stubs, test quality.")
    sub = parser.add_subparsers(dest="command", required=True)
    cov = sub.add_parser("coverage", help="find files below a coverage threshold")
    cov.add_argument("report", help="LCOV, Istanbul JSON or Cobertura XML file")
    cov.add_argument("--threshold", type=float, default=80.0, help="minimum percent per file (default 80)")
    gen = sub.add_parser("generate", help="test stubs from a requirements JSON")
    gen.add_argument("input", help="JSON with framework, language and requirements (see assets/)")
    gen.add_argument("--framework", help="override the framework in the input")
    gen.add_argument("--module", default="module_under_test", help="module name for imports")
    gen.add_argument("--output", "-o", help="write the test file here instead of stdout")
    qual = sub.add_parser("quality", help="score an existing test file")
    qual.add_argument("test_file", help="test source file")
    for p in (cov, gen, qual):
        p.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    handler = {"coverage": cmd_coverage, "generate": cmd_generate, "quality": cmd_quality}[args.command]
    sys.exit(handler(args))


if __name__ == "__main__":
    main()
