# Question Design for Async Decision Questionnaires

A decision questionnaire is read once, by someone busy, without you in the room to clarify. Every question has to survive that reading. This reference covers how to find the right questions, how to word them, which answer format to attach, how to order and size the set, and the failure patterns the linter checks for.

## 1. Find the gap before writing a single question

The questions should target exactly one thing: **the gap between what the recipient knows and what the sender needs to decide.** Anything outside that gap is either something the sender can find out alone (and should) or something the recipient cannot answer either.

Work out the gap from two sender-side facts, both of which the sender can always answer:

1. **Who is this going to, and what do they know that I don't?** Role, expertise, relationship, and the specific knowledge they hold — "the Finance Controller knows what infrastructure spend is already committed for Q1", not "Finance has opinions".
2. **What must I walk away able to decide or do?** A short list of concrete outputs — "pick a hosting option", "know the cost ceiling", "know whether backups count for residency".

Then, for each output, ask: *which single fact or judgment from this recipient would unblock it?* That is the question. If an output needs nothing from this recipient, it does not belong in this questionnaire.

### Facts you can look up are not questions

Before sending, strip every question whose answer exists somewhere the sender can reach: a contract repository, a dashboard, a previous decision record, the codebase, the org chart. Asking the recipient to look something up for you spends their goodwill on clerical work and dilutes the questions only they can answer. The test: *could a diligent new hire find this in under 20 minutes?* If yes, find it yourself.

### Do not interview the sender about the subject

The sender is writing the questionnaire precisely because they cannot answer the subject questions. Grilling them on the subject ("what do you think the cost ceiling should be?") either produces guesses that then leak into the questionnaire as leading framing, or reveals that they could have decided alone. Interview the sender only about the send: who, what they need back, by when, what happens if nobody answers.

## 2. One idea per question

A question asks for exactly one fact or judgment. The two common violations:

| Pattern | Example | Problem | Fix |
|---|---|---|---|
| Conjunction | "Should backups stay in the EU and should logs stay there too?" | A "yes" might mean yes to one; a "no" is uninterpretable | Two questions, or one pick-one with four combinations |
| Stacked questions | "What does Legal say? What does the DPO say?" | Respondent answers the easier half | Separate questions, or route to the right person |
| Hidden either/or | "Is cost or speed more important, and by how much?" | Mixes a choice with a magnitude | Ranked question, then a number question |
| Embedded premise | "When we move to Frankfurt, what will break?" | Presumes the decision | "If we chose Frankfurt, what would break?" |

The linter flags more than one question mark and the patterns "and/or + auxiliary verb" ("and should", "or would"). It cannot see a hidden premise — review for that by hand.

## 3. Neutral wording

A leading question tells the recipient which answer you want. Async makes this worse, not better: the recipient cannot see your face, so they read the wording as the signal, and agreeable people supply the answer it implies.

Leading families the linter catches:

- **Tag questions and negative interrogatives:** "Don't you think…", "Wouldn't it be…", "Isn't it better…", "Shouldn't we…", "…, right?"
- **Certainty markers:** "obviously", "clearly", "surely".
- **Agreement prompts:** "Do you agree that…".

Leading patterns it does not catch, which need a human pass:

- **Loaded descriptors:** "the risky US option", "the proven Frankfurt setup".
- **Asymmetric detail:** three sentences of upside on option A, one line on B.
- **Order bias:** the recommended option always listed first in every question. List options in a fixed, stated order (A, B, C) and mark the recommendation explicitly instead of signalling it by position.

### Recommending without leading

A sender often has a lean, and hiding it is unhelpful — the recipient may want to react to it. The honest pattern is to **state the lean once, in the options table, labelled as such** ("A — our current lean"), and then ask neutral questions. "Which option would you approve?" with a labelled recommendation is fair. "Don't you think A is safest?" is not.

## 4. Attach an answer format to every question

Free-form answers are slow to write and impossible to compare across respondents. Every question declares one of five formats:

| Format | Use when | Rules |
|---|---|---|
| **pick-one** | A choice among known alternatives | At least two choices; always include "none of these" and "don't know" so nobody is forced into a false answer |
| **ranked** | Relative priority matters more than absolute | Three to five items; more than five and the middle of the ranking is noise |
| **number** | A threshold, budget, date offset, volume | Always state the unit ("EUR per month", "requests per second", "weeks"); ask for a single number or an explicit range, not "roughly" |
| **yes-no** | A binary constraint | Always invite the condition: "yes / no / yes-if…". Bare yes-no hides the most useful part of the answer |
| **free-text** | Facts you cannot enumerate (which contracts, which customers) | Cap the length (30-80 words) and say so; uncapped text produces essays from some respondents and one word from others |

