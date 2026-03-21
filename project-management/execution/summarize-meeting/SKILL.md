---
name: summarize-meeting
description: Structured meeting summarization that captures decisions, action items, and open questions in a consistent format.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-03-04
  tech-stack: meeting-facilitation, action-tracking, decision-logging
---

# Meeting Summary Expert

## Overview

Transform meeting notes, transcripts, or recordings into clear, actionable summaries. Every summary follows a consistent structure that makes it easy for attendees and non-attendees alike to understand what was discussed, what was decided, and who is doing what by when.

### When to Use

- **After any meeting** where decisions were made or actions were assigned.
- **Sprint ceremonies** -- planning, retro, backlog refinement, sprint review.
- **Stakeholder meetings** -- steering committees, executive reviews, client calls.
- **Ad-hoc discussions** -- when an impromptu conversation produces commitments that need tracking.

## Methodology

### Step 1: Capture Meeting Metadata

Record the essential context:

| Field | Description |
|-------|-------------|
| **Date** | Meeting date (YYYY-MM-DD) |
| **Time** | Start and end time with timezone |
| **Participants** | Names and roles (e.g., "Sarah Chen, Product Lead") |
| **Topic** | One-line meeting purpose |
| **Location** | Room name, video link, or "async" |

### Step 2: Extract Key Discussion Points

From the raw notes or transcript, identify the substantive topics discussed. Guidelines:

- **Summarize, do not transcribe.** Capture the essence of each topic in 1-3 bullet points.
- **Use plain language.** Avoid jargon. Anyone reading the summary should understand the points without having attended.
- **Focus on what matters.** Skip small talk, repeated points, and tangential discussions.
- **Note disagreements.** If there was significant debate, capture the key positions and how they were resolved (or not).

### Step 3: Extract Action Items

Every action item must answer three questions:

1. **Who** is responsible? (Single owner, not a team)
2. **What** specifically must they do? (Concrete, observable deliverable)
3. **By when?** (Specific date, not "soon" or "next sprint")

Format as a table:

| Due Date | Owner | Action |
|----------|-------|--------|
| 2026-03-10 | Sarah Chen | Share revised wireframes with the design team |
| 2026-03-07 | James Park | Schedule load test for the staging environment |

**Action item quality checks:**

- Each action has exactly one owner (not "Sarah and James")
- The deliverable is specific enough to verify completion
- The due date is a calendar date, not a relative timeframe
- Actions use active verbs: "share," "schedule," "draft," "review," "decide"

### Step 4: Record Decisions

List each decision made during the meeting as a numbered item. Include enough context that someone who was not present understands the decision and its rationale.

**Format:**

1. **[Decision]** -- [Brief rationale or context]. Decided by [who].
2. **[Decision]** -- [Brief rationale or context]. Decided by [who].

**Examples:**

1. **Launch date set for April 15** -- Allows two full sprints for QA after feature freeze on March 28. Decided by steering committee.
2. **Use PostgreSQL instead of MongoDB for the analytics service** -- Team consensus based on query pattern analysis showing 80% relational queries. Decided by engineering leads.

### Step 5: Capture Open Questions

List unresolved questions that need follow-up. For each question, note who is expected to provide an answer and by when, if known.

1. Do we need a separate staging environment for the new analytics service? (James to investigate by March 10)
2. What is the budget ceiling for the Q2 marketing campaign? (Pending finance review)

### Step 6: Save and Distribute

**File naming convention:** `Meeting-Summary-[YYYY-MM-DD]-[topic-slug].md`

Examples:
- `Meeting-Summary-2026-03-04-sprint-planning.md`
- `Meeting-Summary-2026-03-04-q2-roadmap-review.md`

**Distribution:**
- Share the summary within 24 hours of the meeting.
- Send to all participants and relevant stakeholders who were not present.
- Store in the team's shared documentation space (Confluence, Notion, shared drive).

## Output Template

```markdown
# Meeting Summary

## Metadata

| Field | Value |
|-------|-------|
| **Date** | [YYYY-MM-DD] |
| **Time** | [HH:MM] - [HH:MM] [TZ] |
| **Participants** | [Name, Role]; [Name, Role]; ... |
| **Topic** | [One-line meeting purpose] |

## Summary

- [Key discussion point 1]
- [Key discussion point 2]
- [Key discussion point 3]

## Action Items

| Due Date | Owner | Action |
|----------|-------|--------|
| [YYYY-MM-DD] | [Name] | [Specific, verifiable action] |

## Decisions Made

1. **[Decision]** -- [Rationale]. Decided by [who].

## Open Questions

1. [Question]? ([Who is expected to answer, by when])
```

