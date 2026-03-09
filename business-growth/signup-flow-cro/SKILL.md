---
name: signup-flow-cro
description: Signup and registration flow optimization covering SSO strategy, progressive profiling, field reduction, multi-step flow design, authentication UX, post-submit experience, and mobile registration patterns.
version: 1.0.0
author: borghei
category: business-growth
tags: [cro, signup, registration, authentication, conversion-optimization]
triggers:
  - user wants to optimize signup, registration, or account creation
  - user mentions signup conversion, registration friction, or signup dropoff
  - user asks about SSO, social login, or magic link authentication
  - user mentions free trial signup optimization
  - user reports high mobile signup abandonment
  - user asks whether to require a credit card for trial
---

# Signup Flow CRO

Production-grade signup and registration optimization framework covering authentication strategy, field reduction methodology, multi-step flow architecture, SSO implementation, progressive profiling, credit card requirement analysis, post-submit experience design, and mobile-specific registration patterns. For post-signup onboarding, use onboarding-cro. For lead capture forms (not account creation), use form-cro.

---

## Table of Contents

- [Initial Assessment](#initial-assessment)
- [Authentication Strategy](#authentication-strategy)
- [Field Reduction Methodology](#field-reduction-methodology)
- [Multi-Step Flow Architecture](#multi-step-flow-architecture)
- [Credit Card Requirement Analysis](#credit-card-requirement-analysis)
- [Post-Submit Experience](#post-submit-experience)
- [Mobile Signup Optimization](#mobile-signup-optimization)
- [Signup Flow Patterns by Product Type](#signup-flow-patterns-by-product-type)
- [Progressive Profiling](#progressive-profiling)
- [Error and Edge Case Handling](#error-and-edge-case-handling)
- [A/B Test Framework](#ab-test-framework)
- [Metrics and Benchmarks](#metrics-and-benchmarks)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Initial Assessment

### Required Context

| Question | Why It Matters |
|----------|---------------|
| Flow type? (free trial, freemium, paid, waitlist) | Determines friction tolerance |
| B2B or B2C? | B2B tolerates more fields, B2C needs minimal friction |
| How many steps/screens currently? | Baseline for optimization |
| What fields are required? | Identifies reduction opportunities |
| Current completion rate? | Benchmark for improvement |
| Where do users drop off? (field-level data) | Pinpoints specific friction |
| What data is needed before first product use? | Separates must-have from nice-to-have |
| What compliance requirements exist? | Constrains what can be deferred |

---

## Authentication Strategy

### Authentication Methods Ranked by Friction

| Method | Friction Level | Best For | Conversion Impact |
|--------|---------------|----------|------------------|
| Google SSO (one-click) | Very low | B2B SaaS, productivity tools | +15-30% vs email+password |
| Apple Sign In | Very low | iOS/Mac-heavy audience | +10-20% on Apple devices |
| Microsoft SSO | Low | Enterprise B2B | +10-15% for enterprise |
| GitHub SSO | Low | Developer tools | +15-25% for dev audience |
| Magic link (email) | Low | Security-conscious, B2B | +5-10% vs password |
| Email + password | Medium | Universal fallback | Baseline |
| Phone + OTP | Medium | Mobile-first, B2C | Varies by market |
| Email + password + verification | High | When verification is required | -10-20% vs no verification |

### SSO Strategy Decision

| Your Audience | Primary SSO | Secondary SSO | Keep Email+Password? |
|--------------|-------------|---------------|---------------------|
| B2B SaaS (general) | Google Workspace | Microsoft | Yes |
| Developer tools | GitHub | Google | Yes |
| Enterprise | Microsoft/Okta | Google | Yes (for personal evals) |
| B2C consumer | Google | Apple | Yes |
| Mobile-first | Apple / Google | Phone OTP | Optional |
| Privacy-focused | Magic link | Email+password | Yes |

### SSO Placement

```
┌──────────────────────────────────┐
│  Create your account             │
│                                  │
│  [Continue with Google]          │  ← SSO options first
│  [Continue with Microsoft]       │
│                                  │
│  ──── or ────                   │  ← Visual separator
│                                  │
│  Email: [_______________]       │  ← Email+password as alternative
│  Password: [_______________]    │
│                                  │
│  [Create Account]               │
└──────────────────────────────────┘
```

**Rules:**
- SSO buttons above the email form (not below)
- Use branded button styles (Google's official button, etc.)
- "or" divider between SSO and email options
- SSO reduces fields to zero (name and email come from the provider)

---

## Field Reduction Methodology

### The "Before First Use" Test

For every field, ask: **Does the product literally not function without this data?**

| Field | Passes Test? | Action |
|-------|-------------|--------|
| Email | Yes (account identity) | Keep |
| Password | Yes (account security) | Keep (or use SSO/magic link) |
| First name | Usually no | Defer to onboarding or profile |
| Last name | No | Defer or drop entirely |
| Company name | Usually no | Enrich from email domain |
| Phone number | Rarely | Defer unless SMS verification required |
| Job title | No | Defer to onboarding or enrich |
| Team size | No | Defer to onboarding |
| How did you hear about us? | Never | Post-signup survey or attribution |
| Industry | No | Enrich from company data |

### Enrichment Sources

| Field | Enrichment Method | Timing |
|-------|-------------------|--------|
| Company name | Email domain lookup (Clearbit, Apollo) | Immediately post-signup |
| Company size | Company data API | Immediately post-signup |
| Industry | Company data API | Immediately post-signup |
| Job title | LinkedIn API or manual CSM research | Before first sales contact |
| Location | IP geolocation | On signup |

### Minimum Viable Field Sets

| Signup Type | Minimum Fields | Additional (if needed) |
|------------|----------------|----------------------|
| Freemium | Email only (or SSO) | -- |
| Free trial (product-led) | Email + Password (or SSO) | -- |
| Free trial (sales-assisted) | Email + Password + Company | + Role (for routing) |
| Paid signup | Email + Password + Payment | -- |
| Waitlist | Email | + One qualifying question |
| Enterprise trial | Email + Company + Role | + Team size (for provisioning) |

---

## Multi-Step Flow Architecture

### When to Use Multi-Step

| Condition | Single-Step | Multi-Step |
|-----------|------------|------------|
| Total fields | 1-4 | 5+ |
| Need to qualify/route | No | Yes |
| Product needs configuration | No | Yes |
| B2B with team setup | No | Yes |

### Step Design

**Step 1: Account Creation (lowest friction)**
- Email + Password (or SSO)
- NOTHING else on this step
- This is where 60%+ of abandonment happens if overloaded

**Step 2: Personalization (if needed)**
- Role / goal / use case selection
- This personalizes their product experience
- Skip button available ("Set up later")

**Step 3: Configuration (if needed)**
- Team invite, integration connect, data import
- Each sub-step is optional with "Skip for now"
- Show value of completing each ("Invite your team to collaborate")

### Progress Design

- Show step count: "Step 1 of 3"
- Show progress bar
- Label each step descriptively: "Create Account", "Your Role", "Your Team"
- Allow back navigation (preserve entered data)
- Never reset the form on back navigation or browser back button

---

## Credit Card Requirement Analysis

### Decision Framework

| Factor | Require CC | Do Not Require CC |
|--------|-----------|------------------|
| Trial conversion goal | > 60% trial-to-paid | > 30% trial-to-paid with higher volume |
| Product complexity | Simple, immediate value | Complex, needs exploration |
| ACV | > $100/month | < $100/month |
| Sales motion | Product-led | Sales-assisted |
| Competitor practice | Competitors require CC | Competitors offer CC-free trial |
| Target audience | Enterprise (committed buyers) | SMB/prosumer (browsers) |

### Impact Analysis

| Approach | Signup Volume | Trial Quality | Trial-to-Paid | Net Revenue |
|----------|-------------|---------------|---------------|-------------|
| No CC required | Higher (+40-80%) | Lower (more tire-kickers) | Lower (2-15%) | Often higher net |
| CC required | Lower | Higher (committed) | Higher (40-70%) | Depends on volume |
| CC with "$0 charge" | Middle | Middle | Middle (20-40%) | Middle |

### Recommendation Framework

**Default to no CC required** unless:
1. Your product delivers immediate, obvious value (no learning curve)
2. Your trial-to-paid with CC is > 50%
3. You have a high-touch sales team to handle lower volume
4. Support costs for free trials are unsustainable

**If requiring CC:** Display prominently:
- "You won't be charged until [date]"
- "Cancel anytime before [date]"
- "We'll email you 3 days before your trial ends"

---

## Post-Submit Experience

### Immediately After Signup

| Element | Implementation |
|---------|---------------|
| Auto-login | Log the user in immediately (never force a separate login) |
| Welcome screen | Show a clear next step, not a blank dashboard |
| Confirmation email | Send immediately, include: what to expect, key features, support contact |
| Email verification | Defer if possible. If required, send inline and let them continue using the product before verifying |

### Email Verification Strategy

| Approach | Impact on Activation | When to Use |
|----------|---------------------|-------------|
| No verification | Best activation rate | Low-risk products, freemium |
| Verify to unlock specific feature | Good -- users activate first | B2B SaaS with free tier |
| Verify within 24 hours | Moderate -- creates urgency | Products that send emails |
| Verify before any use | Worst activation rate | Regulated industries, financial products |

**Default recommendation:** Let users use the product immediately. Verify within 24-48 hours. Gate only the features that require a verified email (e.g., sending emails, team invites).

---

## Mobile Signup Optimization

### Mobile-Specific Rules

| Rule | Implementation |
|------|---------------|
| SSO first | Google/Apple Sign In is one tap on mobile |
| One column | Never use side-by-side fields on mobile |
| Large inputs | Minimum 44px height for all touch targets |
| Appropriate keyboards | `type="email"`, `type="tel"`, `type="password"` |
| Auto-fill support | Use standard field names for browser auto-fill |
| Sticky CTA | Pin "Create Account" button to bottom of viewport |
| No CAPTCHA | Use invisible reCAPTCHA or alternatives |
| Password visibility | Toggle to show/hide password |

### Mobile vs Desktop Signup Differences

| Aspect | Desktop | Mobile |
|--------|---------|--------|
| Primary auth | SSO or Email+Password | SSO preferred (one-tap) |
| Fields per screen | Up to 5 | Max 3 |
| Password rules | Show requirements upfront | Show on interaction |
| CAPTCHA | Standard reCAPTCHA acceptable | Invisible or none |
| Social proof | Sidebar or adjacent | Below form or above |

---

## Signup Flow Patterns by Product Type

### B2B SaaS Trial

```
[Google SSO] or [Email + Password]
→ Auto-login to product
→ Welcome screen: "What brings you here?" (3 options)
→ Guided first action based on selection
→ Team invite prompt (optional, day 2-3)
```

### B2C Consumer App

```
[Apple Sign In] or [Google Sign In] or [Email]
→ Immediately into product
→ Personalization (follows, preferences) inline
→ Profile completion deferred
```

### Enterprise/Sales-Assisted

```
[Work Email + Password + Company Name]
→ Auto-login to sandbox
→ Role + team size (for provisioning)
→ CSM outreach triggered for qualified accounts
→ Guided setup with dedicated support
```

### Waitlist / Early Access

```
[Email only]
→ Confirmation page: position in waitlist
→ Referral mechanism: "Jump ahead by sharing"
→ Weekly update email on progress
→ Access granted email with one-click activation
```

---

## Progressive Profiling

Collect information over multiple sessions instead of one long form.

### Progressive Profiling Schedule

| Session | What to Collect | How |
|---------|----------------|-----|
| Signup (session 1) | Email + auth | Signup form |
| First use (session 1-2) | Role, primary goal | In-product prompt or setup wizard |
| Day 3-5 | Team size, use case | Contextual question in product |
| Day 7-14 | Industry, company size | Survey or enrichment |
| Before first payment | Billing info | Upgrade flow |

### Implementation Rules

- Each profiling touchpoint asks 1-2 questions maximum
- Always explain why you are asking ("So we can personalize your experience")
- Always provide a "Skip" option
- Never ask for information you can enrich automatically
- Store partial profiles and build over time

---

## Error and Edge Case Handling

### Password Requirements

| Approach | User Experience | Security |
|----------|----------------|----------|
| Show requirements upfront | Best -- user knows what to enter | Good |
| Show requirements on focus | Good | Good |
| Show errors only after submit | Bad -- frustrating | Same |
| Real-time checkmarks | Best -- progressive validation | Good |

**Recommended:** Show password requirements as a checklist that checks off in real-time as the user types.

### Common Error Scenarios

| Error | Bad UX | Good UX |
|-------|--------|---------|
| Email already registered | "Error: account exists" | "This email already has an account. [Log in] or [Reset password]" |
| Weak password | "Password too weak" | Checkmarks showing which requirements are met/unmet |
| SSO failure | Generic error page | "Something went wrong with Google login. [Try again] or [Use email instead]" |
| Network error | Form clears, no message | "Connection issue. Your data is saved. [Try again]" |
| Rate limiting | Blocked with no explanation | "Too many attempts. Please try again in [N] minutes" |

---

## A/B Test Framework

### High-Impact Tests

| Test | Hypothesis | Metric |
|------|-----------|--------|
| Add Google SSO | SSO increases completion by 15-30% | Signup completion rate |
| Remove non-essential fields | Fewer fields = higher completion | Completion rate + activation rate |
| Single-step vs multi-step | Multi-step feels easier for 5+ field forms | Completion rate |
| CC required vs not | No CC increases volume enough to offset lower conversion | Net revenue |
| Defer email verification | Immediate product access increases activation | Activation rate |

### Measurement Rules

- Track signup completion rate AND downstream activation rate
- A test that increases signups but decreases activation is not a win
- Track by traffic source (paid vs organic may respond differently)
- Track mobile and desktop separately

---

## Metrics and Benchmarks

### Key Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Signup page visit-to-completion | Completions / Page views | 30-50% (B2B), 40-60% (B2C) |
| SSO adoption rate | SSO signups / Total signups | 30-60% when offered |
| Field-level drop-off | Abandonment per field | Identify highest-drop field |
| Time to complete | Median seconds from first interaction to submit | < 45s for simple, < 2min for multi-step |
| Mobile completion rate | Mobile completions / Mobile page views | Should be within 15% of desktop |
| Email verification rate | Verified / Total signups | > 70% within 48 hours |

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Signup Flow Audit | Issue/Impact/Fix/Priority table | Per-step analysis with estimated impact |
| Recommended Field Set | Justified list | Required vs deferrable fields with rationale |
| Authentication Strategy | Decision matrix | SSO options, placement, priority |
| Flow Redesign Spec | Step-by-step outline | Screen-by-screen design with copy |
| Progressive Profiling Plan | Session-by-session schedule | What to collect, when, and how |
| A/B Test Plan | Prioritized table | Top 5 tests with hypothesis and expected impact |
| Mobile Optimization Checklist | Per-element rules | Touch targets, keyboards, auto-fill, sticky CTA |

---

## Related Skills

- **onboarding-cro** -- Use for post-signup activation optimization. Signup-flow-cro ends when the user has an account; onboarding-cro starts there.
- **form-cro** -- Use for non-signup forms (lead capture, contact, demo request). Different optimization framework than registration.
- **page-cro** -- Use when the landing page leading to signup is the bottleneck, not the signup form itself.
- **paywall-upgrade-cro** -- Use when the real challenge is converting free users to paid, not getting them to sign up.
