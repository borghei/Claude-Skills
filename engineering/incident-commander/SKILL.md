---
name: incident-commander
description: >
  Manages incident response with severity classification, timeline
  reconstruction, and post-incident review generation. Use when handling
  production incidents, writing postmortems, classifying severity, or building
  incident response playbooks.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: incident-response
  tier: POWERFUL
  updated: 2026-03-31
  tags: [incident-response, severity-classification, rca, postmortem]
---
# Incident Commander Skill

**Category:** Engineering Team
**Tier:** POWERFUL
**Author:** Claude Skills Team
**Version:** 1.0.0  
**Last Updated:** February 2026

## Overview

The Incident Commander skill provides a comprehensive incident response framework for managing technology incidents from detection through resolution and post-incident review. This skill implements battle-tested practices from SRE and DevOps teams at scale, providing structured tools for severity classification, timeline reconstruction, and thorough post-incident analysis.

## Key Features

- **Automated Severity Classification** - Intelligent incident triage based on impact and urgency metrics
- **Timeline Reconstruction** - Transform scattered logs and events into coherent incident narratives
- **Post-Incident Review Generation** - Structured PIRs with multiple RCA frameworks
- **Communication Templates** - Pre-built templates for stakeholder updates and escalations
- **Runbook Integration** - Generate actionable runbooks from incident patterns

## Skills Included

### Core Tools

1. **Incident Classifier** (`incident_classifier.py`)
   - Analyzes incident descriptions and outputs severity levels
   - Recommends response teams and initial actions
   - Generates communication templates based on severity

2. **Timeline Reconstructor** (`timeline_reconstructor.py`)
   - Processes timestamped events from multiple sources
   - Reconstructs chronological incident timeline
   - Identifies gaps and provides duration analysis

3. **PIR Generator** (`pir_generator.py`)
   - Creates comprehensive Post-Incident Review documents
   - Applies multiple RCA frameworks (5 Whys, Fishbone, Timeline)
   - Generates actionable follow-up items

## Incident Response Framework

### Severity Classification System

#### SEV1 - Critical Outage
**Definition:** Complete service failure affecting all users or critical business functions

**Characteristics:**
- Customer-facing services completely unavailable
- Data loss or corruption affecting users
- Security breaches with customer data exposure
- Revenue-generating systems down
- SLA violations with financial penalties

**Response Requirements:**
- Immediate escalation to on-call engineer
- Incident Commander assigned within 5 minutes
- Executive notification within 15 minutes
- Public status page update within 15 minutes
- War room established
- All hands on deck if needed

**Communication Frequency:** Every 15 minutes until resolution

#### SEV2 - Major Impact
**Definition:** Significant degradation affecting subset of users or non-critical functions

**Characteristics:**
- Partial service degradation (>25% of users affected)
- Performance issues causing user frustration
- Non-critical features unavailable
- Internal tools impacting productivity
- Data inconsistencies not affecting user experience

**Response Requirements:**
- On-call engineer response within 15 minutes
- Incident Commander assigned within 30 minutes
- Status page update within 30 minutes
- Stakeholder notification within 1 hour
- Regular team updates

**Communication Frequency:** Every 30 minutes during active response

#### SEV3 - Minor Impact
**Definition:** Limited impact with workarounds available

**Characteristics:**
- Single feature or component affected
- <25% of users impacted
- Workarounds available
- Performance degradation not significantly impacting UX
- Non-urgent monitoring alerts

**Response Requirements:**
- Response within 2 hours during business hours
- Next business day response acceptable outside hours
- Internal team notification
- Optional status page update

**Communication Frequency:** At key milestones only

#### SEV4 - Low Impact
**Definition:** Minimal impact, cosmetic issues, or planned maintenance

**Characteristics:**
- Cosmetic bugs
- Documentation issues
- Logging or monitoring gaps
- Performance issues with no user impact
- Development/test environment issues

**Response Requirements:**
- Response within 1-2 business days
- Standard ticket/issue tracking
- No special escalation required

**Communication Frequency:** Standard development cycle updates

### Incident Commander Role

#### Primary Responsibilities

1. **Command and Control**
   - Own the incident response process
   - Make critical decisions about resource allocation
   - Coordinate between technical teams and stakeholders
   - Maintain situational awareness across all response streams

2. **Communication Hub**
   - Provide regular updates to stakeholders
   - Manage external communications (status pages, customer notifications)
   - Facilitate effective communication between response teams
   - Shield responders from external distractions

3. **Process Management**
   - Ensure proper incident tracking and documentation
   - Drive toward resolution while maintaining quality
   - Coordinate handoffs between team members
   - Plan and execute rollback strategies if needed

