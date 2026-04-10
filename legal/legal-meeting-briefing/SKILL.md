---
name: legal-meeting-briefing
description: >
  Prepare structured briefings for meetings with legal relevance and track action items. Use when prepping legal meetings.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: legal-operations
  updated: 2026-04-10
  tags: [meeting-briefing, legal-ops, action-items, preparation, meetings]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Legal Meeting Briefing Skill

## Overview

Production-ready toolkit for preparing structured briefings for meetings with legal relevance and tracking resulting action items. Supports 8 meeting types with type-specific preparation guidance, a 13-section briefing template, and action item management with priority levels and follow-up cadence. Designed for legal teams preparing counsel, in-house attorneys, and legal operations professionals for productive meetings.

## Table of Contents

- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Meeting Types](#meeting-types)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

## Tools

### 1. Meeting Brief Generator (`scripts/meeting_brief_generator.py`)

Generate a meeting briefing skeleton pre-populated with sections based on meeting type.

```bash
python scripts/meeting_brief_generator.py \
  --type deal-review \
  --title "Series B Term Sheet Review" \
  --date 2026-04-15 \
  --participants '[{"name":"Jane Smith","org":"Legal","role":"Lead Counsel"}]'

python scripts/meeting_brief_generator.py \
  --type board \
  --title "Q1 Board Meeting" \
  --date 2026-04-20 \
  --agenda "Legal update,Risk report,Pending approvals" --json

python scripts/meeting_brief_generator.py \
  --type regulatory \
  --title "FDA Pre-Submission Meeting" \
  --date 2026-05-01 \
  --participants '[{"name":"Dr. Lee","org":"FDA","role":"Reviewer"}]'
```

### 2. Action Item Tracker (`scripts/action_item_tracker.py`)

Manage action items from legal meetings with priority levels, ownership, and status tracking.

```bash
python scripts/action_item_tracker.py add \
  --title "Draft NDA for Vendor X" \
  --owner "Jane Smith" \
  --priority high \
  --deadline 2026-04-20 \
  --meeting "Series B Review"

python scripts/action_item_tracker.py list \
  --filter-status open \
  --filter-priority high

python scripts/action_item_tracker.py complete --id 3

python scripts/action_item_tracker.py dashboard --json

python scripts/action_item_tracker.py update --id 5 \
  --status in-progress --notes "Waiting for counterparty response"
```

## Reference Guides

| Reference | Purpose |
|-----------|---------|
| `references/meeting_type_guides.md` | Preparation guidance for all 8 meeting types |
| `references/briefing_templates.md` | Complete 13-section briefing template and action item tracking |

## Workflows

### 5-Step Briefing Methodology

| Step | Action | Output |
|------|--------|--------|
| 1. Identify Meeting | Determine meeting type, participants, objectives | Meeting classification |
| 2. Assess Preparation Needs | Select type-specific sections and depth | Section checklist |
| 3. Gather Context | Collect documents, prior notes, open issues | Background materials |
| 4. Synthesize into Briefing | Run generator; populate sections with gathered context | Draft briefing |
| 5. Identify Preparation Gaps | Review for missing info; flag items needing follow-up | Gap list |

### Meeting Type Selection

| Meeting Type | Key Indicator |
|-------------|---------------|
| Deal Review | Transaction under consideration or in progress |
| Board/Committee | Board of directors, audit committee, compensation committee |
| Vendor Call | Meeting with supplier, contractor, or service provider |
| Team Sync | Internal legal team meeting |
| Client/Customer | External client or customer-facing meeting |
| Regulatory/Government | Meeting with regulator, agency, or government body |
| Litigation/Dispute | Meeting about active or potential legal dispute |
| Cross-Functional | Meeting with stakeholders from multiple departments |

### Action Item Workflow

1. **Capture** -- Record action items during or immediately after meeting
2. **Assign** -- Set owner, priority, and deadline for each item
3. **Track** -- Monitor progress via dashboard; update status as work progresses
4. **Follow-Up** -- Follow cadence based on priority level
5. **Close** -- Mark complete when done; archive for audit trail

### Follow-Up Cadence

| Priority | Follow-Up Frequency | Escalation |
|----------|-------------------|------------|
| High | Daily check-in | Escalate after 2 missed days |
| Medium | Weekly check-in | Escalate after 1 missed week |
| Low | Monthly check-in | Escalate after 1 missed month |
| Overdue | Immediate escalation | Notify supervisor and meeting owner |

## Meeting Types

### Deal Review

Focus: Transaction analysis, contract review, approval requirements.

| Section | Content |
|---------|---------|
| Deal Summary | Parties, structure, value, timeline |
| Contract Status | Draft version, open issues, redline items |
| Approval Requirements | Who must approve; delegated authority limits |
| Counterparty Dynamics | Negotiation position, prior dealings, leverage |
| Comparable Deals | Similar transactions for benchmarking terms |

### Board/Committee

Focus: Legal department update, risk highlights, governance.

| Section | Content |
|---------|---------|
| Legal Department Update | Headcount, budget, key accomplishments |
| Risk Highlights | Top legal risks with likelihood and impact |
| Regulatory Update | Recent regulatory changes affecting the organization |
| Pending Approvals | Items requiring board or committee action |
| Litigation Summary | Active matters, reserves, settlement status |

### Regulatory/Government

Focus: Compliance posture, enforcement patterns, privilege considerations.

| Section | Content |
|---------|---------|
| Regulatory Body Context | Agency structure, jurisdiction, enforcement priorities |
| Enforcement Patterns | Recent enforcement actions in the sector |
| Matter History | Prior interactions, submissions, correspondence |
| Privilege Considerations | What is privileged; what can be shared |
| Compliance Posture | Current compliance status; remediation progress |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Brief missing type-specific sections | Wrong meeting type selected | Review meeting type descriptions; select the most specific type |
| Participants not formatted | JSON format error | Use valid JSON array: `'[{"name":"X","org":"Y","role":"Z"}]'` |
| Action items not persisting | Tracker uses file-based storage | Ensure write permissions in working directory; check `action_items.json` |
| Dashboard shows stale data | Cached data from previous run | Re-run dashboard command; items are loaded fresh from storage |
| Overdue items not flagged | Clock/timezone mismatch | Verify system date; deadlines use YYYY-MM-DD format |
| Agenda items not populating | Comma-separated format expected | Use `--agenda "Item 1,Item 2,Item 3"` format |
| Brief too generic | Minimal parameters provided | Add participants, agenda, and type-specific context |
| Action item ID not found | Item was completed or deleted | Run `list --filter-status all` to see all items including completed |

## Success Criteria

- **Preparation Coverage**: Every legal meeting has a briefing covering all relevant sections for its type
- **Action Item Capture**: 100% of action items captured with owner, deadline, and priority within 24 hours
- **On-Time Completion**: 90%+ of action items completed by deadline
- **Meeting Effectiveness**: Participants report improved preparation and productivity (measured by survey)
- **Follow-Up Compliance**: High-priority items followed up daily; medium weekly; low monthly

## Scope & Limitations

**This skill covers:**
- Meeting briefing generation with type-specific sections for 8 meeting types
- Action item tracking with CRUD operations, filtering, and status dashboard
- Follow-up cadence management based on priority levels
- Preparation gap identification for pre-meeting readiness

**This skill does NOT cover:**
- Calendar integration or meeting scheduling
- Real-time meeting notes or transcription
- Email drafting or distribution of briefings
- Document management or version control for meeting materials
- Video conferencing or collaboration tool integration

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|--------------|-------------|-----------------|
| Generic briefing for all meeting types | Misses type-specific concerns; wastes prep time on irrelevant sections | Select correct meeting type; use type-specific guidance |
| Capturing action items days after meeting | Details forgotten; ownership unclear; deadlines slip | Capture during meeting or within 2 hours; use tracker immediately |
| Single owner for all items | Creates bottleneck; no accountability for individual tasks | Assign specific owner per item; each item has exactly one owner |
| No follow-up on action items | Items go stale; commitments missed; trust erodes | Follow cadence: high=daily, medium=weekly, low=monthly |
| Skipping privilege considerations for regulatory meetings | Inadvertent privilege waiver; disclosed protected communications | Always complete privilege section for regulatory/government meetings |

## Tool Reference

### `scripts/meeting_brief_generator.py`

Generate meeting briefing skeleton from parameters.

```
usage: meeting_brief_generator.py [-h] [--json]
                                   --type {deal-review,board,vendor,team-sync,
                                           client,regulatory,litigation,cross-functional}
                                   --title TITLE
                                   --date DATE
                                   [--participants PARTICIPANTS]
                                   [--agenda AGENDA]
                                   [--output OUTPUT]

options:
  -h, --help            Show help message and exit
  --json                Output in JSON format
  --type                Meeting type (determines sections included)
  --title               Meeting title
  --date                Meeting date (YYYY-MM-DD)
  --participants        JSON array of participants: [{"name","org","role","interests"}]
  --agenda              Comma-separated agenda items
  --output              Write briefing to file instead of stdout
```

### `scripts/action_item_tracker.py`

Manage action items with CRUD operations and status dashboard.

```
usage: action_item_tracker.py [-h] [--json]
                               {add,list,update,complete,dashboard} ...

commands:
  add         Add a new action item
  list        List action items with optional filters
  update      Update an existing action item
  complete    Mark an action item as complete
  dashboard   Show action item summary dashboard

add options:
  --title TITLE         Action item description (required)
  --owner OWNER         Responsible person (required)
  --priority {high,medium,low}  Priority level (required)
  --deadline DEADLINE   Due date YYYY-MM-DD (required)
  --meeting MEETING     Source meeting name
  --notes NOTES         Additional notes

list options:
  --filter-status {open,in-progress,complete,overdue,all}
  --filter-priority {high,medium,low,all}
  --filter-owner OWNER

update options:
  --id ID               Action item ID (required)
  --status {open,in-progress,complete}
  --priority {high,medium,low}
  --deadline DEADLINE
  --notes NOTES

complete options:
  --id ID               Action item ID (required)

dashboard options:
  (no additional options)
```
