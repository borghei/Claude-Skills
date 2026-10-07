# Founder Pillar Set

An alternative to the general pillar set, for people building a company. The
general set is organised by subject. This one is organised by **reader**,
because a founder's posts are read by a small number of people whose decisions
matter a great deal, and those people want different things.

The shares and stage adjustments below are planning heuristics. They are a
considered default, not a measured optimum.

## Contents

1. Why founders need a different set
2. The three readers
3. The four pillars
4. Angles for each pillar
5. Stage adjustments
6. Launch, fundraise and hiring periods
7. What founders should leave out
8. Founder plan checklist
9. Worked fortnight

## 1. Why founders need a different set

A specialist posting about their field wants to be found by many people with
the same interest. A founder is in a different position:

- **The audience that matters is small.** A handful of investors, a few dozen
  possible hires, some hundreds of plausible buyers.
- **Those readers are checking, not browsing.** They look at the profile before
  a meeting, after an introduction, during diligence. They read several posts
  in a row.
- **The founder is the company's most credible voice and its most biased one.**
  Everything is read as partly promotional, so plain evidence does more than
  enthusiasm.

A subject-keyed plan lets a founder drift into posting only about the product,
which serves none of the three readers well. A reader-keyed plan asks, for
every slot, "who is this one for?"

## 2. The three readers

| Reader | What they are trying to find out | What reassures them | What puts them off |
|--------|----------------------------------|---------------------|--------------------|
| Investor (current or future) | Does this person see the market clearly, and do they learn? | A specific view held with reasons; decisions explained with their trade-offs | Hype, vanity metrics, every week described as a triumph |
| Candidate | What is it like to work there, and is the work real? | Honest detail about how the team builds, what broke, what was fixed | Culture slogans, perks lists, posts that could be about any company |
| Buyer or design partner | Do they understand my problem, and have they solved it for someone like me? | Their own problem described accurately; a comparable customer's outcome | Feature announcements with no problem attached |

Before planning, write down one real person for each reader. If the founder
cannot name one for a given reader, lower that pillar's share.

## 3. The four pillars

| Pillar | Written for | What goes in it | Default share | Default ask |
|--------|-------------|-----------------|---------------|-------------|
| `market-view` | Investors and peers | What the founder believes about the market, the category and the timing, with the experience behind the belief | 25 | `reply` |
| `build-log` | Candidates | How the team works, what shipped, what broke, what was removed | 30 | `keep` |
| `customer-desk` | Buyers | Problems heard first-hand, objections, outcomes for named or anonymised customers | 30 | `contact` |
| `ledger` | All three | One decision: the options, what was chosen, what it cost | 15 | `pass-on` |

Notes on the design:

- There is **no separate promotional pillar**. For a founder, `customer-desk`
  carries the commercial weight, and it does so by describing problems and
  outcomes. If a founder wants explicit launch posts, add an `announce` pillar
  marked `"promotional": true` at 10 and take five points each from
  `build-log` and `customer-desk`.
- `ledger` is the smallest pillar and the most read by investors. It is small
  because good decision posts depend on real decisions, which do not arrive
  weekly.
- `build-log` and `customer-desk` are equal because they are the two pillars a
  founder can always fill: something was built and somebody was spoken to in
  any given week.

Use the set by copying `assets/sample_founder_config.json`, or by putting
`"pillar_set": "founder"` in a config that has no `pillars` key.

## 4. Angles for each pillar

An angle is a way into a post. Each needs a real event behind it; none works as
a template filled with generalities. Pick the angle after you know what
happened, not before.

### market-view

| Angle | The post says | Needs |
|-------|---------------|-------|
| The shared assumption | "Everyone in this category assumes X. Here is the customer conversation that made me stop." | A specific conversation or data point |
| Why now | "This was not buildable three years ago. Here is what changed." | The concrete change: a cost, a rule, a behaviour |
| The customer we turn away | "We do not sell to this kind of company, and here is why." | A real refusal |
| What I got wrong about the market | "Our first plan assumed X. It took N months to see otherwise." | The original plan in the founder's old words |
| The unglamorous dependency | "The category's real bottleneck is a boring thing nobody pitches." | First-hand evidence of the bottleneck |

### build-log

| Angle | The post says | Needs |
|-------|---------------|-------|
| The week's dull fix | "The most valuable thing we shipped this week has no announcement." | What it was, how long it took, what it unblocked |
| Done by hand | "People assume this part is automated. Two of us do it manually every morning." | The honest reason it is still manual |
| What we removed | "We deleted a feature that some customers used. Here is how that went." | The numbers and the complaints |
| How we decide | "This is the actual process by which something gets onto the roadmap." | One real example run through it |
| The outage | "We were down for N minutes on Tuesday. Here is the timeline." | Timeline, cause, what changed |
| A first for the team | "Our fourth hire did something I could not have done." | Their consent and a specific thing |

### customer-desk

