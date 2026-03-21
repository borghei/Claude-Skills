---
name: ab-test-setup
description: Design and implement statistically rigorous A/B tests and experiments. Covers hypothesis formulation, sample size calculation, metric selection, traffic allocation, implementation patterns (client-side and server-side), statistical analysis, and common pitfalls. Use when planning experiments, calculating sample sizes, designing test variants, analyzing results, or when someone says "let's test that."
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: product-team
  domain: experimentation
  updated: 2026-03-09
  frameworks: hypothesis-testing, statistical-significance, feature-flags
---

# A/B Test Setup - Experimentation Design & Analysis

**Category:** Product Team
**Tags:** A/B testing, experiments, statistical significance, sample size, feature flags, hypothesis testing

## Overview

A/B Test Setup provides the complete framework for designing experiments that produce statistically valid, actionable results. Most A/B tests fail not because the variant was wrong, but because the test was poorly designed: wrong sample size, wrong metric, or someone peeked at results and stopped early. This skill prevents those mistakes.

---

## The Experiment Lifecycle

```
1. HYPOTHESIZE  →  2. DESIGN  →  3. CALCULATE  →  4. IMPLEMENT
       ↑                                                    │
       │                                                    ▼
7. ITERATE  ←  6. DOCUMENT  ←  5. ANALYZE  ←  [Run to completion]
```

---

## Step 1: Hypothesis Formulation

### The Hypothesis Template

```
Because [observation or data point],
we believe [specific change]
will cause [measurable outcome]
for [defined audience segment].

We'll know this is true when [primary metric] changes by [minimum detectable effect].
We'll watch [guardrail metrics] to ensure no negative impact.
```

### Good vs Bad Hypotheses

| Quality | Hypothesis | Problem |
|---------|-----------|---------|
| Bad | "Changing the button color might increase clicks" | No data basis, no target, no measurement plan |
| Mediocre | "A green button will get more clicks than blue" | No "why", no target size, no guardrails |
| Good | "Because heatmaps show 40% of users don't notice our CTA, making the button 2x larger with contrasting color will increase CTA clicks by 15%+ for new visitors. Guardrail: page load time stays under 2s." | Data-backed, specific change, measurable outcome, defined audience, guardrail |

### Hypothesis Sources (Where to Find Test Ideas)

| Source | What to Look For | Example |
|--------|-----------------|---------|
| Analytics data | Drop-off points, low-performing pages | "80% of users drop off at step 3 of onboarding" |
| User research | Confusion, frustration, unmet needs | "Users don't understand what the product does from the homepage" |
| Heatmaps/session recordings | Ignored elements, rage clicks | "Nobody scrolls past the fold on pricing page" |
| Support tickets | Recurring complaints, feature confusion | "Users constantly ask how to invite team members" |
| Competitor analysis | Different approaches to same problem | "Competitor uses a wizard; we use a form" |
| Sales objections | Common reasons prospects don't convert | "Prospects want to see pricing before signing up" |

---

## Step 2: Test Design

### Test Types

| Type | Variants | Traffic Need | Best For |
|------|----------|-------------|---------|
| A/B | 2 (control + 1 variant) | Moderate | Single change validation |
| A/B/n | 3+ variants | High | Comparing multiple approaches |
| Multivariate (MVT) | Combinations of changes | Very high | Optimizing multiple elements |
| Split URL | Different pages | Moderate | Major redesigns |
| Bandit | Dynamic allocation | Low-moderate | Revenue optimization |

**Default recommendation:** Standard A/B test. Only use A/B/n or MVT when you have enough traffic and a specific need.

### What to Test (By Impact)

