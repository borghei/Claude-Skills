---
name: churn-prevention
description: >
  SaaS churn reduction covering cancel flow design, dynamic save offers, exit
  survey architecture, dunning sequences, payment recovery, win-back campaigns,
  and churn impact modeling.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-growth
  updated: 2026-03-31
  tags: [churn, retention, cancel-flow, dunning, payment-recovery, win-back]
---
# Churn Prevention

Production-grade SaaS churn reduction framework covering cancel flow architecture, dynamic save offer mapping, exit survey design, dunning sequence engineering, payment recovery optimization, win-back campaigns, and churn impact modeling. Addresses both voluntary churn (customers who decide to leave) and involuntary churn (customers who leave due to payment failure).

---

## Table of Contents

- [Initial Assessment](#initial-assessment)
- [Churn Taxonomy](#churn-taxonomy)
- [Cancel Flow Architecture](#cancel-flow-architecture)
- [Exit Survey Design](#exit-survey-design)
- [Dynamic Save Offer System](#dynamic-save-offer-system)
- [Dunning Sequence Engineering](#dunning-sequence-engineering)
- [Win-Back Campaign Framework](#win-back-campaign-framework)
- [Churn Health Scoring](#churn-health-scoring)
- [Metrics and Benchmarks](#metrics-and-benchmarks)
- [Churn Impact Calculator](#churn-impact-calculator)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Initial Assessment

### Required Context

| Question | Why It Matters |
|----------|---------------|
| Current monthly churn rate? (voluntary vs involuntary split) | Determines which lever to pull |
| Do you have a cancel flow, or is cancellation instant/via support? | Determines build vs optimize mode |
| What payment processor? (Stripe, Braintree, Paddle) | Affects dunning implementation |
| Average contract value and billing cycle? | Sizes the save offer budget |
| Current MRR? | Calculates the dollar impact of churn reduction |
| SaaS model? (self-serve vs sales-assisted) | Determines intervention type |
| Do you collect exit reasons today? | Data availability for save offer mapping |

---

## Churn Taxonomy

### Voluntary Churn (Customer Decides to Leave)

| Type | Signal | Addressable? |
|------|--------|-------------|
| Value gap | Not getting enough value for the price | Yes -- save offers, feature education |
| Product-market mismatch | Wrong ICP, product does not fit their use case | Partially -- downgrade or pivot |
| Competitor switch | Found a better alternative | Yes -- competitive counter-offers |
| Budget cut | Cannot afford it anymore | Yes -- discount or pause |
| Project completion | Seasonal or project-based need | Yes -- pause option |
| Poor experience | Bad support, bugs, frustration | Yes -- human intervention |
| Never activated | Signed up, never used it | Partially -- reactivation before cancel |

### Involuntary Churn (Payment Fails)

| Cause | % of Failed Payments | Recoverable? |
|-------|---------------------|-------------|
| Expired card | 40-50% | Yes -- card updater service |
| Insufficient funds | 20-30% | Yes -- smart retry timing |
| Bank decline (fraud flag) | 10-15% | Sometimes -- customer must contact bank |
| Account closed | 5-10% | No -- customer must provide new card |
| Network error | 5-10% | Yes -- automatic retry |

---

## Cancel Flow Architecture

### The 5-Stage Cancel Flow

```
[Cancel Button] → [Exit Survey] → [Dynamic Save Offer] → [Confirmation] → [Post-Cancel]
```

### Stage 1: Cancel Trigger

- Cancel option is findable (Settings > Account > Cancel). Do not hide it.
- Clicking "Cancel" starts the flow -- it does not immediately cancel the account
- Works on both desktop and mobile

### Stage 2: Exit Survey (Required, 1 Question)

**Question:** "What is the main reason you are cancelling?"

Present as radio buttons (not a dropdown). Maximum 8 options:

| Reason | Internal Code |
|--------|--------------|
| Too expensive for the value I get | PRICE |
| Not using it enough | LOW_USAGE |
| Missing a feature I need | MISSING_FEATURE |
| Switching to a different product | COMPETITOR |
| My project or need ended | PROJECT_END |
| Too complicated to use | COMPLEXITY |
| Just testing, did not plan to keep it | TESTING |
| Other (with optional text field) | OTHER |

**Rules:**
- Survey is required before showing the save offer (the answer determines the offer)
- One question only. No multi-page surveys.
- Optional free-text field for "Other" and as a supplement to any selection
- Track response distribution monthly to identify systemic issues

### Stage 3: Dynamic Save Offer

**Map each exit reason to exactly one save offer:**

| Exit Reason | Save Offer | Offer Copy |
|------------|-----------|------------|
| PRICE | 30-50% discount for 2-3 months | "We'd like to offer you [X]% off for the next [N] months" |
| LOW_USAGE | Pause account for 1-3 months | "Pause your account and come back when you need it" |
| MISSING_FEATURE | Roadmap preview + workaround | "[Feature] is coming in [Q]. Here's how to achieve it now" |
| COMPETITOR | Competitive comparison + discount | "Here's how we compare to [competitor]. Plus [X]% off" |
| PROJECT_END | Pause option | "Pause instead of cancel -- your data stays safe" |
| COMPLEXITY | Free onboarding session | "Let us set it up for you -- free 30-min session with our team" |
| TESTING | No offer -- let them go | "Thanks for trying us out. You're welcome back anytime." |
| OTHER | General retention offer | "Before you go -- we'd love to make this right. [Contact support]" |

**Offer presentation rules:**
- One clear offer per screen (not multiple choices)
- Quantify the value: "Save $120 over the next 3 months" not "Get a discount"
- CTA: "Accept Offer" vs "Continue Cancelling" (both clearly labeled)
- No countdown timers, no fake urgency
- No guilt-trip copy

### Stage 4: Confirmation

If they decline the save offer or there is no offer to make:

```
┌────────────────────────────────────────┐
│  We're sorry to see you go             │
│                                        │
│  What happens when you cancel:         │
│  - Your data is saved for 90 days     │
│  - Access continues until [date]      │
│  - You can reactivate anytime         │
│                                        │
│  [Yes, Cancel My Account]             │
│  [Wait, I Changed My Mind]            │
│                                        │
│  No pre-checked boxes.                │
│  No confusing language.               │
└────────────────────────────────────────┘
```

### Stage 5: Post-Cancel

| Timing | Channel | Message |
|--------|---------|---------|
| Immediately | Email | Cancellation confirmation + data retention policy + reactivation link |
| Day 7 | Email | "We miss you" + single CTA to reactivate + what they are missing |
| Day 30 | Email | Product update + relevant improvement + reactivation offer |
| Day 60 | Email | Final win-back with strongest offer (if applicable) |

---

## Exit Survey Design

### Data Analysis Framework

Track exit survey responses monthly and calculate:

| Metric | Formula | Action Threshold |
|--------|---------|-----------------|
| Reason distribution | % of cancels per reason | Any reason > 30% = systemic issue |
| Save rate by reason | Saved / Cancel attempts per reason | Any reason < 5% save rate = wrong offer |
| Reason trend | Month-over-month change | Increasing trend = worsening problem |
| Feature gap frequency | Count of "missing feature" with specific feature named | Top 3 missing features = product roadmap input |

### Competitive Intelligence from Exit Surveys

When users select "Switching to a different product":

- Ask a follow-up: "Which product are you switching to?" (optional, free text or dropdown)
- Track the top 3 competitors winning your churners
- Feed this data into competitive-teardown skill for quarterly analysis

---

## Dynamic Save Offer System

### Offer Economics

| Offer Type | Cost to Business | Save Rate Benchmark | When Profitable |
|-----------|-----------------|---------------------|----------------|
| 30% discount (3 months) | 30% of 3 months revenue | 15-25% | If LTV after save > discount cost |
| 50% discount (2 months) | 50% of 2 months revenue | 20-30% | If retained customer stays 6+ months |
| Pause (1-3 months) | $0 (no revenue during pause) | 25-40% | If 50%+ reactivate after pause |
| Free onboarding session | CS team time (~$50-100) | 10-20% | If ARPU > $100/month |
| Downgrade to lower tier | Revenue reduction | 30-50% | If some revenue > no revenue |
| Feature unlock | $0 (already built) | 5-15% | Always profitable |

### Save Offer Decision Tree

```
User selects exit reason →
├── PRICE →
│   ├── Customer ARPU > median? → Offer 30% discount
│   └── Customer ARPU < median? → Offer downgrade to cheaper plan
├── LOW_USAGE →
│   ├── Last login > 30 days? → Offer pause
│   └── Last login < 30 days? → Offer usage tips + discount
├── MISSING_FEATURE →
│   ├── Feature on roadmap? → Share roadmap + workaround
│   └── Feature not planned? → Offer discount or acknowledge gap
├── COMPETITOR →
│   ├── Known competitor? → Show comparison + retention offer
│   └── Unknown competitor? → General retention offer
├── PROJECT_END →
│   └── Always → Offer pause
├── COMPLEXITY →
│   ├── Enterprise/high-value? → Offer dedicated onboarding session
│   └── SMB/low-value? → Offer guided tutorial link
└── TESTING →
    └── Always → No offer, let go gracefully
```

---

## Dunning Sequence Engineering

Failed payments cause 20-40% of total churn. Most of it is recoverable with proper dunning.

### Smart Retry Schedule

Do not retry immediately after failure. Cards often recover within 3-7 days.

| Retry | Timing | Why This Timing |
|-------|--------|-----------------|
| Initial charge | Day 0 | Normal billing cycle |
| Retry 1 | Day 3 | Most card issues resolve within 72 hours |
| Retry 2 | Day 7 | Paycheck cycle alignment |
| Retry 3 | Day 12 | Second paycheck cycle |
| Retry 4 | Day 18 | Final attempt before service action |
| Service action | Day 21 | Downgrade or cancel |

### Card Updater Services

Enable automatic card updating to prevent expired card churn:

| Processor | Service | How to Enable |
|-----------|---------|---------------|
| Stripe | Automatic card updates | Enabled by default on most plans |
| Braintree | Account Updater | Must enable in merchant settings |
| Paddle | Built-in | Automatic |
| Recurly | Account Updater | Configuration required |

### Dunning Email Sequence

| Day | Subject Line | Body Focus | CTA |
|-----|-------------|-----------|-----|
| 0 | "Your [Product] payment didn't go through" | Factual, no blame. Card may be expired or funds unavailable. | [Update Payment Method] |
| 3 | "Action needed: update your payment for [Product]" | Remind what they will lose access to. | [Update Payment Method] |
| 7 | "Your [Product] account is at risk" | List features/data they have created. Mild urgency. | [Update Payment Method] |
| 14 | "Final notice: your [Product] access ends in 7 days" | Clear deadline. Offer to help if bank issue. | [Update Payment Method] + [Contact Support] |
| 21 | "Your [Product] account has been paused" | Account status change. Data is safe. Easy reactivation. | [Reactivate Account] |

**Email rules:**
- Every email links directly to the payment update page (not the dashboard)
- No guilt, no shame. Card failures happen.
- Subject lines are specific (include product name)
- Include the amount owed and the card last 4 digits
- Offer a support channel for customers who need help

---

## Win-Back Campaign Framework

### Win-Back Timing

| Window | Success Rate | Approach |
|--------|-------------|---------|
| Day 7 post-cancel | 5-10% | Gentle reminder, no pressure |
| Day 30 post-cancel | 3-7% | Product update + offer |
| Day 60 post-cancel | 2-5% | Strongest offer + fresh start |
| Day 90+ post-cancel | 1-3% | Major product change only |

### Win-Back Email Sequence

**Day 7 Email:**
- Subject: "Your [Product] account is waiting for you"
- Body: What they left behind (data, projects, team). One CTA: reactivate.
- No discount. Just value reminder.

**Day 30 Email:**
- Subject: "Here's what's new in [Product]"
- Body: 2-3 specific improvements since they left. One CTA: reactivate.
- Small incentive: "Come back with 1 month free"

**Day 60 Email:**
- Subject: "We'd love to have you back -- [offer]"
- Body: Strongest offer (50% off 3 months or extended free period). Clear deadline.
- Final significant outreach attempt.

---

## Churn Health Scoring

### Leading Indicators of Churn

| Signal | Weight | Detection |
|--------|--------|-----------|
| Login frequency declining (week over week) | High | Usage analytics |
| Feature usage dropping | High | Feature event tracking |
| Support ticket escalation | High | Help desk data |
| NPS response < 7 | High | Survey data |
| Invoice dispute or payment question | Medium | Billing system |
| Champion left the company | High | Contact monitoring |
| Contract renewal in < 90 days | Medium | CRM data |
| Competitor evaluation detected | High | Sales intelligence |

### Risk Score Calculation

```
Risk Score = Sum of (Signal Weight x Signal Present)

0-20: Low risk (monitor)
21-40: Moderate risk (proactive outreach)
41-60: High risk (intervention required)
61+: Critical risk (executive escalation)
```

---

## Metrics and Benchmarks

### Key Metrics

| Metric | Formula | Good | Excellent |
|--------|---------|------|-----------|
| Save rate | Customers saved / Cancel attempts | 10-15% | 20%+ |
| Voluntary churn rate | Voluntary cancels / Total customers (monthly) | < 3% | < 1.5% |
| Involuntary churn rate | Failed payment cancels / Total customers (monthly) | < 1.5% | < 0.5% |
| Payment recovery rate | Failed payments recovered / Total failed | 25-35% | 40%+ |
| Win-back rate | Reactivations / Cancellations (90-day window) | 5-10% | 10%+ |
| Exit survey completion rate | Surveys completed / Cancel attempts | > 70% | > 90% |
| Save offer acceptance rate | Offers accepted / Offers shown | 15-25% | 30%+ |

### Red Flags

| Signal | Diagnosis | Action |
|--------|-----------|--------|
| Save rate < 5% | Offers not matching reasons | Rebuild offer-reason mapping |
| Exit survey completion < 60% | Survey too long or optional | Make it required, 1 question |
| Recovery rate < 20% | Retry logic or emails broken | Audit dunning sequence |
| Single reason > 40% | Systemic product/pricing issue | Escalate to product/leadership |
| Churn rate > 5% monthly | Business is likely contracting | Churn prevention alone will not fix; review ICP + product |

---

## Churn Impact Calculator

### Quick Estimate

```
Monthly MRR at risk = Total MRR x Monthly churn rate
Annual MRR saved by 1% churn reduction = Total MRR x 0.01 x 12
Annual MRR saved by 20% save rate = (Monthly MRR at risk x 0.20) x 12

Example:
  MRR: $500,000
  Monthly churn: 4% = $20,000/month lost
  Reduce to 3% = $5,000/month saved = $60,000/year
  Add 20% save rate on remaining = $3,000/month saved = $36,000/year
  Total annual impact: $96,000
```

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Cancel Flow Design | 5-stage flow with copy | Complete flow from trigger to post-cancel |
| Exit Survey | Radio button options + mapping | 6-8 reasons with save offer mapping |
| Save Offer System | Decision tree | Reason-to-offer mapping with economics |
| Dunning Sequence | 5-email sequence | Subject lines, body copy, timing, retry schedule |
| Win-Back Campaign | 3-email sequence | Day 7, 30, 60 emails with subject lines and offers |
| Churn Scorecard | Metric table | Current metrics vs benchmarks with gap analysis |
| Impact Model | Revenue calculation | Dollar impact of churn reduction at various improvement levels |

---

## Related Skills

- **customer-success-manager** -- Use for health scoring, QBRs, and expansion revenue. Not for cancel flow or dunning design.
- **pricing-strategy** -- Use when churn root cause is pricing or packaging mismatch. Not for save offer design.
- **onboarding-cro** -- Use when churn traces back to poor activation. If users never experienced value, fix onboarding first.
- **referral-program** -- Use for acquisition. Churn prevention handles the other end of the funnel.

---

## Tool Reference

### 1. churn_impact_calculator.py

**Purpose:** Calculate the revenue impact of churn reduction at various improvement levels.

```bash
python scripts/churn_impact_calculator.py --mrr 500000 --churn-rate 4.0 --save-rate 20
python scripts/churn_impact_calculator.py --mrr 500000 --churn-rate 4.0 --save-rate 20 --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `--mrr` | Yes | Current monthly recurring revenue in dollars |
| `--churn-rate` | Yes | Current monthly churn rate as percentage (e.g., 4.0 for 4%) |
| `--save-rate` | No | Cancel flow save rate as percentage (default: 15) |
| `--target-churn` | No | Target churn rate as percentage (default: current minus 1) |
| `--json` | No | Output results as JSON |

### 2. dunning_sequence_analyzer.py

**Purpose:** Analyze dunning email sequence effectiveness and recommend retry timing optimizations.

```bash
python scripts/dunning_sequence_analyzer.py dunning_data.json
python scripts/dunning_sequence_analyzer.py dunning_data.json --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `dunning_data.json` | Yes | JSON file with failed payment and retry data |
| `--json` | No | Output results as JSON |

**Input JSON format:**
```json
{
  "failed_payments": [
    {
      "payment_id": "PAY-001",
      "amount": 99.00,
      "failure_reason": "expired_card",
      "retry_attempts": [
        {"day": 0, "recovered": false},
        {"day": 3, "recovered": false},
        {"day": 7, "recovered": true}
      ]
    }
  ]
}
```

### 3. exit_survey_analyzer.py

**Purpose:** Analyze exit survey responses to identify churn patterns, save offer effectiveness, and systemic issues.

```bash
python scripts/exit_survey_analyzer.py survey_data.json
python scripts/exit_survey_analyzer.py survey_data.json --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `survey_data.json` | Yes | JSON file with exit survey response data |
| `--json` | No | Output results as JSON |
| `--period` | No | Analysis period label (default: "current") |

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Save rate below 5% across all reasons | Save offers do not match exit reasons | Rebuild the exit-reason-to-offer mapping using survey data; run exit_survey_analyzer.py to identify mismatches |
| Exit survey completion under 60% | Survey is optional or too long | Make the single-question survey required before showing the save offer; remove multi-page flows |
| Payment recovery rate below 20% | Retry logic misconfigured or dunning emails not sending | Audit dunning sequence with dunning_sequence_analyzer.py; verify email deliverability and retry schedule |
| Single exit reason exceeds 40% of responses | Systemic product or pricing issue | Escalate to product or leadership; this is not solvable with cancel flow alone |
| Churn rate above 5% monthly | Likely ICP, product-market fit, or pricing problem | Churn prevention alone will not fix this; pair with pricing-strategy and product feedback loops |
| Win-back emails have zero reactivations | Emails not reaching inbox or offers are weak | Check deliverability (SPF, DKIM, DMARC); test stronger offers; verify reactivation links work |
| Involuntary churn rising while voluntary is stable | Card updater not enabled or retry timing is poor | Enable automatic card updating on your payment processor; review retry schedule in dunning_sequence_analyzer.py |

---

## Success Criteria

- Monthly voluntary churn rate below 2.5% (below 1.5% is excellent)
- Monthly involuntary churn rate below 1.0% (below 0.5% is excellent)
- Cancel flow save rate of 15-25% (above 20% is excellent)
- Payment recovery rate of 30%+ on failed payments
- Exit survey completion rate above 80%
- Win-back reactivation rate of 5-10% within 90 days post-cancel
- Save offer acceptance rate above 20% with retained customers staying 6+ months post-save

---

## Scope & Limitations

- **In scope:** Cancel flow design, exit survey architecture, save offer mapping, dunning sequences, payment recovery, win-back campaigns, churn impact modeling
- **Out of scope:** Product-market fit analysis, pricing restructuring, ICP redefinition, customer acquisition
- **Data dependency:** Scripts analyze point-in-time snapshots from JSON input; no real-time CRM integration
- **Not predictive ML:** All scoring is deterministic and algorithmic -- no machine learning models
- **Legal note:** Cancel flows must comply with FTC guidelines (US) and consumer protection laws (EU) -- do not make cancellation unreasonably difficult
- **Revenue estimates:** Impact calculations are projections based on input assumptions, not guarantees

---

## Integration Points

- **customer-success-manager** -- Feed health scores into churn risk assessment; use churn data to calibrate health score thresholds
- **pricing-strategy** -- When exit survey data shows PRICE as the dominant reason (>30%), escalate to pricing-strategy for structural pricing review
- **onboarding-cro** -- When exit survey data shows LOW_USAGE or COMPLEXITY as top reasons, the root cause is often poor activation; fix onboarding first
- **revenue-operations** -- Pipeline and forecast models should account for churn reduction impact on net revenue retention (NRR)
- **referral-program** -- Retained customers from save offers are candidates for referral program enrollment after 90 days of continued usage
