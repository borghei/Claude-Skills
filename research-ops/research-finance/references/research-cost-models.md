# Research Cost Models

Reference for building research budgets that fund what the work will actually
consume: cost structures by method, what drives each unit cost, and the line
items that are reliably forgotten.

## 1. The four cost blocks

Every research budget decomposes into four blocks. Most under-budgeting comes
from putting a cost in the wrong block, not from omitting it entirely.

| Block | Scales with | Examples |
|-------|-------------|----------|
| **Per participant** | Enrolment or screening volume | Incentives, assessments, labs, imaging, transcription |
| **Per site** | Number of sites | Startup, training, initiation visit, close-out |
| **Per site-month** | Sites × duration | Coordination, monitoring visits, site fees, storage |
| **Fixed** | Nothing | Protocol development, statistics, data management, final report |

The classic misclassification is **site coordination billed as fixed**. It is a
per-site-month cost, and on a 30-month study across six sites it is 180
site-months — often one of the largest lines in the budget. Booked as fixed, it
is understated by roughly an order of magnitude.

The second most common is **monitoring billed as fixed** when it scales with
both sites and duration.

## 2. Screening and yield

Participant-stage costs divide into those incurred on **everyone screened** and
those incurred only on **those enrolled**.

```
participants_screened = participants_enrolled / (1 - screen_failure_rate)
```

| Screen failure rate | Screened per 100 enrolled |
|--------------------|--------------------------|
| 10% | 112 |
| 20% | 125 |
| 30% | 143 |
| 40% | 167 |
| 50% | 200 |

Charged on screened: screening assessments, screening labs, consent time, and
the site's screening effort.
Charged on enrolled: the visit schedule, incentives, treatment, and follow-up.

The same logic applies outside clinical work under a different name. In product
research the equivalent is recruiting yield: if 30% of screener respondents
qualify and 70% of qualified participants actually attend, you pay for screener
completes and no-shows regardless.

| Research recruiting stage | Typical yield |
|--------------------------|---------------|
| Invitation → screener complete | 5-20% |
| Screener complete → qualified | 20-50% |
| Qualified → scheduled | 50-80% |
| Scheduled → attended | 70-90% |

Multiply these through: reaching 8 attended sessions typically means several
hundred invitations. Budget the funnel, not the sessions.

## 3. Cost drivers by method

### Interview-based research

| Line | Driver | Notes |
|------|--------|-------|
| Recruiting | Sessions × yield | The dominant cost for hard-to-reach populations |
| Incentives | Sessions | Scales steeply with seniority of participant |
| Moderation time | Sessions × (session + prep + debrief) | Budget 2.5x session length in total |
| Transcription | Session hours | Cheap; do not skip it — it makes synthesis auditable |
| Synthesis | Sessions | Roughly 1-1.5 hours per session of analysis |
| Readout | Fixed per study | |

**The cost nobody counts:** moderator and notetaker time. A "cheap" 8-session
study consumes roughly 40-50 person-hours across preparation, sessions,
debriefs, synthesis, and readout. Where that time is not budgeted, it is taken
from something else.

### Survey research

| Line | Driver | Notes |
|------|--------|-------|
| Panel sample | Completes × incidence | Cost rises sharply as incidence falls — a 5% incidence audience can cost several times a general-population complete |
| Instrument design | Fixed | Underestimated; a good instrument takes days |
| Programming and testing | Instrument length | |
| Incentives (owned list) | Completes | Much cheaper than panel |
| Analysis | Fixed plus subgroups | Each reported subgroup adds analysis cost |

**Incidence is the dominant driver.** A survey needing 400 completes from an
audience representing 4% of the panel requires screening roughly 10,000 people,
and screening costs money even when the respondent does not qualify.

### Experiments

| Line | Driver | Notes |
|------|--------|-------|
| Engineering build | Variant complexity | Nearly always the largest cost |
| Instrumentation | Number of new events | |
| Analysis | Fixed | |
| Opportunity cost of traffic | Duration × exposed users | Real when the losing variant underperforms |

**The cost nobody counts:** engineering time. Experiments carry no external
invoice, which makes them look free next to a study with a vendor quote. Count
the engineering days at a loaded rate, or the portfolio comparison is
systematically distorted in favour of experiments.

### Clinical studies

| Line | Driver | Notes |
|------|--------|-------|
| Site startup | Sites | Contracts, ethics, training, initiation |
| Per-participant grants | Enrolled × visits | The visit schedule drives this directly |
| Screening costs | Screened | Grossed up for screen failure |
| Site coordination | Site-months | Per-site-month, for the full duration |
| Monitoring | Site visits | Scales with sites, duration, and risk-based monitoring plan |
| Central lab / imaging | Participants × timepoints | |
| Data management and EDC | Participants and CRF complexity | Build cost plus per-participant |
| Biostatistics | Fixed plus interim analyses | Each interim is additional |
| Medical writing | Fixed | Protocol, CSR, publications |
| Regulatory and ethics | Sites and countries | Multi-country multiplies submissions |
| Insurance | Participants and risk class | |
| Pharmacovigilance | Duration and event rate | |

