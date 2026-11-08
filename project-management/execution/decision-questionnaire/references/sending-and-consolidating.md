# Sending, Following Up and Consolidating Answers

Writing the questionnaire is half the work. This reference covers the send itself, variants for more than one recipient, the follow-up cadence, turning answers into a decision record, and when to abandon async and meet.

## 1. Choosing async over a meeting

Use a questionnaire when all of these hold:

- The decision needs **specific knowledge** from one to five people, not a negotiation among them.
- The questions can be **stated precisely now**. If you cannot yet word the question, you need a conversation to find it, not a form.
- Respondents can answer **independently** — one person's answer does not depend on hearing another's first.
- A delay of several working days is acceptable.

Prefer a live conversation when:

| Signal | Why async fails |
|---|---|
| The recipients disagree with each other and know it | Independent answers just document the conflict; someone has to broker it |
| The decision is emotionally loaded (reorgs, cuts, people) | Written questions read as cold; answers get guarded |
| You cannot write the options table | You are still in discovery; a questionnaire would fix the frame too early |
| The answer is needed today | Async realistically needs two working days minimum |

A useful hybrid: send the questionnaire anyway and use it as the agenda for a short meeting. Respondents who fill it in beforehand make the meeting fifteen minutes instead of an hour.

## 2. The send message

The questionnaire travels inside a short message (email, chat, ticket comment). That message has four lines and nothing else:

1. What you need: "I need your input on where the analytics add-on is hosted for EU customers."
2. Why them: "You know what spend is committed for Q1, which I don't."
3. Cost and deadline: "About 12 minutes, by Thursday 20 November."
4. The default: "If I hear nothing, I'll go ahead with Frankfurt."

Do not paste the questions into the message body *and* attach the document — respondents answer whichever they see first, and you end up merging two partial answer sets.

### Where answers go

Decide one place for answers before sending: the document itself (inline under each question), a form, or a reply. Mixed channels are the most common source of lost answers. If respondents will see each other's answers, say so in "how your answers will be used" — it changes what people write.

## 3. Multiple recipients

| Situation | Variant | Notes |
|---|---|---|
| Same knowledge, need a cross-check | **Same questionnaire to each**, answered independently | Do not let respondents see each other's answers before submitting; anchoring makes agreement meaningless |
| Different knowledge per person | **One core plus per-recipient sections** | Keep the critical decision question identical for all; add role-specific questions only to the person who can answer them |
| One decider, several advisers | **Advisers first, decider second** | Send advisers the questionnaire, consolidate, then send the decider a two-question follow-up with the consolidated view |
| Large group (6+) | **Not a questionnaire** — use a survey or a decision meeting | Above about five, consolidation becomes polling and the "decision" becomes a vote nobody owns |

When the same question goes to several people, the consolidator compares answers:

- **pick-one / yes-no:** any difference is a conflict (yes-no compares the verdict, ignoring the stated condition).
- **ranked:** a conflict only when first choices differ; differences lower in the ranking are reported but not blocking.
- **number:** a conflict when the spread exceeds half the median (e.g. 1,500 vs 4,000).

## 4. Follow-up cadence

| When | Action |
|---|---|
| Send day | Send; put the deadline in your own calendar |
| Midpoint | One reminder to non-respondents only, restating time needed and the default |
| Deadline −1 working day | Direct message: "Tomorrow I'll go ahead with the default unless you'd like to weigh in." |
| Deadline | Run the consolidator. Record the decision, or follow up on blocking questions only |
| After deadline | Apply the default if critical questions are unanswered; tell non-respondents what was decided |

One reminder and one last-call is the ceiling. More than that trains people that your deadlines are soft.

### Follow-up on a partial answer

Do not resend the whole questionnaire. Send only the unanswered critical questions, or the conflicting ones, with what you already know: "Security picked A, you picked C — what would need to be true for A to work for you?" That is a different, sharper question than the original, and it often resolves the conflict in one reply.

## 5. Reading the consolidator outcome

| Outcome | Meaning | Next step |
|---|---|---|
| `ready-to-record` | Every critical question has a usable, consistent answer | Write the decision record; resolve non-critical conflicts at leisure |
| `needs-follow-up` | A critical question is unanswered before the deadline, or answered with a conflict | Targeted follow-up on the listed questions only (exit code 1) |
| `default-applied` | Deadline passed with critical questions unanswered and no conflict blocking | Record the decision as "decided by default" and notify recipients |

A conflict on a critical question blocks even after the deadline: the default exists to replace silence, not to overrule an explicit objection. When a respondent has said "not A", proceeding with A by default is a decision someone must own, so the tool keeps it in follow-up.

"Don't know" answers are recorded separately, never treated as votes. Three "don't know" responses to a critical question with no real answer is functionally unanswered — and a signal you asked the wrong people.

## 6. Writing the decision record

Use `assets/decision_record_template.md`. The record exists so that, six months later, someone can see what was decided, on what evidence, and what would reopen it. Fill it in this order:

1. **Outcome first**, stated as an action. If the default applied, say so in the first line.
2. **What the answers established** — one row per question that influenced the outcome, with the answer per respondent and how it was used. Questions that turned out not to matter can be omitted; note that they were asked.
3. **Disagreements** — every conflict, how it was settled, by whom, and why. A record that hides a disagreement invites the losing side to reopen the decision later.
4. **Open items** — useful "don't know" answers and catch-all points that need their own decision, each with an owner.
5. **Revisit if** — the concrete condition that would reopen the decision.

Then close the loop: send the record to every recipient, including those who did not answer. People who answered see their input used; people who did not learn what was decided without them, which is the strongest incentive to answer the next one.

## 7. When the questionnaire itself was wrong

Signs the questionnaire asked the wrong thing:

- Most answers land in "none of these" or the catch-all.
- Respondents answer a different question from the one asked.
- A respondent replies "I'm not the right person for this".
- The answers are consistent but do not let you decide.

Do not patch the questionnaire and resend to the same people. Go back to the gap analysis: either the recipient does not hold the knowledge you thought, or the decision is not yet framed well enough for questions. A short conversation is usually the faster repair.

## 8. Worked example (from the sample files)

The sample questionnaire asks a Security Lead and a Finance Controller to help choose the EU hosting region for an analytics add-on.

- **Clean run, day before the deadline** (`sample_answers.json`, `--today 2026-11-19`): both pick A, cost ceilings 4,000 and 3,500 (spread under half the median, so no conflict). They disagree on whether backups must stay in the EU — but that question is not critical. Outcome `ready-to-record`; the backup question goes into "Disagreements" with a follow-up owner.
- **Conflict run** (`sample_answers_conflict.json`): Security picks A, Finance picks C. Q1 is critical, so the outcome is `needs-follow-up` (exit 1). The follow-up is one question to Finance: what would make A acceptable?
- **Silence after the deadline** (an empty response list, `--today 2026-11-21`): outcome `default-applied`; the record states that Frankfurt was chosen without Security and Finance input.
