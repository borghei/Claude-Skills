---
name: linkedin-humanizer
description: >
  Audits and rewrites LinkedIn drafts to remove machine-sounding patterns:
  tiered tell catalogue, emoji-pattern scoring, rule explanations, and a voice
  fingerprint built from the author's own posts. Use when a draft reads
  generated, before publishing, or when an edit flattened someone's voice.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: tools
  domain: linkedin
  updated: 2026-10-07
  tags: [linkedin, humanizer, ai-writing, editing, voice, pre-publish]
---

# LinkedIn Humanizer

A draft that sounds generated fails twice. Readers who recognise the cadence
stop at the second line, and the author's name is now attached to a paragraph
that could have been posted by anyone. The usual fix makes it worse: someone
runs a find-and-replace on a list of forbidden words, chops the long sentences
into fragments, sprinkles in "honestly", and produces text that sounds like a
machine imitating a person who is trying not to sound like a machine.

This skill treats the problem as editing, with a catalogue. Thirty-three rules
are sorted into three tiers by what should happen to the text: **remove** (tool
residue no person writes), **reduce** (habits that are fine once and a signature
in bulk), and **review** (choices a careful writer makes on purpose). Each rule
carries the reason it fires, the fix, and the case for keeping the text as it
is. A separate scorer handles emoji placement, and a fingerprint built from the
author's own past posts decides which habits are theirs and must survive the
edit.

**Scope boundary.** This skill edits and audits a draft that already exists. It
does **not** choose an angle or write a post from a blank page; that is
`linkedin-post-writer`. It does **not** classify the opening lines of other
people's posts for reuse; that is `linkedin-hook-analyzer`. Comments and replies
have their own skills (`linkedin-comment-writer`, `linkedin-reply-manager`),
though the catalogue here applies to any short text pasted in. Interviewing the
author for the missing story or figure is `linkedin-story-interviewer`; this
skill only reports that the figure is missing. It makes no claim about how any
automated classifier will score the text and does not try to defeat one: the
target is a human reader. Everything runs offline on text the user supplies.
Nothing is posted, scheduled, fetched or sent anywhere; the user pastes the
finished draft into LinkedIn themselves.

## When to use this skill

- A draft was produced with a writing assistant and is about to go out under a person's name
- A post "feels off" and nobody can say which sentence is responsible
- An editor or ghostwriter needs to justify a change to an author who likes the sentence
- A team wants one pre-publish gate that every draft passes, with a documented exit code
- An earlier clean-up pass removed every dash and contraction and the result reads stiff
- Several past posts are available and drafts keep drifting away from how the author writes

## Inputs the skill expects

- The draft as plain text (a `.txt` file or stdin). Formatting should be what will be pasted
- Optional: three to ten of the author's own past posts, separated by `---` lines, for the fingerprint
- Optional: the facts the draft is missing (a figure with what it counts, a name, a date). The skill asks for them; it never invents them
- Who will read the post, when the audience is unusually strict about style

## Clarify First

Before editing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Audit only, or audit and rewrite** — an audit returns findings and leaves every word alone; a rewrite changes the author's text and needs their sign-off on meaning
- [ ] **Whether past posts are available** — with a fingerprint, the author's real habits (their dashes, their fragments) are waived; without one, every reduce-tier rule applies at face value and the edit may strip their voice
- [ ] **The facts behind vague sentences** — when the audit reports "nothing only the author could know", the only honest fix is a real figure or name from the author; the agent must not supply one
- [ ] **How strict the audience is** — a general feed needs the remove and reduce tiers; an audience that hunts for generated text may justify acting on the review tier too

Stop rule: ask only the 2-3 that most change the output. If the user says "just
clean it up," run the remove and reduce tiers, change nothing in the review
tier, and list every assumption and every unfilled fact at the top of the reply.

## Workflows

Quick start: run Workflow 1 on the draft, fix what it reports, and re-run until
the exit code is 0.

### Workflow 1 — Audit a draft before it is published

1. Save the draft exactly as it will be pasted, including line breaks.
2. Run the tell audit. Read the remove tier first: those hits block the gate on
   their own and usually mean a paste accident, not a style problem.
3. Run the emoji audit. It scores placement, not presence.
4. For each reduce-tier finding, read the `seen:` lines and decide per instance.
   The allowance exists because one contrast or one triple is ordinary writing.
5. Validate the result: the gate must pass (exit 0) before the draft is handed
   back. If it fails only on rule RD-16, stop and get the missing detail from the
   author.

```bash
python3 tools/linkedin/linkedin-humanizer/scripts/tell_audit.py \
  --input tools/linkedin/linkedin-humanizer/assets/sample_draft.txt --why

python3 tools/linkedin/linkedin-humanizer/scripts/emoji_audit.py \
  --input tools/linkedin/linkedin-humanizer/assets/sample_draft.txt
```

The sample draft fails with four blockers and a habit load of 29 against a limit
of 6. `assets/sample_draft_edited.txt` is the same post after Workflow 2 and
passes both tools.

