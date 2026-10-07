# Rewrite Playbook

How to turn audit findings into a better draft without producing a different
kind of bad draft. The catalogue (`rule-catalogue.md`) says what is wrong with
a sentence; this file says in what order to fix things and when to stop.

Every example is invented. Thresholds are editorial heuristics.

## Contents

1. The principle: restore, do not disguise
2. Order of operations
3. The paragraph method
4. Moves by rule
5. Getting facts from the author
6. The over-edit checklist
7. Full worked example
8. When to hand the draft back unedited

---

## 1. The principle: restore, do not disguise

A generated-sounding draft is missing information. The stock phrases, the
triples, and the staged questions are what fills the space where a figure, a
name, or a decision should be. Disguising the fill (new synonyms, shuffled
sentence lengths) leaves the space empty. Restoring means finding out what the
author knows that the draft does not say, and putting that in.

This is why the single most useful question in a rewrite is not "how do I
rephrase this?" but "what happened?"

Three rules follow from the principle:

1. **Never add a fact the author did not supply.** A specific-sounding invented
   detail is worse than a vague true one, and it is the author's reputation.
2. **Never add a feeling the author did not express.** No inserted hesitation,
   no confession, no "this was hard to write".
3. **Change as little as fixes the problem.** If the audit found little, the
   edit is small. There is no quota of changes to fill.

---

## 2. Order of operations

Work in this order. Each step changes what the next step sees.

| Step | What | Why this position |
|------|------|-------------------|
| 1 | Clear the remove tier | Deleting a preamble changes which line is the opening; filling a placeholder may supply the missing figure |
| 2 | Re-run the audit | The opener and closer rules look at fixed positions |
| 3 | Fix the opening line (RD-09) | Highest weight, and the new opening often makes a later paragraph redundant |
| 4 | Replace clustered paragraphs (RD-19) | Whole-paragraph replacement removes many smaller findings at once |
| 5 | Fix the remaining weighted-2 rules (RD-03, RD-04, RD-08, RD-10, RD-16) | Most recognisable patterns |
| 6 | Bring counted habits under allowance (RD-01, RD-02, RD-05, RD-06, RD-11…) | Now there are fewer of them |
| 7 | Run the over-edit checklist (§6) | Steps 3 to 6 can introduce new patterns |
| 8 | Re-run with `--tier review` | Confirm the gate, read the notes, change nothing by default |

Do not start at step 6. Tidying vocabulary in a paragraph that step 4 will
delete is wasted effort, and it is the reason word-list editing takes so long
and achieves so little.

---

## 3. The paragraph method

The unit of repair is the paragraph. For each paragraph the audit touched:

1. **State its job in six words.** "Says what we changed." "Gives the result."
   If the job cannot be stated, the paragraph is a candidate for deletion.
2. **Find the fact.** What number, name, date, quote or decision does this
   paragraph depend on? If the draft does not contain it, ask (§5).
3. **Write the fact as a plain sentence.** Subject first, verb second.
4. **Add at most one sentence of consequence or reaction.** In the author's
   register, which the fingerprint describes.
5. **Check the join.** Read the last sentence of the previous paragraph and the
   first of this one together. If a connective is needed to get from one to the
   other, reorder before adding the connective.

A paragraph that survives step 1 but fails step 2 (it has a job, but no fact is
available) should be cut to one honest general sentence rather than padded.

---

## 4. Moves by rule

| Finding | The move | The move to avoid |
|---------|----------|-------------------|
| RD-01 stock vocabulary | Replace the word with the thing it stood for | Swapping for a synonym from the same register |
| RD-02 intensifier | Delete; if the sentence now seems weak, add the evidence | Replacing with a different intensifier |
| RD-03 contrast frame | State the second half alone, then support it | Rephrasing the denial ("far from being…") |
| RD-04 Q-and-A bridge | Delete the question; join the answer to the previous sentence | Turning it into a colon reveal ("The result: …") |
| RD-05 triple | Keep the items that are specific; usually two | Padding to four to dodge the pattern |
| RD-06 fragments | Fold each into its neighbouring sentence | Deleting them all, including the author's own |
| RD-08 announced candor | Delete the announcement, keep the fact | Moving the announcement mid-sentence |
| RD-09 stock opener | Promote the most specific sentence in the draft to line one | Writing a clever new first line with nothing behind it |
| RD-10 stock closer | Ask something answerable only from experience, or end on the last fact | "Curious what others think" |
| RD-11 dash density | Comma, colon or brackets by function; keep the best dash | Full stops |
| RD-12 participle opener | Actor, then verb | Converting to a passive |
| RD-13 signpost | Delete; reorder if the link breaks | A different connective |
| RD-14 noun stack | Recover the verb and its subject | A shorter noun |
| RD-15 uniform length | Join two causally linked sentences once | Alternating long and short throughout |
| RD-16 no anchors | Ask the author | Inventing a plausible figure |
| RD-17 label reveal | Say it as a sentence the author would say aloud | A different label |
| RD-18 hedge stack | Commit, or name the specific unknown | Removing all uncertainty from an uncertain claim |
| RD-19 cluster | Replace the paragraph | Editing the paragraph |

The right-hand column matters as much as the middle one. Nearly every "move to
avoid" converts one finding into another: the Q-and-A bridge into a label
reveal, the dash into a fragment, the triple into a longer list. An edit that
changes the rule ID without changing the load has not improved the draft.

---

## 5. Getting facts from the author

