---
name: incident-commander
description: >
  Use when handling production incidents, classifying severity, reconstructing
  timelines, writing postmortems, generating communication templates, or
  building incident response playbooks. Provides automated severity scoring,
  RCA frameworks (5 Whys, Fishbone, Bow Tie), and structured PIR generation.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: incident-response
  tier: POWERFUL
  updated: 2026-04-02
  tags: [incident-response, severity-classification, rca, postmortem]
  python-tools: incident_classifier.py, severity_classifier.py, timeline_reconstructor.py, incident_timeline_builder.py, pir_generator.py, postmortem_generator.py
  tech-stack: python, json, markdown
---
# Incident Commander

The agent classifies incident severity, reconstructs timelines from heterogeneous event sources, and generates structured post-incident reviews with root cause analysis and action items.

---

## Quick Start

```bash
# Classify an incident (JSON or stdin)
echo '{"description": "Database connections timing out", "affected_users": "80%", "business_impact": "high"}' \
  | python scripts/incident_classifier.py --format text

# Multi-dimensional severity scoring
python scripts/severity_classifier.py incident.json --format markdown

# Reconstruct timeline with phase detection and gap analysis
python scripts/timeline_reconstructor.py --input events.json --detect-phases --gap-analysis --format markdown

# Build structured timeline with MTTD/MTTR metrics
python scripts/incident_timeline_builder.py incident_data.json --format markdown

# Generate Post-Incident Review
python scripts/pir_generator.py --incident incident.json --rca-method fishbone --action-items --format markdown

# Generate postmortem with benchmark comparisons
python scripts/postmortem_generator.py incident_data.json --format markdown
```

## Tools Overview

| Tool | Input | Output |
|------|-------|--------|
| `incident_classifier.py` | Incident description JSON | Severity level, response teams, communication templates |
| `severity_classifier.py` | Incident data with impact/signals | Multi-dimensional score across 5 weighted dimensions |
| `timeline_reconstructor.py` | Timestamped events array | Chronological timeline with phases and gap analysis |
| `incident_timeline_builder.py` | Incident + events JSON | Timeline with MTTD/MTTR, phase distribution, comms templates |
| `pir_generator.py` | Incident data + optional timeline | PIR document with RCA (5 Whys, Fishbone, Timeline, Bow Tie) |
| `postmortem_generator.py` | Incident + resolution + action items | Postmortem with benchmarks, factor analysis, coverage gaps |

---

## Workflow 1: Incident Response (Detection to Resolution)

**Step 1 -- Classify severity.**

```bash
python scripts/severity_classifier.py incident.json --format json
```

The agent scores across five dimensions: revenue impact (25%), user scope (25%), data/security risk (20%), service criticality (15%), blast radius (15%).

| Severity | Definition | Response Time | Comms Cadence |
|----------|-----------|---------------|---------------|
| **SEV-1** | Complete outage, data loss, security breach | 15 min | Every 15 min |
| **SEV-2** | Partial degradation, >25% users affected | 30 min | Every 30 min |
| **SEV-3** | Single feature affected, workaround available | 2 hours | At milestones |
| **SEV-4** | Cosmetic, dev/test only, no user impact | Next business day | Standard cycle |

**Validation checkpoint:** Severity classification includes confidence score and recommended escalation path.

**Step 2 -- Establish command.**

The Incident Commander:
- Assigns within 5 min (SEV-1) or 30 min (SEV-2)
- Creates war room and incident tracking ticket
- Sends initial notification using generated template
- Coordinates between technical teams and stakeholders
- Shields responders from external distractions

**Step 3 -- Investigate and mitigate.**

The agent generates targeted investigation commands based on the affected service:

```bash
kubectl get pods -n production -l app=<service>
kubectl logs -l app=<service> --tail=100
helm history <service> -n production
```

**Decision framework for SEV-1/SEV-2:**
- Bias toward action over analysis
- Prefer rollbacks to risky fixes under pressure
- Document every decision for later review
- Consult SMEs but do not block on them

**Step 4 -- Communicate.**

The agent generates three communication templates per severity:
1. **Internal notification** -- technical details, response team, war room link
2. **Executive summary** -- business impact, ETA, leadership actions required
3. **Customer communication** -- impact scope, what is being done, next update time

**Validation checkpoint:** All stakeholders notified within committed timeframes.

---

## Workflow 2: Post-Incident Review

**Step 1 -- Reconstruct the timeline.**

```bash
python scripts/timeline_reconstructor.py --input events.json --detect-phases --gap-analysis --format markdown
```

