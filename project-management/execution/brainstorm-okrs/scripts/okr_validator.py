#!/usr/bin/env python3
"""OKR Validator - Validate and score OKR sets against quality criteria.

Checks that objectives are qualitative and inspirational, key results are
measurable outcomes (not outputs), and each set follows the Radical Focus
framework. Scores each OKR set 0-100 and provides improvement suggestions.

Usage:
    python okr_validator.py --input okrs.json
    python okr_validator.py --input okrs.json --format json
    python okr_validator.py --demo
    python okr_validator.py --demo --format json

Input JSON format:
    {
        "okr_sets": [
            {
                "objective": "Become the most trusted onboarding experience",
                "key_results": [
                    {
                        "description": "Reduce time-to-first-value",
                        "metric": "minutes to first completed task",
                        "target_value": 5,
                        "current_value": 18
                    }
                ]
            }
        ]
    }

Standard library only. No external dependencies.
"""

import argparse
import json
import re
import sys
import textwrap


# Words that suggest an output (task/activity) rather than an outcome
OUTPUT_VERBS = [
    "launch", "build", "implement", "create", "develop", "design",
    "deploy", "ship", "release", "write", "publish", "deliver",
    "migrate", "refactor", "integrate", "set up", "configure",
    "hire", "onboard", "train", "document", "automate",
]

DEMO_DATA = {
    "okr_sets": [
        {
            "objective": "Become the most trusted onboarding experience in our category",
            "key_results": [
                {
                    "description": "Reduce time-to-first-value for new users",
                    "metric": "minutes to first completed task",
                    "target_value": 5,
                    "current_value": 18,
                },
                {
                    "description": "Increase onboarding completion rate",
                    "metric": "percent of users completing onboarding",
                    "target_value": 85,
                    "current_value": 52,
                },
                {
                    "description": "Improve new user satisfaction score",
                    "metric": "CSAT score (1-5) at day 7",
                    "target_value": 4.5,
                    "current_value": 3.2,
                },
            ],
        },
        {
            "objective": "Increase revenue by 25%",
            "key_results": [
                {
                    "description": "Launch 5 new features",
                    "metric": "features launched",
                    "target_value": 5,
                    "current_value": 0,
                },
                {
                    "description": "Build a new billing system",
                    "metric": "system built",
                    "target_value": 1,
                    "current_value": 0,
                },
            ],
        },
        {
            "objective": "Make our platform the fastest way for teams to collaborate on documents",
            "key_results": [
                {
                    "description": "Reduce average document collaboration cycle time",
                    "metric": "hours from draft to final version",
                    "target_value": 4,
                    "current_value": 24,
                },
                {
                    "description": "Increase concurrent editing adoption",
                    "metric": "percent of documents with 2+ simultaneous editors",
                    "target_value": 40,
                    "current_value": 12,
                },
                {
                    "description": "Reduce context-switching during collaboration",
                    "metric": "average tool switches per collaboration session",
                    "target_value": 1,
                    "current_value": 4,
                },
            ],
        },
    ]
}


def validate_objective(objective: str) -> dict:
    """Validate an objective string. Returns issues and score."""
    issues = []
    score = 100

    # Check if objective contains numbers (should be qualitative)
    if re.search(r'\d+', objective):
        issues.append({
            "severity": "warning",
            "message": "Objective contains numbers. Objectives should be qualitative and inspirational. Move metrics to key results.",
        })
        score -= 20

    # Check length
    if len(objective.split()) < 5:
        issues.append({
            "severity": "warning",
            "message": "Objective is very short. Consider making it more specific and inspirational.",
        })
        score -= 10

    if len(objective.split()) > 25:
        issues.append({
            "severity": "info",
            "message": "Objective is quite long. Aim for a concise, memorable statement.",
        })
        score -= 5

    # Check for vague language
    vague_words = ["improve", "better", "enhance", "optimize", "good", "great", "nice"]
    objective_lower = objective.lower()
    found_vague = [w for w in vague_words if w in objective_lower.split()]
    if found_vague and len(objective.split()) < 10:
        issues.append({
            "severity": "warning",
            "message": f"Objective uses vague language ({', '.join(found_vague)}). Be more specific about the desired outcome.",
        })
        score -= 10

    if not issues:
        issues.append({
            "severity": "pass",
            "message": "Objective is qualitative and appears well-formed.",
        })

    return {"score": max(score, 0), "issues": issues}