When the audit reports RD-16, or a paragraph has a job but no fact, ask. Keep
the questions closed and few; the author is busy and the answers are short.

| Missing | Ask | Not |
|---------|-----|-----|
| A figure | "What was the number before and after, and over what period?" | "Do you have any metrics?" |
| A name | "Who did the work on this? Can they be named?" | "Anyone you'd like to mention?" |
| A date | "When did you make the call?" | "Roughly when was this?" |
| The cost | "What did it cost, in time or money or a person?" | "Were there any challenges?" |
| The exception | "Where did this not work?" | "Any caveats?" |

Rules for using the answers:

- Use the author's figure with its referent: "9 days to 2, median, signup to
  first label". A number without what it counts is decoration.
- If the author says "about a third", write "about a third". Do not sharpen it.
- If someone cannot be named, describe them by role.
- If the author has nothing, say so in the hand-back and deliver a shorter post.
  A longer interview to draw the story out is a separate job from this edit.

---

## 6. The over-edit checklist

Editing leaves its own marks. Before returning a rewrite, check each line. Any
"yes" means dial back, not push further.

- [ ] Did the edit create a fragment that was not in the original? Re-join it.
- [ ] Did a removed dash become a full stop? Use a comma, colon or brackets.
- [ ] Are the sentences now alternating long, short, long, short? Break the
      pattern once by leaving two medium sentences together.
- [ ] Did any phrase of candor, hesitation or self-deprecation get added that
      the author did not write? Remove it.
- [ ] Are there now zero dashes, zero contractions and zero lists of three in a
      post over 150 words? Restore whichever the author used.
- [ ] Is any figure, name or date in the rewrite absent from the author's
      material? Remove it and flag it.
- [ ] Does the rewrite claim something stronger than the original did? Restore
      the original strength of claim.
- [ ] Would the author recognise the first line as something they would say out
      loud? If not, offer two alternatives instead of one.
- [ ] Has the voice comparison moved further from the fingerprint than the
      original was? Then the edit swapped one foreign voice for another.

Validate by running `tell_audit.py --tier review` and, where a fingerprint
exists, `voice_fingerprint.py --compare`. The gate must pass and drift should
be at or below two measures.

---

## 7. Full worked example

The draft is `assets/sample_draft.txt`. The author is a fictional head of
onboarding at a fictional shipping-software company, Tidewell.

### 7.1 What the audit said

Four blockers (preamble, sign-off, placeholder, markup). Reduce tier: nine
stock words with a cluster in paragraph four, two contrast frames, a staged
"The result?", seven fragments, an announced candor, a stock closer, three
dashes in 151 words, two participle openers, one signpost. Emoji score 25.

### 7.2 Step 1 and 2: remove tier, re-run

Deleting the first and last lines removes the preamble and sign-off. The
placeholder needs the company name. The bold markers go. On re-run, the line
"In today's fast-paced landscape…" is now first and RD-09 fires at weight 3.

### 7.3 Asking the author

The draft contains no figure and no name. Four questions went to the author:

1. What was the onboarding number before and after? *Median signup to first
   shipped label: 9 days in January, 2 days now.*
2. What was the one change that did most of it? *Making the carrier-rates table
   optional. It asked for seven fields before you could print anything.*
3. Who found that? *Maren Okafor in support pulled 60 calls and tagged where
   each customer went quiet. 41 were on that screen. Isak built the fix in four
   days.*
4. What didn't work? *The guided tour I argued for. And accounts adding a
   second warehouse still stall.*

Everything in the rewrite comes from those four answers.

### 7.4 Paragraph by paragraph

| Original paragraph | Its job | Decision |
|--------------------|---------|----------|
| "In today's fast-paced landscape, onboarding isn't just a process…" | Open the post | Replace with the before-and-after figure |
| "Let me be honest: most teams get this wrong." | Raise stakes | Delete. No fact behind it |
| "At [Your Company], we leveraged a comprehensive, holistic framework…" | Say what was done | Replace with the 60 calls and the seven-field table |
| "The result? Faster activation, happier users, and stronger retention." | Give the result | Already covered by the new opening; delete |
| Three emoji-headed bullets | Lessons | Replace with why the table existed and who it failed |
| "Simple. Clear. Repeatable." / "That's it." | Emphasis | Delete |
| "It's important to note that onboarding is not about features…" | Thesis | Replace with what the fix was and what else did not move the number |
| "Building trust early, teams create momentum…" | Reinforce | Delete |
| "Bottom line: invest in onboarding." | Close | Replace with the unsolved part |
| "What do you think? Agree?" | Ask | Replace with a question only practitioners can answer |

Six of ten paragraphs were deleted outright. That ratio is typical: most of a
generated draft is restatement.

### 7.5 The result

`assets/sample_draft_edited.txt`. Habit load 0, emoji score 100, and one
drifting measure against the sample fingerprint (sentences run a little long).
Note what the edit did not do: it did not add a confession beyond the author's
own "I was wrong about the tour", did not invent a retention figure, and kept
the author's brackets and contractions.

---

## 8. When to hand the draft back unedited

- **The audit passes and the review notes are all defensible.** Say so. A pass
  that finds nothing should change nothing.
- **The draft is the author's own unassisted writing and they like it.** Report
  the findings, explain the two or three that carry weight, and let them choose.
- **The findings are all habits the fingerprint protects.** The draft sounds
  like the author; that was the goal.
- **The post is an announcement of a fact** (a job, a date, a launch). Clear
  the remove tier and the opener, and leave the rest.
