# Sub-Skill: Review Memory Health

**Parent:** self-improving-agent
**Trigger:** "review memory", "memory health check", "clean up MEMORY.md", "prune stale entries"

## Purpose

Audit the memory system for health issues: bloat, stale entries, contradictions, and promotion candidates. This is the maintenance workflow that keeps the self-improvement system effective.

## Workflow

### Step 1: Load Memory Files

Read all memory sources:
- `MEMORY.md` (primary)
- `memory/<topic>.md` files (overflow)
- `.claude/rules/` files (promoted rules)
- `CLAUDE.md` rules section

### Step 2: Classify Each Entry

Use `memory_health_checker.py`:
```bash
python scripts/memory_health_checker.py --memory ./MEMORY.md --rules ./.claude/rules/
```

Classification categories:
| Category | Criteria | Action |
|----------|----------|--------|
| PROMOTE | 3+ recurrences, consistent, impactful | Move to rules |
| CONSOLIDATE | Multiple entries saying the same thing | Merge into one |
| STALE | References deleted files or resolved issues | Delete |
| KEEP | Still relevant, not yet proven enough | Leave in place |
| EXTRACT | Recurring solution worth packaging | Create skill |
| CONTRADICTION | Conflicts with another entry or rule | Resolve |

### Step 3: Check Constraints

- MEMORY.md under 200 lines?
- Any topic files over 100 lines?
- Any rules without a "why" annotation?
- Any rules older than 90 days without re-verification?

### Step 4: Execute Actions

With user confirmation:
1. Promote ready entries (delegate to `promote` sub-skill)
2. Merge duplicate entries
3. Delete stale entries
4. Flag contradictions for resolution
5. Move overflow to topic files

### Step 5: Report

Output health report:
```
Memory Health Report
  Total entries: 47
  PROMOTE:       5 (ready for graduation)
  CONSOLIDATE:   8 (duplicates to merge)
  STALE:         3 (safe to delete)
  KEEP:          29 (healthy)
  CONTRADICTION: 2 (need resolution)
  Line count:    187/200
```

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Memory path | No | Defaults to ./MEMORY.md |
| Rules path | No | Defaults to ./.claude/rules/ |
| Auto-apply | No | Apply non-destructive actions automatically |

## Outputs

- Health classification for every entry
- Constraint violation warnings
- Actionable recommendations (prioritized)
- Post-cleanup statistics
