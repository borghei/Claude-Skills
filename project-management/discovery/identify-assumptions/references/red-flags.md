# Red Flags: Identify Assumptions

> Common ways this skill's output goes wrong — concrete examples, why they're bad, and how to fix them. Pair with the SKILL.md and Troubleshooting table.

## How to use this document

When you have just produced an assumption map or risk-prioritization output, scan the red flags below. Each red flag shows a *bad* and *good* version, anchored in Torres' four risk categories and the extended 8-category model.

---

## Red Flag 1: Assumption Inflation ("Everything Is Risky")

**Symptom.** Assumption map lists 47 assumptions, all rated high-impact/high-uncertainty. Team is paralyzed; nothing can be tested in priority order.

**Why it's bad.** Risk-everywhere is risk-nowhere. The point of the map is to *separate* the load-bearing assumptions from the ambient ones, so the team can run targeted experiments. An inflated map produces analysis paralysis.

**Bad example:**
> Assumption map: 47 items, all rated 9/10 impact and 9/10 uncertainty. Devil's advocate enabled.

**Good example:**
> Assumption map: 47 raw assumptions. Re-rated: 5 are load-bearing (high impact + high uncertainty), 12 are medium, 30 are low-stakes. Top 5 become the experiment backlog this quarter. Mediums get monitored; lows accepted."

**How to catch it.** What percentage of assumptions are in the top-right quadrant (high impact + high uncertainty)? Above 20% means inflation.

---

## Red Flag 2: Confusing Assumptions with Facts

**Symptom.** Map lists "users want a faster checkout" as a low-uncertainty assumption because "we know this." No supporting evidence cited.

**Why it's bad.** The point of the map is to surface beliefs that *feel* true but are actually unvalidated. Tagging unvalidated beliefs as "facts" defeats the exercise. Torres specifically warns that the most dangerous assumptions feel obviously true.

**Bad example:**
> "Assumption: 'Users want a faster checkout'. Uncertainty: low (we know this)."

**Good example:**
> "Assumption: 'Users want a faster checkout'. Evidence supporting: zero quantitative, 2 anecdotal mentions. Evidence against: support tickets are about errors, not speed. Uncertainty: actually high. Promote to top 5."

**How to catch it.** For each low-uncertainty assumption, demand the evidence. "We know this" is not evidence.

---

## Red Flag 3: Missing Categories (Only Tested What You Wanted to Test)

**Symptom.** All assumptions are about Value (will customers want this?). Nothing about Usability, Viability, Feasibility, or any of the extended 4 (Ethics, Go-to-Market, Strategy, Team).

**Why it's bad.** A map that covers only one category is a confirmation tool, not a risk map. Real projects fail across multiple risk categories — the most expensive failures come from categories the team did not examine.

**Bad example:**
> Map: 12 Value assumptions. No Usability, no Viability, no Feasibility. Team confident the product is desired; ships; users cannot figure out the onboarding.

**Good example:**
> Map: balanced across all 4 (or 8) categories. Value: 4 assumptions. Usability: 3. Viability: 3. Feasibility: 4. Devil's advocate review: each category surfaces at least 1 medium+ assumption."

**How to catch it.** Count assumptions per category. If any category has zero, you skipped it intentionally or accidentally.

---

## Red Flag 4: Assumptions Phrased So Vaguely They Cannot Be Tested

**Symptom.** "Users will engage with the feature." No definition of engagement, no measurable threshold, no target population.

**Why it's bad.** Vague assumptions cannot be falsified by an experiment. The whole point of identifying them is to design experiments that can disprove them. Vagueness defeats the experiment-design step.

**Bad example:**
> "Assumption: 'Users will adopt the feature.'"

**Good example:**
> "Assumption: 'At least 30% of trial users (Y) will use the new dashboard at least twice in week 1 (Z).' Testable via cohort analysis; threshold is concrete. If <20%, the assumption fails."

**How to catch it.** Can you design a falsifying experiment for the assumption *as written*? If not, the assumption is too vague.

---

## Red Flag 5: One-Person Devil's Advocate (No Cross-Perspective Stress Test)

**Symptom.** PM alone wrote the assumption map. Plays devil's advocate against own assumptions. Predictably finds them all reasonable.

