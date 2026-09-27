# Prompt Patterns Catalog

Read this when designing or structuring a prompt — the complete catalog of production prompting techniques with examples: system-prompt architecture, chain-of-thought, few-shot, output structuring, decomposition, and calibration.

## 1. System Prompt Architecture

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

### Layer Design Principles

| Layer | Principle | Common Mistake |
|-------|-----------|----------------|
| Identity | Be specific about expertise level | "You are an AI assistant" (too generic) |
| Capabilities | Enumerate, don't imply | Assuming model knows available tools |
| Output Format | Show exact schema | Describing format in prose instead of schema |
| Quality Standards | Quantify when possible | "Be thorough" (unquantifiable) |
| Anti-Patterns | State the actual failure mode | "Don't be wrong" (useless) |
| Examples | Show edge cases, not just happy path | Only showing trivial examples |

## 2. Chain-of-Thought (CoT) Patterns

### Standard CoT

On current Claude models, reasoning happens in API-level thinking
(`thinking: {type: "adaptive"}` plus `effort`); read it from thinking blocks rather
than asking for it in the answer. Asking Claude Opus 5.5 to reproduce its
reasoning in the output can trigger a `reasoning_extraction` refusal. Use the
prompt pattern below only on models without native thinking.

```
Work through this in order:
1. First, identify [what needs to be analyzed]
2. Then, evaluate [specific criteria]
3. Finally, synthesize [the conclusion]
```

**When to use:** Complex reasoning, math, multi-step logic
**When NOT to use:** Simple classification, formatting tasks, creative writing

### Structured CoT with Scratchpad (models without native thinking only)

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

**Advantage:** Model can reason messy, output is clean. On Claude models with
thinking, the thinking block already gives you this separation; skip the tags.

### Self-Consistency CoT

```
Solve this problem three different ways, then compare your answers.
If all three agree, that's your answer.
If they disagree, identify which approach is most reliable and explain why.
```

**When to use:** High-stakes decisions where correctness matters more than speed.
**Cost:** 3x token usage. Use selectively.

## 3. Few-Shot Design

### Shot Selection Criteria

| Criterion | Good Example | Bad Example |
|-----------|-------------|-------------|
| Representative | Covers typical input pattern | Only edge cases |
| Diverse | Different input types/lengths | All same structure |
| Edge-covering | Includes tricky cases | Only happy path |
| Output-calibrating | Shows desired detail level | Overly verbose or terse |
| Ordered | Simple → complex progression | Random order |

### Few-Shot Template

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

### Dynamic Few-Shot Selection

For production systems with thousands of examples:

```
1. Embed all examples
2. Embed the current input
3. Find K nearest examples by embedding similarity
4. Include those K examples as shots
5. Typical K: 3-5 (diminishing returns after 5)
```

## 4. Output Structuring Patterns

### JSON Mode with Schema

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

### Structured Reasoning with Sections

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

## 5. Prompt Decomposition

Complex prompts that try to do everything fail. Decompose them.

### Single Responsibility Prompts

| Bad (monolithic) | Good (decomposed) |
|-----------------|-------------------|
| "Review this code for bugs, style, performance, security, and suggest improvements" | Prompt 1: "Identify bugs" / Prompt 2: "Check style" / Prompt 3: "Find performance issues" / Prompt 4: "Security audit" / Prompt 5: "Synthesize findings" |

### Pipeline Pattern

```
Prompt 1 (Extract):    Input → structured data
Prompt 2 (Analyze):    Structured data → findings
Prompt 3 (Synthesize): Findings → recommendation
Prompt 4 (Format):     Recommendation → user-facing output
```

Each prompt is testable independently. A failure in Prompt 2 doesn't require re-running Prompt 1.

## 6. Calibration Techniques

### Temperature Guidelines

| Task Type | Temperature | Rationale |
|-----------|-------------|-----------|
| Code generation | 0.0-0.2 | Correctness > creativity |
| Classification | 0.0 | Deterministic expected |
| Analysis/reasoning | 0.2-0.5 | Some flexibility in framing |
| Creative writing | 0.7-1.0 | Diversity of expression |
| Brainstorming | 0.8-1.2 | Maximum variety |

### Confidence Calibration

```
For each finding, rate your confidence:

Confidence levels:
- VERIFIED: I can point to specific evidence in the provided context
- LIKELY: Strong inference from available information
- UNCERTAIN: Reasonable guess, but limited evidence
- SPECULATIVE: Possible but I'm reaching

Never state SPECULATIVE findings as VERIFIED.
```
