---
name: prompt-engineer-toolkit
description: >
  Production prompt engineering frameworks for building, testing, versioning,
  and evaluating prompts. Covers chain-of-thought, few-shot design, system
  prompt architecture, prompt regression testing, and evaluation rubrics. Use
  when designing prompts for production systems, running A/B tests on prompts,
  building prompt libraries, or debugging prompt quality degradation.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-engineering
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: prompt-patterns, evaluation-rubrics, regression-testing, version-control
---
# Prompt Engineer Toolkit - Production Prompt Engineering

**Tier:** POWERFUL
**Category:** Engineering
**Tags:** prompt engineering, chain-of-thought, few-shot, evaluation, testing, prompt versioning

## Overview

Prompt Engineer Toolkit provides the complete lifecycle for production prompts: design patterns that work, testing frameworks that catch regressions, versioning systems that track changes, and evaluation rubrics that replace subjective "looks good" with measurable quality. This is not about clever tricks -- it is about treating prompts as production code with the same rigor.

## Core Prompt Patterns

### 1. System Prompt Architecture

Every production prompt has a layered structure. Order matters.

```
┌──────────────────────────────────────┐
│  Layer 1: Identity & Role            │  Who the model is
│  "You are a senior code reviewer..." │
├──────────────────────────────────────┤
│  Layer 2: Capabilities & Constraints │  What it can and cannot do
│  "You can read files, run tests..."  │
├──────────────────────────────────────┤
│  Layer 3: Output Format              │  How to structure responses
│  "Always respond with JSON..."       │
├──────────────────────────────────────┤
│  Layer 4: Quality Standards          │  What good output looks like
│  "Include edge cases, cite sources"  │
├──────────────────────────────────────┤
│  Layer 5: Anti-Patterns              │  What to avoid
│  "Never fabricate citations..."      │
├──────────────────────────────────────┤
│  Layer 6: Examples                   │  Calibration via demonstration
│  "Here is an example..."            │
└──────────────────────────────────────┘
```

#### Layer Design Principles

| Layer | Principle | Common Mistake |
|-------|-----------|----------------|
| Identity | Be specific about expertise level | "You are an AI assistant" (too generic) |
| Capabilities | Enumerate, don't imply | Assuming model knows available tools |
| Output Format | Show exact schema | Describing format in prose instead of schema |
| Quality Standards | Quantify when possible | "Be thorough" (unquantifiable) |
| Anti-Patterns | State the actual failure mode | "Don't be wrong" (useless) |
| Examples | Show edge cases, not just happy path | Only showing trivial examples |

### 2. Chain-of-Thought (CoT) Patterns

#### Standard CoT

```
Think through this step by step:
1. First, identify [what needs to be analyzed]
2. Then, evaluate [specific criteria]
3. Finally, synthesize [the conclusion]

Show your reasoning for each step.
```

**When to use:** Complex reasoning, math, multi-step logic
**When NOT to use:** Simple classification, formatting tasks, creative writing

#### Structured CoT with Scratchpad

```
Use the following reasoning process:

<scratchpad>
- List relevant facts
- Identify applicable rules
- Work through the logic
- Check for edge cases
</scratchpad>

Then provide your final answer outside the scratchpad tags.
```

**Advantage:** Model can reason messy, output is clean.

#### Self-Consistency CoT

```
Solve this problem three different ways, then compare your answers.
If all three agree, that's your answer.
If they disagree, identify which approach is most reliable and explain why.
```

**When to use:** High-stakes decisions where correctness matters more than speed.
**Cost:** 3x token usage. Use selectively.

### 3. Few-Shot Design

#### Shot Selection Criteria

| Criterion | Good Example | Bad Example |
|-----------|-------------|-------------|
| Representative | Covers typical input pattern | Only edge cases |
| Diverse | Different input types/lengths | All same structure |
| Edge-covering | Includes tricky cases | Only happy path |
| Output-calibrating | Shows desired detail level | Overly verbose or terse |
| Ordered | Simple → complex progression | Random order |

#### Few-Shot Template

```
Here are examples of the expected input and output:

Example 1 (simple case):
Input: [simple input]
Output: [simple output with annotation]

Example 2 (typical case):
Input: [typical input]
Output: [typical output with annotation]

Example 3 (edge case):
Input: [tricky input]
Output: [correct handling with annotation]

Now process this:
Input: {user_input}
Output:
```