4. **Post-Incident Leadership**
   - Ensure thorough post-incident reviews are conducted
   - Drive implementation of preventive measures
   - Share learnings with broader organization

#### Decision-Making Framework

**Emergency Decisions (SEV1/2):**
- Incident Commander has full authority
- Bias toward action over analysis
- Document decisions for later review
- Consult subject matter experts but don't get blocked

**Resource Allocation:**
- Can pull in any necessary team members
- Authority to escalate to senior leadership
- Can approve emergency spend for external resources
- Make call on communication channels and timing

**Technical Decisions:**
- Lean on technical leads for implementation details
- Make final calls on trade-offs between speed and risk
- Approve rollback vs. fix-forward strategies
- Coordinate testing and validation approaches

### Communication Templates

#### Initial Incident Notification (SEV1/2)

```
Subject: [SEV{severity}] {Service Name} - {Brief Description}

Incident Details:
- Start Time: {timestamp}
- Severity: SEV{level}
- Impact: {user impact description}
- Current Status: {investigating/mitigating/resolved}

Technical Details:
- Affected Services: {service list}
- Symptoms: {what users are experiencing}
- Initial Assessment: {suspected root cause if known}

Response Team:
- Incident Commander: {name}
- Technical Lead: {name}
- SMEs Engaged: {list}

Next Update: {timestamp}
Status Page: {link}
War Room: {bridge/chat link}

---
{Incident Commander Name}
{Contact Information}
```

#### Executive Summary (SEV1)

```
Subject: URGENT - Customer-Impacting Outage - {Service Name}

Executive Summary:
{2-3 sentence description of customer impact and business implications}

Key Metrics:
- Time to Detection: {X minutes}
- Time to Engagement: {X minutes} 
- Estimated Customer Impact: {number/percentage}
- Current Status: {status}
- ETA to Resolution: {time or "investigating"}

Leadership Actions Required:
- [ ] Customer communication approval
- [ ] PR/Communications coordination  
- [ ] Resource allocation decisions
- [ ] External vendor engagement

Incident Commander: {name} ({contact})
Next Update: {time}

---
This is an automated alert from our incident response system.
```

#### Customer Communication Template

```
We are currently experiencing {brief description of issue} affecting {scope of impact}. 

Our engineering team was alerted at {time} and is actively working to resolve the issue. We will provide updates every {frequency} until resolved.

What we know:
- {factual statement of impact}
- {factual statement of scope}
- {brief status of response}

What we're doing:
- {primary response action}
- {secondary response action}

Workaround (if available):
{workaround steps or "No workaround currently available"}

We apologize for the inconvenience and will share more information as it becomes available.

Next update: {time}
Status page: {link}
```

### Stakeholder Management

#### Stakeholder Classification

**Internal Stakeholders:**
- **Engineering Leadership** - Technical decisions and resource allocation
- **Product Management** - Customer impact assessment and feature implications
- **Customer Support** - User communication and support ticket management
- **Sales/Account Management** - Customer relationship management for enterprise clients
- **Executive Team** - Business impact decisions and external communication approval
- **Legal/Compliance** - Regulatory reporting and liability assessment

**External Stakeholders:**
- **Customers** - Service availability and impact communication
- **Partners** - API availability and integration impacts
- **Vendors** - Third-party service dependencies and support escalation
- **Regulators** - Compliance reporting for regulated industries
- **Public/Media** - Transparency for public-facing outages

#### Communication Cadence by Stakeholder

| Stakeholder | SEV1 | SEV2 | SEV3 | SEV4 |
|-------------|------|------|------|------|
| Engineering Leadership | Real-time | 30min | 4hrs | Daily |
| Executive Team | 15min | 1hr | EOD | Weekly |
| Customer Support | Real-time | 30min | 2hrs | As needed |
| Customers | 15min | 1hr | Optional | None |
| Partners | 30min | 2hrs | Optional | None |

### Runbook Generation Framework

#### Dynamic Runbook Components

1. **Detection Playbooks**
   - Monitoring alert definitions
   - Triage decision trees
   - Escalation trigger points
   - Initial response actions

2. **Response Playbooks**
   - Step-by-step mitigation procedures
   - Rollback instructions
   - Validation checkpoints
   - Communication checkpoints

3. **Recovery Playbooks**
   - Service restoration procedures
   - Data consistency checks
   - Performance validation
   - User notification processes

#### Runbook Template Structure

