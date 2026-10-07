---
name: linkedin-post-writer
description: >
  Drafts LinkedIn posts from a brief: picks an angle and opening pattern the
  author's real material supports, structures the body, and gates the draft
  before it is pasted. Use when writing a post, choosing a hook, or checking a
  draft before publishing.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: tools
  domain: linkedin
  updated: 2026-10-07
  tags: [linkedin, copywriting, hooks, content-drafting, pre-publish]
---

# LinkedIn Post Writer

Most weak posts are decided before the first word is written. The author
starts from a topic ("something about onboarding") instead of from material (a
number, a date, a thing a customer said), so the draft has to be built from
generalities, and generalities all sound alike. The opening is then chosen for
how it sounds, a format is borrowed from a post that did well for someone else,
and the result is a confident paragraph about nothing in particular with a
question bolted to the end.

This skill reverses the order. It starts with an inventory of what the author
really has, lets that inventory decide which of fourteen opening patterns are
available, builds the body from beats that each need a fact, and runs a
mechanical gate before the text leaves the editor. Patterns the author lacks
the material for are not offered; instead the skill says which single question
would unlock them.

**Scope boundary.** This skill drafts a single feed post and checks it. It does
**not** run the full machine-tell audit, score emoji, or build a voice
fingerprint; hand the draft to `linkedin-humanizer` for that. It does **not**
study other people's posts to extract their openings; that is
`linkedin-hook-analyzer`. Drawing a story out of an author who "has nothing to
say" is `linkedin-story-interviewer`; turning an article, talk or thread into
posts is `linkedin-content-repurposer`; deciding what to post this month is
`linkedin-content-planner`. Comments and replies (`linkedin-comment-writer`,
`linkedin-reply-manager`, `linkedin-thread-tracker`), profile copy
(`linkedin-profile-optimizer`), team programmes (`linkedin-employee-advocacy`)
and performance review (`linkedin-engagement-analytics`) are separate skills.
Everything here is offline: the skill produces text for the user to paste into
LinkedIn themselves. It does not post, schedule, fetch, or call any service.

## When to use this skill

- Someone asks for a LinkedIn post and has a topic but no angle
- A draft exists and the opening is not working
- An author has one good fact (a result, a mistake, a quote) and wants the post built around it
- A ghostwriter needs a repeatable way to brief, draft and check posts for several authors
- A draft is finished and needs a last mechanical check before it is pasted
- The same author keeps producing the same shape of post and wants a different one

## Inputs the skill expects

- A brief: topic, one goal, the audience in a sentence (`assets/post_brief_template.md`)
- The author's material: any of a figure, a dated event, a scene, a changed belief, an opposing view, a before-and-after, a quote, a rule, a sample count, a question they were asked, a person to credit, a term to explain, a prediction, a list of steps
- Constraints: what must be included, what must not be named, preferred length
- Optional: a voice profile or two past posts, so the draft is in the author's register

## Clarify First

Before drafting, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The one goal** (conversation, saves, reshares, or inbound interest) — it changes which pattern ranks first and what the last line asks for; a post that tries for all four gets none
- [ ] **What the author actually has** — at least one concrete item of material; without it every pattern is locked and the only honest output is a question back to the author
- [ ] **Who it is for** — the same fact is written differently for peers, buyers and candidates; "everyone" produces a post for no one
- [ ] **What cannot be said** — client names, unreleased figures, people who have not agreed to be named; these decide whether a quote or a number can be used at all

Stop rule: ask only the 2-3 that most change the output. If the user says "just
draft it," use the material in the request as given, pick the top-ranked
pattern, and list the assumed goal and audience at the top of the reply. If
there is no material at all, ask the single unlock question for the pattern
that best fits the topic; do not invent a figure to get started.

## Workflows

Quick start: fill in the brief, run the picker, draft from the first option,
run the gate.

### Workflow 1 — From brief to angle

1. Fill in `assets/post_brief_template.md` with the author, or convert their
   notes into the JSON shape in `assets/sample_brief.json`. Leave a material
   field empty if the author does not have it.
2. Run the picker. It ranks only the patterns the material supports and lists
   the rest as locked, each with the question that would unlock it.
3. Read any `caution` lines. A counter-position or a prediction with no
   evidence behind it is an opinion; get the evidence or choose another pattern.
