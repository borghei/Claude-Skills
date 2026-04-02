# Self-Improvement Methodology Reference

## The Five Layers of Agent Learning

### Layer 1: Session Memory (Ephemeral)
- Context window contents
- Current conversation state
- Tool call history for this session
- Lost when session ends

### Layer 2: Persistent Memory (MEMORY.md)
- Observations captured across sessions
- Key-value learnings with metadata
- 200-line limit to prevent bloat
- Topic files for overflow

### Layer 3: Enforced Rules (CLAUDE.md / .claude/rules/)
- Promoted patterns that proved reliable
- Loaded every session automatically
- Highest authority after system instructions
- Must have "why" annotation

### Layer 4: Extracted Skills
- Reusable packages graduated from patterns
- Self-contained with scripts and references
- Can be shared across projects

### Layer 5: Meta-Learning
- Strategies for what to capture and when
- Adaptive thresholds based on value delivered
- Self-tuning promotion criteria

## Confidence Scoring Model

```
effective_confidence = base_score * recency_factor * consistency_factor

base_score:
  user-stated:  1.0  (user explicitly told us)
  observed:     0.8  (we saw it work)
  inferred:     0.6  (we deduced from evidence)
  guessed:      0.3  (speculation)

recency_factor:
  0-7 days:     1.0
  7-30 days:    0.9
  30-90 days:   0.7
  90+ days:     0.5

consistency_factor:
  never contradicted:       1.0
  contradicted + reaffirmed: 0.9
  contradicted, unresolved:  0.5
  actively contradicted:     0.0 (delete)
```

## Promotion Decision Tree

```
Entry in MEMORY.md
├── Recurrence >= 3?
│   ├── NO → KEEP (continue monitoring)
│   └── YES
│       ├── Consistent solution every time?
│       │   ├── NO → KEEP (needs more evidence)
│       │   └── YES
│       │       ├── Referenced code/tools still exist?
│       │       │   ├── NO → STALE (delete)
│       │       │   └── YES
│       │       │       ├── Expressible in 1-2 sentences?
│       │       │       │   ├── NO → EXTRACT (make a skill)
│       │       │       │   └── YES → PROMOTE
│       │       │       │       ├── Coding convention → .claude/rules/
│       │       │       │       ├── Architecture rule → CLAUDE.md
│       │       │       │       ├── Tool preference → CLAUDE.md
│       │       │       │       └── Scoped rule → .claude/rules/ with paths:
```

## Memory Curation Checklist

Weekly health check steps:

1. [ ] Read MEMORY.md completely
2. [ ] Check line count (must be < 200)
3. [ ] For each entry, classify: PROMOTE / CONSOLIDATE / STALE / KEEP / EXTRACT
4. [ ] Merge duplicates (CONSOLIDATE)
5. [ ] Delete stale entries (references deleted code, old patterns)
6. [ ] Promote ready entries (recurrence >= 3, consistent, impactful)
7. [ ] Move topic-specific overflow to topic files
8. [ ] Verify all rules in .claude/rules/ still reference existing code
9. [ ] Log the health check outcome

## Anti-Patterns in Self-Improvement

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| Memory hoarding | MEMORY.md > 200 lines, never pruned | Schedule weekly curation |
| Premature promotion | Rules promoted after 1 occurrence | Enforce 3+ recurrence minimum |
| Cargo cult rules | Rules copied without understanding why | Require "why" annotation on every rule |
| Stale rule accumulation | Rules reference deleted code/tools | Timestamp rules, verify periodically |
| Contradiction spiral | New rules conflict with existing ones | Belief revision protocol: compare confidence, resolve |
| Observation bias | Only capturing failures, not successes | Track both; success patterns inform approach selection |
| Over-promotion | Everything becomes a rule | Cap at 15-25% promotion rate; most entries should KEEP |

## Metrics and Thresholds

| Metric | Healthy Range | Action if Out of Range |
|--------|--------------|----------------------|
| MEMORY.md line count | 50-200 | Prune if over; if under 50, capture more |
| Promotion rate (30d) | 15-25% | Adjust capture strategy or promotion criteria |
| Stale entry ratio | < 10% | Run curation immediately |
| Rule count | 10-50 | Consolidate if over 50; add more if under 10 |
| First-attempt success | > 70% | Investigate regressions, check rule quality |
| Contradiction count | 0 | Resolve immediately via belief revision |