```markdown
# {Service/Component} Incident Response Runbook

## Quick Reference
- **Severity Indicators:** {list of conditions for each severity level}
- **Key Contacts:** {on-call rotations and escalation paths}
- **Critical Commands:** {list of emergency commands with descriptions}

## Detection
### Monitoring Alerts
- {Alert name}: {description and thresholds}
- {Alert name}: {description and thresholds}

### Manual Detection Signs
- {Symptom}: {what to look for and where}
- {Symptom}: {what to look for and where}

## Initial Response (0-15 minutes)
1. **Assess Severity**
   - [ ] Check {primary metric}
   - [ ] Verify {secondary indicator}
   - [ ] Classify as SEV{level} based on {criteria}

2. **Establish Command**
   - [ ] Page Incident Commander if SEV1/2
   - [ ] Create incident tracking ticket
   - [ ] Join war room: {link/bridge info}

3. **Initial Investigation**
   - [ ] Check recent deployments: {deployment log location}
   - [ ] Review error logs: {log location and queries}
   - [ ] Verify dependencies: {dependency check commands}

## Mitigation Strategies
### Strategy 1: {Name}
**Use when:** {conditions}
**Steps:**
1. {detailed step with commands}
2. {detailed step with expected outcomes}
3. {validation step}

**Rollback Plan:**
1. {rollback step}
2. {verification step}

### Strategy 2: {Name}
{similar structure}

## Recovery and Validation
1. **Service Restoration**
   - [ ] {restoration step}
   - [ ] Wait for {metric} to return to normal
   - [ ] Validate end-to-end functionality

2. **Communication**
   - [ ] Update status page
   - [ ] Notify stakeholders
   - [ ] Schedule PIR

## Common Pitfalls
- **{Pitfall}:** {description and how to avoid}
- **{Pitfall}:** {description and how to avoid}

## Reference Information
- **Architecture Diagram:** {link}
- **Monitoring Dashboard:** {link}
- **Related Runbooks:** {links to dependent service runbooks}
```

### Post-Incident Review (PIR) Framework

#### PIR Timeline and Ownership

**Timeline:**
- **24 hours:** Initial PIR draft completed by Incident Commander
- **3 business days:** Final PIR published with all stakeholder input
- **1 week:** Action items assigned with owners and due dates
- **4 weeks:** Follow-up review on action item progress

**Roles:**
- **PIR Owner:** Incident Commander (can delegate writing but owns completion)
- **Technical Contributors:** All engineers involved in response
- **Review Committee:** Engineering leadership, affected product teams
- **Action Item Owners:** Assigned based on expertise and capacity

#### Root Cause Analysis Frameworks

#### 1. Five Whys Method

The Five Whys technique involves asking "why" repeatedly to drill down to root causes:

**Example Application:**
- **Problem:** Database became unresponsive during peak traffic
- **Why 1:** Why did the database become unresponsive? → Connection pool was exhausted
- **Why 2:** Why was the connection pool exhausted? → Application was creating more connections than usual
- **Why 3:** Why was the application creating more connections? → New feature wasn't properly connection pooling
- **Why 4:** Why wasn't the feature properly connection pooling? → Code review missed this pattern
- **Why 5:** Why did code review miss this? → No automated checks for connection pooling patterns

**Best Practices:**
- Ask "why" at least 3 times, often need 5+ iterations
- Focus on process failures, not individual blame
- Each "why" should point to a actionable system improvement
- Consider multiple root cause paths, not just one linear chain

#### 2. Fishbone (Ishikawa) Diagram

Systematic analysis across multiple categories of potential causes:

**Categories:**
- **People:** Training, experience, communication, handoffs
- **Process:** Procedures, change management, review processes
- **Technology:** Architecture, tooling, monitoring, automation
- **Environment:** Infrastructure, dependencies, external factors

**Application Method:**
1. State the problem clearly at the "head" of the fishbone
2. For each category, brainstorm potential contributing factors
3. For each factor, ask what caused that factor (sub-causes)
4. Identify the factors most likely to be root causes
5. Validate root causes with evidence from the incident

#### 3. Timeline Analysis

Reconstruct the incident chronologically to identify decision points and missed opportunities:

**Timeline Elements:**
- **Detection:** When was the issue first observable? When was it first detected?
- **Notification:** How quickly were the right people informed?
- **Response:** What actions were taken and how effective were they?
- **Communication:** When were stakeholders updated?
- **Resolution:** What finally resolved the issue?

**Analysis Questions:**
- Where were there delays and what caused them?
- What decisions would we make differently with perfect information?
- Where did communication break down?
- What automation could have detected/resolved faster?

### Escalation Paths

#### Technical Escalation

