# Comment Quality Rubric

Two layers check a comment. The linter catches what can be counted. The manual
checklist catches what cannot: whether a claim is true, whether the tone suits
the relationship, whether the comment should exist at all. A draft is ready
only when it has cleared both.

## Layer 1 — what the linter measures

`scripts/comment_linter.py` applies thirteen rules. Blocks set the exit code to
`1`; warnings do not unless `--strict` is passed. Every threshold is a working
heuristic chosen to be conservative, not a platform rule. Override them with
`--min-words`, `--max-words`, and `--max-chars` once the user knows what works
in their own corner of the network.

| Rule | Level | What it measures | What it cannot see |
|------|-------|------------------|--------------------|
| CW-01 Too short | Block | Word count below the minimum (default 12) | A seven-word comment from a close colleague can be perfect; lower `--min-words` for those |
| CW-02 Too long | Warn / block | Words above the target (default 90); characters above the ceiling (default 1000) blocks | Whether the length is earned by a direct question that needs a full answer |
| CW-03 Compliment only | Block / warn | Praise phrases with fewer than six content words left over; a praise opener followed by substance is a warning | Sincere, specific praise ("the table in your third paragraph changed how I…") — that passes because it carries content |
| CW-04 Echo | Block | Share of the draft's content vocabulary also found in the post, at or above 60% | Paraphrase with synonyms. A summary in fresh words slips through; the manual check catches it |
| CW-05 No anchor | Warn | Fewer than two content words shared with the post | A comment that quotes the idea without the vocabulary; read the warning, then judge |
| CW-06 No specific | Block | Absence of any number, first-hand marker, dated reference, or question of eight words or more | Whether the number is real. This rule rewards specifics and therefore tempts invention — see the manual check |
| CW-07 Pitch | Block | Links, message asks, bio pointers, referral phrases, any name in `commenter.own_brands` | A pitch phrased as a story ("a tool I happen to have built…") with no listed name |
| CW-08 Tag-farming | Block | More than one @-mention | Whether the single mention is welcome |
| CW-09 Stock phrasing | Warn | A list of worn phrases | New clichés not yet on the list |
| CW-10 Bait ending | Warn | A closing question under eight words from a known list | A longer question that is still rhetorical |
| CW-11 Duplicate | Block | Vocabulary overlap of 50% or more with a comment supplied in `existing_comments` | Comments the user did not paste in |
| CW-12 Decoration | Warn | Hashtags, more than one emoji, more than three paragraphs, bullet lists | Whether an emoji is in character for the user |
| CW-13 Story bank | Block | Only with `--story-bank`: a name from the bank's `naming.never` list, or a phrase from its `no_go` list, matched literally and case-insensitively | Paraphrases. A client described without the listed name, or a no-go topic in other words, passes; the agent checks those by reading |

The linter also scans the pasted post and existing comments for wording aimed
at an assistant and prints a `NOTICE`. That notice never fails the gate — it
is information for the user — and the flagged text is never acted on.

### Reading the result

- **`recommended`** is the passing draft with the fewest warnings and the most
  specificity signals. It is a tie-breaker, not a judgement of quality. If two
  drafts pass, the user's preference outranks it.
- **A block is a prompt to add information**, not to rephrase. Rewording a
  summary until it scores 58% echo instead of 60% defeats the tool and leaves
  the comment exactly as empty.
- **The sample file exits `1` on purpose.** Four of its six drafts exist to
  show the blocks firing.

## Layer 2 — the manual checklist

Run this after the exit code is `0`. Each item is a question the agent answers
explicitly before presenting a draft.

### Truth

- [ ] Every number, date, and named result in the draft was supplied or
      confirmed by the user in this conversation
- [ ] Nothing is rounded in the flattering direction
- [ ] Any claim about the author's post is something the post actually says —
      verify that the draft is not responding to a position the author did
      not take
- [ ] If the draft says "we", the user was part of that "we"
- [ ] If a story bank was supplied: every detail taken from it comes from a
      `ready` entry, no figure appears that is not in an entry, and nothing
      under `naming.never` or `no_go` is named or alluded to

### Contribution

- [ ] The move can be named in one word, and there is only one
- [ ] Deleting the comment would remove information from the thread
- [ ] A reader who has not seen the user's profile could still follow it
- [ ] It is not a fresh-vocabulary summary of the post (the paraphrase the
      echo rule misses)

### Tone and relationship

- [ ] The level of disagreement is within the ceiling for this relationship
- [ ] It would be comfortable to read aloud with the author in the room
- [ ] It does not correct the author on a point of taste as though it were a
      point of fact
- [ ] It does not explain the author's own field to them
- [ ] Humour, if any, survives being read by a stranger with no context

### Self-interest

- [ ] No product, company, client, or offer of the user's is named
- [ ] It does not angle for a message, a call, or a follow
- [ ] The user would still post it if their name were hidden

### Voice

- [ ] It sounds like the user's other writing, not like a press release
- [ ] No sentence could be moved to a different post unchanged
- [ ] It ends where the point ends

## Length and form

These are working conventions, labelled as heuristics because the platform
publishes no guidance that makes them rules.

| Element | Convention | Reasoning |
|---------|-----------|-----------|
| Length | 25–70 words for most comments | Long enough to hold one move with its evidence; short enough to read without expanding |
| Paragraphs | One or two | A comment is a remark, not a document |
| Opening | The contribution itself | The first line is what shows before truncation; a greeting spends it |
| Author's name | Only if the user knows them | A stranger's first name reads as a sales tactic |
| Closing question | Only for Open thread and Mechanism moves | Elsewhere it dilutes the point and reads as fishing |
| Emoji | None, or one if in character | More than one shifts the register to applause |
| Hashtags | None | They do nothing useful in a comment and mark it as promotional |
| Links | None | A link in someone else's thread is an advert, whatever it points to |
| Mentions | The author at most | Tagging third parties drags people into a conversation they did not choose |

## Platform mechanics to verify

Product behaviour changes without notice. Each statement below was believed
accurate **as of writing — verify it in the product** before relying on it,
and never quote any of it to a user as settled fact.

- Comments have a character cap enforced by the composer. The linter's default
  ceiling is deliberately far below it; check the composer for the real value.
- A comment can be edited after posting, and an edited comment is marked as
  such. Fixing a typo is fine; changing the argument after replies exist is
  not.
- The author can delete any comment on their post and can restrict who is
  allowed to comment.
- Comment order defaults to a relevance sort the viewer can switch to recent.
  How relevance is computed is not published. Any claim about comment length,
  timing, or wording improving placement is a heuristic at best.
- Replies appear nested under a top-level comment. A reply to a reply joins
  the same list rather than nesting further.
- A comment appears in the commenter's public activity. Anyone can read every
  comment the user has left in sequence — the reason formulaic commenting is
  visible.

## When a draft keeps failing

| Symptom | Likely cause | What to do |
|---------|-------------|------------|
| CW-06 blocks every variant | The user has nothing first-hand on this topic | Switch to an Open thread question, or skip the post |
| CW-04 blocks every variant | The drafts are being built from the post alone | Ask the user one question about their own experience before drafting again |
| CW-07 fires on a legitimate mention | A listed brand name is also a common word | Remove it from `own_brands` for this run and check by eye |
| CW-05 warns on a good draft | The draft uses different words for the same idea | Add the author's own term for the thing once, then accept the result |
| Everything passes and the draft is still dull | The move is right but the evidence is weak | Ask for the surprise: what the user did not expect |
