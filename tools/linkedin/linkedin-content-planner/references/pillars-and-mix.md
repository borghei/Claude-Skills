# Pillars and Mix

How to choose pillars, set their shares, and keep a plan balanced. Everything
quantitative in this document is a planning heuristic chosen to be a sensible
default. None of it is a claim about how any platform ranks posts.

## Contents

1. What a pillar is for
2. The general pillar set
3. Writing your own pillars
4. Setting shares
5. Pairing pillars with asks
6. Pairing pillars with formats
7. How the builder spreads the plan
8. Rebalancing a plan that has drifted
9. Pillar health review
10. Worked example

## 1. What a pillar is for

A pillar is a promise about what a reader will find if they keep reading you.
It does three jobs:

- **For the reader:** it makes you predictable in subject while leaving each
  post free to surprise in content.
- **For the writer:** it turns "what shall I post?" into "which of four things
  is due?", which is a much easier question on a Tuesday morning.
- **For the plan:** it gives the calendar something to balance.

A pillar is not a topic list, a hashtag or a format. "Carousels" is not a
pillar. "Payroll" is too wide to be one. "How shop-floor payroll actually goes
wrong, from cases I handled" is a pillar.

**Use three to five.** With two, the feed reads as one note played twice. With
six or more, no pillar comes round often enough for a reader to recognise it,
and the plan cannot give each one a meaningful share. The builder raises CP-001
outside that range.

## 2. The general pillar set

The built-in general set suits most people who are not founders: employees,
consultants, freelancers, specialists, people looking for their next role.

| Pillar | What goes in it | Default share | Default ask |
|--------|-----------------|---------------|-------------|
| `craft` | How the work is done, taught from your own cases: a method, a check you always run, a mistake you see repeatedly and how to avoid it | 35 | `keep` |
| `field-notes` | First-person episodes: something that happened, what you thought going in, what changed | 30 | `reply` |
| `peers` | Other people: credit for someone's work, a question to the room, a response to something a colleague published | 20 | `pass-on` |
| `offer` | What you sell, are hiring for or are looking for, stated plainly with one way to respond | 15 | `contact` |

Why these four:

- `craft` is why a stranger would follow you. It has the largest share because
  it compounds: useful posts keep being found and saved.
- `field-notes` is why they would trust you. Method without episodes reads
  like a textbook; episodes show the method was earned.
- `peers` stops the feed being a monologue and puts your name in other
  people's conversations.
- `offer` exists because readers cannot act on an offer they never see. It is
  small because every promotional post spends trust the other three earn.

Rename them freely. The names in the config are the names that appear in the
plan, and they must match the story bank's pillar names if a bank is used.

## 3. Writing your own pillars

A pillar statement that works has three parts: a subject, a source and a
reader.

> *[Subject]*, from *[where your knowledge of it comes from]*, for *[who needs
> it]*.

| Weak | Why | Stronger |
|------|-----|----------|
| "Leadership" | No source, no reader, shared with everyone | "Running a depot team through peak season, from eight peaks, for first-time supervisors" |
| "Industry news" | You are not the source | "What a regulation change means on the shop floor, from implementing three of them" |
| "My journey" | Subject is you; the reader is absent | "Going from in-house to independent, for specialists considering it" |
| "Tips" | A format, not a subject | "Checks I run before any pay run goes out" |

Tests to apply to each candidate:

1. **Ten-post test.** Can you list ten posts for it from things that have
   already happened? If not, it is an aspiration, and belongs in the plan only
   after an interview has filled it.
2. **Overlap test.** Would any post fit two pillars equally? Some overlap is
   fine; if most posts fit two, merge them.
3. **Reader test.** Can you name one real person who would want this pillar?
4. **Tension test.** Does the pillar contain at least one thing you got wrong
   or changed your mind about? A pillar of pure success is hard to read.

## 4. Setting shares

Shares are percentages that sum to 100. The builder will not run otherwise; it
does not normalise silently, because a config that sums to 115 means a decision
has not been made.

### Starting points

| Goal | craft | field-notes | peers | offer |
|------|-------|-------------|-------|-------|
| Build a reputation in a specialism | 45 | 25 | 20 | 10 |
| Balanced default | 35 | 30 | 20 | 15 |
| Become known inside a community | 30 | 25 | 35 | 10 |
| Actively selling or hiring this quarter | 30 | 30 | 20 | 20 |

These are starting points to adjust after a month, not recommendations with
evidence behind the exact numbers.

### Guard rails

| Limit | Default | Reason | Flag |
|-------|---------|--------|------|
| Largest pillar | at most 50% of the plan | Beyond half, the other pillars stop registering | CP-002 (error) |
| Promotional posts | at most 1 per week | Two asks for business in a week changes how the rest is read | CP-003 (error) |
| Smallest pillar | at least 1 slot | A pillar with no slot is not in the plan | CP-005 (warn) |
| Drift from target | within 15 points over the plan | Larger drift means the plan is too short for the shares | CP-010 (warn) |

Mark a pillar as promotional with `"promotional": true`. The builder will
avoid placing more than the weekly limit, and reports an error only when the
pillar's share makes that impossible.

### Shares and plan length