**Level 1:** On-call engineer
- **Responsibility:** Initial response and common issue resolution
- **Escalation Trigger:** Issue not resolved within SLA timeframe
- **Timeframe:** 15 minutes (SEV1), 30 minutes (SEV2)

**Level 2:** Senior engineer/Team lead
- **Responsibility:** Complex technical issues requiring deeper expertise
- **Escalation Trigger:** Level 1 requests help or timeout occurs
- **Timeframe:** 30 minutes (SEV1), 1 hour (SEV2)

**Level 3:** Engineering Manager/Staff Engineer
- **Responsibility:** Cross-team coordination and architectural decisions
- **Escalation Trigger:** Issue spans multiple systems or teams
- **Timeframe:** 45 minutes (SEV1), 2 hours (SEV2)

**Level 4:** Director of Engineering/CTO
- **Responsibility:** Resource allocation and business impact decisions
- **Escalation Trigger:** Extended outage or significant business impact
- **Timeframe:** 1 hour (SEV1), 4 hours (SEV2)

#### Business Escalation

**Customer Impact Assessment:**
- **High:** Revenue loss, SLA breaches, customer churn risk
- **Medium:** User experience degradation, support ticket volume
- **Low:** Internal tools, development impact only

**Escalation Matrix:**

| Severity | Duration | Business Escalation |
|----------|----------|-------------------|
| SEV1 | Immediate | VP Engineering |
| SEV1 | 30 minutes | CTO + Customer Success VP |
| SEV1 | 1 hour | CEO + Full Executive Team |
| SEV2 | 2 hours | VP Engineering |
| SEV2 | 4 hours | CTO |
| SEV3 | 1 business day | Engineering Manager |

### Status Page Management

#### Update Principles

1. **Transparency:** Provide factual information without speculation
2. **Timeliness:** Update within committed timeframes
3. **Clarity:** Use customer-friendly language, avoid technical jargon
4. **Completeness:** Include impact scope, status, and next update time

#### Status Categories

- **Operational:** All systems functioning normally
- **Degraded Performance:** Some users may experience slowness
- **Partial Outage:** Subset of features unavailable
- **Major Outage:** Service unavailable for most/all users
- **Under Maintenance:** Planned maintenance window

#### Update Template

```
{Timestamp} - {Status Category}

{Brief description of current state}

Impact: {who is affected and how}
Cause: {root cause if known, "under investigation" if not}
Resolution: {what's being done to fix it}

Next update: {specific time}

We apologize for any inconvenience this may cause.
```

### Action Item Framework

#### Action Item Categories

1. **Immediate Fixes**
   - Critical bugs discovered during incident
   - Security vulnerabilities exposed
   - Data integrity issues

2. **Process Improvements**
   - Communication gaps
   - Escalation procedure updates
   - Runbook additions/updates

3. **Technical Debt**
   - Architecture improvements
   - Monitoring enhancements
   - Automation opportunities

4. **Organizational Changes**
   - Team structure adjustments
   - Training requirements
   - Tool/platform investments

#### Action Item Template

```
**Title:** {Concise description of the action}
**Priority:** {Critical/High/Medium/Low}
**Category:** {Fix/Process/Technical/Organizational}
**Owner:** {Assigned person}
**Due Date:** {Specific date}
**Success Criteria:** {How will we know this is complete}
**Dependencies:** {What needs to happen first}
**Related PIRs:** {Links to other incidents this addresses}

**Description:**
{Detailed description of what needs to be done and why}

**Implementation Plan:**
1. {Step 1}
2. {Step 2}
3. {Validation step}

**Progress Updates:**
- {Date}: {Progress update}
- {Date}: {Progress update}
```

## Usage Examples

### Example 1: Database Connection Pool Exhaustion

```bash
# Classify the incident
echo '{"description": "Users reporting 500 errors, database connections timing out", "affected_users": "80%", "business_impact": "high"}' | python scripts/incident_classifier.py

# Reconstruct timeline from logs
python scripts/timeline_reconstructor.py --input assets/db_incident_events.json --output timeline.md

# Generate PIR after resolution
python scripts/pir_generator.py --incident assets/db_incident_data.json --timeline timeline.md --output pir.md
```

### Example 2: API Rate Limiting Incident

```bash
# Quick classification from stdin
echo "API rate limits causing customer API calls to fail" | python scripts/incident_classifier.py --format text

# Build timeline from multiple sources
python scripts/timeline_reconstructor.py --input assets/api_incident_logs.json --detect-phases --gap-analysis

# Generate comprehensive PIR
python scripts/pir_generator.py --incident assets/api_incident_summary.json --rca-method fishbone --action-items
```

