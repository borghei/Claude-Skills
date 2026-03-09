---
name: decision-logger
description: >
  Two-layer memory architecture for tracking executive decisions. Layer 1 stores raw
  deliberation transcripts, Layer 2 stores founder-approved decisions only. Future
  sessions read Layer 2 to prevent hallucinated consensus from past debates. Handles
  conflict detection, supersession tracking, DO_NOT_RESURFACE enforcement, overdue
  action item alerts, and decision search. Use when logging decisions, reviewing past
  decisions, checking overdue items, detecting conflicting decisions, or when user
  mentions decision log, decision history, past decisions, action items, decision
  tracking, or decision review.
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: c-level
  domain: decision-memory
  updated: 2026-03-09
  frameworks:
    - two-layer-memory
    - conflict-detection
    - supersession-tracking
    - action-item-management
    - decision-search
  triggers:
    - decision log
    - log decision
    - past decisions
    - decision history
    - action items
    - overdue items
    - decision review
    - decision conflict
    - decision tracking
    - board minutes
    - approved decisions
    - decision search
    - what did we decide
    - reopen decision
  cross-references:
    - c-level-advisor/chief-of-staff
    - c-level-advisor/board-meeting
    - c-level-advisor/strategic-alignment
    - c-level-advisor/executive-mentor
---

# Decision Logger

Two-layer memory system for executive decisions. Layer 1 stores everything discussed. Layer 2 stores only what the founder approved. Future sessions read Layer 2 only -- this prevents hallucinated consensus from past debates bleeding into new deliberations.

## Keywords

decision log, memory, approved decisions, action items, board minutes, conflict detection, DO_NOT_RESURFACE, decision history, overdue, supersession, decision search, decision tracking, accountability

---

## Two-Layer Architecture

### Why Two Layers?

Single-layer decision logs create a dangerous problem: agents read old debates, rejected proposals, and discarded ideas, then treat them as context for new decisions. This causes "hallucinated consensus" where rejected ideas gradually become accepted through repetition.

The two-layer system prevents this by strictly separating raw discussion from approved decisions.

### Layer Architecture

```
Layer 1: Raw Transcripts (NEVER auto-loaded)
  Location: memory/board-meetings/YYYY-MM-DD-raw.md
  Contains: Full deliberation, all perspectives, rejected arguments
  Loaded: Only on explicit founder request
  Retention: Active 90 days, then archived

Layer 2: Approved Decisions (AUTO-LOADED every session)
  Location: memory/board-meetings/decisions.md
  Contains: Only founder-approved decisions and action items
  Loaded: Automatically at start of every board meeting (Phase 1)
  Mutation: Append-only. Decisions are never deleted, only superseded.
```

### Layer Interaction Rules

| Rule | Rationale |
|------|-----------|
| Layer 2 is append-only | Preserves complete decision history |
| Layer 1 is never auto-loaded | Prevents hallucinated consensus |
| Only Chief of Staff writes to Layer 2 | Single point of control |
| Agents never write directly | All writes go through Chief of Staff after founder approval |
| Superseded decisions stay in Layer 2 | History is the record; nothing is deleted |

---

## Decision Entry Format

### Standard Decision Record

```markdown
## [YYYY-MM-DD] -- [DECISION TITLE]

**Decision:** [One clear statement of what was decided]
**Context:** [1-2 sentences on why this decision was needed]
**Owner:** [One person or role accountable for execution]
**Deadline:** [YYYY-MM-DD]
**Review Date:** [YYYY-MM-DD]
**Confidence:** [High / Medium / Low]
**Rationale:** [Why this option over alternatives, 1-2 sentences]

**User Override:** [If founder changed agent recommendation -- what and why]

**Rejected Alternatives:**
- [Proposal] -- [reason for rejection] [DO_NOT_RESURFACE]
- [Proposal] -- [reason for rejection]

**Action Items:**
- [ ] [Action] -- Owner: [name] -- Due: [YYYY-MM-DD]
- [ ] [Action] -- Owner: [name] -- Due: [YYYY-MM-DD]

**Dependencies:** [Other decisions this depends on]
**Supersedes:** [DATE of previous decision on same topic, if any]
**Superseded by:** [Filled retroactively if overridden later]
**Raw transcript:** memory/board-meetings/[DATE]-raw.md
**Tags:** [topic tags for search -- e.g., pricing, hiring, market-entry]
```

