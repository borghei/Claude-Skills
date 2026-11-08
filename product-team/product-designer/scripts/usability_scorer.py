#!/usr/bin/env python3
"""
Usability Test Scorer: SUS scores and task performance metrics from usability test data.

SUS item wording lives in references/sus-questions.json; the `sample` action copies the
borderline sample CSVs from assets/ (refusing to overwrite unless --force). Stdlib only.

Usage:
    python usability_scorer.py --sus-responses responses.csv --task-data tasks.csv
    python usability_scorer.py sample --out-dir /tmp/demo
    python usability_scorer.py --sus-responses responses.csv --format json

Exit codes:
    0  SUS mean >= 68 and no task with completion under 75%
    1  SUS mean below 68, or a task rated Major/Critical (completion under 75%)
    2  bad input (missing file, missing or out-of-range values, no rows, no input, file exists)
"""

import argparse
import csv
import json
import os
import shutil
import statistics
import sys
from typing import Dict, List

SKILL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SUS_BENCHMARK = 68.0
TRUE_WORDS, FALSE_WORDS = ("true", "1", "yes"), ("false", "0", "no")
SUS_BANDS = [(80.3, "A", "Excellent", "Top 10%"), (68, "B", "Good", "Above average"),
             (51, "C", "OK", "Below average"), (35, "D", "Poor", "Bottom 20%"),
             (float("-inf"), "F", "Awful", "Bottom 5%")]
TASK_SEVERITY = [(50, "Critical"), (75, "Major"), (90, "Minor"), (float("inf"), "None")]

with open(os.path.join(SKILL, "references", "sus-questions.json"), "r", encoding="utf-8") as _f:
    SUS_QUESTIONS = json.load(_f)["questions"]


class InputError(Exception):
    """Raised for test data the scorer cannot use; reported with exit code 2."""


def median(values: List[float]) -> float:
    """Median; the mean of the two middle values for an even count."""
    s = sorted(values)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else round((s[mid - 1] + s[mid]) / 2, 1)


def calculate_sus_score(responses: List[int]) -> float:
    """SUS score from 10 responses (1-5): odd items score-1, even items 5-score, sum x 2.5."""
    if len(responses) != 10:
        raise ValueError("SUS requires exactly 10 responses")
    adjusted = [score - 1 if (i + 1) % 2 == 1 else 5 - score for i, score in enumerate(responses)]
    return round(sum(adjusted) * 2.5, 1)


def interpret_sus_score(score: float) -> Dict:
    """Interpret SUS score using standard benchmarks."""
    grade, adjective, percentile = next(b[1:] for b in SUS_BANDS if score >= b[0])
    acceptable = "Acceptable" if score >= 70 else "Marginal" if score >= 50 else "Not acceptable"
    return {
        "score": score,
        "grade": grade,
        "adjective": adjective,
        "percentile": percentile,
        "acceptable": acceptable,
        "benchmark": SUS_BENCHMARK,
        "above_benchmark": score >= SUS_BENCHMARK,
    }


def calculate_task_metrics(tasks: List[Dict]) -> Dict:
    """Per-task completion rate, time on task (completed attempts only), errors and severity."""
    task_groups: Dict[str, List[Dict]] = {}
    for t in tasks:
        task_groups.setdefault(t["task"], []).append(t)

    results = {}
    for task_name, attempts in task_groups.items():
        total = len(attempts)
        completed = sum(1 for a in attempts if a["completed"])
        times = [a["time_seconds"] for a in attempts if a["completed"]]
        errors = [a["errors"] for a in attempts]

        completion_rate = round((completed / total) * 100, 1)
        severity = next(label for limit, label in TASK_SEVERITY if completion_rate < limit)
        results[task_name] = {
            "participants": total,
            "completion_rate": completion_rate,
            "avg_time_seconds": round(sum(times) / len(times), 1) if times else 0,
            "median_time_seconds": median(times) if times else 0,
            "avg_errors": round(sum(errors) / total, 1),
            "usability_severity": severity,
        }
    return results


def _cell(row: Dict, key: str, line: int) -> str:
    value = (row.get(key) or "").strip()
    if not value:
        raise InputError(f"line {line}: missing value for '{key}'")
    return value


