#!/usr/bin/env python3
"""
gameday_planner.py — Generate a chaos gameday agenda with roles, scenarios, and timing.

Given a target service, duration (half/full day), scenario list, and team size,
emits a complete gameday plan: kickoff, role assignments, per-scenario blocks
with timing, debrief slots, and a synthesis template.

Stdlib only. Markdown or JSON output.

Usage:
    python3 gameday_planner.py --service search-api --duration half --scenarios pod-kill,latency
    python3 gameday_planner.py --service payments --duration full --scenarios dep-error,partition,cache-flush --team-size 6 --env staging
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path


SCENARIO_CATALOG: dict[str, dict[str, str]] = {
    "pod-kill": {
        "name": "Single pod kill",
        "hypothesis": "Killing 1 of N pods causes < 30s of degraded latency (within 2× baseline), error rate stays under 0.5%, replacement is healthy within 60s.",
        "blast_radius": "1 pod of N",
        "abort": "Total error rate > 5% for 60s",
        "tool": "kubectl delete pod / Chaos Mesh PodChaos",
    },
    "rolling-restart": {
        "name": "Rolling restart of all pods",
        "hypothesis": "Rolling restart causes no user-visible errors; p99 latency stays within 1.5× baseline.",
        "blast_radius": "1 pod missing at a time",
        "abort": "Any pod fails health check after 3 minutes",
        "tool": "kubectl rollout restart",
    },
    "latency": {
        "name": "Latency injection between services",
        "hypothesis": "Adding 500ms latency between A and B increases end-to-end p99 by ≤ 600ms. No timeouts fire.",
        "blast_radius": "All traffic between A and B",
        "abort": "Timeout rate > 1% or circuit breaker opens",
        "tool": "Chaos Mesh NetworkChaos delay / tc qdisc",
    },
    "partition": {
        "name": "Network partition (block traffic)",
        "hypothesis": "When traffic is blocked, service uses cache for ≤ TTL, then fails fast with clear error. Health check reflects degradation.",
        "blast_radius": "All traffic to specified peer",
        "abort": "Open FD count grows unboundedly; unrelated services error",
        "tool": "Chaos Mesh NetworkChaos partition / iptables",
    },
    "dep-error": {
        "name": "Downstream returns errors (503)",
        "hypothesis": "Downstream returns 503 for 5 min; fallback engages; user-facing error rate stays < 0.5%; alert fires within 2 min.",
        "blast_radius": "Only calls to mocked downstream",
        "abort": "User-visible error rate > 1%; retry storm > 100× normal",
        "tool": "Toxiproxy / Mountebank / custom proxy",
    },
    "dep-timeout": {
        "name": "Downstream returns slowly",
        "hypothesis": "Downstream latency increases 10×; circuit breaker trips; fallback engages; thread pool doesn't saturate.",
        "blast_radius": "All calls to mocked downstream",
        "abort": "Thread pool > 90% saturated; fallback fails to engage",
        "tool": "Toxiproxy latency toxic / Mountebank",
    },
    "cpu-stress": {
        "name": "CPU saturation",
        "hypothesis": "CPU at 100% causes latency increase but no errors; cgroup throttles correctly; other co-located processes unaffected.",
        "blast_radius": "1 instance",
        "abort": "Error rate > 5%; GC pause > 5s",
        "tool": "Chaos Mesh StressChaos / stress-ng",
    },
    "memory-pressure": {
        "name": "Memory pressure",
        "hypothesis": "Memory at 90% used; app continues with slight latency increase; OOM-killer doesn't fire on cgroup-limited processes.",
        "blast_radius": "1 instance",
        "abort": "Any OOM kill; error rate > 2%",
        "tool": "Chaos Mesh StressChaos / stress-ng",
    },
    "disk-fill": {
        "name": "Disk fill",
        "hypothesis": "Disk at 95%; alert fires; app rejects writes with 4xx; no data corruption; recovery is automatic when space freed.",
        "blast_radius": "1 instance disk volume",
        "abort": "Process crash; any data corruption detected",
        "tool": "dd if=/dev/zero / Chaos Mesh IOChaos",
    },
    "cache-flush": {
        "name": "Cache flush",
        "hypothesis": "Cache flushed; origin RPS spikes 10×; autoscaler engages in 90s; p99 stays under SLO; no errors.",
        "blast_radius": "All cached endpoints",
        "abort": "Origin error rate > 1%; instance count > 3× normal",
        "tool": "Redis FLUSHDB / CDN purge API / varnishadm",
    },
    "traffic-spike": {
        "name": "5× traffic spike",
        "hypothesis": "5× synthetic traffic for 5 min; autoscaler engages in 90s; latency stays under SLO; error rate < 1%; cost returns to baseline in 10 min.",
        "blast_radius": "Synthetic traffic (no real users)",
        "abort": "Real-user error rate > 1%; cost > 5× normal",
        "tool": "k6 / Locust / Vegeta",
    },
    "az-degraded": {
        "name": "Single AZ degraded",
        "hypothesis": "One AZ unreachable; traffic shifts to remaining AZs in 60s; latency increases by ≤ 50ms; error rate < 0.2%.",
        "blast_radius": "1/N capacity",
        "abort": "Error rate > 1%; cross-AZ runaway cost",
        "tool": "AZ-level network block / Chaos Mesh",
    },
}


def parse_scenario_list(s: str) -> list[str]:
    items = [item.strip() for item in s.split(",")]
    invalid = [i for i in items if i and i not in SCENARIO_CATALOG]
    if invalid:
        raise ValueError(f"Unknown scenarios: {', '.join(invalid)}. Available: {', '.join(SCENARIO_CATALOG)}")
    return [i for i in items if i]


@dataclass
class GamedayBlock:
    start_offset_min: int
    duration_min: int
    name: str
    activity: str


@dataclass
class GamedayPlan:
    service: str
    environment: str
    duration_label: str
    total_minutes: int
    scenario_count: int
    team_size: int
    roles: dict[str, str]
    scenarios: list[dict[str, str]]
    schedule: list[GamedayBlock]
    pre_gameday_checklist: list[str]
    debrief_template: list[str]
    metadata: dict[str, str] = field(default_factory=dict)


def assign_roles(team_size: int) -> dict[str, str]:
    """Suggest role assignments based on team size."""
    base = {
        "lead": "<senior eng — calm under stress, system knowledge>",
        "scribe": "<detail-oriented; fast writer>",
        "operator": "<familiar with chaos tool; cool under pressure>",
        "observer-systems": "<watches infra dashboards>",
        "observer-business": "<watches KPIs, customer-facing metrics>",
        "oncall": "<real oncall rotation — not participating in chaos>",
        "external-rep": "<CS/PM — represents user impact>",
    }
    if team_size <= 3:
        # Combine roles
        return {
            "lead-and-scribe": base["lead"] + " (also scribing)",
            "operator-and-observer": base["operator"] + " (also observing systems)",
            "oncall": base["oncall"],
        }
    if team_size <= 5:
        return {
            "lead": base["lead"],
            "scribe": base["scribe"],
            "operator": base["operator"],
            "observer": base["observer-systems"] + " + business KPIs",
            "oncall": base["oncall"],
        }
    # 6+
    return base


def build_schedule(scenarios: list[str], duration_minutes: int) -> list[GamedayBlock]:
    blocks: list[GamedayBlock] = []
    t = 0
    # Kickoff
    blocks.append(GamedayBlock(t, 15, "kickoff", "Intro, roles, ground rules, abort plan"))
    t += 15
    # Steady state
    blocks.append(GamedayBlock(t, 15, "steady-state-capture", "Capture baseline metrics with screenshots"))
    t += 15
    # Scenarios
    remaining_min = duration_minutes - 15 - 15 - 30  # subtract synth & closing
    per_scenario_min = max(45, remaining_min // max(1, len(scenarios)))
    for i, sc in enumerate(scenarios, 1):
        cat = SCENARIO_CATALOG[sc]
        inject_min = 15
        observe_min = max(15, per_scenario_min - inject_min - 15 - 15)
        recover_min = 15
        debrief_min = 15
        blocks.append(GamedayBlock(t, inject_min, f"scenario-{i}-inject", f"Inject: {cat['name']}"))
        t += inject_min
        blocks.append(GamedayBlock(t, observe_min, f"scenario-{i}-observe", "Watch dashboards; scribe records observations"))
        t += observe_min
        blocks.append(GamedayBlock(t, recover_min, f"scenario-{i}-recover", "Stop injection; observe recovery to steady state"))
        t += recover_min
        blocks.append(GamedayBlock(t, debrief_min, f"scenario-{i}-debrief", f"Quick debrief; record findings on {cat['name']}"))
        t += debrief_min
    # Synthesis + close
    blocks.append(GamedayBlock(t, 20, "synthesis", "Cross-scenario patterns; biggest surprises; action items"))
    t += 20
    blocks.append(GamedayBlock(t, 10, "close", "Assign owners + due dates; schedule writeup; thank participants"))
    return blocks


def build_plan(args: argparse.Namespace) -> GamedayPlan:
    scenarios = parse_scenario_list(args.scenarios)
    duration_minutes = 240 if args.duration == "half" else 480
    sched = build_schedule(scenarios, duration_minutes)

    return GamedayPlan(
        service=args.service,
        environment=args.env,
        duration_label=args.duration,
        total_minutes=sched[-1].start_offset_min + sched[-1].duration_min,
        scenario_count=len(scenarios),
        team_size=args.team_size,
        roles=assign_roles(args.team_size),
        scenarios=[{"id": s, **SCENARIO_CATALOG[s]} for s in scenarios],
        schedule=sched,
        pre_gameday_checklist=[
            "T-7 days: pick scenarios, draft hypotheses, share with team",
            "T-3 days: confirm dates, assign roles, rehearse in staging",
            "T-1 day: review runbooks for affected services; confirm tools",
            "T-1 day: inform customer support / oncall of the window",
            "T-1 day: confirm dashboards / Slack channel / abort mechanism",
            "T+0: 30 min before — final check, abort mechanism rehearsal",
        ],
        debrief_template=[
            "What were the biggest surprises?",
            "What didn't we measure that we wish we had?",
            "What hypothesis did we disprove?",
            "What's the most important action item?",
            "What should we re-run next quarter?",
            "What's our maturity level after this exercise?",
        ],
        metadata={"generated_at": datetime.now(timezone.utc).isoformat()},
    )


def render_markdown(plan: GamedayPlan) -> str:
    out = []
    out.append(f"# Gameday plan: {plan.service}")
    out.append("")
    out.append(f"_Generated: {plan.metadata['generated_at']}_")
    out.append("")
    out.append("## Overview")
    out.append("")
    out.append(f"- **Service**: `{plan.service}`")
    out.append(f"- **Environment**: {plan.environment}")
    out.append(f"- **Duration**: {plan.duration_label} day ({plan.total_minutes} min)")
    out.append(f"- **Scenarios**: {plan.scenario_count}")
    out.append(f"- **Team size**: {plan.team_size}")
    out.append("")
    out.append("## Roles")
    out.append("")
    out.append("| Role | Suggested |")
    out.append("|------|-----------|")
    for role, suggest in plan.roles.items():
        out.append(f"| {role} | {suggest} |")
    out.append("")
    out.append("## Scenarios")
    out.append("")
    for i, s in enumerate(plan.scenarios, 1):
        out.append(f"### Scenario {i}: {s['name']}")
        out.append("")
        out.append(f"- **ID**: `{s['id']}`")
        out.append(f"- **Hypothesis**: {s['hypothesis']}")
        out.append(f"- **Blast radius**: {s['blast_radius']}")
        out.append(f"- **Abort**: {s['abort']}")
        out.append(f"- **Tool**: {s['tool']}")
        out.append("")
    out.append("## Schedule")
    out.append("")
    out.append("| T+ | Duration | Block | Activity |")
    out.append("|----|----------|-------|----------|")
    for b in plan.schedule:
        h = b.start_offset_min // 60
        m = b.start_offset_min % 60
        t = f"{h}h{m:02d}m"
        out.append(f"| {t} | {b.duration_min} min | {b.name} | {b.activity} |")
    out.append("")
    out.append("## Pre-gameday checklist")
    out.append("")
    for c in plan.pre_gameday_checklist:
        out.append(f"- [ ] {c}")
    out.append("")
    out.append("## Ground rules (read at kickoff)")
    out.append("")
    out.append("1. Safety first: if anything outside experiment scope alerts, pause.")
    out.append("2. Oncall handles real incidents; chaos pauses for them.")
    out.append("3. Anyone can call abort at any time. No questions asked.")
    out.append("4. We're here to learn, not to win. Surprises = success.")
    out.append("5. Scribe captures everything; trust the process.")
    out.append("6. Findings are blameless: we name systems, not people.")
    out.append("7. We finish on time. No mid-day scenario additions.")
    out.append("")
    out.append("## Per-scenario scribe template")
    out.append("")
    out.append("```markdown")
    out.append("## Scenario X: <name>")
    out.append("")
    out.append("### Hypothesis")
    out.append("<copy from scenario>")
    out.append("")
    out.append("### Pre-injection baseline (captured at <time>)")
    out.append("- error rate: <>")
    out.append("- p95 latency: <>")
    out.append("- p99 latency: <>")
    out.append("- request rate: <>")
    out.append("")
    out.append("### Injection")
    out.append("- Tool: <>")
    out.append("- Started: <>")
    out.append("- Ended: <>")
    out.append("")
    out.append("### Observations (chronological)")
    out.append("- T+0:00 — <event>")
    out.append("- T+0:30 — <event>")
    out.append("")
    out.append("### Result")
    out.append("- [ ] Hypothesis confirmed")
    out.append("- [ ] Partially confirmed")
    out.append("- [ ] Disproven")
    out.append("")
    out.append("### Surprises")
    out.append("- ")
    out.append("")
    out.append("### Action items")
    out.append("| ID | Action | Owner | Due | Priority |")
    out.append("|----|--------|-------|-----|----------|")
    out.append("| AI-1 |  |  |  | P? |")
    out.append("```")
    out.append("")
    out.append("## Debrief questions")
    out.append("")
    for q in plan.debrief_template:
        out.append(f"- {q}")
    out.append("")
    out.append("## Post-gameday")
    out.append("")
    out.append("- Within 5 business days: scribe publishes full writeup")
    out.append("- Action items tracked in normal backlog with owners + due dates")
    out.append("- Schedule follow-up gameday in 3 months to re-run failed scenarios")
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate a chaos gameday agenda",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--service", help="Target service name (required unless --list-scenarios)")
    p.add_argument(
        "--duration",
        choices=["half", "full"],
        default="half",
        help="half = 4h, full = 8h (default: half)",
    )
    p.add_argument(
        "--scenarios",
        help="Comma-separated scenario IDs (run --list-scenarios for catalog)",
    )
    p.add_argument(
        "--env",
        choices=["staging", "production-canary", "production"],
        default="staging",
        help="Target environment (default: staging)",
    )
    p.add_argument("--team-size", type=int, default=5, help="Team size — affects role assignments (default: 5)")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", help="Output file path")
    p.add_argument("--list-scenarios", action="store_true", help="List all scenarios in catalog")
    args = p.parse_args()
    if not args.list_scenarios and not (args.service and args.scenarios):
        p.error("--service and --scenarios are required (or use --list-scenarios)")
    return args


def main() -> int:
    args = parse_args()
    if args.list_scenarios:
        print("Available scenarios:\n")
        for k, v in SCENARIO_CATALOG.items():
            print(f"  {k:<20} {v['name']}")
        return 0
    try:
        plan = build_plan(args)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.format == "json":
        out = json.dumps(asdict(plan), indent=2, default=str)
    else:
        out = render_markdown(plan)
    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
