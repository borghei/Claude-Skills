---
name: senior-prompt-engineer
description: >
  This skill should be used when the user asks to "optimize prompts", "design
  prompt templates", "evaluate LLM outputs", "build agentic systems", "implement
  RAG", "create few-shot examples", "analyze token usage", or "design AI
  workflows". Use for prompt engineering patterns, LLM evaluation frameworks,
  agent architectures, and structured output design.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: prompt-engineering
  updated: 2026-03-31
  tags: [prompt-optimization, llm-evaluation, agents, prompt-engineering]
---
# Senior Prompt Engineer

Prompt engineering patterns, LLM evaluation frameworks, and agentic system design.

## Table of Contents

- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
  - [Prompt Optimizer](#1-prompt-optimizer)
  - [RAG Evaluator](#2-rag-evaluator)
  - [Agent Orchestrator](#3-agent-orchestrator)
- [Prompt Engineering Workflows](#prompt-engineering-workflows)
  - [Prompt Optimization Workflow](#prompt-optimization-workflow)
  - [Few-Shot Example Design](#few-shot-example-design-workflow)
  - [Structured Output Design](#structured-output-design-workflow)
- [Reference Documentation](#reference-documentation)
- [Common Patterns Quick Reference](#common-patterns-quick-reference)

---

## Quick Start

```bash
# Analyze and optimize a prompt file
python scripts/prompt_optimizer.py prompts/my_prompt.txt --analyze

# Evaluate RAG retrieval quality
python scripts/rag_evaluator.py --contexts contexts.json --questions questions.json

# Visualize agent workflow from definition
python scripts/agent_orchestrator.py agent_config.yaml --visualize
```

---

## Tools Overview

### 1. Prompt Optimizer

Analyzes prompts for token efficiency, clarity, and structure. Generates optimized versions.

**Input:** Prompt text file or string
**Output:** Analysis report with optimization suggestions

**Usage:**
```bash
# Analyze a prompt file
python scripts/prompt_optimizer.py prompt.txt --analyze

# Output:
# Token count: 847
# Estimated cost: $0.0025 (GPT-4)
# Clarity score: 72/100
# Issues found:
#   - Ambiguous instruction at line 3
#   - Missing output format specification
#   - Redundant context (lines 12-15 repeat lines 5-8)
# Suggestions:
#   1. Add explicit output format: "Respond in JSON with keys: ..."
#   2. Remove redundant context to save 89 tokens
#   3. Clarify "analyze" -> "list the top 3 issues with severity ratings"

# Generate optimized version
python scripts/prompt_optimizer.py prompt.txt --optimize --output optimized.txt

# Count tokens for cost estimation
python scripts/prompt_optimizer.py prompt.txt --tokens --model gpt-4

# Extract and manage few-shot examples
python scripts/prompt_optimizer.py prompt.txt --extract-examples --output examples.json
```

---

### 2. RAG Evaluator

Evaluates Retrieval-Augmented Generation quality by measuring context relevance and answer faithfulness.

**Input:** Retrieved contexts (JSON) and questions/answers
**Output:** Evaluation metrics and quality report

**Usage:**
```bash
# Evaluate retrieval quality
python scripts/rag_evaluator.py --contexts retrieved.json --questions eval_set.json

# Output:
# === RAG Evaluation Report ===
# Questions evaluated: 50
#
# Retrieval Metrics:
#   Context Relevance: 0.78 (target: >0.80)
#   Retrieval Precision@5: 0.72
#   Coverage: 0.85
#
# Generation Metrics:
#   Answer Faithfulness: 0.91
#   Groundedness: 0.88
#
# Issues Found:
#   - 8 questions had no relevant context in top-5
#   - 3 answers contained information not in context
#
# Recommendations:
#   1. Improve chunking strategy for technical documents
#   2. Add metadata filtering for date-sensitive queries

# Evaluate with custom metrics
python scripts/rag_evaluator.py --contexts retrieved.json --questions eval_set.json \
    --metrics relevance,faithfulness,coverage

# Export detailed results
python scripts/rag_evaluator.py --contexts retrieved.json --questions eval_set.json \
    --output report.json --verbose
```

---

### 3. Agent Orchestrator

Parses agent definitions and visualizes execution flows. Validates tool configurations.

**Input:** Agent configuration (YAML/JSON)
**Output:** Workflow visualization, validation report

**Usage:**
```bash
# Validate agent configuration
python scripts/agent_orchestrator.py agent.yaml --validate

# Output:
# === Agent Validation Report ===
# Agent: research_assistant
# Pattern: ReAct
#
# Tools (4 registered):
#   [OK] web_search - API key configured
#   [OK] calculator - No config needed
#   [WARN] file_reader - Missing allowed_paths
#   [OK] summarizer - Prompt template valid
#
# Flow Analysis:
#   Max depth: 5 iterations
#   Estimated tokens/run: 2,400-4,800
#   Potential infinite loop: No
#
# Recommendations:
#   1. Add allowed_paths to file_reader for security
#   2. Consider adding early exit condition for simple queries

# Visualize agent workflow (ASCII)
python scripts/agent_orchestrator.py agent.yaml --visualize

# Output:
# ┌─────────────────────────────────────────┐
# │            research_assistant           │
# │              (ReAct Pattern)            │
# └─────────────────┬───────────────────────┘
#                   │
#          ┌────────▼────────┐
#          │   User Query    │
#          └────────┬────────┘
#                   │
#          ┌────────▼────────┐
#          │     Think       │◄──────┐
#          └────────┬────────┘       │
#                   │                │
#          ┌────────▼────────┐       │
#          │   Select Tool   │       │
#          └────────┬────────┘       │
#                   │                │
#     ┌─────────────┼─────────────┐  │
#     ▼             ▼             ▼  │
# [web_search] [calculator] [file_reader]
#     │             │             │  │
#     └─────────────┼─────────────┘  │
#                   │                │
#          ┌────────▼────────┐       │
#          │    Observe      │───────┘
#          └────────┬────────┘
#                   │
#          ┌────────▼────────┐
#          │  Final Answer   │
#          └─────────────────┘

# Export workflow as Mermaid diagram
python scripts/agent_orchestrator.py agent.yaml --visualize --format mermaid
```

---

## Prompt Engineering Workflows

### Prompt Optimization Workflow

Use when improving an existing prompt's performance or reducing token costs.

**Step 1: Baseline current prompt**
```bash
python scripts/prompt_optimizer.py current_prompt.txt --analyze --output baseline.json
```

**Step 2: Identify issues**
Review the analysis report for:
- Token waste (redundant instructions, verbose examples)
- Ambiguous instructions (unclear output format, vague verbs)
- Missing constraints (no length limits, no format specification)

**Step 3: Apply optimization patterns**
| Issue | Pattern to Apply |
|-------|------------------|
| Ambiguous output | Add explicit format specification |
| Too verbose | Extract to few-shot examples |
| Inconsistent results | Add role/persona framing |
| Missing edge cases | Add constraint boundaries |

**Step 4: Generate optimized version**
```bash
python scripts/prompt_optimizer.py current_prompt.txt --optimize --output optimized.txt
```

**Step 5: Compare results**
```bash
python scripts/prompt_optimizer.py optimized.txt --analyze --compare baseline.json
# Shows: token reduction, clarity improvement, issues resolved
```

**Step 6: Validate with test cases**
Run both prompts against your evaluation set and compare outputs.

---

### Few-Shot Example Design Workflow

Use when creating examples for in-context learning.

**Step 1: Define the task clearly**
```
Task: Extract product entities from customer reviews
Input: Review text
Output: JSON with {product_name, sentiment, features_mentioned}
```

**Step 2: Select diverse examples (3-5 recommended)**
| Example Type | Purpose |
|--------------|---------|
| Simple case | Shows basic pattern |
| Edge case | Handles ambiguity |
| Complex case | Multiple entities |
| Negative case | What NOT to extract |

**Step 3: Format consistently**
```
Example 1:
Input: "Love my new iPhone 15, the camera is amazing!"
Output: {"product_name": "iPhone 15", "sentiment": "positive", "features_mentioned": ["camera"]}

Example 2:
Input: "The laptop was okay but battery life is terrible."
Output: {"product_name": "laptop", "sentiment": "mixed", "features_mentioned": ["battery life"]}
```

**Step 4: Validate example quality**
```bash
python scripts/prompt_optimizer.py prompt_with_examples.txt --validate-examples
# Checks: consistency, coverage, format alignment
```

**Step 5: Test with held-out cases**
Ensure model generalizes beyond your examples.

---

### Structured Output Design Workflow

Use when you need reliable JSON/XML/structured responses.

**Step 1: Define schema**
```json
{
  "type": "object",
  "properties": {
    "summary": {"type": "string", "maxLength": 200},
    "sentiment": {"enum": ["positive", "negative", "neutral"]},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
  },
  "required": ["summary", "sentiment"]
}
```

**Step 2: Include schema in prompt**
```
Respond with JSON matching this schema:
- summary (string, max 200 chars): Brief summary of the content
- sentiment (enum): One of "positive", "negative", "neutral"
- confidence (number 0-1): Your confidence in the sentiment
```

**Step 3: Add format enforcement**
```
IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation.
Start your response with { and end with }
```

**Step 4: Validate outputs**
```bash
python scripts/prompt_optimizer.py structured_prompt.txt --validate-schema schema.json
```

---

## Reference Documentation

| File | Contains | Load when user asks about |
|------|----------|---------------------------|
| `references/prompt_engineering_patterns.md` | 10 prompt patterns with input/output examples | "which pattern?", "few-shot", "chain-of-thought", "role prompting" |
| `references/llm_evaluation_frameworks.md` | Evaluation metrics, scoring methods, A/B testing | "how to evaluate?", "measure quality", "compare prompts" |
| `references/agentic_system_design.md` | Agent architectures (ReAct, Plan-Execute, Tool Use) | "build agent", "tool calling", "multi-agent" |

---

## Common Patterns Quick Reference

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Zero-shot** | Simple, well-defined tasks | "Classify this email as spam or not spam" |
| **Few-shot** | Complex tasks, consistent format needed | Provide 3-5 examples before the task |
| **Chain-of-Thought** | Reasoning, math, multi-step logic | "Think step by step..." |
| **Role Prompting** | Expertise needed, specific perspective | "You are an expert tax accountant..." |
| **Structured Output** | Need parseable JSON/XML | Include schema + format enforcement |

---

## Common Commands

```bash
# Prompt Analysis
python scripts/prompt_optimizer.py prompt.txt --analyze          # Full analysis
python scripts/prompt_optimizer.py prompt.txt --tokens           # Token count only
python scripts/prompt_optimizer.py prompt.txt --optimize         # Generate optimized version

# RAG Evaluation
python scripts/rag_evaluator.py --contexts ctx.json --questions q.json  # Evaluate
python scripts/rag_evaluator.py --contexts ctx.json --compare baseline  # Compare to baseline

# Agent Development
python scripts/agent_orchestrator.py agent.yaml --validate       # Validate config
python scripts/agent_orchestrator.py agent.yaml --visualize      # Show workflow
python scripts/agent_orchestrator.py agent.yaml --estimate-cost  # Token estimation
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Token count seems inaccurate | Character-based estimation varies by language and special characters | Use `--model` flag matching your target model; Claude uses a 3.5 char/token ratio vs 4.0 for GPT models |
| Clarity score is low despite clear prompt | Vague-pattern detector flags common words like "analyze" or "some" even in valid contexts | Review flagged lines individually; not every match is a true issue --- focus on genuinely ambiguous instructions |
| Few-shot examples not detected | Examples do not follow the `Input:/Output:` or `Example N:` labeling convention | Format examples with explicit `Input:` and `Output:` prefixes so the extractor can parse them |
| RAG evaluator shows 0.0 for all metrics | Input JSON schema mismatch --- missing `question`, `content`, or `question_id` keys | Verify JSON uses the expected keys (`question`/`query`, `content`/`text`, `question_id`/`query_id`) |
| Agent YAML parsing fails | Built-in YAML parser is simplified and cannot handle advanced syntax (anchors, multi-line blocks) | Convert config to JSON, or restructure YAML to use only simple key-value pairs and dash-prefixed lists |
| Optimization produces minimal changes | `--optimize` only performs whitespace normalization, not semantic rewriting | Use `--analyze` first to get suggestions, then manually apply structural improvements before re-running `--optimize` |
| Mermaid diagram renders incorrectly | More than 6 tools overflow the generated subgraph | Reduce tool count in the config or manually edit the Mermaid output to split into sub-diagrams |

---

## Success Criteria

- **Prompt clarity score above 70/100** on all production prompts, measured via `prompt_optimizer.py --analyze`
- **Token efficiency improved by 30%+** after applying optimization suggestions and removing redundant content
- **RAG context relevance at or above 0.80** across evaluation sets, verified by `rag_evaluator.py`
- **Answer faithfulness at or above 0.95** with zero unsupported claims in critical workflows
- **Agent validation passes with zero errors** for all deployed agent configurations
- **Cost per agent run within budget** --- estimated monthly spend confirmed via `agent_orchestrator.py --estimate-cost`
- **Few-shot example coverage includes edge cases** --- at least 1 simple, 1 complex, and 1 negative example per prompt template

---

## Scope & Limitations

**This skill covers:**
- Static prompt analysis: token counting, clarity scoring, structure detection, and optimization suggestions
- RAG evaluation: context relevance, answer faithfulness, groundedness, and retrieval metrics (Precision@K, ROUGE-L, MRR, NDCG)
- Agent workflow design: configuration validation, ASCII/Mermaid visualization, and token cost estimation
- Few-shot example extraction and management from existing prompts

**This skill does NOT cover:**
- Live LLM calls or runtime prompt testing --- all analysis is static/deterministic (see `senior-ml-engineer` for LLM integration)
- Vector database setup or embedding generation --- RAG evaluator scores pre-retrieved contexts only (see `senior-data-engineer` for pipeline orchestration)
- Fine-tuning, RLHF, or model training workflows (see `senior-ml-engineer` for model deployment)
- Production monitoring, A/B test execution, or real-time drift detection (see `senior-data-scientist` for experiment design)

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-ml-engineer` | LLM integration and model deployment | Optimized prompts from this skill feed into `llm_integration_builder.py` prompt templates |
| `senior-data-scientist` | A/B test design for prompt experiments | `experiment_designer.py` defines test parameters; this skill provides the prompt variants to compare |
| `senior-data-engineer` | RAG pipeline orchestration | `pipeline_orchestrator.py` builds the retrieval pipeline; this skill evaluates its output quality |
| `senior-fullstack` | End-to-end application scaffolding | Fullstack apps consume agent configs validated by `agent_orchestrator.py` |
| `senior-security` | Prompt injection and adversarial input review | Security analysis covers the attack surface; this skill ensures prompts include defensive constraints |
| `senior-qa` | Quality assurance for AI-powered features | QA test suites validate that optimized prompts produce consistent outputs in production |

---

## Tool Reference

### prompt_optimizer.py

**Purpose:** Static analysis tool for prompt engineering. Estimates token counts, scores clarity and structure, detects ambiguous instructions and redundant content, extracts few-shot examples, and generates optimized prompt versions.

**Usage:**
```bash
python scripts/prompt_optimizer.py <prompt_file> [options]
```

**Parameters:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `prompt` | _(positional)_ | string | _(required)_ | Path to the prompt text file to analyze |
| `--analyze` | `-a` | flag | off | Run full analysis (clarity, structure, issues, suggestions) |
| `--tokens` | `-t` | flag | off | Count tokens and estimate cost only |
| `--optimize` | `-O` | flag | off | Generate whitespace-optimized version of the prompt |
| `--extract-examples` | `-e` | flag | off | Extract few-shot examples (Input/Output pairs) as JSON |
| `--model` | `-m` | choice | `gpt-4` | Model for token/cost estimation. Choices: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`, `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku` |
| `--output` | `-o` | string | _(none)_ | Write results to this file path |
| `--json` | `-j` | flag | off | Output analysis as JSON instead of human-readable report |
| `--compare` | `-c` | string | _(none)_ | Path to a baseline analysis JSON file for comparison |

**Example:**
```bash
python scripts/prompt_optimizer.py prompt.txt --analyze --model claude-3-sonnet --json
```

**Output Formats:**
- **Default (text):** Human-readable report with metrics, scores, detected sections, issues, and suggestions
- **JSON (`--json`):** Structured `PromptAnalysis` object with keys: `token_count`, `estimated_cost`, `model`, `clarity_score`, `structure_score`, `issues`, `suggestions`, `sections`, `has_examples`, `example_count`, `has_output_format`, `word_count`, `line_count`
- **Token-only (`--tokens`):** Single-line token count and cost estimate
- **Examples (`--extract-examples`):** JSON array of `{input_text, output_text, index}` objects
- **Optimized (`--optimize`):** Cleaned prompt text with normalized whitespace

---

### rag_evaluator.py

**Purpose:** Evaluates Retrieval-Augmented Generation quality by measuring context relevance (lexical overlap, term coverage), answer faithfulness (claim-level verification), groundedness (ROUGE-L), and retrieval metrics (Precision@K, MRR, NDCG).

**Usage:**
```bash
python scripts/rag_evaluator.py --contexts <contexts.json> --questions <questions.json> [options]
```

**Parameters:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--contexts` | `-c` | string | _(required)_ | Path to JSON file with retrieved contexts. Expected keys per object: `question_id`/`query_id`, `content`/`text` |
| `--questions` | `-q` | string | _(required)_ | Path to JSON file with questions and answers. Expected keys per object: `id`, `question`/`query`, `answer`/`response`, `expected`/`ground_truth` |
| `--k` | | int | `5` | Number of top contexts to evaluate per question |
| `--output` | `-o` | string | _(none)_ | Write detailed report to this JSON file |
| `--json` | `-j` | flag | off | Output as JSON instead of human-readable text |
| `--verbose` | `-v` | flag | off | Include per-question detail breakdowns in the report |
| `--compare` | | string | _(none)_ | Path to a baseline report JSON for metric comparison |

**Example:**
```bash
python scripts/rag_evaluator.py --contexts retrieved.json --questions eval_set.json --k 10 --verbose --output report.json
```

**Output Formats:**
- **Default (text):** Human-readable report with summary, retrieval metrics (context relevance, Precision@K), generation metrics (faithfulness, groundedness), issues, and recommendations
- **JSON (`--json`):** Structured `RAGEvaluationReport` object with keys: `total_questions`, `avg_context_relevance`, `avg_faithfulness`, `avg_groundedness`, `retrieval_metrics`, `coverage`, `issues`, `recommendations`, `question_details`
- **Verbose (`--verbose`):** Adds per-question `question_details` array containing individual context scores and faithfulness breakdowns

---

### agent_orchestrator.py

**Purpose:** Parses agent configurations (YAML or JSON), validates tool registrations and flow correctness, generates ASCII or Mermaid workflow diagrams, and estimates token costs per run and monthly spend.

**Usage:**
```bash
python scripts/agent_orchestrator.py <config_file> [options]
```

**Parameters:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `config` | _(positional)_ | string | _(required)_ | Path to agent configuration file (YAML or JSON) |
| `--validate` | `-V` | flag | off | Validate agent configuration (errors, warnings, tool status). Runs by default if no other action is specified |
| `--visualize` | `-v` | flag | off | Generate workflow diagram |
| `--format` | `-f` | choice | `ascii` | Visualization format. Choices: `ascii`, `mermaid` |
| `--estimate-cost` | `-e` | flag | off | Estimate token usage and costs |
| `--runs` | `-r` | int | `100` | Daily run count for monthly cost projection |
| `--output` | `-o` | string | _(none)_ | Write output to this file path |
| `--json` | `-j` | flag | off | Output validation and cost results as JSON |

**Example:**
```bash
python scripts/agent_orchestrator.py agent.yaml --validate --visualize --format mermaid --output workflow.md
```

**Output Formats:**
- **Validation (text):** Agent info, tool status with OK/WARN indicators, flow analysis (max iterations, token estimate, loop detection), errors, and warnings
- **Validation (JSON, `--json`):** Structured `ValidationResult` object with keys: `is_valid`, `errors`, `warnings`, `tool_status`, `estimated_tokens_per_run`, `potential_infinite_loop`, `max_depth`
- **Visualization (`--visualize`):** ASCII box-drawing diagram (default) or Mermaid flowchart (`--format mermaid`) showing the agent pattern flow and registered tools
- **Cost estimation (`--estimate-cost`):** Token range per run, cost range per run, and projected monthly cost at the specified daily run rate