#### Dynamic Few-Shot Selection

For production systems with thousands of examples:

```
1. Embed all examples
2. Embed the current input
3. Find K nearest examples by embedding similarity
4. Include those K examples as shots
5. Typical K: 3-5 (diminishing returns after 5)
```

### 4. Output Structuring Patterns

#### JSON Mode with Schema

```
Respond with a JSON object matching this exact schema:

{
  "analysis": {
    "summary": "string - one sentence summary",
    "severity": "string - one of: critical, high, medium, low",
    "findings": [
      {
        "issue": "string - description of the issue",
        "location": "string - file:line",
        "fix": "string - recommended fix",
        "confidence": "number - 0.0 to 1.0"
      }
    ],
    "overall_score": "number - 0 to 100"
  }
}

Rules:
- findings array must have at least one entry
- confidence must reflect actual certainty, not optimism
- overall_score: 90-100 (excellent), 70-89 (good), 50-69 (needs work), <50 (poor)
```

#### Structured Reasoning with Sections

```
Structure your response with these exact sections:

## Assessment
[1-2 sentence bottom line]

## Evidence
[Specific observations supporting the assessment]

## Risks
[What could go wrong, with likelihood estimates]

## Recommendation
[Specific actionable next steps with owners]
```

### 5. Prompt Decomposition

Complex prompts that try to do everything fail. Decompose them.

#### Single Responsibility Prompts

| Bad (monolithic) | Good (decomposed) |
|-----------------|-------------------|
| "Review this code for bugs, style, performance, security, and suggest improvements" | Prompt 1: "Identify bugs" / Prompt 2: "Check style" / Prompt 3: "Find performance issues" / Prompt 4: "Security audit" / Prompt 5: "Synthesize findings" |

#### Pipeline Pattern

```
Prompt 1 (Extract):    Input → structured data
Prompt 2 (Analyze):    Structured data → findings
Prompt 3 (Synthesize): Findings → recommendation
Prompt 4 (Format):     Recommendation → user-facing output
```

Each prompt is testable independently. A failure in Prompt 2 doesn't require re-running Prompt 1.

### 6. Calibration Techniques

#### Temperature Guidelines

| Task Type | Temperature | Rationale |
|-----------|-------------|-----------|
| Code generation | 0.0-0.2 | Correctness > creativity |
| Classification | 0.0 | Deterministic expected |
| Analysis/reasoning | 0.2-0.5 | Some flexibility in framing |
| Creative writing | 0.7-1.0 | Diversity of expression |
| Brainstorming | 0.8-1.2 | Maximum variety |

#### Confidence Calibration

```
For each finding, rate your confidence:

Confidence levels:
- VERIFIED: I can point to specific evidence in the provided context
- LIKELY: Strong inference from available information
- UNCERTAIN: Reasonable guess, but limited evidence
- SPECULATIVE: Possible but I'm reaching

Never state SPECULATIVE findings as VERIFIED.
```

## Prompt Testing Framework

### Test Case Design

Every production prompt needs a test suite.

#### Test Case Structure

```json
{
  "test_id": "classify-urgent-001",
  "input": "Server is down, customers can't access the product",
  "expected": {
    "contains": ["critical", "immediate"],
    "not_contains": ["low priority", "can wait"],
    "format_regex": "^\\{.*\\}$",
    "max_tokens": 500,
    "required_fields": ["severity", "category"]
  },
  "tags": ["classification", "urgency", "happy-path"]
}
```

#### Test Suite Composition

| Category | % of Suite | Purpose |
|----------|-----------|---------|
| Happy path | 40% | Confirm basic functionality works |
| Edge cases | 30% | Boundary conditions, unusual inputs |
| Adversarial | 15% | Inputs designed to break the prompt |
| Regression | 15% | Cases that previously failed |

### Evaluation Rubric

#### Automated Scoring

| Dimension | Measurement | Weight |
|-----------|-------------|--------|
| Adherence | Contains required elements, matches schema | 30% |
| Accuracy | Correct classification/analysis/answer | 30% |
| Safety | No forbidden content, no hallucinations | 20% |
| Format | Matches expected structure, length bounds | 10% |
| Relevance | Response addresses the actual input | 10% |

#### Scoring Formula

