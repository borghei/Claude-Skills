---
name: beta-program
description: >
  Closed beta program playbook covering recruitment, success criteria,
  communication cadence, and beta-to-GA exit gates.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: beta-program, kano-model, cohort-design, beta-to-ga-gates
  tags:
    - beta-program
    - early-access
    - success-criteria
    - ga-readiness
---
# Closed Beta Program Playbook

## Overview

A structured playbook for running a closed beta that produces clear learning, retained design partners, and an unambiguous decision on whether to proceed to general availability. Most betas fail not because the product is wrong, but because the program is run informally: recruitment is opportunistic, success criteria are implicit, communication is sporadic, and exit gates are never defined. This skill replaces all of that with concrete templates and decision rules.

A good closed beta runs 4-8 weeks, recruits 10-30 participants from three concentric cohorts ("friends, family, fanatics"), publishes a weekly cadence the team commits to, and exits on pre-agreed criteria rather than the calendar. The outputs are a beta program plan, a recruitment script, a weekly cadence template, and an exit memo that either greenlights GA, extends the beta, or kills the feature.

## Core Capabilities

- **Cohort design** — sequence recruitment through Friends → Family → Fanatics rings of decreasing trust and increasing signal.
- **Kano scoping** — decide the beta feature set (Must-be / Performance / Delight) so the beta produces quotable testimonials, not neutral feedback.
- **Exit gates** — quantitative + qualitative success criteria set *before* recruitment, resolving to Greenlight / Extend / Pivot / Kill.
- **Weekly cadence** — a committed Monday→Friday communication rhythm that keeps a beta from dying of silence.

## When to Use

- **Pre-GA validation** -- A feature has cleared internal alpha but needs external validation under real workloads before a public launch.
- **High-risk feature** -- Significant blast radius, regulatory exposure, or pricing changes that warrant a controlled rollout to a small group first.
- **Design partner program** -- Recruiting a small set of customers whose feedback shapes v1 scope and pricing.
- **Enterprise rollout** -- New module that needs reference customers and case studies before broad sales enablement.

## When NOT to Use

- Continuous trunk-based delivery where every change ships to all users behind feature flags (use `launch-playbook/` and a progressive rollout instead).
- Pure usability testing with 5-7 participants (use a research protocol, not a beta program).
- Internal-only dogfooding (run a 2-week alpha with engineering and customer-facing staff).

## Clarify First

Before building the beta plan, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Beta hypothesis & headline outcome:** what you are trying to learn and the one result that matters (drives the whole plan and which exit gates you set).
- **Exit gates:** the quantitative + qualitative success criteria, agreed *before* recruiting (resolve to Greenlight / Extend / Pivot / Kill — the decision rule of the program).
- **Target cohort & size:** Friends / Family / Fanatics mix and participant count (drives the recruitment script and how you weight feedback).
- **Duration:** the 4-8 week window (drives the weekly cadence and when the exit memo is due).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

1. Frame the beta hypothesis, target cohort, and headline outcome (from `create-prd/`).
2. Set exit gates in `assets/beta-program-plan.md` and get PM + Eng + sponsor sign-off **before** recruiting.
3. Recruit via `assets/recruitment-script.md` (over-recruit 2x), then stand up the comms channel and publish the cadence on day 1.
4. Run the weekly cadence (`assets/weekly-cadence-template.md`); review the exit memo (`assets/exit-memo.md`) at week N for a Greenlight / Extend / Pivot / Kill decision.

See `references/beta-framework.md` for the full framework tables, step-by-step workflow, troubleshooting, and success criteria.

## Anti-Patterns

### Recruiting only friends
**Mistake:** The cohort is 30 employees and 5 advisor friends, with no Fanatics cold-recruited from the ICP.
**Why it happens:** Friends say yes within two days, and cold recruiting is slow.
**Instead:** Sequence Friends, then Family, then Fanatics, and keep Fanatics at 30% of the cohort or more. Screen them for active pain in the problem area.