## Best Practices

### During Incident Response

1. **Maintain Calm Leadership**
   - Stay composed under pressure
   - Make decisive calls with incomplete information
   - Communicate confidence while acknowledging uncertainty

2. **Document Everything**
   - All actions taken and their outcomes
   - Decision rationale, especially for controversial calls
   - Timeline of events as they happen

3. **Effective Communication**
   - Use clear, jargon-free language
   - Provide regular updates even when there's no new information
   - Manage stakeholder expectations proactively

4. **Technical Excellence**
   - Prefer rollbacks to risky fixes under pressure
   - Validate fixes before declaring resolution
   - Plan for secondary failures and cascading effects

### Post-Incident

1. **Blameless Culture**
   - Focus on system failures, not individual mistakes
   - Encourage honest reporting of what went wrong
   - Celebrate learning and improvement opportunities

2. **Action Item Discipline**
   - Assign specific owners and due dates
   - Track progress publicly
   - Prioritize based on risk and effort

3. **Knowledge Sharing**
   - Share PIRs broadly within the organization
   - Update runbooks based on lessons learned
   - Conduct training sessions for common failure modes

4. **Continuous Improvement**
   - Look for patterns across multiple incidents
   - Invest in tooling and automation
   - Regularly review and update processes

## Integration with Existing Tools

### Monitoring and Alerting
- PagerDuty/Opsgenie integration for escalation
- Datadog/Grafana for metrics and dashboards
- ELK/Splunk for log analysis and correlation

### Communication Platforms
- Slack/Teams for war room coordination
- Zoom/Meet for video bridges
- Status page providers (Statuspage.io, etc.)

### Documentation Systems
- Confluence/Notion for PIR storage
- GitHub/GitLab for runbook version control
- JIRA/Linear for action item tracking

### Change Management
- CI/CD pipeline integration
- Deployment tracking systems
- Feature flag platforms for quick rollbacks

## Conclusion

The Incident Commander skill provides a comprehensive framework for managing incidents from detection through post-incident review. By implementing structured processes, clear communication templates, and thorough analysis tools, teams can improve their incident response capabilities and build more resilient systems.

The key to successful incident management is preparation, practice, and continuous learning. Use this framework as a starting point, but adapt it to your organization's specific needs, culture, and technical environment.