def load_sus_csv(filepath: str) -> List[Dict]:
    """Load SUS responses from CSV: participant, q1..q10, each an integer 1-5."""
    rows = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        for line, row in enumerate(csv.DictReader(f), 2):
            responses = []
            for i in range(1, 11):
                raw = _cell(row, f"q{i}", line)
                if raw not in ("1", "2", "3", "4", "5"):
                    raise InputError(f"line {line}: q{i} must be 1-5, got {raw!r}")
                responses.append(int(raw))
            rows.append({"participant": row.get("participant") or f"P{len(rows)+1}", "responses": responses})
    if not rows:
        raise InputError(f"{filepath}: no response rows")
    return rows


def load_task_csv(filepath: str) -> List[Dict]:
    """Load task performance data from CSV: participant, task, completed, time_seconds, errors."""
    rows = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        for line, row in enumerate(csv.DictReader(f), 2):
            done = _cell(row, "completed", line).lower()
            if done not in TRUE_WORDS + FALSE_WORDS:
                raise InputError(f"line {line}: completed must be true/false, got {done!r}")
            try:
                seconds = float(_cell(row, "time_seconds", line))
                errors = int(_cell(row, "errors", line))
            except ValueError as exc:
                raise InputError(f"line {line}: {exc}") from None
            if seconds < 0 or errors < 0:
                raise InputError(f"line {line}: time_seconds and errors cannot be negative")
            rows.append({"participant": row.get("participant") or "Unknown", "task": _cell(row, "task", line),
                         "completed": done in TRUE_WORDS, "time_seconds": seconds, "errors": errors})
    if not rows:
        raise InputError(f"{filepath}: no task rows")
    return rows


def create_sample_files(out_dir: str, force: bool) -> None:
    """Copy the borderline sample CSVs (SUS 67.5, two Minor tasks) into out_dir; never overwrite unasked."""
    targets = [(f"sample_{kind}_borderline.csv", os.path.normpath(os.path.join(out_dir, f"sample_{kind}.csv"))) for kind in ("sus", "tasks")]
    existing = [dst for _, dst in targets if os.path.exists(dst)]
    if existing and not force:
        raise InputError(f"{', '.join(existing)} already exists; pass --force to overwrite or --out-dir elsewhere")
    for src, dst in targets:
        shutil.copyfile(os.path.join(SKILL, "assets", src), dst)
    print(f"Sample files created: {targets[0][1]}, {targets[1][1]}")


def score_sus(raw: List[Dict]) -> Dict:
    """Per-participant scores plus the aggregate (sample standard deviation, n-1; 0 for one participant)."""
    participants = []
    for p in raw:
        score = calculate_sus_score(p["responses"])
        participants.append({"participant": p["participant"], "responses": p["responses"],
                             "score": score, "interpretation": interpret_sus_score(score)})
    scores = [p["score"] for p in participants]
    mean = round(sum(scores) / len(scores), 1)
    aggregate = {
        "count": len(scores),
        "mean_score": mean,
        "median_score": median(scores),
        "std_dev": round(statistics.stdev(scores), 1) if len(scores) > 1 else 0.0,
        "min_score": min(scores),
        "max_score": max(scores),
        "interpretation": interpret_sus_score(mean),
    }
    return {"participants": participants, "aggregate": aggregate}


def scale_lines(mean: float) -> List[str]:
    """A 0-100 ruler (one column per 3.33 points) with the grade band under it."""
    band = "".join(interpret_sus_score(c / 30 * 100)["grade"] for c in range(31))
    ruler = list(" " * 31)
    ruler[min(int(mean / 100 * 30), 30)] = "^"
    return ["  0     20    40    60    80   100", "  |-----|-----|-----|-----|-----|",
            f"  {''.join(ruler)} ({mean})", f"  {band}"]


