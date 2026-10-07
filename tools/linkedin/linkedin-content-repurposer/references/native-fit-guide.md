# Native-Fit Guide

What makes a repurposed post read as though it was written for LinkedIn, and
how to get there from a source that was written for somewhere else.

**On platform mechanics.** This guide avoids stating how the feed ranks,
truncates or distributes posts, because those behaviours are not published in
verifiable detail and change without notice. Where a mechanic matters to a
decision, it is marked *verify in the product*: look at how your own recent
posts are displayed and how they performed, and trust that over any rule,
including the defaults in this skill.

## Contents

1. What "native" means here
2. The reader's situation
3. Opening
4. Body shape
5. Rhythm and paragraphing
6. Stakes and voice
7. The ask
8. Links
9. Tags, mentions and formatting
10. Length
11. Native-fit checklist
12. Before and after

## 1. What "native" means here

A post is native when a reader cannot tell it started life somewhere else. That
has little to do with tricks of formatting and a great deal to do with three
things:

- it was plainly written **to be read here**, alone, with no prior context;
- it is **one thing**: one point, one voice, one ask;
- it sounds like **a person at work talking to peers**, not a broadcast.

Everything below follows from those.

## 2. The reader's situation

A useful mental picture, offered as an assumption to test, not a finding:

- The reader did not choose this post. It appeared between other things.
- They see the first lines before deciding whether to read on. *Verify in the
  product* how many characters are shown before the cut on the devices your
  readers use; it has varied over time and by layout.
- They are at or near work, reading as a professional, with their name
  attached to anything they react to.
- They know nothing about the talk, the thread or the article this came from.

Compare with the source's reader: a conference audience that chose the
session, a subscriber who opened the email, a follower mid-scroll through a
thread. Each of those had context this reader lacks.

## 3. Opening

The opening is the part of a source that survives least often, because it was
written to do a different job: announce a thread, greet a room, introduce an
article.

**What a working opening does.** It gives the reader a concrete reason to
continue: something that happened, a number that needs explaining, a belief
about to be reversed. It can be understood with no context. It does not
describe the post ("In this post I'll share...") or its history ("Last week I
spoke at...").

**Where to find it.** Rarely at the start of the source. Look at the
analyser's spine candidates: the highest-scoring sentence typically holds a
figure, the author and a turn, and it is typically in the middle or near the
end, where the source delivered its payoff.

| Source opening | Why it fails here | Rebuilt from the spine |
|----------------|-------------------|------------------------|
| "A thread on the dullest change I ever made..." | Announces a format | "We nearly bought a system to predict bus breakdowns. Then I read 31 breakdown reports by hand." |
| "Thanks for having me. Today I want to talk about onboarding." | Greets a room | "41 of 48 new hires told us the same thing: the week they needed help was week three." |
| "In this article I want to walk through our rota changes." | Describes a document | "For a year, our Saturday support rota was whoever replied last in the group chat." |

The tools treat the first 200 characters as the opening window by default.
That number is a working assumption so there is something to check; change it
with `--opening-chars` once you have looked at your own posts.

Detailed scoring of opening lines is outside this skill.

## 4. Body shape

Most sources have a shape that fits their channel. A post usually wants a
simpler one. Three shapes cover most repurposed material:

| Shape | Order | Suits |
|-------|-------|-------|
| Finding first | Result, then how it was found, then what to do with it | Threads and articles with a clear outcome |
| Reversal | What I believed, what happened, what I believe now, what that means for you | Talks, where the speaker narrated a change of mind |
| Case | One situation in sequence: before, the change, after | Sections of articles describing a single intervention |

Pick the shape from the material. If the source contains "I used to think",
it is a reversal. If it has a before-and-after pair of figures, finding first.

What a post body rarely needs from the source: a preview of what is coming, a
recap of what was said, definitions the reader already has, the second and
third example of the same thing.

## 5. Rhythm and paragraphing

- **Short paragraphs.** One to three sentences. A paragraph is a unit of
  thought, and on a narrow screen long ones look like a wall. The fidelity
  check notes any paragraph above ninety words.
- **Blank lines between paragraphs.** The post editor preserves them; the
  source's markup (headings, bullets, tables) may not render. *Verify in the
  product* what formatting is supported before relying on anything beyond
  plain line breaks.
- **Vary sentence length.** Transcripts run long; threads run uniformly short.
  Neither reads well in bulk. Mix them.
- **Not one sentence per line throughout.** A column of single-sentence lines
  reads as a formula. Use a one-line paragraph for the sentence that deserves
  it and let the rest group naturally.

## 6. Stakes and voice

A source written to inform (an article, a talk) often leaves the author out.
A post reads better with the author in it, for a simple reason: the reader is
deciding whether to trust this, and "I did this and here is what happened" is
easier to weigh than "organisations should consider".

- Keep or restore the first person. The analyser notes a source with none
  (RP-021).
- Keep the part where something was at risk or went wrong. Sources polished
  for publication tend to have smoothed it out; transcripts tend to still
  have it.
- Keep one phrase in the author's actual words. Do not manufacture one.
- Do not add feelings the source does not express. "I was devastated" is a
  claim about a person and needs their say-so like any other fact.

## 7. The ask

One post, one ask. The source's ask belonged to its channel (repost,
subscribe, come to the next session) and does not transfer.

