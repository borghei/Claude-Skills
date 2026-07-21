# Method Selection Guide

Every discovery method with its cost, sample, output, and — the part usually
left out — the questions it structurally cannot answer. Read this when someone
has requested a method before anyone has written the question down.

## 1. The selection sequence


Work these in order. Skipping step 1 causes most method errors.

1. **Write the question in interrogative form.** If it begins "should we," it is
   a decision, not a research question. Rewrite as: what would I need to know to
   decide?
2. **Classify the question.** Generative, evaluative, comparative, descriptive,
   prioritisation, desirability, or diagnostic.
3. **Check reversibility.** Reversible decisions usually deserve an experiment,
   not a study.
4. **Check what evidence you already own.** Support tickets, sales call
   recordings, session replays, and churn surveys are free and already
   collected. Mining them first routinely answers 30-50% of the question and
   sharpens what remains.
5. **Check the binding constraint** — timeline, participant access, or traffic.
   The constraint, not the ideal, determines the method.
6. **Pick the cheapest method that answers the question.** Not the most rigorous
   available; the cheapest that clears the evidence bar for this decision.

## 2. Question types


| Type | Form | What it needs |
|------|------|---------------|
| **Generative** | "How do people currently...?" | Depth. Small n, rich observation. |
| **Evaluative** | "Can people do X with this?" | Task performance. Small n, structured tasks. |
| **Comparative** | "Does A beat B?" | Controlled contrast. Large n or randomisation. |
| **Descriptive** | "How many / how often?" | Coverage. Full population or a representative sample. |
| **Prioritisation** | "Which of these matters most?" | Forced trade-offs across many respondents. |
| **Desirability** | "Would people want this?" | Revealed preference, not stated. |
| **Diagnostic** | "Why did this metric move?" | Quant to localise, then qual to explain. |

The single most useful heuristic: **quant tells you what and how many; qual
tells you why and how.** Interviews cannot tell you what share of users are
affected — six people cannot represent a proportion. Surveys cannot tell you why
— people confabulate reasons for their own behaviour with impressive fluency.

## 3. Method profiles


### Semi-structured interviews

- **Answers:** generative, diagnostic
- **Sample:** 6-8 per segment, run to theme saturation
- **Elapsed:** 5-10 days including recruiting
- **Output:** behaviour narratives, workarounds, the language users actually use
- **Cannot answer:** how many, how often, which of two designs performs better
- **Failure mode:** drifting into a feature-request session. Anchor every probe
  to a specific past occurrence.
- **[PROVEN]** The default generative method. Highest information per unit cost
  in discovery.

### Contextual inquiry

- **Answers:** generative
- **Sample:** 5-6 per segment
- **Elapsed:** 10-15 days — scheduling on-site or screen-share time is the cost
- **Output:** the actual workflow including the parts people never mention
- **Cannot answer:** anything quantitative; anything about infrequent events
- **Failure mode:** the observer effect. People perform an idealised version of
  the work. Mitigate by asking them to complete real, already-queued tasks.
- **[PROVEN]** Superior to interviews when the workflow involves tools, physical
  artefacts, or steps the participant considers too obvious to describe.

### Moderated usability test

- **Answers:** evaluative
- **Sample:** 5-8 per segment
- **Elapsed:** 5-8 days
- **Output:** task success rate, points of failure, and the reasoning behind them
- **Cannot answer:** whether anyone wants the thing; preference between designs
- **Failure mode:** leading the participant through the task. If you speak
  during a task, you have contaminated it.
- **[PROVEN]** Five participants surface the majority of severe usability
  defects. The marginal defect found by participants 9-12 rarely justifies the
  cost.

### Unmoderated usability test

- **Answers:** evaluative
- **Sample:** 12-20
- **Elapsed:** 2-4 days
- **Output:** task completion, time on task, recorded sessions
- **Cannot answer:** why a participant did something unexpected
- **Failure mode:** an ambiguous task prompt that you cannot clarify mid-session
- **[RECOMMENDED]** Use when the flow is simple and the question is "does this
  work," not "why does this fail."

### A/B experiment

- **Answers:** comparative, desirability
- **Sample:** traffic-powered; needs roughly 300+ weekly sessions per arm for
  most effect sizes to resolve in a fortnight
- **Elapsed:** 14+ days, longer for weekly-cyclical behaviour
- **Output:** observed behaviour at real scale, with a causal claim
- **Cannot answer:** why the losing variant lost; anything about a population
  not in your traffic
- **Failure mode:** stopping early on a favourable reading. Fix the duration and
  the success metric before starting.
- **[PROVEN]** The strongest evidence available for a reversible decision.
  Whenever traffic supports it, prefer it over a study.

### Instrumentation / log analysis

- **Answers:** descriptive, diagnostic
- **Sample:** full population
- **Elapsed:** 1-3 days if instrumentation exists
- **Output:** exact counts, rates, funnels, cohort behaviour
- **Cannot answer:** why; anything about people who never reached your product
- **Failure mode:** measuring what is easy to instrument rather than what
  matters, then reasoning from the proxy
