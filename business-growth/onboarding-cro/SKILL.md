---
name: onboarding-cro
description: Post-signup user onboarding optimization covering activation metrics, time-to-value reduction, onboarding flow design, empty state optimization, multi-channel coordination, and stalled user recovery.
version: 1.0.0
author: borghei
category: business-growth
tags: [cro, onboarding, activation, user-experience, retention, time-to-value]
triggers:
  - user wants to optimize post-signup onboarding or first-run experience
  - user mentions activation rate, user activation, or aha moment
  - user has low Day-1 or Day-7 retention
  - user says users sign up but do not come back
  - user mentions onboarding checklist, empty states, or guided tours
  - user asks about improving trial-to-paid conversion
---

# Onboarding CRO

Production-grade user onboarding optimization framework covering activation definition, time-to-value engineering, flow architecture, empty state design, multi-channel coordination, stalled user recovery, and experiment design. Focused on the critical window between signup and habitual product usage.

---

## Table of Contents

- [Initial Assessment](#initial-assessment)
- [Activation Definition Framework](#activation-definition-framework)
- [Onboarding Flow Architecture](#onboarding-flow-architecture)
- [Time-to-Value Engineering](#time-to-value-engineering)
- [Empty State Design](#empty-state-design)
- [Onboarding Patterns by Product Type](#onboarding-patterns-by-product-type)
- [Multi-Channel Coordination](#multi-channel-coordination)
- [Stalled User Recovery](#stalled-user-recovery)
- [Onboarding Checklist Design](#onboarding-checklist-design)
- [Tooltip and Tour Design](#tooltip-and-tour-design)
- [Metrics and Measurement](#metrics-and-measurement)
- [Experiment Framework](#experiment-framework)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Initial Assessment

### Required Context

| Question | Why It Matters |
|----------|---------------|
| What is the product type? (B2B SaaS, B2C app, marketplace, content platform) | Determines the onboarding pattern |
| What is the core value proposition? | Defines what the aha moment should demonstrate |
| What happens immediately after signup? | Identifies the current first-run experience |
| What action correlates most with 30-day retention? | Defines the activation event |
| Where do users drop off? (funnel data if available) | Pinpoints the biggest bottleneck |
| What is the current activation rate? | Baseline for improvement |
| What is Day-1 / Day-7 / Day-30 retention? | Context for urgency |

---

## Activation Definition Framework

### Finding the Aha Moment

The aha moment is the specific action that, once completed, makes a user significantly more likely to retain. It is NOT a feature -- it is the moment the user experiences the core value.

**Method to identify it:**

1. **Cohort comparison:** Compare 90-day retained users vs churned users. What actions did retained users do in the first 7 days that churned users did not?
2. **Correlation analysis:** For each candidate action, calculate the correlation between completing that action in week 1 and being retained at day 30.
3. **Timing analysis:** When do retained users complete this action? (Day 1? Day 3? Day 7?)

### Activation Event Examples

| Product Type | Activation Event | Why This Works |
|-------------|-----------------|----------------|
| Project management | Create project + invite 1 team member | Collaboration creates switching costs |
| Analytics tool | Install tracking + view first report | Seeing their own data is the value |
| Design tool | Create first design + export or share | Output = value realized |
| CRM | Import contacts + log first activity | Data investment creates lock-in |
| Marketplace | Complete first transaction | Transaction = value delivered |
| Content platform | Follow 3+ sources + consume 5+ items | Personalization drives habit |
| Communication tool | Send first message + get a reply | Two-sided value activation |

### Activation Metric Structure

```
Activation Rate = Users who reach activation event / Total signups
                  (within first N days)

Target: 40-60% activation within 7 days for B2C
        25-40% activation within 14 days for B2B
```

---

## Onboarding Flow Architecture

### Flow Type Selection

| Approach | Best For | Risk | Mitigation |
|----------|----------|------|------------|
| Product-first (drop into product) | Simple products, B2C, mobile apps | Blank slate overwhelm | Pre-populated sample data |
| Guided setup (wizard) | Products needing configuration | Adds friction before value | Keep to 3-5 steps max |
| Value-first (show results immediately) | Products with demo data | May not feel personalized | Use their data if possible |
| Template-first | Creative/productivity tools | Choice paralysis | Curate 3-5 starter templates |
| Video walkthrough | Complex B2B products | Users skip videos | Keep under 90 seconds |

### The First 30-Second Rule

Whatever flow type you choose, within 30 seconds of landing in the product, the user must:

1. See a clear single next action (not 5 options)
2. Understand what the product will do for them
3. Have a visible path forward (no dead ends)

### Flow Design Principles

| Principle | Implementation |
|-----------|---------------|
| One goal per session | First session focuses ONLY on reaching the aha moment |
| Do, don't show | User performs the action, not watches a tutorial about it |
| Progress creates motivation | Show advancement (checklist, progress bar, celebration) |
| Defer complexity | Advanced settings and features surface AFTER activation |
| Always escapable | Users can skip or dismiss any onboarding element |
| Remember state | If user leaves and returns, resume where they left off |

---

## Time-to-Value Engineering

### Time-to-Value (TTV) Reduction Framework

TTV is the elapsed time between signup and the user experiencing core value. Shorter = better.

| Bottleneck | Detection | Fix | Expected TTV Reduction |
|-----------|-----------|-----|----------------------|
| Setup required before use | Users drop off during setup | Reduce required setup steps, use defaults | 30-50% |
| Waiting for data | No value until data arrives | Provide sample/demo data immediately | 40-60% |
| Waiting for team members | Value requires collaboration | Enable solo value first, then team | 20-40% |
| Integration required | Cannot function without connecting tools | Offer manual input as alternative | 30-50% |
| Learning curve | Product too complex for quick win | Guided first action with templates | 20-30% |
| Approval/verification required | Email verification, admin approval | Defer verification to after first value | 40-60% |

### Quick Win Architecture

Design the onboarding to deliver a "quick win" within the first 3 minutes:

1. Identify the simplest valuable output the product can deliver
2. Pre-populate inputs where possible
3. Minimize decisions (use smart defaults)
4. Celebrate the output ("You just created your first [X]!")
5. Immediately show the next step

---

## Empty State Design

Empty states are onboarding moments, not dead ends. Every blank screen is an opportunity to guide the user toward activation.

### Empty State Anatomy

```
┌─────────────────────────────────────┐
│                                     │
│      [Illustration or Preview]      │  Show what this will look like with data
│                                     │
│   What this section does            │  1 sentence, benefit-focused
│                                     │
│   [Primary CTA: Create First X]    │  Single clear action
│                                     │
│   Or try with sample data →        │  Low-friction alternative
│                                     │
└─────────────────────────────────────┘
```

### Empty State Rules

| Rule | Good | Bad |
|------|------|-----|
| Show the end state | Preview with sample data | Completely blank screen |
| Single CTA | "Create your first project" | "Learn more" + "Watch video" + "Read docs" |
| Explain the value | "Track your team's progress in one view" | "No projects found" |
| Offer sample data | "Try with example data" link | Force creation from scratch |

---

## Onboarding Patterns by Product Type

### B2B SaaS

```
Signup → Setup Wizard (3-5 steps) → First Value Action → Team Invite → Deep Setup
         ├── Company info              ├── Template selection     ├── Email invites
         ├── Role/goal selection       ├── Quick configuration    └── Permissions
         └── Integration connect       └── First output created
```

**Key metric:** Time from signup to first team collaboration

### Marketplace / Two-Sided

```
Signup → Complete Profile → Browse/Discover → First Transaction → Repeat Loop
         ├── Photo/avatar         ├── Curated feed          ├── Guided first action
         ├── Preferences          ├── Search + filters      └── Transaction completion
         └── Verification         └── Saved/bookmarked
```

**Key metric:** Time from signup to first completed transaction

### Mobile App (B2C)

```
Install → Permission Requests → Quick Win → Push Notification Setup → Habit Loop
          ├── Location (if needed)   ├── Core action            ├── Value-based ask
          ├── Notifications          ├── Immediate result       └── Frequency choice
          └── Camera/contacts        └── Celebration
```

**Key metric:** Day-1 retention rate

### Content / Media Platform

```
Signup → Interest Selection → Personalized Feed → First Engagement → Social Connection
         ├── Topic picks          ├── Curated content      ├── Read/watch/listen
         ├── Creator follows      ├── Algorithmic mix      └── Like/save/share
         └── Format preferences   └── Notification prefs
```

**Key metric:** Sessions per week in first 14 days

---

## Multi-Channel Coordination

### Email + In-App Matrix

| Trigger | In-App Action | Email Action | Timing |
|---------|--------------|--------------|--------|
| Signup complete | Welcome screen with first step | Welcome email with single CTA | Immediate |
| Step 1 complete | Show step 2 | -- (don't email for every step) | Immediate |
| 24 hours, incomplete onboarding | Persistent banner/checklist | "Complete your setup" email | 24h after signup |
| 72 hours, not activated | Welcome back modal | "Here's what you can do" email | 72h after signup |
| Activation achieved | Celebration modal + next feature | Celebration email + next step | Immediate |
| Day 7, feature discovery | Contextual tooltip | "Did you know?" feature email | Day 7 |
| Day 14, engagement dip | -- | Re-engagement with use case examples | Day 14 |

### Email Design Rules

- Each email has ONE CTA that drives back into the product
- Personalize based on actions already taken (do not ask them to do what they already did)
- Keep emails short (< 150 words body)
- Subject line references the specific next step, not generic "Welcome to [Product]"

---

## Stalled User Recovery

### Stalled User Definition

| Stalled State | Criteria | Recovery Priority |
|--------------|----------|------------------|
| Never started | Signed up, never logged in again | Medium (may be wrong ICP) |
| Partially onboarded | Completed 1-2 setup steps, stopped | High (invested effort, hit a wall) |
| Active but not activated | Logged in 3+ times, never reached aha moment | Highest (engaged but stuck) |
| Activated but churning | Reached aha moment, usage declining | High (retention problem, not onboarding) |

### Recovery Tactics

| Stalled State | Tactic 1 | Tactic 2 | Tactic 3 |
|--------------|----------|----------|----------|
| Never started | "We set up [X] for you" email | Pre-populated account | -- |
| Partially onboarded | "Pick up where you left off" email | Simplify remaining steps | Offer live help |
| Active but not activated | In-app guided walkthrough | "Users like you do [X]" suggestion | Human outreach for high-value |
| Activated but churning | Feature discovery emails | Usage tips based on their workflow | CSM outreach for enterprise |

### Human Touch Triggers

For high-value accounts (enterprise, high ACV), trigger human outreach when:
- User is > 48 hours stalled in onboarding
- User visits help docs more than 3 times in a session
- User starts and abandons the same action 2+ times
- User's engagement score drops below threshold after initial activation

---

## Onboarding Checklist Design

### When to Use a Checklist

- Multiple setup steps required before full value
- Product has several features to discover
- Self-serve B2B products where users self-onboard
- Products with a clear "fully set up" state

### Checklist Best Practices

| Rule | Implementation |
|------|---------------|
| 3-7 items | Fewer than 3 = not worth a checklist. More than 7 = overwhelming. |
| Order by value | Most impactful action first |
| Start with quick wins | First item should be completable in < 60 seconds |
| Show progress | Progress bar or "3 of 5 complete" counter |
| Pre-check completed items | If they already did something, mark it done |
| Celebrate completion | Animation, confetti, "You're all set!" message |
| Dismissable | "I'll do this later" option. Never trap users. |
| Persistent but not blocking | Sidebar widget or dashboard card, not a blocking modal |

### Checklist Item Design

Each item should include:
- Clear action label ("Import your contacts")
- Why it matters ("So you can track interactions")
- Estimated time ("Takes about 2 minutes")
- CTA button ("Import Now")

---

## Tooltip and Tour Design

### When to Use Tooltips/Tours

- Complex UI where features are not self-evident
- Power features users might miss
- UI changes after a major update
- Features that require specific discovery order

### Tour Best Practices

| Rule | Implementation |
|------|---------------|
| Max 3-5 steps per tour | More than 5 and users will dismiss |
| Dismissable at any time | "Skip tour" on every step |
| Don't repeat for returning users | Track tour completion, never show again |
| Highlight the actual UI element | Spotlight effect on the element being explained |
| Action-oriented | "Click here to create a project" not "This is where projects live" |
| Progressive | Show basic tour on day 1, advanced features tour on day 7 |

---

## Metrics and Measurement

### Key Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Activation rate | Users reaching activation / Total signups | B2C: 40-60%, B2B: 25-40% |
| Time to activation | Median time from signup to activation event | B2C: < 1 day, B2B: < 7 days |
| Onboarding completion rate | Users completing all steps / Total signups | > 60% |
| Day-1 retention | Users returning day after signup / Total signups | > 40% |
| Day-7 retention | Users active 7 days after signup / Total signups | > 25% |
| Day-30 retention | Users active 30 days after signup / Total signups | > 15% |
| Checklist completion rate | Users finishing all items / Users who saw checklist | > 50% |

### Funnel Analysis Template

```
Signup                  100%
├── First login          85%  (-15% never return)
├── Setup step 1         70%  (-15% drop during setup)
├── Setup step 2         55%  (-15% setup friction)
├── First value action   40%  (-15% blank slate / confusion)
├── Activation event     30%  (-10% incomplete value delivery)
└── Day-7 return         20%  (-10% no habit formed)
```

Focus optimization on the step with the largest absolute drop.

---

## Experiment Framework

### High-Impact Experiments

| Experiment | Hypothesis | Metric |
|-----------|-----------|--------|
| Reduce setup steps | Fewer steps = higher completion | Activation rate |
| Pre-populate with sample data | Reduces blank slate anxiety | Time to first value action |
| Add onboarding checklist | Progress visibility increases completion | Onboarding completion rate |
| Defer email verification | Removes friction before value | Time to activation |
| Personalize by role/goal | Relevant path increases activation | Activation rate by segment |

### Medium-Impact Experiments

| Experiment | Hypothesis | Metric |
|-----------|-----------|--------|
| Welcome video vs text | Video may improve or hurt depending on product | Activation rate + time on first screen |
| Checklist order change | Value-first ordering improves completion | Checklist completion rate |
| Guided tour vs self-discover | Tours help complex products | Feature adoption rate |
| In-app chat during onboarding | Real-time help reduces stalls | Stall rate, activation rate |

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Activation Definition Doc | Structured definition | Aha moment, activation event, success metric, measurement plan |
| Onboarding Flow Diagram | Step-by-step flow | Post-signup flow with drop-off points and decision branches |
| Checklist Specification | Item-by-item design | 3-7 items with action, rationale, time estimate, and CTA |
| Email Trigger Map | Trigger/timing/goal table | Conditions and content for each onboarding email |
| Empty State Copy | Per-screen design | Illustration description, headline, body, CTA for each empty state |
| Experiment Backlog | Prioritized table | Test ideas ranked by expected impact and effort |
| Stalled User Playbook | Decision tree | Detection criteria, recovery tactics, escalation rules |

---

## Related Skills

- **signup-flow-cro** -- Use for optimizing the registration flow before users enter the product. Onboarding-cro starts after signup is complete.
- **paywall-upgrade-cro** -- Use when onboarding leads into upgrade moments. Do not show paywalls before the aha moment is reached.
- **churn-prevention** -- Use when users activate but then churn. If they never activate, the problem is onboarding, not churn.
- **page-cro** -- Use when the marketing page before signup is the bottleneck, not the post-signup experience.

---

## Tool Reference

### 1. activation_funnel_analyzer.py

**Purpose:** Analyze an onboarding activation funnel to identify the biggest drop-off points and estimate the impact of fixing each step.

```bash
python scripts/activation_funnel_analyzer.py funnel_data.json
python scripts/activation_funnel_analyzer.py funnel_data.json --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `funnel_data.json` | Yes | JSON file with funnel step names and user counts |
| `--json` | No | Output results as JSON |

### 2. onboarding_checklist_scorer.py

**Purpose:** Score an onboarding checklist design against best practices (item count, ordering, quick wins, progress indication).

```bash
python scripts/onboarding_checklist_scorer.py checklist.json
python scripts/onboarding_checklist_scorer.py checklist.json --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `checklist.json` | Yes | JSON file with checklist items and their properties |
| `--json` | No | Output results as JSON |

### 3. ttv_estimator.py

**Purpose:** Estimate time-to-value (TTV) based on onboarding steps and identify bottlenecks that can be reduced or eliminated.

```bash
python scripts/ttv_estimator.py onboarding_steps.json
python scripts/ttv_estimator.py onboarding_steps.json --json
```

| Flag | Required | Description |
|------|----------|-------------|
| `onboarding_steps.json` | Yes | JSON file with onboarding steps, estimated minutes, and requirements |
| `--json` | No | Output results as JSON |

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Activation rate below 25% (B2B) or 40% (B2C) | Aha moment not reached fast enough | Run ttv_estimator.py to identify TTV bottlenecks; target first value within 5 minutes |
| Users complete onboarding but do not return Day 7 | Onboarding leads to setup, not to value | Restructure flow so the first session delivers a meaningful output, not just configuration |
| Onboarding checklist completion below 50% | Too many items or first item is too complex | Reduce to 3-7 items; start with a quick win completable in under 60 seconds; use onboarding_checklist_scorer.py to audit |
| Stalled users at 40%+ of signups | Blank slate problem or unclear next step | Add pre-populated sample data and empty state CTAs; implement stalled user recovery emails at 24h and 72h |
| Day-1 retention below 30% | First-run experience has dead ends or confusion | Apply the 30-second rule: within 30 seconds, user sees a single next action, understands the value, and has a path forward |
| Email onboarding sequences have low open rates | Generic subject lines or wrong timing | Personalize subject lines to reference the specific next step; send at trigger-based timing, not fixed schedules |
| Team invite rate is low | Invite step placed before value is demonstrated | Defer team invite until after the user has experienced core value individually |

---

## Success Criteria

- Activation rate of 30-40% within 14 days for B2B (40-60% for B2C)
- Time-to-first-value under 5 minutes (verified by ttv_estimator.py)
- Onboarding completion rate above 60%
- Day-1 retention above 40%
- Day-7 retention above 25%
- Stalled user recovery emails achieve 10%+ reactivation rate
- Onboarding checklist scores 70+ on onboarding_checklist_scorer.py assessment

---

## Scope & Limitations

- **In scope:** Activation definition, onboarding flow design, time-to-value engineering, empty state design, checklist design, tooltip/tour design, email coordination, stalled user recovery, experiment design
- **Out of scope:** Signup/registration flow (use signup-flow-cro), marketing page optimization (use page-cro), long-term retention strategy, feature development
- **Data dependency:** Best results require funnel analytics (per-step drop-off data); without this, optimization is based on heuristics
- **Product type matters:** B2B SaaS, marketplace, mobile app, and content platforms have fundamentally different onboarding patterns; use the correct pattern for your product type
- **No silver bullet:** If the product does not deliver value, no amount of onboarding optimization will fix retention; validate product-market fit first

---

## Integration Points

- **signup-flow-cro** -- Optimizes the registration flow before onboarding begins; hand-off point is the moment after successful account creation
- **churn-prevention** -- When users activate but then churn, the problem shifts from onboarding to retention; use churn-prevention for post-activation churn
- **paywall-upgrade-cro** -- Upgrade prompts should only appear after the aha moment is reached; never show paywalls during initial onboarding
- **page-cro** -- When the bottleneck is the marketing page (users are not signing up), optimize the page before optimizing onboarding
- **customer-success-manager** -- For enterprise accounts, human-assisted onboarding complements product-led flows; CS team should monitor activation metrics
