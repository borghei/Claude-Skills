#!/usr/bin/env python3
"""
chaos_experiment_designer.py — Scaffold a chaos experiment document.

Given a target service, a fault type, and a few parameters, emits a complete
experiment template covering steady state, hypothesis, blast radius, abort
criteria, observation checklist, and the run/analyze/document loop.

Designed to make "let's do a chaos experiment" turn into a real plan in 60 seconds.

Stdlib only. Markdown or JSON output.

Usage:
    python3 chaos_experiment_designer.py --target payment-svc --fault dependency-timeout
    python3 chaos_experiment_designer.py --target search --fault pod-kill --duration 5m --maturity-level L2
    python3 chaos_experiment_designer.py --target api --fault network-latency --inject-value 200ms --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path


# Fault catalog with default parameters and standard observation lists
FAULT_CATALOG: dict[str, dict[str, object]] = {
    "pod-kill": {
        "description": "Kill one or more instances/pods of the target service",
        "real_world_analog": "Spot interruption, hypervisor reboot, OOM-kill",
        "default_inject_value": "1 pod",
        "hypothesis_template": "Killing {inject_value} of {target}'s pods causes < 30 seconds of degraded latency (within 2× baseline), error rate stays under 0.5%, replacement instance is healthy within 60 seconds.",
        "watch": ["per-pod error rate", "total error rate", "replica count", "in-flight request count", "autoscaler decisions"],
        "tools": ["Chaos Mesh PodChaos pod-kill", "Litmus pod-delete", "kubectl delete pod"],
        "abort_thresholds": {
            "total_error_rate_pct": 5.0,
            "p99_latency_multiplier": 3.0,
            "duration_seconds": 300,
        },
        "blast_radius_default": "1 of N pods",
        "common_bugs": [
            "in-flight requests aborted (graceful drain not honored)",
            "long startup time for replacement",
            "connection pool stuck on dead pod",
            "client retries cascade to other pods",
        ],
    },
    "network-latency": {
        "description": "Inject network latency on the target's outbound or inbound traffic",
        "real_world_analog": "Cross-region routing, congested link, vendor latency spike",
        "default_inject_value": "200ms",
        "hypothesis_template": "Adding {inject_value} of latency to {target}'s downstream calls increases end-to-end p99 by ≤ {inject_value} + 50ms. No timeouts fire. Retry rate increases by < 10%.",
        "watch": ["latency p50/p95/p99", "timeout count", "retry count", "circuit breaker state", "queue depth"],
        "tools": ["Chaos Mesh NetworkChaos delay", "Litmus pod-network-latency", "tc qdisc netem delay"],
        "abort_thresholds": {
            "timeout_rate_pct": 1.0,
            "circuit_breaker_state": "any open",
            "duration_seconds": 600,
        },
        "blast_radius_default": "All traffic from/to target during experiment",
        "common_bugs": [
            "hard-coded timeouts shorter than expected latency",
            "retry storms when timeout fires",
            "client-side queue overflow",
            "metric pollution from per-call timers",
        ],
    },
    "network-partition": {
        "description": "Block all traffic between target and a specified peer/network",
        "real_world_analog": "AZ network failure, security group misconfiguration, BGP issue",
        "default_inject_value": "full partition for 60s",
        "hypothesis_template": "When traffic between {target} and dependency is blocked, {target} serves cached data for ≤ cache TTL, then returns clear errors with retry-after. No hung connections. Health check reflects degraded state within 30s.",
        "watch": ["connection establishment rate", "connection timeout rate", "open file descriptors", "cache hit rate", "downstream call rate"],
        "tools": ["Chaos Mesh NetworkChaos partition", "Litmus pod-network-partition", "iptables / security groups"],
        "abort_thresholds": {
            "open_fd_growth_rate": "no monotonic growth",
            "unrelated_feature_error_rate_pct": 0.5,
            "duration_seconds": 300,
        },
        "blast_radius_default": "All traffic to specified peer",
        "common_bugs": [
            "sockets leaked on partition (eventual OOM)",
            "cache returns stale data without indicating staleness",
            "health check still reports healthy",
            "cascade to upstream when downstream is partitioned",
        ],
    },
    "dependency-timeout": {
        "description": "Mock the target's downstream to return slowly (above timeout)",
        "real_world_analog": "Downstream overloaded, GC pause, cross-region call",
        "default_inject_value": "2000ms response time",
        "hypothesis_template": "When {target}'s downstream returns in {inject_value}, circuit breaker trips after N requests, fallback engages, no requests hang.",
        "watch": ["downstream p95/p99 latency", "downstream timeout count", "circuit breaker state", "fallback path metrics", "thread pool utilization"],
        "tools": ["Toxiproxy latency toxic", "Mountebank with delayed responses", "Chaos Mesh NetworkChaos delay between specific services"],
        "abort_thresholds": {
            "thread_pool_saturation_pct": 90,
            "fallback_unavailable": "abort if fallback doesn't engage",
            "duration_seconds": 300,
        },
        "blast_radius_default": "All calls to mocked downstream from target",
        "common_bugs": [
            "no caller-side timeout",
            "timeout too long",
            "in-flight call count grows unboundedly",
            "thread pool saturates and degrades other work",
        ],
    },
    "dependency-error": {
        "description": "Mock the target's downstream to return errors (5xx)",
        "real_world_analog": "Downstream outage, deploy hiccup, vendor incident",
        "default_inject_value": "100% 503 responses for 5min",
        "hypothesis_template": "When {target}'s downstream returns errors at {inject_value}, fallback path engages, error rate on parent feature stays < 0.5%, alerting fires within 2 minutes.",
        "watch": ["per-dependency error rate", "fallback path utilization", "retry count", "circuit breaker state", "end-user-visible metrics on dependent features"],
        "tools": ["Toxiproxy", "Mountebank", "custom controllable proxy"],
        "abort_thresholds": {
            "user_visible_error_rate_pct": 1.0,
            "retry_storm_threshold": "retry rate > 100× normal",
            "duration_seconds": 600,
        },
        "blast_radius_default": "Only calls to mocked downstream from target",
        "common_bugs": [
            "no fallback at all",
            "fallback itself broken",
            "retries amplify load on degraded downstream",
            "circuit breaker never opens or never closes",
        ],
    },
    "cpu-saturation": {
        "description": "Saturate CPU on the target instance(s)",
        "real_world_analog": "Runaway worker, GC death-spiral, noisy neighbor",
        "default_inject_value": "100% on all cores",
        "hypothesis_template": "Saturating {target}'s CPU at {inject_value} causes latency increase but no errors. Other co-located processes are throttled (cgroup limits) but functional.",
        "watch": ["CPU per pod", "CPU per host", "latency", "error rate", "throttle metrics", "GC time"],
        "tools": ["Chaos Mesh StressChaos", "Litmus pod-cpu-hog", "stress-ng"],
        "abort_thresholds": {
            "error_rate_pct": 5.0,
            "GC_pause_ms": 5000,
            "duration_seconds": 300,
        },
        "blast_radius_default": "1 instance",
        "common_bugs": [
            "no CPU limits (one runaway eats host)",
            "thread starvation in fixed pools",
            "long GC pauses misattributed",
        ],
    },
    "memory-pressure": {
        "description": "Consume memory on the target instance(s)",
        "real_world_analog": "Memory leak, large request, batch job, cache growth",
        "default_inject_value": "90% memory used",
        "hypothesis_template": "Under {inject_value} memory pressure on {target}, kernel pages out cleanly; app continues with slight latency increase; OOM-killer doesn't fire unless cgroup limit exceeded.",
        "watch": ["memory per pod", "swap usage", "OOM events", "latency", "error rate"],
        "tools": ["Chaos Mesh StressChaos", "Litmus pod-memory-hog", "stress-ng"],
        "abort_thresholds": {
            "OOM_kill_count": 0,
            "error_rate_pct": 2.0,
            "duration_seconds": 300,
        },
        "blast_radius_default": "1 instance",
        "common_bugs": [
            "process OOM-killed instead of throttled",
            "cache doesn't evict under pressure",
            "large allocations fail mid-request",
        ],
    },
    "disk-fill": {
        "description": "Fill the target's disk to high utilization",
        "real_world_analog": "Log rotation failure, runaway cache, large uploads",
        "default_inject_value": "95% disk used",
        "hypothesis_template": "At {inject_value} disk on {target}: alert fires within 1 min; app rejects writes with 4xx; no data corruption; recovery is automatic when space is freed.",
        "watch": ["disk usage percent", "write success rate", "log write rate", "application error rate"],
        "tools": ["dd if=/dev/zero", "Chaos Mesh IOChaos"],
        "abort_thresholds": {
            "process_crash": "abort on any crash",
            "data_corruption": "abort on any detected corruption",
            "duration_seconds": 600,
        },
        "blast_radius_default": "1 instance disk volume",
        "common_bugs": [
            "app crashes on write failure",
            "logger silently drops when /var/log full",
            "alert fires only at 100%",
        ],
    },
    "traffic-spike": {
        "description": "Generate synthetic traffic at multiplied rate",
        "real_world_analog": "Viral moment, bot attack, product launch",
        "default_inject_value": "5x normal RPS for 5min",
        "hypothesis_template": "At {inject_value} for 5min against {target}: autoscaler engages within 90s, latency stays under SLO, error rate stays < 1%, cost returns to baseline within 10min after spike ends.",
        "watch": ["RPS", "autoscaler decisions", "latency", "error rate", "queue depth at every layer", "cost per request"],
        "tools": ["k6", "Locust", "Vegeta", "JMeter"],
        "abort_thresholds": {
            "real_user_error_rate_pct": 1.0,
            "cost_multiplier": 5.0,
            "duration_seconds": 600,
        },
        "blast_radius_default": "Synthetic traffic only (do not replay real user data)",
        "common_bugs": [
            "autoscaler too slow",
            "cold cache amplifies origin load",
            "rate-limiter fires on legitimate spike",
            "downstream services overload before primary autoscales",
        ],
    },
}


def parse_duration(s: str) -> int:
    """Parse a duration like '5m', '300s', '1h' into seconds."""
    if not s:
        return 300
    s = s.strip().lower()
    if s.endswith("ms"):
        return max(1, int(float(s[:-2]) / 1000))
    if s.endswith("s"):
        return int(float(s[:-1]))
    if s.endswith("m"):
        return int(float(s[:-1]) * 60)
    if s.endswith("h"):
        return int(float(s[:-1]) * 3600)
    return int(float(s))


@dataclass
class Experiment:
    name: str
    target: str
    fault_type: str
    fault_description: str
    real_world_analog: str
    inject_value: str
    duration_seconds: int
    maturity_level: str
    hypothesis: str
    steady_state_template: list[str]
    watch_metrics: list[str]
    tools: list[str]
    abort_thresholds: dict[str, object]
    blast_radius: str
    common_bugs: list[str]
    pre_run_checklist: list[str] = field(default_factory=list)
    post_run_actions: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


def build_experiment(args: argparse.Namespace) -> Experiment:
    fault = args.fault.lower()
    if fault not in FAULT_CATALOG:
        raise ValueError(f"Unknown fault type: {fault}. Available: {', '.join(FAULT_CATALOG)}")

    cat = FAULT_CATALOG[fault]
    inject_value = args.inject_value or str(cat["default_inject_value"])
    duration = parse_duration(args.duration)
    hyp = str(cat["hypothesis_template"]).format(target=args.target, inject_value=inject_value)

    name = f"chaos-{args.target}-{fault}-{datetime.now(timezone.utc).strftime('%Y%m%d')}"

    return Experiment(
        name=name,
        target=args.target,
        fault_type=fault,
        fault_description=str(cat["description"]),
        real_world_analog=str(cat["real_world_analog"]),
        inject_value=inject_value,
        duration_seconds=duration,
        maturity_level=args.maturity_level,
        hypothesis=hyp,
        steady_state_template=[
            "Quantify the current baseline before injection. Capture as a screenshot or metric snapshot.",
            "Error rate (parent feature): <value> (e.g., 0.05%)",
            "p95 latency: <value> (e.g., 180ms)",
            "p99 latency: <value> (e.g., 380ms)",
            "Request rate (relevant endpoint): <value> rps",
            "Business KPI (if any): <value>",
            "Capacity headroom: <value> (e.g., CPU 35% avg)",
        ],
        watch_metrics=list(cat["watch"]),
        tools=list(cat["tools"]),
        abort_thresholds=dict(cat["abort_thresholds"]),
        blast_radius=str(cat["blast_radius_default"]),
        common_bugs=list(cat["common_bugs"]),
        pre_run_checklist=[
            "Maturity prerequisite met (L1: staging only; L2: tooling automated; L3: prod approved)",
            "Observer assigned to watch dashboards",
            "Abort mechanism tested in last 7 days",
            "Customer support / oncall informed (for prod runs)",
            "Steady-state metrics captured (screenshot)",
            "Slack thread open for the experiment",
            "Hypothesis written before injection",
            "Duration cap agreed",
        ],
        post_run_actions=[
            "Within 1 hour: scribe writes raw observations",
            "Within 1 day: hypothesis status (confirmed / partial / disproven) recorded",
            "Within 3 days: action items filed with owners and due dates",
            "Within 1 week: experiment artifact added to team's chaos catalog",
            "Schedule re-run after fixes",
        ],
        metadata={
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "designer_version": "1.0",
        },
    )


def render_markdown(exp: Experiment) -> str:
    out: list[str] = []
    out.append(f"# Chaos experiment: `{exp.name}`")
    out.append("")
    out.append(f"_Generated: {exp.metadata['generated_at']}_")
    out.append("")
    out.append("## Overview")
    out.append("")
    out.append(f"- **Target service**: `{exp.target}`")
    out.append(f"- **Fault type**: `{exp.fault_type}`")
    out.append(f"- **Inject value**: {exp.inject_value}")
    out.append(f"- **Duration**: {exp.duration_seconds} seconds ({exp.duration_seconds // 60}m {exp.duration_seconds % 60}s)")
    out.append(f"- **Maturity level**: {exp.maturity_level}")
    out.append(f"- **Description**: {exp.fault_description}")
    out.append(f"- **Real-world analog**: {exp.real_world_analog}")
    out.append("")
    out.append("## Hypothesis (falsifiable)")
    out.append("")
    out.append(f"> {exp.hypothesis}")
    out.append("")
    out.append("Edit this to match your specific SLOs and thresholds before running.")
    out.append("")
    out.append("## Steady state (capture before injection)")
    out.append("")
    for line in exp.steady_state_template:
        out.append(f"- {line}")
    out.append("")
    out.append("## Blast radius")
    out.append("")
    out.append(f"- **Default scope**: {exp.blast_radius}")
    out.append("- **Caps by maturity**:")
    out.append("  - L1 (staging): full target service in staging")
    out.append("  - L2 (staging-auto): full target service in staging, scheduled")
    out.append("  - L3 (prod-canary): 1-5% of users / one canary cell / time-boxed")
    out.append("  - L4 (continuous): bounded by error-budget consumption")
    out.append("")
    out.append("Run `scripts/blast_radius_calculator.py` for quantitative estimates.")
    out.append("")
    out.append("## Watch metrics")
    out.append("")
    for m in exp.watch_metrics:
        out.append(f"- {m}")
    out.append("")
    out.append("## Tools (pick one)")
    out.append("")
    for t in exp.tools:
        out.append(f"- {t}")
    out.append("")
    out.append("## Abort criteria")
    out.append("")
    for k, v in exp.abort_thresholds.items():
        out.append(f"- **{k}**: {v}")
    out.append("- Operator or observer can call abort at any time")
    out.append("")
    out.append("## Pre-run checklist")
    out.append("")
    for c in exp.pre_run_checklist:
        out.append(f"- [ ] {c}")
    out.append("")
    out.append("## Post-run actions")
    out.append("")
    for a in exp.post_run_actions:
        out.append(f"- {a}")
    out.append("")
    out.append("## Common bugs surfaced by this fault")
    out.append("")
    for b in exp.common_bugs:
        out.append(f"- {b}")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Run log (fill in during/after the experiment)")
    out.append("")
    out.append("### Pre-injection baseline (captured at <time>)")
    out.append("- error rate: <>")
    out.append("- p95 latency: <>")
    out.append("- p99 latency: <>")
    out.append("- request rate: <>")
    out.append("")
    out.append("### Injection")
    out.append("- Tool used: <>")
    out.append("- Command: `<>`")
    out.append("- Started: <time>")
    out.append("- Ended: <time>")
    out.append("")
    out.append("### Observations (chronological)")
    out.append("- T+0:00 — <event>")
    out.append("- T+0:30 — <event>")
    out.append("- T+1:00 — <event>")
    out.append("")
    out.append("### Result")
    out.append("- [ ] Hypothesis confirmed")
    out.append("- [ ] Hypothesis partially confirmed")
    out.append("- [ ] Hypothesis disproven")
    out.append("")
    out.append("### Surprises")
    out.append("- ")
    out.append("")
    out.append("### Action items")
    out.append("| ID | Action | Owner | Due | Priority | Ticket |")
    out.append("|----|--------|-------|-----|----------|--------|")
    out.append("| AI-1 |  |  |  | P? |  |")
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Scaffold a chaos experiment document",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--target", help="Target service name (e.g., payment-svc)")
    p.add_argument(
        "--fault",
        choices=sorted(FAULT_CATALOG.keys()),
        help="Fault type to inject. Run --list-faults for catalog.",
    )
    p.add_argument("--inject-value", help="Magnitude (e.g., '200ms' for latency, '1 pod' for pod-kill)")
    p.add_argument("--duration", default="5m", help="Duration (e.g., 5m, 300s, 1h) (default: 5m)")
    p.add_argument(
        "--maturity-level",
        choices=["L1", "L2", "L3", "L4"],
        default="L2",
        help="Target maturity level — informs blast radius caps (default: L2)",
    )
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", help="Output file path")
    p.add_argument("--list-faults", action="store_true", help="List all fault types in catalog")
    args = p.parse_args()
    if not args.list_faults and not (args.target and args.fault):
        p.error("--target and --fault are required (or use --list-faults)")
    return args


def main() -> int:
    args = parse_args()
    if args.list_faults:
        print("Available fault types:\n")
        for k, v in FAULT_CATALOG.items():
            print(f"  {k:<22} {v['description']}")
        return 0
    try:
        exp = build_experiment(args)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.format == "json":
        out = json.dumps(asdict(exp), indent=2, default=str)
    else:
        out = render_markdown(exp)
    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