Whole posts cannot be divided. With three posts in a one-week plan, shares of
35/30/20/15 become 1/1/1/0 and the fourth pillar is flagged. This is correct
behaviour, not a fault: judge the mix over a month. For a one-week plan, either
accept that one pillar rests or plan the month and read off the first week.

## 5. Pairing pillars with asks

Each post asks one thing of the reader. Four asks cover almost everything:

| Ask | The post is built so the reader will | Shape it implies |
|-----|--------------------------------------|------------------|
| `reply` | Answer or argue | Ends on a real question or a position with an open flank |
| `keep` | Save it to use later | Self-contained, structured, usable without the author |
| `pass-on` | Send it to someone | About something larger than the author; easy to forward with one line |
| `contact` | Message or look at the profile | Names who it is for and how to respond |

Set a default ask per pillar in the config. The builder counts them, and warns
(CP-009) when one ask covers more than the `max_ask_share` of the plan,
because a feed where every post ends in a question, or every post is a
checklist, becomes predictable in the wrong way.

Override a single slot's ask by hand in the weekly sheet when the material
calls for it. A `craft` post about a contested method may well be a `reply`.

## 6. Pairing pillars with formats

Give each pillar a `formats` list of what suits it. The builder only assigns
formats from that list.

| Pillar | Usually suits | Usually does not |
|--------|---------------|------------------|
| `craft` | Text, multi-page document, annotated image | Short video without structure |
| `field-notes` | Text, short talking video | Designed carousel: polish undercuts the episode |
| `peers` | Text, a reshare with your own paragraph | Anything heavily produced |
| `offer` | Text, single image, document for a case study | Long video |

Format names are free text: use whatever you actually make. Format behaviour
on the platform changes; anything you believe about which format travels
furthest is current as of when you learned it, and should be verified in the
product and against your own results.

## 7. How the builder spreads the plan

Knowing the mechanics helps when reading the output.

1. **Slots.** Every posting weekday between the start date and the end of the
   last week becomes a slot, minus skip dates.
2. **Quotas.** Each pillar's share is converted to a whole number of slots by
   the largest-remainder method: floors first, then leftovers to the largest
   fractions, earlier pillars winning ties.
3. **Order.** Slots are filled one at a time. At each slot the pillar that is
   furthest behind an even spread goes next, avoiding the pillar just used
   when another is available, and avoiding a promotional pillar that has
   already reached its weekly limit.
4. **Formats.** The same furthest-behind rule is applied to formats, limited to
   the pillar's allowed list and to weekly production capacity.
5. **Entries.** With a story bank, each slot takes the next ready entry filed
   under its pillar, unused entries first. An entry is used once per plan.
6. **Flags.** The finished plan is checked against the limits.

The process is deterministic: the same config always produces the same plan.
To change the result, change the config.

## 8. Rebalancing a plan that has drifted

Plans drift in predictable ways. The fix is nearly always in the config.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Same pillar twice running (CP-006) | One pillar has a much larger share than the rest | Lower it, or accept and swap two neighbouring slots by hand |
| A pillar never appears (CP-005) | Share too small for the number of slots | Raise the share, lengthen the plan, or fold the pillar into another |
| Format run of three (CP-007) | Pillars restricted to one format each | Widen `formats` on at least one pillar |
| Produced formats cut back (CP-008) | Mix asks for more than capacity | Lower those formats' shares; raise capacity only if the hours exist |
| Slots without entries (CP-012) | Bank thin for that pillar | Interview for it before the plan starts |
| Offer stacked in one week (CP-003) | Offer share too high for the cadence | Lower the share or extend the plan |

Hand-editing the calendar is fine for a single swap. If you find yourself
moving three or more slots, the config is wrong.

## 9. Pillar health review

Run this checklist at the end of each plan period, before building the next.

- [ ] Did every pillar get published at roughly its planned share?
- [ ] Which pillar was easiest to write? Consider raising its share.
- [ ] Which slots were skipped, and which pillar were they? A pillar that keeps
      being skipped is either short of material or not one you want to write.
- [ ] Did any pillar draw the readers you named for it?
- [ ] Is the offer pillar producing any contact at all? If not, look at the
      wording of the offer before raising the share.
- [ ] Has anything changed (role, product, audience) that makes a pillar
      obsolete?

Change at most one pillar per period. Changing several at once makes it
impossible to tell what made a difference.

## 10. Worked example

Ines runs a one-person payroll studio for small manufacturers (fictional). She
wants three posts a week for four weeks and can produce one designed document
a week.

- Pillars: `craft` 35, `field-notes` 30, `peers` 20, `offer` 15 (promotional).
- Posting days Tuesday, Thursday, Friday; conversation Monday and Wednesday.
- One Friday skipped for a client site visit, leaving 11 slots.
- Formats: text 50, document 30 (produced), video 20 (produced).

The builder's quotas are 4, 3, 2 and 2. The plan opens craft, field-notes,
peers, and places the two offer posts in different weeks. The format mix asks
for five produced posts across four weeks; capacity of one a week allows four,
so CP-008 fires. With her story bank attached, CP-012 fires three times: `offer`
has no ready entry for either of its slots, and `craft` and `field-notes` are
each one entry short.

Her decisions: accept four produced posts, and schedule a short interview
session on the offer pillar before week two. Nothing is hand-edited.
