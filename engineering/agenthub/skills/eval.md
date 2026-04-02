# Sub-Skill: Evaluate Agent Output

**Parent:** agenthub
**Trigger:** "evaluate output", "check agent quality", "grade results"

## Purpose

Evaluate the quality of an agent's output against defined criteria. Quality gates prevent low-quality outputs from propagating to downstream agents.

## Workflow

### Step 1: Define Evaluation Criteria

Each agent can have evaluation criteria in its config:
```json
{
  "eval_criteria": {
    "completeness": "All required output fields populated",
    "accuracy": "Claims supported by evidence",
    "format": "Output matches expected JSON schema",
    "relevance": "Output addresses the assigned task"
  },
  "quality_threshold": 0.7
}
```

### Step 2: Run Evaluation

Score the output on each criterion (0.0 to 1.0):

| Criterion | Check | Score |
|-----------|-------|-------|
| Completeness | All declared outputs present and non-empty | 0.0 - 1.0 |
| Format compliance | Output matches expected schema | Pass/Fail |
| Length adequacy | Output has sufficient depth (not trivially short) | 0.0 - 1.0 |
| Relevance | Output content relates to the task description | 0.0 - 1.0 |
| Consistency | Output does not contradict inputs | 0.0 - 1.0 |

Composite score = weighted average of criteria scores.

### Step 3: Gate Decision

| Composite Score | Decision |
|----------------|----------|
| >= threshold | PASS -- output flows to downstream agents |
| >= threshold - 0.15 | REVISE -- retry with feedback on what to improve |
| < threshold - 0.15 | FAIL -- agent marked as failed |

### Step 4: Revision Feedback (If REVISE)

Generate specific feedback for the agent retry:
- Which criteria scored low
- What was missing or incorrect
- Concrete improvement instructions

### Step 5: Log Evaluation

Record the evaluation result in the session for audit:
- Per-criterion scores
- Composite score
- Decision (PASS/REVISE/FAIL)
- Feedback provided (if any)

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Agent output | Yes | The output to evaluate |
| Eval criteria | Yes | Criteria from agent config |
| Quality threshold | No | Override default threshold |

## Outputs

- Per-criterion scores
- Composite quality score
- Gate decision (PASS / REVISE / FAIL)
- Revision feedback (if applicable)
