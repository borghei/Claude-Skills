---
name: incident-commander
description: >
  Production incident response. Use when handling incidents, classifying severity,
  reconstructing timelines, writing postmortems, generating comms templates, or building
  response playbooks with severity scoring and RCA frameworks.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: incident-response
  tier: POWERFUL
  updated: 2026-11-08
  tags: [incident-response, severity-classification, rca, postmortem]
  python-tools: severity_classifier.py, timeline_reconstructor.py, postmortem_generator.py, incident_classifier.py, incident_timeline_builder.py, pir_generator.py
  tech-stack: python, json, markdown
---
# Incident Commander

Run a production incident from declaration to post-incident review: set severity, coordinate response and comms, rebuild the timeline, and write a review whose action items prevent a repeat. The agent's judgment drives the live incident; the scripts score, structure and draft.

## When to Use

- An incident is active: decide severity, establish command, mitigate, communicate.
- An incident is over: reconstruct the timeline, find root causes, assign action items.
- Designing escalation paths, comms templates, response playbooks or SLA/error-budget policy.

## Clarify First

Settle the inputs that change the work. When one is missing and would not change the result, use a sensible default and say which.

- **Active or post-incident?** Active: ask only for impact (who and how many are affected, revenue, data or security exposure) and what is already being done, then give severity and the first comms. Do not start an RCA during an active incident.
- **Post-incident:** the event sources (alerts, chat, deploys) and the format the organisation uses for reviews.
- **RCA method** (post-incident only): 5 Whys for a single causal chain, Fishbone for many contributing factors, Bow Tie for safety/security-style incidents.

If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

### Active incident

1. Set severity from impact, using the matrix below. The scorer helps but does not decide; when in doubt, pick the higher severity and downgrade later.
2. Name the incident commander, open the channel, post the first internal update and (SEV1/SEV2) the status page within the response window.
3. Mitigate before diagnosing: roll back the last change, fail over, shed load. Record every action with a timestamp.
4. Update on the cadence for the severity until resolved; then declare resolved and schedule the review.

| Severity | Typical impact | First response | Update cadence |
|----------|----------------|----------------|----------------|
| SEV1 | Core service down, > 75% of users, data loss, or a security breach with customer data | Immediate; IC within 5 min; execs within 15 min | Every 15 min |
| SEV2 | Major degradation, 25-75% of users, no workaround, high revenue impact | Within 15 min | Every 30 min |
| SEV3 | Partial degradation, < 25% of users, workaround exists | Within 1 h | Every 2 h |
| SEV4 | Cosmetic or internal, no customer impact | Next business day | As needed |

Full criteria, escalation paths and examples: [references/incident_severity_matrix.md](references/incident_severity_matrix.md).

### Post-incident review

1. Rebuild the timeline from every source and check the gaps (no events for long stretches usually mean missing data, not inactivity).
2. Compute MTTD / time to mitigate / MTTR and compare with your targets.
3. Find root causes and contributing factors with the chosen RCA method; blameless, about systems and decisions.
4. Write action items that would have prevented or shortened this incident, each with an owner, priority and deadline.
5. Validate the review before sharing: every action item has an owner, every timeline gap is explained, and the root cause is a mechanism, not "human error".

## Quick Start

```bash
# Severity: multi-dimensional score from the shared incident schema (SEV2 on the sample)
python3 scripts/severity_classifier.py assets/sample_incident_data.json --format text
# Quick triage from free text only (keyword heuristic; advisory)
python3 scripts/incident_classifier.py --input assets/sample_incident_classification.json --format text
# Timeline with lifecycle phases and gap analysis
python3 scripts/timeline_reconstructor.py --input assets/sample_timeline_events.json --detect-phases --gap-analysis --format markdown
# Review documents
python3 scripts/postmortem_generator.py assets/sample_incident_data.json --format markdown
python3 scripts/pir_generator.py --incident assets/sample_incident_pir_data.json --rca-method fishbone --action-items
```

## Tools Overview

Use one tool per job. Two input schemas are in play; pick the tool that matches the data you have.

