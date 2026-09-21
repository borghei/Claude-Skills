# Red Flags: Delivery Manager

> Common ways this skill's output goes wrong — concrete examples, why they're bad, and how to fix them. Pair with the SKILL.md and Troubleshooting table.

## How to use this document

When you have just produced a release plan, incident response, change-request evaluation, or maturity assessment, scan the red flags below. Each red flag shows a *bad* and *good* version.

---

## Red Flag 1: Blame-Seeking Incident Handling

**Symptom.** Post-incident review focuses on "who did this" — naming individuals, assigning fault. Quiet rooms, defensive language, no candid contributions.

**Why it's bad.** Blame culture destroys reporting. Engineers stop flagging near-misses; small problems compound into outages. Allspaw's blameless post-mortem framing exists because the alternative empirically reduces safety. Naming a culprit is satisfying and counter-productive.

**Bad example:**
> Post-incident: "Raj deployed without proper review. Action: written warning. Lessons: be more careful."

**Good example:**
> Post-incident: "The deployment passed our review gate but our review gate did not catch the missing config flag. Root cause: review checklist did not include config-flag verification for canary deploys. Action: update checklist + add automated check. Raj's deploy followed our process; the process needs work."

**How to catch it.** Read the post-mortem. Does it name an individual as the cause? If yes, the framing is unsafe.

---

## Red Flag 2: Missing Rollback Rehearsal

**Symptom.** Release plan documents a rollback procedure, but the procedure has never been tested in production-like conditions.

**Why it's bad.** Untested rollback procedures fail when needed. The 3am incident is not the time to discover that the rollback script depends on a tool no one has installed, or that the database migration is not reversible. Maturity Level 4-5 requires rehearsed rollback.

**Bad example:**
> Release plan: "Rollback: revert deploy via Jenkins. DB migration is forward-only; data recovery via backup if needed."

**Good example:**
> Release plan: "Rollback procedure tested in staging on 2026-05-15 (signed off by EM + on-call). Migration designed as expand-contract: new columns added in week 1, code switches to new columns in week 2, old columns removed in week 3 — fully rollback-safe at each step. Rollback target time: 15 min p50, 30 min p95."

**How to catch it.** Has the rollback been rehearsed in the last 90 days, with measured target time? If not, the plan is theoretical.

---

## Red Flag 3: Error Budget Treated as Reliability Theater

**Symptom.** Team has SLOs and an "error budget" but never actually slows feature work when the budget is burned.

**Why it's bad.** The point of error budgets is to create an automatic tension between reliability and feature velocity. Budgets that never bite are decorative. Maturity Level 4-5 organizations enforce budget consequences: when burned, feature freeze until reliability work restores it.

**Bad example:**
> SLO: 99.9% uptime. Budget for the month: 43 min. Actual downtime: 4 hours. Action: noted in monthly report, continued feature work."

**Good example:**
> SLO: 99.9% uptime. Budget: 43 min/month. Actual: 4 hours (budget exceeded by 5x). Action triggered by policy: feature work paused, 100% of capacity to reliability for 2 weeks. Restoration plan: 3 named items, ETA documented. Restart criteria: budget restored to <50% consumption for 30 days."

**How to catch it.** Has your team ever paused feature work because the error budget was burned? If never, the budget is decorative.

---

## Red Flag 4: Deployment Strategy Mismatch

**Symptom.** Team uses blue-green deployment for a high-traffic, stateful service where canary would surface bugs earlier. Or rolling deployment for a service where blast-radius needs full isolation.

**Why it's bad.** Each strategy has a profile: blue-green = fast switch, double infrastructure cost, hard for stateful; canary = gradual exposure, slow validation, requires monitoring sophistication; rolling = simple, partial exposure during rollout. Mismatched strategy produces either (a) bigger blast radius than necessary or (b) unnecessary cost.

**Bad example:**
> "We use blue-green for everything." (One service has 200 GB of stateful in-memory cache; blue-green requires warming the green environment for 90 min before switch.)

**Good example:**
> "Deployment strategy per service: stateless APIs use rolling (simple, fast). Customer-facing UI uses canary (5% -> 25% -> 100% over 4 hours, with auto-rollback on error-rate spike). Stateful cache service uses blue-green with pre-warming. Documented per-service in runbook."

**How to catch it.** Can you justify the deployment strategy per service? If not, you are using one strategy for everything.

---

## Red Flag 5: Communication Plan Missing T-7/T-1/T+1

