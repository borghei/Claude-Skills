# Protocol and Endpoint Design

Reference for structuring a clinical study protocol, defining endpoints that can
actually be analysed, and designing eligibility criteria that do not make the
study unaccruable.

> This reference covers study operations and document structure. It is not
> regulatory advice. Requirements vary by jurisdiction, product type, and study
> phase, and every protocol requires qualified regulatory affairs and clinical
> review before submission.

## 1. Protocol contents


ICH E6 sets out the contents a protocol is expected to cover. The auditor script
uses these as its required-section list.

| Section | Contents |
|---------|----------|
| **General information** | Protocol ID and version, sponsor, monitor, investigators, sites, medical expert, laboratories |
| **Background** | Name and description of the investigational product, findings from nonclinical and clinical studies, known and potential risks and benefits, description of and justification for route, dosage, regimen, and treatment period, statement that the trial will be conducted in compliance with the protocol, GCP, and applicable regulatory requirements, description of the population, references |
| **Objectives and purpose** | Detailed description of objectives and purpose |
| **Trial design** | Primary and secondary endpoints, description of design (parallel, crossover, factorial), schematic diagram, randomisation and blinding procedures, description of treatments and dosage, expected duration of participation and sequence of periods, stopping rules, accountability procedures for the investigational product, maintenance of randomisation codes and unblinding procedures, identification of source data recorded directly on CRFs |
| **Selection and withdrawal of subjects** | Inclusion criteria, exclusion criteria, withdrawal criteria, when and how to withdraw, type and timing of replacement data, follow-up for withdrawn subjects |
| **Treatment of subjects** | Treatments to be administered, medication permitted and not permitted before and during, procedures for monitoring compliance |
| **Assessment of efficacy** | Specification of efficacy parameters, methods and timing for assessing, recording, and analysing them |
| **Assessment of safety** | Specification of safety parameters, methods and timing for assessing, recording, and analysing them, procedures for eliciting reports of and recording and reporting adverse events and intercurrent illnesses, type and duration of follow-up after adverse events |
| **Statistics** | Statistical methods, planned number of subjects and reason for the sample size, level of significance, criteria for termination, procedure for accounting for missing/unused/spurious data, procedures for reporting deviations from the original statistical plan, selection of subjects to be included in the analyses |
| **Direct access to source data** | Sponsor will ensure the protocol specifies that investigators permit trial-related monitoring, audits, review, and inspection |
| **Quality control and quality assurance** | QC and QA arrangements |
| **Ethics** | Ethical considerations relating to the trial |
| **Data handling and record keeping** | Data handling, record keeping, retention period |
| **Financing and insurance** | Financing and insurance arrangements if not in a separate agreement |
| **Publication policy** | Publication policy if not in a separate agreement |

The three most commonly omitted from a draft are **quality control**,
**financing and insurance**, and **publication policy** — usually because they
are assumed to live in a separate agreement. That is acceptable if the agreement
exists and the protocol says so; it is a finding if neither is true.

## 2. Endpoints


### The four things every endpoint needs

An endpoint that cannot be stated in this form cannot be powered, collected
consistently, or analysed.

1. **Instrument** — what is measured, with what tool, by whom
2. **Metric** — what is derived from the instrument (change from baseline, a
   proportion, time to first occurrence)
3. **Threshold or contrast** — what value constitutes the outcome
4. **Timepoint** — when it is measured

| Unanalysable | Analysable |
|--------------|-----------|
| "Improvement in wellbeing" | "Change from baseline in the 24-item symptom scale total score at week 24" |
| "Treatment success" | "Proportion of participants with pill-count adherence of 80% or greater at week 12" |
| "Better outcomes" | "Time from randomisation to first hospitalisation for any cause, over 18 months" |

### The endpoint hierarchy

| Role | Count | Purpose |
|------|-------|---------|
| **Primary** | Exactly one, ideally | Determines the sample size and the study's success criterion |
| **Secondary** | 3-8 | Supports the primary; hierarchically ordered if they will be tested |
| **Exploratory** | Any number | Hypothesis-generating; must be labelled as such and never used to claim efficacy |
| **Safety** | As required | Assessed regardless of the efficacy result |

