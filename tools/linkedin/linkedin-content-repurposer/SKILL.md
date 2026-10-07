---
name: linkedin-content-repurposer
description: >
  Turns something made for another channel (a thread, a video or talk
  transcript, a blog post, a newsletter) into a post that reads as native to
  LinkedIn, without changing what the source says. Use when existing material
  should become a LinkedIn post rather than writing one from a blank page.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: tools
  domain: linkedin
  updated: 2026-10-07
  tags: [linkedin, repurposing, content-adaptation, transcripts, fidelity-check]
---

# LinkedIn Content Repurposer

The usual way to reuse a piece is to paste it and trim. The result carries its
old channel with it: a thread arrives with numbering and a call to repost, a
talk arrives with "as you can see on this slide", an article arrives as a
summary of five points when a post can hold one. Readers recognise the residue
at once and read it as something not written for them.

The opposite failure is quieter and worse. In rebuilding the piece, the rewrite
improves on it: a rounder number, a percentage the author never calculated, a
neat quotation nobody said. The post now claims something the source does not,
under the name of the person who made the source.

This skill does both jobs in order. The agent first measures the source and
lists what will not survive the move, then rebuilds from the idea rather than
the sentences, then checks the draft against the source so that nothing was
added on the way.

**Offline only.** The skill works from text files the user provides. It does
not fetch a URL, download a video, pull a transcript, post, schedule or call
any API. If the source lives online, the user pastes or saves the text first.

**Scope boundary.** This skill adapts material that already exists. Writing a
post from a blank page or a draft seed is `linkedin-post-writer`. Removing
machine-sounding phrasing from any draft is `linkedin-humanizer`; scoring or
rewriting the opening line in depth is `linkedin-hook-analyzer`. When the
source has no concrete detail and the author has to supply some, that is
`linkedin-story-interviewer`, whose story bank file this skill can optionally
read. Deciding which week the repurposed post runs in is
`linkedin-content-planner`. Comments and replies are `linkedin-comment-writer`,
`linkedin-reply-manager` and `linkedin-thread-tracker`; profile copy is
`linkedin-profile-optimizer`; reuse of company material by a team is
`linkedin-employee-advocacy`; reading results afterwards is
`linkedin-engagement-analytics`.

## When to use this skill

- "Turn this thread into a LinkedIn post"
- A talk, webinar or podcast appearance has a transcript and nothing has been done with it
- A long article or newsletter issue holds several posts and the author keeps meaning to extract them
- Something did well elsewhere and the pasted version fell flat here
- A draft has already been made from a source and needs checking for invented figures or leftover artefacts
- A team wants a repeatable way to mine one recorded talk for a month of posts

## Inputs the skill expects

- The source as a local `.txt` or `.md` file: thread text, transcript, article, talk script or newsletter
- Confirmation that the user wrote it, or has the right to adapt it, and whose name the post goes under
- The one reader the post is for and the one thing it should ask of them
- Whether links in the source should appear in the post at all
- Optional: a story bank file, to widen the set of figures the author has already confirmed and to enforce never-name and no-go lists
- Optional: a different length band from the default, if the author has their own

## Clarify First

Before analysing or drafting, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Whose words these are** — adapting your own talk is editing; adapting a colleague's, a panel's or an employer's needs permission and attribution, and changes whether the post can be first-person at all.
- [ ] **One post or several** — a long source usually holds more than one; deciding up front stops the draft becoming a summary of everything.
- [ ] **Which single point this post carries** — the analyser offers candidates, but the author knows which one they would defend in the comments.
- [ ] **What happens to links and to co-speakers' remarks** — both are easy to carry over by accident and awkward to remove after publishing.

Stop rule: ask only the two that most change the output. If the user says "just convert it", take the top-ranked spine candidate, produce one post, leave links out of the body, and list those assumptions above the draft.

## Workflows

Quick start: save the source as a text file, run Workflow 1, draft from the
top spine candidate, then run Workflow 2 before showing anyone the result.

### Workflow 1 — Analyse the source before writing anything

1. Save the source text locally. Do not clean it first; the analyser needs to
   see the artefacts.
