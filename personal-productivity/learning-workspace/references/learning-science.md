# Learning Science for Self-Directed Study

The design rules in this skill rest on a small number of well-replicated effects from
cognitive and educational psychology. This file explains each effect, what it means for
how a lesson is built, and the mistakes it predicts. Read it when designing a lesson,
when a learner says "I get it" too quickly, or when progress stalls.

## 1. Performance during practice is a poor guide to learning

The single most important distinction for anyone running their own study:

| | Fluency (retrieval strength) | Storage (durable learning) |
|---|---|---|
| What it is | How easily something comes to mind right now | How well it survives time and interference |
| How it feels | Smooth, confident, "obvious" | Effortful to build; invisible while forming |
| What raises it | Re-reading, massed repetition, seeing the answer | Spaced retrieval, varied practice, generation |
| Failure it causes | Illusion of competence; forgotten in a week | Feels slow; learners abandon it |

**Implication:** never mark an item `secure` on the strength of how a session felt. The
`review_scheduler.py` gate refuses `secure` until an item has been recalled at least three
times on an expanding schedule — the only cheap evidence of storage a solo learner has.

Practical tells that fluency is being mistaken for learning:

- The learner can follow the worked example but cannot start a blank one.
- Recognition questions (multiple choice) go well; recall questions (blank page) do not.
- Answers come fast on the day of the lesson and are gone three days later.
- The learner re-reads notes before every check — that is rehearsal, not retrieval.

## 2. Retrieval practice

Pulling an answer from memory strengthens it far more than reading it again. The act of
retrieval is itself the learning event, not merely a measurement.

Design rules:

1. **Start every lesson with retrieval of due items**, before any new material. Three to
   five questions, no notes, two to four minutes. The scheduler's `warm_up` list is this.
2. **Ask for production, not recognition.** "Write the formula for the standard error" beats
   "Which of these is the standard error?". Use recognition only for first exposure.
3. **Give feedback after the attempt, never before.** A failed retrieval followed by the
   correct answer is still a strong learning event; skipping the attempt is not.
4. **Low stakes.** Retrieval is practice, not an exam. A learner who fears the check will
   look things up first and destroy the effect.

Retrieval formats in rough order of strength:

| Format | Example | Strength |
|---|---|---|
| Free recall | "Write everything you remember about confidence intervals" | Highest; slow |
| Explain-back | "Explain to a new hire why the interval got wider" | High; exposes gaps |
| Cued recall | "What happens to the standard error when n quadruples?" | High; fast |
| Application | "Here is a results table — is the effect real?" | High; tests transfer |
| Recognition | Multiple choice | Low; use for diagnosis only |

## 3. Spacing

The same amount of practice spread over time produces much more durable memory than
practice massed into one sitting. The optimal gap grows as the memory strengthens.

The scheduler's interval ladder, in days after each successful spaced recall:

```
1 -> 3 -> 7 -> 14 -> 30 -> 60 -> 120
```

Rules the tool applies, and why:

| Rule | Reason |
|---|---|
| A recall only extends the streak if it came at least ~75% of the current step after the previous review | Same-day re-reads raise fluency, not storage |
| A failed recall resets the streak to step 1 | The memory was not stored; rebuild from short gaps |
| A partial recall repeats the current step | Partly stored; neither promote nor punish |
| `secure` requires a streak of 3 including a gap of 5+ days | Below that, the item has never survived a real gap |

Ladders are a convention, not a law. A learner with a hard exam date can compress the
upper steps; a lifelong-interest learner can stretch them. What must not change is the
shape: gaps grow only after success.

## 4. Interleaving

Mixing different but related problem types in one practice set (A B C B A C) beats
blocking them (A A A B B B C C C) for skills where the hard part is **choosing** the
method. Blocked practice tells the learner which method to use before they start;
interleaved practice forces them to discriminate.

- Use interleaving once at least two related techniques have been introduced.
- Do not interleave during first exposure — it overloads working memory.
- It suits procedural and diagnostic skills (which test? which pose? which chord?) more
  than pure fact recall.

## 5. Cognitive load and the size of a lesson

Working memory holds only a few new elements at once. A lesson that introduces six new
ideas teaches none of them.

| Load type | Source | What to do |
|---|---|---|
| Intrinsic | The difficulty of the idea itself | Sequence prerequisites first; one new idea per lesson |
| Extraneous | Bad presentation: split attention, clutter, jargon | Remove; put labels on diagrams, define terms once in GLOSSARY.md |
| Germane | Effort spent building understanding | Protect it; this is the effort that should remain |

**Rule of thumb:** one lesson = one tangible win the learner can demonstrate at the end.
If the exit check needs more than three questions to cover the lesson, it was two lessons.