| Job | Primary tool | Input | Alternative |
|-----|--------------|-------|-------------|
| Severity | `severity_classifier.py <file>` — weighted revenue, user scope, data/security, criticality, blast radius; escalation path | Shared incident schema (`assets/sample_incident_data.json`: `incident`, `impact`, `signals`, `context`, `events`, `resolution`, `action_items`) | `incident_classifier.py --input <file>` — keyword triage from `{description, service, affected_users, business_impact}`; its confidence reflects input completeness and is capped at 85% |
| Timeline | `timeline_reconstructor.py --input <events.json>` — merge multi-source events, lifecycle phases (detection, triage, mitigation, resolution, review), gaps | List of `{timestamp, source, type, message, severity, actor}` (`assets/sample_timeline_events.json`) | `incident_timeline_builder.py <file>` — MTTD/MTTR and comms from the shared incident schema |
| Review | `postmortem_generator.py <file>` — exec summary, metrics vs benchmarks, 5 Whys, coverage gaps; timeline taken from `timeline` or derived from typed `events` | Shared incident schema | `pir_generator.py --incident <file> --rca-method {five_whys,fishbone,timeline,bow_tie}` — PIR from the flat schema in `assets/sample_incident_pir_data.json` |

Exit codes: 0 report produced, 2 bad input (missing file, invalid JSON, wrong shape). `severity_classifier.py` exits 0 for any classified severity; add `--fail-on SEV1|SEV2|SEV3` to exit 1 when the incident is at or above that level (for paging or CI gates). It also accepts `--format json|markdown`; each tool lists its flags under `--help`.

## Anti-Patterns

**Mistake:** Letting the keyword classifier set severity during a live incident.
**Why it happens:** A number with a percentage looks authoritative.
**Instead:** Decide from impact with the matrix; use the scorers to check yourself and to document why.

**Mistake:** Root-causing while the service is still down.
**Why it happens:** Engineers want to understand before they act.
**Instead:** Mitigate first (rollback, failover, feature flag off); investigate once users are no longer affected.

**Mistake:** Action items without owners or dates, or "be more careful".
**Why it happens:** The review meeting runs out of time.
**Instead:** Each item names an owner, a deadline and the mechanism it changes (a test, an alert, a guardrail). The review is not done until that is true.

## Files

- `scripts/` — the six tools above (three primary, three alternatives).
- `assets/sample_incident_data.json` (shared schema), `assets/sample_incident_classification.json` and `assets/simple_incident.json` (triage input), `assets/sample_timeline_events.json` and `assets/simple_timeline_events.json` (events), `assets/sample_incident_pir_data.json` (PIR input), `assets/incident_report_template.md`, `assets/runbook_template.md`.
- `expected_outputs/` — reference outputs for the samples.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/response-playbooks.md](references/response-playbooks.md)** — quick-start commands, the detection-to-resolution and post-incident-review workflows, escalation management, anti-patterns, and tool troubleshooting. Read when running an incident end-to-end or using the scripts.
- **[references/incident-response-framework.md](references/incident-response-framework.md)** — PagerDuty/Google SRE/Atlassian framework comparison, role definitions (IC, Comms, Ops, Scribe, SME, Liaison), communication protocols, escalation matrix, and the 7-phase incident lifecycle. Read when designing the response process or assigning roles.
- **[references/incident_severity_matrix.md](references/incident_severity_matrix.md)** — full SEV-1 to SEV-4 impact criteria, response requirements, escalation paths, classification guidelines, decision tree, and examples. Read when classifying or calibrating severity.
- **[references/communication_templates.md](references/communication_templates.md)** — ready-to-use internal, executive, customer, status-page, escalation, and resolution templates by severity. Read when drafting any incident communication.
- **[references/rca_frameworks_guide.md](references/rca_frameworks_guide.md)** — step-by-step 5 Whys, Fishbone, Timeline, and Bow Tie frameworks with templates, selection guidance, and anti-patterns. Read when performing root cause analysis.
- **[references/sla-management-guide.md](references/sla-management-guide.md)** — SLI/SLO/SLA hierarchy, error-budget policy, burn-rate alerting, breach handling, and incident-to-SLA mapping with worked examples. Read when assessing or communicating SLA impact.

## Scope & Limitations

**Covers:** severity classification, timeline reconstruction, post-incident reviews, RCA frameworks, escalation and communication templates, SLA/error-budget tracking. Tools are offline and deterministic; they read JSON and write text, JSON or Markdown.

**Does not cover:** monitoring and alerting setup (`engineering/observability-designer`), security forensics (`engineering/senior-secops`), deployment and rollback execution (`engineering/release-orchestrator`), or debugging the underlying fault (`engineering/bug-diagnosis`).
