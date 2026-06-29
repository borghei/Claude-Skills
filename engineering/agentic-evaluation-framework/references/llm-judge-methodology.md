# LLM-as-Judge & Agentic Evaluation Methodology

A practical, vendor-agnostic guide to evaluating LLM and agent outputs you can
trust enough to ship on. Pair it with `rubric_scorer.py` (absolute scoring) and
`pairwise_ranking.py` (comparison ranking).

---

## 1. Choose the grading method first

The most important decision is *who or what grades*. Use the cheapest method
that is valid for the question.

| Method | Use when | Cost | Trust |
|--------|----------|------|-------|
| **Programmatic check** | Output is verifiable: JSON schema, regex, exact/numeric match, unit test, tool-call shape, latency budget | ~free, deterministic | Highest — no judgement |
| **LLM-as-judge** | Quality is fuzzy: helpfulness, tone, faithfulness, reasoning, relevance — and you have many items | Cheap per item, but biased | Medium — must be calibrated |
| **Human review** | High stakes, ambiguous, safety-critical, or you are calibrating a judge | Expensive, slow | Highest for judgement, but variable |

Rule of thumb: **programmatic where you can, LLM-judge where you must, human to
calibrate and for high stakes.** Most mature eval suites layer all three:
programmatic gates catch the obvious, the LLM judge scores the fuzzy middle, and
humans label a calibration set plus spot-check the tails.

---

## 2. Absolute scoring vs pairwise comparison

There are two ways to grade with an LLM judge.

**Absolute (rubric) scoring** — rate each output on a scale per criterion.
- Good for: thresholds, CI gates, dashboards, tracking a metric over time.
- Weakness: scores are noisy and drift; "4 out of 5" means different things to
  different judges and on different days.

**Pairwise comparison** — show two outputs for the same input, ask which is better.
- Good for: choosing between models/prompts; far more reliable than absolute
  numbers because "is A better than B?" is an easier judgement than "rate A".
- Weakness: O(n²) comparisons; gives a ranking, not an absolute quality level.
- Convert wins/losses to a ranking with Elo (streaming) or Bradley-Terry
  (fixed batch, order-independent MLE) — see `pairwise_ranking.py`.

Use **absolute** for gates and trend lines; use **pairwise** for model selection
and whenever absolute scores are too noisy to separate variants.

---

## 3. Designing a scoring rubric

A rubric is only as good as its anchors. Vague criteria produce low inter-rater
agreement and untrustworthy scores.

1. **Decompose "good" into 3-6 criteria.** e.g. accuracy/faithfulness,
   helpfulness/completeness, safety, format/instruction-following, conciseness.
   Fewer, orthogonal criteria beat many overlapping ones.
2. **Weight by what matters.** `rubric_scorer.py` normalizes weights to sum to 1;
   a safety failure can hard-fail the item via a per-criterion `threshold`.
3. **Use a short ordinal scale** (1-5 or 1-7). Wider scales add noise, not signal.
4. **Write an anchor for every scale point.** "5 = fully correct and directly
   answers the question; 3 = partially correct with a minor omission; 1 = wrong
   or off-topic." Anchors are what make two judges agree.
5. **Make the judge cite evidence.** Require the judge to quote the span that
   justifies the score before emitting it — this reduces hand-waving and lets
   you audit disagreements.
6. **Score one criterion at a time.** Asking for all criteria in one pass invites
   halo effects (one good criterion inflates the rest).

---

## 4. Judge bias catalog & mitigations

LLM judges are systematically biased. Name the bias, then design it out.

| Bias | What happens | Mitigation |
|------|--------------|------------|
| **Position bias** | The judge favors whichever answer is shown first (or last) | Run every pair in **both orders**; count a win only if it holds both ways (record disputed pairs as `tie`) |
| **Verbosity / length bias** | Longer answers score higher regardless of quality | Normalize for length; instruct the judge to ignore length; penalize unnecessary verbosity explicitly in the rubric |
| **Self-preference bias** | A model rates its own family's outputs higher | Use a **different model family** as judge than the one under test; anchor on human labels |
| **Sycophancy / authority bias** | Confident or flattering tone scores higher | Score on substance; strip persuasive framing; require evidence citations |
| **Formatting bias** | Markdown, lists, and headers inflate scores | Evaluate content, not presentation, unless format is an explicit criterion |
| **Anchoring / order-of-criteria** | Early criteria color later ones | Score criteria independently; randomize criterion order |

A judge with **no measured bias controls is not trustworthy**, no matter how good
the model is.

---

## 5. Calibrating against human labels

A judge is only as good as its agreement with humans.

1. Build a **gold set**: 50-200 items with trusted human scores or human
   pairwise preferences.
2. Run the LLM judge on the same set.
3. Measure agreement:
   - Absolute: correlation (Spearman/Pearson) and exact-/within-1 agreement;
     `rubric_scorer.py` reports exact-agreement rate and a deviation-based
     normalized agreement when you include multiple graders per cell.
   - Pairwise: agreement rate between judge and human on which output won.
4. If agreement is low, the fault is usually the **rubric or judge prompt**, not
   the humans — tighten anchors, decompose the criterion, or fall back to human
   review for that dimension.
5. **Re-calibrate periodically** — model upgrades and prompt edits cause judge
   drift; an eval that was calibrated last quarter may have silently decayed.

---

## 6. The eval feedback loop

Evals are not a one-time report; they are a loop wired into development.

```
collect outputs  ->  grade (prog / judge / human)  ->  analyze failures
      ^                                                       |
      |                                                       v
  add failures  <----  fix prompt/model/agent  <----  regression-gate on labeled set
  to eval set
```

- **Freeze a labeled eval set** and gate every prompt/model/agent change on it —
  it is a regression test for behavior.
- **Grow the set from production failures.** Every real-world miss becomes a new
  eval case so it can never silently regress again.
- **Slice, don't just average.** A flat average hides that you got worse on a
  critical segment; break results down by input type, difficulty, and cohort.

---

## 7. Track quality, cost, and latency together

A quality win that triples cost or latency may be a net loss. Never report
quality alone.

- **Quality** — rubric score, win rate, or pass rate on the eval set.
- **Cost** — tokens × price per item (and total per eval run); cheaper judges
  and smaller models change the economics of running evals on every change.
- **Latency** — p50/p95 per item; matters for the product *and* for how often
  you can afford to run the eval.

Report the three side by side per variant. The variant you ship is the best
**quality-per-dollar-per-second** at your latency budget — not the single
highest score. When two variants tie on quality, cost and latency break the tie.

---

## 8. Programmatic checks every agent eval should include

Even with an LLM judge, cheap deterministic checks catch the obvious for free:

- **Schema/format** — output parses as valid JSON / matches the expected shape.
- **Tool-use correctness** — the right tool called with valid arguments.
- **Grounding** — cited sources actually exist in the provided context.
- **Safety/refusal** — disallowed content is refused; allowed content is not
  over-refused.
- **Budget** — token count, step count, and latency within bounds.
- **Determinism spot-check** — same input at temperature 0 yields stable output.

Run these first; only send what survives to the (more expensive) LLM judge.
