# Sub-Skill: Remember

**Parent:** self-improving-agent
**Trigger:** "remember this", "capture learning", "log what happened", "save this error"

## Purpose

Capture errors, corrections, and learnings from the current session into the memory system. This is the entry point for the self-improvement loop -- nothing can be improved if it is not first recorded.

## Workflow

### Step 1: Classify the Event

Determine what type of learning to capture:

| Type | Signal | Example |
|------|--------|---------|
| Error resolution | A tool error was fixed | "Bash command failed because path had spaces" |
| User correction | User edited agent output | "User changed import path from relative to absolute" |
| Pattern discovery | A reusable approach worked | "Using `test.beforeEach` eliminated shared state bugs" |
| Anti-pattern | An approach repeatedly fails | "Never use `cy.wait()` -- always use assertions" |
| Preference | User stated a preference | "Use pnpm, not npm" |

### Step 2: Record the Learning

Format the entry using the feedback capture template:

```markdown
## Learning: [Short description]

**Context:** [What task was being performed]
**What happened:** [Outcome description]
**Root cause:** [Why the outcome occurred]
**Correct approach:** [What should have been done]
**Confidence:** [High/Medium/Low]
**Recurrence:** [First time / Seen N times]
**Action:** [KEEP / PROMOTE / EXTRACT]
```

### Step 3: Check for Duplicates

Before adding, search existing memory for related entries:
- If a matching entry exists, increment its recurrence count
- If recurrence crosses the promotion threshold (3+), flag for promotion

### Step 4: Store

Add the entry to the appropriate location:
- MEMORY.md for general learnings
- `memory/<topic>.md` for topic-specific learnings
- Verify MEMORY.md stays under 200 lines

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Description | Yes | What was learned |
| Context | Yes | What task triggered the learning |
| Type | No | Auto-classified from description |

## Outputs

- New memory entry with confidence score
- Duplicate detection result (new vs incremented)
- Promotion flag if recurrence threshold met