### Recruitment that leads with the feature
**Mistake:** The outreach email opens "We're launching an exciting new AI assistant, want to try it?"
**Why it happens:** The team is proud of what it built and leads with it.
**Instead:** Name the participant's problem in the first paragraph, then the ask (hours per week, duration) and the payoff. Target people who described this pain in discovery, starting from `assets/recruitment-script.md`.

### Building one-offs for a single participant
**Mistake:** The largest beta customer asks for a custom export format, and engineering builds it in week 3 for that customer alone.
**Why it happens:** The participant is a paying account, and keeping them happy feels like protecting the beta.
**Instead:** Log the request in the `customer-feedback-triage/` queue with the rest of the beta input. Commit to it for v1.1 only if the broader signal supports it, and track sales-promised customizations separately.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

- `references/beta-framework.md` -- Full framework (cohort, Kano, success gates, cadence, exit gates), the 8-step workflow, troubleshooting matrix, and success criteria. Read this when building the plan, setting gates, running the cadence, or diagnosing problems.
- `references/beta-program-guide.md` -- Practical reference guide: why betas fail, cohort sequencing, Kano deep dive, exit-gate worked examples, common failure modes. Read this for narrative depth and worked examples.
- `references/red-flags.md` -- Bad-vs-good examples for the beta plan, recruitment script, cadence, and exit memo. Read this to review beta artifacts before opening recruitment.
- `assets/beta-program-plan.md` -- Beta program plan template with gates, cohort sizing, timeline.
- `assets/recruitment-script.md` -- Email/DM templates for the three cohorts plus screening questions.
- `assets/weekly-cadence-template.md` -- Monday digest, Tuesday office hours, Wednesday review, Friday snapshot templates.
- `assets/exit-memo.md` -- Exit-gate decision memo template (Greenlight / Extend / Pivot / Kill).
- Kano, Noriaki. "Attractive Quality and Must-Be Quality." Journal of the Japanese Society for Quality Control, 1984.

## Scope & Limitations

**In Scope:**
- Closed beta planning, recruitment, cadence, and exit-gate decisions
- Three-cohort sequencing (Friends, Family, Fanatics)
- Kano scoping for beta feature set
- Weekly communication templates and exit memo
- Beta-to-GA handoff to `launch-playbook/`

**Out of Scope:**
- Public open beta or waitlist management (different mechanics; treat as a soft launch via `launch-playbook/`)
- A/B testing and statistical experiment design (see `discovery/brainstorm-experiments/`)
- Pricing experiments (run a dedicated pricing test, not piggybacked on beta)
- Marketing campaign execution for the beta (light recruitment only; full GTM lives in `launch-playbook/`)

**Important Caveats:**
- A 30-person closed beta is not statistically representative. Treat outcome metrics as directional, not conclusive.
- Friends-cohort feedback is biased toward "this is great" -- weight Fanatics-cohort feedback 2x in the exit decision.
- If your beta participants are also paying customers, any service disruption is a real incident. Run beta features behind a feature flag with a documented rollback path (see `delivery-manager/`).

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `create-prd/` | Receives from | PRD defines the hypothesis and headline outcome that beta gates measure |
| `discovery/identify-assumptions/` | Receives from | Riskiest assumptions become the beta's primary learning goals |
| `discovery/brainstorm-experiments/` | Complementary | Beta is one experiment type; brainstorm-experiments covers smaller/faster alternatives |
| `daci-framework/` | Uses | DACI driver owns the exit-gate decision |
| `launch-playbook/` | Feeds into | Greenlit beta hands testimonials, case studies, and known issues to launch |
| `release-notes/` | Feeds into | Beta release notes preview the GA changelog |
| `summarize-meeting/` | Complementary | Office hours and 1:1 notes become structured weekly summaries |
| `senior-pm/` | Reports to | Exec sponsor receives the exit memo and signs the GA decision |
