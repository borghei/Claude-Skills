# Red Flags: North Star Metric

> Common ways this skill's output goes wrong — concrete examples, why they're bad, and how to fix them.

## How to use this document

Scan the NSM spec and `metric_tree_builder.py` output before publishing to the team or board. Each red flag shows the *bad* version next to the *good* version, anchored to Sean Ellis's NSM framing, Amplitude's archetype model, and OMTM (Lean Analytics).

---

## Red Flag 1: NSM = revenue

**Symptom.** Team picks "Monthly Recurring Revenue" as the North Star Metric.

**Why it's bad.** Revenue is the lagging financial *outcome* of value delivered. It is what happens after customer value is delivered, retention is good, and pricing is correct. Using revenue as NSM gives the team no actionable lever — every team affects revenue indirectly through 12 layers. The NSM should be a customer-value proxy that revenue *follows from*.

**Bad example:**
> "NSM: Monthly Recurring Revenue. Current: $4.2M. Target: $6.5M by Q4. Inputs: 'Marketing spend, Sales velocity, Product features'."

**Good example:**
> "NSM: Weekly active accounts that complete a deliverable. Current: 12,400. Target: 22,000 by 2027-06-30. Why: revenue follows from value; value is delivered when a user completes a deliverable; we are a productivity product. Inputs: (1) WAA — direct activity, (2) Publisher rate — depth of value. Revenue is tracked as a KPI alongside the NSM but is not the NSM."

**How to catch it.** Apply the 5 tests: customer value, strategic alignment, leading, single number, movable. Revenue fails "leading" — it lags every action.

---

## Red Flag 2: Missing counter-metrics

**Symptom.** NSM spec has 4 input metrics, all of which the team is trying to drive up. No anti-metrics, no counter-metrics.

**Why it's bad.** The NSM is a powerful lever that can be gamed. Without counter-metrics, the team can hit the NSM number through harmful means — bad signups, junk content, low-quality usage. The number goes up; the business goes down.

**Bad example:**
> "NSM: Messages sent per WAU. Inputs: 1) WAU. 2) Messages per session. 3) Sessions per week. (No anti-metrics. No counter-metrics.) (6 months later: messages per WAU doubled; abuse reports up 9x; ad revenue per impression down 35% due to spam-driven engagement.)"

**Good example:**
> "NSM: Messages sent per WAU. Inputs: WAU, Messages/session, Sessions/week. Anti-metrics (must NOT degrade):
> • Messages reported as spam (threshold: stay below 0.4%).
> • Abuse reports per 10k messages (threshold: stay below 12).
> • Blocked-user rate (threshold: stay below 3% monthly).
> Counter-metrics (the business protection):
> • Revenue per message (threshold: stay above $0.018; if NSM goes up while revenue/msg goes down, we are losing on bad messages).
> Every NSM ships with >= 2 anti + >= 1 counter."

**How to catch it.** Read the NSM spec. Search for "anti" and "counter". If either is missing, the guardrails are absent.

---

## Red Flag 3: Inputs do not multiply/sum to the NSM

**Symptom.** Inputs are "loosely related" to the NSM. Team cannot write an explicit formula.

**Why it's bad.** If inputs are not mathematically derived from the NSM, moving an input may not move the NSM. The team works hard on inputs and the NSM doesn't budge; the relationship was correlative, not causal.

**Bad example:**
> "NSM: WAU. Inputs: (1) Marketing campaign launches. (2) NPS. (3) Feature adoption. (4) Customer-support response time. (No formula. No multiplication or addition relationship.)"

**Good example:**
> "NSM: WAA (weekly active accounts).
> Formula: WAA = New_signups_30d_back * Activation_rate * Retention_rate_4w.
> Inputs:
> 1. New_signups_30d_back (controls top-of-funnel).
> 2. Activation_rate (% of new signups completing first key action in 7 days).
> 3. Retention_rate_4w (% of activated users still active in week 4).
> Each input mathematically combines to the NSM."

**How to catch it.** Ask: "write the formula relating inputs to the NSM." If the team cannot, the inputs are loose.

---

## Red Flag 4: Leading indicators = lagging indicators

**Symptom.** Team labels "weekly retention" as a leading indicator. Weekly retention is measured at day 7.

**Why it's bad.** A leading indicator must move *before* the input metric. It gives an early-warning signal. Weekly retention is measured 7 days later; by then, the input has already moved or not. The team is reading the speedometer, not the road ahead.

**Bad example:**
> "Input: weekly retention. Leading indicator: weekly retention. (Tautology.)"

**Good example:**
> "Input: weekly retention (measured at day 7).
> Leading indicators (move days/weeks earlier):
> • Day-1 session count for new signups (predicts whether they will retain to day 7).
> • First-action-completion in session 1 (predicts day-1 return).
> • Re-engagement notification CTR (predicts session 2 — required for week-1 retention).
> These move 1-6 days before retention can be measured."

**How to catch it.** For each leading indicator, ask: "how many days/weeks before the input does this move?" If 0 days or 'same time', it's not leading.

---

