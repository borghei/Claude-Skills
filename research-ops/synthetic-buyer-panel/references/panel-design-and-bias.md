# Panel Design and Bias

A synthetic buyer panel is a fast way to surface objections, segment
differences and wording before any money is spent. It is not a sample of real
people. This reference covers how to build a profile that produces a useful
panel, the biases every simulated panel carries, and how to read the output
without overclaiming.

## 1. What a simulated panel is good and bad at

| Good at | Bad at |
|---------|--------|
| Listing the objections a type of buyer is likely to raise | Predicting the share of real people who will buy |
| Showing which segments or behaviours react differently to the same pitch | Estimating demand volume or market size |
| Generating the words buyers might use for a doubt | Producing quotes that can be used as testimonials |
| Stress-testing a pitch for confusing or missing information | Detecting brand, location or timing effects it was not told about |
| Producing a first price corridor to test | Setting the final price |

Use the panel to decide what to test with real people, never to replace that test.

## 2. Building the profile

**Target.** One sentence naming who, where and what they do today. "Renters aged
25 to 55 within a 15-minute walk of Market Street who buy cleaning products at
the supermarket" gives the agents something to reason from. "Everyone who
cares about the planet" gives them nothing and the answers come back generic.
The deal tool rejects targets under five words.

**Segments.** Two to four groups that plausibly behave differently: life stage,
income band, company size. Each has a share and an income range; give an age
range per segment when life stage drives behaviour. Shares must add to 1.0.

**Behaviours.** Four to eight buying habits that cut across segments: a weekly
big shop, a price comparer, a brand loyalist, an online orderer. Behaviours are
usually more predictive than demographics, so spend the effort here.

**Objections.** The real doubts this buyer has before they hear the pitch,
in their words. Pull them from reviews of competitors, support tickets, sales
call notes or interviews where possible. At least three; five to eight is
better. Each buyer is dealt one as the doubt already in their head, spread
evenly so no objection is over-represented.

**Contexts.** Concrete everyday details that make a buyer specific: their route
to work, household size, schedule. They make answers less generic and more
varied.

**Ground the profile in evidence.** Mark which parts come from real data and
which are assumptions, and show the profile to the person who knows the customer
before dealing. A wrong profile makes the whole panel wrong, with confidence.

## 3. Writing the pitch buyers see

Show buyers the same pitch a passer-by would meet: what it is, what it costs,
where it is sold and any launch deal, in a short plain paragraph.

- Include the price and unit. Without them the price questions are meaningless,
  and the deal tool refuses to deal.
- No superlatives. "The best refill shop in the city" primes agreeable answers;
  the deal tool warns on hype words.
- Nothing the business cannot deliver on day one.
- Every buyer sees the same pitch, word for word. Never tailor it per buyer.

## 4. Known biases and how the tools counter them

| Bias | What happens | Counter-measure |
|------|--------------|-----------------|
| Agreeableness | Model personas say yes more than people | Brief states passing is normal; tally warns above 60% buy rate; read rate as a ceiling |
| Homogeneity | Many answers sound the same | Concrete contexts and doubts per card; tally warns when over 30% of reasons repeat word for word |
| Correlated error | All agents share the same model priors | Never treat n as independent samples; no confidence intervals are reported |
| Hallucinated facts | Agents invent features, reviews or competitors | Brief forbids facts beyond the pitch; moderator rejects answers that cite them |
| Moderator leakage | The person running the panel fills gaps | Tally never fills missing answers; coverage below 90% fails |
| Pitch priming | Hype or leading language raises buy rate | Deal tool warns on hype words; pitch reviewed before dealing |

## 5. Choosing panel size

| Purpose | Size | Why |
|---------|------|-----|
| First look at an idea | 20 | Enough to list objections; segment rates are noise |
| Comparing segments or behaviours | 40-60 | At least 8-10 buyers per group to see a difference |
| Comparing two pitches or prices | 40-60 per variant, same seed | The same cards see each variant, so the difference is the pitch |
| Anything above 200 | Rarely worth it | Cost grows linearly; correlated error does not shrink |

Use the same seed when comparing variants. Different seeds deal different
buyers and mix pitch effects with panel effects.

## 6. Reading the tally

1. **Reliability first.** Check coverage, invalid answers and the duplicate
   share. If a reliability check fails, fix the run before reading anything else.
2. **Differences, not levels.** A segment 30 points above the average is a lead
   to follow up. The overall buy rate is the least trustworthy number on the page.
3. **Pass reasons.** The top two reason codes are the panel's main output. Each
   should map to an action: price, access, trust, habit, need or a competing
   alternative.
4. **Flips.** What would turn a no into a yes is the most actionable list: it is
   a set of candidate changes to the offer, channel or price.
5. **Price corridor.** The median "bargain" to median "getting expensive" range
   is a starting corridor for a real price test. It is not a recommendation on
   its own.

## 7. From panel to real test

Every panel ends with a question for real people. Turn the top pass reason into
a real-world test: a priced pre-sale, a two-price landing page, a pop-up with
the changed offer. Record the panel result as simulated evidence and the real
test result separately; only the real test confirms demand.

## 8. Ethics and honesty

- Never present panel answers as customer quotes, reviews or testimonials.
- Never use the panel to claim market validation in a deck or to an investor
  without saying, in the same sentence, that the buyers were simulated.
- Do not build personas that stereotype protected groups; segment on behaviour,
  life stage and context rather than on ethnicity, religion or similar traits.