```
score = (adherence * 0.30) + (accuracy * 0.30) + (safety * 0.20) + (format * 0.10) + (relevance * 0.10)

Pass threshold: 0.80
Warning threshold: 0.70
Fail threshold: < 0.70
```

### Regression Testing Protocol

```
1. Before any prompt change:
   - Run full test suite against current prompt (baseline)
   - Record scores per test case

2. After prompt change:
   - Run same test suite against new prompt (candidate)
   - Compare scores per test case

3. Acceptance criteria:
   - Average score: candidate >= baseline
   - No individual test case drops by more than 10%
   - Zero safety violations (any safety failure = reject)
   - If criteria met: promote candidate
   - If criteria not met: iterate on prompt or reject
```

## Prompt Versioning

### Version Control Strategy

```
prompts/
├── support-classifier/
│   ├── v1.txt                 # Original version
│   ├── v2.txt                 # Added edge case handling
│   ├── v3.txt                 # Current production
│   ├── changelog.md           # Change log with rationale
│   └── tests/
│       ├── suite.json         # Test cases
│       └── baselines/
│           ├── v1-results.json
│           ├── v2-results.json
│           └── v3-results.json
├── code-reviewer/
│   ├── v1.txt
│   └── ...
```

### Changelog Format

```markdown
## v3 (2026-03-09)
**Author:** borghei
**Change:** Added explicit handling for multi-language inputs
**Reason:** v2 defaulted to English analysis for non-English code comments
**Test results:** Average score 0.87 (v2 was 0.82). No regressions.
**Rollback plan:** Revert to v2.txt

## v2 (2026-02-15)
**Author:** borghei
**Change:** Added structured output format with JSON schema
**Reason:** Downstream parser needed consistent format
**Test results:** Average score 0.82 (v1 was 0.79). Format compliance 100% (v1 was 73%).
```

### Prompt Diff Analysis

Before deploying a new version, always diff:

```
Key questions for prompt diffs:
1. Were any constraints removed? (Risk: safety regression)
2. Were any examples changed? (Risk: calibration shift)
3. Was the output format changed? (Risk: downstream parser breaks)
4. Were any anti-patterns removed? (Risk: known failure modes return)
5. Is the new prompt longer? (Risk: context budget impact)
```

## Common Prompt Failure Modes

| Failure Mode | Symptom | Fix |
|-------------|---------|-----|
| Instruction override | Model ignores constraints | Move constraints earlier, add "CRITICAL:" prefix |
| Format drift | Output structure varies between calls | Add JSON schema, reduce temperature |
| Sycophancy | Model agrees with wrong premise | Add "Challenge assumptions" instruction |
| Verbosity bloat | Output too long, buries the answer | Add word/token limits, "be concise" |
| Hallucination | Fabricated facts, citations, or code | Add "Only reference provided context" |
| Anchoring | First example dominates output style | Diversify examples, add "each input is independent" |
| Lost in the middle | Middle instructions get ignored | Front-load and back-load critical instructions |

## Workflows

### Workflow 1: Design a Production Prompt

```
1. Define the task precisely (input type, output type, quality criteria)
2. Write the system prompt using the 6-layer architecture
3. Create 10+ test cases (40% happy, 30% edge, 15% adversarial, 15% regression)
4. Run test suite, score results
5. Iterate until passing threshold (0.80+)
6. Version as v1, record baseline scores
7. Deploy with monitoring
```

### Workflow 2: Debug a Degraded Prompt

```
1. Identify which test cases are failing
2. Categorize failures (format? accuracy? safety? relevance?)
3. Check: did the model change? (API version, model update)
4. Check: did the input distribution change? (new edge cases)
5. Check: was the prompt modified? (diff against last known good)
6. Fix the root cause (not the symptom)
7. Run full regression suite before deploying fix
```

### Workflow 3: Migrate Prompt to New Model

```
1. Run full test suite on current model (baseline)
2. Run same suite on new model (no prompt changes)
3. Compare: if scores are equivalent, done
4. If scores drop: identify which dimensions degraded
5. Adjust prompt for new model's behavior patterns
6. Re-run suite until scores meet or exceed baseline
7. Document model-specific adjustments in changelog
```

## Integration Points

| Skill | Integration |
|-------|-------------|
| **self-improving-agent** | Prompts that degrade are a regression signal; test them |
| **agent-designer** | Agent system prompts are the highest-stakes prompts to test |
| **context-engine** | Context retrieval quality directly affects prompt effectiveness |
| **ab-test-setup** | A/B test prompt variants in production with statistical rigor |

