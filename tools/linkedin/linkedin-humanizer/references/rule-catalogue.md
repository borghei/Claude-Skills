# Rule Catalogue

The complete set of rules applied by `scripts/tell_audit.py`, in the order the
tool evaluates them. Each entry gives what the pattern looks like, why a reader
notices it, a before-and-after pair, and the circumstances in which the original
text should stay.

All allowances and weights are editorial heuristics chosen for feed-length
posts of roughly 80 to 400 words. They are starting points to tune, not
measurements. The example texts are invented.

## Contents

1. How the tiers work
2. Remove tier (RM-01 to RM-07)
3. Reduce tier (RD-01 to RD-19)
4. Review tier (RV-01 to RV-07)
5. How load is calculated
6. Rules deliberately left out

---

## 1. How the tiers work

The tiers answer one question: *what should happen to this text?*

| Tier | Answer | Counting | Gate |
|------|--------|----------|------|
| Remove | Delete it or fill it. There is no version of this that a person meant to publish. | Every hit | One hit fails |
| Reduce | Bring it back under the allowance. Once is writing; five times is a signature. | Hits above the allowance, multiplied by the rule weight | Fails above `--max-load` |
| Review | Look at it and decide. The pattern has a long human history. | Listed as notes | Never fails |

Two consequences follow. First, a draft can pass with reduce-tier findings on
display, and that is intended: the allowance is the rule. Second, the review
tier must be requested (`--tier review`) because showing it by default trains
people to delete things that were fine.

---

## 2. Remove tier

Residue of the tool that produced the draft, or of the template it was built
from. Weight is irrelevant here: one hit blocks.

### RM-01 Tool residue token

**Looks like:** citation markers and reference tokens that chat tools attach to
sourced sentences, bracketed source numbers with daggers, or lenticular
brackets around a source name.

**Why it matters:** these strings have no meaning to a reader and no person
types them. They are the clearest evidence that text was pasted unread.

| Before | After |
|--------|-------|
| Return rates fell after the redesign 【source 4】. | Return rates fell after the redesign. *(Then check the claim: what was the rate, and whose data is it?)* |

**Keep when:** never. Also treat the hit as a prompt to verify the sentence it
was attached to, since the citation it pointed to is now gone.

### RM-02 Assistant preamble

**Looks like:** "Sure, here's a draft…", "Certainly!", "Here is a LinkedIn post
about…", "Great question."

**Why it matters:** it is the wrapper of a reply, addressed to the person who
asked for the draft.

| Before | After |
|--------|-------|
| Here's a post about your Q3 hiring results:<br><br>We hired eleven people in Q3… | We hired eleven people in Q3… |

**Keep when:** never. After deleting it, re-run the audit: the line that is now
first has not yet been checked by the opener rule.

### RM-03 Assistant sign-off

**Looks like:** "Let me know if you'd like me to adjust the tone", "I hope this
helps", "Feel free to tweak", "Would you like me to add hashtags?"

**Why it matters:** an offer to revise is not part of the post.

**Fix:** delete the sentence. Nothing replaces it.

### RM-04 Model self-reference

**Looks like:** "As of my last update", "As an AI", "I don't have access to
real-time data", "I cannot verify".

**Why it matters:** the text is describing its own author, and the author is
not the person whose name is on the post.

| Before | After |
|--------|-------|
| As of my last update, the regulation had not yet taken effect. | The regulation takes effect on 1 January. *(Only if the author has checked. Otherwise cut the sentence.)* |

### RM-05 Unfilled placeholder

**Looks like:** `[Your Company]`, `[insert link]`, `{name}`, `{{topic}}`, `XX%`,
`TK`, filler Latin.

**Why it matters:** a slot shipped without its value. It is also the single
most screenshot-worthy mistake a post can contain.

| Before | After |
|--------|-------|
| At [Your Company], we cut onboarding time by XX%. | At Tidewell we cut median onboarding time from 9 days to 2. |

**Keep when:** never. Do not guess the value. If the author cannot supply it,
remove the sentence.

### RM-06 Unrendered markup

**Looks like:** `**bold**`, lines starting with `#` and a space, `[text](url)`
links, code fences.

**Why it matters:** the post composer displays these characters literally (as
of writing; verify in the product). Asterisks around a phrase tell the reader
the text came from somewhere that renders them.

| Before | After |
|--------|-------|
| `**Speed matters** — customers who see value early stay` | Customers who printed a label on day one were still with us at day ninety. |

Note the rewrite is not "Speed matters: customers who…". Stripping the
asterisks from a slide heading leaves a slide heading. See RD-17.