| Category | High Impact | Medium Impact | Low Impact |
|----------|-----------|---------------|-----------|
| **Copy** | Headline/value prop, CTA text | Body copy, social proof | Microcopy, labels |
| **Design** | Page layout, above-fold content | Visual hierarchy, imagery | Color, font size |
| **UX** | Number of steps, form fields | Button placement, navigation | Animations, transitions |
| **Pricing** | Price point, plan names | Feature packaging, anchoring | Billing frequency display |
| **Social Proof** | Testimonials vs none, logos | Testimonial format, placement | Testimonial count |

### Metric Selection

Every test needs three types of metrics:

**Primary Metric (1 only)**
- The single metric that determines success
- Directly tied to the hypothesis
- Must be measurable within the test duration
- Examples: signup rate, click-through rate, purchase rate

**Secondary Metrics (2-3)**
- Explain why the primary metric moved
- Provide context for decision-making
- Examples: time on page, scroll depth, feature adoption rate

**Guardrail Metrics (1-3)**
- Things that must NOT get worse
- Stop the test if significantly negative
- Examples: error rate, support ticket volume, page load time, refund rate

---

## Step 3: Sample Size Calculation

### Quick Reference Table

Minimum visitors PER VARIANT needed (95% confidence, 80% power):

| Baseline Rate | 5% Lift | 10% Lift | 15% Lift | 20% Lift | 50% Lift |
|--------------|---------|----------|----------|----------|----------|
| 1% | 620,000 | 156,000 | 70,000 | 39,000 | 6,400 |
| 2% | 305,000 | 77,000 | 34,000 | 19,500 | 3,200 |
| 3% | 200,000 | 51,000 | 23,000 | 12,800 | 2,100 |
| 5% | 116,000 | 29,500 | 13,200 | 7,500 | 1,250 |
| 10% | 54,000 | 13,800 | 6,200 | 3,500 | 600 |
| 20% | 24,000 | 6,200 | 2,800 | 1,600 | 280 |
| 50% | 6,100 | 1,600 | 720 | 410 | 75 |

### Duration Calculation

```
Duration (days) = (Sample size per variant * Number of variants) / Daily traffic to test page
```

**Minimum duration:** 7 days (to capture day-of-week effects)
**Maximum recommended:** 6 weeks (beyond this, external factors contaminate results)

### What If You Don't Have Enough Traffic?

| Situation | Solution |
|-----------|----------|
| Need 100K visitors, get 5K/week | Increase minimum detectable effect (test bolder changes) |
| Very low traffic (<1K/week) | Use qualitative testing (user testing, surveys) instead |
| Medium traffic (5-20K/week) | Run for 4-6 weeks, test big changes only |
| High traffic (50K+/week) | You can test subtle changes, run multiple tests |

---

## Step 4: Implementation

### Client-Side Implementation

JavaScript modifies the page after initial render.

**Pros:** Quick to implement, no deploy needed
**Cons:** Can cause flicker (flash of original content), blocked by ad blockers
**Tools:** PostHog, Optimizely, VWO, Google Optimize

**Anti-flicker pattern:**
```javascript
// Add to <head> before any rendering
<style>.ab-test-hide { opacity: 0 !important; }</style>
<script>document.documentElement.classList.add('ab-test-hide');</script>

// In your test script (runs after variant assignment):
document.documentElement.classList.remove('ab-test-hide');
```

### Server-Side Implementation

Variant determined before page renders. No flicker, no client-side dependency.

**Pros:** No flicker, not blocked by ad blockers, works for logged-in features
**Cons:** Requires engineering work, deploy needed
**Tools:** PostHog, LaunchDarkly, Split, Unleash, custom feature flags

**Basic feature flag pattern:**
```python
# Server-side variant assignment
def get_variant(user_id: str, experiment: str) -> str:
    # Deterministic hash ensures same user always sees same variant
    hash_input = f"{user_id}:{experiment}"
    hash_value = hashlib.md5(hash_input.encode()).hexdigest()
    bucket = int(hash_value[:8], 16) % 100

    if bucket < 50:
        return "control"
    else:
        return "variant"
```

### Traffic Allocation

