---
name: process-mapper
description: >
  Map, measure and improve business processes — SIPOC and swimlane capture,
  cycle-time and bottleneck analysis, handoff diagnosis, and a payback-ranked
  improvement backlog. Use when a process is slow, error-prone, or crosses too
  many teams.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-operations
  domain: process-improvement
  updated: 2026-07-21
  tags: [process-mapping, lean, cycle-time, bottleneck, continuous-improvement]
---

# Process Mapper

Turns "this takes forever and nobody knows why" into a measured map with a
ranked backlog. Most process work fails on two things: it maps what people
describe rather than what runs, and it costs wait-time savings as if they were
labour savings. This skill is built to prevent both.

## When to use this skill

- **A process is slow** and nobody can say which step is responsible
- **Work bounces between teams** and the handoffs are suspected but not measured
- **Rework is high** — submissions get returned, tickets get reopened, orders get corrected
- **Before automating anything** — to check the step should exist at all
- **Onboarding a new team** onto an inherited process nobody has documented
- **An improvement programme needs a backlog** ranked by payback rather than by volume of complaint

## Inputs the skill expects

- Process boundaries: trigger event, terminal state, and the unit that flows through
- Step list with owner (role, not person), touch time, and wait time per step
- Wait times from system timestamps rather than self-report where possible
- Rework rate per step and the step each loop returns to
- System of record per step, to detect re-keying points
- Monthly volume and a loaded hourly cost, for valuing improvements

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which variant are we mapping, and what share of volume is it?** — mapping every exception produces an unreadable map; mapping a 20% path optimises the wrong process
- [ ] **Where do the wait times come from — timestamps or memory?** — self-reported queue time is understated by 40-70%, which moves the constraint to the wrong step
- [ ] **Is the goal lead time, labour cost, or quality?** — these have different constraints and often opposite fixes
- [ ] **Has the business quantified what faster is worth?** — without their number, cycle-time gains cannot be costed and must be argued separately

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Capture and measure the process

1. Scope first: agree trigger, terminal, unit, and variant on one page before any detail. Use the SIPOC frame in `assets/process-map-template.md`.
2. Observe the work happening before running a workshop. Observation finds the workaround spreadsheet and the chase email; workshops do not.
3. Pull wait times from system timestamps. Use median and 85th percentile, never mean — process-time distributions have long right tails.
4. Classify each step as value-added, business-value-added, or non-value-added. Test approvals by their rejection rate: below 5% and it is a queue with a job title.
5. Run the analyser and check the modelled lead time against measured end-to-end lead time. A gap above 20% means missing steps or, more often, missing wait.

```bash
python3 business-operations/process-mapper/scripts/process_analyzer.py \
  --input business-operations/process-mapper/assets/sample_process.json \
  --format text
```

### Workflow 2 — Diagnose handoffs and rework loops

1. Run the handoff analyser on the same process file — no separate input needed.
2. Read handoff density first. Above 0.5 owner changes per step, consolidating ownership beats optimising any individual step.
3. Check what share of total wait sits at handoffs. Above 60%, the problem is between teams and no amount of internal team improvement will move it.
4. Treat every system switch as a re-keying and data-loss point, and every cross-team rework loop as a check that belongs upstream of where it fires.
5. Look at ping-pong: an owner visited three or more separate times should own their segment end to end.

```bash
python3 business-operations/process-mapper/scripts/handoff_analyzer.py \
  --input business-operations/process-mapper/assets/sample_process.json \
  --format text
```

### Workflow 3 — Build the improvement backlog

1. Generate opportunities from the findings, applying the improvement hierarchy in order: eliminate, consolidate, parallelise, standardise, automate.
2. Split every saving into `touch_minutes_saved_per_unit` (labour, costed) and `lead_minutes_saved_per_unit` (elapsed, not costed). This split is the discipline that keeps the business case survivable.
3. Supply `annual_cycle_time_value` only when the business has quantified it — that figure is theirs, not the analyst's.
4. Run the scorer and read the tiers. Anything above 20 days of effort is a project needing its own sponsor, not a backlog item.
5. Override payback order in one case: if first-pass yield is below 85%, sequence the rework fixes first regardless of their payback. Flow improvements cannot hold on a process that reworks half its units.

```bash
python3 business-operations/process-mapper/scripts/improvement_scorer.py \
  --input business-operations/process-mapper/assets/sample_opportunities.json \
  --format json
```

## Decision frameworks

### Diagnostic thresholds [PROVEN]

| Signal | Threshold | What it means |
|--------|-----------|---------------|
| Step share of lead time | Above 20% | This is the constraint |
| Wait/touch ratio on a step | Above 3x | A queue, not work |
| Wait/touch ratio | Above 10x | Batch-and-queue scheduling; fix policy, not capacity |
| Rework rate per step | Above 10% | Fix before any speed work |
| First-pass yield end to end | Below 85% | Rework is the dominant cost |
| Handoff density | Above 0.5/step | Fragmented ownership |
| Wait sitting at handoffs | Above 60% | Optimise between teams, not inside them |
| Non-value-added touch time | Above 25% | Eliminate before automating |
| Approval rejection rate | Below 5% | The approval is theatre |

### Process cycle efficiency bands [PROVEN]