### Completed Action Item Format

```markdown
- [x] [Action] -- Owner: [name] -- Completed: [YYYY-MM-DD] -- Result: [one sentence]
```

---

## Conflict Detection System

Before logging any new decision, the system checks for three types of conflicts.

### Conflict Type 1: DO_NOT_RESURFACE Violation

A new decision matches a previously rejected proposal.

```
Detection: New proposal text similarity > 70% to a rejected proposal

Response:
  BLOCKED: "[Proposal]" was rejected on [DATE].
  Reason: [original rejection reason]

  To reopen: Founder must explicitly say "reopen [topic] from [DATE]"
  This cannot be overridden by agents.
```

### Conflict Type 2: Topic Contradiction

Two active decisions on the same topic reach different conclusions.

```
Detection: Same tags + contradictory conclusions

Response:
  DECISION CONFLICT DETECTED

  Active decision (older): [DATE] -- [decision text]
  New decision: [DATE] -- [decision text]

  These decisions contradict each other.

  Options:
  1. Supersede old decision (new replaces old)
  2. Merge decisions (reconcile the conflict)
  3. Defer to founder (present both, let founder choose)
```

### Conflict Type 3: Owner Conflict

Same action assigned to different people in different decisions.

```
Detection: Same action description, different owners

Response:
  OWNER CONFLICT

  Action: "[action text]"
  Decision 1 ([DATE]): Owner = [Person A]
  Decision 2 ([DATE]): Owner = [Person B]

  Resolve: Which owner is correct?
```

### Conflict Resolution Decision Tree

```
START: Conflict detected
  |
  v
[What type of conflict?]
  |
  +-- DO_NOT_RESURFACE --> Block automatically. Only founder can reopen.
  |
  +-- Topic contradiction --> [Is the new decision from a board meeting?]
  |                           |
  |                           +-- YES --> Supersede old by default (board > individual)
  |                           +-- NO  --> Present both to founder for resolution
  |
  +-- Owner conflict --> [Which decision is more recent?]
                         |
                         +-- Flag to founder with both dates
                         +-- Default to more recent unless founder overrides
```

---

## Decision Lifecycle

### States

```
PROPOSED --> APPROVED --> ACTIVE --> [COMPLETED | SUPERSEDED | EXPIRED]

PROPOSED:    Agent synthesis presented to founder
APPROVED:    Founder explicitly approved
ACTIVE:      Being executed, action items in progress
COMPLETED:   All action items done, review confirmed success
SUPERSEDED:  New decision replaced this one
EXPIRED:     Review date passed without renewal
```

### State Transitions

| From | To | Trigger | Who |
|------|----|---------|-----|
| Proposed | Approved | Founder says "yes" or "approve" | Founder |
| Proposed | Rejected | Founder says "no" or "reject" | Founder |
| Approved | Active | Action items begin execution | Automatic |
| Active | Completed | All action items marked done | Chief of Staff |
| Active | Superseded | New decision on same topic | Chief of Staff |
| Active | Expired | Review date passed, no renewal | System alert |

---

## Logging Workflow

### Post-Decision Logging (after Board Meeting Phase 5)

```
Step 1: Founder approves synthesis
  |
Step 2: Write Layer 1 raw transcript
  --> memory/board-meetings/YYYY-MM-DD-raw.md
  |
Step 3: Run conflict detection against decisions.md
  |
  +-- Conflicts found --> Surface to founder, wait for resolution
  +-- No conflicts --> Continue
  |
Step 4: Append approved entries to decisions.md (Layer 2)
  |
Step 5: Set review dates and action item deadlines
  |
Step 6: Confirm to founder:
  "Logged: [N] decisions, [M] action items tracked, [K] flags added"
```

---

## Action Item Management

### Overdue Detection

At the start of every session, scan for:

1. Action items past their deadline
2. Decisions with review dates that have passed
3. Decisions older than 90 days with no completion status

### Alert Format