| Strategy | Split | When to Use |
|----------|-------|-------------|
| Standard | 50/50 | Default. Maximum statistical power. |
| Conservative | 90/10 or 80/20 | Risky changes, revenue-impacting tests |
| Ramped | Start 95/5, increase to 50/50 | New infrastructure, technical risk |

**Critical rules:**
- Users must see the same variant on every visit (sticky assignment by user ID or cookie)
- Allocation must be balanced across time of day and day of week
- Never change allocation mid-test

---

## Step 5: Running the Test

### Pre-Launch Checklist

- [ ] Hypothesis documented with primary metric and minimum detectable effect
- [ ] Sample size calculated, expected duration estimated
- [ ] Both variants implemented and QA'd on all device types
- [ ] Tracking verified (events fire correctly for both variants)
- [ ] No other tests running on the same page/feature
- [ ] Stakeholders informed of test duration and "no peeking" rule
- [ ] External factor calendar checked (no major launches, holidays, press)

### During the Test

**DO:**
- Monitor for technical errors (variant not rendering, tracking broken)
- Check that traffic split is balanced daily
- Document any external events that might affect results

**DO NOT:**
- Look at results before reaching sample size ("peeking problem")
- Make changes to either variant
- Add traffic from new sources mid-test
- Stop the test early because one variant "looks like it's winning"

### The Peeking Problem (Critical)

Looking at results before reaching the planned sample size and stopping because one variant looks better leads to a **25-40% false positive rate** (vs the intended 5%).

Why: Statistical significance fluctuates wildly with small samples. A variant can show p < 0.05 at 20% of planned sample size and p > 0.30 at full sample.

**Solutions:**
1. Pre-commit to sample size and do not check results until reached
2. If you must monitor: use sequential testing methods (group sequential design, always-valid p-values)
3. Set calendar reminder for expected completion date -- that is when you look

---

## Step 6: Analysis

### Analysis Checklist

1. **Did we reach planned sample size?** If not, results are preliminary only.
2. **Is it statistically significant?** p < 0.05 = 95% confidence the difference is real.
3. **What's the confidence interval?** Tells you the range of likely true effect.
4. **Is the effect size meaningful?** A 0.1% lift that's "significant" may not be worth implementing.
5. **Are secondary metrics consistent?** Do they support the primary result?
6. **Any guardrail violations?** Did anything get worse?
7. **Segment analysis:** Different results for mobile vs desktop? New vs returning?

### Interpreting Results

| Result | Primary Metric | Confidence | Action |
|--------|---------------|------------|--------|
| Clear winner | Variant +15%, p < 0.01 | High | Implement variant |
| Modest winner | Variant +5%, p < 0.05 | Medium | Implement if easy, else run longer |
| Flat | < 2% difference, p > 0.20 | High (no effect) | Keep control, test something bolder |
| Loser | Variant -10%, p < 0.05 | High | Keep control, investigate why |
| Inconclusive | 5% difference, p = 0.08 | Low | Need more traffic or bolder test |
| Mixed signals | Primary up, guardrail down | Investigate | Dig into segments, do not ship blindly |

### Common Analysis Mistakes

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Stopping at first significance | 25-40% false positive rate | Commit to sample size |
| Cherry-picking segments | Finding "winners" that don't replicate | Pre-register segments of interest |
| Ignoring confidence intervals | Overestimating effect size | Always report CI alongside p-value |
| Multiple comparisons | Inflated Type I error | Bonferroni correction for A/B/n |
| Survivorship bias | Only analyzing users who completed flow | Include all users from assignment point |
| Simpson's paradox | Aggregate hides segment reversal | Always check key segments |

---

## Step 7: Documentation

Every test must be documented, regardless of outcome.

### Test Documentation Template

