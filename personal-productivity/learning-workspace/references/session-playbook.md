# Session Playbook: Running, Checking, Resuming

Step-by-step scripts for the three things that happen in a learning workspace: running a
lesson, checking understanding, and resuming after a gap. Read the relevant section at
the start of a session.

## Session zero: setting up

Goal: a validated mission and a first lesson, in one sitting of about 30 minutes.

1. **Interview for the mission.** Ask why the learner wants this, then ask what changes in
   their work or life when they have it. Keep asking until the answer names an outcome
   ("size my own experiments") rather than a topic ("statistics").
2. **Turn the outcome into 2–4 observable success criteria.** Use the "could someone watch
   me do it?" test.
3. **Capture constraints.** Session length, sessions per week, any hard date. These size
   lessons and the curriculum.
4. **Capture claimed prior knowledge.** Treat it as a hypothesis; lesson 1 verifies it.
5. **Draft 4–8 modules** in dependency order, each with an observable outcome. More than
   about 12 is a plan that will be rewritten before it is used.
6. **Find resources before teaching.** At least one primary source and one community.
   Do not teach facts from memory alone when a checkable source exists.
7. **Write the spec and run the scaffolder.** Fix every error it reports; decide on each
   warning.
8. **Run lesson 1** immediately if time allows — momentum matters more than polish.

## Running a lesson

Target length is the mission's session length (default 25 minutes). Proportions for a
25-minute lesson:

| Block | Minutes | Purpose |
|---|---|---|
| Warm-up | 3–4 | Retrieval of due items, no notes |
| Core idea | 5–7 | One new idea, minimal load, cited source |
| Worked example | 3–5 | Fully worked; learner states each step's reason |
| Practice | 7–9 | Faded tasks, immediate feedback |
| Exit check | 3 | Explain-back + one transfer question |
| Record | 1–2 | Update the learning record |

### Before the lesson

1. Run `review_scheduler.py --input learning-record.json --today <date>`.
2. Read the resume brief: active module, next module, warm-up list, open misconceptions.
3. Read NOTES.md for preferences.
4. Choose the lesson's single win. It must sit at the edge of what is `secure` and lead
   toward a mission success criterion.
5. Copy the lesson template to `lessons/NNNN-slug.md` and fill the plan.

### During the lesson

- **Warm-up first, always.** Ask each due item as a production question. The learner
  answers, then grades themselves recalled/partial/failed against the correct answer.
- **One idea.** If a second idea is needed to make the first make sense, it is a
  prerequisite and belongs in an earlier lesson.
- **Predict before revealing.** Ask for a prediction before every demonstration.
- **Fade the example.** Practice tasks remove steps progressively; the last task changes
  the surface.
- **Watch for the misconception signature.** A confident wrong answer that the learner
  defends is a misconception, not a slip. Stop and handle it (below).
- **Invite questions.** Remind the learner the teacher is there to answer anything unclear;
  an unasked question is the most common hidden gap.

### After the lesson

1. Add a session entry: date, module, lesson path.
2. Append each warm-up review result to its item.
3. Add new items with `state: new` (or `learning` if the exit check showed it) and evidence.
4. Add misconceptions with a recheck date 2–5 days out.
5. Update module status if its outcome was demonstrated.
6. Add any new terms to GLOSSARY.md.
7. Re-run the scheduler; the gate must pass before the session is closed.

## Checking understanding

Use at least two different check types per lesson — any single type can be gamed by
fluency.

| Check | Prompt pattern | Catches |
|---|---|---|
| Explain-back | "Explain this to a colleague who missed the lesson" | Memorised phrases without a model |
| Predict | "What will happen if we double n?" | Rules applied without understanding |
| Transfer | Same idea, new context: "Now it's a retention metric, not conversion" | Surface-bound knowledge |
| Contrast | "How is this different from X?" | Confusion between neighbours |
| Find the error | "Here is a colleague's write-up — what's wrong?" | Passive recognition only |
| Boundary | "When would this not work?" | Over-generalisation |
| Perform (skills) | "Do it now; I'll watch / record it" | Knowing about versus being able to |

### Reading the answers

| Answer pattern | Meaning | Action |
|---|---|---|
| Correct, fast, in own words | Learned (for today) | Record evidence; schedule review |
| Correct, slow, with hints | Partially formed | Grade `partial`; one more practice task |
| Correct words, cannot apply | Fluency without model | Give a transfer task; do not record evidence yet |
| Confident and wrong | Misconception | Handle as below |
| "I don't know" | Honest gap | Good — reteach with a new example |

### Handling a misconception

1. Do not correct immediately. Ask a question the wrong model answers wrongly.
2. Let the learner commit to the prediction, then show the result.
3. Give the replacement model in one or two sentences and show why it predicts correctly.
4. Have the learner restate it in their own words.
5. Record it with `status: open` and a recheck date. Mark `corrected` only after a later
   recheck on a new surface succeeds.

## Resuming

The workspace is designed so any session — or any assistant — can pick up with no memory
of earlier conversations.

1. Run the scheduler. Read `restart_mode`.
2. **`continue`** (gap ≤ 21 days): normal lesson; the warm-up covers due items.
3. **`rebuild`** (gap > 21 days): no new material. Spend the session on retrieval of
   everything due, re-teach whatever fails, and re-check open misconceptions. Resume new
   material next session.
4. Re-read MISSION.md aloud with the learner. A long gap often means the mission drifted;
   ask whether it still holds and record any change.
5. If the scheduler reports more than ~15 items due, cap the warm-up at five, prioritise
   the most overdue, and add a dedicated review session rather than stretching the lesson.

## Mission changes

Change the mission when the learner's real goal has moved, not when a lesson was hard.

| Signal | Likely meaning |
|---|---|
| Learner keeps asking about an adjacent area | Mission is too narrow or aimed wrong |
| Success criteria are met but the learner keeps going | Mission complete; write the next one |
| Lessons tied to one criterion are consistently skipped | That criterion is not wanted |
| External change (new job, exam moved) | Constraints or criteria are stale |

Procedure: confirm with the learner, edit MISSION.md, add a dated row to **Mission
changes**, update the curriculum, and keep the history — the record of how goals evolved
is useful later.

## Wrapping up a mission

When every success criterion has been demonstrated:

1. Run a final mixed check across all modules (interleaved, from blank).
2. Mark the mission complete in MISSION.md with the date.
3. Keep the review schedule running on `secure` items at the long end of the ladder; a few
   minutes a month preserves most of what was built.
4. Ask whether there is a next mission. If so, start a new workspace or a new mission
   section; do not let an old curriculum silently expand.
