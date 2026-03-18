# Velocity Benchmarks & Interpretation Guide

Industry benchmarks, healthy patterns, and guidance for interpreting sprint velocity metrics.

## Benchmarks by Team Size

These benchmarks represent median ranges from industry surveys (DORA, State of DevOps, Accelerate). They are guidelines, not targets — every team's context is different.

### Small Team (2-4 engineers)

| Metric | Healthy Range | Warning |
|--------|---------------|---------|
| Commits/day (team) | 4-12 | <2 or >20 (noise) |
| PRs merged/week | 5-15 | <3 (bottleneck) |
| Avg PR size (LOC) | 50-200 | >500 (too large) |
| Cycle time (commit→merge) | 2-8 hours | >24 hours |
| Deploy frequency | 1-5/week | <1/week |
| Deep work session ratio | 35-50% | <20% |

### Medium Team (5-9 engineers)

| Metric | Healthy Range | Warning |
|--------|---------------|---------|
| Commits/day (team) | 8-25 | <5 or >40 |
| PRs merged/week | 10-30 | <5 |
| Avg PR size (LOC) | 50-250 | >400 |
| Cycle time (commit→merge) | 4-16 hours | >48 hours |
| Deploy frequency | 2-10/week | <1/week |
| Review turnaround | 1-4 hours | >8 hours |

### Large Team (10+ engineers)

| Metric | Healthy Range | Warning |
|--------|---------------|---------|
| Commits/day (team) | 15-50 | <10 |
| PRs merged/week | 20-60 | <10 |
| Avg PR size (LOC) | 50-200 | >300 (review burden) |
| Cycle time (commit→merge) | 4-24 hours | >72 hours |
| Deploy frequency | 5-25/week | <2/week |
| Knowledge distribution (bus factor) | >2 per area | 1 (critical risk) |

## Healthy vs Unhealthy Velocity Patterns

### Healthy Patterns

1. **Steady throughput with gradual improvement** — Velocity stays within a 20% band sprint-to-sprint, trending slightly upward over quarters.

2. **Balanced commit types** — Mix of feat (30-50%), fix (15-25%), refactor (10-20%), test (5-15%), docs (5-10%). Indicates sustainable development.

3. **Declining cycle time** — PRs merge faster over time. Signals improving review culture and smaller PR sizes.

4. **High deep work ratio** — 35-50% of sessions are deep work (>50 min). Indicates focused, uninterrupted development time.

5. **Consistent PR sizes** — Average PR size stays below 300 LOC with low variance. Small PRs review faster and ship safer.

### Unhealthy Patterns

1. **Velocity spikes** — Sudden 50%+ increases followed by crashes. Usually means crunch followed by recovery or technical debt payment.

2. **Zero refactor commits** — No `refactor:` type commits for 3+ sprints. Technical debt is accumulating silently.

3. **Monotonically increasing velocity** — Teams rarely get faster forever. If velocity only goes up, the definition of "done" may be weakening.

4. **90%+ feature commits** — No time allocated for fixes, refactoring, or documentation. Unsustainable pace.

5. **Growing cycle time** — PRs taking longer to merge each sprint. Signals review bottleneck, unclear ownership, or too-large PRs.

6. **Single-contributor dominance** — One person responsible for 60%+ of commits. Bus factor = 1.

7. **All micro-sessions** — >70% of sessions are under 20 minutes. Indicates excessive context switching, meetings, or interruptions.

## Sprint Predictability

### Measuring Predictability

**Coefficient of Variation (CV):** Standard deviation of velocity divided by mean velocity across sprints.

| CV Range | Predictability | Interpretation |
|----------|---------------|----------------|
| <15% | High | Reliable sprint planning possible |
| 15-25% | Moderate | Plan with buffer, forecasts useful |
| 25-40% | Low | Significant variability, wide confidence intervals |
| >40% | Very low | Planning is guesswork; investigate root causes |

### Improving Predictability

- Break work into smaller stories (reduces per-item variance)
- Consistent sprint length (no variable-length sprints)
- Protect the sprint from scope injection
- Account for PTO, holidays, on-call rotations in capacity
- Track and reduce carryover items

## Burndown / Burnup Interpretation

### Burndown Warning Signs

- **Flat line for 3+ days:** Blocked work or underestimated stories
- **Upward slope mid-sprint:** Scope creep or discovered work
- **Cliff at sprint end:** Batch completion — stories not truly incremental
- **Staircase pattern:** Large stories completing all at once instead of daily progress

### Burnup Advantages

Burnup charts show both scope and completion, making scope changes visible. Preferred for:
- Sprints where requirements evolve
- Stakeholder communication (shows added scope explicitly)
- Long-running releases spanning multiple sprints

## When Velocity Metrics Mislead

### Velocity Is NOT a Performance Metric

Velocity measures team throughput for planning purposes. Using it to evaluate individual or team performance creates perverse incentives:
- Inflated story points (Goodhart's Law)
- Avoiding refactoring and testing (reduces "velocity")
- Splitting work into trivial commits to inflate counts

### Contexts Where Raw Velocity Misleads

1. **New team or new domain** — Velocity will be low while the team learns. This is expected.
2. **Major refactoring sprint** — Velocity may drop while improving long-term health. Track refactor commits separately.
3. **Onboarding sprint** — New team members reduce short-term velocity while increasing long-term capacity.
4. **Infrastructure/tooling sprint** — Investment sprints have lower feature velocity but enable future acceleration.
5. **Post-incident sprint** — Incident response and prevention work may not show up in standard metrics.

### Better Combined Metrics

Instead of velocity alone, consider:

| Combined Metric | What It Shows |
|----------------|---------------|
| Velocity + Defect Rate | Are we shipping fast AND reliably? |
| Throughput + Cycle Time | Are we delivering more items faster? |
| Commit Count + Test Ratio | Are we building features with quality? |
| LOC + Churn Rate | Are we adding stable code? |
| Deploy Frequency + MTTR | How fast do we ship and recover? |

---

**Last Updated:** 2026-03-18
