---
name: calendar-prep
description: >
  Generate one-page meeting briefings from structured input (attendees, prior
  context, decisions needed). Use before customer calls, board meetings, or
  1:1s to prepare a pre-read or briefing.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: meetings
  updated: 2026-05-04
  python-tools: meeting_prep_briefer.py
  tech-stack: meetings, productivity
---

# Calendar Prep

Convert structured meeting context into a one-page briefing in seconds.

---

## Keywords

meeting prep, calendar prep, briefing, pre-read, pre-meeting, talking points, agenda, board meeting, customer call, 1:1

---

## Clarify First

Before generating the briefing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Meeting type & attendees** — customer call vs board vs 1:1 changes the briefing's structure, tone, and emphasis
- [ ] **Your goal / decision sought** — this becomes the front-loaded first line of the briefing
- [ ] **Prior context** — last contact, open issues, current status; without it the briefing is generic and useless

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

---

## Quick Start

1. Fill in `assets/meeting_input.json` with attendees, context, decisions needed, supporting links
2. Run: `python scripts/meeting_prep_briefer.py meeting_input.json`
3. Read the briefing 5 minutes before the meeting

---

## Core Workflows

### Workflow 1: Customer Call Prep
1. Pull the customer's recent activity, last meeting notes, current account status
2. Fill input JSON with: attendees, last contact, open issues, your goal, decisions you're trying to make
3. Run briefer
4. Walk in knowing: what you want, what they want, where you have leverage

**Time Estimate:** 10-15 minutes per major customer call.

### Workflow 2: Board / Investor Meeting Prep
1. Pull metrics dashboard, prior board deck, last investor update
2. Build input JSON; emphasize decisions sought from the board
3. Pair output with `documents/pptx-toolkit/` deck audit

**Time Estimate:** 30-60 minutes per board meeting.

### Workflow 3: Manager 1:1 Prep
1. Compress the past two weeks: top 3 wins, top 3 challenges, top 3 asks
2. Run briefer
3. Lead with asks (1:1s default to status; the leverage is in asking)

**Time Estimate:** 5-10 minutes per 1:1.

---

## Tools

### meeting_prep_briefer.py

Reads a structured JSON input describing meeting context and produces a one-page briefing in markdown.

```bash
python scripts/meeting_prep_briefer.py meeting_input.json
python scripts/meeting_prep_briefer.py meeting_input.json --json
```

---

## Reference Guides

- **`references/briefing_methodology.md`** — When briefings help and when they don't, format conventions

---

## Templates

- **`assets/meeting_input.json`** — Input file template

---

## Best Practices

- **One page max.** A 3-page briefing is one you won't read.
- **Front-load the decision.** The first sentence should be the decision you want.
- **Read the briefing.** Generating one without reading it is performance theater.
- **Capture outputs.** Pair with `personal-productivity/meeting-insights/` post-meeting to convert the briefing's questions into the meeting's decisions.
