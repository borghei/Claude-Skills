# Red Flags: AI Feature PRD

> Common ways this skill's output goes wrong — concrete examples, why they're bad, and how to fix them.

## How to use this document

Scan before sharing the artifact. Each red flag shows the *bad* version next to the *good* version, anchored to the 11-section AI PRD structure (Sections 9-11 are AI-specific). Read this once before drafting and again before review.

---

## Red Flag 1: Hallucination-tolerance hand-waving

**Symptom.** Section 10 ("Eval & Safety Plan") describes hallucination risk in narrative prose but never names a tolerance number.

**Why it's bad.** Hallucination is statistical. Without a numeric bar, engineering ships and quality reviewers cannot pass or fail it. The team will relitigate the bar mid-build and lose two weeks doing it.

**Bad example:**
> "We will work hard to minimize hallucinations and ensure the assistant gives accurate, faithful answers. The team will monitor quality closely throughout development."

**Good example:**
> "Hallucination rate <= 2% measured via faithfulness check (RAGAS) against the 200-item gold set, evaluated weekly during build and monthly post-GA. A spike above 3.5% on a single weekly run triggers tightening of retrieval prompt and a re-eval before the next ramp stage."

**How to catch it.** Search Section 10 for "%" or "ms" or "$". If those characters do not appear, the targets are not numeric.

---

## Red Flag 2: No eval criteria before model selection

**Symptom.** Section 9.1 names a primary model ("claude-sonnet-4.5") before Section 10.1 has any golden set or acceptance bar defined.

**Why it's bad.** Karpathy's "Software 2.0" framing: the eval *is* the spec. Picking a model before defining what you are evaluating means you have no defensible reason for the choice — the team is buying a tool before knowing the job.

**Bad example:**
> "Section 9.1: Primary model is claude-sonnet-4.5 because it's the strongest model available today. Section 10.1: TBD — golden set under construction."

**Good example:**
> "Section 10.1: 200-item gold set covering 70% common / 20% edge / 10% adversarial cases for our domain. Acceptance >= 90%, hallucination <= 2%, refusal-on-harmful >= 98%. Section 9.1: Three candidate models scored against this gold set: claude-sonnet-4.5 (94% acceptance, 1.6% hallucination), gpt-5 (92%, 1.8%), Llama-4-70B (87%, 3.1%). Primary: claude-sonnet-4.5 — wins on hallucination at acceptable cost; gpt-5-mini as fallback for outage."

**How to catch it.** Read Section 9 before Section 10. If 9 names a model and 10 says "TBD", reorder the work.

---

## Red Flag 3: No fallback model

**Symptom.** Section 9.1 names a single primary model and stops. No fallback, no switch trigger.

**Why it's bad.** Frontier-model outages happen. Vendor pricing changes happen. Vendor deprecation happens (a model labeled "GA" today can be sunset in 6 months). A single-vendor PRD bakes in operational risk that nobody named.

**Bad example:**
> "Primary model: claude-sonnet-4.5 (Anthropic, via Bedrock). Reason chosen: best on our eval set."

**Good example:**
> "Primary: claude-sonnet-4.5 (via Bedrock). Fallback: gpt-5-mini (via Azure) for vendor outage; claude-haiku-4 for cost cap. Switch trigger: primary error rate > 2% sustained 10 min OR p95 latency > 2x baseline OR per-tenant cost > 120% of budget. Re-evaluate primary every 90 days; documented in 11.4."

**How to catch it.** Ask: "What happens if Anthropic Bedrock goes down for 4 hours?" If the PRD does not answer, the fallback is missing.

---

## Red Flag 4: 100% acceptance target

**Symptom.** Section 10.1 sets an acceptance rate of 100% (or >= 99%) for a non-trivial task.

**Why it's bad.** Real AI features land at 85-95% on hard tasks. A 100% acceptance target is a tell that either (a) the golden set is too easy, or (b) the team has not done eval work and is wishing. Either way, the bar will not survive contact with production.

**Bad example:**
> "Acceptance rate: 100% on the gold set, measured via human review."

**Good example:**
> "Acceptance rate: >= 90% on the 200-item gold set (target stretched from current baseline of 84%). Composition: 70% common, 20% edge, 10% adversarial. If we hit 95%+ in eval, we audit the gold set for difficulty (easy gold sets produce false confidence)."

**How to catch it.** Any threshold at 99% or 100% on the gold set is suspect on day 1.

---

## Red Flag 5: Eval golden set as "TBD"

**Symptom.** Section 10.2 lists "Golden set: TBD — will compile during build" or similar.

**Why it's bad.** Without a gold set in source control on day 1, the team has no objective signal during the build. Prompts will be tuned against the engineer's gut, not against a measurable target. The first time the gold set exists is post-launch, when the team is firefighting.