### Workflow 2 — Rewrite without leaving edit marks

1. Clear the remove tier completely, then re-run. Removing a pasted preamble
   changes which line is the opening, and the opener rule only inspects line one.
2. Work paragraph by paragraph, worst first. Where RD-19 fired, rewrite the
   paragraph from its underlying fact; replacing words one at a time yields the
   same empty paragraph in different vocabulary.
3. Fix each remaining reduce-tier hit with the move in
   `references/rewrite-playbook.md`. Excess dashes become commas, colons or
   brackets, never full stops: splitting at a dash manufactures fragments.
4. Ask the author for any missing figure, name or date. Leave a visible gap in
   the reply if they have none.
5. Run the over-edit checklist (playbook §6): no new fragments, no added candor
   phrases, contractions and at least one long sentence still present.
6. Re-run the audit with `--tier review` and confirm the gate passes.

```bash
python3 tools/linkedin/linkedin-humanizer/scripts/tell_rules.py --explain RD-03

python3 tools/linkedin/linkedin-humanizer/scripts/tell_audit.py \
  --input tools/linkedin/linkedin-humanizer/assets/sample_draft_edited.txt --tier review
```

### Workflow 3 — Build a voice fingerprint and edit against it

1. Collect at least five posts the author wrote themselves, without assistance,
   into one file separated by `---` lines. Reshares and announcements written by
   a comms team do not count.
2. Build the fingerprint and save the JSON. Read the `Protect` lines: these are
   reduce-tier rules the author's own writing already exceeds.
3. Audit the draft with `--voice`. Protected rules are still displayed, marked
   as the author's habit, and add nothing to the load.
4. Compare the draft to the fingerprint. Drift on three or more measures means
   the draft is in someone else's voice even if no rule fired.
5. Record the result in `assets/voice_profile_template.md` so the next draft
   starts from it.

```bash
python3 tools/linkedin/linkedin-humanizer/scripts/voice_fingerprint.py \
  --input tools/linkedin/linkedin-humanizer/assets/sample_past_posts.txt \
  --compare tools/linkedin/linkedin-humanizer/assets/sample_draft.txt

python3 tools/linkedin/linkedin-humanizer/scripts/tell_audit.py \
  --input tools/linkedin/linkedin-humanizer/assets/sample_draft.txt \
  --voice tools/linkedin/linkedin-humanizer/assets/sample_voice.json
```

## Decision frameworks

### The three tiers

| Tier | What it catches | How it is counted | Effect on the gate |
|------|-----------------|-------------------|--------------------|
| **Remove** (RM-01 to RM-07) | Citation tokens, assistant preamble and sign-off, model self-reference, unfilled placeholders, unrendered markup, option labels | One hit is enough | Any hit fails the gate |
| **Reduce** (RD-01 to RD-19) | Stock vocabulary, contrast frames, staged question-and-answer, triples, fragments, announced candor, stock openers and closers, dash density, noun stacks, hedge stacks, no author-only detail | Hits above a per-post allowance, weighted 1-3 | Load above `--max-load` fails the gate |
| **Review** (RV-01 to RV-07) | A single dash, a lone triple, passive voice, curly quotes, semicolons, out-of-fashion flagged words, a long post with no contractions | Reported as notes | Never fails the gate |

The tiers are a statement about evidence. A remove-tier hit is proof of a paste
accident. A reduce-tier hit is a pattern that only means something in quantity.
A review-tier hit is a taste question, and treating taste as proof is how good
sentences get deleted. All allowances and weights are editorial heuristics.

### What to do with a finding

| Situation | Action | Why |
|-----------|--------|-----|
| Remove-tier hit | [PROVEN] Delete or fill, every time, then re-run | No reader forgives a visible placeholder, and it shifts which line the opener rule sees |
| One paragraph holds three or more stock words (RD-19) | [PROVEN] Rewrite the paragraph from the fact it gestures at | Word swaps keep the emptiness; the paragraph has no claim to preserve |
| Reduce-tier hit at exactly the allowance | [RECOMMENDED] Leave it | One contrast or one triple is ordinary prose; scrubbing to zero is its own tell |
| Rule fires on a habit visible in the author's past posts | [RECOMMENDED] Waive through the fingerprint, not by hand | The waiver is then recorded and repeatable across drafts |
| RD-16 fires and the author has no figure to give | [RECOMMENDED] Ship the post shorter and plainer | An honest thin post beats a specific-sounding invented one |
| Review-tier notes on a general-audience post | [RECOMMENDED] Read them, change nothing by default | Each has a legitimate human use documented in the catalogue |
| Acting on the whole review tier for a strict audience | [EXPERIMENTAL] Only on request, and re-check for over-editing | Removing every dash, triple and passive tends to flatten the voice |

### Which gate settings to use