### Difficulty is the enemy of acquisition and the friend of retention

This looks contradictory and is not. While acquiring a new idea, make it as easy as
possible to understand (clear example, low load). Once acquired, make practice effortful
(spaced, interleaved, recall from blank). Easy-to-understand, hard-to-practise.

## 6. Worked examples and fading

Novices learn more from studying a fully worked example than from solving the same
problem unaided, because problem-solving search consumes the working memory needed to
learn the pattern. As competence grows the advantage reverses — experts learn more from
solving.

Fading sequence for a new procedure:

1. Full worked example with each step's reason written next to it.
2. Same type, last step left blank.
3. Same type, last two steps blank.
4. New surface, all steps blank.
5. Mixed (interleaved) with earlier types.

Skipping straight to step 4 is the most common reason a capable learner "just doesn't get"
a topic.

## 7. Generation and elaboration

Information the learner generates (predicts, explains, connects) is remembered better than
information they receive.

- **Predict before revealing.** "Before we run the simulation — how far apart will the two
  sample means be?" A wrong prediction followed by the reveal is memorable.
- **Ask why, then why again.** Elaborative questions tie a new fact to existing knowledge.
- **Self-explanation.** After each worked-example step, the learner states the reason.

## 8. Feedback

| Situation | Timing | Form |
|---|---|---|
| New concept, first practice | Immediate | Correct answer plus the reason |
| Procedural skill being automated | Immediate | Short, specific ("sign error in step 3") |
| Retrieval of an established item | After the attempt | Correct answer; let the learner self-grade recalled/partial/failed |
| Judgment or open-ended work | After a full attempt | Compare to an expert's reasoning, not just the answer |

Feedback that only says "wrong" teaches nothing. Feedback that gives the answer before the
attempt removes the retrieval.

## 9. The zone of proximal development

The productive next lesson is the one the learner cannot do alone yet but can do with
support. Too easy wastes time and builds false confidence; too hard produces no learning
and erodes motivation.

How to locate it from the workspace:

1. Read `learning-record.json`: items `secure` are the floor, items `learning` are the edge.
2. Read open misconceptions — they block anything that builds on them.
3. Read the curriculum dependency order — the next module is the first `todo` whose
   prerequisites are all `done`.
4. Pick the smallest step from the edge toward the mission's success criteria.

Signals the lesson was mis-pitched:

| Signal | Diagnosis | Adjust |
|---|---|---|
| Exit check perfect, no hesitation, under half the planned time | Too easy | Skip ahead; mark items as prior knowledge with evidence |
| Warm-up items mostly failed | Previous lesson did not store | Re-teach with a new example before advancing |
| Learner cannot start the first practice task | Too hard; prerequisite missing | Drop back a step; add a worked example |
| Learner disengages despite correct answers | Mission disconnect | Re-tie the lesson to the mission's "why" |

## 10. Misconceptions

A misconception is not missing knowledge; it is wrong knowledge that actively produces
wrong answers and resists correction. Telling the learner the right answer once rarely
removes it.

Handling sequence:

1. **Surface it** with a question the misconception answers wrongly.
2. **Make the conflict visible** — let the learner see their prediction fail.
3. **Give the replacement model** and show why it predicts correctly.
4. **Record it** in `learning-record.json` with a recheck date.
5. **Recheck later** with a new surface — misconceptions return under time pressure.

The scheduler fails the gate on an open misconception with no recheck date, because
unrechecked misconceptions reappear exactly when the learner builds on them.

## 11. Knowledge topics versus skill topics

| | Knowledge-heavy (history, theory, law) | Skill-heavy (instrument, language, yoga, coding) |
|---|---|---|
| Lesson centre | Explanation plus retrieval | Demonstration plus deliberate practice |
| Exit check | Explain-back, application question | Perform the move; self-record or get observed |
| Evidence for `secure` | Spaced recall | Spaced performance at target quality |
| Biggest risk | Fluency illusion from reading | Practising errors until they are automatic |
| Role of community | Debate and correction | Observation and feedback on form |

Most topics are mixed. Decide per module, not per topic.

## 12. Motivation and adherence

Learning plans fail on adherence more than on design.

- Tie every lesson to the mission's concrete outcome; abstract lessons are the first to be
  skipped.
- Keep sessions short and fixed in the calendar; a 25-minute lesson three times a week
  beats a two-hour lesson that happens once a fortnight.
- After a long gap, restart with a rebuild session (warm-up on everything due, no new
  material). The scheduler flags `restart_mode: rebuild` after 21 days without a session.
- Record wins. The learning record is also evidence of progress for a discouraged learner.