## What to Focus On

When summarizing, prioritize:

- **Decisions that affect roadmap or strategy** -- These have the broadest impact and are most likely to be referenced later.
- **Who does what by when** -- Accountability is the primary value of a meeting summary.
- **Blockers and risks surfaced** -- These need visibility beyond the meeting room.
- **Changes to previously agreed plans** -- These create confusion if not documented.

When summarizing, deprioritize:

- Status updates that are available elsewhere (Jira, dashboards)
- Repetition of information already documented
- Social conversation and small talk
- Detailed technical discussions better captured in design docs

## Integration with Other Skills

- Feed decisions into `wwas/` to create backlog items with strategic context.
- Use action items to create tickets via `../jira-expert/`.
- Document recurring meeting outcomes in `../confluence-expert/` templates.

## References

- See `references/meeting-facilitation-guide.md` for meeting types, note-taking strategies, and anti-patterns.
- See `assets/meeting_summary_template.md` for ready-to-use templates.

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Action items are assigned to teams instead of individuals | Culture avoids individual accountability; facilitator does not press for a single owner | Enforce the "one owner" rule during the meeting; if a team is named, ask "Who on that team is the single point of contact?" |
| Summaries are too long and nobody reads them | Summarizer includes too much detail; tries to capture everything | Apply the "would someone who missed the meeting need this?" filter to every bullet point; target 1 page maximum for 1-hour meetings |
| Decisions are not documented, leading to re-litigation in future meetings | Meeting moved quickly; facilitator focused on discussion, not decisions | Pause after each decision and state it aloud: "Let me confirm: we decided X because Y"; add decision capture as a facilitator checklist item |
| Action items have vague due dates ("soon", "next sprint") | Facilitator does not push for specificity; team uncomfortable committing to dates | Require a calendar date for every action; if the team cannot commit, set a date to decide the date |
| Summaries are distributed days after the meeting | Summarizer is overburdened or perfectionist | Set a 24-hour distribution rule; use a structured template to reduce writing effort; assign summary responsibility before the meeting |
| Open questions from previous meetings are never resolved | No follow-up mechanism; questions captured but not tracked | Add "Previous Open Questions" as a standing agenda item; assign each question an owner and a resolution date |
| Attendees disagree with the summary after distribution | Summary reflects summarizer's interpretation, not group consensus | Share key decisions and action items verbally at the meeting close; invite corrections within 24 hours of distribution |

## Success Criteria

- 100% of meetings with decisions or action items produce a written summary within 24 hours
- Every action item has a single named owner and a specific calendar due date
- Action item completion rate exceeds 80% by the stated due date
- Summaries are 1 page or less for meetings under 1 hour
- Decisions are documented with enough context that a non-attendee can understand the rationale
- Open questions from previous meetings are tracked and resolved within 2 meeting cycles
- Meeting summary satisfaction (from periodic team survey) averages 4+/5

## Scope & Limitations

**In Scope:** Capturing meeting metadata, extracting key discussion points, documenting decisions with rationale, recording action items with owners and due dates, capturing open questions, distributing summaries, maintaining consistent naming conventions and storage.

**Out of Scope:** Meeting facilitation and agenda design, real-time transcription (use a transcription tool as input), project status tracking (hand off to `../jira-expert/`), strategic decision frameworks (hand off to `../senior-pm/`), recording or video management.

**Limitations:** Summary quality is bounded by the quality of input notes or transcript. Automated transcription tools may introduce errors that the summarizer must catch. The skill does not replace the need for a skilled facilitator -- poorly run meetings produce poor summaries regardless of template quality. Sensitive or confidential meetings may require restricted distribution that the standard workflow does not address.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `wwas/` | Meetings -> WWAS | Decisions and commitments from meetings become WWAS backlog items |
| `job-stories/` | Meetings -> Stories | Discovery discussions surface situations and motivations for job stories |
| `../jira-expert/` | Meetings -> Jira | Action items create Jira tickets; decisions update issue comments |
| `../confluence-expert/` | Meetings -> Confluence | Summaries stored in Confluence using meeting notes template |
| `../senior-pm/` | Meetings -> PM | Steering committee and stakeholder meeting summaries feed portfolio reporting |
| `../delivery-manager/` | Meetings -> DM | Release planning and incident review meeting outcomes feed delivery tracking |
