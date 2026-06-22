---
name: performance-profiler
description: >
  Performance profiling for Node.js, Python, and Go: CPU flamegraphs, memory leak detection,
  bundle analysis, query optimization, and k6 load testing. Use when diagnosing slow
  endpoints, memory growth, large bundles, or traffic spikes.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: performance-engineering
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: clinic, py-spy, pprof, k6, webpack-bundle-analyzer
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

Before profiling, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Runtime & symptom** — Node / Python / Go and CPU / memory / bundle / query / load-spike (selects the profiler and toolchain)
- [ ] **Baseline + SLA target** — current numbers and the P95/P99 (or size) threshold to beat (measure-first needs both to verify a delta)
- [ ] **Environment** — local / staging / prod determines the safe profiling method and whether load testing is allowed

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `benchmark_reporter.py` | Parse benchmark results and report regressions/improvements vs thresholds | `python scripts/benchmark_reporter.py results.json --fail-on-regression` |
| `bottleneck_detector.py` | Analyze logs/traces to flag slow latency, queries, and spans | `python scripts/bottleneck_detector.py trace.json --latency-threshold 200` |
| `resource_analyzer.py` | Analyze CPU/memory/disk usage data and flag anomalies and trends | `python scripts/resource_analyzer.py metrics.json --cpu-threshold 80` |

All three accept a file path or `-` for stdin and support `--json`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/cpu-and-memory-profiling.md](references/cpu-and-memory-profiling.md)** — the full Measure-First rule, Node.js CPU profiling (Clinic.js flamegraphs, V8 CPU profiles), and memory leak detection (Node heap snapshots, Python memray/tracemalloc). Read when chasing CPU or memory issues.
- **[references/database-and-bundle.md](references/database-and-bundle.md)** — EXPLAIN ANALYZE workflow, N+1 detection patterns and middleware script, Next.js bundle analyzer setup, quick size checks, and the common-bundle-wins table. Read when optimizing queries or bundle size.
- **[references/load-testing-and-methodology.md](references/load-testing-and-methodology.md)** — full k6 load-test script, the before/after measurement template, quick-win optimization checklist, common pitfalls, best practices, troubleshooting table, and success criteria. Read when load testing or documenting a win.

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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/observability-designer` | Performance profiling findings feed into observability dashboard design; alerting thresholds derived from profiling baselines | Profiler baselines and SLA thresholds → Prometheus/Grafana alert rules and dashboard panels |
| `engineering/ci-cd-pipeline-builder` | k6 load tests and bundle size checks integrate as CI pipeline gates | k6 threshold configs and bundle budget scripts → CI pipeline stage definitions |
| `engineering/database-designer` | Query optimization recommendations inform schema design decisions; index suggestions feed back to schema migrations | EXPLAIN ANALYZE findings and index recommendations → schema migration files and index definitions |
| `engineering/senior-backend` | Backend architecture decisions incorporate profiling data; connection pool sizing and caching strategies validated by load tests | Profiling reports and load test results → architecture decision records and implementation guidance |
| `engineering/tech-debt-tracker` | Performance regressions and unresolved bottlenecks are tracked as technical debt items with measured impact | Before/after measurement reports and unresolved findings → tech debt backlog with quantified cost |
| `engineering/senior-frontend` | Bundle analysis results drive frontend optimization work; code-splitting and lazy-loading decisions backed by profiler data | Bundle analyzer output and Lighthouse scores → frontend optimization tasks and component refactoring plans |
