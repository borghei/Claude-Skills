# Pirate Metrics Deep Dive

A working reference for the Pirate Metrics (AARRR / AAARRR) framework, how it sits in the broader growth canon, and how to apply it cleanly.

## 1. Origin: Dave McClure's "Startup Metrics for Pirates" (2007)

Dave McClure, founding partner of 500 Startups, gave a talk in 2007 titled "Startup Metrics for Pirates: AARRR!" The acronym was chosen because each letter sounds like a pirate (and the joke aged better than most). The five-stage growth funnel:

| Stage | Question | Why it matters |
|---|---|---|
| **Acquisition** | How do users find us? | If acquisition is broken, nothing else matters; but it is the most over-optimized stage in most teams |
| **Activation** | Do they have a good first experience? | This is the leverage point; activation rate is correlated with everything downstream |
| **Retention** | Do they come back? | Retention is the true product-market-fit signal; without it, acquisition is pouring water into a leaky bucket |
| **Revenue** | Do they pay? | Monetization signals (trial-to-paid, expansion, LTV) |
| **Referral** | Do they bring friends? | The most underrated channel; viral coefficient > 1 is rare but transformative |

McClure's original argument was that startups obsess over acquisition (top) and revenue (bottom) and ignore the middle (activation, retention), which is where most products actually break.

## 2. AAARRR: adding Awareness

A common extension prepends **Awareness** at the very top:

- **Awareness**: Do they know we exist at all? (brand search, mentions, share of voice)
- **Acquisition**: Do they visit us? (signups, visits)

Use AAARRR when:
- The product category is new (users do not know to search for you).
- The brand is new and competing in a crowded category.
- The team is doing top-of-funnel demand-gen and needs an awareness metric to manage.

Use AARRR (no awareness) when:
- The category is known.
- The funnel starts at "visit to your site" because demand-gen lives in a separate funnel.

## 3. Brian Balfour's "Four Fits"

Brian Balfour's "Four Fits" framework adds the channel-product and model-channel layers around AARRR. Useful when AARRR alone is not surfacing the real failure:

- **Market-Product fit** -- the product solves a real problem for a real market.
- **Product-Channel fit** -- the channel can reliably deliver users matching the product.
- **Channel-Model fit** -- the channel CPA matches the LTV the model can sustain.
- **Model-Market fit** -- the business model (subscription, transaction, ad-supported) matches the market's willingness to pay.

If activation is fine but acquisition is failing, the leak is usually channel-product or channel-model fit. AARRR diagnoses the funnel; Balfour's Four Fits diagnose the system around the funnel.

## 4. Andrew Chen on funnel design

Andrew Chen (formerly Uber Rider Growth) argues that effective funnels are:

- **Built from real cohorts**, not snapshots. A snapshot funnel pools users at different lifecycle stages and lies.
- **Specific to a single journey**. A "general activation funnel" that tries to cover all user types ends up vague.
- **Visualized**. A funnel that lives only in a spreadsheet does not get used.
- **Reviewed weekly**. The deltas matter as much as the absolute numbers.

Chen's "Law of Shitty Clickthroughs" is also relevant: the conversion rate of any specific tactic decays over time as users habituate. Today's 6% conversion will be 2% in 18 months unless the tactic is refreshed. Funnel optimization is a continuous job, not a project.

## 5. Sean Ellis: activation as the leverage point

Sean Ellis (coined "growth hacking"; creator of the PMF survey) is the primary source for the activation-rate framing.

His method:
1. Identify the cohort of users who are still active (or paying) at a meaningful retention horizon (often D30 or D90).
2. Look at what those users did in their first session / first week / first month.
3. Find the behavior with the highest correlation to surviving to that horizon.
4. That behavior is the activation event.

The "Sean Ellis PMF Survey" (separately famous) -- "How would you feel if you could no longer use this product?" with a 40%+ "very disappointed" threshold -- is a different tool from activation, but it pairs naturally: the activated cohort is where you should run the PMF survey.

## 6. Lean Analytics: One Metric That Matters (OMTM)

Croll and Yoskovitz, *Lean Analytics* (2013), introduced OMTM: at any stage of company growth, there is one metric that matters most, and the team should rally around it. The mapping to AARRR:

| Company stage | OMTM candidate | AARRR stage |
|---|---|---|
| Pre-PMF | Activation rate or D30 retention | Activation / Retention |
| Post-PMF | Weekly active users or revenue | Retention / Revenue |
| Scale | Net revenue retention | Revenue |

The OMTM concept lives in this skill via the activation event: in onboarding-focused work, activation rate is often the OMTM, full stop.

## 7. The Amplitude North Star Playbook

Amplitude's *North Star Playbook* (2019, updated through 2024) links the funnel to the North Star Metric (NSM):

- The NSM is the headline metric of customer value (see `north-star-metric/`).
- The funnel's terminal stages decompose into NSM input metrics.
- Funnel conversion improvements move NSM inputs, which move the NSM.