**Why it's bad.** The trio (PM + Designer + Engineer) is in the SKILL.md because each perspective surfaces different assumptions. An engineer sees feasibility risks the PM does not; a designer sees usability risks the engineer does not. Solo mapping is a confirmation echo chamber.

**Bad example:**
> PM creates map alone, marks all assumptions as low-medium risk. No engineering perspective on feasibility.

**Good example:**
> Trio runs the map together. PM lists 8 Value assumptions; Designer adds 4 Usability; Engineer flags 3 Feasibility (one of which is critical — 'the third-party API we're depending on has a 99.5% SLA, not 99.9% as the PRD assumes'). Engineer's catch advances to top of experiment backlog."

**How to catch it.** Was the map produced by 1 person or a cross-functional trio? Solo maps are weaker by definition.

---

## Red Flag 6: Mistaking the Easiest Assumption to Test for the Most Important

**Symptom.** Team picks the assumption that has the easiest experiment, not the one that is most load-bearing. Builds confidence in the wrong thing.

**Why it's bad.** Selection bias toward easy experiments produces a portfolio of validated-but-irrelevant assumptions. The most dangerous assumption is the one that nobody wants to test because the experiment is hard. Discipline = test the riskiest, even when uncomfortable.

**Bad example:**
> "We tested the assumption that 'users will click the new button' (easy A/B test). Validated. Proceeding to build the whole feature." (The hard assumption — 'enterprise IT will approve our SOC 2 status' — went untested.)

**Good example:**
> "Top assumption: 'Enterprise IT will approve our security posture.' Hard to test but load-bearing. Designed a paper-SOC-2 exercise with 3 target customers' IT teams. Found 2 blockers; surfaced 4 weeks before we would have hit them post-build."

**How to catch it.** Rank-order assumptions by impact-on-failure. Are you testing the top 3 first? If you are testing the easiest 3, you optimized for comfort.

---

## Red Flag 7: No Ownership of Assumptions

**Symptom.** Map has 12 assumptions. No name attached to any. Two weeks later, none have been tested.

**Why it's bad.** Unowned assumptions stagnate. The map is just paperwork unless each top assumption has someone responsible for designing and running the next experiment. Continuous discovery (Torres) is a cadence; cadence requires ownership.

**Bad example:**
> Map: 12 assumptions. Next step: "we'll figure out experiments at next planning."

**Good example:**
> Map: 12 assumptions. Top 5 assigned: A1 to PM, A2 to PM, A3 to designer, A4 to engineer (feasibility spike), A5 to PM. Each owner brings an experiment design to next sprint planning. Review weekly."

**How to catch it.** Each top assumption needs a name and a date. If either is missing, ownership is fake.

---

## Red Flag 8: Treating Assumptions Test as One-Shot

**Symptom.** Run one experiment; treat the assumption as "validated forever." Two quarters later, the assumption is wrong because the world changed.

**Why it's bad.** Assumptions decay. Market conditions shift, customer needs evolve, competitor moves invalidate prior conclusions. Torres' continuous discovery means re-testing the load-bearing assumptions on a cadence, not once.

**Bad example:**
> "We validated in Q2 that enterprise customers want feature X. Building it now in Q4." (Market shifted; competitor launched it free; customer demand collapsed.)

**Good example:**
> "Validated in Q2. Re-validated in Q3 via 3 customer check-ins (assumption still holds, but pricing sensitivity has shifted). Continuing in Q4 with updated pricing. Quarterly re-validation cadence."

**How to catch it.** When was each load-bearing assumption last validated? If over 6 months ago, it is potentially stale.

---

## Red Flag 9: Conflating Risk and Likelihood

**Symptom.** Map ranks all "high impact" assumptions as critical, regardless of how likely they are to fail.

**Why it's bad.** Risk = impact x probability. A high-impact assumption that is well-evidenced (low probability of failure) is less urgent than a medium-impact assumption with no evidence. The two-axis model in the SKILL.md (impact + uncertainty) exists for this reason.

**Bad example:**
> "Assumption: 'Our cloud provider will not go down during launch'. Impact: high. Priority: critical." (Cloud provider has 99.99% SLA; well-evidenced low probability of failure.)

**Good example:**
> "Assumption: 'Our cloud provider will not go down'. Impact: high. Uncertainty: low (99.99% SLA, evidence). Risk priority: low — monitor, do not test. Resources to actually risky assumptions."

**How to catch it.** Is impact alone driving priority? Combine with uncertainty/probability of failure.

---

## Red Flag 10: Missing Ethics and Strategy Categories for AI / Risky Features

**Symptom.** For an AI-enabled feature, the assumption map has no items in the Ethics or Strategy categories (extended 8-category model).

**Why it's bad.** AI features have category-specific risks: hallucination, bias, regulatory, reputation, opportunity cost. A map that omits these categories for an AI feature is missing the most likely failure modes.

**Bad example:**
> AI summarization feature. Assumption map: Value, Usability, Viability, Feasibility. No Ethics category.

**Good example:**
> AI summarization feature. Map includes Ethics: 'Summaries will not hallucinate facts at a rate >2%'; 'Summaries will not exhibit racial/gender bias in stress tests'; 'Output will not violate customer NDAs (data leakage)'. Tests designed for each."

**How to catch it.** For AI, security, or compliance-sensitive features, does the map include Ethics and Strategy? If not, you skipped the most failure-prone categories.

---

## Red Flag 11: Assumption Map That Never Updates

**Symptom.** Initial map created in Q1. No revisions in Q2, Q3. New customer insights, experiment results, and competitor moves never make it back into the map.

**Why it's bad.** A static map is a stale map. Assumptions resolve (validated or invalidated), new ones emerge from experiments, and the priority list shifts. A map that does not move is a relic, not a tool.

**Bad example:**
> Map created January. Same 12 assumptions still listed in October, none marked validated or invalidated.

**Good example:**
> Map updated bi-weekly. Status column: 'Tested - validated', 'Tested - invalidated', 'Testing in progress', 'Not yet tested'. New assumptions added from interview-synthesis output. Old assumptions retired. Living document."

**How to catch it.** When was the map last updated? If over 30 days, it is no longer steering the team.

---

## Red Flag 12: Skipping the Map for "Obviously Risky" Projects

**Symptom.** "This project is huge; we know it's risky. Let's just start building." No map produced.

**Why it's bad.** "Obviously risky" projects are exactly where the map is most valuable — they have the most assumptions to map and the most expensive failures. Skipping the map because the project feels risky is like skipping the safety checklist before takeoff because the flight is long.

**Bad example:**
> "We're rebuilding the entire onboarding. Too big to map every assumption. Let's just start." [6 months later: rebuild ships, activation drops 12%; 8 of the top assumptions were wrong.]

**Good example:**
> "We're rebuilding onboarding. Stakes are high; we ran a 2-day mapping workshop. Top 7 assumptions identified. Tested 4 via discovery before committing to build (3 invalidated, 1 confirmed, 1 partial). Rebuild scope changed substantially."

**How to catch it.** For high-stakes projects, did you produce an assumption map *before* committing? If not, you walked into the project blind.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | Assumption Inflation | Top-right quadrant under 20% of total? |
| 2 | Beliefs as Facts | Evidence cited for every low-uncertainty rating? |
| 3 | Missing Categories | All 4 (or 8) categories have at least one assumption? |
| 4 | Vague Assumptions | Could you design a falsifying experiment? |
| 5 | Solo Devil's Advocate | Trio (PM + Designer + Engineer) produced the map? |
| 6 | Easiest Tested First | Top 3 by impact tested first, not easiest? |
| 7 | No Ownership | Each top assumption has owner + date? |
| 8 | One-Shot Test | Quarterly re-validation cadence for load-bearing? |
| 9 | Impact Only, No Probability | Both axes (impact + uncertainty) drive priority? |
| 10 | Missing Ethics for AI | Ethics + Strategy covered for AI/risky? |
| 11 | Static Map | Last updated within 30 days? |
| 12 | Skipping for "Obviously Risky" | High-stakes project mapped before committing? |

## Related Reading

- SKILL.md Troubleshooting section (for symptom -> root cause -> resolution)
- references/risk-categories.md (for the 4 + 4 category definitions, if present)
- brainstorm-experiments/references/red-flags.md (for experiment design after mapping)
- customer-interview-script/references/red-flags.md (for interview-based testing)