## Red Flag 5: NSM changes every quarter

**Symptom.** Q1 NSM was "DAU". Q2 NSM was "Trial-to-paid conversion". Q3 NSM is "Activation rate".

**Why it's bad.** An NSM that changes every quarter is not a North Star — it's whatever metric the team is currently optimizing. The point of an NSM is durable alignment; constant change indicates strategic drift or lack of commitment. Often the underlying issue is genuine strategic confusion, which the NSM exposes but cannot fix.

**Bad example:**
> "Q1 NSM: DAU. Q2: Revenue. Q3: Activation rate. (Each quarter the team optimizes the new NSM; no compounding improvement; team feels they 'never make progress'.)"

**Good example:**
> "NSM committed for at least 4 quarters: 'Weekly active accounts publishing >= 1 deliverable'. Reviewed quarterly but not changed unless strategy genuinely shifts (re-align to new market, pivot business model). Quarterly OKRs map to inputs that move the NSM; the NSM is the durable target."

**How to catch it.** What was the NSM 12 months ago? If different, ask: "did strategy genuinely shift, or did the team change metrics?"

---

## Red Flag 6: NSM exposes strategic disagreement (and team tries to fix it with the metric)

**Symptom.** Five candidate NSMs. Team can't pick. Three weeks of debate.

**Why it's bad.** NSM debate is often a proxy for strategy debate. If the team can't agree on the NSM, they don't agree on what business they're in. The NSM is downstream of strategy; trying to fix it without fixing the strategy debate is theater.

**Bad example:**
> "NSM candidates after 5 sessions: (1) WAU, (2) MRR, (3) Customers, (4) Time-on-platform, (5) NPS. Team divided 2/2/1/1/1. Decision: 'we'll go with WAU because most people picked it.'"

**Good example:**
> "After 2 sessions of NSM debate with no resolution, recognize the underlying issue: strategy. Convene a strategy session with the exec sponsor. Three weeks later: strategy resolved (we are a productivity product for teams of 5-50, optimizing for value delivered per team). NSM follows: 'Weekly active teams publishing >= 1 deliverable'. The metric debate took 30 min after strategy was clear."

**How to catch it.** Length of NSM debate. > 2 sessions = the NSM is not the actual disagreement.

---

## Red Flag 7: NSM is gameable without team noticing

**Symptom.** NSM is "signups". Marketing runs a giveaway that drives 10x signups. NSM is green. Quarter retention drops; revenue per user collapses. Team realizes too late.

**Why it's bad.** Signups without quality is a junk metric. The NSM didn't include the protection (counter-metric on activation or retention or revenue-per-user). Goodhart's Law in action: when a measure becomes a target, it ceases to be a good measure.

**Bad example:**
> "NSM: total signups/month. Target: 50k. Achieved: 60k after the giveaway. Quarterly review: 'NSM exceeded — celebrating'. (Reality: revenue per signup down 78%; the marginal users are not real customers.)"

**Good example:**
> "NSM: paid weekly active accounts (the 'paid' adjective is the structural fix). Counter-metric: cost per acquired paid account (must stay below $X). With these two together, the team cannot win NSM via cheap junk signups — the counter constrains acquisition quality."

**How to catch it.** Ask: "what is the cheapest dumb thing we could do to move the NSM up?" If that exists and is not blocked by a counter, the NSM is gameable.

---

## Red Flag 8: NSM lives in a slide deck, not in dashboards

**Symptom.** Exec slide says "Our NSM is WAA". Team's weekly review shows revenue, MAU, conversion. The NSM is nowhere on the team's daily dashboard.

**Why it's bad.** A metric that isn't visible isn't a North Star. The team optimizes what they see daily; if the NSM isn't on the dashboard, the team will optimize whatever is. The slide-deck NSM is decoration.

**Bad example:**
> "Exec deck slide 3: 'NSM = WAA'. Team's BI dashboard: 14 widgets, none showing WAA. PRDs reference revenue, not WAA. Standups never mention WAA."

**Good example:**
> "NSM appears in:
> • Team's main dashboard (top widget, 13-week trend).
> • Weekly status update (first line of 'Highlights').
> • PRD Section 4 (KRs tie to NSM inputs).
> • Quarterly review (headline number).
> • New-hire onboarding (one of the first things a new joiner learns).
> If a stakeholder cannot find the current NSM in < 2 clicks, the NSM is not operational."

**How to catch it.** Try to find the current NSM number. > 2 clicks = not operational.

---

## Red Flag 9: NSM without instrumentation

**Symptom.** Team picks "publishers per WAA" as an input. Engineering: "we don't track who counts as a publisher; need to instrument that."

**Why it's bad.** An NSM-without-data is aspirational. The team will spend the next 8 weeks instrumenting before they can even measure the metric, let alone move it. NSM exercises that precede telemetry investment produce dashboards that show nothing.

**Bad example:**
> "Q3 NSM: 'Weekly active accounts publishing >= 1 deliverable'. Engineering: 'we don't currently track publish events as a discrete metric; need 8 weeks of instrumentation.' Q3 ends; team has metric data for the last 4 weeks only; no trend; no calibration."

