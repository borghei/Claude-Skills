---
name: internal-comms
description: >
  Plan, sequence, and pressure-test internal announcements before they send.
  Use when announcing a reorg, policy, or product change, drafting an all-hands
  or exec update, or deciding who hears what and in which order.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-operations
  domain: internal-communications
  updated: 2026-07-21
  tags: [internal-comms, change-management, announcements, all-hands, stakeholder-sequencing]
---

# Internal Communications

Internal communication fails in predictable ways: the wrong people hear it first, the message
explains the decision but not the consequence, and nobody tests the draft before it reaches
2,000 inboxes. This skill treats an announcement as an artifact with a blast radius, a
sequence, and a pass/fail quality bar — not as a writing exercise.

The three levers are **who hears it in what order**, **what the message must contain**, and
**which channel carries it**. Get those right and tone matters far less than people assume.

## When to use this skill

- Announcing a **reorg, layoff, or leadership change** where sequencing errors are unrecoverable
- Rolling out a **policy change** (RTO, expenses, security, performance process) that people must act on
- Communicating a **product or system migration** with a deadline and a required user action
- Structuring a recurring **all-hands or weekly exec update** that currently reads as a status dump
- **Pressure-testing a draft** before send: reading level, jargon density, missing elements
- Deciding **channel and cadence** for a multi-week change programme rather than a one-shot email

## Inputs the skill expects

- The **change itself**: what is changing, effective date, whether it is reversible
- **Audience list** with impact level (high / medium / low) and rough headcount per group
- **Draft text**, if one exists (plain markdown or text is fine)
- **Constraints**: embargo, legal review, regulatory disclosure, market-sensitivity
- **Available channels** and which ones your org actually reads
- **Who can answer questions** after send, and where

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Blast radius — who is materially affected vs merely informed** — this decides whether you need a cascade (manager-first) or a single broadcast, and cascades cost 3-5 days
- [ ] **Reversibility of the decision** — reversible changes can be announced as proposals with a feedback window; irreversible ones must never be, because inviting input you will ignore is the fastest way to lose trust
- [ ] **Effective date and the required user action** — sets every T-offset in the plan and determines whether the message is informational or instructional
- [ ] **Whether anything is legally or market-sensitive** — embargo constraints override the ideal sequence and force simultaneous rather than cascaded delivery

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Audit a draft before it sends

Run this on every announcement that reaches more than ~50 people. It takes 30 seconds and
catches the failure modes that generate the most follow-up questions.

1. Save the draft as JSON with `title`, `body`, `audience`, and `channel`.
2. Run the auditor. It scores five required elements (what changed, why, who is affected,
   what to do, where to ask), reading grade, jargon density, and hedging.
3. Fix every `FAIL` element. Treat `WARN` on reading grade as advisory unless the audience
   includes non-native speakers or frontline staff, in which case treat it as `FAIL`.
4. Re-run until the score clears 75.

```bash
python3 business-operations/internal-comms/scripts/announcement_auditor.py \
  --input business-operations/internal-comms/assets/sample_announcement.json \
  --min-score 75 --format text
```

### Workflow 2 — Sequence a change communication

1. Describe the change and list audiences with impact and headcount.
2. Run the sequencer. It computes blast radius, orders audiences by a
   *impact-then-influence* rule, and assigns T-offsets in days relative to broadcast.
3. Review the manager-enablement step — if the plan says you need one and you skip it,
   managers learn about the change from their own reports, which is the single most
   common reorg comms failure.
4. Export the plan and assign an owner per step.

```bash
python3 business-operations/internal-comms/scripts/comms_sequencer.py \
  --input business-operations/internal-comms/assets/sample_change.json \
  --format text
```

### Workflow 3 — Pick the channel

1. Characterise the message on six dimensions: urgency, complexity, audience size,
   sensitivity, whether it needs two-way discussion, and whether it needs a durable record.
2. Run the scorer to rank channels and see which are actively disqualified.
3. Use the top-ranked channel as the primary, and the highest-ranked *durable* channel
   as the system of record. Never let a chat message be the record.

```bash
python3 business-operations/internal-comms/scripts/channel_fit_scorer.py \
  --input business-operations/internal-comms/assets/sample_message_profile.json \
  --top 4 --format json
```

## Decision frameworks

### Blast radius → sequence pattern [PROVEN]

Blast radius is the count of people whose *work or employment changes*, not the count who
receive the email.

| Radius | Pattern | Lead time before broadcast | Manager enablement |
|--------|---------|----------------------------|--------------------|
| 1-10 | Direct 1:1 conversations, then quiet team note | Same day | Not needed |
| 11-50 | Manager brief → team meetings → written follow-up | 1-2 days | Required, 60-min session |
| 51-250 | Exec brief → manager brief + FAQ → all-hands → written | 3-5 days | Required, with talk track + FAQ |
| 250+ | Add a pre-brief for informal influencers and a 2-week reinforcement cadence | 5-10 days | Required, plus a manager Q&A channel |

