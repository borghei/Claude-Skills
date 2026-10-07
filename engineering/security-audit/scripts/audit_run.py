#!/usr/bin/env python3
"""Set up and summarise a security audit run.

Subcommands:
    init         create the run directory, run-metadata.json, and empty
                 ledger and findings files outside the target repository
    coverage-id  derive the deterministic ID of a coverage unit
    budget       split an agent budget into recon, hunters, critics, verifiers
    summary      count ledger and findings state for the final report

Exit codes: 0 success, 1 the request cannot be satisfied (budget too small,
unsafe output location), 2 unreadable input or usage error.

Usage:
    python3 audit_run.py init --target ~/code/app --tier focused
    python3 audit_run.py coverage-id --surface "src/api.py#POST /orders" \
        --boundary "src/authz.py#require_owner" --subsystem services/orders \
        --attack-class "attack-classes.md#Access control"
    python3 audit_run.py budget --budget 40 --profile standard --units 28
    python3 audit_run.py summary --run-dir ~/security-audits/app/run-1
"""

import argparse
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import (  # noqa: E402
    PROFILES, SEVERITIES, TIERS, AuditInputError, coverage_id, is_repo_path,
    load_json)

RECON_AGENTS = 4
CRITICS = {"quick": 1, "standard": 2, "deep": 2}
VERIFIERS_PER_CANDIDATE = {"quick": 1, "standard": 2, "deep": 2}