### RM-07 Leftover option label

**Looks like:** "Option A:", "Version 2:", "Hook 1 —", "Title:", "Subject:".

**Why it matters:** the draft was one of several alternatives and its label
came along.

**Fix:** delete the label. If more than one option is present, the author has
not yet chosen; ask.

---

## 3. Reduce tier

Each rule has an **allowance** (hits per post that are simply normal) and a
**weight** (how much each hit beyond the allowance adds to the load).

### RD-01 Stock vocabulary — allowance 1, weight 1

**Looks like:** abstract business words that could be moved to any other
sentence without changing its meaning: leverage, utilise, harness, unlock,
elevate, empower, streamline, foster, robust, seamless, comprehensive, crucial,
pivotal, holistic, synergy, cutting-edge, game-changing, transformative,
landscape, ecosystem, paradigm, nuanced, multifaceted, impactful, actionable,
supercharge, skyrocket, fast-paced, best-in-class, next-level, deep dive, move
the needle, double down, unpack, thought leader.

**Why readers notice:** none of them names a thing. A sentence built from them
can be agreed with and cannot be checked.

| Before | After |
|--------|-------|
| We leveraged customer insights to streamline the checkout experience. | We watched 30 people try to pay. Nineteen stopped at the delivery-date picker, so we removed it. |

**Keep when:** the word is a literal term of art (an insurer's "comprehensive
cover", a hardware "ecosystem" of named devices) or part of a product name.

### RD-02 Empty intensifier — allowance 2, weight 1

**Looks like:** truly, incredibly, fundamentally, essentially, ultimately,
literally, absolutely, extremely, undoubtedly, significantly, deeply, genuinely.

**Why readers notice:** the adverb claims an importance the sentence has not
shown.

| Before | After |
|--------|-------|
| This was a truly transformative quarter for the team. | We shipped the two features that had been on the roadmap since 2023. |

**Keep when:** the word is doing literal work ("literally" as opposed to
figuratively; "significantly" in a statistical statement with the test named).

### RD-03 Contrast frame — allowance 1, weight 2

**Looks like:** "X isn't just a Y. It's a Z." "It's not about features, it's
about outcomes." "Not because A, but because B." "Less about X, more about Y."
"Stop doing X. Start doing Y."

**Why readers notice:** it denies a claim nobody in the room made in order to
make the following claim sound like a discovery. It is the frame people name
first when asked what generated writing sounds like.

| Before | After |
|--------|-------|
| Onboarding isn't a checklist. It's a relationship. | The accounts that renewed had spoken to the same person at least three times in their first month. |

**Keep when:** the denied view is real and attributable: "Our board thought
this was a pricing problem. It was a packaging problem." One per post.

### RD-04 Question-and-answer bridge — allowance 0, weight 2

**Looks like:** "The result?" "The catch?" "Here's the thing." "Plot twist."
"Why? Because…" "Sound familiar?" "And guess what?"

**Why readers notice:** it is a pause for effect before a sentence that did not
need one.

| Before | After |
|--------|-------|
| We moved the pricing page above the fold. The result? Demo requests doubled. | We moved the pricing page above the fold and demo requests went from 14 a week to 31. |

**Keep when:** almost never. A question the author was really asked, with the
asker identified, is a different pattern and does not match this rule.

### RD-05 Triple list — allowance 1, weight 1

**Looks like:** "faster, cheaper, and simpler"; "clarity, focus and momentum".

**Why readers notice:** three is the default list length of generated prose,
and the third item is usually the weakest because it was added for the sound.

| Before | After |
|--------|-------|
| The new process is faster, clearer, and more scalable. | The new process takes four days, and a new hire can run it from the written steps. |

**Keep when:** there are three things. One triple per post passes without
comment in the reduce tier and is noted in the review tier as RV-02.

### RD-06 Staccato fragments — allowance 2, weight 1

**Looks like:** sentences of one to three words used for emphasis. "Simple.
Clear. Repeatable." "That's it." "Every time."

**Why readers notice:** a run of them has a drumbeat that prose written at
speed does not have.

| Before | After |
|--------|-------|
| We tried it. It failed. Badly. So we tried again. | The first version failed badly enough that we lost two pilot customers, and the second took until April. |

**Keep when:** the author's past posts show the habit (the fingerprint will
protect the rule). List items, labels ending in a colon and "P.S." lines are
excluded from the count.

### RD-07 One-word paragraph — allowance 1, weight 1

**Looks like:** a paragraph consisting of "Exactly." or "Still." or "Nothing."

