#!/usr/bin/env python3
"""Track model versions, metadata, and lifecycle stage in a local JSON registry.

Maintains a structured model registry.  Each entry records model name,
version, metrics, parameters, stage (staging/production/archived), and
timestamps.  Supports registering, promoting, listing, and comparing models.

Usage:
    python model_registry.py register --name fraud_detector --version v2.3 --metrics '{"f1":0.91,"auc":0.95}' --params '{"n_estimators":200}'
    python model_registry.py promote --name fraud_detector --version v2.3 --stage production
    python model_registry.py list --name fraud_detector
    python model_registry.py list --stage production --json
    python model_registry.py compare --name fraud_detector --versions v2.2 v2.3
"""

import argparse
import json
import os
import sys
from datetime import datetime


DEFAULT_REGISTRY = "model_registry.json"
VALID_STAGES = {"development", "staging", "production", "archived", "retired"}


def _load_registry(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_registry(registry: list, path: str):
    with open(path, "w") as f:
        json.dump(registry, f, indent=2)


def _find_entry(registry: list, name: str, version: str):
    for entry in registry:
        if entry["name"] == name and entry["version"] == version:
            return entry
    return None


def cmd_register(args):
    registry = _load_registry(args.registry)

    existing = _find_entry(registry, args.name, args.version)
    if existing:
        print(f"Error: Model '{args.name}' version '{args.version}' already registered. Use 'promote' to update stage.", file=sys.stderr)
        sys.exit(1)

    try:
        metrics = json.loads(args.metrics) if args.metrics else {}
    except json.JSONDecodeError:
        print("Error: --metrics must be valid JSON.", file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(args.params) if args.params else {}
    except json.JSONDecodeError:
        print("Error: --params must be valid JSON.", file=sys.stderr)
        sys.exit(1)

    entry = {
        "name": args.name,
        "version": args.version,
        "stage": args.stage or "development",
        "registered_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "metrics": metrics,
        "parameters": params,
        "tags": [t.strip() for t in args.tags.split(",")] if args.tags else [],
        "description": args.description or "",
        "artifact_path": args.artifact or "",
    }

    registry.append(entry)
    _save_registry(registry, args.registry)

    if args.json:
        print(json.dumps(entry, indent=2))
    else:
        print(f"Registered: {args.name} {args.version} (stage: {entry['stage']})")
        if metrics:
            print(f"  Metrics: {json.dumps(metrics)}")


def cmd_promote(args):
    registry = _load_registry(args.registry)
    entry = _find_entry(registry, args.name, args.version)

    if not entry:
        print(f"Error: Model '{args.name}' version '{args.version}' not found.", file=sys.stderr)
        sys.exit(1)

    if args.stage not in VALID_STAGES:
        print(f"Error: Invalid stage '{args.stage}'. Valid: {', '.join(sorted(VALID_STAGES))}.", file=sys.stderr)
        sys.exit(1)

    old_stage = entry["stage"]

    # If promoting to production, archive the current production version
    if args.stage == "production":
        for e in registry:
            if e["name"] == args.name and e["stage"] == "production" and e["version"] != args.version:
                e["stage"] = "archived"
                e["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    entry["stage"] = args.stage
    entry["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _save_registry(registry, args.registry)

    if args.json:
        print(json.dumps(entry, indent=2))
    else:
        print(f"Promoted: {args.name} {args.version}: {old_stage} -> {args.stage}")


def cmd_list(args):
    registry = _load_registry(args.registry)
    if not registry:
        print("Registry is empty.")
        return

    filtered = registry
    if args.name:
        filtered = [e for e in filtered if e["name"] == args.name]
    if args.stage:
        filtered = [e for e in filtered if e["stage"] == args.stage]

    filtered.sort(key=lambda e: e["updated_at"], reverse=True)

    if args.json:
        print(json.dumps(filtered, indent=2))
    else:
        print(f"{'Name':<25} {'Version':<10} {'Stage':<14} {'Updated':<20} {'Metrics'}")
        print("-" * 90)
        for e in filtered:
            metrics_str = ", ".join(f"{k}={v}" for k, v in e.get("metrics", {}).items())
            print(f"{e['name']:<25} {e['version']:<10} {e['stage']:<14} {e['updated_at']:<20} {metrics_str}")


def cmd_compare(args):
    registry = _load_registry(args.registry)
    entries = [e for e in registry if e["name"] == args.name and e["version"] in args.versions]

    if len(entries) < 2:
        print(f"Error: Need at least 2 versions to compare. Found {len(entries)} for '{args.name}'.", file=sys.stderr)
        sys.exit(1)

    all_metrics = set()
    all_params = set()
    for e in entries:
        all_metrics.update(e.get("metrics", {}).keys())
        all_params.update(e.get("parameters", {}).keys())

    if args.json:
        print(json.dumps({"name": args.name, "entries": entries, "metric_keys": sorted(all_metrics)}, indent=2))
    else:
        print(f"Model Comparison: {args.name}")
        print("=" * 60)

        header = f"{'Attribute':<20}"
        for e in entries:
            header += f" {e['version']:<18}"
        print(header)
        print("-" * len(header))

        print(f"{'stage':<20}" + "".join(f" {e['stage']:<18}" for e in entries))
        print(f"{'updated_at':<20}" + "".join(f" {e['updated_at']:<18}" for e in entries))

        if all_metrics:
            print("\nMetrics:")
            for m in sorted(all_metrics):
                vals = [e.get("metrics", {}).get(m) for e in entries]
                best = max((v for v in vals if v is not None), default=None)
                row = f"  {m:<18}"
                for v in vals:
                    marker = " *" if v == best and v is not None else ""
                    row += f" {str(v if v is not None else '-'):<16}{marker}"
                print(row)
            print("  * = best")

        if all_params:
            print("\nParameters:")
            for p in sorted(all_params):
                row = f"  {p:<18}"
                for e in entries:
                    val = e.get("parameters", {}).get(p, "-")
                    row += f" {str(val):<18}"
                print(row)


def main():
    parser = argparse.ArgumentParser(description="Manage a local model version registry.")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY, help=f"Path to registry file (default: {DEFAULT_REGISTRY})")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    sub = parser.add_subparsers(dest="command", help="Command")

    reg = sub.add_parser("register", help="Register a new model version")
    reg.add_argument("--name", required=True, help="Model name")
    reg.add_argument("--version", required=True, help="Model version")
    reg.add_argument("--metrics", help="Metrics as JSON string")
    reg.add_argument("--params", help="Parameters as JSON string")
    reg.add_argument("--stage", default="development", help="Initial stage")
    reg.add_argument("--tags", help="Comma-separated tags")
    reg.add_argument("--description", help="Model description")
    reg.add_argument("--artifact", help="Path to model artifact")

    promo = sub.add_parser("promote", help="Change model stage")
    promo.add_argument("--name", required=True, help="Model name")
    promo.add_argument("--version", required=True, help="Model version")
    promo.add_argument("--stage", required=True, help=f"Target stage: {', '.join(sorted(VALID_STAGES))}")

    lst = sub.add_parser("list", help="List registered models")
    lst.add_argument("--name", help="Filter by model name")
    lst.add_argument("--stage", help="Filter by stage")

    cmp = sub.add_parser("compare", help="Compare model versions")
    cmp.add_argument("--name", required=True, help="Model name")
    cmp.add_argument("--versions", nargs="+", required=True, help="Versions to compare")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "register":
        cmd_register(args)
    elif args.command == "promote":
        cmd_promote(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "compare":
        cmd_compare(args)


if __name__ == "__main__":
    main()