4. Offer the author the top two or three options in one line each. Let them
   choose; they know which one they are comfortable publishing.

```bash
python3 tools/linkedin/linkedin-post-writer/scripts/angle_picker.py \
  --input tools/linkedin/linkedin-post-writer/assets/sample_brief.json --top 3
```

### Workflow 2 — Draft the post

1. Write the opening from the chosen pattern in
   `references/opening-patterns.md`. The agent writes it from the author's
   material and nothing else; the point of the line must land inside the first
   clause.
2. Write the second line so it works if the first is all the reader sees
   before expanding: add the stake, do not restate.
3. Build the body from the pattern's beats (`references/post-structures.md`).
   One beat per paragraph, each anchored to a fact. Cut any beat the author has
   no fact for.
4. Include the part that did not work. A post with no cost, exception or open
   question reads as an advertisement.
5. Close according to the goal: a question only a practitioner could answer,
   the last fact, or nothing. Never a stock ask.
6. Draft two alternative openings from the second-ranked pattern so the author
   has a real choice.

```bash
python3 tools/linkedin/linkedin-post-writer/scripts/angle_picker.py \
  --input tools/linkedin/linkedin-post-writer/assets/sample_brief.json \
  --top 5 --format json
```

### Workflow 3 — Gate the draft before it is pasted

1. Save the draft as plain text with the line breaks it will have in the feed.
2. Run the gate. Blockers fail it outright; more than three warnings fail it.
3. Fix blockers first: a leftover placeholder or a stock closing line is never
   acceptable. Then work the warnings in the order shown.
4. Verify that every figure, name and quote in the draft appears in the brief,
   using the manual checklist in `references/pre-publish-gate.md` §4. The tool
   cannot do this part.
5. Re-run until the exit code is 0, then hand over the text with its character
   count. For a full style audit, pass the result to `linkedin-humanizer`.

```bash
python3 tools/linkedin/linkedin-post-writer/scripts/post_gate.py \
  --input tools/linkedin/linkedin-post-writer/assets/sample_draft.txt

python3 tools/linkedin/linkedin-post-writer/scripts/post_gate.py \
  --input tools/linkedin/linkedin-post-writer/assets/sample_draft_revised.txt
```

The first sample fails with two blockers and three warnings. The revised
version of the same post passes clean.

## Decision frameworks

### Pattern by material

The pattern is chosen by what the author has, then ranked by goal. Goal-fit
scores are editorial heuristics, not measurements.

| The author has… | Pattern | Strongest for |
|-----------------|---------|---------------|
| One precise figure | Receipt line | Saves, inbound |
| A date and something that went wrong | Dated mistake | Conversation |
| A moment they were present for | Cold scene | Conversation, reshares |
| A belief they dropped | Changed mind | Conversation |
| A disagreement with common practice, plus evidence | Counter-position | Conversation, reshares |
| A before and an after | Measured gap | Saves, inbound |
| Someone's exact words | Borrowed line | Conversation |
| A rule they keep | House rule | Saves |
| A count of things examined | Field count | Saves, reshares, inbound |
| A question they keep being asked | Reported question | Conversation |
| A person who did a specific thing | Named credit | Reshares |
| A term their audience misuses | Plain definition | Saves |
| An expectation with a date on it | Dated bet | Conversation, reshares |
| Three or more real steps | Counted list | Saves |

### Choices that come up in every draft

| Decision | Recommendation | Why |
|----------|----------------|-----|
| Start from topic or from material | [PROVEN] Material. If there is none, ask for it before drafting | A post is as specific as its least specific input |
| Opening: statement or question | [RECOMMENDED] Statement. Put a real question at the close | A question in line one asks for attention before giving a reason |
| Where the key fact goes | [PROVEN] In the first clause of the first line | The feed truncates the opening; anything after the cut is seen only by people already interested |
| How many ideas | [PROVEN] One. Park the second in a note for the next post | Two ideas halve the space for evidence on each |
| Length | [RECOMMENDED] As long as the facts last: usually 600 to 1,400 characters | Past the facts, length is restatement |
| Include what failed | [RECOMMENDED] Yes, with the same precision as what worked | It is what separates a report from a promotion |
| Hashtags | [RECOMMENDED] None to three, on the last line | They are labels, not content |
| A link in the body | [EXPERIMENTAL] Put it in the first comment unless the link is the point | Widely practised, effect unverified; the gate warns and `--allow-links` overrides |
| Mentioning the author's product | [RECOMMENDED] Once, where the story reaches it | Earlier, the post becomes an advert |