Rules of thumb:

- If you catch yourself writing a free-text question for a judgment call, convert it into a pick-one with the realistic options and an escape.
- A number question is the best defence against vague agreement: "is the cost acceptable?" gets "yes"; "what is the most you would approve?" gets 3,500.
- Ranking is the right tool for "what matters most" — never ask people to rate five things on a 1-5 scale; everything comes back as 4.

## 5. "Why this matters" — only when needed

A one-line rationale under a question helps in two cases:

1. The question could be misread ("Must backups stay in the EU?" — the respondent may not realise backups are a separate decision from primary storage).
2. The question invites a throwaway answer ("Which contracts name a region?" — without the rationale, "none that I know of" looks like a fine answer).

Adding a rationale to every question doubles reading time and buries the ones that need it. The linter does not require it; the review checklist asks you to justify each one.

## 6. Order, grouping and size

**Most important first.** Async means you may get one pass, possibly partial. Put the questions that decide the outcome at the top and mark them critical. If the respondent stops after three questions, you should still be able to decide.

**Group by theme once you have more than four questions.** Themes are recipient-facing ("Approval", "Compliance", "Gaps"), not sender-facing ("Stuff for the infra ticket"). Within a theme, still most-important-first.

**Size budget: about ten questions and fifteen minutes.** Past that, completion rates drop and late questions get skimmed. The linter estimates effort from answer formats:

| Format | Approx. minutes |
|---|---|
| yes-no | 0.75 |
| pick-one | 1.0 |
| number | 1.5 |
| ranked | 2.0 |
| free-text | 3.0 |

If you are over budget: cut questions you can answer yourself; merge two pick-ones into one with combined choices; move "nice to know" questions to a second round after the decision.

## 7. The closing catch-all

End with one open question: "Is there anything we did not ask that would change this decision?" It is the only deliberately open question in the set, and it is the one that catches the constraint the sender did not know existed. Keep it last and keep it single.

## 8. Context paragraph

One paragraph, under about 150 words, written for someone who was in none of the meetings:

- What exists today.
- What changed that forces a decision now.
- What is already decided and **not** up for discussion (so the recipient does not spend their answer relitigating it).

"See the thread from last week" is not context. The recipient will not read the thread, and if they do, they will answer the thread rather than your questions.

## 9. The default if nobody answers

Every questionnaire states what happens if no answer arrives by the deadline, as an action: "we proceed with option A and record that the choice was made without Finance input." This does three things:

- It converts silence into a decision instead of a blocker.
- It gives the recipient a reason to answer — if they dislike the default, they now have to say so.
- It makes the sender commit to a lean, which often exposes that the questionnaire is really asking for a veto check, not open input. That is fine; say so.

A default must be something the sender is actually willing to do. A default of "we wait" is not a default.

## 10. Linter finding reference

| Code | Severity | Meaning |
|---|---|---|
| missing-purpose / missing-decision / missing-context | error | Header fields the recipient needs to orient |
| missing-deadline / deadline-past | error | No deadline, or it has already passed relative to `--today` |
| missing-default-if-no-answer | error | Silence would block the work |
| missing-recipient | error | Nobody named |
| single-option / multiple-recommended / missing-tradeoffs | error | The options table cannot support a choice |
| leading / vague / compound | error | Wording problems that corrupt answers |
| missing-format / too-few-choices / missing-unit | error | Answers would not be comparable |
| too-many-questions / effort-over-budget | error | Over the size budget |
| missing-use / missing-catch-all / no-escape-option / no-escape-choice | warn | Weaker but sendable |
| uncapped-free-text / yes-no-no-condition / missing-theme | warn | Answer quality will vary |
| deadline-tight / context-long / estimate-over-budget / missing-effort | warn | Likely to be answered late or skimmed |

Warnings do not fail the gate. Fix them when the decision is high-stakes or the recipient is senior; ship with them for a quick internal check.

## 11. Hand-review checklist

The linter cannot read intent. Before sending, read the questionnaire once as the recipient and confirm each line:

- [ ] Every question targets something only this recipient knows; nothing is a lookup the sender could do.
- [ ] No question presumes the decision ("when we move to…" instead of "if we chose…").
- [ ] Options are described with comparable detail and no loaded adjectives.
- [ ] The recommendation, if any, appears once, labelled, in the options table.
- [ ] The critical questions are first and would let you decide even if the rest are skipped.
- [ ] Each "why this matters" line earns its place by preventing a misreading or a throwaway answer.
- [ ] The default on silence is an action you are genuinely willing to take.
- [ ] Context mentions what is already decided and off the table.
- [ ] One answer channel is named.
