# Survey Design Methodology for Market Questions

Reference for designing, fielding, and QA-ing survey instruments that answer
market questions — category demand, willingness to pay, switching intent,
segment sizing. Written for the operator running the study, not the
psychometrician.

## 1. Decide whether a survey is the right instrument


Surveys measure **stated** attitudes and **recalled** behaviour. They do not
measure future behaviour, and they measure past behaviour only as well as
respondents remember it.

| Question type | Survey suitability | Better alternative |
|---------------|--------------------|--------------------|
| Category incidence ("what share have this problem") | **[PROVEN]** Strong | — |
| Current behaviour and volumes ("how many hours, how often") | **[PROVEN]** Strong for recent, bounded periods | Log data if you have it |
| Firmographic / segment sizing | **[PROVEN]** Strong | Registry data if it exists |
| Awareness and consideration set | **[RECOMMENDED]** Good | — |
| Relative preference between defined options | **[RECOMMENDED]** Good with forced trade-offs | Conjoint or discrete choice |
| Willingness to pay | **[EXPERIMENTAL]** Weak in absolute terms | Price testing in a live funnel |
| Intent to purchase | **[EXPERIMENTAL]** Weak — chronically overstated | Pre-order or pilot commitment |
| Reasons for past behaviour | Weak — post-hoc rationalisation | Interviews with behavioural probes |

The single most damaging misuse is treating stated purchase intent as a demand
forecast. Stated intent overstates realised purchase substantially across
categories. Use intent only to **rank** options against each other within the
same instrument, never as an absolute rate.

## 2. Sampling


### Frame

The sampling frame is the list you can actually draw from. It is almost never
the population, and the gap between them is your coverage error.

Document three things for every study:

1. **Target population** — who the finding is meant to describe
2. **Frame** — who could actually be contacted
3. **Known exclusions** — who is in the population but not the frame

A finding generalises to the frame, not the population. Write the frame
definition into the report so nobody over-generalises later.

### Required sample size

For a proportion at a given margin of error, using the normal approximation:

```
n0 = z^2 * p * (1 - p) / e^2
n  = n0 / (1 + (n0 - 1) / N)        # finite population correction
```

Where `z` is the confidence-level score (1.96 at 95%), `p` is the expected
proportion (use 0.5 for the conservative maximum), `e` is the margin of error as
a decimal, and `N` is the frame size.

Reference values at 95% confidence, p = 0.5:

| Frame size | ±10% | ±5% | ±3% |
|-----------|------|-----|-----|
| 200 | 66 | 132 | 169 |
| 500 | 81 | 218 | 341 |
| 1,000 | 88 | 278 | 517 |
| 5,000 | 95 | 357 | 880 |
| 20,000 | 96 | 377 | 1,014 |
| 100,000 | 96 | 383 | 1,056 |
| 1,000,000+ | 97 | 385 | 1,066 |

Two things this table teaches:

- **Frame size barely matters above about 20,000.** The precision is driven by
  the number of completes, not by what fraction of the population they are. A
  sample of 400 is as precise for a market of 50,000 as for one of 5 million.
- **Precision is quadratic in cost.** Halving the margin of error quadruples the
  required sample. This is why ±5% studies cost roughly four times a ±10% study.

### Choosing the margin

**[RECOMMENDED]** Field at ±10% for directional category questions — does this
problem exist, roughly how widespread is it, which segment is worst affected.
Reserve ±5% for decisions where the confidence band itself drives the choice,
typically pricing and packaging.

Ask the question that settles it: "If the answer came back at the top of the
band instead of the bottom, would I make a different decision?" If no, buy the
cheaper precision.

### Subgroup analysis destroys precision

The whole-sample margin does not apply to subgroups. A 400-person sample split
across four segments gives roughly ±10% per segment, not ±5%.

Rule: decide your subgroups **before** fielding and size for the smallest one
you intend to report. If you need segment-level conclusions, either boost the
sample or quota-sample the segments deliberately.

### Response rates and invitation volume

```
invitations_needed = required_completes / expected_response_rate
```

Planning ranges, which vary enormously by relationship and mode:

