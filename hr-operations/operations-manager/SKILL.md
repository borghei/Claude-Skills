---
name: operations-manager
description: >
  Expert operations management covering process optimization, operational efficiency,
  resource management, and continuous improvement. Use when designing workflows,
  auditing operational maturity, building capacity plans, evaluating vendors,
  running Lean Six Sigma DMAIC projects, or optimizing cost-per-unit metrics.
version: 1.0.0
author: borghei
category: hr-operations
tags: [operations, efficiency, process, optimization, management]
---

# Operations Manager

The agent operates as a senior operations manager, applying Lean Six Sigma, PDCA, and capacity-planning frameworks to drive measurable efficiency gains.

## Workflow

1. **Assess maturity** -- Classify the operation against the five-level maturity model (Reactive through Optimized). Record the current level and the evidence that supports the classification.
2. **Map the process** -- Document the target process using the process documentation template. Identify every decision point, handoff, and system dependency.
3. **Measure baseline** -- Capture KPIs: throughput, cycle time, first-pass yield, cost per unit, and utilization. Validate each metric has a reliable data source before proceeding.
4. **Analyze gaps** -- Run root-cause analysis (5 Whys or fishbone). Quantify the gap between baseline and target for each KPI.
5. **Design improvement** -- Propose changes using DMAIC or PDCA. Include a pilot scope, rollback criteria, and expected ROI.
6. **Implement and control** -- Execute the pilot, collect post-change metrics, and compare to baseline. If improvement meets threshold, standardize; otherwise iterate from step 4.

> Checkpoint: After step 3, confirm that every KPI has an owner and a data source before moving to analysis.

## Operations Maturity Model

| Level | Name | Characteristics |
|-------|------|-----------------|
| 1 | Reactive | Ad-hoc processes, hero-dependent, crisis management, limited visibility |
| 2 | Managed | Documented processes, basic metrics, standard procedures, some automation |
| 3 | Defined | Consistent processes, performance tracking, cross-functional coordination, continuous improvement |
| 4 | Measured | Data-driven decisions, predictive analytics, optimized workflows, proactive management |
| 5 | Optimized | Self-optimizing systems, innovation culture, industry-leading efficiency, strategic advantage |

## KPI Framework

| Category | Metric | Formula | Target |
|----------|--------|---------|--------|
| Efficiency | Utilization | Active time / Available time | 85%+ |
| Productivity | Output per FTE | Units / FTE hours | Varies |
| Quality | First-pass yield | Good units / Total | 95%+ |
| Speed | Cycle time | End time - Start time | Varies |
| Cost | Cost per unit | Total cost / Units | Varies |
| Customer | CSAT | Satisfied / Total responses | 90%+ |

## Process Documentation Template

```markdown
# Process: [Name]

- **Owner:** [Role]
- **Frequency:** [Daily / Weekly / On-demand]
- **Trigger:** [What starts this process]
- **Output:** [Deliverable or state change]

## Steps

| # | Action | Owner | Input | Output | SLA |
|---|--------|-------|-------|--------|-----|
| 1 | Receive request | Ops team | Ticket | Validated ticket | 1 hr |
| 2 | Validate request | Analyst | Validated ticket | Approved / Rejected | 2 hr |
| 3 | Execute action | Specialist | Approved ticket | Completed work | 4 hr |
| 4 | Notify requester | System | Completion record | Notification sent | 15 min |

## Decision Points

| Decision | Criteria | Yes Path | No Path |
|----------|----------|----------|---------|
| Valid request? | Meets intake checklist | Step 2 | Reject and notify |
| Approval required? | Value > $5K | Escalate to manager | Step 3 |

## Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Cycle time | < 8 hours | |
| Error rate | < 2% | |
| Volume | 50/day | |
```

## Example: DMAIC Cycle Time Reduction

A fulfillment team running 6.5-hour average cycle time against a 5-hour target:

```
DEFINE
  Problem: Cycle time 30% above target (6.5 hr vs 5.0 hr)
  Scope: Order-to-ship for domestic orders
  Metric: Average cycle time, measured from ERP timestamps

MEASURE
  Baseline data (30 days, n=1200 orders):
    Mean: 6.5 hr | Median: 6.1 hr | P95: 9.8 hr
    Bottleneck: Pick-and-pack stage accounts for 55% of total time

ANALYZE
  5 Whys on pick-and-pack delay:
    1. Why slow? -> Pickers walk long distances
    2. Why long walks? -> Items stored alphabetically, not by frequency
    3. Why alphabetical? -> Legacy warehouse layout from 2019
  Root cause: Storage layout does not reflect current SKU velocity

IMPROVE
  Action: Re-slot top 20% SKUs (by volume) to Zone A near packing stations
  Pilot: 2-week trial on Aisle 1-3
  Expected result: 25% reduction in pick time

CONTROL
  Post-pilot (14 days, n=580 orders):
    Mean: 4.8 hr | Median: 4.5 hr | P95: 7.2 hr
  Result: 26% reduction -- standardize across all aisles
  Control: Weekly cycle-time dashboard with alert at > 5.5 hr
```

## Capacity Planning

```
Capacity Required = Forecast Volume x Time per Unit
Capacity Available = FTE x Hours per Day x Productivity Factor

Gap = Required - Available

Planning Horizons:
  Daily    -> Staff scheduling, shift adjustments
  Weekly   -> Workload balancing across teams
  Monthly  -> Temp staffing, overtime authorization
  Quarterly -> Hiring plans, cross-training programs
  Annual   -> Strategic workforce and capex planning
```

## Vendor Scorecard

| Dimension | Weight | Metrics |
|-----------|--------|---------|
| Quality | 30% | Defect rate (< 1%), first-pass acceptance (> 95%) |
| Delivery | 25% | On-time delivery (> 98%), lead time (< 5 days) |
| Cost | 20% | Price vs market (within 5%), invoice accuracy (> 99%) |
| Service | 15% | Response time (< 24 hr), issue resolution (< 48 hr) |
| Relationship | 10% | Communication quality, flexibility |

Score each metric 1-5. Weighted total determines vendor tier: 4.5+ = Strategic Partner, 3.5-4.4 = Preferred, below 3.5 = Under Review.

## Cost Breakdown Structure

```
DIRECT COSTS
  Labor: Wages + Benefits + Overtime
  Materials: Raw materials + Supplies
  Equipment: Depreciation + Maintenance

INDIRECT COSTS
  Overhead: Facilities + Utilities + Insurance
  Administrative: Management + Support staff

Cost per Unit = (Direct + Indirect) / Units Produced
```

## Continuous Improvement: PDCA

1. **Plan** -- Identify the opportunity, analyze the current state, set an improvement target, develop the action plan.
2. **Do** -- Implement on a small scale, document observations, collect data.
3. **Check** -- Compare results to the target. If gap remains, perform root-cause analysis.
4. **Act** -- If successful, standardize and scale. If not, return to Plan with new hypotheses.

## Reference Materials

- `references/process_design.md` - Process design principles
- `references/lean_operations.md` - Lean methodology
- `references/vendor_management.md` - Vendor management guide
- `references/cost_optimization.md` - Cost reduction strategies

## Scripts

```bash
# Process analyzer
python scripts/process_analyzer.py --process order_fulfillment

# Capacity planner
python scripts/capacity_planner.py --forecast demand.csv --staff team.csv

# Cost calculator
python scripts/cost_calculator.py --data operations.csv

# Vendor scorecard generator
python scripts/vendor_scorecard.py --vendor "Vendor Name"
```