### Platform mechanics the gate assumes

| Setting | Default | Status |
|---------|---------|--------|
| Post character limit | 3,000 | Current as of writing; verify in the product |
| Characters visible before truncation | 140 | Conservative mobile estimate as of writing; desktop shows more. Override with `--fold-chars` |
| Markdown rendering | None | As of writing, asterisks and pound signs display literally |

These change without notice. Treat them as configuration, not knowledge.

## Anti-Patterns

### Writing the opening first and looking for a post to fit it
**Mistake:** The author has a line they like ("Nobody talks about the real cost of meetings") and builds four paragraphs to justify it.
**Why it happens:** A good-sounding line arrives easily and feels like progress. The material that would support it takes effort to dig out.
**Instead:** Fill in the brief first. `angle_picker.py` will show that the line is a teaser with nothing behind it, and that the author's real asset is, say, "62 person-hours every Monday", which opens the post on its own.

### Borrowing a format without the material it needs
**Mistake:** A measured-gap post did well for someone else, so the author writes "We went from struggling to thriving in six months" with no figures.
**Why it happens:** The format is visible and the measurements behind it are not.
**Instead:** Treat every pattern's `needs` as a hard requirement. A gap needs two numbers measured the same way and a time span. If the author has one number, it is a receipt line; if none, the pattern is locked and the picker says what to ask.

### Trying for every goal at once
**Mistake:** The post tells a story, lists seven tips, thanks the team, and ends by inviting people to book a call.
**Why it happens:** Each addition seems free, and each stakeholder has a request.
**Instead:** One goal per post, chosen in the brief. The goal sets the pattern ranking and the close. Everything else goes in a note for the next post; `linkedin-content-planner` is the place to schedule them.

### Leaving out what went wrong
**Mistake:** Every paragraph reports success. The fortnight where two teams shipped conflicting changes is cut "to keep it positive".
**Why it happens:** The author is writing under their employer's name and caution feels safe.
**Instead:** Keep one cost, exception or unsolved part, stated as precisely as the wins. Compare the two sample drafts: the revised one opens on the mistake, and it is the more credible post.

### Closing with a generic ask
**Mistake:** "What do you think?" or "Agree?" as the last line.
**Why it happens:** The author has been told to end on a question and has no specific one.
**Instead:** Ask something that can only be answered from experience ("what broke in the first two weeks?") or end on the last fact. `post_gate.py` blocks the stock wordings outright.

### Passing the gate and skipping the read-through
**Mistake:** Exit code 0, so the draft is pasted.
**Why it happens:** A green check feels like approval.
**Instead:** The gate checks mechanics. It cannot tell whether the figure is right, whether Ines agreed to be quoted, or whether the post is interesting. Check every fact against the brief and have the author read the text aloud once.

## Files

Tools overview and reference documentation for this skill:

| File | Purpose |
|------|---------|
| `scripts/angle_picker.py` | Ranks the fourteen opening patterns by the material in a brief and the stated goal; prints the opening skeleton, body beats and close for each, and the unlock question for every pattern the brief cannot support |
| `scripts/post_gate.py` | Pre-paste gate with fifteen checks: opening fit and phrasing, length, placeholders and markup, paragraph density, hashtags, links, specificity, habit spot-check, closing line; exits 1 on any blocker or excess warnings |
| `references/opening-patterns.md` | The fourteen patterns: what each needs, how to build it, an original example, the usual way it goes wrong, and four opening types to avoid |
| `references/post-structures.md` | Body beats per pattern, the second line, closes by goal, length bands, layout, and a full worked draft from the sample brief |
| `references/pre-publish-gate.md` | Every gate check with its level and rationale, platform mechanics and their caveats, the manual checks the tool cannot do, and how to tune thresholds |
| `assets/sample_brief.json` | A filled brief for a fictional COO writing about cancelling a weekly all-hands |
| `assets/sample_draft.txt` | First draft from that brief; fails the gate on a placeholder, a stock closer, a long opening, a dense paragraph and six hashtags |
| `assets/sample_draft_revised.txt` | The same post after revision; passes the gate |
| `assets/post_brief_template.md` | Fill-in brief covering goal, audience, material inventory, constraints and sign-off |