**Symptom.** Release plan covers T-0 (the deploy itself) but no pre-deploy comms, no go/no-go gate, no post-deploy follow-up.

**Why it's bad.** Surprises break trust with stakeholders. A release that ships without T-7 scope-finalization and T-1 go/no-go feels chaotic to support, sales, and customer-facing teams. A release without T+1 follow-up leaves customers and stakeholders wondering whether it landed safely.

**Bad example:**
> Release plan: "Deploy v2.5.0 on Tuesday at 10am. Slack post when done."

**Good example:**
> Release plan: "T-7 (Tue prior): scope frozen, release notes drafted, internal preview posted. T-1 (Mon): go/no-go meeting at 4pm with eng, product, support, marketing. Owner has authority to delay. T-0 (Tue 10am): deploy, monitoring on, status updates every 30 min in #release. T+1 (Wed): customer comms (changelog, release email if customer-facing), retro scheduled for following week."

**How to catch it.** Does the plan cover all four checkpoints? Missing any is a process gap.

---

## Red Flag 6: Change Advisory Board (CAB) as Rubber Stamp

**Symptom.** CAB meets weekly, approves every change request in <2 minutes per request, never blocks or modifies a change. Or, CAB blocks every change, becoming a velocity tax.

**Why it's bad.** Both ends are anti-patterns. A rubber-stamp CAB is bureaucratic theater — it adds delay without adding safety. A blocking CAB is risk-averse paranoia — it slows the org without proportionate risk reduction. Healthy CABs are *exceptions-based*: standard changes auto-approve, only high-risk changes need real review.

**Bad example:**
> CAB approves 100% of 47 requests this month, average 90 seconds per request.

**Good example:**
> Change taxonomy: Standard (pre-approved, automated, no CAB) = 80% of changes. Normal (CAB review) = 18%. Major (executive review + customer comm) = 2%. CAB only sees 'Normal' and 'Major' — about 10 requests per month, each with a real review. Standard changes flow through CI/CD."

**How to catch it.** What % of changes does CAB see? If above 50%, the taxonomy is broken. If 100% approved, the review is fake.

---

## Red Flag 7: Incident Severity Inflation or Deflation

**Symptom.** Every minor issue gets logged as Sev-1 (inflation), or genuine outages stay at Sev-3 (deflation) because higher severity triggers paperwork.

**Why it's bad.** Severity inflation desensitizes the team — "another Sev-1, ignore the page." Severity deflation hides real problems — customers experience outages while the dashboard says "green." Both produce wrong investment in reliability.

**Bad example:**
> Last 30 days: 42 Sev-1 incidents declared. 38 were minor support tickets escalated by frustrated users.

**Good example:**
> Severity rubric documented: Sev-1 = >5% of customers impacted, revenue impact, or data loss. Sev-2 = degradation affecting >1% customers. Sev-3 = isolated. Quarterly severity review by senior on-call to recalibrate. Sev-1 rate stable at 1-3 per month."

**How to catch it.** Sample 10 recent Sev-1 declarations. How many actually meet the documented criteria? Below 80% match means severity is misused.

---

## Red Flag 8: Runbook That No One Has Run Recently

**Symptom.** Runbook for database failover, dated 2022, never tested. When the failover is needed, half the commands fail because the tool changed.

**Why it's bad.** Runbooks rot faster than code. A runbook untested in 6+ months should be treated as fiction. The fix is game-day exercises — scheduled runbook executions on staging or production with safety net.

**Bad example:**
> "We have a comprehensive runbook for database failover." (Last executed 2022. Tools referenced are deprecated.)

**Good example:**
> "Quarterly game-day: rotation of critical runbooks tested by on-call engineer in staging or controlled production. Last database-failover game-day: 2026-04-10, all steps executed, 3 commands updated, runtime measured (12 min vs 18 min target). Runbook freshness tracked per item."

**How to catch it.** For your top 5 critical runbooks, when were they last executed end-to-end? If any over 6 months, that runbook is suspect.

---

## Red Flag 9: Feature Flags Used Without Cleanup

**Symptom.** Codebase has 400+ feature flags, half of them set to 100% on for 2+ years. Conditional logic everywhere, nobody knows which flags are still meaningful.

**Why it's bad.** Feature flag debt is real debt. Every flag is conditional complexity, a potential bug surface, and a cognitive tax on engineers. The discipline is flag-with-end-date.

**Bad example:**
> Feature flag inventory: 412 flags. 187 at 100% on for >18 months. 23 at 0% with no documentation on why.