Practical: the funnel and the NSM tree should share vocabulary. The "activation" stage in the funnel is often the same event as an input metric in the NSM tree. If they disagree, fix the disagreement -- it usually means strategic ambiguity, not metric ambiguity.

## 8. Counter-metrics in detail

Every funnel optimization carries a risk of degrading something else. The classic failure modes:

**Acquisition gaming.**
- Drop email verification -> signup rate climbs, fake-account rate climbs more.
- Optimize for low-friction signup -> users who do not match the product profile flood in.
- Counter-metric candidates: real-email %, signup-to-activation %, signup quality score.

**Activation gaming.**
- Auto-import data -> "activated" climbs, real engagement stays flat.
- Lower the activation bar -> definition drifts; "activated" no longer predicts retention.
- Counter-metric candidates: D7 retention of activated users; engagement events per activated user.

**Retention gaming.**
- Push notification spam -> D7 climbs, unsubscribe rate climbs more.
- Counter-metric candidates: NPS / CSAT; uninstall rate; email-unsubscribe rate.

**Revenue gaming.**
- Aggressive paywall -> trial-to-paid climbs, first-month churn climbs more.
- Counter-metric candidates: refund rate; first-month churn; LTV.

**Referral gaming.**
- Incentivize invites with high-value rewards -> invites sent climbs, invite acceptance and quality drop.
- Counter-metric candidates: invite-acceptance rate; activation rate of referred users.

## 9. Cohort vs snapshot

A snapshot funnel pools users at different stages of their lifecycle into a single chart. It hides time-based effects and lies.

A cohort funnel pins a starting population (e.g., everyone who signed up in week W) and follows them through subsequent stages over a fixed observation window. It is honest but harder to set up.

| Comparison | Snapshot | Cohort |
|---|---|---|
| Easy to compute | Yes | No |
| Honest | No | Yes |
| Comparable week to week | Mostly no | Yes |
| Captures lifecycle effects | No | Yes |
| Influenced by marketing pushes | Heavily | Cleanly attributable to the cohort |

The trade-off: cohort funnels take time to mature (a D30 metric is only available 30 days after the cohort lands). Use both: cohort for honest analysis, snapshot for fast-moving daily ops.

## 10. Leading, activation, and lagging metrics

| Type | Time horizon | Use |
|---|---|---|
| Leading | Hours / days | On-call / daily dashboard. Move first; predict activation. |
| Activation | First N days | Headline conversion. Move things to optimize. |
| Lagging | D30 / D60 / D90 | Audit. Confirms activation is still predictive. |

A common mistake is treating the activation event as the lagging metric. Activation is leading-adjacent: it should move within the first session or first week. D30 retention is the lagging metric that validates the activation definition.

## 11. Hooks, loops, and the modern view

In 2023-2026 growth literature, the linear funnel is increasingly paired with **loops** ("growth loops", Sangeet Paul Choudary's "platform loops"). A loop is a self-reinforcing cycle where the output of one stage becomes the input to another -- typical examples: content loops (users create content -> content draws new users), invite loops (activated users invite others), data loops (more usage -> better recommendations -> more usage).

Linear funnel + loops is the full picture:
- The funnel describes the user's journey from awareness to revenue.
- The loops describe how the system self-reinforces.

A modern PM owns both. This skill is the funnel half; opportunity-tree skills like `discovery/interview-synthesis/` and `discovery/brainstorm-ideas/` cover the loops half.

## 12. Anti-patterns

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Optimizing only the top of funnel | Acquisition climbs; revenue flat | Run the analysis; redirect to the largest absolute drop, usually mid-funnel |
| Treating "completed onboarding" as activation | Activation climbs but D30 flat | Re-derive activation from retained-vs-churned cohort behavior |
| No counter-metrics | Stage conversion climbs; user satisfaction or business KPI drops | Pair every stage with a counter-metric |
| Snapshot funnel only | Weekly numbers swing; no clear signal | Add a cohort funnel for weekly review |
| 12-stage funnel | Stakeholders glaze over | Compress to 5-7 stages; let the deeper drill-down live in a dashboard |
| Funnel is an annual artifact | Drops never get fixed | Weekly review; assign owners per stage |
| One funnel for all user types | Buyer journey differs by segment | One funnel per segment (or per persona) |

## Reading list

- Dave McClure, "Startup Metrics for Pirates" (2007 talk, multiple updated versions)
- Sean Ellis + Morgan Brown, *Hacking Growth* (2017)
- Alistair Croll + Benjamin Yoskovitz, *Lean Analytics* (2013)
- Brian Balfour, "Four Fits" framework
- Andrew Chen, "The Law of Shitty Clickthroughs"
- Amplitude, *North Star Playbook* (2019, latest 2024)
- Sangeet Paul Choudary, *Platform Revolution* (2016)

---
**Last Updated:** 2026-05-22
