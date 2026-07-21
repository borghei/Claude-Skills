# Process Capture Methods

How to get an accurate process map out of an organisation. Analysis of the
resulting data lives in `lean-process-analysis.md`.

The failure mode this file exists to prevent: mapping the process people
*describe* rather than the process that *runs*. These differ, always, and the
gap is usually where the problem lives.

---

## 1. Scoping before capture

Set four boundaries before the first interview. Skipping this produces a map
that sprawls for weeks and improves nothing.

| Boundary | Question | Example |
|----------|----------|---------|
| Trigger | What event starts it? | "Signed order form submitted" |
| Terminal | What state ends it? | "Customer credentials delivered" |
| Unit | What flows through? | One enterprise order |
| Variant | Which path are we mapping? | Standard terms, existing customer |

**Map one variant end to end before mapping any others.** A map covering every
exception is unreadable and un-analysable. Capture the dominant path (typically
70-85% of volume), then note exception paths separately with their frequency.

### SIPOC — the one-page frame

Do this before detailed capture. It takes 30 minutes and prevents scope fights.

| Element | Question | Keep to |
|---------|----------|---------|
| **S**uppliers | Who provides inputs? | 3-7 entries |
| **I**nputs | What do they provide? | 3-7 entries |
| **P**rocess | What are the high-level steps? | 5-7 steps, verb-first |
| **O**utputs | What does the process produce? | 3-7 entries |
| **C**ustomers | Who receives the outputs? | 3-7 entries |

If the process box needs more than seven steps at this altitude, the scope is
too wide — split it. The SIPOC is the contract for what is in and out of scope,
and it is what you show the sponsor before spending two weeks on detail.

---

## 2. Capture techniques, ranked

### [PROVEN] Go and observe

Watch the work happen, at the place it happens, with the person who does it.
Nothing else surfaces the workaround spreadsheet, the second system nobody
mentions, or the informal check that prevents half the defects.

Rules: observe, do not correct. Ask "what happens next?" not "why do you do it
that way?" — the second question makes people defend the process instead of
describing it. Watch at least three units, ideally including one that goes wrong.

### [PROVEN] System timestamp extraction

Pull actual timestamps from the systems of record. This is the only source that
gives real wait times, and wait time is where the answer usually is. Self-report
underestimates queue time by 40-70% because people remember the work, not the
waiting.

Extract: created, assigned, first-touched, completed, and reopened per step.
Median and 85th percentile, never mean — process time distributions have long
right tails, and the mean describes a unit nobody experiences.

### [RECOMMENDED] Swimlane workshop

Room with one representative per owner, one lane per owner, sticky note per
step, drawn left to right. Two hours produces a map plus the argument about who
owns what, which is itself a finding.

Its weakness is that it captures the process as understood by people senior
enough to be in the room. Always validate the workshop map against observation
and timestamps before analysing it.

### [RECOMMENDED] Follow one unit end to end

Take a single real case and trace it through every system and person. Slow, and
n=1, but it reliably finds the invisible steps: the re-keying, the chase email,
the "I just check with Priya first."

### Avoid: documentation archaeology

Reading the existing SOP tells you what someone intended two reorganisations
ago. Use it to generate questions, never as a data source.

---

## 3. What to record per step

The scripts expect these fields. Each exists because it drives a diagnostic.

| Field | Definition | Source | Why |
|-------|-----------|--------|-----|
| `id` | Stable identifier | Assigned | Rework loop targets |
| `name` | Verb-first description | Observation | Readability |
| `owner` | Role or team, never a person's name | Observation | Handoff detection |
| `value_type` | value_added / business_value_added / non_value_added | Judged, see below | PCE and elimination targets |
| `process_time_min` | Hands-on work, one unit, no interruption | Observation or timing | Touch time, labour cost |
| `wait_time_min` | Elapsed from ready-to-start until started | System timestamps | Queue diagnosis |
| `rework_rate` | Share of units returned or redone at this step | System or tally | First-pass yield |
| `rework_to` | Step id the work returns to | Observation | Loop cost |
| `system` | System of record used | Observation | Switch detection |
| `automated` | Runs without a human trigger | Observation | Transfer risk |

### Classifying value type

Three tests, applied in order:

1. **Value-added** — the customer would knowingly pay for it, it transforms the
   work, and it is done right the first time. All three, or it is not VA.