```
EXPERIMENT: [Name]
DATE: [Start] to [End]
OWNER: [Name]

HYPOTHESIS:
Because [observation], we believed [change] would cause [outcome] for [audience].

VARIANTS:
- Control: [description]
- Variant: [description + screenshot]

METRICS:
- Primary: [metric] (baseline: [X]%, MDE: [Y]%)
- Secondary: [metrics]
- Guardrails: [metrics]

RESULTS:
- Sample size: [actual] / [planned]
- Duration: [X] days
- Primary metric: Control [X]% vs Variant [Y]% (p = [Z], CI: [range])
- Secondary metrics: [results]
- Guardrails: [all clear / violation noted]

DECISION: [Ship variant / Keep control / Iterate]

LEARNINGS:
- [What we learned about our users]
- [What we'd do differently next time]
```

---

## Experiment Prioritization Framework

### ICE Scoring

| Factor | Score (1-10) | Question |
|--------|-------------|----------|
| **Impact** | How much will this move the metric? | Big change to primary KPI = 10 |
| **Confidence** | How sure are we it will work? | Strong data supporting hypothesis = 10 |
| **Ease** | How easy is it to implement and measure? | Can ship in a day = 10 |

**ICE Score = (Impact + Confidence + Ease) / 3**

Rank all test ideas by ICE score. Run highest first.

### Test Backlog Template

| # | Hypothesis | Primary Metric | ICE | Est. Duration | Status |
|---|-----------|---------------|-----|---------------|--------|
| 1 | Larger CTA increases signups | Signup rate | 8.3 | 2 weeks | Ready |
| 2 | Social proof on pricing increases conversion | Plan selection rate | 7.0 | 3 weeks | Needs design |
| 3 | Shorter onboarding increases activation | Feature activation | 6.7 | 4 weeks | In backlog |

---

## Proactive Triggers

- Someone debates between two design options: propose an A/B test instead of opinionating
- Conversion rate mentioned as underperforming: offer to design a test, not guess at solutions
- Pricing page changes discussed: always test pricing changes with guardrail metrics
- Post-launch of any feature: propose follow-up experiment to optimize
- "Let's just try it and see": redirect to structured hypothesis before implementation

---

## Related Skills

| Skill | Use When |
|-------|----------|
| **analytics-tracking** | Setting up event tracking that feeds experiment metrics |
| **campaign-analytics** | Folding experiment results into broader attribution |
| **launch-strategy** | Testing within a product launch sequence |
| **prompt-engineer-toolkit** | A/B testing AI prompts in production |

---

## Tool Reference

### sample_size_calculator.py

Calculates required sample size per variant using the normal approximation to the two-proportion z-test. Includes Bonferroni correction for multi-variant tests and duration estimation.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--baseline`, `-b` | float | (required) | Baseline conversion rate (e.g. 0.05 for 5%) |
| `--mde`, `-m` | float | (required) | Minimum detectable effect as relative lift (e.g. 0.10 for 10%) |
| `--alpha`, `-a` | float | 0.05 | Significance level |
| `--power`, `-p` | float | 0.80 | Statistical power |
| `--variants`, `-v` | int | 2 | Number of variants including control |
| `--daily-traffic`, `-d` | int | 0 | Daily eligible traffic for duration estimation |
| `--one-tailed` | flag | False | Use one-tailed test instead of two-tailed |
| `--json` | flag | False | Output as JSON |

```bash
python scripts/sample_size_calculator.py --baseline 0.05 --mde 0.10
python scripts/sample_size_calculator.py --baseline 0.12 --mde 0.15 --power 0.9 --daily-traffic 5000
python scripts/sample_size_calculator.py --baseline 0.05 --mde 0.10 --variants 3 --json
```

### experiment_analyzer.py

Analyzes A/B test results using the two-proportion z-test with confidence intervals and segment breakdown.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `input` | positional | (required) | CSV file with results or "sample" to create sample |
| `--alpha`, `-a` | float | 0.05 | Significance level |
| `--json` | flag | False | Output as JSON |

**CSV format:** `variant,visitors,conversions,segment`

```bash
python scripts/experiment_analyzer.py sample
python scripts/experiment_analyzer.py results.csv
python scripts/experiment_analyzer.py results.csv --alpha 0.01 --json
```

### experiment_planner.py

Generates a structured experiment plan from a hypothesis text, including metric selection, sample size, timeline, risks, and documentation template.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--hypothesis`, `-H` | string | (required) | Experiment hypothesis text |
| `--baseline`, `-b` | float | 0.05 | Baseline conversion rate |
| `--mde`, `-m` | float | 0.10 | Minimum detectable effect as relative lift |
| `--daily-traffic`, `-d` | int | 0 | Daily eligible traffic |
| `--variants`, `-v` | int | 2 | Number of variants including control |
| `--json` | flag | False | Output as JSON |