**Co-primary endpoints** — where success requires both to succeed — reduce power
and require a larger sample. **Multiple primary endpoints** — where success
requires either — inflate type I error and require multiplicity adjustment. Both
are legitimate designs and both need a statistician and an explicit
pre-specified strategy. Neither should arrive by accident because two
stakeholders each wanted their measure designated primary.

### Estimands

Modern protocols are expected to define the **estimand** — precisely what the
treatment effect being estimated actually is — not just the endpoint. Five
attributes:

1. **Population** — which participants the effect refers to
2. **Variable** — the endpoint measured on each participant
3. **Intercurrent events** — what happens if a participant discontinues, takes
   rescue medication, or dies before the endpoint is measured
4. **Population-level summary** — difference in means, risk difference, hazard
   ratio
5. **Handling strategy** for each intercurrent event — treatment policy,
   hypothetical, composite, while-on-treatment, or principal stratum

Attribute 3 is where most protocols are silent, and it is where the analysis
argument later happens. Decide in advance: if a participant discontinues at week
6 and the endpoint is at week 12, what is their outcome? A protocol that has not
answered that has not defined its endpoint.

### Surrogate endpoints

A surrogate substitutes for a clinical outcome that would take too long or too
many participants to measure. Use only when the surrogate has been validated as
predicting the clinical outcome in that population and that intervention class.

The failure mode is well documented across therapeutic areas: an intervention
improves the surrogate and worsens the clinical outcome. Treat a surrogate as an
acceptable primary only where regulatory precedent exists for it in that
indication, and keep the clinical outcome as a secondary endpoint wherever the
study duration permits.

## 3. Eligibility criteria


### The trade-off

Each criterion buys internal validity and costs accrual and generalisability.

| Criteria count | Typical consequence |
|----------------|--------------------|
| Under 15 | Broad, fast accrual, results generalise |
| 15-25 | Standard for a phase 3 study |
| 25-35 | Screen failure climbs steeply; accrual timelines stretch materially |
| Over 35 | Accrual frequently fails; treated population may not resemble the studied one |

### Design rules

1. **Every criterion needs a stated reason** — a specific safety risk, a
   confounding risk, or a regulatory requirement. "It seemed sensible" is how
   criteria accumulate.
2. **Never state the same restriction twice.** An exclusion that negates an
   inclusion adds screening work and creates a version-control hazard when one
   is amended and the other is not.
3. **Make every criterion objectively verifiable.** "Adequate organ function"
   is a source of protocol deviations; "eGFR ≥ 45 mL/min/1.73m² within 28 days
   of randomisation" is not.
4. **Bound every window.** A lab value with no recency window will be applied
   inconsistently across sites.
5. **Prefer inclusion criteria for what defines the population** and exclusion
   criteria for safety and interpretability risks. Mixing the two makes the
   population definition hard to read.
6. **Model the cumulative screen failure rate** before finalising. If each of 25
   criteria excludes 5% independently, roughly a quarter of screened patients
   remain — and criteria correlate, usually making it worse.

### Common over-restrictions

| Criterion | Cost | Consider |
|-----------|------|----------|
| Narrow age band | Excludes the population most likely to receive the treatment | Widen unless a specific age-related safety risk exists |
| No prior therapy | Severely restricts accrual in most indications | Stratify by prior therapy rather than excluding |
| Broad comorbidity exclusions | Removes the real-world population entirely | Exclude only comorbidities with a named interaction risk |
| Excluding common concomitant medications | Frequent screen failure driver | Permit with documented washout where safe |
| Requiring a rarely-performed test at screening | Site burden, slow screening | Accept an equivalent routine test |

## 4. Withdrawal and missing data


Pre-specify, in the protocol, before enrolment:

- **Withdrawal criteria** — what causes a participant to come off treatment, and
  separately what causes them to come off study. These are different, and
  conflating them is how follow-up data gets lost unnecessarily.
- **Follow-up for withdrawn participants** — a participant who stops treatment
  can usually still contribute endpoint data. Say so, and collect it.
- **Missing data strategy** — the imputation approach and at least one
  sensitivity analysis under a different missingness assumption.
- **Replacement policy** — whether withdrawn participants are replaced, and how
  that interacts with the analysis populations.

