#!/usr/bin/env python3
"""Run a JSON scenario suite against recorded agent transcripts.

Evaluates every assertion in the suite against the matching recorded
transcript and reports pass/fail per assertion, per scenario, and in
aggregate — including cost and latency budget checks.

Usage:
    python3 scenario_runner.py --suite suite.json --transcripts run.json
    python3 scenario_runner.py --suite suite.json --transcripts run.json \
        --format json --fail-under 0.9
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2}


def load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON file, exiting with an actionable message on failure."""
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {path} is not valid JSON (line {exc.lineno}): {exc.msg}",
              file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict):
        print(f"ERROR: {path} must contain a JSON object at the top level.",
              file=sys.stderr)
        sys.exit(1)
    return data


def index_transcripts(run: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Index recorded transcripts by scenario_id for O(1) lookup."""
    records = run.get("transcripts", [])
    if not isinstance(records, list):
        print("ERROR: 'transcripts' must be a list of transcript objects.",
              file=sys.stderr)
        sys.exit(1)
    indexed: Dict[str, Dict[str, Any]] = {}
    for record in records:
        scenario_id = record.get("scenario_id")
        if scenario_id:
            indexed[str(scenario_id)] = record
    return indexed


def tool_names(transcript: Dict[str, Any]) -> List[str]:
    """Return the ordered list of tool names called in a transcript."""
    return [str(call.get("name", "")) for call in transcript.get("tool_calls", [])]


def dig(payload: Any, path: str) -> Any:
    """Resolve a dotted path inside a nested dict/list structure."""
    current = payload
    for part in path.split("."):
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def check_assertion(assertion: Dict[str, Any],
                    transcript: Dict[str, Any]) -> Tuple[bool, str]:
    """Evaluate one assertion against one transcript.

    Returns (passed, human-readable detail).
    """
    kind = assertion.get("type", "")
    output = str(transcript.get("final_output", ""))
    calls = transcript.get("tool_calls", [])
    names = tool_names(transcript)

    if kind == "tool_called":
        want = assertion["tool"]
        return want in names, f"called={names}"
    if kind == "tool_not_called":
        want = assertion["tool"]
        return want not in names, f"called={names}"
    if kind == "tool_call_order":
        wanted = list(assertion["tools"])
        cursor = 0
        for name in names:
            if cursor < len(wanted) and name == wanted[cursor]:
                cursor += 1
        return cursor == len(wanted), f"matched {cursor}/{len(wanted)} in {names}"
    if kind == "tool_arg_equals":
        for call in calls:
            if call.get("name") == assertion["tool"]:
                actual = (call.get("arguments") or {}).get(assertion["arg"])
                if actual == assertion["value"]:
                    return True, f"{assertion['arg']}={actual!r}"
                return False, f"{assertion['arg']}={actual!r} want {assertion['value']!r}"
        return False, f"tool {assertion['tool']} never called"
    if kind == "max_tool_calls":
        return len(calls) <= assertion["value"], f"{len(calls)} calls"
    if kind == "output_contains":
        needle = str(assertion["value"])
        return needle.lower() in output.lower(), f"len(output)={len(output)}"
    if kind == "output_not_contains":
        needle = str(assertion["value"])
        return needle.lower() not in output.lower(), f"len(output)={len(output)}"
    if kind == "output_matches":
        try:
            pattern = re.compile(assertion["pattern"], re.IGNORECASE | re.DOTALL)
        except re.error as exc:
            return False, f"invalid regex: {exc}"
        return bool(pattern.search(output)), f"pattern={assertion['pattern']!r}"
    if kind == "json_field_equals":
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError:
            return False, "final_output is not valid JSON"
        actual = dig(parsed, assertion["path"])
        return actual == assertion["value"], f"{assertion['path']}={actual!r}"
    if kind == "no_error":
        err = transcript.get("error")
        return err in (None, "", False), f"error={err!r}"
    if kind == "max_turns":
        turns = int(transcript.get("turns", 0))
        return turns <= assertion["value"], f"{turns} turns"
    if kind == "max_latency_ms":
        latency = float(transcript.get("latency_ms", 0))
        return latency <= assertion["value"], f"{latency:.0f}ms"
    if kind == "max_cost_usd":
        cost = float(transcript.get("cost_usd", 0))
        return cost <= assertion["value"], f"${cost:.4f}"
    return False, f"unknown assertion type {kind!r}"


def budget_assertions(scenario: Dict[str, Any],
                      defaults: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Synthesize budget assertions from suite defaults when not overridden."""
    declared = {a.get("type") for a in scenario.get("assertions", [])}
    extra: List[Dict[str, Any]] = []
    for key in ("max_latency_ms", "max_cost_usd", "max_turns"):
        if key in defaults and key not in declared:
            extra.append({"type": key, "value": defaults[key],
                          "severity": "major", "source": "suite-default"})
    return extra


def run_suite(suite: Dict[str, Any], run: Dict[str, Any]) -> Dict[str, Any]:
    """Execute every scenario in the suite against the recorded run."""
    transcripts = index_transcripts(run)
    defaults = suite.get("defaults", {})
    results: List[Dict[str, Any]] = []

    for scenario in suite.get("scenarios", []):
        scenario_id = str(scenario.get("id", "<unnamed>"))
        transcript = transcripts.get(scenario_id)
        if transcript is None:
            results.append({
                "scenario_id": scenario_id,
                "status": "missing",
                "assertions": [],
                "passed": 0,
                "total": len(scenario.get("assertions", [])),
                "cost_usd": 0.0,
                "latency_ms": 0.0,
            })
            continue

        checks = list(scenario.get("assertions", [])) + budget_assertions(scenario, defaults)
        detail: List[Dict[str, Any]] = []
        for assertion in checks:
            try:
                passed, note = check_assertion(assertion, transcript)
            except KeyError as exc:
                passed, note = False, f"assertion missing field {exc}"
            detail.append({
                "type": assertion.get("type"),
                "severity": assertion.get("severity", "major"),
                "passed": passed,
                "detail": note,
            })
        passed_count = sum(1 for d in detail if d["passed"])
        critical_failed = any(
            not d["passed"] and d["severity"] == "critical" for d in detail
        )
        status = "pass" if passed_count == len(detail) else "fail"
        results.append({
            "scenario_id": scenario_id,
            "description": scenario.get("description", ""),
            "status": status,
            "critical_failure": critical_failed,
            "assertions": detail,
            "passed": passed_count,
            "total": len(detail),
            "cost_usd": float(transcript.get("cost_usd", 0.0)),
            "latency_ms": float(transcript.get("latency_ms", 0.0)),
        })

    total = len(results)
    passing = sum(1 for r in results if r["status"] == "pass")
    return {
        "suite": suite.get("suite", "unnamed-suite"),
        "run_id": run.get("run_id", "unknown-run"),
        "model": run.get("model", "unknown-model"),
        "scenarios_total": total,
        "scenarios_passed": passing,
        "pass_rate": round(passing / total, 4) if total else 0.0,
        "critical_failures": sum(1 for r in results if r.get("critical_failure")),
        "total_cost_usd": round(sum(r["cost_usd"] for r in results), 4),
        "mean_latency_ms": round(
            sum(r["latency_ms"] for r in results) / total, 1) if total else 0.0,
        "results": results,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Suite: {report['suite']}   Run: {report['run_id']} ({report['model']})")
    print("=" * 68)
    for result in report["results"]:
        badge = {"pass": "PASS", "fail": "FAIL", "missing": "MISS"}[result["status"]]
        print(f"[{badge}] {result['scenario_id']}  "
              f"{result['passed']}/{result['total']} assertions  "
              f"{result['latency_ms']:.0f}ms  ${result['cost_usd']:.4f}")
        for check in result["assertions"]:
            if not check["passed"]:
                print(f"       x {check['severity']:<8} {check['type']}: {check['detail']}")
        if result["status"] == "missing":
            print("       x no recorded transcript for this scenario")
    print("-" * 68)
    print(f"Pass rate: {report['pass_rate'] * 100:.1f}% "
          f"({report['scenarios_passed']}/{report['scenarios_total']})")
    print(f"Critical failures: {report['critical_failures']}")
    print(f"Total cost: ${report['total_cost_usd']:.4f}   "
          f"Mean latency: {report['mean_latency_ms']:.0f}ms")


def main() -> None:
    """Parse arguments, run the suite, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Run a JSON scenario suite against recorded agent transcripts.")
    parser.add_argument("--suite", required=True,
                        help="Path to the scenario suite JSON file.")
    parser.add_argument("--transcripts", required=True,
                        help="Path to the recorded run JSON (transcripts array).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--fail-under", type=float, default=None,
                        help="Exit 2 if the pass rate falls below this ratio (0-1).")
    parser.add_argument("--strict-critical", action="store_true",
                        help="Exit 2 if any assertion tagged severity=critical fails.")
    args = parser.parse_args()

    suite = load_json(Path(args.suite))
    run = load_json(Path(args.transcripts))
    report = run_suite(suite, run)
    output(report, args.format)

    if args.strict_critical and report["critical_failures"]:
        sys.exit(2)
    if args.fail_under is not None and report["pass_rate"] < args.fail_under:
        sys.exit(2)


if __name__ == "__main__":
    main()