2. **Business-value-added** — the customer would not pay, but the business
   genuinely requires it: regulatory checks, fraud controls, statutory records.
   Minimise, do not eliminate.
3. **Non-value-added** — everything else. Waiting, moving, re-keying, checking,
   correcting, chasing. Eliminate.

Two disciplines that keep this honest:

- **Approvals are business-value-added only if they reject.** Measure the
  rejection rate; below 5%, reclassify as non-value-added.
- **Judge from the customer's seat, not the department's.** "Compliance review"
  feels essential inside compliance. The test is whether a regulator requires it,
  not whether it is someone's job.

Expect 20-40% of touch time to be non-value-added in an unexamined process. If
your map shows under 10%, you classified generously — re-run the three tests.

---

## 4. Getting the time data right

| Rule | Reason |
|------|--------|
| Use median and 85th percentile, not mean | Long right tails make means unrepresentative |
| Record process time for one unit, uninterrupted | Otherwise you capture the interrupt, not the work |
| Take wait time from timestamps, never self-report | Self-report understates queues by 40-70% |
| Record rework rate from system data or a two-week tally | Recalled rates are optimistic by roughly half |
| Note whether a step batches | A weekly batch step has up to 5 days of hidden wait |
| Capture the same period for all steps | Mixing a quiet month with a peak month invents bottlenecks |

**Batching is the most commonly missed source of wait time.** A step run every
Tuesday has an average wait of 2.5 working days before it even starts, and this
appears nowhere in anyone's description of their work. Ask "when do you do this
— as it arrives, or on a schedule?" at every step.

### When you cannot measure

Do not stop; record the uncertainty. Use a three-point estimate from the person
doing the work (best / typical / worst), take the typical, and mark the step's
confidence as low. Then measure the two or three steps that dominate lead time
properly before committing to any improvement. **Measure the constraint; estimate
the rest.**

---

## 5. Validating the map

Before analysing, run all four checks. Skipping validation is how a map of a
fictional process reaches a steering committee.

1. **Walk it back to the doers.** Read the map aloud to the people who do the
   work. The reliable prompt: "What did I get wrong?" — not "does this look
   right?", which gets nodding.
2. **Test the arithmetic.** Modelled lead time should be within 20% of measured
   end-to-end lead time from system data. A large gap means missing steps or
   missing wait — almost always missing wait.
3. **Find the exceptions.** Ask "when does it not go this way?" Record each
   exception path with its frequency. If exceptions exceed 30% of volume, you
   mapped a variant, not the process.
4. **Check for invisible steps.** Chase emails, status meetings, spreadsheet
   reconciliation, and "just checking with X" are real steps with real time.
   They are absent from every process document ever written.

---

## 6. Notation

Keep it simple enough to be redrawn on a whiteboard.

- **Lane per owner**, left to right in time order. Owners are roles, not people.
- **Box per step**, verb-first: "Verify credit limit", not "Credit verification".
- **Diamond per decision**, with the percentage split on each branch. Unlabelled
  branches hide the volume that matters.
- **Dashed arrow per rework loop**, labelled with its rate, drawn backward to
  the step it returns to.
- **Annotate each box** with process time / wait time, and each handoff with the
  system change if there is one.

Keep the whole map on one page. A process map that needs scrolling will not be
read by the person who can approve changing it — and getting it on one page
forces the altitude decision you were avoiding.

---

## 7. Sequence for a full engagement

| Phase | Duration | Output |
|-------|----------|--------|
| Scope + SIPOC | 0.5 day | One-page frame, agreed with sponsor |
| Observation | 1-2 days | Raw step list, invisible steps found |
| Timestamp extraction | 0.5-1 day | Real wait times, rework rates |
| Swimlane workshop | 0.5 day | Ownership map, disagreements surfaced |
| Validation | 0.5 day | Corrected map within 20% of measured lead time |
| Analysis | 0.5 day | PCE, constraint, loops, handoff risk |
| Opportunity scoring | 0.5 day | Prioritised backlog with payback |
| Readout | 0.5 day | Sponsor decision on the NOW tier |

**Four to six days end to end for a process crossing three to five teams.**
Anything running longer is scope creep, and scope creep in process mapping is
fatal: the organisation changes underneath you and the map is stale before the
readout.
