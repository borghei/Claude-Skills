# PRD: [AI Feature Name]

**Version:** 0.1 (draft)
**Owner:** [PM name]
**Last updated:** 2026-05-22
**Status:** Draft / In Review / Approved / Shipped
**EU AI Act risk tier:** Minimal / Limited / High / Unacceptable

---

## 1. Summary

[2-3 sentences. What the AI feature is, who it is for, why now. Name the model class explicitly (e.g., "a Claude Sonnet-4.5 based assistant"). Avoid marketing language.]

## 2. Contacts

| Name | Role | Responsibility |
|---|---|---|
| | Product Manager | Final scope decision |
| | Engineering Lead | Technical feasibility |
| | Design Lead | UX direction |
| | ML / Applied Research Lead | Model + eval ownership |
| | Safety / Trust reviewer | Refusal policy, red-team sign-off |
| | Legal / Compliance | Risk tier, DPA, data flow |
| | Sponsor / Stakeholder | Business approval |

## 3. Background

- **Context:** [What exists today? What is the deterministic / current baseline?]
- **Why now:** [Model capability that unblocks this. Customer or business pressure. Regulatory clarity.]
- **What recently became possible:** [The specific frontier-model capability, internal data, or partner enabling this initiative.]
- **AI premium:** [Why does this need to be AI, not a deterministic feature? Be specific. If you cannot answer this credibly, reconsider.]

## 4. Objective