Remember: The goal isn't to prevent all incidents (which is impossible), but to detect them quickly, respond effectively, communicate clearly, and learn continuously.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Classifier assigns SEV1 to minor issues | Description contains high-severity keywords like "down" or "outage" in a non-critical context | Provide explicit `affected_users` percentage and `business_impact` fields to give the scoring engine more signal beyond keyword matching |
| Timeline reconstructor reports "No valid events found" | Event timestamps are in an unsupported format or the `timestamp`/`time` field is missing | Use ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`), `YYYY-MM-DD HH:MM:SS`, Unix epoch, or other supported formats; ensure each event has a `timestamp` or `time` key |
| PIR generator produces a shallow 5 Whys analysis | Incident data lacks detail in the `description`, `affected_services`, or `customer_impact` fields | Enrich the input JSON with specific technical details; supply a timeline file via `--timeline` so the generator can cross-reference events |
| Gap analysis shows no gaps even though response was slow | The gap threshold defaults to 15-45 minutes depending on the tool; sparse events may all fall within one window | Increase event granularity by including communication and action events, not just alerts and resolutions |
| Postmortem generator marks all action items as invalid | Action items in the input JSON are missing `title`, `owner`, or `deadline` fields | Ensure every action item object includes at minimum `title`, `owner`, `priority`, and `deadline` keys |
| Severity classifier composite score seems too low | The weighted scoring dimensions (revenue, user scope, data/security, service criticality, blast radius) need structured `impact` and `signals` objects | Provide the full input schema with `impact`, `signals`, and `context` keys rather than a flat description string |
| Timeline builder produces "No phases detected" | Events lack `type` fields that map to known phase triggers (detection, declaration, escalation, investigation, mitigation, resolution) | Set the `type` field on each event to one of the recognized event types listed in the tool's `EVENT_TYPES` constant |

## Success Criteria

- **MTTA under 5 minutes** -- Incident Commander assigned and war room established within 5 minutes of a SEV1 declaration, as measured by the timeline builder's phase detection
- **MTTD under 10 minutes** -- Mean Time to Detect stays below 10 minutes for SEV1 incidents; the severity classifier and timeline tools surface detection-to-triage latency for tracking
- **MTTR under 2 hours for SEV1** -- Mean Time to Resolve for critical incidents remains under 120 minutes, validated by postmortem generator benchmark comparisons
- **PIR published within 48 hours** -- Post-Incident Review draft completed within 24 hours and final version published within 48 hours of resolution for SEV1/SEV2 incidents
- **100% action item coverage** -- Every contributing factor category identified in the 5 Whys analysis has at least one corresponding action item; the postmortem generator's coverage gap detector reports zero gaps
- **Stakeholder update cadence met** -- SEV1 updates every 15 minutes, SEV2 every 30 minutes, with no communication gaps flagged by the timeline reconstructor's gap analysis
- **Action item completion within SLA** -- All P0 action items closed within 48 hours, P1 within 2 weeks; the postmortem generator's `is_past_deadline` check returns false for all open items

## Scope & Limitations

**This skill covers:**
- Automated severity classification using keyword analysis, impact metrics, and multi-dimensional weighted scoring across five dimensions (revenue, user scope, data/security, service criticality, blast radius)
- Incident timeline reconstruction from heterogeneous event sources (logs, alerts, Slack messages, deployment events) with automatic phase detection, gap analysis, and duration metrics
- Post-incident review generation with four RCA frameworks (5 Whys, Fishbone, Timeline Analysis, Bow Tie) and structured action item tracking with quality scoring
- Communication template generation for internal stakeholders, executives, status pages, and customer notifications across all severity levels

**This skill does NOT cover:**
- Real-time monitoring, alerting, or on-call scheduling -- see `senior-devops` and `senior-secops` for infrastructure monitoring and security alerting workflows
- Automated incident remediation or runbook execution -- this skill generates runbook templates but does not execute commands against live infrastructure
- Organizational change management or team restructuring -- see `c-level-advisor/cto-advisor` for engineering org design and leadership decision frameworks
- Compliance-specific incident reporting (SOC 2, HIPAA, GDPR breach notification) -- see `ra-qm-team` for regulatory compliance skills with framework-specific reporting requirements

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-devops` | Monitoring alerts and deployment events feed into the timeline reconstructor as event sources; runbook templates generated here inform DevOps playbooks | Alerts/deployments -> `timeline_reconstructor.py` -> phase analysis; runbook templates -> DevOps execution |
| `senior-secops` | Security incidents classified by `incident_classifier.py` trigger SecOps escalation paths; breach indicators auto-escalate to SEV1 via `severity_classifier.py` | Security alerts -> severity classification -> SecOps response; PIR security findings -> SecOps remediation |
| `senior-qa` | Test failures and regression data provide incident context; PIR action items of type `prevention` feed back into QA test plans | QA regression data -> incident context; PIR action items -> QA test coverage expansion |
| `code-reviewer` | PIR action items categorized as `immediate_fix` or `architectural` route to code review workflows; deployment-related root causes trigger review process improvements | PIR action items -> code review queue; review process gaps -> PIR lessons learned |
| `release-orchestrator` | Deployment events from release pipelines feed timeline reconstruction; rollback decisions during incidents inform release gating criteria | Release events -> timeline builder; incident rollback data -> release gate policies |
| `senior-architect` | Architectural root causes identified in Fishbone and Bow Tie analyses escalate to architecture review; blast radius analysis informs system design decisions | PIR architectural findings -> architecture review backlog; dependency analysis -> resilience design |

## Tool Reference

### incident_classifier.py

**Purpose:** Analyzes incident descriptions and outputs severity levels (SEV1-SEV4), recommended response teams, initial actions, escalation paths, and communication templates. Uses keyword matching and impact scoring to classify incidents.

**Usage:**
```bash
python scripts/incident_classifier.py --input incident.json
echo '{"description": "Database is down", "business_impact": "high"}' | python scripts/incident_classifier.py --format text
python scripts/incident_classifier.py --interactive
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--input`, `-i` | string | -- | Input file path (JSON format) or `-` for stdin |
| `--format`, `-f` | choice | `json` | Output format: `json` or `text` |
| `--interactive` | flag | off | Run in interactive mode with prompts for each field |
| `--output`, `-o` | string | stdout | Output file path |

**Input JSON fields:** `description` (required), `service`, `affected_users`, `business_impact`, `duration_minutes`. Accepts plain text via stdin (auto-parsed into structured data).

**Example:**
```bash
echo '{"description": "API rate limits causing failures", "service": "api-gateway", "affected_users": "50%", "business_impact": "high"}' | python scripts/incident_classifier.py --format text
```

**Output Formats:**
- **JSON** -- Full classification result with `classification`, `response`, `initial_actions`, `communication`, `timeline`, and `escalation` objects
- **Text** -- Formatted report with severity, confidence score, recommended teams, prioritized actions, and communication details

