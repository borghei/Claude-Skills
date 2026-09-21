# Worked Example: Payments Platform, Sprint 42

A fictional payments team of six engineers has piloted a coding agent on tests and docs for two sprints. The engineering manager wants to "put the agent on everything that fits" for Sprint 42. Three engineers can review: two seniors at 6 hours each and the tech lead at 4 hours. All numbers below are illustrative sample data, not benchmarks.

## Step 1 - First plan: the gate fails

Input: [`../assets/backlog_sample.json`](../assets/backlog_sample.json) - eight tickets, seven planned for the agent.

```bash
python3 scripts/agent_delegation_scorer.py --input assets/backlog_sample.json
# exit 2
```

| Ticket | Score | Band | Why |
|--------|-------|------|-----|
| PAY-101 tests for rounding helpers | 100 | agent-eligible | Clear, isolated, well tested |
| PAY-102 HTTP client patch bump | 95 | agent-eligible | Clear, module-level, well tested |
| PAY-107 API docs for new filters | 93 | agent-eligible | Isolated docs change |
| PAY-108 CSV export on payouts report | 77 | agent-eligible | Medium risk, but 3 criteria, good tests, module scope |
| PAY-103 pagination off-by-one | 66 | agent-assisted | Service-wide blast radius, partial tests |
| PAY-104 refund service refactor (8 pts) | 65 | agent-assisted | Service-wide, partial tests, large |
| PAY-105 webhook secret rotation | 31 | human-only | **Hard block**: touches payments and secrets |
| PAY-106 "Improve checkout" | 25 | human-only | No criteria, no context, no tests |

Gate findings:

- **Policy breach:** PAY-105 is planned for the agent but is hard-blocked.
- **Capacity breach:** agent work needs **30.88** review hours (including a 30% rework allowance); the budget is **12.8** (16 reviewer hours x 0.8). The refactor alone needs almost 9 review hours.
- Warnings: PAY-103 and PAY-104 are agent-assisted, not agent-eligible.

## Step 2 - Re-plan

The manager cuts the plan, not the review:

- PAY-105 goes to the tech lead (hard block).
- PAY-103 and PAY-104 go to engineers, who may use the agent to draft tests.
- PAY-106 goes back to refinement; it is not ready for anyone.

Input: [`../assets/backlog_within_capacity.json`](../assets/backlog_within_capacity.json)

```bash
python3 scripts/agent_delegation_scorer.py --input assets/backlog_within_capacity.json
# exit 0 - 4 agent tickets, 10.4 review hours of a 12.8-hour budget (65% of reviewer hours)
```

Each of the four agent tickets gets a named owner and reviewer from [`../assets/agent_ticket_template.md`](../assets/agent_ticket_template.md), and the agent's PRs go through the same branch protection as everyone else's.

## Step 3 - Month-end metrics

Input: [`../assets/delivery_records_sample.json`](../assets/delivery_records_sample.json) - 30 PRs, 13 deployments, 3 production defects.

```bash
python3 scripts/agent_delivery_metrics.py --input assets/delivery_records_sample.json --gate
# exit 2
```

| Metric | Human | Agent |
|--------|-------|-------|
| PR acceptance rate | 87.5% | 71.4% |
| Review rework rate | 28.6% | 70.0% |
| Post-merge rework rate | 7.1% | 20.0% |
| Median h to first review | 4.0 | 9.0 |
| Median reviewer min / PR | 25 | 40 |
| Escaped defects / 10 merged | 0.71 | 2.0 |

| Deployments | Change fail rate | Deployment rework rate | Median failed deployment recovery (h) |
|-------------|------------------|------------------------|---------------------------------------|
| With agent changes | 33.3% | 16.7% | 2.8 |
| Human only | 14.3% | 14.3% | 0.8 |

## Step 4 - What the team does with it

Read with care: the agent cohort has exactly 10 merged PRs, so the numbers are directional. Even so, the pattern is consistent:

1. **Reviewers do the agent's thinking.** 70% of merged agent PRs needed changes, and agent PRs cost 40 reviewer minutes against 25 for human PRs. The speed gain is being paid for in review time.
2. **Quality escapes.** Post-merge rework and escaped defects are both well above the human cohort, and deployments containing agent changes fail more often. This is the instability the DORA 2025 report warns about.
3. **Actions for Sprint 43:**
   - Narrow the band: bugs require `test_coverage: good` to be agent-eligible.
   - Set `rework_allowance` to 0.7 (the measured review rework rate). That shrinks planned agent work to fit review capacity.
   - Add a Definition of Done item: agent PRs include a failing-then-passing test for every bug fix.
   - Split deployments smaller so the mixed-deployment attribution gets sharper.
   - Re-run the metrics after Sprint 44 before expanding to new ticket types.