**Good example:**
> Flag policy: every flag has an owner, a creation date, and a target sunset date. Monthly flag-cleanup ritual: flags past sunset date either removed or re-justified. Current inventory: 41 flags, all under 6 months old or actively managed."

**How to catch it.** How many flags are over 12 months old? If above 20, you have flag debt.

---

## Red Flag 10: Deploy Frequency Without Lead Time

**Symptom.** Team reports "we deploy 50 times per week" but lead time from commit to production is 8 days.

**Why it's bad.** Deploy frequency without lead time hides the real bottleneck. DORA's metrics work together: deployment frequency, change lead time, change fail rate, failed deployment recovery time (formerly MTTR), and, since the 2024 report, deployment rework rate. Reporting one without the others paints a misleading picture.

**Bad example:**
> Quarterly delivery report: "Deployments: 287 (industry-leading). Reliability: high."

**Good example:**
> Quarterly delivery report (DORA): Deploys per week = 50, lead time p50 = 8 days (target 3), change failure rate = 12% (target <15%), failed deployment recovery time = 42 min (target <60), rework rate = 6% of deploys. Improvement area: lead time — root cause is review queue depth, action plan in place."

**How to catch it.** Does your delivery report show all the DORA metrics (the classic four, plus rework rate if you track it)? If not, one or more is being hidden.

---

## Red Flag 11: SLA Promises Without Capacity to Meet Them

**Symptom.** Sales promises 99.99% uptime in customer contracts. Engineering has not staffed for that SLO; actual uptime is 99.5%.

**Why it's bad.** Promised reliability without engineering capacity produces breached contracts, SLA credits, and customer churn. SLOs must be co-owned by sales and engineering, with cost implications visible to both.

**Bad example:**
> "We promise 99.99% in enterprise contracts." (Engineering team of 5 supporting one region, no 24/7 on-call, last quarter uptime 99.5%.)

**Good example:**
> "SLO tiers: 99.9% standard (covered by current capacity), 99.95% premium (requires multi-region, costs $X/month, dedicated on-call rotation), 99.99% enterprise (requires both + active-active, costs $Y, contract minimums). Sales authorized to promise tier matching customer commitment."

**How to catch it.** Are your contractual SLAs aligned with your engineering capacity? If not, you are pre-paying penalties.

---

## Red Flag 12: Maturity Score Inflation

**Symptom.** Team self-assesses at Level 4 (Continuous Deployment) but actual deploys are manual, monitoring is uptime-only, and rollback is not automated.

**Why it's bad.** Inflated maturity assessments hide real gaps. Leadership invests based on the inflated number ("we're already great at delivery, invest elsewhere") while real risks accumulate. The SKILL.md's level criteria exist precisely to prevent this.

**Bad example:**
> "Self-assessment: Level 4. We deploy a lot." (No automation, no canary, no auto-rollback, basic uptime monitoring.)

**Good example:**
> "Self-assessment: Level 2 (Automated Build/Test). Evidence: CI passing, automated unit tests, manual deploys via Jenkins, basic uptime monitoring. Target Level 3 by Q4: deploy automation + comprehensive monitoring. Investment plan: $X, 2 engineers for 1 quarter."

**How to catch it.** For each level claim, name the specific evidence required by the SKILL.md's level criteria. If evidence is missing, downgrade the level.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | Blame-Seeking Incident Handling | Post-mortem names individuals as cause? |
| 2 | Untested Rollback | Rollback rehearsed in last 90 days? |
| 3 | Error Budget Theater | Has feature work paused when budget burned? |
| 4 | Deployment Strategy Mismatch | Per-service strategy justified? |
| 5 | Missing T-7/T-1/T+1 | All four release checkpoints in plan? |
| 6 | CAB Rubber Stamp / Blocker | <50% of changes go to CAB, real review when they do? |
| 7 | Severity Inflation/Deflation | 80%+ of declared severities match rubric? |
| 8 | Stale Runbook | Last end-to-end execution under 6 months? |
| 9 | Feature Flag Debt | Flags over 12 months under 20 total? |
| 10 | Deploy Frequency Without Lead Time | All DORA metrics reported together? |
| 11 | SLA Beyond Capacity | Contractual SLA aligned with engineering capacity? |
| 12 | Maturity Score Inflation | Each level claim has specific evidence? |

## Related Reading

- SKILL.md Troubleshooting section (for symptom -> root cause -> resolution)
- references/release-checklist.md (if present)
- references/incident-response.md (if present)
- agile-coach/references/red-flags.md (for adjacent maturity-assessment patterns)
