---
name: summarize-meeting
description: >
  Turns meeting notes or transcripts into a summary of decisions, owned and dated
  action items, and open questions. Use when writing up a meeting, a recap email or
  a decision log; for patterns across a series use meeting-analyzer.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: action_item_tracker.py, decision_log_builder.py, meeting_effectiveness_scorer.py
  tech-stack: meeting-facilitation, action-tracking, decision-logging
  tags:
    - meeting-summary
    - action-items
    - decisions
    - meetings
---
# Meeting Summary Expert

## Overview

Transform meeting notes, transcripts, or recordings into clear, actionable summaries. Every summary follows a consistent structure that makes it easy for attendees and non-attendees alike to understand what was discussed, what was decided, and who is doing what by when.

**Done looks like:** every decision is numbered with who made it and why; every action item has one owner, a concrete deliverable and a calendar date; open questions have an owner; nothing is invented that the notes do not support (mark gaps as `[owner?]` or `[date?]` and ask).

## When to Use

- **After any meeting** where decisions were made or actions were assigned.
- **Sprint ceremonies** -- planning, retro, backlog refinement, sprint review.
- **Stakeholder meetings** -- steering committees, executive reviews, client calls.
- **Ad-hoc discussions** -- when an impromptu conversation produces commitments that need tracking.

For accountability across a recurring series (who keeps missing commitments, which meetings never decide anything), use `../../meeting-analyzer/` instead.

## Clarify First

Before summarizing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The source material and its fidelity:** raw notes, transcript, or recording (summary quality is bounded by input; missing owners/dates for action items cannot be invented).
- **Meeting type:** planning, retro, steering committee, or client call (tailors discussion synthesis and which decisions matter).
- **Distribution scope + confidentiality:** attendees, non-attendees, or execs, and any sensitivity limits (determines whether standard 24-hour distribution applies).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

Once summaries are captured as JSON (one object per meeting under `meetings`), three tools check them. All read `--meetings FILE`, print text or `--format json` (`--json` is the same), and `--example` prints a valid input.

| Tool | Checks |
|------|--------|
| `action_item_tracker.py` | Completion rate, overdue items, owners with the most open work, items with no owner or date. `--as-of YYYY-MM-DD` sets the date for overdue checks; it defaults to the latest meeting date so old notes give a stable result. |
| `decision_log_builder.py` | Numbered decision log (`DEC-YYYYMMDD-NNN`), rationale coverage, high-impact decisions marked reversible. `--search TEXT` filters by keyword. |
| `meeting_effectiveness_scorer.py` | 0-100 per meeting from decisions, owned/dated actions, time per output, agenda coverage and attendee count. |

```bash
python3 project-management/execution/summarize-meeting/scripts/action_item_tracker.py \
  --meetings project-management/execution/summarize-meeting/assets/sample_meetings.json
python3 project-management/execution/summarize-meeting/scripts/decision_log_builder.py \
  --meetings project-management/execution/summarize-meeting/assets/sample_meetings.json --search postgres
python3 project-management/execution/summarize-meeting/scripts/meeting_effectiveness_scorer.py \
  --meetings project-management/execution/summarize-meeting/assets/sample_meetings.json --format json
```

On the sample: 5 actions, 2 done, 1 overdue (Carol, 4 days as of 2026-03-14), 1 with no owner or date; 3 decisions with 67% rationale coverage; the status sync with eight people, no agenda and no decision scores lowest.

**Exit codes:** `0` report produced · `2` missing or unreadable file, invalid JSON, or the wrong shape (top level not an object, `meetings` not a list). The tools report findings; they do not gate.

## Anti-Patterns

### Posting an AI summary without review
**Mistake:** A transcription tool's auto-summary is posted as the official summary, with nobody checking it.
**Why it happens:** The output looks finished, and the 24-hour distribution window pushes people to send it as is.
**Instead:** Treat any machine-generated summary as a draft. Someone who attended checks names, who decided what, and whether each action item was actually agreed, then adds a "reviewed by" line. No "reviewed by" line means it is still a draft.

### Sensitive details sent to a wide list
**Mistake:** A summary that goes beyond the attendees includes personnel feedback, a customer's commercial terms, or in-flight legal language.
**Why it happens:** The summarizer captures everything said in the room, and the distribution list is set by habit.
**Instead:** If anyone outside the meeting is on the distribution list, run a redaction pass before sending. Confirm confidentiality limits up front (see Clarify First). Once the email is sent, you cannot recall it.

### Pasting the transcript as the summary
**Mistake:** The "summary" is four pages of who said what.
**Why it happens:** Copying the transcript feels safe because nothing is left out.
**Instead:** Compress it into the template's sections: discussion points, numbered decisions, action items and open questions. If the summary runs past a page of named-speaker dialogue, cut it down.

Seven more, each with a bad and a good example: `references/red-flags.md`.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/summarization-process.md](references/summarization-process.md)** — the full six-step methodology (metadata → discussion → actions → decisions → open questions → distribute), the output template, focus priorities, troubleshooting table, and success criteria. Read when producing a summary.
- **[references/meeting-facilitation-guide.md](references/meeting-facilitation-guide.md)** — meeting types, note-taking strategies, and anti-patterns. Read to tailor the summary to the meeting type or improve input quality.
- **[references/red-flags.md](references/red-flags.md)** — common ways summaries go wrong with bad/good examples. Read before posting, emailing, or linking a summary.
- **[assets/meeting_summary_template.md](assets/meeting_summary_template.md)** — ready-to-use fill-in template. Use to draft the summary directly.

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

## Files

| File | Purpose |
|------|---------|
| `scripts/action_item_tracker.py` | Action completion, overdue and ownership report |
| `scripts/decision_log_builder.py` | Decision log with rationale coverage |
| `scripts/meeting_effectiveness_scorer.py` | Per-meeting effectiveness score |
| `assets/sample_meetings.json` | Three meetings that exercise all three tools |
| `assets/meeting_summary_template.md` | Fill-in summary template |
| `examples/product-review-may-22.md` | Worked summary |
