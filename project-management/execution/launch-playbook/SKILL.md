---
name: launch-playbook
description: >
  Internal and external launch coordination playbook covering pre-launch,
  launch day, and post-launch with run-of-show, comms, RACI, rollback, and
  retro. Use to coordinate a GA launch, major release, or re-launch.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: launch, three-launches, dark-launch, raci, progressive-rollout
---
# Launch Playbook (Internal + External Coordination)

## Overview

A complete launch coordination playbook for software products and features. It covers the three windows that matter -- pre-launch (T-30 to T-1), launch day (T-0), and post-launch (T+1 to T+30) -- and produces five concrete artifacts: a run-of-show, an internal comms plan, an external comms checklist, a rollback plan, and a post-launch retro template.

Most failed launches are not failed builds; they are failed coordination. Engineering ships on time, but support has not been trained, sales does not have collateral, the changelog is wrong, the rollback path was never tested, and the executive sponsor hears about a customer complaint before hearing about the launch. This playbook prevents those failures by assigning every owner and every artifact before T-30.

## Core Capabilities

- **Three-launches sequencing** — Cagan's alpha/beta/GA model de-risks the launch; this skill owns the GA window.
- **T-30 to T+30 timeline** — day-by-day pre-launch, launch-day, and post-launch action plan across all workstreams.
- **Launch-type selection** — big bang vs progressive rollout vs dark launch decision rules (and how to combine them).
- **RACI ownership** — every workstream assigned across PM, Eng, PMM, Sales, Support, Legal, Exec.
- **Five artifacts** — run-of-show, internal comms plan, external comms checklist, rollback plan, post-launch retro.

## When to Use

- **GA after closed beta** -- A feature is exiting beta (see `beta-program/`) and needs coordinated launch.
- **Major version release** -- Significant new functionality with cross-functional dependencies (sales enablement, support training, legal review).
- **Re-launch / repositioning** -- An existing feature is being relaunched with new positioning, pricing, or audience.
- **High-blast-radius change** -- Infrastructure migration, pricing change, or breaking API change requiring tightly coordinated comms.

**When NOT to use:** continuous-delivery bug fixes and minor improvements (use `release-notes/` only); internal-only changes with no external comms (use a release runbook); product sunsets and deprecations (use `eol-communication/`).

## Clarify First

Before building the launch plan, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Launch date (T-0)** — anchors the entire T-30→T+30 timeline and every artifact deadline
- [ ] **Launch type** — big bang / progressive rollout / dark launch drives the run-of-show and the rollback plan
- [ ] **Cross-functional owners (RACI)** — every workstream named across PM/Eng/PMM/Sales/Support/Legal; a missing owner is the #1 cause of failed launches
- [ ] **Exec sponsor** — holds go/no-go authority and receives the T-1/T+1/T+7/T+30 updates

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

1. **Kickoff at T-30.** Confirm date, launch type, and exec sponsor; open the run-of-show and internal comms plan assets.
2. **Assign the RACI** within 48 hours — every workstream named.
3. **Build and sign off the five artifacts before T-7**; test the rollback drill by T-7.
4. **Go/no-go at T-3**, run launch day from one run-of-show, stabilize T+1 to T+7, run the 30-day retro.

Full timeline tables, RACI matrix, launch-type rules, and the 10-step workflow are in `references/launch-timeline-and-execution.md`.

## References

- `references/launch-timeline-and-execution.md` — read this when planning/running the launch: three-launches framework, full T-30→T+30 timeline, launch-type selection, RACI matrix, 10-step workflow, troubleshooting, and success criteria.
- `references/launch-coordination-guide.md` — read this for the reasoning behind the playbook: three-launches sequencing, RACI worked examples, big-bang vs progressive decision rules, and anti-patterns.
- `references/red-flags.md` — read this before signing off any launch artifact: common failure modes with bad/good examples and fixes.
- `assets/launch-run-of-show.md` — hourly run-of-show template for launch day.
- `assets/internal-comms-plan.md` — pre-launch, launch-day, and post-launch internal comms templates.
- `assets/external-comms-checklist.md` — T-30 to T-0 checklist for press, blog, social, email, sales enablement, support training, and legal review.
- `assets/rollback-plan.md` — rollback decision matrix, drill checklist, and execution runbook template.
- `assets/post-launch-retro.md` — 7-day and 30-day retrospective template.
- Cagan, Marty. *Inspired: How to Create Tech Products Customers Love*. Wiley, 2018.

## Scope & Limitations

**In Scope:** GA launch coordination across Engineering, Product, PMM, Sales, Support, Legal; run-of-show, rollback plan, comms plans, post-launch retrospective; big bang, progressive rollout, and dark launch patterns; T-30 to T+30 timeline; RACI assignment for cross-functional launches.

**Out of Scope:** Beta program execution (`beta-program/`); release notes content generation (`release-notes/`); end-of-life / sunset communication (`eol-communication/`); incident response runbooks (`delivery-manager/` and engineering on-call); marketing campaign performance analysis beyond the 30-day window (handoff to demand gen).

**Important Caveats:** A launch is not a moment; it is a 60-day window (T-30 to T+30) -- staff accordingly. The single most common cause of failed launches is a missing RACI assignment, not a missing artifact: if you can name the artifact but not the owner, the artifact will not exist. Big-bang launches concentrate risk on one date; default to progressive rollout unless marketing leverage justifies the risk.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `beta-program/` | Receives from | Greenlit beta hands off testimonials, known issues, and pricing decision |
| `create-prd/` | Receives from | PRD provides positioning, segments, and v1 scope |
| `release-notes/` | Feeds into | Launch produces the GA release notes |
| `daci-framework/` | Uses | Major launch decisions (go/no-go, rollback) use DACI |
| `eol-communication/` | Complementary | Launches that replace older features trigger sunset comms |
| `delivery-manager/` | Uses | Deployment, on-call rota, and rollback execution |
| `senior-pm/` | Reports to | Exec sponsor receives T-1, T+1, T+7, T+30 updates |
| `summarize-meeting/` | Feeds into | War-room standups and retro produce structured summaries |
| `status-update-generator/` | Feeds into | Post-launch metrics roll up into weekly status |