---

### severity_classifier.py

**Purpose:** Multi-dimensional severity classification engine that scores incidents across five weighted dimensions (revenue impact 25%, user impact scope 25%, data/security risk 20%, service criticality 15%, blast radius 15%). Generates escalation paths, SLA impact assessments, and immediate action plans.

**Usage:**
```bash
python scripts/severity_classifier.py incident.json
python scripts/severity_classifier.py incident.json --format markdown
cat incident.json | python scripts/severity_classifier.py --format json
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `data_file` | positional | stdin | JSON file with incident data (reads stdin if omitted) |
| `--format` | choice | `text` | Output format: `text`, `json`, or `markdown` |

**Input JSON structure:** Requires `incident` key with title/description. Optional keys: `impact` (revenue_impact, affected_users_percentage, affected_regions, data_integrity_risk, security_breach, customer_facing, degradation_type, workaround_available), `signals` (error_rate_percentage, latency_p99_ms, alert_count, customer_reports, dependent_services, affected_endpoints), `context` (on_call configuration).

**Example:**
```bash
echo '{"incident": {"title": "Payment API failure", "description": "Payments failing"}, "impact": {"revenue_impact": "critical", "affected_users_percentage": 60, "customer_facing": true}}' | python scripts/severity_classifier.py --format json
```

**Output Formats:**
- **JSON** -- Complete analysis with severity_score, escalation_path, action_plan, sla_impact, and all dimension breakdowns
- **Text** -- Human-readable report with severity badge, dimension scores, escalation chain, and action checklist
- **Markdown** -- Formatted report with tables for dimension scores, escalation paths, and SLA impact assessment

---

### timeline_reconstructor.py

**Purpose:** Reconstructs incident timelines from timestamped events sourced from logs, alerts, Slack messages, and deployment systems. Detects incident phases (detection, triage, escalation, mitigation, resolution, review), calculates duration metrics, and performs gap analysis to identify periods of inactivity.

**Usage:**
```bash
python scripts/timeline_reconstructor.py --input events.json --output timeline.md
python scripts/timeline_reconstructor.py --input events.json --detect-phases --gap-analysis
cat events.json | python scripts/timeline_reconstructor.py --format text
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--input`, `-i` | string | -- | Input file path (JSON format) or `-` for stdin |
| `--output`, `-o` | string | stdout | Output file path |
| `--format`, `-f` | choice | `json` | Output format: `json`, `text`, or `markdown` |
| `--detect-phases` | flag | off | Enable automatic incident phase detection |
| `--gap-analysis` | flag | off | Enable gap analysis to identify periods of inactivity |
| `--min-events` | int | `2` | Minimum number of events required for valid timeline |

**Input JSON format:** Array of event objects. Each event supports: `timestamp` or `time` (required), `source`, `type`, `message` or `description`, `severity` or `level`, `actor` or `user`, plus arbitrary metadata fields.

**Example:**
```bash
python scripts/timeline_reconstructor.py --input events.json --detect-phases --gap-analysis --format markdown --output report.md
```

**Output Formats:**
- **JSON** -- Structured output with `timeline` (events, phases, time range), `metrics` (durations, counts), `gap_analysis`, `narrative`, and `summary`
- **Text** -- Human-readable timeline report with phase markers, duration calculations, and gap warnings
- **Markdown** -- Professional report with timeline table, phase summary, and gap analysis sections

---

### incident_timeline_builder.py

**Purpose:** Builds structured incident timelines with automatic phase detection, gap analysis (threshold: 15 minutes), communication template generation, and response metrics calculation (MTTD, MTTR). Produces professional reports with phase duration distribution charts.

**Usage:**
```bash
python scripts/incident_timeline_builder.py incident_data.json
python scripts/incident_timeline_builder.py incident_data.json --format json
python scripts/incident_timeline_builder.py incident_data.json --format markdown
cat incident_data.json | python scripts/incident_timeline_builder.py --format text
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `data_file` | positional | stdin | JSON file with incident data (reads stdin if omitted) |
| `--format` | choice | `text` | Output format: `text`, `json`, or `markdown` |

**Input JSON structure:** Requires `incident` key (id, title, severity, status, commander, service, affected_services, declared_at, resolved_at) and `events` array. Each event requires `timestamp`, `type` (one of: detection, declaration, escalation, investigation, mitigation, communication, resolution, action_item), `actor`, and `description`.

**Example:**
```bash
python scripts/incident_timeline_builder.py incident.json --format markdown > report.md
```