The agent accepts events from logs, alerts, Slack messages, and deployment systems. Each event needs a `timestamp` and `description`. Optional fields: `source`, `type`, `actor`, `severity`.

**Supported phases:** detection, declaration, escalation, investigation, mitigation, communication, resolution.

**Step 2 -- Perform root cause analysis.**

```bash
python scripts/pir_generator.py --incident incident.json --timeline timeline.json --rca-method five_whys --action-items
```

Available RCA methods:

| Method | Best For |
|--------|----------|
| `five_whys` | Linear causal chains, quick analysis |
| `fishbone` | Multi-category analysis (People, Process, Technology, Environment) |
| `timeline` | Identifying missed decision points and delays |
| `bow_tie` | Barriers analysis, prevention and mitigation controls |

**Step 3 -- Generate action items.**

The agent categorizes action items as: `immediate_fix`, `process_improvement`, `monitoring_alerting`, `documentation`, `training`, `architectural`, `tooling`.

Each action item includes: title, owner, priority, deadline, success criteria, and dependencies.

**Step 4 -- Validate postmortem quality.**

```bash
python scripts/postmortem_generator.py incident_data.json --format json
```

The agent checks:
- Every contributing factor has at least one action item (coverage gap detection)
- Action items have quality scores (0-100) based on specificity
- MTTD/MTTR benchmarked against industry standards
- Missing actions suggested for uncovered themes

**Validation checkpoint:** Zero coverage gaps. All P0 action items have owners and deadlines within 48 hours.

---

## Workflow 3: Escalation Management

**Technical escalation path:**

| Level | Role | SEV-1 Trigger | SEV-2 Trigger |
|-------|------|---------------|---------------|
| L1 | On-call engineer | Immediate | 15 min |
| L2 | Senior engineer / Team lead | 30 min | 1 hour |
| L3 | Engineering Manager / Staff | 45 min | 2 hours |
| L4 | Director / CTO | 1 hour | 4 hours |

**Business escalation:**

| Severity | Duration | Escalate To |
|----------|----------|-------------|
| SEV-1 | Immediate | VP Engineering |
| SEV-1 | 30 min | CTO + Customer Success VP |
| SEV-1 | 1 hour | CEO + Full Executive Team |
| SEV-2 | 2 hours | VP Engineering |
| SEV-2 | 4 hours | CTO |

---

## Anti-Patterns

1. **Individual blame in postmortems** -- focus on system failures. "Why did the process allow this?" not "Why did Alice do this?"
2. **Skipping PIR for SEV-2** -- every SEV-1 and SEV-2 gets a postmortem within 3 business days.
3. **Action items without owners** -- every item needs a specific person and deadline.
4. **Deploying fixes under pressure without validation** -- validate fixes before declaring resolution; plan for secondary failures.
5. **Communication gaps** -- provide updates even when there is no new information.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Classifier assigns SEV1 to minor issues | Description keywords trigger high severity without impact data | Provide `affected_users` percentage and `business_impact` fields |
| Timeline shows "No valid events found" | Timestamps in unsupported format or missing `timestamp` key | Use ISO-8601, `YYYY-MM-DD HH:MM:SS`, or Unix epoch |
| PIR produces shallow 5 Whys | Incident data lacks detail | Enrich input with `affected_services`, `customer_impact`; supply timeline via `--timeline` |
| Postmortem marks all action items invalid | Missing required fields | Each action item needs `title`, `owner`, `priority`, `deadline` |
| Severity score seems too low | Flat description without structured impact data | Provide full schema with `impact`, `signals`, `context` keys |

---

## References

| Guide | Path |
|-------|------|
| Incident Response Framework | `references/incident-response-framework.md` |
| Severity Matrix | `references/incident_severity_matrix.md` |
| Communication Templates | `references/communication_templates.md` |
| RCA Frameworks Guide | `references/rca_frameworks_guide.md` |
| SLA Management | `references/sla-management-guide.md` |

---

## Integration Points

| Skill | Integration |
|-------|-------------|
| `senior-devops` | Monitoring alerts feed timeline; runbook templates inform playbooks |
| `senior-secops` | Security incidents auto-escalate to SEV-1; breach indicators trigger SecOps response |
| `release-orchestrator` | Deployment events feed timeline; rollback data informs release gates |
| `senior-architect` | Architectural root causes escalate to architecture review |
| `code-reviewer` | PIR action items route to code review workflows |

---

**Last Updated:** April 2026
**Version:** 1.1.0