```bash
python scripts/experiment_planner.py --hypothesis "Larger CTA will increase signups by 15%"
python scripts/experiment_planner.py -H "Simplified checkout boosts conversions" -b 0.08 -m 0.15 -d 3000
python scripts/experiment_planner.py -H "New pricing page" --json
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Sample size is unrealistically large | MDE too small or baseline too low | Increase MDE (test bolder changes) or target a higher-traffic page |
| Test duration exceeds 6 weeks | Insufficient daily traffic | Consider qualitative methods, test bigger changes, or combine traffic from multiple pages |
| p-value hovers around 0.05 | Borderline significance | Do not stop early; run to planned sample size or extend 20% |
| Results significant but lift is tiny (<1%) | Overpowered test | Check practical significance alongside statistical significance |
| Segment results contradict overall | Simpson's paradox | Investigate segment composition; report both overall and segment results |
| Variant performs differently on mobile vs desktop | Device-specific UX issues | Design device-specific variants; increase per-segment sample size |
| Calculator produces negative CI | Very small samples or extreme rates | Ensure sufficient sample size; check data integrity |

---

## Success Criteria

| Criterion | Target | How to Measure |
|-----------|--------|----------------|
| Tests reach planned sample size | 100% of tests | Compare actual vs planned sample at conclusion |
| False positive rate | <5% | Track post-implementation lift vs test prediction |
| Test velocity | 2+ tests per team per month | Count experiments documented per sprint |
| Documentation completeness | 100% of tests documented | Audit experiment records quarterly |
| Average test duration | <4 weeks | Measure start-to-conclusion calendar days |
| Decision quality | >80% of shipped variants hold gains at 90 days | Post-ship metric tracking |

---

## Scope & Limitations

**In scope:**
- Hypothesis formulation and validation
- Sample size and power calculations
- Frequentist two-proportion z-tests
- A/B, A/B/n, and split URL test planning
- Segment-level analysis
- Pre/post test documentation

**Out of scope:**
- Bayesian A/B testing methods (use dedicated Bayesian tools)
- Multi-armed bandit algorithms (require real-time allocation infrastructure)
- Multivariate testing (MVT) analysis (combinatorial explosion requires specialized tools)
- Server-side feature flag implementation (see engineering skills)
- Revenue-based metrics requiring transaction-level data
- Sequential testing / always-valid p-values (use Optimizely Stats Engine or similar)

---

## Integration Points

| Tool / Platform | Integration Method | Use Case |
|-----------------|-------------------|----------|
| PostHog / Amplitude | JSON export from experiment_analyzer | Feed results into product analytics |
| Jira / Linear | experiment_planner JSON output | Create experiment tickets with metadata |
| Google Sheets | CSV export from experiment_analyzer | Share results with non-technical stakeholders |
| LaunchDarkly / Unleash | experiment_planner checklist | Pre-launch validation before feature flag rollout |
| Slack / Notion | Copy human-readable output | Async experiment status updates |
| CI/CD pipelines | `--json` flag on all scripts | Automated experiment health checks |