**Why readers notice:** white space is emphasis. Spending it on one word, more
than once, is a visible technique.

**Fix:** attach the word to the paragraph before it, or delete it and see
whether anything is lost.

**Keep when:** once, when the word is the news ("Sold.").

### RD-08 Announced candor — allowance 0, weight 2

**Looks like:** "Let me be honest", "I'll be real with you", "Honestly?",
"Real talk", "Full transparency", "Hard truth", "Not gonna lie", "Confession:".

**Why readers notice:** the announcement stands in for the disclosure. It also
implies the surrounding text is something less than honest.

| Before | After |
|--------|-------|
| I'll be honest: this launch was hard. | We launched three weeks late and refunded eleven pre-orders. |

**Keep when:** never as an opener. Mid-post, in an author who talks this way,
check the fingerprint before removing.

### RD-09 Stock opener — allowance 0, weight 3 (first line only)

**Looks like:** "In today's…", "In a world where…", "In the age of…", "Let's
talk about…", "I'm thrilled / excited / humbled to…", "Have you ever…",
"Picture this", "We've all been there".

**Why readers notice:** the first line is the only part of the post everyone
sees. A stock one is recognised before it is read.

| Before | After |
|--------|-------|
| I'm thrilled to announce that I'm joining Bramblecroft as Head of Data. | I start at Bramblecroft on Monday as Head of Data. The first job is a pricing model nobody trusts. |

**Keep when:** never. This is the heaviest reduce-tier rule because the cost is
paid by the whole post.

### RD-10 Stock closer — allowance 0, weight 2 (last two lines only)

**Looks like:** "What do you think?", "Thoughts?", "Agree?", "Tag someone who
needs this", "Repost if…", "Follow for more", "Let that sink in", "Read that
again", "Comment X below and I'll send…".

**Why readers notice:** it asks for engagement without giving the reader
anything specific to respond to.

| Before | After |
|--------|-------|
| What do you think? | If you've removed an onboarding step and activation got worse, which step was it? |

**Keep when:** never in the stock wording. A post may also simply end.

### RD-11 Dash density — allowance 1 per 100 words (minimum 1), weight 1

**Looks like:** em or en dashes, or a spaced double hyphen, appearing more often
than about once every hundred words.

**Why readers notice:** at that rate the dash stops marking an aside and
becomes the way every sentence is assembled.

**Fix:** keep the dash that does the most work. Convert each of the others by
function:

| The dash is… | Replace with |
|--------------|--------------|
| joining a trailing clause | a comma |
| introducing a consequence or list | a colon |
| wrapping an aside on both sides | brackets |
| none of these | rewrite the sentence |

Never a full stop: "We tried it — it failed" becoming "We tried it. It failed."
trades one finding for RD-06.

**Keep when:** the author's fingerprint shows a comparable rate. The sample
author runs at about one per hundred words, so the sample voice file protects
this rule.

### RD-12 Participle opener — allowance 1, weight 1

**Looks like:** "Building trust early, teams create momentum." "Opening a second
warehouse, the company doubled capacity."

**Why readers notice:** the sentence starts on an action with no actor, then
supplies a vague one after the comma.

| Before | After |
|--------|-------|
| Reducing friction at signup, we saw activation climb. | Activation went from 31% to 44% after we cut the signup form to two fields. |

**Keep when:** once, where the action is the subject of the sentence.

### RD-13 Signpost phrase — allowance 0, weight 1

**Looks like:** "It's important to note that", "It's worth mentioning", "That
said,", "In conclusion", "To sum up", "At the end of the day", "When it comes
to", "Moreover", "Furthermore", "Additionally,", "Needless to say".

**Why readers notice:** these are essay connectives. In a 200-word post they
narrate a structure that is too short to need narrating.

**Fix:** delete. If the two sentences no longer connect, the order is wrong.

### RD-14 Noun stack — allowance 2, weight 1

**Looks like:** "the implementation of the solution", "the optimisation of our
processes", "the alignment of stakeholders".

**Why readers notice:** verbs have been turned into nouns, which removes the
person who did the thing and adds four words.

| Before | After |
|--------|-------|
| The implementation of the new workflow led to a reduction of errors. | After we switched workflows, errors fell from 40 a month to 6. |

**Keep when:** it is the fixed name of something.

### RD-15 Uniform sentence length — fires once, weight 1

**Looks like:** six or more full sentences whose word counts all sit within a
few words of each other.

**Why readers notice:** people writing quickly produce a long explanatory
sentence, then a short reaction. Evenness reads as assembled.