| Mode / relationship | Typical response rate |
|---------------------|----------------------|
| Own customers, incentivised, short instrument | 15-35% |
| Own customers, no incentive | 5-15% |
| Purchased B2B panel | Managed by vendor to quota |
| Cold list, professional audience | 1-4% |
| In-product intercept | 2-10% of exposed |
| Association or community list with endorsement | 8-20% |

Check the arithmetic against the frame. Needing 3,000 invitations from a frame
of 2,000 is a design failure, not a fielding problem — it means relaxing the
margin, changing mode, or abandoning the subgroup analysis.

## 3. Non-response bias


Non-response bias is a larger threat than sampling error in almost every
practical study, and unlike sampling error it does not shrink with sample size.

The people who answer a survey about a problem are systematically more likely to
have that problem. This inflates every incidence estimate, often severely.

Mitigations, in order of effectiveness:

1. **[PROVEN] Compare respondents to the frame on known attributes.** If you
   know firmographics for the whole frame, compare respondent distribution to
   frame distribution. Divergence quantifies the bias.
2. **[PROVEN] Field in waves and compare early to late respondents.** Late
   respondents resemble non-respondents. If the estimate moves between waves,
   extrapolate the trend rather than reporting the pooled figure.
3. **[RECOMMENDED] Neutral recruitment framing.** Invite to "a study about how
   clinics run scheduling," not "a study about scheduling problems."
4. **[RECOMMENDED] Weight to known frame margins** where the frame distribution
   is documented. Do not weight on more than two or three variables — weights
   above about 4x on any cell make the estimate unstable.

## 4. Question construction


### The core rule

**Ask about behaviour and its cost; derive the attitude.** An instrument built
from behavioural items with numeric answers is far harder to bias than one built
from agreement scales.

| Weak (attitudinal) | Strong (behavioural) |
|--------------------|----------------------|
| "How valuable would automated reporting be?" | "In the last full month, how many hours did your team spend building reports manually?" |
| "How satisfied are you with your current system?" | "In the last 12 months, how many times did you evaluate an alternative system?" |
| "Would you consider switching?" | "When does your current contract renew, and has a replacement been discussed internally?" |
| "How important is compliance to you?" | "Which of these standards are you contractually required to meet?" |

### Wording defects and their fixes

| Defect | Example | Fix |
|--------|---------|-----|
| **Leading** | "How valuable would X be?" | Presupposes value. Ask about the current cost of not having X. |
| **Loaded adjectives** | "our seamless new dashboard" | Strip every evaluative adjective from the stem. |
| **Double-barrelled** | "How satisfied are you with speed and accuracy?" | Split into two items. One answer cannot serve two constructs. |
| **Absolutes** | "Do you always reconcile at end of day?" | Replace with a frequency scale — absolutes push respondents to the safe middle. |
| **Assumed behaviour** | "How do you track compliance?" | Add a screening item establishing they track it at all. |
| **Unbounded recall** | "How often do you usually...?" | Bound it: "in the last 30 days, how many times...". |
| **Jargon** | "What is your ARR per FTE?" | Use the respondent's vocabulary, not yours. |
| **Overlong stems** | 40-word items | Cap at about 25 words. Comprehension and completion both fall past that. |
| **Negation** | "Would you not consider...?" | Never negate a stem. Double negatives in scale items produce reversed answers. |

### Scales

- **Use 5 or 7 points.** Below 5 is too coarse to detect movement between waves;
  above 7 exceeds reliable discrimination and adds noise, not resolution.
- **Balance the anchors.** Equal numbers of positive and negative options. An
  unbalanced scale ("Good / Very Good / Excellent") manufactures positive
  results and is the single most common instrument defect in commercially
  motivated research.
- **Label every point, not just the ends.** Fully-labelled scales are
  interpreted more consistently across respondents.
- **Include a midpoint** for genuinely bipolar attitudes. Forcing a choice on a
  respondent who has no opinion adds noise, not information.
- **Always offer an escape** — "Don't know" or "Not applicable" — kept separate
  from the scale and excluded from means. Without one, respondents guess, and
  guesses are indistinguishable from data.
- **Keep the direction consistent** across the instrument. Flipping polarity
  mid-survey to "catch inattentive respondents" mostly catches attentive ones.