2. Run the analyser. Read the **Move** line (compress, expand, split or
   rebuild in place) and the number of posts the source holds.
3. Read every `rework` finding: each is something to remove or remake.
4. Choose one spine candidate with the author. The candidates are sentences
   to carry the idea from, not sentences to paste.
5. Fill `assets/repurposing_brief_template.md` and confirm it with the author
   before drafting.

```bash
python3 tools/linkedin/linkedin-content-repurposer/scripts/repurpose_analyzer.py \
  --input tools/linkedin/linkedin-content-repurposer/assets/sample_thread.txt
```

### Workflow 2 — Check a draft against its source

1. Save the draft as a text file beside the source.
2. Run the fidelity check. A `blocker` means the draft states a figure or
   quotation the source does not contain.
3. Resolve blockers by restoring the source's wording or removing the claim.
   Never resolve one by editing the source to match.
4. Clear the `rework` items: copied sentences, leftover artefacts, an opening
   that talks about where the material came from. Then work through the
   checklist in `references/native-fit-guide.md`.
5. Validate again with `--fail-on blocker` and hand the draft to the author
   only when it exits 0.

```bash
python3 tools/linkedin/linkedin-content-repurposer/scripts/draft_fidelity_check.py \
  --source tools/linkedin/linkedin-content-repurposer/assets/sample_thread.txt \
  --draft tools/linkedin/linkedin-content-repurposer/assets/sample_draft.txt \
  --fail-on blocker
```

The sample draft fails on purpose (exit 1): it changes 12 breakdowns to 9,
adds a percentage and invents a quotation. `assets/sample_draft_clean.txt` is
the same material rebuilt properly and passes with no findings.

### Workflow 3 — Mine a long source for several posts

1. Run the analyser on the article or transcript in JSON form.
2. Read `posts_in_source` and the `units` list. Treat each unit as a candidate
   post with its own single point.
3. For each unit worth using, write one brief. Do not write a "part 1 of 4"
   series; each post must stand alone for a reader who sees only that one.
4. Draft and check each post separately against the full source.
5. Hand the set to planning so the posts are spread across weeks and pillars
   instead of published back to back.

```bash
python3 tools/linkedin/linkedin-content-repurposer/scripts/repurpose_analyzer.py \
  --input tools/linkedin/linkedin-content-repurposer/assets/sample_article.md \
  --format json
```

**Exit-code contract.** Both tools: `0` completed; `1` a finding reached the
`--fail-on` level; `2` a file is missing, unreadable, too short, or (for
`--story-bank`) not a story bank.

## Decision frameworks

### What the Move line means

| Move | When the analyser says it | What to do | Tag |
|------|---------------------------|------------|-----|
| Rebuild in place | Source already sits inside the length band | Keep the length, remake the opening and the joins | [PROVEN] Typical for threads |
| Compress | Source is above the band, one main point | Keep one point, cut the others entirely | [RECOMMENDED] Cutting beats summarising |
| Split | Source is well above the band with several sections | One post per point, each self-sufficient | [RECOMMENDED] |
| Expand | Source is below the band | Add the case, the figure and the stake from the author; do not pad | [EXPERIMENTAL] Needs new material, so the story bank or the author must supply it |

### What may change and what may not

| Element | May change | Must not change |
|---------|-----------|-----------------|
| Opening | Entirely rewritten | The claim it leads to |
| Order | Freely; lead with the outcome if that is stronger | Cause and effect |
| Length | Compressed or expanded | Which facts are stated |
| Sentences | Rewritten in the author's written voice | Meaning |
| Figures | Rounded only if the author approves and says so | Values, units, periods, what they count |
| Quotations | Turned into reported speech | Wording inside quotation marks |
| People named | Removed or anonymised | Added |

### Length and opening defaults

The band of 800 to 1,600 characters and the 200-character opening window are
house heuristics, set as defaults so the tools have something to measure
against. They are not platform limits. Post length limits and where the feed
truncates a post are current as of writing only; verify them in the product,
and override with `--target-min`, `--target-max` and `--opening-chars`.