def git(target: Path, *args: str) -> Optional[str]:
    """Run a read-only git query in the target; None when unavailable.

    The target is untrusted: its own git config must not run a helper, and the
    query must not rewrite its index.
    """
    try:
        done = subprocess.run(["git", "-c", "core.fsmonitor=false",
                               "-c", "safe.bareRepository=explicit",
                               "--no-optional-locks", "-C", str(target), *args],
                              check=False,
                              capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def plan_budget(budget: int, profile: str, units: int,
                candidates: Optional[int]) -> Dict[str, Any]:
    """Reserve recon, critics, and verifiers first; hunters get the rest."""
    critics = CRITICS[profile]
    per_candidate = VERIFIERS_PER_CANDIDATE[profile]
    minimum = RECON_AGENTS + critics + per_candidate
    remaining = budget - RECON_AGENTS - critics
    if candidates is None:
        reserve = max(per_candidate, math.ceil(max(remaining, 0) * 0.3))
    else:
        reserve = max(per_candidate, candidates * per_candidate)
    hunters = max(0, remaining - reserve)
    return {
        "budget": budget, "profile": profile, "minimum_budget": minimum,
        "feasible": budget >= minimum, "recon": RECON_AGENTS, "critics": critics,
        "validation_reserve": reserve, "hunters": hunters, "units": units,
        "units_deferred": max(0, units - hunters),
        "defer_reason": "budget_cannot_fund_hunters" if units > hunters else None,
    }


def cmd_init(args: argparse.Namespace) -> Dict[str, Any]:
    """Create run-N for the target and write its starting files."""
    target = args.target.expanduser().resolve()
    if not target.is_dir():
        raise AuditInputError(f"target is not a directory: {target}")
    for scope in args.scope:
        if not is_repo_path(scope):
            raise AuditInputError(f"--scope {scope!r} must be repository-relative")
    repo = re.sub(r"[^A-Za-z0-9._-]", "-", target.name) or "target"
    root = (args.output_root.expanduser().resolve()) / repo
    if (root == target or target in root.parents) and not args.allow_inside_target:
        return {"ok": False, "error": "output directory is inside the target; "
                "choose a path outside it, or pass --allow-inside-target only "
                "when version control ignores that whole directory"}
    if args.budget is not None:
        gate = plan_budget(args.budget, args.profile, 0, None)
        if not gate["feasible"]:
            return {"ok": False, "error": f"budget {args.budget} cannot fund "
                    f"reconnaissance, critics, and one verifier (minimum "
                    f"{gate['minimum_budget']}); raise it, narrow the scope, "
                    "or pick the quick profile"}
    number = 1
    while (root / f"run-{number}").exists():
        number += 1
    prior = sorted(str(path.parent) for path in root.glob("run-*/coverage-ledger.json"))
    run_dir = root / f"run-{number}"
    (run_dir / "agents").mkdir(parents=True)
    run_id = f"{repo}-run-{number}"
    commit = git(target, "rev-parse", "HEAD")
    status = git(target, "status", "--porcelain")
    metadata = {
        "schema_version": 1, "run_id": run_id, "repo": repo, "target": str(target),
        "source_ref": {"commit": commit,
                       "dirty": None if status is None else bool(status)},
        "tier": args.tier, "companions": TIERS[args.tier], "profile": args.profile,
        "scope_paths": args.scope, "budget": args.budget, "agents_spent": 0,
        "execution_policy": "source-review-and-sandboxed-local-only",
        "prior_runs": prior, "shared_file_owner": "lead",
        "run_status": "in_progress", "incomplete_reason": None,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    files = {"run-metadata.json": metadata,
             "coverage-ledger.json": {"schema_version": 1, "run_id": run_id, "units": []},
             "findings.json": {"schema_version": 1, "run_id": run_id, "findings": []}}
    for name, body in files.items():
        (run_dir / name).write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "run_dir": str(run_dir), "run_id": run_id,
            "tier": args.tier, "companions": TIERS[args.tier],
            "profile": args.profile, "prior_runs": prior,
            "partial_coverage": args.profile == "quick" or bool(args.scope)
            or args.tier != "full"}


def cmd_summary(args: argparse.Namespace) -> Dict[str, Any]:
    """Count unit states and verdicts, and list every disclosed gap."""
    run_dir = args.run_dir.expanduser()
    metadata = load_json(run_dir / "run-metadata.json")
    units = load_json(run_dir / "coverage-ledger.json").get("units", [])
    records = load_json(run_dir / "findings.json").get("findings", [])
    statuses: Dict[str, int] = {}
    gaps: List[Dict[str, Any]] = []
    linked: set = set()
    for unit in units:
        status = unit.get("status", "unknown")
        statuses[status] = statuses.get(status, 0) + 1
        if status == "candidate":
            linked |= set(unit.get("fingerprints", []))
        if status in ("deferred", "out_of_scope", "blocked", "planned", "in_progress"):
            gaps.append({"coverage_id": unit.get("coverage_id"), "status": status,
                         "label": unit.get("label"),
                         "reason": "; ".join(unit.get("unresolved", []))})
    verdicts: Dict[str, int] = {}
    severities = {level: 0 for level in reversed(SEVERITIES)}
    for record in records:
        verdict = record.get("verdict", "unknown")
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        if verdict == "confirmed":
            severities[record["severity"]["overall"]] += 1
    recorded = {record.get("fingerprint") for record in records}
    return {
        "ok": True, "run_id": metadata.get("run_id"), "tier": metadata.get("tier"),
        "profile": metadata.get("profile"), "scope_paths": metadata.get("scope_paths"),
        "run_status": metadata.get("run_status"),
        "budget": metadata.get("budget"), "agents_spent": metadata.get("agents_spent"),
        "units": statuses, "verdicts": verdicts, "confirmed_by_severity": severities,
        "gaps": gaps, "unvalidated_candidates": sorted(linked - recorded),
    }


def render(command: str, result: Dict[str, Any]) -> str:
    """Readable output; the summary form pastes into REPORT.md."""
    if not result.get("ok", True):
        return f"ERROR: {result['error']}"
    if command == "coverage-id":
        return result["coverage_id"]
    if command != "summary":
        return "\n".join(f"{key}: {value}" for key, value in result.items()
                         if key != "ok")
    lines = [f"Run {result['run_id']} - tier {result['tier']}, profile "
             f"{result['profile']}, status {result['run_status']}", "",
             "| Unit status | Count |", "|---|---|"]
    lines += [f"| {name} | {count} |" for name, count in sorted(result["units"].items())]
    lines += ["", "| Verdict | Count |", "|---|---|"]
    lines += [f"| {name} | {count} |" for name, count in sorted(result["verdicts"].items())]
    lines += ["", "| Confirmed severity | Count |", "|---|---|"]
    lines += [f"| {name} | {count} |"
              for name, count in result["confirmed_by_severity"].items()]
    if result["gaps"]:
        lines += ["", "| Coverage gap | Status | Reason |", "|---|---|---|"]
        lines += [f"| {gap['label']} | {gap['status']} | {gap['reason'] or '-'} |"
                  for gap in result["gaps"]]
    if result["unvalidated_candidates"]:
        lines += ["", "Unvalidated candidates (not findings): "
                  + ", ".join(result["unvalidated_candidates"])]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Define the subcommands and their options."""
    parser = argparse.ArgumentParser(
        description="Set up and summarise a security audit run.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create a run directory outside the target")
    init.add_argument("--target", type=Path, required=True, help="repository root to audit")
    init.add_argument("--output-root", type=Path, default=Path("~/security-audits"),
                      help="parent of <repo>/run-<N> (default: ~/security-audits)")
    init.add_argument("--tier", choices=sorted(TIERS), default="focused",
                      help="breadth: core, focused (core + 4 companions), full (all 10)")
    init.add_argument("--profile", choices=PROFILES, default="standard",
                      help="depth and redundancy of the run (default: standard)")
    init.add_argument("--scope", action="append", default=[], metavar="PATH",
                      help="limit the run to a repository-relative path (repeatable)")
    init.add_argument("--budget", type=int, help="maximum agent invocations")
    init.add_argument("--allow-inside-target", action="store_true",
                      help="permit an output root inside the target (must be git-ignored)")
    ident = sub.add_parser("coverage-id", help="derive a coverage unit ID")
    for name in ("surface", "boundary", "subsystem", "attack-class"):
        ident.add_argument(f"--{name}", required=True, help=f"canonical {name} reference")
    ident.add_argument("--lifecycle", help="lifecycle mode, when it is material")
    budget = sub.add_parser("budget", help="allocate an agent budget")
    budget.add_argument("--budget", type=int, required=True, help="maximum agent invocations")
    budget.add_argument("--profile", choices=PROFILES, default="standard")
    budget.add_argument("--units", type=int, required=True, help="planned coverage units")
    budget.add_argument("--candidates", type=int,
                        help="expected candidates (default: reserve 30%% of the balance)")
    summary = sub.add_parser("summary", help="count ledger and findings state")
    summary.add_argument("--run-dir", type=Path, required=True, help="run directory")
    return parser


def main() -> None:
    """Dispatch the chosen subcommand and set the exit code."""
    args = build_parser().parse_args()
    try:
        if args.command == "init":
            result = cmd_init(args)
        elif args.command == "summary":
            result = cmd_summary(args)
        elif args.command == "budget":
            result = plan_budget(args.budget, args.profile, args.units, args.candidates)
            result["ok"] = result["feasible"]
            if not result["feasible"]:
                result["error"] = (f"budget below the minimum of "
                                   f"{result['minimum_budget']} for this profile")
        else:
            refs = {"surface": args.surface, "boundary": args.boundary,
                    "subsystem": args.subsystem, "attack_class": args.attack_class}
            if args.lifecycle:
                refs["lifecycle"] = args.lifecycle
            result = {"ok": True, "coverage_id": coverage_id(refs), "refs": refs}
    except (AuditInputError, OSError, KeyError, TypeError, AttributeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render(args.command, result))
    sys.exit(0 if result.get("ok", True) else 1)


if __name__ == "__main__":
    main()
