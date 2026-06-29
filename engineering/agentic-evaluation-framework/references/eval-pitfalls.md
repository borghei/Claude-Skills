# Evaluation Pitfalls & Anti-Patterns

The failure modes that make an eval *lie to you* — and how to avoid them. An
eval that produces a confident wrong number is worse than no eval, because teams
ship on it.

---

## Anti-patterns

### 1. Single-grader rubric
**Smell:** one judge (or one human) scores everything; you report the number as truth.
**Why it lies:** you cannot tell signal from that grader's idiosyncrasy. There is
no agreement to measure, so ambiguity in the rubric hides.
**Fix:** at least two graders on a calibration set; measure inter-rater agreement
(`rubric_scorer.py` reports it) before trusting any score. Tighten anchors until
they agree.

### 2. Judging on the training/development set
**Smell:** the eval set overlaps with examples used to write the prompt or tune the model.
**Why it lies:** you measure memorization, not generalization. Scores look great
and collapse in production.
**Fix:** hold out a fresh eval set the model has never seen; keep it sealed and
rotate periodically.

### 3. Gameable / proxy metrics
**Smell:** the metric is easy to optimize without improving quality — e.g.
rewarding length, keyword presence, or "did it produce JSON" instead of "is the
JSON correct".
**Why it lies:** Goodhart's law — once a metric is a target it stops being a good
measure. The model learns the proxy, not the goal.
**Fix:** measure the outcome you actually care about; pair any proxy with a
quality check; watch for sudden metric jumps with no real improvement.

### 4. Ignoring variance
**Smell:** a single run per item; rankings reported without confidence.
**Why it lies:** LLM outputs are stochastic; a 2-point "win" can be pure noise.
**Fix:** multiple samples per item; report spread, not just the mean; for
pairwise, collect enough matches that the ranking is stable and check the
win-rate matrix for intransitivity (A>B>C>A signals noise).

### 5. Optimizing the judge instead of the model
**Smell:** you keep tweaking the judge prompt until scores go up.
**Why it lies:** you are improving the *measurement*, not the system. The product
did not get better.
**Fix:** freeze the judge once it agrees with humans; changes to the judge
require re-calibration against the gold set, tracked separately from model work.

### 6. No bias controls
**Smell:** pairwise comparisons run in a fixed order; same model family judges itself.
**Why it lies:** position and self-preference bias inflate the favored side by a
wide margin — the ranking measures bias, not quality.
**Fix:** swap positions and require both-order wins; use a different judge family
than the model under test. (See the bias catalog in `llm-judge-methodology.md`.)

### 7. Averaging away the failures
**Smell:** one headline average across all items.
**Why it lies:** a great average can hide a catastrophic regression on a critical
slice (e.g. safety, a key customer segment, hard inputs).
**Fix:** slice by input type, difficulty, and cohort; gate on the worst slice,
not the mean.

### 8. Quality in a vacuum
**Smell:** the report shows only a quality score — no cost, no latency.
**Why it lies:** the "best" variant may be 3× the cost or unusably slow.
**Fix:** track quality, cost, and latency together; pick on quality-per-dollar-
per-second at your latency budget.

### 9. Stale eval set
**Smell:** the eval set has not changed in months while the product has.
**Why it lies:** it no longer reflects real usage, and known production failures
are not represented, so they keep recurring.
**Fix:** treat the eval set as living; feed every production failure back in as a
new regression case.

### 10. LLM judge where a check would do
**Smell:** using an expensive, biased LLM judge to verify something
deterministic — valid JSON, an exact answer, a tool name.
**Why it lies:** you pay more, add latency, and import judge bias to grade
something that has a right answer.
**Fix:** use a programmatic check; reserve the judge for genuinely fuzzy quality.

---

## Decision table: programmatic vs LLM-judge vs human

| Question | Use |
|----------|-----|
| Does it parse / match a schema / pass a unit test? | **Programmatic** |
| Is there a single correct answer (exact / numeric / tool call)? | **Programmatic** |
| Is it within a token / step / latency budget? | **Programmatic** |
| Is it fuzzy quality (helpful, faithful, well-reasoned, on-tone) and high volume? | **LLM-judge** (calibrated, bias-controlled) |
| Are you choosing between variants on fuzzy quality? | **LLM-judge, pairwise** |
| Is it high-stakes, safety-critical, legally sensitive, or ambiguous? | **Human** |
| Are you building/validating the gold set the judge calibrates to? | **Human** |
| Did the judge and a check disagree, or is the judge near a threshold? | **Human** (adjudicate the tail) |

Layer them: programmatic gate first (free, catches the obvious) → LLM judge on
what survives (cheap, scales) → human on the gold set and the contested tail
(expensive, authoritative).
