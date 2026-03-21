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

---

## Tool Reference

### 1. decision_tracker.py

Tracks executive decisions with full lifecycle management (Proposed > Approved > Active > Completed/Superseded/Expired). Scans for overdue action items, stale decisions, and generates status summaries.

```bash
python scripts/decision_tracker.py --input decisions.json --json
python scripts/decision_tracker.py --input decisions.json
```

| Flag | Type | Description |
|------|------|-------------|
| `--input` | required | Path to JSON file with decision records (title, status, owner, deadline, action items, tags) |
| `--json` | optional | Output in JSON format instead of human-readable text |

### 2. decision_quality_scorer.py

Scores decision quality across 6 dimensions: framing (problem definition), alternatives (options considered), information (evidence quality), reasoning (logic soundness), commitment (action clarity), and metacognition (awareness of uncertainty). Generates improvement recommendations.

```bash
python scripts/decision_quality_scorer.py --input decision_assessments.json --json
python scripts/decision_quality_scorer.py --input decision_assessments.json
```

| Flag | Type | Description |
|------|------|-------------|
| `--input` | required | Path to JSON file with decision assessments (dimension scores 1-10, optional outcome data) |
| `--json` | optional | Output in JSON format instead of human-readable text |

### 3. decision_tree_builder.py

Builds decision trees with expected value analysis. Calculates optimal paths through probability-weighted outcomes, identifies highest-value decisions, and generates sensitivity analysis on key assumptions.

```bash
python scripts/decision_tree_builder.py --input tree_data.json --json
python scripts/decision_tree_builder.py --input tree_data.json
```

| Flag | Type | Description |
|------|------|-------------|
| `--input` | required | Path to JSON file with decision nodes (options, probabilities, outcomes, values) |
| `--json` | optional | Output in JSON format instead of human-readable text |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Same topic discussed 3+ times without a logged decision | Decision avoidance or no clear decision-making authority | Force a decision at next session; use decision tree builder to clarify options; assign explicit decision owner |
| Action items consistently overdue by same owner | Owner over-committed, lacks capacity, or accountability issue | Review owner workload; redistribute if capacity issue; escalate to founder if accountability issue |
| Decisions made without checking history | Decision log not consulted at session start; no integration habit | Automate decision log loading at board meeting Phase 1; surface relevant past decisions proactively |
| Rejected proposals resurfacing in new language | DO_NOT_RESURFACE not enforced; team members unaware of prior rejection | Enforce conflict detection before logging; block proposals matching rejected items; require explicit "reopen" from founder |
| Decision log growing but never consulted for patterns | Log treated as archive, not strategic tool | Run quarterly decision review; analyze decision velocity, completion rate, and quality trends |
| All decisions owned by one person | Bottleneck or delegation failure | Distribute ownership; use decision quality scorer to assess whether centralization improves or hurts quality |
| Decision quality scores low on "alternatives" dimension | Team anchoring on first option instead of exploring | Require minimum 3 alternatives for decisions above a threshold; use decision tree builder to model options |

---

## Success Criteria

- All board meeting decisions logged in Layer 2 within 24 hours of approval
- Action item completion rate exceeds 80% within stated deadlines
- Zero DO_NOT_RESURFACE violations (rejected proposals do not re-enter decision flow)
- Decision review dates honored for 90%+ of active decisions
- Decision quality score averages above 7/10 across all 6 dimensions
- Conflict detection catches 100% of topic contradictions before new decisions are logged
- Decision log consulted at the start of every board meeting session

---

## Scope & Limitations

**In scope:** Two-layer decision memory architecture, decision entry and lifecycle management (Proposed > Approved > Active > Completed/Superseded/Expired), conflict detection (DO_NOT_RESURFACE, topic contradiction, owner conflict), action item tracking with overdue alerting, decision search and retrieval by topic/owner/date/status, decision quality scoring, and expected value analysis via decision trees.

**Out of scope:** CRM or project management tool integration (tools consume JSON exports), meeting transcription or recording, team-level task management (use project-management/ skills), strategic planning or OKR tracking (use strategic-alignment or ceo-advisor), and automated decision-making. This skill tracks and evaluates decisions; it does not make them.

**Limitations:** Conflict detection uses tag and text matching; semantically similar but differently worded proposals may not be caught. Decision quality scoring is retrospective and depends on honest self-assessment. Decision tree expected value calculations assume probabilities are estimable; highly uncertain environments may make probability assignment misleading. The two-layer architecture requires discipline to maintain; if Layer 2 is not consistently updated, institutional memory degrades.

---

## Integration Points

- **chief-of-staff** -- Manages the logging workflow; single point of control for Layer 2 writes
- **board-meeting** -- Triggers decision logging after Phase 5 approval; decision log loaded at Phase 1
- **strategic-alignment** -- Checks if decisions cascade properly to team goals and OKRs
- **executive-mentor** -- Reviews stale decisions for re-evaluation; coaches on decision quality improvement
- **ceo-advisor** -- Strategic decisions logged and tracked; decision patterns inform leadership coaching
