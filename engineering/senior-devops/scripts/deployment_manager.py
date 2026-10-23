#!/usr/bin/env python3
"""Produce a deployment plan (strategy, steps, health checks, rollback) from a service spec.

Reads a JSON deployment spec, picks rolling, blue-green or canary from risk, traffic,
statefulness, schema change and rollback tolerance, and prints the plan: steps with
traffic weights and bake times, probe thresholds, automatic rollback triggers and a
rollback runbook. It only plans; it never runs kubectl, cloud CLIs or anything else.

Usage:
    python deployment_manager.py <spec.json>
    python deployment_manager.py <spec.json> --strategy blue-green --json
    python deployment_manager.py --example > deploy.json
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

STRATEGIES = ("rolling", "blue-green", "canary")
EXAMPLE = {
    "service": "checkout-api", "version": "2.4.0", "previous_version": "2.3.1", "replicas": 6,
    "risk": "medium", "user_facing": True, "traffic_rps": 400, "stateful": False,
    "schema_change": "backward_compatible", "rollback_tolerance_minutes": 5, "can_double_capacity": False,
    "health": {"port": 8080, "liveness_path": "/healthz", "readiness_path": "/ready", "startup_seconds": 20},
    "baseline": {"error_rate_pct": 0.3, "p99_latency_ms": 220},
    "slo": {"error_rate_pct": 1.0, "p99_latency_ms": 500},
}
CANARY_LADDERS = {"high": ([1, 5, 25, 50, 100], 15), "medium": ([5, 25, 50, 100], 10), "low": ([10, 50, 100], 5)}
MIN_REQUESTS_PER_STEP = 2000  # enough canary requests to see a 1% error rate with some confidence


FIELDS = {"service": "k8sname", "version": "tag", "previous_version": "tag", "replicas": "count", "risk": ("low", "medium", "high"),
          "user_facing": "bool", "traffic_rps": "num", "stateful": "bool", "can_double_capacity": "bool",
          "schema_change": ("none", "backward_compatible", "breaking"), "rollback_tolerance_minutes": "num",
          "health.port": "port", "health.liveness_path": "path", "health.readiness_path": "path", "health.startup_seconds": "num",
          "baseline.error_rate_pct": "num", "baseline.p99_latency_ms": "num", "slo.error_rate_pct": "num", "slo.p99_latency_ms": "num"}
KIND_TEXT = {"k8sname": "a Kubernetes name (lowercase letters, digits and '-', 1-63 characters, alphanumeric at both ends)",
             "tag": "an image tag (1-128 of A-Z a-z 0-9 . _ + -, not starting with . or -)", "bool": "true or false", "num": "a non-negative number", "count": "an integer of 1 or more",
             "port": "an integer from 1 to 65535", "path": "a URL path such as /healthz"}


def valid(value: object, kind: object) -> bool:
    """Return True when value matches the field kind from FIELDS."""
    number = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if isinstance(kind, tuple):
        return isinstance(value, str) and value in kind
    text = value if isinstance(value, str) else ""
    return {"k8sname": bool(re.fullmatch(r"[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?", text)),
            "tag": bool(re.fullmatch(r"[A-Za-z0-9_+][A-Za-z0-9._+-]{0,127}", text)), "bool": isinstance(value, bool),
            "num": number and value >= 0, "count": number and float(value).is_integer() and value >= 1,
            "port": number and float(value).is_integer() and 1 <= value <= 65535,
            "path": bool(re.fullmatch(r"/[A-Za-z0-9._~/-]{0,200}", text))}[kind]


def load_spec(path: str) -> Dict:
    """Load and validate the spec, filling defaults for optional fields."""
    p = Path(path)
    if p.is_dir():
        p = p / "deployment.json"
    if not p.is_file():
        raise ValueError(f"spec not found: {p} (pass a JSON file, or a directory containing deployment.json)")
    try:
        spec = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{p} is not valid JSON: {exc.msg} at line {exc.lineno}")
    if not isinstance(spec, dict):
        raise ValueError(f"{p}: spec must be a JSON object (see --example)")
    if "service" not in spec or "version" not in spec:
        raise ValueError(f"{p}: 'service' and 'version' are required (see --example)")
    for key, kind in FIELDS.items():
        section, _, field = key.rpartition(".")
        holder = spec.get(section, {}) if section else spec
        if not isinstance(holder, dict):
            raise ValueError(f"{p}: '{section}' must be an object (see --example)")
        if field in holder and not valid(holder[field], kind):
            raise ValueError(f"{p}: '{key}' must be {KIND_TEXT.get(kind, 'one of: ' + ', '.join(kind))}")
    defaults = {"previous_version": "previous", "replicas": 3, "risk": "medium", "user_facing": True, "traffic_rps": 0,
                "stateful": False, "schema_change": "none", "rollback_tolerance_minutes": 15, "can_double_capacity": False}
    missing = [k for k in ("baseline", "slo") if k not in spec]
    spec = {**defaults, **spec, "_warnings": []}
    if spec["previous_version"] == spec["version"]:
        spec["_warnings"].append(f"previous_version equals version ({spec['version']}): nothing changes, and rollback "
                                 "would redeploy the same build.")
    if missing:
        spec["_warnings"].append(f"No {' or '.join(missing)} in the spec; rollback thresholds use the example values. Supply real numbers.")
    spec["health"] = {**EXAMPLE["health"], **spec.get("health", {})}
    spec["baseline"] = {**EXAMPLE["baseline"], **spec.get("baseline", {})}
    spec["slo"] = {**EXAMPLE["slo"], **spec.get("slo", {})}
    return spec


def choose(spec: Dict) -> Tuple[str, List[str], List[str]]:
    """Pick a strategy and return it with the reasons and any warnings."""
    reasons, warnings = [], []
    risk, rps, tol = spec["risk"], spec["traffic_rps"], spec["rollback_tolerance_minutes"]
    if spec["schema_change"] == "breaking":
        warnings.append("Breaking schema change: every strategy runs old and new code against the same data for a while. "
                        "Split it into expand (additive, deploy), migrate, contract (remove, later deploy) before shipping.")
    if spec["stateful"]:
        reasons.append("Stateful service: two full copies or a split fleet would share or duplicate state, so replace pods one at a time.")
        return "rolling", reasons, warnings
    if tol <= 2 and spec["can_double_capacity"]:
        reasons.append(f"Rollback tolerance is {tol} min and capacity can double: blue-green rolls back with one traffic switch.")
        return "blue-green", reasons, warnings
    if spec["user_facing"] and risk != "low" and rps >= 20:
        reasons.append(f"User-facing, {risk} risk, {rps} rps: enough traffic to judge a small slice before exposing everyone.")
        return "canary", reasons, warnings
    if risk == "high":
        if spec["can_double_capacity"]:
            reasons.append(f"High risk but only {rps} rps, too little for a canary signal: verify a full green stack, then switch.")
            return "blue-green", reasons, warnings
        warnings.append("High risk without spare capacity for blue-green or traffic for a canary: roll slowly and watch closely.")
    if tol <= 2:
        warnings.append(f"Rollback tolerance is {tol} min but a rolling rollback takes several minutes; consider adding capacity for blue-green.")
    reasons.append(f"{risk.title()} risk, {'user-facing' if spec['user_facing'] else 'internal'}, {rps} rps: "
                   "a rolling update with surge capacity and readiness gates is enough.")
    return "rolling", reasons, warnings


def steps_for(strategy: str, spec: Dict) -> List[Dict]:
    """Return ordered deployment steps; canary steps carry traffic weight and bake time."""
    svc, ver, n = spec["service"], spec["version"], max(int(spec["replicas"]), 1)
    if strategy == "canary":
        ladder, base = CANARY_LADDERS[spec["risk"]]
        out = [{"step": "deploy canary", "detail": f"Start {svc}:{ver} next to the stable version with 0% traffic; wait for readiness."}]
        for pct in ladder[:-1]:
            rps_at = spec["traffic_rps"] * pct / 100
            need = math.ceil(MIN_REQUESTS_PER_STEP / rps_at / 60) if rps_at else 10 ** 6  # no traffic, no signal
            bake = min(max(base, need), 60)
            if need > 60 and not any("Too little traffic" in w for w in spec.setdefault("_warnings", [])):
                spec["_warnings"].append(f"Too little traffic for a {pct}% canary step to reach {MIN_REQUESTS_PER_STEP} "
                                         "requests in 60 min; bake time is capped at 60 min, so treat early steps as smoke tests.")
            out.append({"step": f"shift {pct}%", "traffic_pct": pct, "bake_minutes": bake,
                        "detail": f"Route {pct}% to {ver}; compare canary against stable on the rollback triggers for {bake} min."})
        out.append({"step": "promote 100%", "traffic_pct": 100, "bake_minutes": base,
                    "detail": f"Route all traffic to {ver}; keep the stable ReplicaSet scaled for {base} min, then scale it down."})
        return out
    if strategy == "blue-green":
        keep = max(30, int(spec["rollback_tolerance_minutes"]) * 6)
        return [{"step": "deploy green", "detail": f"Start {n} replicas of {svc}:{ver} as green; no production traffic."},
                {"step": "verify green", "detail": "Run smoke tests against the green service address; all probes ready."},
                {"step": "switch", "traffic_pct": 100, "detail": "Point the router or Service selector at green in one change."},
                {"step": "bake", "bake_minutes": 15, "detail": "Watch the rollback triggers; blue stays running and untouched."},
                {"step": "retire blue", "detail": f"Keep blue for {keep} min as the rollback target, then scale it to zero."}]
    surge, unavailable = ("0", "1") if spec["stateful"] else ("25%", "0")
    return [{"step": "configure", "detail": f"maxSurge={surge}, maxUnavailable={unavailable}, minReadySeconds=30, progressDeadlineSeconds=600."},
            {"step": "roll", "detail": f"Replace {n} pods with {svc}:{ver}; each new pod must pass readiness before an old one stops."
             + (" Ordered, one at a time (StatefulSet partition), with a backup taken first." if spec["stateful"] else "")},
            {"step": "bake", "bake_minutes": 10, "detail": "Watch the rollback triggers once every pod runs the new version."}]


def health_and_triggers(spec: Dict) -> Tuple[Dict, List[Dict]]:
    """Derive probe settings and automatic rollback triggers from baseline and SLO."""
    h, b, slo = spec["health"], spec["baseline"], spec["slo"]
    startup_failures = max(3, math.ceil(h["startup_seconds"] * 1.5 / 5))
    checks = {"startup": {"path": h["liveness_path"], "port": h["port"], "period_s": 5, "failure_threshold": startup_failures},
              "liveness": {"path": h["liveness_path"], "port": h["port"], "period_s": 10, "timeout_s": 2, "failure_threshold": 3},
              "readiness": {"path": h["readiness_path"], "port": h["port"], "period_s": 5, "timeout_s": 2,
                            "failure_threshold": 3, "success_threshold": 1},
              "smoke_test": "Hit the readiness path and one read-only business endpoint on the new version before it gets traffic."}
    err = round(min(max(b["error_rate_pct"] * 2, b["error_rate_pct"] + 0.5), slo["error_rate_pct"]), 2)
    lat = int(min(b["p99_latency_ms"] * 1.5, slo["p99_latency_ms"]))
    triggers = [{"signal": "error rate (5xx / total)", "threshold": f"> {err}%", "window": "2 consecutive 1-min windows"},
                {"signal": "p99 latency", "threshold": f"> {lat} ms", "window": "3 consecutive 1-min windows"},
                {"signal": "new pod readiness", "threshold": "not ready 5 min after start", "window": "any pod"},
                {"signal": "container restarts", "threshold": ">= 2 restarts of a new pod", "window": "10 min"}]
    return checks, triggers


def runbook(strategy: str, spec: Dict) -> List[str]:
    """Return the manual rollback procedure for the chosen strategy."""
    svc, prev = spec["service"], spec["previous_version"]
    first = {"canary": f"Set canary weight to 0% (Argo Rollouts: kubectl argo rollouts abort {svc}); stable is still serving.",
             "blue-green": f"Switch the router or Service selector back to blue ({prev}); blue was never scaled down.",
             "rolling": f"kubectl rollout undo deployment/{svc} (or redeploy {prev}); watch kubectl rollout status."}[strategy]
    steps = [first, "Confirm the error rate and p99 latency return to baseline within 5 minutes.",
             f"Freeze further deploys of {svc} and record the trigger, time and version in the incident channel.",
             "Keep the failed version's logs and metrics; open a post-incident review if users were affected."]
    if spec["schema_change"] != "none":
        steps.insert(2, f"Do not roll the schema back by hand: {prev} must still work against the migrated schema "
                        "(expand/contract). If it does not, escalate before touching the database.")
    return steps


def main() -> None:
    """Parse arguments, build the plan and print it as text or JSON."""
    ap = argparse.ArgumentParser(description="Produce a deployment plan from a JSON service spec. Never executes anything.")
    ap.add_argument("spec", nargs="?", help="deployment spec JSON file (or a directory containing deployment.json)")
    ap.add_argument("--strategy", choices=STRATEGIES, help="force a strategy instead of choosing one")
    ap.add_argument("--example", action="store_true", help="print a sample spec and exit")
    ap.add_argument("--json", action="store_true", help="print the plan as JSON")
    ap.add_argument("--output", "-o", help="also write the JSON plan to this file (refuses to overwrite)")
    ap.add_argument("--verbose", "-v", action="store_true", help="include the resolved spec in the output")
    args = ap.parse_args()
    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return
    try:
        if not args.spec:
            raise ValueError("a spec path is required (run with --example to see the format)")
        spec = load_spec(args.spec)
        chosen, reasons, warnings = choose(spec)
        strategy = args.strategy or chosen
        if args.strategy and args.strategy != chosen:
            reasons.append(f"Forced with --strategy {args.strategy}; the inputs alone point to {chosen}.")
            if args.strategy != "rolling" and spec["stateful"]:
                warnings.append(f"{args.strategy} on a stateful service: make sure both versions never write the same state.")
        checks, triggers = health_and_triggers(spec)
        steps = steps_for(strategy, spec)
        warnings += spec.pop("_warnings")
        plan = {"service": spec["service"], "version": spec["version"], "previous_version": spec["previous_version"],
                "strategy": strategy, "reasons": reasons, "warnings": warnings, "steps": steps,
                "health_checks": checks, "rollback_triggers": triggers, "rollback_runbook": runbook(strategy, spec),
                "executes_anything": False}
        if args.verbose:
            plan["spec"] = spec
        if args.output:
            if Path(args.output).exists():
                raise ValueError(f"{args.output} already exists; choose another path")
            Path(args.output).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps(plan, indent=2))
        return
    print(f"Deployment plan: {plan['service']} {plan['previous_version']} -> {plan['version']}  [{strategy}]")
    for r in reasons:
        print(f"  Why: {r}")
    for w in warnings:
        print(f"  Warning: {w}")
    print("\nSteps:")
    for i, s in enumerate(plan["steps"], 1):
        extra = "".join(f" [{k.split('_')[0]} {s[k]}{'%' if k == 'traffic_pct' else ' min'}]"
                        for k in ("traffic_pct", "bake_minutes") if k in s)
        print(f"  {i}. {s['step']}{extra}: {s['detail']}")
    print("\nHealth checks:")
    for name, c in checks.items():
        print(f"  {name}: {c if isinstance(c, str) else ', '.join(f'{k}={v}' for k, v in c.items())}")
    print("\nAutomatic rollback when any of these holds:")
    for t in triggers:
        print(f"  - {t['signal']} {t['threshold']} ({t['window']})")
    print("\nRollback runbook:")
    for i, s in enumerate(plan["rollback_runbook"], 1):
        print(f"  {i}. {s}")
    if args.output:
        print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
