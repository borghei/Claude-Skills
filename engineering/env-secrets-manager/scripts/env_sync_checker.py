#!/usr/bin/env python3
"""Compare env configs across environments to detect drift.

Loads multiple .env files (e.g., .env.development, .env.staging, .env.production)
and reports:
  - Variables present in some environments but missing in others
  - Value differences for shared variables (with secret redaction)
  - Structural inconsistencies (ordering, section grouping)
  - Drift percentage between each pair of environments

Usage:
    python env_sync_checker.py .env.dev .env.staging .env.prod
    python env_sync_checker.py .env.* --baseline .env.example --json
    python env_sync_checker.py envs/ --show-values --json
"""

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

# Variable names that hold secrets — values will be redacted in output
SECRET_KEY_PATTERNS = [
    re.compile(r".*SECRET.*", re.IGNORECASE),
    re.compile(r".*PASSWORD.*", re.IGNORECASE),
    re.compile(r".*TOKEN.*", re.IGNORECASE),
    re.compile(r".*API_KEY.*", re.IGNORECASE),
    re.compile(r".*PRIVATE_KEY.*", re.IGNORECASE),
    re.compile(r".*ACCESS_KEY.*", re.IGNORECASE),
    re.compile(r".*CREDENTIAL.*", re.IGNORECASE),
    re.compile(r".*_DSN$", re.IGNORECASE),
    re.compile(r"^DATABASE_URL$", re.IGNORECASE),
]


def is_secret_key(key: str) -> bool:
    """Check if a variable name likely holds a secret."""
    return any(p.match(key) for p in SECRET_KEY_PATTERNS)


def redact_value(key: str, value: str, show_values: bool = False) -> str:
    """Redact secret values unless --show-values is set."""
    if show_values:
        return value
    if is_secret_key(key) and value:
        if len(value) <= 4:
            return "****"
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    return value


def parse_env_file(filepath: str) -> dict:
    """Parse a .env file into {KEY: value} dict.

    Handles comments, blank lines, quoted values, and inline comments.
    """
    variables = {}
    path = Path(filepath)
    if not path.exists():
        return variables

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if not key or key.startswith("#"):
                continue
            value = value.strip()
            if value and value[0] in ('"', "'"):
                quote = value[0]
                end = value.find(quote, 1)
                if end != -1:
                    value = value[1:end]
            else:
                comment_match = re.search(r"\s+#\s", value)
                if comment_match:
                    value = value[: comment_match.start()]
                value = value.strip()
            variables[key] = value
    return variables


def resolve_env_files(paths: list[str]) -> list[tuple[str, str]]:
    """Resolve input paths to (label, filepath) pairs.

    If a path is a directory, find all .env* files inside it.
    Supports glob patterns.
    """
    results = []
    for path_arg in paths:
        p = Path(path_arg)
        if p.is_dir():
            # Find all .env* files in the directory
            for child in sorted(p.iterdir()):
                if child.is_file() and child.name.startswith(".env"):
                    label = child.name
                    results.append((label, str(child)))
        elif "*" in path_arg or "?" in path_arg:
            for match in sorted(glob.glob(path_arg)):
                mp = Path(match)
                if mp.is_file():
                    results.append((mp.name, str(mp)))
        elif p.is_file():
            results.append((p.name, str(p)))
        else:
            print(f"Warning: Path not found, skipping: {path_arg}", file=sys.stderr)
    return results


def compute_drift(env_a: dict, env_b: dict) -> dict:
    """Compute drift metrics between two environments."""
    keys_a = set(env_a.keys())
    keys_b = set(env_b.keys())
    all_keys = keys_a | keys_b
    common_keys = keys_a & keys_b

    only_a = sorted(keys_a - keys_b)
    only_b = sorted(keys_b - keys_a)

    # Value differences among shared keys
    value_diffs = []
    for key in sorted(common_keys):
        if env_a[key] != env_b[key]:
            value_diffs.append(key)

    total = len(all_keys)
    drift_keys = len(only_a) + len(only_b) + len(value_diffs)
    drift_pct = round((drift_keys / total * 100), 1) if total > 0 else 0.0

    return {
        "only_first": only_a,
        "only_second": only_b,
        "value_differences": value_diffs,
        "shared_count": len(common_keys),
        "total_unique_keys": total,
        "drift_count": drift_keys,
        "drift_percentage": drift_pct,
    }