## 4. Contingency, overhead, and escalation

### Contingency

| Study type | Recommended contingency |
|-----------|------------------------|
| Short, single-site, well-precedented | 5-8% |
| Standard multi-site study | 10-15% |
| First-in-population, novel endpoint, or new geography | 15-25% |
| Multi-country regulatory study | 15-20% |

**[RECOMMENDED]** 10% is the practical floor for anything multi-site. Below
about 8%, every protocol amendment becomes a change request, and change requests
consume management attention out of all proportion to their value.

### Overhead

Overhead (indirect cost recovery) varies enormously by organisation and funder,
and some funders cap it or exclude specific categories. Two rules:

1. **State whether the quoted number is inclusive or exclusive of overhead.**
   The same study is quoted at very different totals depending on this, and the
   mismatch surfaces after award, which is the worst time.
2. **Check what the overhead base is.** Some organisations apply it to direct
   costs only, some include contingency, and some exclude participant incentives
   or equipment. The base changes the total materially.

### Escalation

For studies over 24 months, include an explicit escalation line. Site grants,
staff costs, and vendor rates all rise over a multi-year study, and a budget
fixed at year-one rates is short by the time it reaches close-out.

## 5. Cost per insight

Cost per insight is blunt but forces a comparison across methods that otherwise
get evaluated in isolation.

```
cost_per_insight = total_cost / decision_ready_insights
```

Two disciplines make it meaningful:

- **Count only decision-ready insights** — those that met a stated confidence
  bar. Counting every observation makes any method look efficient.
- **Count all costs including internal time.** Otherwise methods with external
  invoices look expensive relative to methods that consume salaried hours.

### Method comparison

| Method | Relative cost per insight | Why |
|--------|--------------------------|-----|
| Existing-artefact analysis (tickets, calls, logs) | Lowest | The evidence is already paid for |
| Instrumentation analysis | Low | Assumes instrumentation exists; otherwise the build cost dominates |
| Interview round | Moderate | Recruiting and internal time dominate |
| Survey | Moderate | Panel cost dominates; falls sharply on an owned list |
| Experiment | Moderate | Engineering time dominates and is usually uncounted |
| Diary study | High | Long duration, high attrition, heavy analysis |
| Multi-site clinical study | Highest by orders of magnitude | Regulatory and site infrastructure dominate |

The ordering is more useful than the absolute numbers. Its main practical use is
forcing the question: **has the cheap evidence been mined before the expensive
evidence is commissioned?** In most organisations the answer is no.

## 6. Commonly omitted line items

Run this list against any draft budget.

- [ ] Screening costs grossed up for screen failure
- [ ] Recruiting funnel costs, not just completed sessions
- [ ] No-show and replacement costs
- [ ] Site coordination as per-site-month for the full duration
- [ ] Monitoring scaled to sites and duration
- [ ] Data management build **and** per-participant costs
- [ ] Statistics beyond the initial analysis plan
- [ ] Each interim analysis costed separately
- [ ] Transcription and translation
- [ ] Internal moderator, analyst, and engineering time at a loaded rate
- [ ] Close-out: database lock, site close-out visits, archiving
- [ ] Final report and any publication costs
- [ ] Record retention for the full required period
- [ ] Insurance
- [ ] Currency and inflation escalation on studies over 24 months
- [ ] Protocol amendment contingency
- [ ] Regulatory submission fees per country
- [ ] Participant travel and reimbursement
- [ ] Equipment purchase, calibration, and disposal

The last-third of that list — close-out, retention, reporting — is where studies
most often run out of money, because it falls at the end when the budget is
already committed and the appetite for a supplementary request is lowest.

## 7. Budget review checklist

- [ ] Every cost assigned to the correct block (participant / site / site-month / fixed)
- [ ] Screening costs grossed up by 1/(1 − screen failure rate)
- [ ] Recruiting funnel yield modelled, not just final sessions
- [ ] Site coordination charged per site-month across the full duration
- [ ] Internal time costed at a loaded rate
- [ ] Close-out, reporting, and retention explicitly funded
- [ ] Contingency at or above 10% for multi-site work
- [ ] Overhead base stated; inclusive/exclusive made explicit in the quoted total
- [ ] Escalation line present for studies over 24 months
- [ ] Cost per enrolled participant computed and benchmarked
- [ ] Cost per decision-ready insight computed
- [ ] Fixed costs below about 55% of the total, or the concentration justified
- [ ] Every assumption traceable to a source or a comparable study
