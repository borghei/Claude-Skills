---
name: decision-questionnaire
description: >
  Turn a blocked decision into an async questionnaire a stakeholder can answer
  without a meeting. Use when you need someone else's input to decide, a meeting
  would be overkill, or answers from several people must be consolidated.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: questionnaire_linter.py, answer_consolidator.py
  tech-stack: async-decisions, stakeholder-input, decision-records, questionnaires
  tags:
    - decision-making
    - async
    - questionnaire
    - stakeholders
    - decision-record
---

# Decision Questionnaire

Some decisions stall because the knowledge sits with someone else. A meeting costs everyone an hour; "thoughts?" gets a vague reply. A structured questionnaire costs the recipient fifteen minutes and returns comparable, recordable answers.

The agent interviews the sender only about the send (who, what they need back, by when, what happens on silence), never the subject they cannot answer. It writes neutral, one-idea questions with answer formats, gates the draft, and consolidates replies into a decision record.

## When to Use

- A decision is blocked on knowledge that one to five specific people hold
- You would otherwise book a meeting just to ask questions
- Answers came back and must become a recorded decision

## Clarify First

What most shapes the questionnaire is the gap between what the recipient knows and what the sender needs. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Recipient and what they know:** role and expertise set tone, how much context to carry, and which questions only they can answer.
- **What you must walk away able to decide:** each question has to unblock one of these outputs, or it gets cut.
- **Deadline and default if silent:** without both, silence blocks the work instead of resolving it.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Gate a draft before sending (exit 1 = not ready)
python3 project-management/execution/decision-questionnaire/scripts/questionnaire_linter.py \
  --input project-management/execution/decision-questionnaire/assets/sample_questionnaire_flawed.json \
  --today 2026-11-08
```

```bash
# Consolidate replies into a decision-record draft (exit 1 = critical question still blocked)
python3 project-management/execution/decision-questionnaire/scripts/answer_consolidator.py \
  --input project-management/execution/decision-questionnaire/assets/sample_questionnaire_clean.json \
  --answers project-management/execution/decision-questionnaire/assets/sample_answers_conflict.json \
  --today 2026-11-19 --format json
```

## Tools Overview

| Tool | Reads | Reports |
|---|---|---|
| `questionnaire_linter.py` | Questionnaire JSON | Missing header fields, past deadline, leading/vague/compound wording, missing formats, units or choices, options without trade-offs, size over budget |
| `answer_consolidator.py` | Questionnaire + responses | Answers per question, "don't know", conflicts, missing respondents, outcome `ready-to-record` / `needs-follow-up` / `default-applied` |

### Exit code contract

| Code | Linter | Consolidator |
|---|---|---|
| 0 | Ready to send (warnings allowed) | Ready to record, or default applied |
| 1 | At least one error finding | A critical question is unanswered before the deadline or in conflict |
| 2 | Missing file, invalid JSON, bad date | Same |

## Workflow

1. **Interview the send, not the subject.** [PROVEN] Ask who it goes to, what they know that the sender doesn't, and what the sender must be able to decide afterwards. Cut every question the sender could answer by looking it up.
2. **Write the header.** Purpose, the decision riding on it, sender and recipients, how answers will be used, a context paragraph under 150 words for someone in none of the meetings, deadline, effort, and the default action if nobody answers.
3. **Lay out the options.** [RECOMMENDED] Two to four, each with its trade-off; mark at most one as the sender's lean; add "none of these".
4. **Write the questions.** One idea each, neutral, most important first, grouped by theme, each with a format: pick-one, ranked, number with unit, yes-no with condition, or capped free text. "Why this matters" only where misreadable. End with one catch-all.
5. **Validate against the quality gate.** Run `questionnaire_linter.py`; it must pass with zero errors before sending. Then read it once as the recipient and check the hand-review checklist in `references/question-design.md` (hidden premises, loaded descriptors).
6. **Send with a four-line message** (what, why you, time and deadline, default) and one answer channel.
7. **Remind once, then last-call** a day before the deadline, asking only blocking questions.
8. **Consolidate and record.** [RECOMMENDED] Run `answer_consolidator.py`, settle critical conflicts, fill `assets/decision_record_template.md`, and send it to every recipient.

```bash
python3 project-management/execution/decision-questionnaire/scripts/answer_consolidator.py \
  --input project-management/execution/decision-questionnaire/assets/sample_questionnaire_clean.json \
  --answers project-management/execution/decision-questionnaire/assets/sample_answers.json --today 2026-11-19
```

## Anti-Patterns

### The Leading Question
**Mistake:** "Don't you think Frankfurt is the safest choice?"
**Why it happens:** The sender has a lean and wants it confirmed.
**Instead:** State the lean once in the options table, labelled, then ask "Which option would you approve?"

### The Thoughts Dump
**Mistake:** A link to a design doc and "Thoughts?"
**Why it happens:** Writing questions forces the sender to work out what they need.
**Instead:** Turn each unknown into a formatted question; keep one open question, at the end.

### No Default on Silence
**Mistake:** A deadline with no stated consequence, so the decision waits indefinitely.
**Why it happens:** Stating a default feels presumptuous.
**Instead:** Write the action you will take on silence; anyone who dislikes it now has a reason to reply.

### The Survey Creep
**Mistake:** Twenty-five questions, half of them nice-to-know.
**Why it happens:** Every stakeholder adds "while we're asking…".
**Instead:** Hold to about ten questions and fifteen minutes; defer the rest.

### Merging Conflicts Away
**Mistake:** Two respondents disagree and the record reports only the majority view.
**Why it happens:** A clean record looks more decisive.
**Instead:** Record each conflict and how it was settled; hidden disagreements reopen decisions.

## Files

| File | Purpose |
|---|---|
| `scripts/questionnaire_linter.py` | Pre-send gate |
| `scripts/answer_consolidator.py` | Replies to decision-record draft |
| `assets/questionnaire_template.md`, `assets/decision_record_template.md` | Templates |
| `assets/sample_questionnaire_clean.json` / `_flawed.json` | Linter exits 0 / 1 |
| `assets/sample_answers.json` / `sample_answers_conflict.json` | Consolidator exits 0 / 1 |

## Reference Documentation

- [references/question-design.md](references/question-design.md) — gap analysis, wording, the five answer formats, sizing, linter codes, hand-review checklist. Read while drafting.
- [references/sending-and-consolidating.md](references/sending-and-consolidating.md) — async vs meeting, multi-recipient variants, follow-up cadence, consolidator outcomes, the decision record. Read before sending.

## Scope & Limitations

**In Scope:** async questionnaires for blocked decisions, multi-recipient variants, pre-send linting, consolidating answers into a decision record.

**Out of Scope:**
- Who decides, approves and is consulted (see `project-management/execution/daci-framework/`)
- Live customer discovery interviews (see `project-management/discovery/customer-interview-script/`)
- Large-sample surveys and statistical analysis of responses
- Broad stakeholder engagement planning (see `project-management/execution/stakeholder-map/`)

**Important Caveats:**
- The linter reads JSON, not prose; render the sent version with the template.
- Wording checks are pattern-based and miss loaded adjectives and hidden premises; a human read is still required.
- Effort estimates are a sizing aid. The consolidator matches respondents by exact name and does not judge free text.