**Output Formats:**
- **JSON** -- Full analysis with incident summary, sorted timeline, detected phases, gaps, decision points, metrics (MTTD, MTTR, phase durations, gap statistics), and four generated communication templates (initial notification, status page, executive summary, customer notification)
- **Text** -- Formatted report with incident summary, key metrics, phase breakdown, chronological timeline with decision point markers, gap warnings, and generated communications
- **Markdown** -- Professional report with summary table, metrics bullets, phase duration table with ASCII bar chart, chronological timeline with decision point highlighting, gap analysis callouts, and event type breakdown table

---

### pir_generator.py

**Purpose:** Generates comprehensive Post-Incident Review documents from incident data and optional timeline reconstructions. Applies four RCA frameworks (5 Whys, Fishbone/Ishikawa, Timeline Analysis, Bow Tie) and produces structured action items, lessons learned, and prevention recommendations.

**Usage:**
```bash
python scripts/pir_generator.py --incident incident.json --timeline timeline.json --output pir.md
python scripts/pir_generator.py --incident incident.json --rca-method fishbone --action-items
cat incident.json | python scripts/pir_generator.py --format markdown
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--incident`, `-i` | string | -- | Incident data file (JSON) or `-` for stdin |
| `--timeline`, `-t` | string | -- | Timeline reconstruction file (JSON), optional |
| `--output`, `-o` | string | stdout | Output file path |
| `--format`, `-f` | choice | `markdown` | Output format: `json`, `markdown`, or `text` |
| `--rca-method` | choice | `five_whys` | RCA framework: `five_whys`, `fishbone`, `timeline`, or `bow_tie` |
| `--template-type` | choice | `comprehensive` | PIR document template: `comprehensive`, `standard`, or `brief` |
| `--action-items` | flag | off | Include enhanced action item generation and categorization |

**Input JSON fields:** `incident_id`, `title`, `description`, `severity`, `start_time`, `end_time`, `affected_services`, `customer_impact`, `business_impact`, `incident_commander`, `responders`, `status`.

**Example:**
```bash
python scripts/pir_generator.py --incident incident.json --rca-method fishbone --template-type comprehensive --action-items --format markdown --output pir.md
```

**Output Formats:**
- **JSON** -- Complete PIR data with `pir_document`, `metadata`, `incident_info`, `rca_results` (method-specific analysis), `lessons_learned`, and `action_items` (categorized as immediate_fix, process_improvement, monitoring_alerting, documentation, training, architectural, tooling)
- **Markdown** -- Full PIR document using the selected template (comprehensive includes executive summary, timeline, RCA, what went well/wrong, lessons learned, action items, prevention measures, and appendix)
- **Text** -- Plain text version of the PIR document

---

### postmortem_generator.py

**Purpose:** Generates structured postmortem reports with automatic 5-Whys analysis, contributing factor classification (process, tooling, human, environment, external), action item validation with quality scoring, MTTD/MTTR benchmark comparisons, and coverage gap detection. Identifies missing action items and provides theme-based recommendations.

**Usage:**
```bash
python scripts/postmortem_generator.py incident_data.json
python scripts/postmortem_generator.py incident_data.json --format markdown
python scripts/postmortem_generator.py incident_data.json --format json
cat incident_data.json | python scripts/postmortem_generator.py
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `data_file` | positional | stdin | JSON file with incident + resolution data (reads stdin if omitted) |
| `--format` | choice | `text` | Output format: `text`, `json`, or `markdown` |

**Input JSON structure:** Requires `incident` (id, title, severity, commander, service, affected_services), `timeline` (issue_started, detected_at, declared_at, mitigated_at, resolved_at, postmortem_at -- all ISO-8601), `resolution` (root_cause, contributing_factors array, customer_impact object), `action_items` array (each with title, owner, priority, deadline, type, status), and `participants` array.

**Example:**
```bash
python scripts/postmortem_generator.py incident.json --format markdown > postmortem.md
```

**Output Formats:**
- **JSON** -- Full analysis with incident metadata, timeline metrics (MTTD, MTTR, time-to-mitigate, time-to-declare) with industry benchmark comparisons, contributing factor distribution by category, 5-Whys chains per factor, action item validation (quality scores 0-100, deadline tracking), coverage gap analysis, suggested missing actions, and theme-based recommendations
- **Text** -- Human-readable report with executive summary, metrics table with benchmark deltas, contributing factors with category weights, 5-Whys chains, action items with validation status, and improvement recommendations
- **Markdown** -- Professional postmortem document with summary table, metrics section with benchmark comparison, contributing factor breakdown, 5-Whys analysis, validated action items, coverage gaps, and strategic recommendations per systemic theme