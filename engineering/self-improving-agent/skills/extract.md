# Sub-Skill: Extract

**Parent:** self-improving-agent
**Trigger:** "extract patterns", "find reusable patterns", "what did we learn"

## Purpose

Extract reusable patterns from completed work sessions. Analyzes session history to identify approaches that succeeded consistently and packages them as candidate rules or skill components.

## Workflow

### Step 1: Gather Session Data

Collect recent session outcomes:
- Tasks completed and their outcomes (success, partial, failure)
- Corrections made by the user
- Tool usage patterns
- Error resolutions applied

### Step 2: Identify Patterns

Run `pattern_extractor.py` on session logs:
```bash
python scripts/pattern_extractor.py --input session-log.jsonl --min-occurrences 2
```

Pattern categories:
- **Solution patterns:** Same approach solved similar problems multiple times
- **Error patterns:** Same error occurred and was resolved the same way
- **Workflow patterns:** A sequence of steps was effective repeatedly
- **Anti-patterns:** Approaches that consistently failed

### Step 3: Score Patterns

Each pattern gets scored on:
- **Frequency:** How often it appeared (2-3 = low, 4-6 = medium, 7+ = high)
- **Consistency:** Same solution every time vs varied approaches
- **Impact:** Prevented errors (high) vs minor convenience (low)
- **Generalizability:** Works across contexts vs project-specific

### Step 4: Package Candidates

For each high-scoring pattern, create a candidate entry:
```
Pattern: [description]
Evidence: [N occurrences across M sessions]
Score: [frequency * consistency * impact]
Recommendation: KEEP | PROMOTE | EXTRACT_TO_SKILL
```

### Step 5: Present for Review

Output the ranked pattern list for human review. Patterns are candidates, not automatically promoted -- the **promote** sub-skill handles graduation.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Session logs | Yes | JSONL file of session outcomes |
| Min occurrences | No | Minimum pattern frequency (default: 2) |
| Time range | No | Only analyze sessions within N days |

## Outputs

- Ranked list of extracted patterns with scores
- Candidate entries ready for promotion review
- Anti-pattern warnings