| If the post is | A fitting ask |
|----------------|---------------|
| A method or check | Nothing, or "try it on one case this week" |
| A reversal or opinion | A real question you want answered, specific enough that the answers will differ |
| A case with an outcome | "How do you handle this?" narrowed to the exact situation |
| An offer | One way to respond |

A question nobody could answer wrongly ("Agree?", "Thoughts?") is not an ask.
Ending without an ask is fine when the post is complete.

## 8. Links

Sources are full of links: to the article, the recording, the slides, the
sign-up page.

How the feed treats posts that contain external links is widely discussed and
not something this guide can verify. Opinions differ and the behaviour may
have changed since any given claim was made. So decide on editorial grounds:

1. **Does the post stand without the link?** It must. If the post is only a
   pointer, it is not yet a post.
2. **Does the link help the reader who wants more?** If so, include it where
   it reads naturally, typically at the end.
3. **Where?** In the body, or in a comment the author adds themselves
   afterwards. Both are common practice. Pick one, keep to it for a month,
   and compare your own results.

The analyser reports links as a note (RP-004), not a fault, because the
decision is the author's.

## 9. Tags, mentions and formatting

- **Hashtags.** Clusters carried over from other networks read as residue
  (RP-003). If you use tags at all, a couple of specific ones is plenty.
  Whether they affect distribution: *verify in the product*.
- **Mentions.** Handles from another network do not work here and look wrong
  (RP-002). Mention a person only when the post genuinely concerns them and
  they would be glad to be notified.
- **Markdown.** Headings, tables, code fences and image syntax will appear as
  literal characters (RP-010). Convert to sentences.
- **Emoji and symbols.** Follow the author's own habit in what they write
  themselves. Do not add any that the author would not use.

## 10. Length

The default band of 800 to 1,600 characters is a house heuristic: long enough
for a case with its evidence, short enough to be one thing. The platform's own
limit on post length is higher; *verify in the product* what it currently is.

Length follows from content, not the reverse:

- Under the band and complete: fine. Do not pad.
- Over the band because there are two points: split.
- Over the band with one point: look for the second example, the recap and
  the caveat nobody needs.

Override the band with `--target-min` and `--target-max` if the author's own
posts reliably work at another length.

## 11. Native-fit checklist

- [ ] A stranger could read the opening with no context and want the next line
- [ ] The opening does not mention the source, greet anyone or describe the post
- [ ] One point; other points saved for other posts
- [ ] First person present; something was at stake
- [ ] Every figure matches the source in value, unit and period
- [ ] No numbering, handles, timestamps, slide references or headings remain
- [ ] Paragraphs are short and separated by blank lines
- [ ] One ask, or none
- [ ] Link placement decided on purpose
- [ ] The fidelity check exits 0 with `--fail-on blocker`
- [ ] The author has read it and recognises it as theirs

## 12. Before and after

Source (thread segments 5 to 7, fictional):

> 5/ We changed one thing: the night fitter reads the defect cards at 10pm,
> before the morning run-out, instead of the office reading them the next
> afternoon.
>
> 6/ Second half of 2024: 12 roadside breakdowns. Same fleet, same routes,
> same budget. No new system.
>
> 7/ I used to think our problem was that we did not have enough data. We had
> the data. We had it sixteen hours too late.

Rebuilt:

> So we changed one thing. The night fitter now reads the cards at 10pm,
> before the morning run-out.
>
> In the second half of 2024 we had 12 roadside breakdowns. Same fleet, same
> routes, same budget.
>
> For years I believed we were short of data. We were not. We had it sixteen
> hours late.

What changed: numbering gone, the seams between segments closed, context that
each segment repeated removed. What did not: 10pm, 12, the second half of
2024, sixteen hours, and the claim.