## References

- `references/prompt-patterns-catalog.md` - Complete catalog of prompting techniques with examples
- `references/evaluation-rubric-templates.md` - Reusable evaluation rubrics by task type
- `references/model-specific-behaviors.md` - Known behavior differences across model families

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Model ignores critical instructions | Instructions buried in the middle of a long prompt | Front-load and back-load critical constraints; use "CRITICAL:" or "IMPORTANT:" prefixes to increase salience |
| Output format randomly breaks | Temperature too high or format spec is ambiguous | Set temperature to 0.0-0.2 for structured output; provide an exact JSON schema rather than prose descriptions |
| Few-shot examples cause repetitive output | Examples are too similar, anchoring the model on a single pattern | Diversify examples across input types, lengths, and complexity levels; add "each input is independent" instruction |
| Prompt works on one model but fails on another | Model-specific instruction-following differences | Run full test suite on the target model; adjust layer ordering and verbosity per `references/model-specific-behaviors.md` |
| Test scores drop after a minor prompt edit | Removed a constraint or anti-pattern that was load-bearing | Always diff before deploying; check if constraints, examples, or anti-patterns were removed; use the Prompt Diff Analysis checklist |
| Confidence scores cluster at extremes (all 0.9+ or all 0.1) | Calibration instructions missing or poorly defined | Add explicit confidence-level definitions (VERIFIED / LIKELY / UNCERTAIN / SPECULATIVE) with concrete criteria for each level |
| Prompt exceeds context window budget | Accumulated examples and instructions over multiple iterations | Audit token usage per layer; trim redundant examples; switch to dynamic few-shot selection to include only the most relevant shots |

## Success Criteria

- **Test suite pass rate >= 80%** across all prompt versions before production deployment, with zero safety-dimension failures.
- **Format compliance >= 95%** on structured output prompts, measured by schema validation against the declared JSON schema.
- **Regression delta <= 5%** on average score when migrating prompts between model versions, with no individual test case dropping by more than 10%.
- **Prompt version turnaround < 48 hours** from identifying a quality degradation to deploying a tested fix with full regression results recorded.
- **Few-shot example coverage >= 3 diversity categories** (simple, typical, edge) in every production prompt, validated during prompt review.
- **Changelog completeness: 100%** of prompt version changes documented with author, rationale, test results, and rollback plan.
- **Downstream parser breakage rate: 0** after any prompt format change, verified by integration tests against consuming systems.

## Scope & Limitations

**This skill covers:**
- Designing, structuring, and layering system prompts for production AI applications
- Building and running test suites, evaluation rubrics, and regression tests for prompt quality
- Versioning prompts with changelogs, baselines, and rollback plans
- Calibration techniques including temperature tuning, confidence levels, and few-shot selection

**This skill does NOT cover:**
- Fine-tuning or training models -- see `engineering/model-training-pipeline` for training workflows
- Retrieval-augmented generation (RAG) pipeline design -- see `engineering/context-engine` for context retrieval architecture
- Agent orchestration and multi-step tool use -- see `engineering/agent-designer` for agent system design
- LLM infrastructure, hosting, or cost optimization -- see `engineering/llm-gateway-design` for inference infrastructure patterns

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **agent-designer** | Agent system prompts are the highest-stakes prompts; use this toolkit to test and version them | Agent specs → prompt layers → tested system prompts |
| **self-improving-agent** | Prompt degradation signals feed into self-improvement loops for automatic correction | Test suite results → regression alerts → prompt iteration |
| **context-engine** | Retrieved context quality directly impacts prompt effectiveness; coordinate retrieval tuning with prompt testing | Retrieved chunks → prompt context layer → evaluation scores |
| **ab-test-setup** | A/B test prompt variants in production with statistical rigor before full rollout | Prompt candidates → traffic split → scoring comparison → winner promotion |
| **llm-gateway-design** | Gateway handles prompt routing, versioning, and model fallback at the infrastructure layer | Versioned prompts → gateway config → model routing → response logging |
| **code-review-automation** | Code review prompts are high-frequency production prompts that benefit from this toolkit's testing framework | Review criteria → prompt design → test suite → deployed reviewer prompt |