Choosing a missing-data approach after seeing the data is a serious credibility
problem, and reviewers look for evidence of it.

### Analysis populations

| Population | Definition | Use |
|-----------|-----------|-----|
| **ITT** | All randomised participants, analysed as randomised | Primary efficacy in superiority trials — preserves randomisation |
| **mITT** | ITT with a pre-specified minimal exclusion (e.g. never dosed) | Acceptable when defined before unblinding |
| **Per-protocol** | Participants completing without major deviations | Sensitivity only — it breaks randomisation and biases toward the treatment |
| **Safety** | All who received any study treatment, analysed as treated | All safety analyses |

Define all four in the protocol. The per-protocol population must never be the
primary in a superiority trial: excluding non-compliers post-randomisation
introduces exactly the confounding randomisation exists to remove.

## 5. Safety and oversight


- **AE and SAE definitions** must be stated verbatim, not referenced loosely.
- **SAE reporting window** to the sponsor is immediate — within 24 hours is the
  standard expectation.
- **Stopping rules** for harm and for futility, defined before first enrolment.
- **Data safety monitoring board** for phase 3 and 4 studies, for any study with
  mortality endpoints, and for any study in a vulnerable population. If absent,
  the protocol should justify the absence.
- **Unblinding procedure** — who can unblind, under what circumstances, how it
  is documented, and how the trial's integrity is preserved afterward.

## 6. Documentation readiness


Before a protocol goes to an ethics committee, these should exist in draft:

- [ ] Protocol, with version number and date
- [ ] Investigator's brochure or equivalent product information
- [ ] Informed consent form, at an appropriate reading level, per language
- [ ] Participant-facing materials (information sheet, diary, recruitment text)
- [ ] Case report form aligned line-by-line with the protocol schedule of assessments
- [ ] Statistical analysis plan, or at minimum the statistical section signed by a statistician
- [ ] Data management plan
- [ ] Monitoring plan
- [ ] Safety reporting plan, including the SAE reporting pathway per site
- [ ] Site delegation-of-authority template
- [ ] Trial registration record prepared for submission before first enrolment

The CRF-to-protocol alignment check is the one most often skipped and the one
that most reliably generates protocol deviations: any assessment in the schedule
without a matching CRF field will be collected inconsistently or not at all.

## 7. Randomisation and blinding


### Randomisation methods

| Method | Mechanism | Use when |
|--------|-----------|----------|
| **Simple** | Each participant allocated independently | Large trials (>200); risks imbalance in smaller ones |
| **Block** | Allocation balanced within blocks | **[PROVEN]** Default. Keep block size varied and concealed, or allocation becomes predictable at block end |
| **Stratified block** | Blocks within strata (site, prognostic factor) | Known strong prognostic factors; keep strata few |
| **Minimisation** | Allocates to minimise imbalance across several factors | Small trials with multiple important covariates |

Two rules that prevent most randomisation failures:

1. **Allocation concealment is distinct from blinding.** Concealment protects the
   allocation sequence up to the moment of assignment; blinding protects
   knowledge afterwards. A trial can be unblinded by necessity and still require
   strict concealment.
2. **Do not stratify on many factors.** Each stratum needs enough participants to
   fill blocks. More than two or three stratification factors in a moderate
   trial produces many sparse strata and defeats the purpose.

### Blinding levels

| Level | Blinded | Notes |
|-------|---------|-------|
| Open-label | Nobody | Acceptable where blinding is impossible; expect performance and detection bias |
| Single-blind | Participant | Assessor bias remains |
| Double-blind | Participant and investigator | Standard where feasible |
| Triple-blind | Plus outcome assessor or analyst | Strongest, particularly for subjective endpoints |

Where blinding is impossible (surgical, behavioural, device interventions),
**blind the outcome assessor**. It is nearly always feasible, it is the single
most effective bias control available in an open-label trial, and it is
frequently overlooked.

## 8. Schedule of assessments


The schedule is the operational core of the protocol. Every row costs site time,
participant burden, and money.

Build it as a matrix: visits across the top, assessments down the side. Then
challenge every cell against three questions:

1. **Which endpoint or safety requirement does this serve?** A cell serving
   neither is unfunded curiosity and should be cut.