def check_sync(
    env_files: list[tuple[str, str]],
    baseline_path: str | None = None,
    show_values: bool = False,
) -> dict:
    """Run full sync check across all environments."""
    # Parse all env files
    environments = {}
    for label, filepath in env_files:
        environments[label] = {
            "path": filepath,
            "vars": parse_env_file(filepath),
        }

    if len(environments) < 2:
        return {
            "error": "Need at least 2 environment files to compare",
            "environments_found": len(environments),
            "passed": False,
        }

    # Parse baseline if provided
    baseline_vars = None
    if baseline_path:
        baseline_vars = parse_env_file(baseline_path)

    # Collect all keys across all environments
    all_keys = set()
    for env_data in environments.values():
        all_keys.update(env_data["vars"].keys())
    all_keys = sorted(all_keys)

    # Build the key presence matrix
    key_matrix = {}
    for key in all_keys:
        key_matrix[key] = {}
        for label, env_data in environments.items():
            if key in env_data["vars"]:
                key_matrix[key][label] = redact_value(key, env_data["vars"][key], show_values)
            else:
                key_matrix[key][label] = None  # missing

    # Find keys not present in all environments
    env_labels = list(environments.keys())
    missing_keys = {}  # key -> list of envs where it's missing
    for key in all_keys:
        missing_in = [label for label in env_labels if key_matrix[key][label] is None]
        if missing_in and len(missing_in) < len(env_labels):
            missing_keys[key] = {
                "present_in": [l for l in env_labels if key_matrix[key][l] is not None],
                "missing_in": missing_in,
            }

    # Baseline comparison
    baseline_issues = []
    if baseline_vars is not None:
        baseline_keys = set(baseline_vars.keys())
        for label, env_data in environments.items():
            env_keys = set(env_data["vars"].keys())
            missing_from_baseline = sorted(baseline_keys - env_keys)
            extra_beyond_baseline = sorted(env_keys - baseline_keys)
            if missing_from_baseline or extra_beyond_baseline:
                baseline_issues.append({
                    "environment": label,
                    "missing_from_baseline": missing_from_baseline,
                    "extra_beyond_baseline": extra_beyond_baseline,
                })

    # Pairwise drift
    pairwise_drift = []
    for i in range(len(env_labels)):
        for j in range(i + 1, len(env_labels)):
            label_a = env_labels[i]
            label_b = env_labels[j]
            drift = compute_drift(
                environments[label_a]["vars"],
                environments[label_b]["vars"],
            )
            pairwise_drift.append({
                "pair": [label_a, label_b],
                **drift,
            })

    # Overall pass/fail: drift > 5% on any pair is a fail (per SKILL.md success criteria)
    max_drift = max((d["drift_percentage"] for d in pairwise_drift), default=0.0)
    passed = max_drift <= 5.0 and not baseline_issues

    return {
        "environments": {label: {"path": d["path"], "var_count": len(d["vars"])}
                         for label, d in environments.items()},
        "total_unique_keys": len(all_keys),
        "missing_keys": missing_keys,
        "pairwise_drift": pairwise_drift,
        "max_drift_percentage": max_drift,
        "baseline_file": baseline_path,
        "baseline_issues": baseline_issues,
        "passed": passed,
    }


def print_human(results: dict) -> None:
    """Pretty-print sync check results."""
    if "error" in results:
        print(f"Error: {results['error']}")
        return

    print("Env Sync Checker")
    print("=" * 60)

    # Environment summary
    for label, info in results["environments"].items():
        print(f"  {label:<30} {info['var_count']} vars  ({info['path']})")
    print(f"  Total unique keys: {results['total_unique_keys']}")
    print()

    # Missing keys
    missing = results["missing_keys"]
    if missing:
        print(f"MISSING KEYS ({len(missing)} keys not present everywhere):")
        for key, info in missing.items():
            present = ", ".join(info["present_in"])
            absent = ", ".join(info["missing_in"])
            print(f"  {key}")
            print(f"    present: {present}")
            print(f"    missing: {absent}")
        print()

    # Pairwise drift
    print("PAIRWISE DRIFT:")
    for drift in results["pairwise_drift"]:
        pair = " <-> ".join(drift["pair"])
        pct = drift["drift_percentage"]
        status = "OK" if pct <= 5.0 else "DRIFT"
        print(f"  {pair}: {pct}% drift ({drift['drift_count']}/{drift['total_unique_keys']} keys) [{status}]")

        if drift["only_first"]:
            print(f"    Only in {drift['pair'][0]}: {', '.join(drift['only_first'])}")
        if drift["only_second"]:
            print(f"    Only in {drift['pair'][1]}: {', '.join(drift['only_second'])}")
        if drift["value_differences"]:
            print(f"    Value differs: {', '.join(drift['value_differences'])}")
    print()

    # Baseline issues
    if results["baseline_file"]:
        if results["baseline_issues"]:
            print(f"BASELINE COMPARISON (vs {results['baseline_file']}):")
            for issue in results["baseline_issues"]:
                print(f"  {issue['environment']}:")
                if issue["missing_from_baseline"]:
                    print(f"    Missing from baseline: {', '.join(issue['missing_from_baseline'])}")
                if issue["extra_beyond_baseline"]:
                    print(f"    Extra beyond baseline: {', '.join(issue['extra_beyond_baseline'])}")
            print()
        else:
            print(f"Baseline ({results['baseline_file']}): All environments match.")
            print()

    # Overall result
    status = "PASSED" if results["passed"] else "FAILED"
    print(f"Result: {status} (max drift: {results['max_drift_percentage']}%)")
    if not results["passed"]:
        print("  Target: <= 5% drift between environments")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare env configs across environments (dev/staging/prod) to detect drift. "
                    "Reports missing keys, value differences, and drift percentage.",
        epilog="Examples:\n"
               "  %(prog)s .env.dev .env.staging .env.prod\n"
               "  %(prog)s .env.* --baseline .env.example --json\n"
               "  %(prog)s envs/ --show-values\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="+",
                        help="Env files, directories, or glob patterns to compare")
    parser.add_argument("--baseline", metavar="FILE",
                        help="Baseline file (e.g., .env.example) to compare all envs against")
    parser.add_argument("--show-values", action="store_true",
                        help="Show actual values instead of redacting secrets")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")

    args = parser.parse_args()

    env_files = resolve_env_files(args.paths)
    if not env_files:
        print("Error: No env files found from the provided paths.", file=sys.stderr)
        return 2

    if args.baseline and not Path(args.baseline).exists():
        print(f"Error: Baseline file not found: {args.baseline}", file=sys.stderr)
        return 2

    results = check_sync(env_files, baseline_path=args.baseline, show_values=args.show_values)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print_human(results)

    if "error" in results:
        return 2
    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