- **Business benefit:** [How this moves revenue, retention, cost, share]
- **Customer benefit:** [How this improves the user's life]

**Key Results:**
- KR1: [Quality metric] from [current] to [target] by [date]
- KR2: [Adoption metric] from [current] to [target] by [date]
- KR3: [Cost metric] kept below [target] through [date]
- KR4: [Safety metric, e.g. refusal-on-harmful >= 98%] by [date]

## 5. Market Segments

**Included:**
- [Segment]: People who need to [job] because [context].

**Excluded for safety reasons:**
- [e.g., minors; users in healthcare advice contexts; users in jurisdictions where this feature is restricted].

## 6. Value Proposition

For [primary segment]:
- **Jobs addressed:** [...]
- **Gains created:** [...]
- **Pains relieved:** [...]
- **Competitive advantage:** [...]

## 7. Solution

**UX patterns for non-determinism:** [Cite-source? Regenerate button? Confidence indicator? Undo? Escape hatch to human?]

**Key features:**
1. [Feature] -- P0
2. [Feature] -- P1
3. [Feature] -- P2

**Prompt sketch (contract, not the production prompt):**

```
Role: <who the assistant is>
Goal: <primary task>
Inputs: <context passed>
Constraints: <refusal scope, style>
Output format: <schema or shape>
Tools: <tool list with one-line descriptions>
```

**Assumptions:**
- [Assumption] -- Validation plan: [how + when]

## 8. Release

- **Relative timeline:** [Now / Next / Later or T-shirt size]
- **v1 scope:** [What ships]
- **Explicitly deferred:** [What is intentionally excluded from v1]
- **Success criteria:** [Link to KRs in Section 4]

---

## 9. AI System Design

### 9.1 Model selection rationale

| Field | Value |
|---|---|
| Primary model | [vendor + model + version, e.g. `claude-sonnet-4.5` via Anthropic API] |
| Fallback model | [vendor + model + version] |
| Reason for primary | [Eval performance, cost, safety profile, latency] |
| Switch trigger to fallback | [Outage; cost overrun; eval regression] |
| Update / re-evaluation policy | Every 90 days against new releases |
| Vendor / data-residency considerations | [DPA in place? Region? Training opt-out confirmed?] |

### 9.2 Architecture pattern

Pattern chosen: [ ] Prompt only [ ] Few-shot [ ] RAG [ ] Fine-tune (SFT) [ ] RLHF / preference [ ] Agentic / tool use

| Pattern | Considered? | Why chosen / rejected |
|---|---|---|
| Prompt only | Yes / No | |
| Few-shot | Yes / No | |
| RAG | Yes / No | |
| Fine-tune (SFT) | Yes / No | |
| RLHF / preference | Yes / No | |
| Agentic | Yes / No | |

### 9.3 Data flow

[Diagram or describe: input -> preprocessing -> (retrieval?) -> model -> postprocessing -> output. Mark trust boundaries.]

| Aspect | Approach |
|---|---|
| User data leaving the boundary | [What goes to which vendor under which DPA] |
| PII handling | [Redacted? Hashed? Tokenized? Excluded from logs?] |
| Retention | [User input retention; output retention; training-data opt-out] |
| Logging | [What is logged, for how long, who can access] |

### 9.4 Prompt contract

```
[Sketch the system prompt structure. Production prompt lives in source control under prompts/<feature>/v<n>.txt with PR review.]
```

---

## 10. Eval & Safety Plan

### 10.1 Eval criteria

| Metric | Target | Method | Cadence |
|---|---|---|---|
| Acceptance rate | >= [%] | [Rubric / pairwise / LLM-as-judge] | Weekly |
| Hallucination rate | <= [%] | [Faithfulness / RAGAS / rubric] | Weekly |
| Refusal rate (benign) | <= [%] | Benign-set eval | Pre-launch + monthly |
| Refusal rate (harmful) | >= [%] | Red-team set | Pre-launch + on prompt change |
| p95 latency | < [ms] | Production telemetry | Continuous |
| Cost per interaction | < $[X] | Token accounting | Continuous |
| Win-rate vs baseline | > [%] | Pairwise | Before each model/prompt change |
| Format compliance | >= [%] | Auto-validation | Every release |
| Format-compliant output schema | [JSON schema link or inline] | -- | -- |

Eval tooling: [Promptfoo / Langfuse / Anthropic Console / Braintrust / OpenAI Evals / RAGAS / other]

### 10.2 Golden set

- **Size:** [N examples]
- **Composition:** [70% common / 20% edge / 10% adversarial -- adjust if needed]
- **Source:** [Production logs / user research / synthesized + human-reviewed]
- **Ownership:** PM owns the set; ML owns the run; both review failures weekly
- **Location:** [Source control path]
- **Refresh cadence:** [Quarterly; replace 10-20% of items]

### 10.3 Guardrails

| Layer | What it does | Implementation |
|---|---|---|
| Input filter | [Intent classification, PII strip, scope check] | [Tool / regex / classifier] |
| Pre-prompt | [System-prompt constraints] | [Reference prompt path] |
| In-model | [Choice of well-aligned model] | [Model name] |
| Output filter | [Content classification, PII, jailbreak-success] | [Tool] |
| Post-response | [Schema validation, citation check] | [Code path] |
| Human-in-loop | [Escalation queue trigger] | [Threshold + destination] |

### 10.4 Refusal policy

**Always refuse:**
- [Category + 2-3 concrete examples]

**Redirect / disclaim:**
- [Category + behavior]

**Clarify before answering:**
- [Category + behavior]

**Answer plainly:**
- [Everything not covered above]

Refusal-policy ownership: [Safety reviewer name]. Policy reviewed every [cadence].

### 10.5 Failure modes & graceful degradation

| Failure | Detection | Response |
|---|---|---|
| Primary model outage | Health check + error rate | Failover to fallback; degrade features |
| Quality regression | Eval CI alert | Roll back prompt/model; notify on-call |
| Hallucination spike | Faithfulness eval + user reports | Tighten retrieval; add citation requirement |
| Jailbreak success | Red-team monitor + output filter | Add to red-team set; patch system prompt |
| Cost spike | Per-tenant token meter | Throttle; downgrade model |
| Latency spike | p95 alert | Reduce context; cache; pre-warm |
| Drift | Online sampling | Re-evaluate model; refresh golden set |

### 10.6 Human-in-the-loop checkpoints

- **Hard gates** (never auto-execute): [List high-stakes actions]
- **Soft gates** (low-confidence -> review queue): [Confidence threshold + destination]
- **Sampling review:** [N%] of production traffic, [cadence], by [reviewer]
- **Escalation triggers:** [Explicit "I don't know"; repeat dissatisfaction; off-topic]

### 10.7 Ethical review checklist

- [ ] We identified who could be harmed by this feature.
- [ ] We tested with users from affected demographic groups.
- [ ] We considered the cost of a wrong answer in this domain.
- [ ] EU AI Act risk tier declared: [Minimal / Limited / High / Unacceptable] -- see `ra-qm-team/eu-ai-act-specialist/`.
- [ ] EU AI Act application date for this tier confirmed (as of Sept 2026: transparency 2 Aug 2026; high-risk Annex III 2 Dec 2027; Annex I 2 Aug 2028) -- see `references/ai-pm-frameworks-guide.md` Section 4.
- [ ] GDPR / HIPAA / COPPA / ADA reviewed for the data flow.
- [ ] Training-data provenance documented (if fine-tuning).
- [ ] Users informed they are interacting with AI.
- [ ] Non-AI alternative or escape hatch available.
- [ ] Disparate-impact subgroup eval planned.

---

## 11. Operations & Cost

### 11.1 Cost model

| Cost line | Formula | Estimate at scale |
|---|---|---|
| Inference (primary) | requests/mo x avg_tokens x $/token | $ |
| Inference (fallback) | <= 10% of primary | $ |
| Vector store / retrieval | docs x dimension x $/GB-mo | $ |
| Eval runs | golden_set x runs x $/call | $ |
| Human review | hours x rate | $ |
| Logging / observability | events/mo x $/event | $ |
| **Total** | | $ |

Use `engineering/llm-cost-optimizer/` to model variance.

### 11.2 Cost monitoring

- Per-tenant token meter; alert at 80%, auto-throttle at 120%.
- Daily cost dashboard.
- Cost-per-successful-interaction (CSI) tracked weekly.
- Variance review every Monday.

### 11.3 Deployment ramp

| Stage | Audience | Gate to next |
|---|---|---|
| Shadow | Mirrored traffic, no user output | Eval bar met; no crashes |
| Internal | Employees + invited testers | Acceptance >= 85%; no P0 safety incidents in 1 week |
| Canary | 1-5% of users | Acceptance >= 90%; cost in range; no regression |
| Percent rollout | 10% -> 25% -> 50% | Each step held >= 3 days; metrics within bounds |
| GA | 100% | Stable for 2 weeks; runbook in place |

Pair with `feature-flag-strategy/` for flag mechanics.

### 11.4 Lifecycle

- **Model refresh:** Re-evaluate primary against alternatives every 90 days.
- **Prompt versioning:** Every prompt change has a PR, an eval delta, a rollback path.
- **Golden-set refresh:** Replace 10-20% of items quarterly.
- **Deprecation / sunset:** [Criteria for sunsetting this feature or migrating to a new model.]

---

## Appendix A: Glossary

- **Golden set** -- a curated dataset used to measure quality consistently across model/prompt changes.
- **Pairwise eval** -- side-by-side comparison of two variants for human preference.
- **Faithfulness** -- the fraction of claims in the output that are supported by the retrieved context.
- **Refusal rate** -- the fraction of inputs to which the model declines to respond.
- **CSI** -- cost-per-successful-interaction; total cost divided by accepted outputs.

---

**Sign-offs:**

| Role | Name | Date |
|---|---|---|
| PM | | |
| Eng Lead | | |
| ML Lead | | |
| Safety reviewer | | |
| Legal / Compliance | | |
| Sponsor | | |
