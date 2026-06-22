---
name: meeting-insights
description: >
  Analyze meeting transcripts to extract decisions, action items, owners, due
  dates, open questions, and risks. Use after recorded meetings, sales calls,
  customer interviews, or planning sessions, or to build a decision log.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: meetings
  updated: 2026-05-04
  python-tools: transcript_analyzer.py
  tech-stack: meetings, async-collaboration
---

# Meeting Insights

Turn raw meeting transcripts into a structured set of decisions, action items, owners, due dates, open questions, and risks.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Templates](#templates)
- [Best Practices](#best-practices)

---

## Keywords

meeting, meetings, transcript, notes, minutes, action items, decisions, decision log, follow-up, recap, sales call, customer interview, retrospective, standup, planning, async

---

## Clarify First

Before extracting insights, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Transcript with speaker labels** — `Speaker: text` format drives owner attribution on action items
- [ ] **Meeting type** — recap vs customer interview vs decision log changes which extractions matter (decisions/actions vs pains/quotes)
- [ ] **Output target** — recap email, append-only decision log, or interview synthesis sets the structure of the deliverable

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

---

## Quick Start

### Process a Transcript in 5 Minutes

1. Save your transcript text as `transcript.txt` (one speaker turn per line, format `Speaker: text`)
2. Run:
   ```bash
   python scripts/transcript_analyzer.py transcript.txt
   ```
3. Review the structured output: decisions, action items, owners, due dates, open questions
4. Drop into `assets/recap_template.md` to send a follow-up

---

## Core Workflows

### Workflow 1: Post-Meeting Recap

**Goal:** Convert a 60-minute conversation into a 90-second readable summary that everyone can act on.

**Steps:**
1. Export the transcript (Otter, Fireflies, Zoom, Google Meet, etc.)
2. Run: `python scripts/transcript_analyzer.py transcript.txt`
3. Verify owners and due dates — the analyzer is heuristic; humans correct
4. Paste structured output into `assets/recap_template.md`
5. Send within 24 hours of the meeting

**Expected Output:** Recap with decisions, action items (owner + due date), open questions, and risks.

**Time Estimate:** 5-10 minutes vs. 30+ for manual note review.

### Workflow 2: Customer Interview Synthesis

**Goal:** Pull the signals out of a discovery call without losing the customer's actual words.

**Steps:**
1. Run analyzer in JSON mode: `python scripts/transcript_analyzer.py transcript.txt --json`
2. Filter for `pains` and `quotes` — these are the discovery signals
3. Use `references/insight_extraction_patterns.md` to triangulate across multiple interviews
4. Tag findings by ICP segment for product / marketing handoff

**Expected Output:** Tagged customer pain list with verbatim quotes per insight.

**Time Estimate:** 15 minutes per interview after the call.

### Workflow 3: Decision Log Maintenance

**Goal:** Build an organizational memory so the same decision is not re-litigated quarter after quarter.

**Steps:**
1. After each meeting, run the analyzer to extract decisions
2. Append to a running decision log keyed by date and topic
3. When a future meeting raises an old topic, search the log first
4. Re-open formally rather than silently overturning

**Expected Output:** Append-only decision log searchable by topic and date.

**Time Estimate:** 2-3 minutes per meeting.

---

## Tools

### transcript_analyzer.py

Reads a transcript text file and extracts:

- **Decisions** — sentences with decision markers ("we decided", "agreed", "going with")
- **Action items** — sentences with action markers ("will", "going to", "by next week"), with heuristic owner + due date
- **Open questions** — sentences ending in "?" or marked with "open question"
- **Risks** — sentences with risk markers ("risk", "concern", "blocker", "if X then Y")
- **Quotes** — distinctive verbatim sentences > 12 words (for customer interview workflows)

```bash
# Human-readable
python scripts/transcript_analyzer.py transcript.txt

# JSON for programmatic use
python scripts/transcript_analyzer.py transcript.txt --json
```

**Transcript format expected:**

```
Alice: We need to decide on the launch date this week.
Bob: I'll send the draft by Friday.
Alice: Are we blocked on legal review?
Bob: Yes, that's the risk — if legal slips, launch slips.
```

---

## Reference Guides

- **`references/insight_extraction_patterns.md`** — Heuristic triggers for decisions, actions, and risks; how to triangulate across interviews

---

## Templates

- **`assets/recap_template.md`** — Post-meeting recap email with placeholder sections

---

## Best Practices

- **Verify before sending.** The analyzer is heuristic; an unverified recap that mis-attributes an action item destroys trust.
- **Owner + date or it does not exist.** An action item without an owner is a hope; without a date, it is a wish.
- **Send within 24 hours.** Memory of who said what fades fast; recap latency directly correlates with action-item completion rate.
- **Quote verbatim.** For customer interviews, the customer's words matter more than your summary of them.
- **Decision log is append-only.** Never silently overturn — re-open with a dated update.

---

## Integration Points

- Pairs with `product-team/user-story/` for converting interview pains into stories
- Pairs with `project-management/` for action-item tracking
- Feeds into `marketing/` voice-of-customer workflows