- **[PROVEN]** Always the first stop for any "how many" question. Free,
  immediate, and no sampling error.

### Survey with forced trade-offs

- **Answers:** prioritisation, descriptive
- **Sample:** 100+ completes, more for subgroup reporting
- **Elapsed:** 10-15 days including fielding
- **Output:** ranked priorities, incidence rates, segment distributions
- **Cannot answer:** why; anything requiring depth or follow-up
- **Failure mode:** rating scales instead of forced trade-offs. Ask people to
  rate five features on importance and all five come back important.
- **[RECOMMENDED]** Force the trade-off — allocate 100 points, or pick the one
  you would give up. Constraint is what makes the answer informative.

### Painted-door test

- **Answers:** desirability
- **Sample:** traffic-powered
- **Elapsed:** 5-10 days
- **Output:** click-through to a feature that does not yet exist — revealed
  interest rather than stated interest
- **Cannot answer:** whether interest survives contact with the real thing
- **Failure mode:** user trust damage if handled carelessly. Always land on an
  honest "not built yet, want to be told when it is?" — never a dead end.
- **[RECOMMENDED]** Far better evidence than asking "would you use this," and
  roughly the same cost.

### Diary study

- **Answers:** generative
- **Sample:** 8-12
- **Elapsed:** 21-30 days
- **Output:** behaviour over time, infrequent events, context that a single
  session cannot reach
- **Cannot answer:** anything on a short timeline
- **Failure mode:** participant drop-off after week one. Budget for 30-40%
  attrition and check in mid-study.
- **[RECOMMENDED]** The only practical way to observe events that happen
  monthly or quarterly.

### Support ticket and sales call analysis

- **Answers:** generative, diagnostic, prioritisation
- **Sample:** 50+ artefacts
- **Elapsed:** 1-3 days
- **Output:** problem frequency, the customer's own language, objection patterns
- **Cannot answer:** anything about people who never contacted you — a
  systematically silent majority
- **Failure mode:** treating ticket volume as problem prevalence. Tickets
  measure problems severe enough to complain about, which is a biased subset.
- **[PROVEN]** Always run this before recruiting anyone. It is free, immediate,
  and reliably sharpens the question you were about to spend two weeks on.

## 4. Sample size reasoning


### Qualitative: saturation, not statistics

Qualitative sample size is governed by theme saturation — the point at which new
sessions stop producing new themes. Track it explicitly: log new themes per
session and stop after two consecutive sessions with none.

| Sessions (per segment) | Typical state |
|------------------------|---------------|
| 1-3 | Everything is new. Do not synthesise — you are pattern-matching on noise. |
| 4-6 | Themes begin repeating. First defensible patterns. |
| 7-9 | Saturation for a homogeneous segment. |
| 10-12 | Only needed across 2+ distinct segments. |
| 15+ | Almost always over-research. |

**The count is per segment.** Eight sessions across four segments is two per
segment, which is anecdote wearing a sample size.

### Quantitative: precision and power

For proportions, at 95% confidence with p = 0.5:

| Completes | Margin of error |
|-----------|-----------------|
| 100 | ±10% |
| 250 | ±6% |
| 385 | ±5% |
| 1,065 | ±3% |

Precision is quadratic in cost: halving the margin quadruples the sample. Decide
which margin actually changes your decision before buying the tighter one.

For experiments, the sample is driven by the minimum effect worth detecting. A
small detectable effect is expensive; decide the smallest effect that would
change your action, and power for that, not for the smallest effect that is
technically detectable.

## 5. Mixed-method combinations


For decisions above the reversible-in-a-quarter bar, one method is not enough.
The combinations that earn their cost:

| Combination | Sequence | What it buys |
|-------------|----------|--------------|
| **Logs then interviews** | Quant localises, qual explains | The fastest route from "activation dropped" to "here is why" |
| **Interviews then survey** | Qual generates hypotheses, quant sizes them | Stops you sizing the wrong thing; the survey items come from real user language |
| **Survey then interviews** | Quant finds the outlier segment, qual explains it | Good when the segments are unknown |
| **Painted door then interviews** | Revealed interest, then the why behind it | Filters out politely-stated interest before you spend on depth |
| **Ticket analysis then anything** | Free evidence first | Always. It costs a day and sharpens everything downstream. |

**[PROVEN]** Qual-then-quant is the right default order for a new problem space:
you cannot write good survey items about a domain you do not yet understand, and
a survey written from internal assumptions measures your assumptions.

## 6. Methods to be sceptical of


| Method | Problem |
|--------|---------|
| **Focus groups** | Group dynamics dominate. One confident participant sets the tone and the rest converge. Individual interviews cost the same per participant and yield uncontaminated data. |
| **Feature request voting** | Measures the preferences of the small subset who use your feedback channel, weighted by their enthusiasm rather than the value of the work. |
| **Stated purchase intent** | Overstates realised purchase substantially and inconsistently across categories. Useful only for ranking options within one instrument. |
| **Satisfaction scores as a discovery input** | A single number that aggregates away everything you would need to act. Fine as a tracked metric, useless as a research finding. |
| **Asking users to design** | People are reliable reporters of their experience and unreliable designers of solutions. |
| **Internal-stakeholder "user" interviews** | Your colleagues' model of the user is not the user. Useful for surfacing internal assumptions to test — never as evidence about users. |

