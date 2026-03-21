#!/usr/bin/env python3
"""Validate ML pipeline definitions for completeness, ordering, and best practices.

Reads a pipeline definition file (JSON) and checks for missing stages,
incorrect ordering, missing validation gates, absent monitoring hooks,
and configuration issues.

Usage:
    python pipeline_validator.py --pipeline pipeline.json
    python pipeline_validator.py --pipeline pipeline.json --strict --json

Pipeline definition format:
{
    "name": "fraud_detection_training",
    "stages": [
        {
            "name": "data_ingestion",
            "type": "data",
            "inputs": ["raw_transactions"],
            "outputs": ["cleaned_data"],
            "timeout_minutes": 30
        },
        {
            "name": "feature_engineering",
            "type": "transform",
            "inputs": ["cleaned_data"],
            "outputs": ["feature_set"],
            "validation": {"null_check": true, "schema_check": true}
        },
        {
            "name": "model_training",
            "type": "train",
            "inputs": ["feature_set"],
            "outputs": ["trained_model"],
            "parameters": {"algorithm": "xgboost"}
        },
        {
            "name": "model_evaluation",
            "type": "evaluate",
            "inputs": ["trained_model", "test_data"],
            "outputs": ["metrics"],
            "gate": {"metric": "f1", "threshold": 0.85}
        },
        {
            "name": "model_deployment",
            "type": "deploy",
            "inputs": ["trained_model", "metrics"],
            "outputs": ["serving_endpoint"],
            "rollback": true
        }
    ],
    "schedule": "0 2 * * 1",
    "notifications": {"on_failure": "ml-team@company.com"}
}
"""

import argparse
import json
import os
import re
import sys


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------

REQUIRED_STAGE_TYPES = {"data", "transform", "train", "evaluate"}
RECOMMENDED_STAGE_TYPES = {"deploy", "monitor"}
VALID_STAGE_TYPES = {"data", "transform", "train", "evaluate", "deploy", "monitor", "validate", "register", "test"}

EXPECTED_ORDER = ["data", "transform", "train", "evaluate", "deploy", "monitor"]
CRON_PATTERN = re.compile(r"^(\*|[0-9,\-\/]+)\s+(\*|[0-9,\-\/]+)\s+(\*|[0-9,\-\/]+)\s+(\*|[0-9,\-\/]+)\s+(\*|[0-9,\-\/]+)$")


