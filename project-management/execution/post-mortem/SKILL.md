---
name: post-mortem
description: >
  Blameless post-mortem expert for incidents, outages, regressions, customer
  escalations, missed launches, and failed experiments. Pairs Google SRE
  practice with Allspaw / Dekker / Perrow systems thinking.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: [post-mortem, incident-management, rca, blameless, 5-whys]
  tags: [post-mortem, rca, blameless, incident, sre, five-whys, causal-tree]
---
# Post-Mortem (Blameless Incident Review)

## Overview

A post-mortem is a structured, blameless review held after an incident, outage, regression, missed launch, or failed experiment. The goal is not to assign fault but to learn how the system (people, process, code, and organization) produced the outcome, and to commit to durable changes that reduce the chance of recurrence.

This skill operationalizes the Google SRE blameless post-mortem template, the Etsy "morgue" tradition, John Allspaw's "How Complex Systems Fail" reading, Charles Perrow's Normal Accident Theory, and Sidney Dekker's *Field Guide to Understanding "Human Error"*. Where the companion `discovery/pre-mortem/` skill imagines failure before it happens, post-mortem learns from failure that already did.

## Core Capabilities

- **Severity classification** — Sev 0-4 + near-miss thresholds, with post-mortem requirement and SLA per level
- **Blameless facilitation** — five ground rules, the Dekker New View, hindsight/counterfactual removal, the Allspaw test
- **10-section authoring** — header → summary → impact → timeline → what went well/wrong → factors → RCA → actions → lessons
- **Root-cause analysis** — 5 Whys for clear chains, Causal Tree for multi-factor Sev 0/1/2; root-cause vs contributing-factor
- **Action-item discipline** — single owner, real ticket, testable acceptance criteria, recurring completion audit
- **Distribution & archive** — audience-appropriate formats; searchable, service-tagged archive

## When to Use

- **Sev 1 / Sev 2 incident** — customer-facing outage, data loss, security event, payments failure, or significant regression.
- **Sev 3 with novelty** — worth a post-mortem if it surfaced a failure class the team has not seen before.
- **Missed launch or rolled-back release** — the launch itself is the incident.
- **Failed experiment with a negative business outcome** — e.g. a pricing test that depressed revenue.
- **Customer escalation** — an exec customer call where the product was the proximate cause.
- **Near miss** — the deploy that "almost" took the site down; some of the highest-leverage learning a team gets.

If the incident is below the severity threshold and the team has seen the same class of failure recently, document the recurrence in the existing post-mortem rather than producing a new one.

## Clarify First

Before authoring the post-mortem, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Severity level** — Sev 0-4 / near-miss sets the template depth, the SLA window, and whether 5 Whys or a Causal Tree is required
- [ ] **Incident timeline / chat transcript** — the source for the Timeline and Impact sections; without it the reconstruction is guesswork
- [ ] **Customer / business impact** — scope, duration, and who was affected drives both the Impact section and the severity itself
- [ ] **Root-cause method** — 5 Whys for a clear single chain vs Causal Tree for multi-factor Sev 0/1/2; drives the RCA section

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

1. At incident close, the incident commander assigns an author who opens `assets/post_mortem_template.md`.
2. Scaffold Header, Summary, Impact, and Timeline from the incident chat transcript.
3. Within the SLA window (Sev 1: 5 business days, Sev 2: 7), draft the remaining sections, run the chosen root-cause method, and hold a 60-90 min blameless review.
4. Apply the Allspaw test, file every action item as a real ticket with an owner and due date, then publish to the searchable archive.

The blameless principles, severity thresholds, full template, workflow, and root-cause methods all live in the references below.

## References

- **[references/post-mortem-process.md](references/post-mortem-process.md)** — severity thresholds, the 10-section template, the Day 0 → Day 30 workflow, action-item follow-through, distribution/archive practice, and the assets inventory. Read when running a post-mortem end to end.
- **[references/blameless-culture-guide.md](references/blameless-culture-guide.md)** — what blameless means, the Dekker reframe, blameful vs blameless phrasing, hindsight bias, counterfactuals, establishing the culture, plus the five ground rules and the Allspaw test. Read when facilitating or when a draft feels blameful.
- **[references/5-whys-vs-causal-tree.md](references/5-whys-vs-causal-tree.md)** — both root-cause methods with worked examples, the choose-between table, and the root-cause vs contributing-factors distinction. Read before the root-cause section of the meeting.
- **[references/red-flags.md](references/red-flags.md)** — 12 anti-patterns (blame language, ownerless action items, single root cause, second-mortems...), plus the troubleshooting table and success criteria. Read before publishing or signing off.
- **assets** — [post_mortem_template.md](assets/post_mortem_template.md) (SRE 10-section template), [incident_timeline_worksheet.md](assets/incident_timeline_worksheet.md) (timeline prompts), [action_item_tracker.md](assets/action_item_tracker.md) (cross-incident tracker), [what_went_well_prompts.md](assets/what_went_well_prompts.md) (positive-observation prompts).
- Foundational reading: Google SRE "Postmortem Culture"; Allspaw "Blameless PostMortems and a Just Culture" (2012); Cook "How Complex Systems Fail" (1998); Perrow *Normal Accidents* (1984); Dekker *Field Guide* (2014) and *Just Culture* (2017).

## Scope & Limitations

**In Scope:** Post-mortem authoring for incidents, outages, regressions, missed launches, failed experiments, customer escalations, and near misses. Severity classification, blameless facilitation, 5 Whys, Causal Tree analysis, action-item tracking, distribution and archival practice.

**Out of Scope:** Live incident command and on-call coordination (see `delivery-manager/`). Sprint retrospectives on team practice (see `sprint-retrospective/`). Risk surfacing before launch (see `discovery/pre-mortem/`). Quantitative reliability engineering and error-budget policy (see `engineering/` skills if present).

**Important Caveats:** Blameless culture is a prerequisite, not an output — if management uses post-mortems as a performance signal, the documents become sanitized; establish the separation in writing. Regulated industries (medical devices, aviation, financial services) that require named accountability should run a parallel internal blameless post-mortem alongside the regulator-facing report. A post-mortem is a learning artifact, not a fixing artifact: the fix lives in the action items and their follow-through, so one with zero completed action items is a failed post-mortem. (Cook's 4-page "How Complex Systems Fail" is worth reading before facilitating a complex Sev 0/1 — linked in the blameless culture guide.)

## Integration Points

| Integration | Direction | What flows |
|---|---|---|
| `discovery/pre-mortem/` | Bidirectional | Post-mortem findings update next launch's pre-mortem risk register; pre-mortem mitigations become post-mortem-checked controls |
| `delivery-manager/` | Receives from | Incident response context, severity classification, on-call handoffs |
| `sprint-retrospective/` | Bidirectional | Team-practice retros surface incident patterns; post-mortems feed retro themes |
| `daci-framework/` | Feeds into | Action items use DACI to assign owner (D), accountable (A), consulted, informed |
| `execution/dependency-map/` | Receives from | Cross-team contributing factors map to dependency-graph nodes |
| `execution/status-update-generator/` | Feeds into | Sev 0/1 incidents surface in weekly executive status updates |
| `senior-pm/` | Feeds into | Repeated incident classes feed portfolio risk register via `risk_matrix_analyzer.py` |
| `scrum-master/` | Feeds into | Action items become sprint backlog items with mitigation-focused stories |