**Bad example:**
> "Section 10.2 Golden set: To be compiled during the build phase. ML team owns. Will be in source control before launch."

**Good example:**
> "Section 10.2 Golden set: 200 examples committed at `evals/assistant_v1/gold.jsonl`, frozen 2026-05-22. Composition: 140 common (70%) sourced from production logs of the legacy system; 40 edge (20%) curated with Support; 20 adversarial (10%) curated with Safety. Updates via PR with two-reviewer approval. PM (Sarah K) owns the set; ML (Tomas R) owns the runner."

**How to catch it.** Open the eval repo. If the gold set does not exist as a committed file, the PRD is not ready.

---

## Red Flag 6: Refusal policy is vague

**Symptom.** Section 10.4 says "the assistant refuses harmful requests" with no enumeration of categories or examples.

**Why it's bad.** A vague refusal policy produces inconsistent product behavior. Engineering ships prompts that refuse some things and answer others, with no shared standard. Users complain about both over-refusal and under-refusal in the same week.

**Bad example:**
> "The assistant should refuse harmful, unsafe, or off-policy requests, and redirect to support where appropriate."

**Good example:**
> "Refusal policy follows OpenAI Model Spec structure. (1) Never: generate code intended to compromise systems, give medical diagnoses, provide legal advice on the user's specific case. (2) Refuse: requests for hate speech, sexual content, instructions for mass-casualty weapons. (3) Redirect: questions outside our product scope ('use the help center'). (4) Answer plainly: everything else. Anthropic Acceptable Use Policy adopted by reference. Red-team set of 200 prompts in `evals/refusal/`; refusal-on-harmful >= 98%, refusal-on-benign <= 5%."

**How to catch it.** If the policy fits in one sentence, it is not a policy.

---

## Red Flag 7: No human-in-the-loop on high-stakes actions

**Symptom.** Section 10.6 omits a hard gate for actions that affect money, accounts, or external communication.

**Why it's bad.** A model that auto-executes an action (sends an email, changes a billing entry, deletes a file) on behalf of a user can do irreversible harm. Anthropic's RSP and most AI safety frameworks require human approval on high-stakes actions for good reason.

**Bad example:**
> "The assistant can take any action the user asks for, via the tools provided. Confidence threshold of 0.7 governs whether actions execute."

**Good example:**
> "Hard gate: any action that (a) spends money, (b) sends external communication, (c) modifies account configuration, or (d) deletes data requires explicit user confirmation in the UI before execution. Soft gate: model self-rated confidence < 0.85 routes to a review queue. Sampling: 1% of executed actions audited weekly by domain experts. Escalation: 3 consecutive 'I do not know' responses or 2 negative feedback in same session triggers handoff to a human agent."

**How to catch it.** List every tool the agent has. For each, ask "what if it fires wrongly?" If the answer is "the user is harmed", you need a hard gate.

---

## Red Flag 8: Cost model assumes today's traffic

**Symptom.** Section 11.1 projects $X/month based on current MAU. No 10x scenario.

**Why it's bad.** Per-token cost is roughly linear with traffic. A feature that costs $5k/month at 100k MAU costs $50k/month at 1M MAU. The PRD is a funding artifact; under-projecting the scale case strands the team in a budget crisis at month 6.

**Bad example:**
> "Cost: $4,500/month based on projected 80k MAU and average 12 tokens/interaction. Within budget."

**Good example:**
> "Cost model: $4,500/month at projected 80k MAU (60k requests/day x 1,400 avg tokens x $0.000007). 10x scenario (800k MAU): $45,000/month. Per-tenant meter alerts at 80% and 100% of monthly tenant budget; auto-throttle at 120%. Cost-per-successful-interaction (CSI) tracked weekly — divides cost by acceptance rate, so cheap-but-bad models lose. Sensitivity model in engineering/llm-cost-optimizer/."

**How to catch it.** Multiply the cost line by 10. If the team has not seen that number, they have not modeled scale.

---

## Red Flag 9: EU AI Act risk tier not declared

**Symptom.** Section 10.7 ethical checklist skips the EU AI Act tier declaration ("Minimal / Limited / High / Unacceptable"). Or marks it "Minimal" without justification.

**Why it's bad.** A High-risk classification adds materially to scope (conformity assessment, post-market monitoring, data governance documentation). Discovering this at the eleventh hour from Legal kills launches. The dates matter too (as of September 2026): Limited-risk transparency duties apply from 2 August 2026; Annex III High-risk obligations from 2 December 2027 and Annex I (product-embedded) from 2 August 2028, after the Digital Omnibus deferral. A PRD that says "High-risk, but not until 2026" is working from the pre-Omnibus timeline -- see `ai-pm-frameworks-guide.md` Section 4.

**Bad example:**
> "Ethical checklist: [ ] Have we considered the EU AI Act? -- Yes, we think this is Minimal risk."