2. **Does the CRF have a field for it?** Anything collected without a field is
   collected inconsistently or lost.
3. **What is the visit window?** An assessment with no window is applied
   differently at every site and generates deviations.

### Burden control

| Signal | Consequence |
|--------|-------------|
| Visit duration over 3 hours | Dropout rises sharply |
| More than monthly visits over a long study | Retention falls |
| Long travel with no reimbursement | Systematic exclusion of lower-income participants, harming generalisability |
| Multiple lengthy questionnaires per visit | Later-instrument data quality degrades measurably |

Participant burden is a scientific issue, not only an ethical one. Burden drives
dropout, dropout drives missing data, and missing data is the most common threat
to a trial's primary analysis.

## 9. Protocol amendments


Amendments are expensive: re-submission to every ethics committee, re-consent
where the change affects participants, site retraining, and CRF changes.

| Amendment type | Typical trigger | Avoidable? |
|----------------|-----------------|-----------|
| Eligibility relaxation | Accrual below plan | Often — realistic feasibility assessment up front |
| Endpoint clarification | Ambiguity found during collection | Usually — the four-attribute endpoint test catches it |
| Visit window widening | Sites cannot meet windows | Usually — pilot the schedule with one site first |
| Safety update | New safety information | No — this is the system working |
| Sample size increase | Assumptions proved optimistic | Sometimes — conservative variance assumptions help |

**[RECOMMENDED]** Pilot the full protocol at one site before opening the rest.
The first site reliably surfaces the schedule, CRF, and eligibility problems
that would otherwise become an amendment across every site.

Track amendment count as a quality metric. More than two substantial amendments
in a study usually indicates the protocol was finalised before the operational
detail was worked through.

## 10. Data quality and monitoring


### Risk-based monitoring

100% source data verification is expensive and does not correlate well with
finding the errors that matter. Concentrate effort on:

- **Critical data** — primary endpoint, key safety variables, eligibility,
  consent
- **High-risk sites** — new sites, high enrollers, sites with prior findings
- **Early participants at each site** — errors are systematic, and catching them
  in the first few participants prevents them recurring across all of them

That last point is the highest-yield monitoring practice available. Site errors
are almost never random; they are a consistent misunderstanding that repeats
until someone catches it.

### Deviation categories

| Category | Examples | Response |
|----------|----------|----------|
| **Critical** | Consent not obtained, ineligible participant enrolled, safety reporting failure | Immediate escalation, root-cause analysis, possible site suspension |
| **Major** | Primary endpoint assessment missed, visit outside window affecting endpoint | Documented, trended, retrained |
| **Minor** | Non-critical assessment missed, minor window excursion | Documented and trended |

Trend deviations by site and by type. A rising rate at one site indicates a
training or capacity problem; a rising rate across all sites indicates a protocol
problem — usually a schedule the study asked for and the sites cannot deliver.

## 11. Protocol review checklist


- [ ] All ICH E6 sections present, or explicitly deferred to a named agreement
- [ ] Exactly one primary endpoint, unless co-primaries are intentional and adjusted
- [ ] Every endpoint states instrument, metric, threshold, and timepoint
- [ ] Estimand defined, including intercurrent event handling
- [ ] Secondary endpoints hierarchically ordered if they will be tested
- [ ] Exploratory endpoints labelled as such
- [ ] Eligibility criteria count justified; no criterion stated twice
- [ ] Every criterion objectively verifiable with a bounded window
- [ ] Projected screen failure rate estimated
- [ ] Withdrawal from treatment and withdrawal from study defined separately
- [ ] Follow-up for withdrawn participants specified
- [ ] All four analysis populations defined; ITT is primary
- [ ] Missing data strategy pre-specified with a sensitivity analysis
- [ ] Sample size justified with effect size, alpha, power, and variance source
- [ ] Every interim analysis has an alpha spending function and stopping boundaries
- [ ] AE/SAE definitions verbatim; reporting window within 24 hours
- [ ] Stopping rules for harm and futility defined
- [ ] DSMB present, or its absence justified
- [ ] Schedule of assessments matches the CRF field by field
- [ ] Registration prepared for submission before first enrolment
- [ ] Biostatistics, clinical, and regulatory affairs sign-off obtained