**Fix:** join two related sentences with a clause that carries the reason. Do
this once or twice. Do not alternate long and short through the whole post; a
regular alternation is as mechanical as regular sameness.

### RD-16 Nothing only the author could know — allowance 1 missing anchor, weight 2

**Looks like:** a draft with fewer than two of: a figure, a named person,
company or place, a first-person statement.

**Why readers notice:** they do not notice a missing thing; they notice that
they have read this post before, under other names.

**Fix:** ask the author for one number with what it counts and one name. The
tool reports which anchors are missing. If the author has neither, shorten the
post to what is true.

**Keep when:** a two-line reshare caption.

### RD-17 Label-and-colon reveal — allowance 1, weight 1

**Looks like:** lines beginning "Lesson:", "The takeaway:", "Bottom line:",
"Pro tip:", "Key insight:", "My advice:".

**Why readers notice:** it is slide formatting in a medium without slides.

| Before | After |
|--------|-------|
| Bottom line: invest in onboarding. | If I had one more engineer I'd put them on the first ten minutes of the product. |

### RD-18 Hedge stack — allowance 1, weight 1

**Looks like:** "may potentially", "could possibly", "arguably", "in many ways",
"to some extent", "it could be argued".

**Why readers notice:** two hedges on one claim mean the writer has not decided
whether to make it.

**Fix:** commit, or say exactly what is unknown: "We have six weeks of data, so
this could still be seasonal."

### RD-19 Vocabulary cluster — allowance 0, weight 3

**Looks like:** three or more RD-01 words inside a single paragraph.

**Why readers notice:** at that density the paragraph is all register and no
content.

**Fix:** do not edit the paragraph. Replace it. Ask what happened, to whom, and
how it was measured, and write those three things.

| Before | After |
|--------|-------|
| We leveraged a comprehensive, holistic framework to streamline onboarding and unlock seamless outcomes. | We made the carrier-rates table optional and pre-filled two fields from the postcode. It took four days. |

---

## 4. Review tier

Shown only with `--tier review`. None of these affects the exit code, and each
has a respectable human use.

| Rule | Pattern | The concern | The case for leaving it |
|------|---------|-------------|-------------------------|
| RV-01 | A single dash, within the allowance | Some readers treat any long dash as a giveaway | Writers have used it for centuries; a post with none looks scrubbed |
| RV-02 | The one triple the allowance permits | Third item may be padding | Sometimes there are three things |
| RV-03 | Passive constructions | Can hide who acted | Correct when the actor is unknown or beside the point |
| RV-04 | Curly quotes and apostrophes | Occasionally read as a paste | Every phone keyboard and word processor produces them |
| RV-05 | Words that were early giveaways (delve, tapestry, realm, testament, myriad, embark, navigate) | Still on many people's lists | Often literal ("navigating the harbour"); now avoided by generators as well |
| RV-06 | Semicolons | Unusual in feed writing | Some authors use them habitually |
| RV-07 | 120 or more words with no contraction | Reads over-edited or generated | Formal announcements; writers who never contract |

Act on a review note when (a) the author asks for the strictest pass, or (b)
the note points at a real problem (the passive is hiding the actor the post is
about). Otherwise read and move on.

---

## 5. How load is calculated

For each reduce-tier rule:

```
excess = max(0, hits - allowance)
load   = min(6, excess x weight)        # one rule cannot contribute more than 6
```

The habit load is the sum across rules. The gate fails when any remove-tier
rule fired or when the load exceeds `--max-load` (default 6).

| Load | Verdict | Meaning |
|------|---------|---------|
| 0 | clean | Nothing above allowance |
| 1 to half the limit | touch up | A habit or two; safe after a read-through |
| up to the limit | edit | Fix the flagged lines |
| above the limit | rework | Paragraph-level rewriting needed |

Rules listed in a voice file's `protected_rules` are displayed with the note
"kept: author habit" and contribute zero. Remove-tier rules cannot be protected.

---

## 6. Rules deliberately left out

- **A score for "how generated" the text is.** The tool reports patterns, not a
  probability. Nothing here estimates authorship.
- **Sentence-length variance targets.** RD-15 flags extreme uniformity only.
  Chasing a variance number produces the alternating cadence that is its own
  pattern.
- **Reading-ease formulas.** They reward short words and short sentences, which
  is the direction over-editing already pushes.
- **Emoji.** Handled by `scripts/emoji_audit.py` with its own rules (EM-01 to
  EM-08); see `emoji-patterns.md`.
- **Hashtags, links, length, the fold.** Publishing mechanics belong to the
  drafting gate in `linkedin-post-writer`.
