---
name: summarize-meeting
description: >
  Structured meeting summarization that captures decisions, action items, and
  open questions in a consistent format.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: meeting-facilitation, action-tracking, decision-logging
---
# Meeting Summary Expert

## Overview

Transform meeting notes, transcripts, or recordings into clear, actionable summaries. Every summary follows a consistent structure that makes it easy for attendees and non-attendees alike to understand what was discussed, what was decided, and who is doing what by when.

## Core Capabilities

- **Metadata capture** — date, time, participants with roles, topic, location
- **Discussion synthesis** — summarize substantive topics in plain language; note disagreements and resolutions
- **Action extraction** — one owner, concrete deliverable, and a specific calendar due date per item
- **Decision logging** — numbered decisions with rationale and decision-maker
- **Open-question tracking** — unresolved items with owner and target date
- **Consistent output** — fixed template plus naming convention and 24-hour distribution discipline

## When to Use

- **After any meeting** where decisions were made or actions were assigned.
- **Sprint ceremonies** -- planning, retro, backlog refinement, sprint review.
- **Stakeholder meetings** -- steering committees, executive reviews, client calls.
- **Ad-hoc discussions** -- when an impromptu conversation produces commitments that need tracking.

## Clarify First

Before summarizing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The source material and its fidelity** — raw notes, transcript, or recording (summary quality is bounded by input; missing owners/dates for action items cannot be invented)
- [ ] **Meeting type** — planning, retro, steering committee, or client call (tailors discussion synthesis and which decisions matter)
- [ ] **Distribution scope + confidentiality** — attendees, non-attendees, or execs, and any sensitivity limits (determines whether standard 24-hour distribution applies)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/summarization-process.md](references/summarization-process.md)** — the full six-step methodology (metadata → discussion → actions → decisions → open questions → distribute), the output template, focus priorities, troubleshooting table, and success criteria. Read when producing a summary.
- **[references/meeting-facilitation-guide.md](references/meeting-facilitation-guide.md)** — meeting types, note-taking strategies, and anti-patterns. Read to tailor the summary to the meeting type or improve input quality.
- **[references/red-flags.md](references/red-flags.md)** — common ways summaries go wrong with bad/good examples. Read before posting, emailing, or linking a summary.
- **[assets/meeting_summary_template.md](assets/meeting_summary_template.md)** — ready-to-use fill-in template. Use to draft the summary directly.

## Integration with Other Skills

- Feed decisions into `wwas/` to create backlog items with strategic context.
- Use action items to create tickets via `../jira-expert/`.
- Document recurring meeting outcomes in `../confluence-expert/` templates.

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
