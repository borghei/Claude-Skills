# SLA & Error Budget Management

Read this when calculating SLA compliance, error budgets, and burn rates, or setting deployment-freeze thresholds. Moved verbatim from `SKILL.md`.

## Track SLA and Error Budget

The skill has no SLA tool; compute the budget from your monitoring data as below.

**Error budget calculation example:**
```
SLA: 99.9% availability
Error Budget: 0.1% = 43.8 minutes/month

Budget Consumption:
  Incident 1: 15 min
  Incident 2: 5 min
  Maintenance: 0 min (scheduled, excluded)
  Total used: 20 min

Remaining: 23.8 min (54% remaining)
Burn rate: 0.8x (on track)
```

**Validation checkpoint:** If error budget burn rate exceeds 1.5x, freeze non-critical deployments until burn rate normalizes.
