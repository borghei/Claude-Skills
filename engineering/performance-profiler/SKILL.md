---
name: performance-profiler
description: >
  Performance profiling for Node.js, Python, and Go: CPU flamegraphs, memory leak detection,
  bundle analysis, query optimization, and k6 load testing. Use when diagnosing slow
  endpoints, memory growth, large bundles, or traffic spikes.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: performance-engineering
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: clinic, py-spy, pprof, k6, webpack-bundle-analyzer
  tags:
    - performance
    - profiling
    - flamegraphs
    - memory-leaks
    - load-testing
---
# Performance Profiler

Systematic performance profiling for Node.js, Python, and Go applications. Identifies CPU bottlenecks with flamegraphs, detects memory leaks with heap snapshots, analyzes bundle sizes, optimizes database queries, detects N+1 patterns, and runs load tests with k6 and Artillery. Enforces a measure-first methodology: establish baseline, identify bottleneck, fix, and verify improvement.

**Golden Rule — Measure First:** Profile → Confirm bottleneck → Fix → Measure again → Verify improvement. Every optimization needs baseline metrics, profiler evidence, the fix, post-fix metrics, and a delta. Full rule in `references/cpu-and-memory-profiling.md`.

## Core Capabilities

- **CPU profiling** — Clinic.js/V8 flamegraphs (Node), py-spy/cProfile/scalene (Python), pprof (Go), Chrome DevTools (browser).
- **Memory profiling** — heap snapshots and before/after comparison, GC pressure analysis, leak detection, retained object graphs.
- **Database optimization** — EXPLAIN ANALYZE plan reading, N+1 detection and batching, slow query logs, missing-index identification, connection pool sizing.
- **Bundle analysis** — webpack/Next.js analyzers, tree-shaking, dynamic imports, heavy dependency identification.
- **Load testing** — k6 ramp-up scripts, SLA threshold enforcement in CI, P50/P95/P99 latency tracking, concurrent user simulation.

## When to Use

- App is slow and you do not know where the bottleneck is.
- P99 latency exceeds SLA before a release.
- Memory usage grows over time (suspected leak).
- Bundle size increased after adding dependencies.
- Preparing for a traffic spike (load test before launch).
- Database queries taking >100ms, or verifying no regressions after a dependency upgrade.

## Clarify First

Before profiling, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Runtime & symptom:** Node / Python / Go and CPU / memory / bundle / query / load-spike (selects the profiler and toolchain).
- **Baseline + SLA target:** current numbers and the P95/P99 (or size) threshold to beat (measure-first needs both to verify a delta).
- **Environment:** local / staging / prod determines the safe profiling method and whether load testing is allowed.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

| Tool | Input (JSON) | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `scripts/benchmark_reporter.py` | `{"baseline": [...], "current": [...]}`, each entry `name`, `iterations`, `mean_ms`, `median_ms`, `min_ms`, `max_ms`, `p95_ms` | `--regression-threshold 5`, `--improvement-threshold 5`, `--fail-on-regression`, `--json` | 0 report; 1 regression with `--fail-on-regression`; 2 unreadable input |
| `scripts/bottleneck_detector.py` | Array or JSONL of requests: `endpoint`, `duration_ms`, optional `queries` (`template`, `duration_ms`) and `spans` (`name`, `type`, `duration_ms`) | `--latency-threshold`, `--cv-threshold`, `--json` | 0 report; 2 unreadable input |
| `scripts/resource_analyzer.py` | Array of snapshots: `timestamp` plus `cpu`, `memory`, `disk` (number or `{"percent": n}`) | `--cpu-threshold`, `--memory-threshold`, `--disk-threshold`, `--json` | 0 report; 2 unreadable input |

```bash
# from engineering/performance-profiler/
python3 scripts/benchmark_reporter.py assets/sample_benchmarks.json --fail-on-regression   # exit 1: parse_invoice +50%
python3 scripts/bottleneck_detector.py assets/sample_request_log.json                     # slow GET /orders, N+1 confirmed
python3 scripts/resource_analyzer.py assets/sample_resources.json                         # memory climbing all day
```

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/cpu-and-memory-profiling.md](references/cpu-and-memory-profiling.md)** — the full Measure-First rule, Node.js CPU profiling (Clinic.js flamegraphs, V8 CPU profiles), and memory leak detection (Node heap snapshots, Python memray/tracemalloc). Read when chasing CPU or memory issues.
- **[references/database-and-bundle.md](references/database-and-bundle.md)** — EXPLAIN ANALYZE workflow, N+1 detection patterns and middleware script, Next.js bundle analyzer setup, quick size checks, and the common-bundle-wins table. Read when optimizing queries or bundle size.
- **[references/load-testing-and-methodology.md](references/load-testing-and-methodology.md)** — full k6 load-test script, the before/after measurement template, quick-win optimization checklist, common pitfalls, best practices, troubleshooting table, and success criteria. Read when load testing or documenting a win.

## Anti-Patterns

**Mistake:** Optimizing before measuring.
**Why it matters:** Intuition picks the wrong hotspot most of the time, and the change adds risk without moving the number users feel.
**Instead:** Profile or trace first, fix the top finding, and re-measure against the same baseline.

**Mistake:** Comparing benchmarks run on different machines or loads.
**Why it matters:** Noise from hardware and contention looks like regressions or wins.
**Instead:** Run baseline and current on the same environment, with enough iterations, and gate CI with `--fail-on-regression` only on stable runners.

**Mistake:** Treating averages as the user experience.
**Why it matters:** A good mean hides a slow tail, and the tail is what times out.
**Instead:** Track p95 and p99 per endpoint, and look at variance as well as the median.

## Files

| File | Purpose |
|------|---------|
| `scripts/benchmark_reporter.py`, `scripts/bottleneck_detector.py`, `scripts/resource_analyzer.py` | Stdlib CLIs |
| `assets/sample_benchmarks.json` | Two benchmarks: one regression (+50%), one improvement |
| `assets/sample_request_log.json` | 30 requests with an N+1 pattern and a slow external call |
| `assets/sample_resources.json` | 48 half-hourly snapshots with steadily rising memory |

## Scope & Limitations

**This skill covers:**
- CPU and memory profiling for Node.js, Python, and Go applications using flamegraphs and heap snapshots
- Database query optimization including EXPLAIN ANALYZE interpretation, N+1 detection, and index recommendations
- Frontend bundle analysis and size reduction strategies for webpack and Next.js projects
- Load testing methodology with k6 including ramp-up patterns, threshold enforcement, and CI integration

**This skill does NOT cover:**
- Application Performance Monitoring (APM) platform setup and configuration (Datadog, New Relic, Grafana) — see `engineering/observability-designer`
- Infrastructure-level performance tuning (kernel parameters, network stack, container resource limits) — see `engineering/senior-devops`
- Security-focused performance concerns such as DDoS mitigation or rate limiting — see `engineering/senior-security`
- Mobile application profiling (iOS Instruments, Android Profiler) — see `engineering/senior-mobile`