def validate_key_result(kr: dict, index: int) -> dict:
    """Validate a single key result. Returns issues and score."""
    issues = []
    score = 100

    description = kr.get("description", "")
    metric = kr.get("metric", "")
    target_value = kr.get("target_value")
    current_value = kr.get("current_value")

    # Check for target value
    if target_value is None:
        issues.append({
            "severity": "error",
            "message": f"KR{index}: Missing target_value. Key results must be measurable.",
        })
        score -= 30

    # Check for current value
    if current_value is None:
        issues.append({
            "severity": "warning",
            "message": f"KR{index}: Missing current_value. Include a baseline to measure progress.",
        })
        score -= 10

    # Check for metric description
    if not metric:
        issues.append({
            "severity": "error",
            "message": f"KR{index}: Missing metric. What unit of measurement is this?",
        })
        score -= 20

    # Check for output verbs (suggests task, not outcome)
    desc_lower = description.lower()
    found_outputs = [v for v in OUTPUT_VERBS if desc_lower.startswith(v) or f" {v} " in f" {desc_lower} "]
    if found_outputs:
        issues.append({
            "severity": "warning",
            "message": f"KR{index}: Contains output-oriented language ({', '.join(found_outputs)}). "
                       f"Key results should measure outcomes, not activities. "
                       f"Ask: 'What result does this activity produce?'",
        })
        score -= 25

    # Check if target equals current (no stretch)
    if target_value is not None and current_value is not None:
        if target_value == current_value:
            issues.append({
                "severity": "error",
                "message": f"KR{index}: Target equals current value. There is no improvement to measure.",
            })
            score -= 30

    if not issues:
        issues.append({
            "severity": "pass",
            "message": f"KR{index}: Well-formed measurable key result.",
        })

    return {"score": max(score, 0), "issues": issues}


def validate_okr_set(okr_set: dict, set_index: int) -> dict:
    """Validate a complete OKR set (objective + key results)."""
    objective = okr_set.get("objective", "")
    key_results = okr_set.get("key_results", [])

    result = {
        "set_index": set_index,
        "objective": objective,
        "objective_validation": validate_objective(objective),
        "key_result_validations": [],
        "structural_issues": [],
        "overall_score": 0,
    }

    # Validate KR count
    kr_count = len(key_results)
    if kr_count == 0:
        result["structural_issues"].append({
            "severity": "error",
            "message": "No key results defined. Each objective needs exactly 3 key results.",
        })
    elif kr_count < 3:
        result["structural_issues"].append({
            "severity": "warning",
            "message": f"Only {kr_count} key result(s). Best practice is exactly 3 per objective.",
        })
    elif kr_count > 3:
        result["structural_issues"].append({
            "severity": "warning",
            "message": f"{kr_count} key results defined. More than 3 dilutes focus. Pick the 3 most important.",
        })

    # Validate each KR
    kr_scores = []
    for i, kr in enumerate(key_results, 1):
        kr_validation = validate_key_result(kr, i)
        result["key_result_validations"].append(kr_validation)
        kr_scores.append(kr_validation["score"])

    # Calculate overall score
    obj_score = result["objective_validation"]["score"]
    kr_avg = sum(kr_scores) / len(kr_scores) if kr_scores else 0

    # Structural penalty
    structural_penalty = 0
    if kr_count == 0:
        structural_penalty = 40
    elif kr_count != 3:
        structural_penalty = 10

    result["overall_score"] = max(
        int(obj_score * 0.3 + kr_avg * 0.6 + (100 - structural_penalty) * 0.1),
        0,
    )

    # Generate suggestions
    result["suggestions"] = _generate_suggestions(result)

    return result