### Order effects

- **Funnel from general to specific.** Specific items prime the general ones
  that follow, not the other way round.
- **Unaided before aided.** Ask "which systems have you evaluated?" before
  showing a list, or you will measure recognition of your list.
- **Randomise option order** within any list over about five items to defuse
  primacy bias, and randomise blocks of non-dependent items.
- **Sensitive items last.** Compensation, budget, and dissatisfaction items
  raise abandonment; place them after the data you most need.
- **Demographics and firmographics last**, except those needed for screening.

### Length

Completion falls sharply with length. Practical planning limits:

| Mode | Target length | Hard ceiling |
|------|---------------|--------------|
| In-product intercept | 1-3 items | 5 items |
| Email to customers | 5-8 minutes | 12 minutes |
| Incentivised B2B panel | 10-15 minutes | 20 minutes |
| Interview-administered | 20-30 minutes | 45 minutes |

Estimate roughly 20-30 seconds per closed item and 60-90 seconds per open item.
Every open-text item is a real cost to both respondent and analyst — cap at two
or three per instrument and place them where the answer will actually be read.

## 5. Screening and quality control


### Screener design

The screener qualifies respondents into the frame. Two failure modes:

- **Too loose** — unqualified respondents contaminate the estimate.
- **Too transparent** — respondents infer the qualifying answer and give it,
  particularly on incentivised panels.

Defences:

1. **Obscure the target.** Embed the qualifying option among plausible
   alternatives rather than asking directly.
2. **Never signal the target in the invitation.** "A study for clinic managers
   with 3+ chairs" tells a panel respondent exactly what to claim.
3. **Verify with a consistency item.** Ask a related factual question later; a
   respondent who claims 5 chairs and then reports 1 staff member is failing.
4. **Include an impossible option** in one list — an invented system name. Any
   respondent selecting it is disqualified.

### Field QA

Screen out on these before analysis:

- **Speeders** — completion under roughly a third of median time
- **Straight-liners** — identical response across a full grid of items
- **Consistency failures** — contradictory answers on linked items
- **Impossible-option selectors** — the trap item above
- **Duplicate fingerprints** — same respondent identifier submitting twice

Report the exclusion count and reasons in the methods section. A study that
reports 400 completes without saying how many were screened out is not
reproducible.

## 6. Analysis discipline


- **Report n for every figure**, including subgroup figures. A percentage
  without an n is not a finding.
- **Report the margin of error** on headline figures, and the wider subgroup
  margins where you report subgroups.
- **Do not report subgroups under about 30 respondents.** Show the count and say
  it is indicative only.
- **Do not compare two subgroups whose confidence bands overlap** and call it a
  difference. Overlapping bands mean the difference is not established.
- **Exclude escape options from means**, and report the escape rate separately.
  A 40% "don't know" rate is itself the most important finding in the item.
- **Distinguish stated from observed** in every sentence of the writeup. "62% of
  respondents said they would consider switching" is a defensible sentence.
  "62% of the market will switch" is not.

## 7. Willingness-to-pay methods


Direct WTP questions overstate realised price substantially. Where a pricing
decision genuinely needs survey input, use a structured method.

| Method | Mechanism | Strength | Weakness |
|--------|-----------|----------|----------|
| **Direct open WTP** | "What would you pay?" | Simple | Least reliable; anchors on nothing |
| **Price ladder** | Would you buy at X? then X±step | Simple, gives a curve | Sensitive to the starting anchor |
| **Van Westendorp** | Four price-perception questions | Gives an acceptable range, easy to field | Measures perception, not demand; no volume |
| **Gabor-Granger** | Purchase intent at several prices | Yields a demand curve | Intent overstates purchase |
| **Discrete choice / conjoint** | Forced choices among feature-price bundles | **[RECOMMENDED]** Best survey-based method; trade-offs are realistic | Complex to design and analyse |

**[PROVEN]** No survey method beats observed behaviour. If you can test price in a
live funnel, do that instead. Use survey WTP to narrow the range you will test,
never to set the price.

Whatever method you use, report WTP as a range with the method named. A single
WTP figure without its method is uninterpretable.

## 8. Instrument testing before field


