# Lean Process Analysis

Diagnostic methods and threshold numbers for analysing a mapped process. Capture
technique lives in `process-capture-methods.md`; this file is what to do with the
data once you have it.

---

## 1. The core metrics

| Metric | Formula | What it tells you |
|--------|---------|-------------------|
| Touch time | Sum of process time across steps | Labour actually consumed per unit |
| Wait time | Sum of queue/delay time between and within steps | Time the work sits idle |
| Lead time | Touch + wait | What the customer experiences |
| Process cycle efficiency (PCE) | Value-added time / lead time | Share of elapsed time that is real work |
| Value-added ratio | Value-added time / total touch time | Share of *effort* that is real work |
| First-pass yield (FPY) | Product of (1 - rework rate) across steps | Share of units that complete without rework |
| Rolled throughput | Same as FPY across a chain | Compounding effect of small defect rates |

**PCE and value-added ratio answer different questions and are routinely
confused.** A process can have an excellent value-added ratio (people do useful
work when they touch it) and a terrible PCE (the work sits in queues 95% of the
time). The first is a work-design problem; the second is a scheduling problem,
and they have completely different fixes. Always compute both.

### PCE benchmarks for transactional processes [PROVEN]

| PCE | Band | Typical situation |
|-----|------|-------------------|
| Below 5% | Poor | Un-improved multi-team process with approvals. Most processes start here. |
| 5-15% | Below average | Some flow established; queues still control lead time. |
| 15-25% | Average | Reasonable for a process crossing three or more teams. |
| 25-50% | Good | Strong flow. Remaining gains come from batch size and automation. |
| Above 50% | World class | Rare outside single-owner or automated processes. Verify the data first. |

Manufacturing benchmarks (often quoted at 25-30% for "world class") do not
transfer to office processes. A cross-functional approval process at 20% PCE is
performing well.

### First-pass yield: the compounding trap

Ten steps at 95% each yields `0.95^10 = 60%` first-pass yield. Individually
every step looks fine; four in ten units need rework somewhere. This is why
step-level quality targets mislead — **set the yield target end-to-end, then
derive the per-step requirement**, not the other way round.

| End-to-end FPY | Interpretation |
|---------------|----------------|
| Above 95% | Excellent. Rework is not your problem; look at flow. |
| 85-95% | Normal. Attack the top one or two rework loops. |
| 70-85% | Rework is a major cost. Fix quality before optimising speed. |
| Below 70% | The process is a rework engine. Nothing else you do will hold. |

---

## 2. The waste taxonomy

Eight classic wastes, translated to knowledge and service work:

| Waste | Office manifestation | Diagnostic signal |
|-------|---------------------|-------------------|
| Overproduction | Reports nobody reads; data captured "just in case" | Output with no named consumer |
| Waiting | Approval queues, waiting on another team | High wait/touch ratio |
| Transport | Handing files between systems and teams | System switches per unit |
| Over-processing | Approvals that never reject; duplicate checks | Approval rejection rate near 0% |
| Inventory | Backlogs, work-in-progress queues | Items open longer than lead time |
| Motion | Hunting for information across systems | Steps whose work is "finding" |
| Defects | Rework, corrections, returned submissions | Rework rate per step |
| Unused talent | Senior people on clerical steps | Seniority mismatched to step type |

**The highest-yield diagnostic in office processes: find every approval step and
measure its rejection rate.** An approval that rejects under 5% of the time is
not a control, it is a queue with a job title. Either it is unnecessary, or the
real control belongs upstream where the error is created.

---

## 3. Diagnostic thresholds

Apply these to a mapped process to locate problems fast.

| Signal | Threshold | Interpretation |
|--------|-----------|----------------|
| Step share of lead time | Above 20% | This step is the constraint |
| Wait/touch ratio on a step | Above 3x | A queue, not work |
| Wait/touch ratio | Above 10x | Batch-and-queue scheduling; the fix is policy, not capacity |
| Rework rate on a step | Above 10% | Fix before any speed work |
| Rework rate | Above 20% | The step's inputs are wrong; move the check upstream |
| Handoff density | Above 0.5 per step | Fragmented ownership |
| Share of wait at handoffs | Above 60% | Optimise between teams, not inside them |
| Non-value-added touch time | Above 25% | Eliminate before automating |
| Approval rejection rate | Below 5% | The approval is theatre |
| System switches | Any | Each is a re-keying and data-loss point |

### Reading a wait/touch ratio

A 25-minute credit check that takes two days elapsed has a ratio of about 38x.
That is not a slow credit check — it is a credit check that waits in an inbox.
Adding a second person to run credit checks would change nothing. **The fix for
a high wait/touch ratio is always scheduling: batch size, WIP limits, triggers,
or service-level commitments — never capacity.**

The mistake this prevents is expensive and common: teams see "this step takes
two days" and hire, when the step takes 25 minutes and the queue takes two days.

---

## 4. Little's Law

```
Work in progress = Throughput x Lead time
   =>  Lead time = WIP / Throughput
```

The most useful law in process work because it says lead time can be cut without
anyone working faster: **halve the WIP and you halve the lead time, at constant
throughput.**

Practical applications:

- A team with 40 open items completing 10 per week has a 4-week lead time. Cap
  WIP at 20 and lead time falls to 2 weeks — same people, same speed.
- If lead time is rising while throughput is flat, WIP is growing. Stop starting
  work; start finishing it.
- Quoting a lead time is only credible if you know current WIP. Without it, any
  date is a guess.

### Queueing and utilisation

Lead time rises non-linearly with utilisation. At 50% utilisation a step adds
about 1x its work time in queue; at 80% about 4x; at 90% about 9x; at 95% about
19x. This is why a process where everyone is "fully utilised" has terrible lead
times and why adding capacity to a 95%-utilised step produces a dramatic,
apparently disproportionate improvement.

**Target 70-85% utilisation on any step you want to be responsive.** Deliberate
slack at the constraint is what makes flow possible.

---

## 5. Finding and treating the constraint

A process has exactly one constraint at a time. Improving anything else changes
nothing measurable — which is why broad "efficiency programmes" so often deliver
no lead-time improvement despite real local gains.

The five-step sequence:

1. **Identify** the constraint — the step with the largest share of lead time,
   or the one where work visibly accumulates in front.
2. **Exploit** it — make sure it is never idle or doing work it should not:
   remove non-constraint work, ensure inputs arrive complete and ready.
3. **Subordinate** everything else — upstream steps release work at the pace the
   constraint can absorb. Running upstream flat out just grows the queue.
4. **Elevate** it — only now add capacity, automation, or people.
5. **Repeat** — the constraint moves once relieved. Re-measure; do not assume.

Steps 2 and 3 are free and are almost always skipped in favour of step 4, which
costs money. **Exhaust exploitation and subordination before spending anything.**

---

## 6. The improvement hierarchy

Applied to the same step, earlier verbs beat later ones:

| Rank | Verb | Question | Typical lead-time gain |
|------|------|----------|----------------------|
| 1 | **Eliminate** | Does this need to happen at all? | 100% of the step |
| 2 | **Consolidate** | Can one owner do this and the adjacent step? | Removes a handoff and its queue |
| 3 | **Parallelise** | Must this wait for the previous step? | Up to the shorter branch |
| 4 | **Standardise** | Can variation be removed so it is predictable? | 20-40%, plus rework reduction |
| 5 | **Automate** | Can a system do it? | 60-90% of touch time |

**Automating a step you should have eliminated makes the waste permanent and
expensive to remove.** Automation encodes the current process in software; every
subsequent change now requires a development cycle. Run the first four questions
before writing any code.

Parallelisation is the most under-used lever in approval-heavy processes.
Sequential credit check, legal review, and security review usually have no real
dependency on each other — they are sequential because the process was drawn as
a line.

---

## 7. Valuing improvements honestly

Two different currencies, routinely conflated:

| Saving | Currency | Costable? |
|--------|----------|-----------|
| Touch time removed | Labour hours | Yes — hours x loaded rate |
| Wait time removed | Lead time | Only if the business has quantified it |

**Removing a queue frees nobody's hours.** Cutting two days of waiting from an
order process saves zero labour cost; it may be enormously valuable through
faster revenue recognition, higher win rates, or lower churn — but that value
must come from the business, not be inferred by the analyst.

The standard inflation error: multiplying total lead-time reduction by a loaded
hourly rate. A 1,500-minute lead-time saving at $72/hour "saves" $1,800 per unit
that no budget will ever show. Finance will find this in the first review, and
the credibility loss contaminates the genuine savings in the same document.

State the two separately:

> Removes 60 minutes of touch time per order (98 orders/month = $4,200/month) and
> 25 hours of lead time per order. Sales estimates the cycle-time reduction is
> worth $180K annually in improved win rate — their number, not ours.

### Discounting

Apply confidence and risk factors before presenting, not after challenge:

| Confidence in the saving | Factor | Delivery risk | Factor |
|-------------------------|--------|--------------|--------|
| Measured directly | 1.00 | Low — reversible, single team | 1.00 |
| Estimated from similar work | 0.75 | Medium — cross-team, reversible | 0.85 |
| Asserted, not measured | 0.50 | High — irreversible or many stakeholders | 0.65 |

An unmeasured saving in a high-risk change is worth about a third of its claimed
value. If that still clears the payback bar, it is a genuinely good idea.

---

## 8. Sequencing the backlog

| Tier | Payback | Action |
|------|---------|--------|
| NOW | Under 3 months | Start this quarter |
| NEXT | 3-6 months | Queue behind NOW items |
| LATER | 6-12 months, or over 20 days effort | Needs a business case of its own |
| DROP | Over 12 months or negative | Revisit only if volume changes |

Two rules that override payback:

1. **Fix rework before speed.** A process at 70% first-pass yield cannot hold any
   flow improvement — the rework loop will absorb it. Sequence quality fixes
   first even when a speed fix has better payback.
2. **Respect dependencies.** An improvement scheduled before something it depends
   on will either slip or be delivered on a foundation that is not there yet.

Anything above 20 days of effort is a project, not a process improvement. It
needs a sponsor, a plan, and its own governance — treating it as a backlog item
is how six-month initiatives get started by accident.
