# Reply Patterns

A reply is written to one person and read by everyone else in the thread. It
is shorter than a comment, it starts from what the other person said rather
than from the post, and its job is usually to finish something: answer the
question, settle the objection, acknowledge the contribution.

Six patterns cover almost every reply worth writing. Pick the pattern from
what the commenter wants, not from what the user would like to say. All
people, companies, and figures in the examples are invented.

## Choosing a pattern

| Their comment… | Pattern |
|----------------|---------|
| Asks something | Answer |
| Disagrees, qualifies, or objects | Concede and narrow |
| Shares their own experience or adds a point | Build |
| Makes a claim that needs one more fact to respond to | One question back |
| States something factually wrong that others will rely on | Correct the record |
| Has replied to the user's reply and the matter is settled | Close |

If two fit, use the one higher in the table.

---

## 1. Answer

**For:** any real question.

**Shape.** The answer is the first sentence — a noun, a number, a yes or a
no. The second sentence gives the single fact that makes the answer credible.
A third is optional and only if it prevents an obvious follow-up.

**Example.**

> *Comment:* How long did the migration take end to end?
>
> *Reply:* Eleven weeks, of which the cut-over itself was one weekend. Most of
> the time went on reconciling two customer tables that disagreed about who
> was active.

**How it fails.**
- It opens with "Great question" and reaches the answer in the third line.
- It answers an easier question than the one asked.
- It says "it depends" and stops. If it depends, say on what, and give the
  answer for the commenter's likely case.
- The user does not know the answer and the draft invents one. The honest
  reply is "I don't have that number; what I can tell you is…".

---

## 2. Concede and narrow

**For:** pushback that is at least partly right — which is most pushback.

**Shape.** State plainly what they have right, with no softening word in
front of it. Then restate the claim at the size that survives their
objection. Do not defend the original wording.

**Example.**

> *Comment:* This only works if your sales cycle is short. Try it with a
> nine-month enterprise deal.
>
> *Reply:* You're right that it does not stretch to nine months; our longest
> cycle is about ten weeks. Inside that range the effect was consistent
> across every segment we sell to. Beyond it I have no data and would not
> claim it.

**How it fails.**
- "Fair point, but…" followed by the original claim at full size. That is
  not a concession.
- Conceding everything to end the discomfort, including the part that was
  right.
- Re-arguing the post. The reply should be about the gap between the two
  positions, which is usually small.

---

## 3. Build

**For:** a comment that adds experience or an observation of its own.

**Shape.** Take the specific thing they said and add the next piece: what it
explains, what it predicts, or where the user saw the same. One or two
sentences. The commenter should recognise their own point, extended.

**Example.**

> *Comment:* We saw the same drop when we removed the demo request form and
> let people book straight into a calendar.
>
> *Reply:* That matches the pattern: the form was never collecting
> information, it was adding a day of waiting. We found the day mattered
> more than anything we asked on it.