**Good example:**
> "EU AI Act classification: **Limited risk**. Justification: assistant is conversational, not making decisions about employment, credit, healthcare, or biometrics; users are informed they are interacting with AI; no automated decision-making about EU subjects. Reviewed with ra-qm-team/eu-ai-act-specialist/ on 2026-05-20. If usage drifts to credit/employment/healthcare decisions, we re-classify as High-risk and pause."

**How to catch it.** Section 10.7 must name a tier and cite who reviewed it.

---

## Red Flag 10: Deployment ramp without gate metrics

**Symptom.** Section 11.3 lists ramp stages (Shadow -> Internal -> Canary -> Percent -> GA) without specifying what metric must be green to advance.

**Why it's bad.** Without pre-agreed gates, advancement becomes a calendar decision rather than a metric decision. Teams ramp because "it's Thursday and the plan said canary this week," not because eval is passing.

**Bad example:**
> "Deployment: Shadow week 1, Internal week 2, Canary week 3, then 10/25/50/100%."

**Good example:**
> "Stage -> Gate to advance: Shadow -> logs reviewed, no crashes, eval >= 88% on gold set; Internal (employees) -> acceptance >= 85%, 0 P0 safety incidents in 1 week; Canary (5%) -> acceptance >= 90%, no regression vs baseline on win-rate, cost-per-interaction within $0.05; Percent (10/25/50%) -> each step held >= 3 days, metrics within bounds; GA -> stable for 2 weeks, runbook in place. Owner per gate: Eng Lead (technical), PM (product), Safety (refusal/hallucination)."

**How to catch it.** Ask: "What number is wrong if the ramp halts?" If the team cannot answer per stage, the gates are not real.

---

## Red Flag 11: Prompt versioning skipped

**Symptom.** Section 11.4 ("Lifecycle") does not require prompts in source control with PR review and eval delta.

**Why it's bad.** Prompts drift. A small change to a system prompt can move acceptance 5 points without anyone noticing. Six months later, nobody knows what the live prompt is or who changed it.

**Bad example:**
> "Prompts are maintained by the ML team. We will document major changes."

**Good example:**
> "Every prompt change is a PR against `prompts/assistant/system.txt` with: (1) eval delta on the gold set, (2) reviewer approval, (3) semantic version bump. Production prompt is read from a versioned config; rollback is a config change, not a deploy. Prompt audit runs monthly; orphan prompts are deleted."

**How to catch it.** Open the prompt file in main branch. If it is not version-controlled or has no recent commit history with reviews, the discipline is missing.

---

## Red Flag 12: No production-eval / online sampling

**Symptom.** The team relies entirely on the offline gold set; no sampling of production traffic.

**Why it's bad.** Offline evals measure what the team designed for. Production traffic is what users actually do. Drift between the two is silent until users complain or revenue moves.

**Bad example:**
> "Eval cadence: weekly run against the gold set. Production traces logged but not evaluated."

**Good example:**
> "Offline: weekly gold-set run (Promptfoo + Langfuse). Online: 2% of production traffic sampled, evaluated by Langfuse trace-eval with the same rubric as the gold set. Weekly review of sample failures by PM + domain expert. Drift alert: if online acceptance drops >= 3 points below gold-set acceptance for 2 consecutive weeks, freeze ramp and re-evaluate."

**How to catch it.** Ask: "How would you notice if quality drops in production tomorrow?" If the answer is "users will tell us", the online eval is missing.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | Hallucination-tolerance hand-waving | Does Section 10 contain a numeric threshold (with %)? |
| 2 | No eval criteria before model selection | Was the gold set defined before Section 9.1 named a model? |
| 3 | No fallback model | What happens if the primary vendor goes down for 4 hours? |
| 4 | 100% acceptance target | Is any threshold >= 99% on a non-trivial gold set? |
| 5 | Eval golden set as "TBD" | Does the gold set exist as a committed file today? |
| 6 | Refusal policy vague | Is the policy more than one sentence and enumerated? |
| 7 | No HIL on high-stakes actions | Can the agent execute money/comms/account actions without confirmation? |
| 8 | Cost model assumes today's traffic | Is there a 10x scenario in Section 11.1? |
| 9 | EU AI Act tier not declared | Does Section 10.7 name a tier with justification? |
| 10 | Ramp without gate metrics | Can you name the metric that halts each stage? |
| 11 | Prompt versioning skipped | Is the prompt in source control with PR review? |
| 12 | No production-eval / online sampling | How would you notice quality dropping tomorrow? |

## Related Reading

- SKILL.md Troubleshooting
- references/ai-pm-frameworks-guide.md
- references/eval-design-guide.md
- `ra-qm-team/eu-ai-act-specialist/` (for the tier declaration)
- `engineering/llm-cost-optimizer/` (for the cost math)
