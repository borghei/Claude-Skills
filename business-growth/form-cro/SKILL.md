---
name: form-cro
description: >
  Form optimization for lead capture, contact, demo request, application, and
  checkout forms. Covers field-cost analysis, multi-step form design, validation
  UX, mobile optimization, and A/B testing frameworks.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-growth
  updated: 2026-03-31
  tags: [cro, forms, lead-capture, conversion-optimization, ux]
---
# Form CRO

Production-grade form optimization framework covering field-cost analysis, layout engineering, multi-step form architecture, validation UX patterns, mobile-specific optimization, and structured A/B test design. Applicable to lead capture, contact, demo request, application, survey, and checkout forms. For signup/registration flows, use signup-flow-cro.

---

## Table of Contents

- [Initial Assessment](#initial-assessment)
- [Field-Cost Analysis Framework](#field-cost-analysis-framework)
- [Multi-Step vs Single-Step Decision](#multi-step-vs-single-step-decision)
- [Field Design Patterns](#field-design-patterns)
- [Validation UX](#validation-ux)
- [CTA and Submit Button Optimization](#cta-and-submit-button-optimization)
- [Mobile Form Optimization](#mobile-form-optimization)
- [Trust and Context Elements](#trust-and-context-elements)
- [Form Type Playbooks](#form-type-playbooks)
- [A/B Test Framework](#ab-test-framework)
- [Metrics and Measurement](#metrics-and-measurement)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Initial Assessment

### Required Context

| Question | Why It Matters |
|----------|---------------|
| What type of form? (lead capture, contact, demo, application, checkout) | Different types have different optimal field counts |
| How many fields currently? | Establishes baseline friction level |
| What is the current completion rate? | Benchmark for improvement |
| Where do users abandon? (if field-level analytics exist) | Identifies the specific friction point |
| Mobile vs desktop split? | Mobile forms need separate optimization |
| What happens with submitted data? | Determines which fields are truly necessary |
| Which fields are actually used in follow-up? | Often reveals 30-50% of fields are never used |
| Any compliance requirements? (GDPR, HIPAA) | Constrains what can be removed |

---

## Field-Cost Analysis Framework

Every field has a cost measured in abandonment. The question is not "what data would be nice to have" but "what data is worth the conversion loss."

### Field Cost Matrix

| Field Type | Estimated Abandonment Cost | Justification Threshold |
|-----------|---------------------------|------------------------|
| Email | Baseline (near zero for gated content) | Always justified for lead forms |
| First name | +2-3% drop | Justified if personalization drives follow-up |
| Last name | +2-3% drop | Rarely justified for first touch |
| Phone number | +5-10% drop | Only if sales will call within 24 hours |
| Company name | +3-5% drop | Justified for B2B qualification |
| Company size | +3-5% drop | Justified only if routing decisions depend on it |
| Job title | +3-5% drop | Can often be enriched post-submission |
| Industry | +2-3% drop | Can often be enriched post-submission |
| Message/textarea | +5-8% drop | Justified for contact forms, not for lead capture |
| Budget | +8-12% drop | Only justified for high-intent demo/sales forms |
| Custom question | +3-5% per question | Must directly affect lead routing or qualification |

### The Enrichment Test

Before including any field, ask: **Can this be enriched after submission?**

| Field | Enrichable? | Method | Keep in Form? |
|-------|------------|--------|---------------|
| Company name | Yes (from email domain) | Clearbit, Apollo, manual lookup | Remove |
| Company size | Yes (from company name) | Enrichment API | Remove |
| Industry | Yes (from company name) | Enrichment API | Remove |
| Job title | Partially (from LinkedIn) | Manual enrichment | Remove unless critical for routing |
| Phone number | No | Must be provided | Keep only if sales calls immediately |
| Budget | No | Must be stated | Keep only for high-intent forms |

### Recommended Field Sets by Form Type

| Form Type | Minimum Fields | Optimal Fields | Maximum Fields |
|-----------|---------------|----------------|----------------|
| Newsletter signup | Email | Email | Email + First name |
| Content download | Email | Email + First name | Email + Name + Company |
| Contact form | Email + Message | Email + Name + Message | Email + Name + Subject + Message |
| Demo request | Email + Company | Email + Name + Company + Role | + Phone + Use case + Team size |
| Application form | Varies by requirement | -- | All required fields (justified individually) |

---

## Multi-Step vs Single-Step Decision

### Decision Criteria

| Factor | Single-Step | Multi-Step |
|--------|------------|------------|
| Total fields | < 5 fields | > 5 fields |
| Field complexity | Simple text inputs | Mix of dropdowns, checkboxes, conditional fields |
| User motivation | Low-commitment (newsletter, content) | High-commitment (demo, application) |
| Qualification need | No routing needed | Different paths based on answers |
| Mobile proportion | < 30% mobile | > 50% mobile |

### Multi-Step Best Practices

**Step structure:**
- Step 1: Easiest fields (email, name) -- lowest friction to start
- Step 2: Qualifying information (company, role, use case)
- Step 3: Specific details (budget, timeline, message)

**Progress indication:**
- Show progress bar with step count ("Step 2 of 3")
- Show completion percentage
- Label each step with what it covers ("Your Details", "Company Info", "Project Details")

**Psychological commitment:**
- Once a user completes Step 1, they are 40-60% more likely to complete the form (sunk cost effect)
- Capture the email in Step 1 so you can follow up even if they abandon later

**Back navigation:**
- Always allow users to go back to previous steps
- Preserve entered data when navigating between steps
- Never reset the form on back navigation

---

## Field Design Patterns

### Field Labels

| Pattern | When to Use | Example |
|---------|-------------|---------|
| Above-field labels | Default for most forms | Label sits above the input |
| Inline labels (floating) | Space-constrained layouts | Label moves from inside to above on focus |
| Left-aligned labels | Wide desktop forms | Label to the left of field |
| Placeholder-only labels | Never | Disappears on input, accessibility failure |

### Field Types

| Data Needed | Best Input Type | Avoid |
|------------|-----------------|-------|
| Email | `type="email"` with validation | Plain text input |
| Phone | `type="tel"` with format mask | Plain text input |
| Country | Searchable dropdown | Long static dropdown |
| Company size | Button group (1-10, 11-50, 51-200, 200+) | Free text input |
| Interest/topic | Checkbox group (max 6 options) | Multi-select dropdown |
| Message | Textarea (3-4 rows visible) | Single-line text input |
| Date | Native date picker | Three separate dropdowns |

### Conditional Fields

Show additional fields based on earlier answers. This reduces visible complexity while capturing necessary data.

**Example:** "What is your primary goal?" dropdown shows "Budget range" only if they select "Ready to buy" or "Evaluating solutions."

**Rules:**
- Conditional fields appear with smooth animation (not instant jump)
- Only 1-2 conditional fields per trigger
- Conditional fields are never required (the trigger answer may change)

---

## Validation UX

### Real-Time vs Submit-Time Validation

| Validation Type | When to Use |
|----------------|-------------|
| Real-time (on blur) | Email format, phone format, required fields |
| On submit | Complex validation, server-side checks |
| Inline suggestions | Company name auto-complete, address lookup |

### Error Message Design

| Pattern | Good | Bad |
|---------|------|-----|
| Position | Below the field, in context | Top of form, disconnected |
| Tone | "Please enter a valid email address" | "Error: Invalid input" |
| Specificity | "Phone must include area code" | "Invalid phone number" |
| Color | Red text + red border on field | Red banner at top of page |
| Icon | Error icon next to message | No visual indicator |

### Success Indicators

- Green checkmark on valid fields (especially email and phone)
- Positive microcopy: "Looks good!" on valid email
- Do NOT flash green/red on every keystroke -- validate on blur (when user leaves the field)

---

## CTA and Submit Button Optimization

### Button Copy Framework

| Form Type | Weak Copy | Strong Copy | Strongest Copy |
|-----------|-----------|-------------|----------------|
| Content download | Submit | Download Guide | Get My Free Guide |
| Demo request | Submit | Request Demo | Schedule My Demo |
| Contact form | Send | Send Message | Get in Touch |
| Newsletter | Subscribe | Join Newsletter | Get Weekly Tips |
| Free trial | Sign Up | Start Free Trial | Start Building Free |

**Rules:**
- Use first person ("Get My..." not "Get Your...")
- Specify what they get, not what they do
- Include "Free" when applicable
- Keep under 5 words

### Button Design

| Element | Best Practice |
|---------|---------------|
| Color | High contrast against form background, consistent with brand CTA color |
| Size | Full-width on mobile, min 44px height for touch targets |
| Position | Immediately below last field, no gap |
| Loading state | Show spinner + "Sending..." to prevent double-submit |
| Disabled state | Disabled until required fields are valid (with clear visual distinction) |

---

## Mobile Form Optimization

### Mobile-Specific Rules

| Rule | Implementation |
|------|---------------|
| Touch targets | Minimum 44x44px for all interactive elements |
| Keyboard types | `type="email"` for email, `type="tel"` for phone, `type="number"` for numeric |
| Auto-focus | Focus first field on page load (with keyboard open) |
| Sticky submit | Pin submit button to bottom of viewport on long forms |
| Input spacing | Minimum 8px between fields to prevent mis-taps |
| Dropdown alternatives | Use button groups or radio buttons instead of dropdowns on mobile |
| Auto-fill | Support browser auto-fill for standard fields (name, email, phone, address) |

### Mobile vs Desktop Form Differences

| Aspect | Desktop | Mobile |
|--------|---------|--------|
| Layout | 1 or 2 columns | Always 1 column |
| Field count | Up to 8 | Max 5 per step |
| Dropdown | Standard dropdown | Bottom sheet or full-screen picker |
| Help text | Hover tooltips | Always-visible inline text |
| Validation | On blur | On blur + on submit summary |

---

## Trust and Context Elements

### Trust Signals Near Forms

| Signal | Placement | Impact |
|--------|-----------|--------|
| Privacy assurance | Below submit button | "We'll never share your email" |
| Security badges | Next to form container | SSL, SOC2, GDPR compliance |
| Testimonial | Adjacent to form | Social proof reduces hesitation |
| Response time | Below submit button | "We respond within 2 hours" |
| Subscriber/user count | Above or within form | "Join 10,000+ subscribers" |

### Context Reinforcement

| Element | Purpose | Example |
|---------|---------|---------|
| Form header | Remind what they get | "Get your free SEO audit report" |
| Bullet list above form | Reinforce value | "You'll get: Full site analysis, Priority fix list, 30-min review call" |
| Expected next step | Set expectations | "After submitting, we'll email your report within 24 hours" |

---

## Form Type Playbooks

### Lead Capture (Gated Content)

**Goal:** Maximize completions while capturing qualified leads.
- Fields: Email only (or Email + First name maximum)
- CTA: Value-specific ("Get My Report", "Download Checklist")
- Trust: "No spam, unsubscribe anytime"
- Post-submit: Immediate download + thank you page + follow-up email

### Demo Request

**Goal:** Capture qualified prospects ready for sales conversation.
- Fields: Email + Name + Company (+ Phone and Team size optional)
- CTA: "Schedule My Demo"
- Trust: "30-minute call, no commitment"
- Post-submit: Calendar booking page or confirmation with scheduling link
- Consider: Embedded calendar (Calendly/Cal.com) instead of form

### Contact Form

**Goal:** Enable communication while routing to correct team.
- Fields: Email + Name + Subject dropdown + Message
- CTA: "Send Message"
- Trust: "We respond within [X] hours"
- Post-submit: Confirmation with expected response time
- Consider: Adding department/topic routing dropdown

### Quote Request

**Goal:** Capture enough detail for accurate quoting.
- Fields: Multi-step form with project details
- CTA: "Get My Quote"
- Trust: "Free quote, no obligation"
- Post-submit: Quote delivery timeline + human follow-up

---

## A/B Test Framework

### High-Impact Tests (Run First)

| Test | Hypothesis | Success Metric |
|------|-----------|----------------|
| Remove phone field | Removing phone increases completion by 5-10% | Completion rate |
| Single-step to multi-step | Multi-step increases completion for 6+ field forms | Completion rate + submission quality |
| CTA copy change | Value-specific copy increases clicks by 10-20% | Click-through rate |
| Add social proof | Testimonial near form increases trust | Completion rate |

### Medium-Impact Tests

| Test | Hypothesis | Success Metric |
|------|-----------|----------------|
| Field order change | Easiest fields first increases step-1 completion | Step completion rates |
| Inline validation | Real-time feedback reduces form errors | Error rate + completion rate |
| Add progress bar | Visual progress on multi-step increases completion | Completion rate |
| Embedded calendar vs form | Calendar reduces friction for demo requests | Booking rate |

### Measurement Rules

- Run each test for minimum 2 weeks or 200 conversions per variant (whichever is longer)
- Track both quantity (completion rate) and quality (lead score, SQL rate)
- A test that increases completions but decreases lead quality is not a win

---

## Metrics and Measurement

### Key Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Form completion rate | Submissions / Form views | 20-40% for lead forms, 5-15% for long forms |
| Field-level drop-off | Abandonment per field | Identify the highest-drop field |
| Time to complete | Avg seconds from first interaction to submit | < 60s for simple forms, < 3min for complex |
| Error rate | Users who see error / total users | < 10% |
| Mobile completion rate | Mobile submissions / Mobile form views | Should be within 20% of desktop rate |

### Instrumentation Requirements

Track these events in your analytics:
- Form view (impression)
- Form interaction (first field focus)
- Per-field completion (on blur, per field)
- Form submission attempt
- Form submission success
- Form validation error (per field)

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Form Audit Report | Issue/Impact/Fix/Priority table | Per-field analysis with estimated abandonment cost |
| Recommended Field Set | Justified list | Required vs optional vs enrichable fields with rationale |
| Field Layout Specification | Annotated outline | Order, grouping, label style, validation rules, mobile adaptations |
| CTA Copy Options | 3-option table | Button text variants with reasoning and expected impact |
| A/B Test Plan | Prioritized table | Top 5 tests with hypothesis, variant, metric, and priority |
| Mobile Optimization Checklist | Checkbox list | Mobile-specific fixes with implementation notes |

---

## Related Skills

- **signup-flow-cro** -- Use when the form is an account creation or trial registration flow. Form-cro is for lead capture, contact, and demo forms.
- **popup-cro** -- Use when the form lives inside a modal or popup. Form-cro handles the form itself; popup-cro handles the trigger, timing, and container.
- **page-cro** -- Use when the page surrounding the form needs optimization (headline, value prop, layout).
- **onboarding-cro** -- Use when post-form-submission activation is the bottleneck, not the form itself.

---

## Tool Reference

### 1. form_scorer.py

**Purpose:** Score a form against CRO best practices across field count, field types, CTA quality, mobile readiness, and trust signals.

```bash
python scripts/form_scorer.py form_config.json
python scripts/form_scorer.py form_config.json --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `form_config.json` | Yes | JSON file with form fields, CTA, and context metadata |
| `--json` | No | Output results as JSON |

### 2. field_cost_analyzer.py

**Purpose:** Calculate the estimated abandonment cost of each form field and recommend fields to remove, keep, or make enrichable.

```bash
python scripts/field_cost_analyzer.py form_fields.json
python scripts/field_cost_analyzer.py form_fields.json --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `form_fields.json` | Yes | JSON file with form fields and their types |
| `--json` | No | Output results as JSON |
| `--monthly-visitors` | No | Monthly form visitors for dollar impact estimate (default: 1000) |
| `--current-rate` | No | Current form completion rate as percentage (default: 25) |
| `--value-per-lead` | No | Dollar value per lead for ROI calculation (default: 50) |

### 3. ab_test_calculator.py

**Purpose:** Calculate A/B test sample size, duration, and statistical significance for form optimization experiments.

```bash
python scripts/ab_test_calculator.py --baseline 25 --lift 10 --traffic 500
python scripts/ab_test_calculator.py --baseline 25 --lift 10 --traffic 500 --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `--baseline` | Yes | Current conversion rate as percentage (e.g., 25 for 25%) |
| `--lift` | Yes | Minimum detectable lift as percentage (e.g., 10 for 10% relative lift) |
| `--traffic` | Yes | Daily traffic (visitors per day to the form) |
| `--confidence` | No | Confidence level as percentage (default: 95) |
| `--json` | No | Output results as JSON |

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Form completion rate below 15% | Too many fields or high-friction fields present | Run field_cost_analyzer.py to identify and remove high-cost fields; target email-only for first-touch lead forms |
| Mobile completion rate 50%+ lower than desktop | Form not optimized for touch input | Ensure 44px touch targets, single-column layout, native keyboard types; replace dropdowns with button groups on mobile |
| Users start but do not finish the form | Friction in middle fields (phone, budget, message) | Move high-friction fields to later steps in a multi-step form; capture email in step 1 |
| High error rate on email or phone fields | Validation too aggressive or unclear error messages | Validate on blur (not keystroke); use specific error copy ("Please include @ in email") not generic ("Invalid input") |
| A/B test results are inconclusive after 4 weeks | Insufficient sample size or too small a lift target | Use ab_test_calculator.py to confirm required sample size; consider testing bigger changes (field removal vs copy tweak) |
| CTA clicks are low despite good page traffic | CTA copy is generic or button is not prominent enough | Replace "Submit" with value-specific copy ("Get My Report"); ensure CTA is full-width on mobile, high-contrast color |

---

## Success Criteria

- Form completion rate above 25% for lead capture forms (above 35% is excellent)
- Mobile completion rate within 20% of desktop rate
- Error rate below 10% of form interactions
- Field-level drop-off identifies specific friction points with clear remediation
- Each form field has documented justification (business need or enrichable post-submission)
- A/B tests run for minimum 200 conversions per variant before declaring winner
- Post-form-submission follow-up occurs within 24 hours for demo and contact forms

---

## Scope & Limitations

- **In scope:** Form field optimization, CTA copy, validation UX, mobile optimization, trust signal placement, A/B test design, field cost analysis
- **Out of scope:** Page-level CRO (use page-cro), popup trigger optimization (use popup-cro), signup/registration flows (use signup-flow-cro), post-submission nurture sequences
- **Data dependency:** Field-level analytics (per-field drop-off) provide the most actionable data but require analytics instrumentation
- **Compliance constraint:** GDPR/HIPAA may require specific fields that cannot be removed; document compliance requirements before optimizing
- **Statistical validity:** A/B test recommendations require sufficient traffic volume; low-traffic forms may need longer test durations or alternative evaluation methods

---

## Integration Points

- **page-cro** -- When the form converts well but the surrounding page does not drive form interactions, optimize the page-level elements first
- **popup-cro** -- When the form is inside a popup or modal, trigger timing and container design are handled by popup-cro
- **signup-flow-cro** -- For account creation and registration forms (not lead capture), use signup-flow-cro which handles multi-step auth flows
- **onboarding-cro** -- When post-form-submission activation is the bottleneck, not the form completion rate itself
- **free-tool-strategy** -- Free tools often include lead capture forms; use form-cro to optimize the capture form within the tool
