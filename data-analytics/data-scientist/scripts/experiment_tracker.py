#!/usr/bin/env python3
"""Track data science experiments: parameters, metrics, and notes in a local JSON log.

Maintains a structured experiment log file.  Each experiment records a name,
parameters, metrics, tags, and timestamps.  Supports listing, comparing, and
filtering experiments.

Usage:
    python experiment_tracker.py log --name "xgb_v2" --params '{"lr":0.1,"depth":6}' --metrics '{"f1":0.87,"auc":0.92}'
    python experiment_tracker.py list
    python experiment_tracker.py list --sort-by f1 --top 5
    python experiment_tracker.py compare --ids 1 3 5
    python experiment_tracker.py log --name "baseline" --params '{}' --metrics '{"f1":0.72}' --tags "baseline,prod" --json
"""

import argparse
import json
import os
import sys
from datetime import datetime


DEFAULT_LOG_FILE = "experiments.json"


def _load_experiments(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_experiments(experiments: list, path: str):
    with open(path, "w") as f:
        json.dump(experiments, f, indent=2)


def cmd_log(args):
    experiments = _load_experiments(args.log_file)

    try:
        params = json.loads(args.params) if args.params else {}
    except json.JSONDecodeError:
        print("Error: --params must be valid JSON.", file=sys.stderr)
        sys.exit(1)

    try:
        metrics = json.loads(args.metrics) if args.metrics else {}
    except json.JSONDecodeError:
        print("Error: --metrics must be valid JSON.", file=sys.stderr)
        sys.exit(1)

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    exp_id = len(experiments) + 1
    entry = {
        "id": exp_id,
        "name": args.name,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "parameters": params,
        "metrics": metrics,
        "tags": tags,
        "notes": args.notes or "",
    }

    experiments.append(entry)
    _save_experiments(experiments, args.log_file)

    if args.json:
        print(json.dumps(entry, indent=2))
    else:
        print(f"Experiment #{exp_id} logged: {args.name}")
        if params:
            print(f"  Params:  {json.dumps(params)}")
        if metrics:
            print(f"  Metrics: {json.dumps(metrics)}")
        if tags:
            print(f"  Tags:    {', '.join(tags)}")


def cmd_list(args):
    experiments = _load_experiments(args.log_file)
    if not experiments:
        print("No experiments logged yet.")
        return

    # Filter by tag
    if args.tag:
        experiments = [e for e in experiments if args.tag in e.get("tags", [])]

    # Sort
    if args.sort_by:
        metric_key = args.sort_by
        experiments = [e for e in experiments if metric_key in e.get("metrics", {})]
        experiments.sort(key=lambda e: e["metrics"][metric_key], reverse=True)

    # Top N
    if args.top:
        experiments = experiments[: args.top]

    if args.json:
        print(json.dumps(experiments, indent=2))
    else:
        print(f"{'ID':<5} {'Name':<25} {'Timestamp':<20} {'Metrics'}")
        print("-" * 80)
        for e in experiments:
            metrics_str = ", ".join(f"{k}={v}" for k, v in e.get("metrics", {}).items())
            print(f"{e['id']:<5} {e['name']:<25} {e['timestamp']:<20} {metrics_str}")


def cmd_compare(args):
    experiments = _load_experiments(args.log_file)
    if not experiments:
        print("No experiments logged yet.")
        return

    selected = [e for e in experiments if e["id"] in args.ids]
    if not selected:
        print(f"No experiments found with IDs: {args.ids}", file=sys.stderr)
        sys.exit(1)

    # Gather all metric keys
    all_metrics = set()
    for e in selected:
        all_metrics.update(e.get("metrics", {}).keys())
    all_metrics = sorted(all_metrics)

    # Gather all param keys
    all_params = set()
    for e in selected:
        all_params.update(e.get("parameters", {}).keys())
    all_params = sorted(all_params)

    if args.json:
        comparison = {
            "experiments": selected,
            "metric_keys": all_metrics,
            "param_keys": all_params,
        }
        # Find best per metric
        bests = {}
        for m in all_metrics:
            vals = [(e["id"], e["metrics"].get(m)) for e in selected if m in e.get("metrics", {})]
            if vals:
                best = max(vals, key=lambda x: x[1])
                bests[m] = {"experiment_id": best[0], "value": best[1]}
        comparison["best_per_metric"] = bests
        print(json.dumps(comparison, indent=2))
    else:
        # Header
        header = f"{'Metric':<20}"
        for e in selected:
            header += f" {'#' + str(e['id']) + ' ' + e['name']:<20}"
        print("Experiment Comparison")
        print("=" * 60)
        print(header)
        print("-" * len(header))

        # Parameters
        if all_params:
            print("\nParameters:")
            for p in all_params:
                row = f"  {p:<18}"
                for e in selected:
                    val = e.get("parameters", {}).get(p, "-")
                    row += f" {str(val):<20}"
                print(row)

        # Metrics
        if all_metrics:
            print("\nMetrics:")
            for m in all_metrics:
                values = []
                for e in selected:
                    val = e.get("metrics", {}).get(m)
                    values.append(val)
                best_val = max((v for v in values if v is not None), default=None)
                row = f"  {m:<18}"
                for val in values:
                    marker = " *" if val is not None and val == best_val else ""
                    row += f" {str(val if val is not None else '-'):<18}{marker}"
                print(row)
            print("\n  * = best value")


def main():
    parser = argparse.ArgumentParser(description="Track and compare data science experiments.")
    parser.add_argument("--log-file", default=DEFAULT_LOG_FILE, help=f"Path to experiment log (default: {DEFAULT_LOG_FILE})")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # log
    log_parser = subparsers.add_parser("log", help="Log a new experiment")
    log_parser.add_argument("--name", required=True, help="Experiment name")
    log_parser.add_argument("--params", help="Parameters as JSON string")
    log_parser.add_argument("--metrics", help="Metrics as JSON string")
    log_parser.add_argument("--tags", help="Comma-separated tags")
    log_parser.add_argument("--notes", help="Free-text notes")

    # list
    list_parser = subparsers.add_parser("list", help="List experiments")
    list_parser.add_argument("--sort-by", help="Sort by metric name (descending)")
    list_parser.add_argument("--top", type=int, help="Show top N experiments")
    list_parser.add_argument("--tag", help="Filter by tag")

    # compare
    cmp_parser = subparsers.add_parser("compare", help="Compare experiments side-by-side")
    cmp_parser.add_argument("--ids", nargs="+", type=int, required=True, help="Experiment IDs to compare")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "log":
        cmd_log(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "compare":
        cmd_compare(args)


if __name__ == "__main__":
    main()