PCE = value-added time / lead time, for transactional processes:

| PCE | Band | Situation |
|-----|------|-----------|
| Below 5% | Poor | Un-improved multi-team process. Most start here. |
| 5-15% | Below average | Some flow; queues still control lead time. |
| 15-25% | Average | Reasonable across three or more teams. |
| 25-50% | Good | Strong flow. Remaining gains are batch size and automation. |
| Above 50% | World class | Rare outside single-owner processes. Check the data. |

Manufacturing benchmarks do not transfer. A cross-functional approval process at
20% PCE is performing well, not badly.

### The improvement hierarchy [PROVEN]

Applied to the same step, earlier verbs beat later ones:

| Rank | Verb | Question | Typical gain |
|------|------|----------|-------------|
| 1 | Eliminate | Does this need to happen at all? | 100% of the step |
| 2 | Consolidate | Can one owner do this and the next step? | Removes a handoff and its queue |
| 3 | Parallelise | Must this wait for the previous step? | Up to the shorter branch |
| 4 | Standardise | Can the variation be removed? | 20-40%, plus rework reduction |
| 5 | Automate | Can a system do it? | 60-90% of touch time |

**Automate last.** Automating a step you should have eliminated makes the waste
permanent and expensive to remove, because every future change now needs a
development cycle. Parallelisation is the most under-used lever in
approval-heavy processes — sequential credit, legal, and security reviews
usually have no real dependency and are sequential only because someone drew the
process as a line.

### Valuing a saving [PROVEN]

| Saving | Currency | Costable? |
|--------|----------|-----------|
| Touch time removed | Labour hours | Yes — hours x loaded rate |
| Wait time removed | Lead time | Only with a number from the business |

Removing a queue frees nobody's hours. It may be worth far more than the labour
saving through faster revenue or better win rates — but that value comes from
the business owner, not from the analyst's spreadsheet.

## Anti-Patterns

### Costing wait time as labour
**Mistake:** Multiplying total lead-time reduction by a loaded hourly rate — "we cut 25 hours per order at $72/hour, so we save $1,800 per order."
**Why it happens:** It produces a spectacular number from data already in hand, and the arithmetic looks identical to the legitimate touch-time calculation.
**Instead:** Cost only touch time as labour. Report lead-time reduction separately in its own units and ask the business owner what it is worth to them. Finance will find the inflated figure in the first review, and the credibility loss contaminates the genuine savings sitting in the same document.

### Mapping the described process
**Mistake:** Building the map from a workshop, an existing SOP, or interviews with managers, then analysing it as fact.
**Why it happens:** It is fast, it is comfortable, and everyone in the room believes their description is accurate. Nobody is lying — they are describing the process as designed, because the workarounds have become invisible through repetition.
**Instead:** Observe the work happening, and pull wait times from system timestamps. Then validate by reading the map back to the people who do it, asking "what did I get wrong?" rather than "does this look right?" If your modelled lead time is more than 20% below the measured figure, you are missing steps or missing wait — usually the chase emails and batch delays nobody thinks to mention.

### Optimising a non-constraint
**Mistake:** Running an improvement programme that makes six steps faster, then finding end-to-end lead time unchanged.
**Why it happens:** Improvement effort goes where the team is willing rather than where the constraint is, and every local gain is real and measurable — it just does not reach the customer.
**Instead:** Find the constraint, exploit and subordinate before spending anything, and only then add capacity. Improving a non-constraint step provably changes nothing at the process level. Re-measure after each fix, because the constraint moves once relieved.

### Automating before eliminating
**Mistake:** Commissioning software to speed up a step that should not exist — the classic being an automated approval workflow for an approval that rejects 2% of submissions.
**Why it happens:** Automation has a budget line, a vendor, and a visible deliverable. Eliminating a step requires persuading whoever owns it that their control is unnecessary, which is a political problem with no budget code.
**Instead:** Run the first four verbs of the improvement hierarchy before writing any code. Automation encodes the current process in software and makes every subsequent change a development project — so the cost of automating waste is not the build, it is the decade of paying to work around it.

## Files

| File | Purpose |
|------|---------|
| `scripts/process_analyzer.py` | Cycle time, PCE, value-added ratio, first-pass yield, rework cost, and constraint identification |
| `scripts/handoff_analyzer.py` | Handoff scoring, ping-pong detection, cross-team rework loops, system-switch mapping |
| `scripts/improvement_scorer.py` | Payback-tiered backlog separating labour savings from lead-time savings, with dependency sequencing checks |
| `references/lean-process-analysis.md` | Core metrics, PCE benchmarks, waste taxonomy, diagnostic thresholds, Little's Law, constraint sequence, honest valuation |
| `references/process-capture-methods.md` | Scoping, SIPOC, capture techniques ranked, per-step data fields, time-data rules, validation checks, engagement sequence |
| `assets/process-map-template.md` | Full map deliverable: SIPOC, swimlane, step detail, metrics, handoffs, backlog, validation checklist |
| `assets/sample_process.json` | Twelve-step order-to-activation process across seven owners with rework loops and system switches |
| `assets/sample_opportunities.json` | Eight improvement opportunities spanning all five improvement verbs, including two that correctly fail scoring |