Escape hatch: legal embargo or market sensitivity collapses this to a simultaneous broadcast.
When that happens, say so in the message — "we could not brief managers first because of
disclosure rules" — rather than letting people infer carelessness.

### The five required elements [PROVEN]

Every announcement of consequence answers these, in this order. A message missing any one of
them generates a predictable class of follow-up question.

| Element | Missing it produces | Minimum bar |
|---------|--------------------|-------------|
| **What changed** | "Wait, is this happening now or later?" | One sentence, in the first paragraph, with the effective date |
| **Why** | Rumour and worst-case theory | The actual reason, including the constraint that forced it |
| **Who is affected** | Every reader assumes it is them | Named groups, plus an explicit "if you are not in these groups, nothing changes for you" |
| **What to do** | Nothing happens | An action with a deadline, or the words "no action needed" |
| **Where to ask** | Questions go to the wrong people | A named human or channel, plus when they will respond |

### Message-type → structure [RECOMMENDED]

| Type | Lead with | Length | Feedback window |
|------|-----------|--------|-----------------|
| Irreversible decision (reorg, layoff, shutdown) | The decision | 300-500 words | None — do not solicit input |
| Reversible policy | The problem being solved | 400-700 words | 5-10 business days |
| Migration / deadline | The action and the date | 200-350 words | Questions only |
| Celebratory / milestone | The outcome and who did it | 150-250 words | None |
| Bad news (incident, miss) | What happened, in plain words | 250-400 words | Post-mortem link |

### Cadence for a multi-week change [RECOMMENDED]

Announce once and people forget; announce weekly and they tune out. The pattern that holds:
**T-0 announcement, T+3 days FAQ update, T+1 week manager check-in, T+2 weeks progress note,
T+4 weeks close-out.** Five touches, decreasing in length. See
`references/change-comms-cadence.md` for the full grid including reinforcement channels.

## Anti-Patterns

### The Broadcast Ambush
**Mistake:** Sending a reorg or policy announcement to all-staff without briefing managers first.
**Why it happens:** Leadership fears leaks, and a simultaneous send feels "fair" and egalitarian.
**Instead:** Brief managers 24-48 hours ahead with a talk track and an FAQ, and tell them
explicitly what they may and may not repeat. A manager who cannot answer their team's first
question loses standing that takes months to rebuild. If leak risk is genuinely severe,
compress the window to 2 hours rather than eliminating it.

### Burying the Decision Under the Reasoning
**Mistake:** Opening with three paragraphs of market context before stating what is changing.
**Why it happens:** The author wants the reader to reach the same conclusion they did, so they
reconstruct their own reasoning path.
**Instead:** State the decision in sentence one, then the reasoning. Readers who disagree will
read the reasoning more carefully, not less. Context-first structure reads as though you are
building a case, which signals defensiveness.

### The Fake Consultation
**Mistake:** Announcing a settled decision with "we'd love your feedback" attached.
**Why it happens:** It softens the delivery and feels more collaborative than a flat directive.
**Instead:** If the decision is settled, say so: "This is decided. Here is what we considered."
If input can genuinely change the outcome, say what specifically is still open and by when.
Solicited-then-ignored feedback is measurably worse for trust than no consultation at all.

### Jargon as Cushioning
**Mistake:** "We are realigning our operating model to better leverage synergies across pods."
**Why it happens:** Abstraction makes uncomfortable news feel less blunt to the person writing it.
**Instead:** Write the sentence a person would say out loud. The auditor flags jargon density
above 2% of words; anything above that on a high-impact message means the draft is hiding
something, and readers will assume the worst thing it could be hiding.

### No Named Owner for Questions
**Mistake:** Ending with "reach out with any questions."
**Why it happens:** Nobody wants to volunteer their calendar.
**Instead:** Name a person or a specific channel and a response commitment ("#change-rto,
answered within one business day"). Unrouted questions become hallway conversations,
and hallway conversations become the version of the message people remember.

## Files

| File | Purpose |
|------|---------|
| `scripts/announcement_auditor.py` | Scores a draft on required elements, reading grade, jargon, hedging, and structure |
| `scripts/comms_sequencer.py` | Builds an ordered, T-offset communication plan from a change description and audience list |
| `scripts/channel_fit_scorer.py` | Ranks communication channels against a six-dimension message profile |
| `references/announcement-archetypes.md` | Eight announcement archetypes with structure, length, and worked openings |
| `references/change-comms-cadence.md` | Timing grids, reinforcement schedules, and manager-enablement content |
| `assets/announcement-template.md` | Fill-in template enforcing the five required elements |
| `assets/comms-plan-template.md` | Sequencing plan table with owner, channel, and T-offset columns |
| `assets/sample_announcement.json` | Runnable input for `announcement_auditor.py` |
| `assets/sample_change.json` | Runnable input for `comms_sequencer.py` |
| `assets/sample_message_profile.json` | Runnable input for `channel_fit_scorer.py` |