def format_sus_report(participants: List[Dict], aggregate: Dict) -> str:
    """Format SUS report as human-readable text."""
    interp = aggregate["interpretation"]
    lines = ["=" * 60, "SYSTEM USABILITY SCALE (SUS) REPORT", "=" * 60]
    lines.append(f"\n  AGGREGATE SCORE: {aggregate['mean_score']}")
    lines.append(f"  Grade:           {interp['grade']} ({interp['adjective']})")
    lines.append(f"  Percentile:      {interp['percentile']}")
    lines.append(f"  Acceptable:      {interp['acceptable']}")
    lines.append(f"  Benchmark:       {interp['benchmark']} (industry average)")
    lines.append(f"  Participants:    {aggregate['count']}")
    lines.append(f"  Std Dev (n-1):   {aggregate['std_dev']}")
    lines.append(f"  Range:           {aggregate['min_score']} - {aggregate['max_score']}")

    lines.append("\n  SCORE SCALE")
    lines.extend(scale_lines(aggregate["mean_score"]))

    lines.append("\n  INDIVIDUAL SCORES")
    lines.append(f"  {'Participant':<15} {'Score':>7} {'Grade':>6}")
    lines.append(f"  {'-'*15} {'-'*7} {'-'*6}")
    for p in participants:
        lines.append(f"  {p['participant']:<15} {p['score']:>7} {p['interpretation']['grade']:>6}")

    lines.append("\n  QUESTION ANALYSIS (avg per question)")
    lines.append(f"  {'#':<4} {'Avg':>5} {'Question'}")
    lines.append(f"  {'-'*4} {'-'*5} {'-'*50}")
    for qi in range(10):
        avg_q = round(sum(p["responses"][qi] for p in participants) / len(participants), 1)
        direction = "(+)" if (qi + 1) % 2 == 1 else "(-)"
        lines.append(f"  Q{qi+1:<3} {avg_q:>5} {direction} {SUS_QUESTIONS[qi][:50]}")
    return "\n".join(lines)


def format_task_report(task_results: Dict) -> str:
    """Format task metrics as human-readable text."""
    lines = ["\n" + "=" * 60, "TASK PERFORMANCE REPORT", "=" * 60]
    lines.append(f"\n  {'Task':<25} {'Completion':>12} {'Avg Time':>10} {'Avg Errors':>11} {'Severity':<10}")
    lines.append(f"  {'-'*25} {'-'*12} {'-'*10} {'-'*11} {'-'*10}")
    for task_name, m in task_results.items():
        lines.append(
            f"  {task_name:<25} {m['completion_rate']:>11}% "
            f"{m['avg_time_seconds']:>9}s {m['avg_errors']:>11} "
            f"{m['usability_severity']:<10}"
        )
    return "\n".join(lines)


def gate_failed(output: Dict) -> bool:
    """True when SUS is under the benchmark or a task is Major/Critical."""
    sus_low = "sus" in output and output["sus"]["aggregate"]["mean_score"] < SUS_BENCHMARK
    tasks_bad = any(m["usability_severity"] in ("Major", "Critical")
                    for m in output.get("task_performance", {}).values())
    return sus_low or tasks_bad


def main():
    parser = argparse.ArgumentParser(
        description="Calculate SUS scores and task performance metrics from usability tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python usability_scorer.py sample --out-dir demo/
  python usability_scorer.py --sus-responses responses.csv --task-data tasks.csv --format json

Exit codes: 0 SUS >= 68 and no task under 75% completion, 1 otherwise, 2 bad input
        """,
    )
    parser.add_argument("action", nargs="?", choices=["sample"], help='"sample" to create sample files')
    parser.add_argument("--sus-responses", help="CSV with SUS responses (participant, q1-q10)")
    parser.add_argument("--task-data", help="CSV with task data (participant, task, completed, time_seconds, errors)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--json", action="store_true", help="Same as --format json")
    parser.add_argument("--out-dir", default=".", help="Where 'sample' writes its CSVs (default: current directory)")
    parser.add_argument("--force", action="store_true", help="Let 'sample' overwrite existing sample CSVs")
    args = parser.parse_args()
    as_json = args.json or args.format == "json"

    if args.action == "sample":
        try:
            create_sample_files(args.out_dir, args.force)
        except (OSError, InputError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        return 0

    if not args.sus_responses and not args.task_data:
        print("error: provide --sus-responses and/or --task-data, or use 'sample' to create test files",
              file=sys.stderr)
        return 2

    output = {}
    try:
        if args.sus_responses:
            output["sus"] = score_sus(load_sus_csv(args.sus_responses))
        if args.task_data:
            output["task_performance"] = calculate_task_metrics(load_task_csv(args.task_data))
    except (OSError, csv.Error, InputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if as_json:
        if "sus" in output:  # response arrays are left out of JSON for brevity
            for p in output["sus"]["participants"]:
                del p["responses"]
        print(json.dumps(output, indent=2))
    else:
        if "sus" in output:
            print(format_sus_report(output["sus"]["participants"], output["sus"]["aggregate"]))
        if "task_performance" in output:
            print(format_task_report(output["task_performance"]))
    return 1 if gate_failed(output) else 0


if __name__ == "__main__":
    sys.exit(main())