```
OVERDUE ITEMS (as of [today's date])

Action Items Past Deadline:
  1. [Action] -- Owner: [name] -- Due: [date] -- [X] days overdue
     From decision: [decision title] ([date])

  2. [Action] -- Owner: [name] -- Due: [date] -- [X] days overdue

Decisions Pending Review:
  1. [Decision title] -- Review was due: [date]
     Original decision: [summary]
     Prompt: "You decided [X] on [date]. Worth a check-in?"

Stale Decisions (> 90 days, no status update):
  1. [Decision title] -- Decided: [date] -- Last update: [date]
```

### Action Item Priority Matrix

| Urgency | Impact | Priority | Response |
|---------|--------|----------|----------|
| Overdue | High | Critical | Escalate to founder immediately |
| Overdue | Low | High | Flag in next session |
| Due this week | High | High | Surface proactively |
| Due this week | Low | Medium | Include in weekly summary |
| Due next month | Any | Low | Monitor only |

---

## Search and Retrieval

### Search Capabilities

| Query Type | Example | Returns |
|-----------|---------|---------|
| By topic | "pricing" | All decisions tagged with pricing |
| By owner | "CTO" | All decisions and actions owned by CTO |
| By date range | "Q4 2025" | All decisions from Oct-Dec 2025 |
| By status | "overdue" | All overdue action items |
| By conflict | "conflicts" | All detected contradictions |
| By tag | "hiring AND engineering" | Intersection of tags |

### Decision Summary Views

| View | Contents | When Used |
|------|----------|-----------|
| Last 10 | Most recent 10 approved decisions | Default quick view |
| Full history | All decisions, chronological | Audit or deep review |
| By owner | Grouped by accountable person | Accountability check |
| By topic | Grouped by tag | Strategic review |
| Overdue only | Only overdue items | Action management |
| Active only | Only decisions with open action items | Execution tracking |

---

## File Structure

```
memory/
  board-meetings/
    decisions.md           # Layer 2: append-only, founder-approved
    YYYY-MM-DD-raw.md      # Layer 1: full transcript per meeting
    archive/
      YYYY/                # Raw transcripts after 90 days
```

---

## Integration with Other Skills

| Skill | Integration Point |
|-------|------------------|
| Chief of Staff (`chief-of-staff`) | Manages the logging workflow, writes to Layer 2 |
| Board Meeting (`board-meeting`) | Triggers logging after Phase 5 approval |
| Strategic Alignment (`strategic-alignment`) | Checks if decisions cascade properly to team goals |
| Executive Mentor (`executive-mentor`) | Reviews stale decisions for re-evaluation |
| Org Health (`org-health-diagnostic`) | Decision velocity as health indicator |

---

## Red Flags

- Same topic discussed 3+ times without a logged decision -- decision avoidance
- Action items consistently overdue by the same owner -- capacity or accountability issue
- Decisions made without checking history -- risk of contradiction
- Layer 1 being loaded without explicit request -- hallucinated consensus risk
- No review dates set on decisions -- decisions age without re-evaluation
- Rejected proposals resurfacing in new language -- DO_NOT_RESURFACE not enforced
- Decision log not consulted at start of board meetings -- institutional memory not used
- All decisions owned by one person -- bottleneck or delegation failure

---

## Proactive Triggers

- Review date passed on a decision -- prompt: "You decided [X] on [date]. Worth checking in?"
- Action item overdue > 7 days -- escalate to founder with owner context
- Same topic area has 3+ active decisions -- consolidation review needed
- 30+ days without any logged decision -- is the system being used?
- New decision proposed that matches DO_NOT_RESURFACE -- block and explain
- Decision from 6+ months ago with no status update -- mark as stale, prompt review

---

## Output Artifacts

| Request | Deliverable |
|---------|-------------|
| "Show recent decisions" | Last 10 approved decisions with status |
| "What's overdue?" | All overdue action items with owner and days past due |
| "Search decisions about [topic]" | Filtered decision history by topic/tag |
| "Log this decision" | Formatted decision entry with all fields |
| "Check for conflicts" | Conflict scan against all active decisions |
| "Decision summary for board" | Decision velocity, completion rate, open items |
