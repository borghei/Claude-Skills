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
  updated: 2026-06-17
  tags: [incident-response, severity-classification, rca, postmortem]
  python-tools: incident_classifier.py, severity_classifier.py, timeline_reconstructor.py, incident_timeline_builder.py, pir_generator.py, postmortem_generator.py
  tech-stack: python, json, markdown
---
# Incident Commander

Classify incident severity, reconstruct timelines from heterogeneous event sources, and generate structured post-incident reviews with root cause analysis and action items. Codifies PagerDuty, Google SRE, and Atlassian incident-management practices into severity scoring, escalation matrices, communication templates, RCA frameworks, and SLA/error-budget tracking.

## Core Capabilities

- **Severity classification** — multi-dimensional scoring (revenue, user scope, data/security risk, service criticality, blast radius) into SEV-1 to SEV-4 with confidence and escalation paths.
- **Timeline reconstruction** — chronological timelines from logs, alerts, Slack, and deploy events with phase detection and gap analysis.
- **Post-incident review** — PIRs with 5 Whys, Fishbone, Timeline, or Bow Tie RCA plus categorized action items (owner, priority, deadline).
- **Postmortem quality** — coverage-gap detection, action-item quality scoring, MTTD/MTTR benchmarking.
- **Communication & escalation** — severity-specific internal/executive/customer/status-page templates; technical (L1-L4) and business escalation matrices with time-based triggers.
- **SLA / error-budget tracking** — SLI/SLO/SLA hierarchy, error budgets, burn-rate alerting, and breach handling.

## When to Use

- Handling an active incident — classify severity, establish command, mitigate, communicate.
- Running a post-incident review — reconstruct timeline, perform RCA, assign action items.
- Managing escalation — apply technical and business escalation paths by severity and elapsed time.
- Building or auditing response playbooks, comms templates, or SLA/error-budget policy.

## Clarify First

Before producing the artifact, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task & deliverable** — classify severity, reconstruct a timeline, or generate a PIR/postmortem (selects `severity_classifier.py` vs `timeline_reconstructor.py` vs `pir_generator.py`/`postmortem_generator.py`)
- [ ] **Incident input data** — the incident/events JSON with severity dimensions (revenue, user scope, data/security risk, blast radius) (the input the scripts parse)
- [ ] **RCA method** — 5 Whys, Fishbone, Timeline, or Bow Tie (sets `pir_generator.py --rca-method` and the postmortem structure)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `incident_classifier.py` | Classify severity, recommend response teams and comms templates | `python scripts/incident_classifier.py --input incident.json --format text` |
| `severity_classifier.py` | Multi-dimensional severity score with escalation path | `python scripts/severity_classifier.py incident.json --format markdown` |
| `timeline_reconstructor.py` | Reconstruct timeline from timestamped events with phase + gap analysis | `python scripts/timeline_reconstructor.py --input events.json --detect-phases --gap-analysis --format markdown` |
| `incident_timeline_builder.py` | Build structured timeline with MTTD/MTTR and comms templates | `python scripts/incident_timeline_builder.py incident_data.json --format markdown` |
| `pir_generator.py` | Generate Post-Incident Review with RCA and action items | `python scripts/pir_generator.py --incident incident.json --rca-method fishbone --action-items` |
| `postmortem_generator.py` | Generate postmortem with 5-Whys, benchmarks, coverage gaps | `python scripts/postmortem_generator.py incident_data.json --format markdown` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/response-playbooks.md](references/response-playbooks.md)** — quick-start commands, the detection-to-resolution and post-incident-review workflows, escalation management, anti-patterns, and tool troubleshooting. Read when running an incident end-to-end or using the scripts.
- **[references/incident-response-framework.md](references/incident-response-framework.md)** — PagerDuty/Google SRE/Atlassian framework comparison, role definitions (IC, Comms, Ops, Scribe, SME, Liaison), communication protocols, escalation matrix, and the 7-phase incident lifecycle. Read when designing the response process or assigning roles.
- **[references/incident_severity_matrix.md](references/incident_severity_matrix.md)** — full SEV-1 to SEV-4 impact criteria, response requirements, escalation paths, classification guidelines, decision tree, and examples. Read when classifying or calibrating severity.
- **[references/communication_templates.md](references/communication_templates.md)** — ready-to-use internal, executive, customer, status-page, escalation, and resolution templates by severity. Read when drafting any incident communication.
- **[references/rca_frameworks_guide.md](references/rca_frameworks_guide.md)** — step-by-step 5 Whys, Fishbone, Timeline, and Bow Tie frameworks with templates, selection guidance, and anti-patterns. Read when performing root cause analysis.
- **[references/sla-management-guide.md](references/sla-management-guide.md)** — SLI/SLO/SLA hierarchy, error-budget policy, burn-rate alerting, breach handling, and incident-to-SLA mapping with worked examples. Read when assessing or communicating SLA impact.

## Scope & Limitations

**Covers:** severity classification, timeline reconstruction, PIR/postmortem generation, RCA frameworks, escalation matrices, communication templates, and SLA/error-budget tracking. Tools are deterministic stdlib Python (no ML/LLM calls), accepting JSON input and emitting text/JSON/markdown.

**Does NOT cover:** live monitoring/alerting infrastructure (feeds in from `senior-devops`), security forensics (see `senior-secops`), or deployment/rollback execution (see `release-orchestrator`).

## Integration Points

| Skill | Integration |
|-------|-------------|
| `senior-devops` | Monitoring alerts feed timeline; runbook templates inform playbooks |
| `senior-secops` | Security incidents auto-escalate to SEV-1; breach indicators trigger SecOps response |
| `release-orchestrator` | Deployment events feed timeline; rollback data informs release gates |
| `senior-architect` | Architectural root causes escalate to architecture review |
| `code-reviewer` | PIR action items route to code review workflows |
