# Experiment Methods Reference

## Pretotyping (Alberto Savoia)

Pretotyping is the practice of testing the initial appeal and actual usage of a potential new product by simulating its core experience with the smallest possible investment of time and money.

### The Pretotyping Manifesto

1. **Make sure you are building The Right It before you build It right.**
2. Most new products fail -- even when well executed -- because they are the wrong product.
3. The biggest risk is not "Can we build it?" but "Should we build it?"
4. Your opinion, although interesting, is irrelevant. Test it.
5. Data beats opinions. Your Own Data beats others' data.

### Pretotype Types

| Pretotype | Description | Example |
|-----------|-------------|---------|
| **Mechanical Turk** | Replace complex technology with human effort behind the scenes | A "smart" recommendation engine that is actually a person curating results |
| **Pinocchio** | Build a non-functional physical or digital shell | A 3D-printed hardware device with no electronics inside, shown to potential buyers |
| **Minimum Viable Product** | Smallest functional version that delivers core value | A spreadsheet-based tool before building a web app |
| **Provincial** | Launch in a single small market before expanding | Test a delivery service in one neighborhood |
| **Fake Door** | Advertise a feature that does not exist; measure interest | "Premium Analytics" button that leads to a waitlist form |
| **Impersonator** | Rebrand an existing product to test a new market | Use an existing project management tool repackaged for a new industry |
| **Infiltrator** | Place your product in an existing channel to test demand | Sell your product on an existing marketplace before building your own |
| **Re-label** | Put a new label on an existing product to test demand for the concept | A generic protein bar rebranded as "Developer Fuel" |

---

## Lean Experiment Types Catalog

### Discovery Experiments (Testing Demand)

**Landing Page Test**
- **Setup:** Single page with value proposition, benefits, and a CTA.
- **CTA options:** Sign up for waitlist, pre-order, request demo.
- **Traffic source:** Paid ads, social media, email to target segment.
- **Key metric:** Conversion rate (visitors to CTA).
- **Duration:** 1-2 weeks.
- **Cost:** Low (domain + hosting + ad spend).

**Explainer Video Test**
- **Setup:** 60-90 second video explaining the product concept.
- **Distribution:** Landing page, social media, email.
- **Key metric:** Watch completion rate + CTA conversion.
- **Duration:** 1-2 weeks.
- **Tips:** Keep production simple. Screen recordings or animations work fine.

**Pre-Order / Crowdfunding**
- **Setup:** Accept payment (or a deposit) for a product that does not exist yet.
- **Key metric:** Number of orders or total revenue.
- **Duration:** 2-4 weeks.
- **Strongest SITG signal:** People commit real money.

**Concierge MVP**
- **Setup:** Deliver the service manually to a small number of users.
- **Key metric:** Retention, satisfaction, willingness to pay after manual service.
- **Duration:** 2-4 weeks.
- **Tips:** Do not tell users it is manual. Observe whether they value the outcome regardless of delivery method.

### Validation Experiments (Testing Solutions)

**Fake Door Test**
- **Setup:** Add a button, menu item, or link for a feature that does not exist. When clicked, show a message: "Coming soon! Sign up to be notified."
- **Key metric:** Click-through rate on the fake door element.
- **Duration:** 1-2 weeks.
- **Ethical note:** Be transparent. Show a message immediately; do not leave users confused.

**Feature Stub**
- **Setup:** Build a minimal, mostly static version of the feature behind a feature flag.
- **Key metric:** Engagement rate, completion rate, or adoption rate.
- **Duration:** 1-2 weeks.
- **Tips:** The stub can be a mockup, a simplified version, or a wizard-style flow.

**A/B Test**
- **Setup:** Randomly assign users to control (current experience) or variant (new experience). Measure a primary metric.
- **Key metric:** Depends on what you are testing (conversion rate, retention, engagement).
- **Duration:** 2-4 weeks (until statistical significance).
- **Requirements:** Sufficient traffic volume, proper randomization, no peeking.

**Wizard of Oz**
- **Setup:** The feature appears fully automated to the user, but a human operates it behind the scenes.
- **Key metric:** Same as if the feature were real (engagement, satisfaction, conversion).
- **Duration:** 2-4 weeks.
- **Tips:** Good for testing AI/ML features before building the model.

**In-App Survey**
- **Setup:** Trigger a survey for users who match specific behavioral criteria.
- **Key metric:** Response rate + stated preference distribution.
- **Duration:** 1 week.
- **Limitations:** Low SITG. Use only when behavioral experiments are impractical.

---

## Metric Selection Guide

### Choosing the Right Primary Metric

| What You Are Testing | Recommended Metric | Why |
|---------------------|-------------------|-----|
| Demand / interest | Conversion rate (visitor to sign-up/pre-order) | Measures real commitment, not page views |
| Engagement | Feature adoption rate or DAU/MAU ratio | Shows whether users return to the feature |
| Willingness to pay | Pre-order conversion or pricing page engagement | SITG: money is the strongest signal |
| Usability | Task completion rate or time-to-complete | Directly measures whether users can use it |
| Retention | Day-7 or Day-30 retention rate | Shows long-term value, not novelty |

### Setting the Success Threshold

The threshold must be set **before** the experiment starts.

**Framework for setting thresholds:**

1. **Baseline**: What is the current metric value (if applicable)?
2. **Minimum viable**: What is the minimum result that justifies further investment?
3. **Aspiration**: What result would signal strong product-market fit?

Example: Current trial-to-paid conversion is 8%. A new onboarding flow experiment sets:
- **Threshold (pass):** 10% (25% improvement over baseline)
- **Aspiration:** 14%+
- **Fail:** Below 10%

---

## Sample Size Considerations

### When Sample Size Matters

- **A/B tests**: Require statistical significance. Use a sample size calculator.
- **Landing page tests**: Directional signal is often sufficient with 200-500 visitors.
- **Fake door tests**: 1,000+ impressions of the element for reliable click-through rates.
- **Concierge MVP**: 5-15 users is sufficient for qualitative signal.

### Quick Sample Size Rules of Thumb

| Desired Precision | Minimum Sample per Variant |
|-------------------|---------------------------|
| Directional (rough signal) | 100-200 |
| Moderate confidence | 500-1,000 |
| High confidence (p < 0.05) | 1,000-5,000+ (depends on effect size) |

For precise calculations, use an online sample size calculator with your baseline rate and minimum detectable effect.

---

## Common Pitfalls

### 1. Testing the Solution Before the Problem
Run problem-validation experiments (interviews, surveys) before solution-validation experiments (prototypes, A/B tests).

### 2. No Clear Hypothesis
"Let's see what happens" is not an experiment. Every experiment needs an XYZ hypothesis with a pre-set threshold.

### 3. Peeking at Results
Checking results daily and stopping early when they look good inflates false positive rates. Set a duration and stick to it.

### 4. Confusing Correlation with Causation
Only randomized experiments (A/B tests) establish causation. Observational data (analytics) shows correlation.

### 5. Testing Too Many Variables
Change one thing at a time. Multi-variable tests require exponentially more sample size.

### 6. Ignoring Guardrail Metrics
A variant that improves sign-ups but degrades retention is not a win. Always monitor guardrails.

### 7. Survivorship Bias in Concierge Tests
Concierge users who stick around may not represent the broader population. Be cautious generalizing from small, self-selected samples.

### 8. Over-Reliance on Surveys
Surveys measure stated preference, not revealed preference. People say they want features they will never use. Prefer behavioral experiments.