def _validate_pipeline(pipeline: dict, strict: bool = False) -> list:
    issues = []
    name = pipeline.get("name", "(unnamed)")

    # Top-level checks
    if not pipeline.get("name"):
        issues.append({"severity": "error", "rule": "MISSING_NAME", "message": "Pipeline is missing a 'name' field."})

    stages = pipeline.get("stages", [])
    if not stages:
        issues.append({"severity": "error", "rule": "NO_STAGES", "message": "Pipeline has no stages defined."})
        return issues

    # Check required stage types
    stage_types = [s.get("type", "unknown") for s in stages]
    for req in REQUIRED_STAGE_TYPES:
        if req not in stage_types:
            issues.append({
                "severity": "error",
                "rule": "MISSING_REQUIRED_STAGE",
                "message": f"Pipeline is missing a required '{req}' stage.",
            })

    for rec in RECOMMENDED_STAGE_TYPES:
        if rec not in stage_types and strict:
            issues.append({
                "severity": "warning",
                "rule": "MISSING_RECOMMENDED_STAGE",
                "message": f"Pipeline is missing recommended '{rec}' stage.",
            })

    # Per-stage validation
    all_outputs = set()
    stage_names = []

    for i, stage in enumerate(stages):
        sname = stage.get("name", f"stage_{i}")
        stype = stage.get("type", "unknown")
        stage_names.append(sname)

        # Required fields
        if not stage.get("name"):
            issues.append({"severity": "error", "rule": "STAGE_MISSING_NAME", "message": f"Stage #{i+1} is missing a name."})

        if stype not in VALID_STAGE_TYPES:
            issues.append({"severity": "warning", "rule": "UNKNOWN_STAGE_TYPE", "message": f"Stage '{sname}' has unknown type '{stype}'."})

        # Inputs/outputs
        inputs = stage.get("inputs", [])
        outputs = stage.get("outputs", [])

        if not outputs:
            issues.append({"severity": "warning", "rule": "NO_OUTPUTS", "message": f"Stage '{sname}' defines no outputs."})

        # Check that inputs are produced by earlier stages (except first stage)
        if i > 0 and inputs:
            for inp in inputs:
                if inp not in all_outputs:
                    issues.append({
                        "severity": "warning",
                        "rule": "UNRESOLVED_INPUT",
                        "message": f"Stage '{sname}' requires input '{inp}' which is not produced by any earlier stage.",
                    })

        for out in outputs:
            if out in all_outputs:
                issues.append({
                    "severity": "warning",
                    "rule": "DUPLICATE_OUTPUT",
                    "message": f"Output '{out}' is produced by multiple stages.",
                })
            all_outputs.add(out)

        # Evaluation gate
        if stype == "evaluate" and not stage.get("gate"):
            issues.append({
                "severity": "warning" if not strict else "error",
                "rule": "MISSING_EVAL_GATE",
                "message": f"Evaluation stage '{sname}' has no quality gate defined. Models may deploy without validation.",
            })

        # Deploy should have rollback
        if stype == "deploy" and not stage.get("rollback"):
            issues.append({
                "severity": "warning",
                "rule": "NO_ROLLBACK",
                "message": f"Deploy stage '{sname}' has no rollback configuration.",
            })

        # Timeout
        if strict and not stage.get("timeout_minutes"):
            issues.append({
                "severity": "info",
                "rule": "NO_TIMEOUT",
                "message": f"Stage '{sname}' has no timeout configured.",
            })

    # Ordering check
    order_positions = {}
    for i, stype in enumerate(stage_types):
        if stype in EXPECTED_ORDER:
            order_positions[stype] = i

    for a, b in zip(EXPECTED_ORDER, EXPECTED_ORDER[1:]):
        if a in order_positions and b in order_positions:
            if order_positions[a] > order_positions[b]:
                issues.append({
                    "severity": "error",
                    "rule": "STAGE_ORDER",
                    "message": f"Stage type '{a}' appears after '{b}'; expected order: {' -> '.join(EXPECTED_ORDER)}.",
                })

    # Duplicate stage names
    seen_names = set()
    for sn in stage_names:
        if sn in seen_names:
            issues.append({"severity": "error", "rule": "DUPLICATE_STAGE_NAME", "message": f"Duplicate stage name: '{sn}'."})
        seen_names.add(sn)

    # Schedule validation
    schedule = pipeline.get("schedule")
    if schedule and not CRON_PATTERN.match(schedule.strip()):
        issues.append({"severity": "warning", "rule": "INVALID_SCHEDULE", "message": f"Schedule '{schedule}' does not match cron format."})

    # Notifications
    if not pipeline.get("notifications"):
        issues.append({"severity": "warning", "rule": "NO_NOTIFICATIONS", "message": "Pipeline has no notification configuration for failures."})

    return issues


def validate(pipeline: dict, strict: bool = False) -> dict:
    issues = _validate_pipeline(pipeline, strict)
    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")
    infos = sum(1 for i in issues if i["severity"] == "info")

    return {
        "pipeline_name": pipeline.get("name", "(unnamed)"),
        "total_stages": len(pipeline.get("stages", [])),
        "total_issues": len(issues),
        "errors": errors,
        "warnings": warnings,
        "info": infos,
        "valid": errors == 0,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate ML pipeline definitions for completeness and best practices.")
    parser.add_argument("--pipeline", required=True, help="Path to pipeline definition JSON file")
    parser.add_argument("--strict", action="store_true", help="Enable strict validation (recommended and info checks)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not os.path.exists(args.pipeline):
        print(f"Error: File not found: {args.pipeline}", file=sys.stderr)
        sys.exit(1)

    with open(args.pipeline, "r") as f:
        pipeline = json.load(f)

    if not isinstance(pipeline, dict):
        print("Error: Pipeline definition must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    result = validate(pipeline, args.strict)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["valid"] else "FAIL"
        print("ML Pipeline Validation Report")
        print("=" * 60)
        print(f"Pipeline: {result['pipeline_name']}  |  Stages: {result['total_stages']}")
        print(f"Status: [{status}]  |  Errors: {result['errors']}  Warnings: {result['warnings']}  Info: {result['info']}")
        print()

        if not result["issues"]:
            print("Pipeline definition passes all validation checks.")
        else:
            for issue in result["issues"]:
                sev = issue["severity"].upper()
                print(f"  [{sev}] {issue['rule']}")
                print(f"    {issue['message']}")

    sys.exit(1 if result["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