**Good example:**
> "Pre-NSM check: 'do we have the instrumentation to measure each candidate NSM?' If no, spend 4-6 weeks shipping the instrumentation first. Otherwise pick an NSM that we can measure today (e.g., WAA, where active = login+1 action; we already track this). Trade off ambition for actionability; instrument the dream metric next quarter."

**How to catch it.** For each NSM candidate, ask: "can we report this from today's instrumentation, this week?" If no, telemetry is the prerequisite.

---

## Red Flag 10: Inputs that are not movable

**Symptom.** One of the inputs is "market size" or "competitive pressure" or "regulatory environment".

**Why it's bad.** Inputs are the levers the team can pull. External factors are not levers — they describe the playing field, not the team's actions. Including them in the input tree gives the team an excuse ("the input got worse; we couldn't move the NSM").

**Bad example:**
> "Inputs to MRR NSM: (1) New paid signups, (2) Churn rate, (3) ARPU, (4) Market growth rate, (5) Competitor pricing moves."

**Good example:**
> "Inputs to NSM: (1) New paid signups, (2) Churn rate, (3) ARPU. All three are team-movable. Market growth and competitor pricing are tracked in the 'Context' section of the quarterly review but are not inputs — they are background conditions the team doesn't control."

**How to catch it.** For each input, ask: "can the team move this within a quarter?" If no, it's a condition, not an input.

---

## Red Flag 11: One metric for a multi-archetype company

**Symptom.** Company has Productivity, Communication, and Transaction surfaces. NSM is one number meant to span all three.

**Why it's bad.** Amplitude's archetype framework: each archetype has its own value definition. A single NSM across mismatched archetypes is incoherent — moving the metric for one surface doesn't represent value on the others. The NSM becomes a compromise number that doesn't drive focus.

**Bad example:**
> "Company NSM: 'monthly active users completing any value action'. (Spans productivity tasks, social messages, marketplace transactions. Each surface team optimizes their own thing; the company NSM moves by averaging; no surface is clearly winning.)"

**Good example:**
> "Company-level: each surface has its own NSM, plus a portfolio summary:
> • Productivity surface NSM: WAA publishing deliverables.
> • Communication surface NSM: WAU sending >= 2 meaningful messages.
> • Transaction surface NSM: Weekly transactions per active buyer.
> Portfolio: monthly active 'engaged accounts' (across surfaces). Each surface team operates against its archetype-native NSM; portfolio leaders look at the rollup."

**How to catch it.** Does the company have multiple distinct value-delivery surfaces? If yes and there's one NSM, the metric is averaging.

---

## Red Flag 12: NSM target without baseline

**Symptom.** NSM target: "Reach 50,000 WAA by Q4". No current value. No trajectory.

**Why it's bad.** Without baseline, "50,000" is meaningless. Is the team currently at 5k (need 10x growth) or 47k (need a normal quarter)? The target's ambition cannot be evaluated; commitment cannot be calibrated; missing the target produces no learning.

**Bad example:**
> "NSM: WAA. Target: 50,000 by Q4."

**Good example:**
> "NSM: WAA.
> Current (May 2026): 12,400.
> Trajectory (last 4 quarters): 8,200 → 9,400 → 10,800 → 12,400 (~14%/qtr growth).
> Q4 target: 22,000 (~75% lift, well above trajectory; requires step-change in activation experiment + paid channel expansion).
> Team confidence: 60%. If we miss at 60% confidence, we learn which assumption was wrong."

**How to catch it.** Open the NSM spec. Is current value present? Is the trajectory shown? If no to either, the target is unanchored.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | NSM = revenue | Does the NSM pass the "leading" test? |
| 2 | Missing counter-metrics | Are anti and counter metrics specified with thresholds? |
| 3 | Inputs don't combine to NSM | Can the team write the explicit formula? |
| 4 | Leading = lagging | How many days/weeks before input does the leader move? |
| 5 | NSM changes every quarter | What was the NSM 12 months ago? |
| 6 | NSM debate is strategy debate | > 2 sessions of debate = it's strategy |
| 7 | Gameable without team noticing | What's the cheapest dumb way to move the number? |
| 8 | NSM in a deck, not in dashboards | Can a stakeholder find current value in < 2 clicks? |
| 9 | NSM without instrumentation | Can we measure this from today's data? |
| 10 | Inputs that are not movable | Can the team move this within a quarter? |
| 11 | One NSM across mismatched archetypes | Does the company have distinct value surfaces? |
| 12 | Target without baseline | Is current value + trajectory shown? |

## Related Reading

- SKILL.md Troubleshooting
- references/nsm-framework-guide.md
- Sean Ellis, on the North Star Metric
- John Cutler, on "Tree of Metrics"
- Amplitude, "The North Star Framework"
- Alistair Croll & Benjamin Yoskovitz, *Lean Analytics* (OMTM)
- `brainstorm-okrs/` (KRs should move input metrics)
- `outcome-roadmap/` (initiatives target inputs)