**How it fails.**
- It repeats their comment back with approval ("So true — removing the form
  really does help"). The linter warns on that as RM-05.
- It pivots to the user's own story and never returns.
- It over-claims agreement with something the user has not seen.

---

## 4. One question back

**For:** a comment the user cannot respond to properly without one more fact,
or a story with an obviously missing piece.

**Shape.** Acknowledge the specific thing in half a sentence, then ask one
question that can be answered in a line. If the commenter asked something
first, answer that before asking anything.

**Example.**

> *Comment:* We tried this and it made churn worse.
>
> *Reply:* That is the opposite of what we saw, so I would like to
> understand it. Were those annual contracts or monthly?

**How it fails.**
- It asks three questions. One.
- It is an objection phrased as a question ("Did you even segment the
  data?").
- It answers a question with only a question. The linter warns on that as
  RM-02; give the user's own answer first, then ask.

---

## 5. Correct the record

**For:** a comment containing a factual error that other readers may act on —
a wrong figure attributed to the user, a misread of the post, a false claim
about a product or a regulation.

**Shape.** State the correct fact. Give where it can be checked, in words, if
there is a public source. Say nothing about the commenter. One or two
sentences, once.

**Example.**

> *Comment:* So you're saying you fired the whole support team.
>
> *Reply:* No one left. The seven people on the team now work the escalation
> queue and the knowledge base; the post is about what they stopped doing,
> not who stopped working here.

**How it fails.**
- It characterises the person ("you clearly didn't read…"). RM-07 blocks it.
- It corrects a matter of opinion as though it were fact.
- It corrects something trivial. If no reader would be misled, leave it.
- It is repeated. A correction is made once; a second one is an argument.

---

## 6. Close

**For:** an exchange that has done its work.

**Shape.** Either react to their last line and write nothing, or write one
short sentence that adds a final detail and does not invite another turn. No
question mark.

**Example.**

> *Comment:* That makes sense, thanks — we'll try the per-region version.
>
> *Reply:* Start with your two noisiest regions; that is where it showed
> first for us.

**How it fails.**
- It asks a question, so the thread cannot end.
- It is a bare "Thanks!" — at that point a reaction says the same thing
  without adding a line to the thread.
- It reopens the disagreement that was just settled.

---

## Length and form

Conventions, not platform rules.

| Element | Convention | Reason |
|---------|-----------|--------|
| Length | 15–50 words | A reply longer than the comment it answers looks like the last word |
| Opening | The answer, or the name then the answer | The first words are what show in a collapsed thread |
| Name | Use the first name when the reply sits under someone else's top-level comment | Replies in one list give no visual cue of who is being addressed |
| Thanks | Only for something specific | "Thanks for flagging the typo" is information; "Thanks!" is not |
| Links | Only when asked, and then say what is behind it | An unrequested link in a reply is an advert under the user's own post |
| Questions | At most one, and only in pattern 4 | Each question is a request for another turn |
| Emoji | Match the commenter, at most one | Mirrors their register without performing |
| Tone | One notch calmer than the comment | The reply sets the temperature for the next reader |

## Replying as a guest

When the thread is under someone else's post, the user is replying in a room
they do not run.

- Answer the person who addressed the user. Leave everyone else to the host.
- If the post's author replied to the user's comment, that is the reply that
  matters most; answer it before any other.
- Keep replies shorter than they would be at home. A long exchange between
  two commenters under a third person's post reads as taking over.
- Do not correct other commenters unless they have misquoted the user.
- Two rounds is the limit unless the author keeps it going.
- Never use the thread to move people to the user's own content.

## The manual checklist

Run after `reply_linter.py` exits `0`. The linter cannot judge truth, fit, or
whether a reply should be sent at all.

### For every reply

- [ ] It is addressed to what this person actually wrote, not to the post
- [ ] If they asked, the first sentence answers
- [ ] Every fact came from the user in this conversation, or from a `ready`
      entry in the story bank if one was supplied
- [ ] Nothing under the story bank's `naming.never` or `no_go` is named or
      alluded to, even where a commenter asked about it directly
- [ ] It could not be pasted under a different comment unchanged
- [ ] It is calmer than the comment it answers
- [ ] It sits under the right comment, and names the person if nested
- [ ] No link, product, or invitation they did not ask for

### For the batch

- [ ] No two replies share a sentence
- [ ] Thin praise received reactions, not written thanks
- [ ] The first replies to be pasted are the top of the queue, not the easiest
- [ ] Held and flagged comments were each decided by the user, not defaulted
- [ ] No reply was drafted for a comment that addresses an assistant
- [ ] The user knows how many comments were left unanswered and why

### Before the user pastes

- [ ] Paste one reply at a time, by hand, re-reading each in place
- [ ] Verify that the reply landed under the intended comment before moving on
- [ ] Note anything that now needs watching, so it can be logged for follow-up