def _generate_suggestions(result: dict) -> list[str]:
    """Generate improvement suggestions based on validation results."""
    suggestions = []

    obj_score = result["objective_validation"]["score"]
    if obj_score < 80:
        suggestions.append(
            "Rewrite the objective to be qualitative and inspirational. "
            "Remove numbers and metrics -- those belong in key results."
        )

    kr_validations = result["key_result_validations"]
    output_krs = []
    for i, krv in enumerate(kr_validations, 1):
        for issue in krv["issues"]:
            if "output-oriented" in issue.get("message", ""):
                output_krs.append(i)

    if output_krs:
        kr_list = ", ".join(f"KR{k}" for k in output_krs)
        suggestions.append(
            f"{kr_list} read like tasks, not outcomes. For each, ask 'So what? What result does "
            f"completing this produce?' and use that result as the key result instead."
        )

    if len(kr_validations) != 3:
        suggestions.append(
            "Adjust to exactly 3 key results. Include one counter-metric to prevent gaming."
        )

    if result["overall_score"] >= 80:
        suggestions.append("This OKR set is strong. Confirm 60-70% confidence in hitting targets.")

    return suggestions


def format_text_report(results: list[dict]) -> str:
    """Format validation results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("OKR VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append("")

    for r in results:
        lines.append(f"--- OKR Set {r['set_index']} (Score: {r['overall_score']}/100) ---")
        lines.append(f"Objective: \"{r['objective']}\"")
        lines.append("")

        # Objective issues
        lines.append("  Objective Validation:")
        for issue in r["objective_validation"]["issues"]:
            icon = _severity_icon(issue["severity"])
            lines.append(f"    {icon} {issue['message']}")
        lines.append("")

        # Structural issues
        if r["structural_issues"]:
            lines.append("  Structure:")
            for issue in r["structural_issues"]:
                icon = _severity_icon(issue["severity"])
                lines.append(f"    {icon} {issue['message']}")
            lines.append("")

        # KR issues
        if r["key_result_validations"]:
            lines.append("  Key Results:")
            for krv in r["key_result_validations"]:
                for issue in krv["issues"]:
                    icon = _severity_icon(issue["severity"])
                    lines.append(f"    {icon} {issue['message']}")
            lines.append("")

        # Suggestions
        if r["suggestions"]:
            lines.append("  Suggestions:")
            for s in r["suggestions"]:
                wrapped = textwrap.fill(s, width=70, initial_indent="    -> ", subsequent_indent="       ")
                lines.append(wrapped)
            lines.append("")

    # Summary
    lines.append("=" * 60)
    scores = [r["overall_score"] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    lines.append(f"Average Score: {avg_score:.0f}/100")
    lines.append(f"Sets Evaluated: {len(results)}")

    strong = sum(1 for s in scores if s >= 80)
    needs_work = sum(1 for s in scores if s < 80)
    lines.append(f"Strong: {strong}  |  Needs Work: {needs_work}")
    lines.append("=" * 60)

    return "\n".join(lines)


def _severity_icon(severity: str) -> str:
    """Return a text indicator for severity level."""
    return {
        "error": "[ERROR]",
        "warning": "[WARN] ",
        "info": "[INFO] ",
        "pass": "[OK]   ",
    }.get(severity, "[????] ")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate and score OKR sets against quality criteria.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python okr_validator.py --demo
              python okr_validator.py --input okrs.json
              python okr_validator.py --input okrs.json --format json

            Input JSON format:
              {
                "okr_sets": [
                  {
                    "objective": "...",
                    "key_results": [
                      {"description": "...", "metric": "...", "target_value": N, "current_value": N}
                    ]
                  }
                ]
              }
        """),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--input",
        help="Path to JSON file containing OKR sets to validate",
    )
    group.add_argument(
        "--demo",
        action="store_true",
        help="Run validation on built-in demo data (mix of good and bad OKRs)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format: text (default) or json",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Main entry point."""
    args = parse_args(argv)

    if args.demo:
        data = DEMO_DATA
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.input}: {e}", file=sys.stderr)
            sys.exit(1)

    okr_sets = data.get("okr_sets", [])
    if not okr_sets:
        print("Error: No okr_sets found in input data.", file=sys.stderr)
        sys.exit(1)

    results = []
    for i, okr_set in enumerate(okr_sets, 1):
        results.append(validate_okr_set(okr_set, i))

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text_report(results))


if __name__ == "__main__":
    main()