| Angle | The post says | Needs |
|-------|---------------|-------|
| The sentence that changed the roadmap | "A customer said one thing on a call that reordered our quarter." | The sentence, near-verbatim, with permission or anonymised |
| The objection we could not answer | "A prospect asked a question last month and I had no good reply." | The question and what was done about it |
| One account, before and after | "Here is one clinic's Monday morning before and after." | A measured difference and the customer's agreement |
| Why they nearly did not buy | "The deal almost fell through over something we thought was minor." | The real reason |
| The problem under the request | "They asked for a report. What they needed was to stop being phoned at night." | The request and the discovery |
| Lost deal | "We lost this one, and they were right to choose the other option." | Honesty and no bitterness |

### ledger

| Angle | The post says | Needs |
|-------|---------------|-------|
| The decision and the rejects | "We had three options. Here is why we took the second and what the other two would have cost." | The actual options considered |
| A price change | "We changed pricing in the spring. Here is what happened to sign-ups and to complaints." | Figures the founder is willing to publish |
| The next unit of money | "If we had one more salary to spend, this is where it would go and why not elsewhere." | A real trade-off under discussion |
| The hire we delayed | "We waited six months longer than advised to hire for this role." | What the delay cost and saved |
| What we stopped measuring | "We removed a number from the weekly review." | The number and the behaviour it was causing |

Do not publish figures an investor, board or customer has not agreed to make
public. When in doubt, describe the shape of the decision without the numbers.

## 5. Stage adjustments

| Stage | market-view | build-log | customer-desk | ledger | Reasoning |
|-------|-------------|-----------|---------------|--------|-----------|
| Idea, no product | 35 | 25 | 25 (as research conversations) | 15 | No customers yet; write up discovery calls as findings, not as wins |
| Product, first customers | 25 | 30 | 30 | 15 | The default |
| Hiring hard | 20 | 40 | 25 | 15 | Candidates need more evidence of how the team works |
| Raising | 30 | 25 | 25 | 20 | Investors read `market-view` and `ledger` most closely |
| Scaling sales | 20 | 25 | 40 | 15 | Buyers need comparable outcomes |

Change the shares for a defined period and change them back. A founder feed
that is permanently in fundraising mode reads as one.

## 6. Launch, fundraise and hiring periods

The temptation in any big moment is to suspend the plan and post only about
the moment. Do the opposite: keep the cadence and tell the moment through the
pillars.

| Moment | market-view | build-log | customer-desk | ledger |
|--------|-------------|-----------|---------------|--------|
| Product launch | Why this needed to exist now | The hardest part of building it | The customer problem it came from | What was cut to ship on time |
| Funding announcement | What the round is a bet on | What the team will now build first | Which customers made the case | How the amount was decided |
| Key hire | Why this role matters in this market | What they will own | What customers will notice | Why now and not earlier |

One explicit announcement post is enough. The rest of the fortnight explains
it from four sides, and each of those posts stands on its own for a reader who
missed the announcement.

## 7. What founders should leave out

- **Metrics that only go up.** If a number is shared only when it rises,
  readers learn to discount it. Share a number you would also share when it
  fell, or do not share it.
- **Customer names without consent.** Including in a positive story.
- **Anything under negotiation.** Rounds, acquisitions, partnerships,
  disputes. If a story bank is in use, put these in its no-go list.
- **Competitors by name.** Describe the approach you disagree with, not the
  company.
- **Team members' mistakes.** The founder's own are fair game. Other people's
  are theirs to tell.
- **Borrowed lessons.** A post that could have been written by someone who
  never ran this company is not worth a slot.

## 8. Founder plan checklist

- [ ] One real person named for each of the three readers
- [ ] Shares set for the current stage, with a date to review them
- [ ] Two-week plan built; no slot without a real event behind it
- [ ] `customer-desk` slots have consent or are anonymised
- [ ] `ledger` slots contain nothing the board or investors have not cleared
- [ ] No more than one explicit announcement in the period
- [ ] Conversation days reserved, with investors', candidates' and customers'
      posts on the list of whose to read
- [ ] A fortnightly fifteen-minute review booked to rebuild the next plan

## 9. Worked fortnight

Dariusz runs Pellwick, scheduling software for independent veterinary clinics
(fictional). Three posts a week, Monday, Wednesday and Thursday; conversation
on Tuesday and Friday; one designed image a week at most.

The builder gives six slots with quotas of 1, 2, 2 and 1:

| Date | Pillar | Angle chosen | Event behind it |
|------|--------|--------------|-----------------|
| Mon, week 1 | `build-log` | Done by hand | Two people still reconcile double-booked surgeries each morning |
| Wed, week 1 | `customer-desk` | The problem under the request | A clinic asked for a report and needed fewer night calls |
| Thu, week 1 | `market-view` | The shared assumption | Clinics do not want fewer no-shows as much as predictable afternoons |
| Mon, week 2 | `ledger` | The decision and the rejects | Chose per-clinic pricing over per-vet after modelling three options |
| Wed, week 2 | `build-log` | What we removed | Dropped the waiting-room display nobody had configured |
| Thu, week 2 | `customer-desk` | The objection we could not answer | A practice manager asked what happens when the internet goes down |

`market-view` lands at one post against a target of 25 percent, which is
within tolerance for six slots. Over a second fortnight the quotas even out.