## 7. Recruiting


Recruiting is the constraint that decides whether a study happens, and it is
consistently the last thing teams plan.

### Sources ranked

| Source | Speed | Quality | Bias risk |
|--------|-------|---------|-----------|
| **Own customers (in-product intercept)** | Fast | High | Skews to engaged, frequent users |
| **Own customers (email to a segment)** | Moderate | High | Skews to responsive, satisfied users |
| **Churned customer list** | Slow | Very high value | Hard to reach; worth several times a happy user |
| **Sales pipeline (lost deals)** | Moderate | Very high value | Requires sales cooperation |
| **B2B research panel** | Fast | Variable | Professional respondents; needs a trap item |
| **Community or association list** | Slow | High | Skews to the engaged and vocal |
| **Personal and colleague networks** | Fast | Low for research | Strong social-desirability bias; avoid |

**[PROVEN]** The highest-value participants are the hardest to recruit: churned
users, lost deals, and people who evaluated you and chose otherwise. Budget more
per session for them. A single lost-deal conversation frequently outweighs three
sessions with satisfied power users, because satisfied users cannot tell you why
anyone leaves.

### Incentives

Set the incentive against the participant's time value, not against a standard
rate. Under-incentivising hard-to-reach audiences does not save money; it means
the study does not field.

| Audience | Relative incentive |
|----------|-------------------|
| Consumer, 30 minutes | Baseline |
| Professional, 60 minutes | 3-5x baseline |
| Senior professional or clinician | 8-15x baseline |
| Own customers with a stake in the outcome | Often lower; some decline entirely |

Where incentives are prohibited (some public sector, some clinical contexts),
offer a charitable donation or early access to findings.

## 8. Sequencing a discovery programme


For a new problem space, this order reliably wastes the least money:

1. **Mine what you already own** (1-3 days) — tickets, sales calls, churn
   surveys, session replays. Free, immediate, and it sharpens everything after.
2. **Instrument and measure** (2-5 days) — establish what is happening and at
   what scale. Now you know which segment matters.
3. **Interview for the why** (1-2 weeks) — 6-8 sessions in the segment the data
   pointed at.
4. **Size the finding** (1-2 weeks, optional) — survey if the decision needs a
   proportion rather than a mechanism.
5. **Test the solution** (ongoing) — experiment or usability test.

Skipping step 1 is the most common and most expensive error. Skipping step 2 leads
to interviewing the wrong segment thoroughly.

## 9. Reading a method's weaknesses


Every method has a structural blind spot. Know each one before you cite the result.

| Method | Blind spot |
|--------|-----------|
| Interviews | Says nothing about prevalence. Six people cannot represent a proportion. |
| Usability tests | Measures learnability in an artificial task, not sustained real use |
| Surveys | Captures stated attitude, not behaviour; non-response bias exceeds sampling error |
| Experiments | Cannot explain why; measures only the variants you thought to build |
| Analytics | Silent on people who never arrived, and on why anyone did anything |
| Support tickets | Only problems severe enough to complain about; systematically silent majority |
| Sales calls | Filtered through what the prospect will admit to a salesperson |
| Diary studies | Heavy attrition; self-report quality declines over the study |

The practical consequence: **any decision resting on a single method inherits
that method's blind spot unexamined.** For decisions above the
reversible-in-a-quarter bar, pair methods whose blind spots differ — which is
what "mixed methods" actually means in practice.

## 10. Communicating method limits


A finding is only as good as the audience's understanding of its limits. Three
sentences belong in every readout:

1. **Who was in the sample** — "8 support leads at companies with 200+ employees,
   all existing customers, recruited by email."
2. **Who was not** — "No churned customers and no companies under 200 employees.
   Findings should not be extended to those groups."
3. **What the method can and cannot establish** — "This tells us why agents
   re-triage, not how many are affected. The prevalence question needs
   instrumentation."

Point 3 is the one that prevents the most downstream damage. Qualitative findings
get quantified in retelling — "users re-triage constantly" becomes "most users
re-triage" by the third meeting. Stating the limit explicitly in the readout is
the only reliable defence, and it costs one sentence.

## 11. Selection checklist


- [ ] Question is written in interrogative form, not as a decision
- [ ] Question is classified into one of the seven types
- [ ] Reversibility assessed; reversible decisions routed to an experiment
- [ ] Existing evidence (tickets, calls, logs) mined before recruiting anyone
- [ ] Binding constraint identified — timeline, access, or traffic
- [ ] Method chosen is the cheapest that clears the evidence bar
- [ ] Sample sized per segment, not in total
- [ ] For quant: the margin or effect size that changes the decision is stated
- [ ] For mixed methods: the sequence and what each stage buys are written down
- [ ] The result that would change course is written down before fielding