| Draft type | `--max-load` | Emoji `--fail-under` | Notes |
|------------|--------------|----------------------|-------|
| Personal post, general audience | 6 (default) | 60 (default) | [RECOMMENDED] The setting the samples are calibrated on |
| Company-page or executive post | 3 | 75 | [RECOMMENDED] More scrutiny, fewer second chances |
| Short reshare caption under 40 words | 6 | 60 | Density rules have little to measure; read the result as a spot check |
| Author with a fingerprint on file | 6 with `--voice` | 60 with `--usual N` | [PROVEN] Stops the gate punishing the author for sounding like themselves |

## Anti-Patterns

### Scrubbing by word list
**Mistake:** The editor searches for twenty forbidden words, swaps each for a synonym, and calls the draft clean. "Leverage our comprehensive platform" becomes "use our full platform".
**Why it happens:** A word list is easy to share and easy to apply, and the vocabulary is the most visible layer of the problem.
**Instead:** Treat stock vocabulary as a symptom of a paragraph with no claim. When RD-19 fires, find the fact the paragraph was avoiding ("seven fields before you could print a label") and write that. `tell_audit.py` weights a vocabulary cluster three times a single word for this reason.

### Curing flat rhythm with fragments
**Mistake:** Every sentence is the same length, so the editor breaks them up. "It worked. Really worked. Better than expected." The draft now trips RD-06 and RD-07.
**Why it happens:** Advice to "vary sentence length" is correct and gets applied as "add short sentences", because short is quicker to produce than long.
**Instead:** Fix uniformity by joining, not cutting. Take two adjacent sentences that are causally related and connect them with a clause that carries the cause. Change one place per paragraph and stop.

### Adding sincerity
**Mistake:** The draft feels impersonal, so the edit inserts "I'll be honest", "this one was hard to write", or a confession the author never made.
**Why it happens:** Vulnerability is a real quality of good posts and the phrase is a cheap proxy for it.
**Instead:** Delete announcements of candor (RD-08) and replace them with the uncomfortable fact itself, dated and unframed: "We lost the account on 14 March." If no such fact exists, the post is not a vulnerable one, and that is fine. The agent never invents one.

### Treating the review tier as a to-do list
**Mistake:** Every dash, every passive verb and every list of three is removed because the audit mentioned them.
**Why it happens:** A finding looks like an instruction, and "zero findings" looks like the goal.
**Instead:** The review tier is displayed only on request and never affects the exit code. Read `keep it when` in `tell_rules.py --explain` before touching anything. A 300-word post with no dashes, no contractions and no triples has been visibly scrubbed.

### Auditing against rules instead of against the author
**Mistake:** An author who has written in clipped fragments for years is edited into flowing paragraphs because RD-06 fired.
**Why it happens:** The catalogue is to hand and the author's back catalogue is not.
**Instead:** Build the fingerprint first (Workflow 3). It takes five past posts and one command, and it converts "this is how they write" from an argument into a file the audit reads.

### Promising a score from an automated checker
**Mistake:** The author asks whether the post will "pass" some classifier and the editor says yes.
**Why it happens:** A number feels like a deliverable.
**Instead:** Say plainly that this skill does not measure or target any classifier, that short texts give such tools little to work with, and that the standard here is whether a person who knows the author would believe they wrote it.

## Files

Tools overview and reference documentation for this skill:

| File | Purpose |
|------|---------|
| `scripts/tell_audit.py` | The gate. Applies the three-tier catalogue to a draft, reports each rule that fired with the matching text and fix, honours a voice file, exits 1 on any blocker or excess habit load |
| `scripts/tell_rules.py` | Rule data and shared text splitters. `--list` prints the catalogue; `--explain RULE_ID` prints why a rule fires, the fix, and when to keep the text |
| `scripts/emoji_audit.py` | Scores emoji placement from 0 to 100 across eight rules (bullet runs, headings, stock set, clusters, opening line); exits 1 below `--fail-under` |
| `scripts/voice_fingerprint.py` | Builds a fingerprint from past posts (medians, recurring words, protected rules) and with `--compare` reports where a draft drifts; exits 1 beyond `--max-drift` |
| `references/rule-catalogue.md` | Every rule with what it looks like, why readers notice, a before-and-after rewrite, and the legitimate reason to keep it |
| `references/rewrite-playbook.md` | Order of operations for a rewrite, the paragraph-level method, a full worked example, and the over-edit checklist |
| `references/emoji-patterns.md` | The eight placement rules, how the score is built, what a hand-placed emoji looks like, and how to tune the thresholds to an author |
| `references/voice-fingerprint-guide.md` | What each measure means, how many posts are enough, how protection works, and how to settle a conflict between a rule and a habit |
| `assets/sample_draft.txt` | A generated-sounding draft that trips all three tiers and five emoji rules |
| `assets/sample_draft_edited.txt` | The same post rewritten with real detail; passes both gates |
| `assets/sample_past_posts.txt` | Five posts by a fictional support lead, used to build the sample fingerprint |
| `assets/sample_voice.json` | Fingerprint generated from the sample posts, ready to pass to `--voice` |
| `assets/voice_profile_template.md` | Fill-in profile recording an author's fingerprint, protected habits and off-limits phrases |
| `assets/audit_report_template.md` | Fill-in report for handing audit results and proposed edits back to an author |