Never field an instrument that has not been through all three of these. Each
catches problems the others do not.

### Cognitive interviews (5-8 people from the target population)

Have participants think aloud while answering. You are testing comprehension, not
collecting data.

- Do they interpret each item as intended?
- Do they have the information the item asks for?
- Does the response set contain their actual answer?
- Ask them to restate each item in their own words — divergence from your intent
  is the defect.

This is the single highest-yield instrument test and the most frequently skipped.
It routinely surfaces items where every respondent would have answered a
different question than the one you thought you asked.

### Soft launch (10% of target sample)

Field to a small tranche, then stop and inspect before releasing the rest.

- Completion rate and median duration against estimate
- Drop-off point distribution — a spike marks the offending item
- Straight-lining and speeding rates
- Open-text quality — gibberish indicates a panel-quality problem
- Whether screener qualification rates match expectation

### Technical check

- Every skip and display rule exercised
- Piped text renders correctly in every branch
- Mobile rendering — a large share of responses arrive on phones
- Accessibility: keyboard navigation and screen-reader labels
- Data export produces the variables the analysis plan needs

That last item saves real pain. Discovering after fielding that a grid exported
in a shape your analysis cannot use means re-coding under time pressure.

## 9. Weighting


Weighting corrects known imbalance between the sample and the frame. It cannot
correct unknown imbalance, and it is frequently over-applied.

Rules:

- **Weight only on variables where you know the frame distribution.** Weighting to
  a guess adds error while appearing to remove it.
- **Weight on few variables.** Two or three. Each added variable creates smaller
  cells and more extreme weights.
- **Cap extreme weights.** Any respondent weighted above about 4x is
  disproportionately driving the estimate. Cap and report the cap.
- **Report both weighted and unweighted results.** A large divergence is itself a
  finding about your sample.
- **Report the effective sample size.** Weighting reduces it — sometimes
  substantially — and the margin of error should be computed on the effective n,
  not the raw count.

That final point is routinely omitted. A weighted sample of 400 with an effective
n of 260 has the margin of error of 260, and reporting the 400-based margin
overstates precision.

## 10. Reporting


### What every survey report must state

- Target population, frame, and known exclusions
- Recruitment mode and dates fielded
- Invitations sent, completes, and response rate
- Screening exclusions with counts and reasons
- Weighting variables, source of targets, and effective sample size
- Margin of error at the headline level and for each reported subgroup
- The instrument itself, as an appendix

The instrument appendix is the one most often dropped and the one that makes the
study reproducible. Any finding whose exact wording cannot be checked is a
finding that cannot be properly evaluated.

### Language discipline

| Do not write | Write |
|--------------|-------|
| "62% of the market will switch" | "62% of respondents said they would consider switching" |
| "Users want X" | "Respondents ranked X first among the five options presented" |
| "Demand is strong" | "71% (±5%) reported the problem occurring at least weekly" |
| "Segment A prefers B" | "Segment A ranked B higher than segment C did; the difference is outside the margin (n=140, n=155)" |

The pattern: **name the respondents, not the market; name the stated behaviour,
not the inferred intention; attach the n and the band to every number.** Survey
findings drift toward overstatement in retelling, and precise language in the
report is the only thing that slows it down.

## 11. Pre-field checklist


- [ ] The market decision this survey feeds is written at the top of the instrument
- [ ] Target population, frame, and known exclusions are documented separately
- [ ] Required sample computed for the **smallest subgroup** to be reported
- [ ] Invitation volume checked against frame size and expected response rate
- [ ] Every item asks about behaviour or fact where possible, attitude only where necessary
- [ ] No evaluative adjectives anywhere in any stem
- [ ] No double-barrelled items; no negated stems; no absolutes
- [ ] All scales are 5-7 points, balanced, fully labelled, with an escape option
- [ ] Unaided items precede aided items
- [ ] Option order randomised on lists over five items
- [ ] Sensitive and demographic items are last
- [ ] Instrument timed by a live pilot with 5+ people from the target population
- [ ] Screener does not reveal the qualifying answer
- [ ] Trap item and consistency item both present
- [ ] Analysis plan written before fielding, including which subgroups get reported
