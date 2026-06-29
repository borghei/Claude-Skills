---
name: agentic-evaluation-framework
description: >
  This skill should be used when the user asks to "evaluate LLM output quality",
  "set up LLM-as-judge", "build an eval rubric", "compare model outputs pairwise",
  or "measure agent quality".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-engineering
  updated: 2026-06-29
  tags: [evaluation, llm-as-judge, rubrics, agents, quality]
---

# Agentic Evaluation Framework

> **Category:** Engineering
> **Domain:** AI Engineering

## Overview

Design and run trustworthy evaluations for LLM and agent outputs: pick the right grading method (programmatic check, LLM-as-judge, or human review), write a scoring rubric that judges can apply consistently, rank competing variants by pairwise comparison, and watch for the biases that quietly corrupt judge scores — position bias, verbosity bias, and self-preference. The goal is an eval that you can *trust enough to ship on*: calibrated against human labels, cheap enough to run on every change, and tracked alongside cost and latency so you never trade quality away by accident. This skill is model- and vendor-agnostic: it reasons about the evaluation *method*, not any one provider's API, and its scripts aggregate scores you have already collected — they never call a model.

## Clarify First

Before designing or running an evaluation, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **What "good" means** — the dimensions you care about (accuracy, helpfulness, safety, format, tool-use) and their relative weight (defines the rubric `criteria` and `weights`)
- [ ] **Grading method** — can a deterministic check decide it, do you need an LLM judge, or must a human review it? (selects programmatic vs `rubric_scorer.py` absolute scoring vs `pairwise_ranking.py` comparison vs human-in-the-loop)
- [ ] **Ground truth & budget** — do you have human-labeled examples to calibrate the judge against, and what cost/latency per eval run is acceptable? (sets calibration plan and the quality/cost/latency budget)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions.

## Quick Start

```bash
cd engineering/agentic-evaluation-framework

# 1. Score outputs against a weighted rubric + check inter-rater agreement
python scripts/rubric_scorer.py --data rubric_scores.json

# 2. Rank competing variants from pairwise (A-vs-B) judgements
python scripts/pairwise_ranking.py --data pairwise_matches.json

# JSON output for piping into a dashboard or CI gate
python scripts/rubric_scorer.py --data rubric_scores.json --json
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `scripts/rubric_scorer.py` | Aggregate per-criterion scores into weighted totals, per-criterion means, pass/fail vs thresholds, and an inter-rater agreement metric | `--data`, `--json` |
| `scripts/pairwise_ranking.py` | Turn head-to-head win/loss records into a ranking via Elo + Bradley-Terry, plus a win-rate matrix | `--data`, `--k`, `--base`, `--json` |

Both scripts: Python 3 standard library only, argparse CLI, `--json` and human-readable output. They compute over scores you provide and never call a model. Run `--help` for full usage.

## Workflows

### 1. Build and calibrate an absolute-scoring rubric

1. Translate "what good means" into 3-6 named criteria, each with a weight, a 1-5 (or 1-7) scale, and a written anchor for every scale point (see `references/llm-judge-methodology.md`).
2. Have at least two graders — human, or human plus model — independently score a calibration set, and record the per-criterion scores as the `rubric_scorer.py` input JSON.
3. Run `rubric_scorer.py` and read `inter_rater_agreement`: low agreement means the rubric is ambiguous, not that a grader is wrong — tighten the anchors and re-score before trusting any number.
4. Once graders agree, treat the human scores as ground truth and check that the LLM judge's scores correlate; if not, revise the judge prompt or fall back to human review for that criterion.
5. Wire the passing rubric into CI as a gate (`--json` → pass/fail), and re-run agreement periodically to catch judge drift.

### 2. Rank model/prompt variants by pairwise comparison

1. When absolute scores are noisy, switch to pairwise: show the judge two outputs (A and B) for the same input and ask only "which is better?" — easier and more reliable than an absolute number.
2. Mitigate position bias by running each pair in both orders (A,B and B,A) and counting a win only if it survives both; record outcomes as `pairwise_ranking.py` matches, using `"winner": "tie"` for disagreements.
3. Run `pairwise_ranking.py` to get Elo and Bradley-Terry rankings plus the win-rate matrix; Bradley-Terry is order-independent and preferred for a fixed batch, Elo for a streaming sequence of matches.
4. Inspect the win-rate matrix for intransitivity (A>B, B>C, but C>A) — a sign of an unreliable judge or genuinely tied variants; collect more matches or add human adjudication.
5. Report the ranking next to cost and latency per variant so the "winner" is the best *quality-per-dollar-per-second*, not just the highest score.

## Reference Documentation

- **[references/llm-judge-methodology.md](references/llm-judge-methodology.md)** — rubric design and scale anchoring; absolute vs pairwise scoring; the judge-bias catalog (position, verbosity, self-preference, sycophancy) with concrete mitigations; calibrating a judge against human labels; the eval feedback loop (collect → grade → analyze → fix → regression-gate); and the quality/cost/latency metrics to track together.
- **[references/eval-pitfalls.md](references/eval-pitfalls.md)** — the anti-patterns that make evals lie: single-grader rubrics, judging on the training set, gameable metrics, ignoring variance, optimizing the judge instead of the model, and the decision table for when to use a programmatic check vs an LLM judge vs human review.

## Common Patterns

- **Cheapest valid grader wins** — if a deterministic check (regex, JSON-schema, unit test, exact match) can decide it, use that; reach for an LLM judge only for fuzzy quality, and human review only for high-stakes or judge-calibration work.
- **Pairwise over absolute when scores are noisy** — "which is better, A or B?" is more reliable than "rate this 1-5"; use absolute rubrics for thresholds/gates and pairwise for model selection.
- **Swap positions to kill position bias** — always run each comparison in both orders and only count wins that survive both; a variant that only wins in position A is a judge artifact.
- **Length is not quality** — strip or normalize for verbosity bias; a longer answer is not a better one, and judges systematically over-reward length unless you control for it.
- **Don't let a model grade its own homework** — self-preference bias means a model favors its own outputs; use a different judge family from the model under test, or anchor on human labels.
- **Calibrate before you trust** — a judge is only as good as its agreement with humans on a held-out set; measure that agreement first, then automate.
- **Track quality, cost, and latency as one number** — a quality win that triples cost or latency may be a net loss; always report the three together so the tradeoff is explicit.
- **Evals are regression tests for prompts** — freeze a labeled eval set, gate every prompt/model change on it, and grow the set from production failures you find.
