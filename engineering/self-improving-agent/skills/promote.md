# Sub-Skill: Promote

**Parent:** self-improving-agent
**Trigger:** "promote pattern to rule", "graduate to CLAUDE.md", "make this permanent"

## Purpose

Graduate proven patterns from memory (MEMORY.md) to enforced rules (CLAUDE.md or `.claude/rules/`). This is the critical step that turns observations into permanent behavior changes.

## Workflow

### Step 1: Check Promotion Criteria

A pattern is ready for promotion when ALL of these are met:

| Criterion | Threshold | Verification |
|-----------|-----------|--------------|
| Recurrence | 3+ sessions | Check recurrence count in memory |
| Consistency | Same solution every time | No contradicting entries exist |
| Impact | Prevented errors or saved time | At least one error prevented |
| Stability | Underlying system unchanged | Referenced code/tools still exist |
| Clarity | Statable in 1-2 sentences | Can be expressed as a clear rule |

### Step 2: Determine Target

| Pattern Type | Promote To | Format |
|-------------|-----------|--------|
| Coding convention | `.claude/rules/<area>.md` | Rule with scope path |
| Project architecture | `CLAUDE.md` | Architecture section entry |
| Tool preference | `CLAUDE.md` | Development environment section |
| Debugging pattern | `.claude/rules/debugging.md` | Conditional rule |
| File-scoped rule | `.claude/rules/<scope>.md` with `paths:` | Scoped rule |

### Step 3: Draft the Rule

Format as a clear, enforceable statement:
- Start with an action verb (Use, Always, Never, Prefer)
- Include the "why" as a brief annotation
- Scope to specific files/directories if applicable

Example:
```
Always use `type` not `interface` for object shapes.
Reason: Consistent with codebase convention; types are more flexible for unions.
```

### Step 4: Apply Promotion

Use `rule_promoter.py` to validate and apply:
```bash
python scripts/rule_promoter.py --memory-entry <id> --target claude-md --dry-run
python scripts/rule_promoter.py --memory-entry <id> --target claude-md --apply
```

### Step 5: Clean Up Memory

After promotion:
- Remove the original entry from MEMORY.md
- Add a reference note: "Promoted to CLAUDE.md on [date]"
- Verify MEMORY.md line count is within limits

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Memory entry ID | Yes | The pattern/entry to promote |
| Target | Yes | CLAUDE.md or .claude/rules/<name>.md |
| Dry run | No | Preview without applying (default: true) |

## Outputs

- Promotion validation result (pass/fail with reasons)
- Draft rule text
- Applied changes (if not dry run)
- Updated memory with entry removed