| Source | Usual starting point |
|--------|----------------------|
| Thread | Already near the band; the work is joins and the opening |
| Talk transcript | Far above; pick one argument from one section |
| Article | Above; split by section, never summarise |
| Newsletter issue | One item from it, not the issue |
| Short note or caption | Below; expand only with the author's own detail |

## Anti-Patterns

### Paste and trim
**Mistake:** The thread is pasted, the numbering deleted, and the last two segments cut to fit.
**Why it happens:** The source already performed somewhere, so changing it feels like risk, and trimming is quick.
**Instead:** Pick the spine, close the source, and write the post from the idea. The fidelity check reports FD-003 when more than half the draft's sentences are verbatim, which is the signature of trimming.

### Summarising the whole piece
**Mistake:** A forty-minute talk becomes "five things I covered at the conference".
**Why it happens:** Every section cost effort to prepare and leaving any out feels like waste.
**Instead:** One post, one point. The other four are four more posts. The analyser's `posts_in_source` and RP-023 exist to make this visible before drafting.

### Improving the numbers
**Mistake:** "12 breakdowns, down from 31" becomes "a 61% reduction", or 12 quietly becomes 9.
**Why it happens:** Percentages sound more authoritative, and small slips enter when a rewrite works from memory of the source.
**Instead:** Carry figures exactly, with their units and periods. A derived figure needs the author's sign-off because they will be the one asked to defend it. FD-001 blocks any number the source does not contain.

### Tidying a quotation
**Mistake:** A remark from the transcript is shortened and sharpened, then left in quotation marks.
**Why it happens:** Spoken sentences are messy and the cleaned version is what the speaker "meant".
**Instead:** Either quote the words as spoken or drop the quotation marks and report it. FD-002 blocks quoted passages that do not appear in the source.

### Narrating the post's history
**Mistake:** "I gave a talk last month and wanted to share the key takeaway here."
**Why it happens:** It feels honest to say where the material came from, and it is an easy first line.
**Instead:** Open on the point. Readers care what you found, not which room you found it in. RP-011 and FD-006 flag this.

### Speaking for the panel
**Mistake:** A co-speaker's best line from a panel transcript appears in the first person in the post.
**Why it happens:** Transcripts flatten speakers together, especially once labels are stripped.
**Instead:** Strip nobody's label until you know whose words each passage is. Use only the author's own remarks; credit anything else by name with consent, or leave it out.

## Files

Tools overview and reference documentation for this skill:

| File | Purpose |
|------|---------|
| `scripts/repurpose_analyzer.py` | Measures a source text, detects its channel, lists the artefacts that will not survive the move, recommends compress, expand, split or rebuild, ranks spine candidates and estimates how many posts the source holds |
| `scripts/draft_fidelity_check.py` | Gate that compares a draft with its source: blocks on new figures and altered quotations, flags copied sentences, leftover artefacts, stale openings and length; optionally reads a story bank |
| `scripts/repurpose_rules.py` | Rule data and text primitives shared by both tools: the rule catalogue, artefact patterns, sentence splitting, figure extraction; `--list-rules` prints the catalogue |
| `references/source-format-playbooks.md` | Per-channel playbooks: thread, talk and video transcript, article, newsletter, short note; what to keep, cut and rebuild in each |
| `references/native-fit-guide.md` | What makes a post read as written for LinkedIn: opening, shape, rhythm, ask, links, with platform mechanics marked as verify-in-product |
| `references/fidelity-rules.md` | The contract between source and draft: figures, quotations, attribution, permission, other people's words, and how the gate enforces each |
| `assets/sample_thread.txt` | Nine-part fictional thread with numbering, a handle, a link, a repost ask and a hashtag cluster |
| `assets/sample_talk_transcript.txt` | Fictional talk transcript with timestamps, speaker labels, filler and slide references |
| `assets/sample_article.md` | Fictional four-section article with headings, a table, a footnote and an image, long enough to split |
| `assets/sample_draft.txt` | Draft made from the thread by paste and trim, with a changed figure and an invented quotation; fails the gate |
| `assets/sample_draft_clean.txt` | The same thread rebuilt properly; passes the gate |
| `assets/repurposing_brief_template.md` | Fill-in brief agreed with the author before drafting: source, rights, point, reader, ask, carry-over list, cut list |
