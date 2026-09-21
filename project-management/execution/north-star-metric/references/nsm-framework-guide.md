# NSM Framework Guide

A reference on three overlapping NSM frameworks (Sean Ellis NSM, Amplitude NSM, Lean Analytics OMTM), the math of input metrics, the role of anti-metrics and counter-metrics, and worked examples for five business archetypes.

---

## Part 1: Three overlapping frameworks

### Sean Ellis (NSM)

Sean Ellis (who coined "growth hacking") introduced the NSM as the single metric that best captures the core value your product delivers. The core idea: if every team optimizes against the NSM, they will collectively move the business forward without coordination overhead.

Key rules from Ellis:
- One metric, not a "balanced scorecard"
- Tied to customer-perceived value, not company revenue
- Movable by the team (not a vanity metric)

### Amplitude (NSM framework)

Amplitude codified the NSM into a more rigorous framework with two essential additions:

1. **Archetype mapping** -- match the NSM to one of five business models (attention, transaction, productivity, communication, subscriber)
2. **Input metric decomposition** -- the NSM must mathematically decompose into a handful of inputs the team can directly move

The Amplitude framework also formalized **anti-metrics** (must-not-move metrics that prevent gaming) and **counter-metrics** (business-protection metrics).

### Lean Analytics (OMTM)

Alistair Croll and Benjamin Yoskovitz's "Lean Analytics" introduced the **One Metric That Matters (OMTM)**: at any given stage of company growth, there is exactly one metric the team should obsess over. The OMTM **changes by stage** (Empathy / Stickiness / Virality / Revenue / Scale).

OMTM and NSM differ in framing: NSM is the durable customer-value metric; OMTM is the current-stage focus. Both can co-exist -- the NSM is durable across years, the OMTM might be "weekly retention" this quarter and "expansion revenue" next quarter.

---

## Part 2: The five tests

A defensible NSM must pass all five:

### Test 1: Customer value

If the NSM goes up, did the customer get more value? Or did the company just get more activity?

| NSM | Passes? | Why |
|-----|---------|-----|
| "Pages viewed per session" | Mixed | Could mean useful exploration OR confused navigation |
| "Tasks completed per WAU" | Yes | Tasks completed is the value the product delivers |
| "Time on site" | Mixed | Engagement OR difficulty completing a task |
| "Revenue" | No | Customer value is upstream of revenue |

### Test 2: Strategic alignment

Does this match how the company makes money? An attention NSM in a transactional business is a misalignment.

### Test 3: Leading, not lagging

Does the NSM predict future success? Revenue is a lagging metric -- by the time it moves, the value-delivery question is settled. A retention-style or engagement-style metric leads.

### Test 4: Single number

Can it be a single number on a dashboard? "DAU/MAU ratio" is one number. "DAU and MAU separately" is two -- which is fine as inputs but not as the NSM.

### Test 5: Movable

Can the team affect it within a quarter? If the team's daily work cannot move the metric in 90 days, the NSM is too lagging.

---

## Part 3: Math of input metrics

The NSM should decompose into inputs that have an **explicit** mathematical relationship to it. There are four common patterns:

### Multiplicative

The NSM is the product of inputs.

`NSM = Input_1 x Input_2 x Input_3`

Example: `Total tasks completed = WAU x (Sessions per WAU) x (Tasks per session)`

Multiplicative trees are powerful: moving any single input moves the NSM proportionally. They also expose tradeoffs (a 50% lift in one input compensates for a 33% drop in another).

### Additive

The NSM is the sum of inputs.

`NSM = Input_1 + Input_2 + Input_3`

Example: `Total signups = Web signups + Mobile signups + API signups`

Additive trees are simple but less informative. A 10% lift in any input lifts the NSM by 10% of that input's contribution.

### Funnel

Each input is a gate on the next.

`NSM = Top of funnel x Step_2 conversion x Step_3 conversion x ...`

Example: `Activated paid users = Visitors x Signup rate x Activation rate x Trial-to-paid rate`

Funnel trees are common in growth contexts. They concentrate attention on the lowest-converting step.

### Ratio

The NSM is itself a ratio.

`NSM = Engaged events / Total user-weeks`

Example: `DAU/MAU = DAU / MAU` (an engagement ratio used by social/media apps)

Ratio NSMs decompose differently -- you must move either the numerator OR the denominator deliberately, and the inputs are usually nested ratios themselves.

### Write the formula explicitly

If you cannot write the formula, the inputs are not really inputs. Write `NSM = ...` in your spec and verify the math holds with last quarter's numbers.

---

## Part 4: Leading indicators in depth

A leading indicator moves **before** an input metric. The lag is what makes it valuable -- it gives the team an early warning that the input is about to move (up or down).

### Lag thresholds

- **Same-day leaders** (sessions, button clicks): move within minutes of the team's actions. Useful for A/B tests and incident detection.
- **Daily leaders** (day-1 retention, first-task completion): move within a day. Useful for daily standups.
- **Weekly leaders** (week-1 cohort retention, feature adoption depth): move within a week. Useful for sprint reviews.

### Selecting leading indicators

For each input, ask:

1. What action does a user take that predicts they will affect this input?
2. What metric counts that action?
3. How fast does that metric move relative to the input?

If the leading indicator moves only after the input does, it is not leading -- it is a co-lagging proxy.

### Worked example

**Input:** Week-4 retention (lagging)

Possible leading indicators:

- **Day-1 retention** -- known by tomorrow
- **First-session feature adoption count** -- known within an hour
- **Time to first value** -- known within minutes
- **Signup-flow completion rate** -- known within minutes

All four move within hours; week-4 retention takes a month. The leaders tell you what week-4 will look like, weeks before it arrives.

---

## Part 5: Anti-metrics and counter-metrics

### Anti-metrics

Numbers that must NOT move (or must stay within a bounded direction) while the NSM moves up. They protect against customer-value erosion.

| NSM | Anti-metric | Why |
|-----|-------------|-----|
| Video minutes watched | Time-to-skip | Watching due to autoplay is not watching due to value |
| Messages sent per WAU | Messages reported as spam | Spam-driven volume is not engagement |
| Pages indexed | Crawler error rate | Indexing junk is not indexing value |
| Trial-to-paid conversions | 60-day refund rate | Sales pressure that produces refunds is not selling |

Set thresholds: "Time-to-skip must not exceed 8 seconds median." Without a threshold, the anti-metric is rhetorical.

### Counter-metrics

Numbers the team owns ensuring do not degrade because the NSM is chasing the wrong thing. Where anti-metrics protect the customer, counter-metrics protect the business.

| NSM | Counter-metric | Why |
|-----|----------------|-----|
| Signups | Paid conversion rate | Signups without conversion are operational debt |
| Time on site | Revenue per visit | Time without monetization is loss |
| Active users | Cost per active user | Engagement at infinite cost is bankruptcy |
| Messages sent | Server cost per message | Engagement that costs more than it earns is bankruptcy |

Each NSM should ship with at least 2 anti-metrics and 1 counter-metric.

---

## Part 6: Worked examples by archetype

### Attention archetype: media streaming app

- **NSM**: Time spent watching content with >=50% completion
- **Formula**: NSM = WAU x (Sessions per WAU) x (Minutes per session) x (Completion rate)
- **Inputs**: WAU, sessions per WAU, minutes per session, completion rate
- **Leading indicators**: Day-1 returning users, autoplay opt-out rate, first-session completion rate
- **Anti-metrics**: Time-to-skip < 12 seconds median, churn within 30 days of first watch < 6%
- **Counter-metric**: Subscription churn rate < 4%/mo

### Transaction archetype: marketplace

- **NSM**: Weekly gross merchandise value (GMV)
- **Formula**: NSM = Active buyers x (Orders per buyer) x (Average order value)
- **Inputs**: Active buyers, orders per buyer, average order value
- **Leading indicators**: Cart-create rate, listing-page conversion rate, repeat-buyer rate at 30 days
- **Anti-metrics**: Cancellation rate < 5%, refund rate < 2%, fraud-flagged orders < 0.5%
- **Counter-metric**: Take rate stable >= 12%

### Productivity archetype: SaaS task management

- **NSM**: Weekly active accounts publishing >=1 deliverable
- **Formula**: NSM = WAA x Publisher rate
- **Inputs**: WAA, publisher rate
- **Leading indicators**: First-deliverable in session 1, templates opened in week 1, invite-a-teammate rate
- **Anti-metrics**: Weekly churn < 4%, time-to-publish median < 22 min
- **Counter-metric**: Server cost per published deliverable < $0.08

### Communication archetype: messaging app

- **NSM**: Weekly active accounts sending >=2000 messages (Slack-style)
- **Formula**: NSM = WAA x P(>=2000 msgs in week)
- **Inputs**: WAA, message-volume-per-account distribution
- **Leading indicators**: Day-1 messages sent, channels created, integrations added
- **Anti-metrics**: Spam-flagged messages < 0.1%, abuse-report rate stable
- **Counter-metric**: Paid seat conversion >= 18%

### Subscriber archetype: SaaS subscription

- **NSM**: Paid weekly active subscribers
- **Formula**: NSM = Paid subs x Weekly active rate
- **Inputs**: Paid subs, weekly active rate
- **Leading indicators**: Trial-to-paid conversion rate, day-1 paid activation rate, NPS at day 30
- **Anti-metrics**: 60-day refund rate < 3%, NPS detractor share < 25%
- **Counter-metric**: Gross margin stable >= 78%

---

## Part 7: Common failure modes

| Failure | What it looks like | Fix |
|---------|-------------------|-----|
| NSM = revenue | Team chases revenue directly; PMs lose autonomy because finance owns the metric | Pick a customer-value proxy that revenue follows from |
| Too many NSMs | "Our NSM is engagement, retention, and conversion" | Pick one. The others are inputs or counter-metrics |
| NSM not movable in a quarter | Team's daily work cannot affect the metric within 90 days | Move upstream (closer to user action) or pick a leading proxy |
| NSM gamed | NSM moves up but customers report dissatisfaction | Add anti-metrics with thresholds; review weekly |
| NSM changes every quarter | No durability; team cannot build muscle around the metric | Commit for at least 4 quarters; if strategy truly shifts every 90 days, the NSM exercise is premature |
| NSM is a "balanced scorecard" | 5+ metrics with weights | The scoring is hiding strategic indecision. Pick one |

---

## Further reading

- Sean Ellis, "Hacking Growth" (Crown Business, 2017)
- Alistair Croll and Benjamin Yoskovitz, "Lean Analytics" (O'Reilly, 2013)
- Amplitude's "North Star Playbook" (free download)
- "The Hard Thing About Hard Things" -- Ben Horowitz on the perils of mismeasuring product

---

**Last Updated:** 2026-05-21
