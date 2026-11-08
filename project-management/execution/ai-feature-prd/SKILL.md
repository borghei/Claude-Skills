---
name: ai-feature-prd
description: >
  Extends a PRD with model choice, eval and safety plan, guardrails, cost model and
  rollout gates for an AI or ML feature. Use when specifying any LLM, RAG, agent or ML
  feature, or replacing a rules-based flow with a model.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  tech-stack: ai-prd, ml-prd, llm-product, evals, guardrails, responsible-ai
  tags:
    - prd
    - ai-features
    - evals
    - guardrails
    - model-selection
---
# AI Feature PRD Expert

## Overview

AI and ML features break the assumptions a standard PRD takes for granted. Outputs are non-deterministic. Quality is statistical, not categorical. The "spec" is half product, half eval suite. A regular PRD that says "Search returns the top result" is replaced by "the assistant returns a helpful, harmless, on-policy answer with a refusal rate under 4% on the golden set, p95 latency under 1.8s, and cost-per-conversation under $0.05."

This skill produces an **AI Feature PRD** that extends the standard 8-section PRD (see `create-prd/`) with three additional sections built for the realities of shipping AI: **AI System Design** (Section 9), **Eval & Safety Plan** (Section 10), and **Operations & Cost** (Section 11). This is a template-based skill with no Python tool; the artifact is a markdown PRD. Background frameworks are in `references/ai-pm-frameworks-guide.md`.

## Core Capabilities

- **11-section AI PRD** — the standard 8-section spine plus AI System Design, Eval & Safety Plan, and Operations & Cost.
- **Model & architecture decisions** — primary/fallback/switch logic; prompt vs few-shot vs RAG vs fine-tune vs agent selection with rejected-alternative rationale; data flow and prompt contract.
- **Eval & safety planning** — golden sets, acceptance/hallucination/refusal/latency/cost metrics, guardrail layers, refusal policy, failure-mode taxonomy, human-in-the-loop gates, ethical review.
- **Operations & cost** — cost model, per-tenant metering, shadow→internal→canary→percent→GA deployment ramp with gates, and lifecycle/prompt versioning.

## When to Use

- **Adding an AI/ML feature to an existing product** -- a search assistant, a recommendation, an auto-summarizer, a copilot, an agent.
- **Building an AI-first product** -- the entire surface area is model-mediated.
- **Migrating a deterministic feature to an LLM** -- replacing a rules-based system or scripted flow with a model.
- **Fine-tuning, prompt-tuning, or RAG decision** -- the PRD captures the architecture rationale so engineering does not relitigate it mid-build.
- **Regulated context** -- EU AI Act, HIPAA, FINRA, FDA SaMD -- the PRD must enumerate the risk tier, the eval bar, and the audit trail before kickoff.

**When NOT to use:** for a non-AI feature (use `create-prd/`); for pure model R&D with no product surface (use a research design doc); for a one-off internal prompt or batch script that does not ship to users (a Notion page is fine); when the AI feature has no production traffic plan.

## Clarify First

Before drafting the AI PRD, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **AI task & surface:** what the model does and where it appears to the user (drives Section 9 model selection + architecture pattern: prompt vs RAG vs fine-tune vs agent).
- **Quality & safety bar:** the acceptance / hallucination / refusal / latency targets that define "good enough" (drives Section 10's eval criteria and golden set).
- **Risk / regulatory tier:** EU AI Act tier or regulated context (health, finance, legal) (drives Section 10.7 ethical review and where human-in-the-loop is mandatory).
- **Cost & traffic envelope:** expected volume and cost-per-call ceiling (drives Section 11's cost model and the deployment ramp gates).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

The workflow, start to finish:

1. Settle the Clarify First inputs, then write Sections 1-8 as for any PRD.
2. Write Section 10 (eval and safety) before Section 9: golden set, acceptance, hallucination, refusal, latency and cost bars, using `assets/eval_spec_template.md`.
3. Score candidate models against that golden set and fill Section 9: primary, fallback, switch trigger, architecture pattern, and for reasoning models the effort level or thinking budget, chosen on the golden set because it moves quality, latency and cost together.
4. Fill Section 11 with `assets/ai_feature_prd_template.md`: count thinking tokens as output tokens, subtract prompt-caching savings for stable system prompts and retrieved context, and give every ramp stage a gate metric. Walk `assets/guardrail_checklist.md` and `assets/failure_mode_taxonomy.md`.
5. Verify that every number in Sections 9-11 traces to the golden set or the traffic envelope, and that each ramp stage names the metric that halts it, before calling it done.

Name models by the vendor's current id (for example `claude-sonnet-5-5`, `claude-haiku-5-5`) and check the vendor's model list and pricing page when writing; ids and prices change faster than this skill.

## Anti-Patterns

### Choosing the model before the eval
**Mistake:** Section 9.1 names a primary model while Section 10.1 still says the golden set is under construction.
**Why it happens:** Model choice is the exciting decision, and "use the strongest model" sounds safe.
**Instead:** Define the golden set and the acceptance, hallucination and refusal bars in Section 10 first. Then score candidate models against it and record why the primary and the fallback won.

### Golden set left as "TBD"
**Mistake:** Section 10.2 says the golden set will be compiled during the build.
**Why it happens:** Building one takes curation work with Support and Safety, and the PRD deadline comes first.
**Instead:** Commit the golden set to source control before kickoff, for example 200 items split 70% common, 20% edge and 10% adversarial. Name one owner for the set and one for the eval runner.

### Deployment ramp with no gates
**Mistake:** Section 11.3 lists Shadow, Internal, Canary, Percent and GA with dates, but no metric that must hold to advance.
**Why it happens:** A calendar plan is easier to write than agreeing a threshold for each stage.
**Instead:** Give every stage a gate metric and an owner, such as golden-set acceptance, P0 safety incidents and cost per interaction. Test the plan by asking which number halts the ramp at each stage.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

Pull the reference that matches the task; keep this file lean and load detail on demand.

- **[references/ai-prd-structure.md](references/ai-prd-structure.md)** — why a separate AI PRD is needed (standard-vs-AI comparison), the full 11-section framework with every sub-section (model selection, architecture pattern, data flow, prompt contract, eval criteria, golden set, guardrails, refusal policy, failure modes, HIL, ethical checklist, cost model, deployment ramp, lifecycle), the authoring workflow, tools/assets, troubleshooting, and success criteria. Read when drafting any AI Feature PRD.
- **[references/ai-pm-frameworks-guide.md](references/ai-pm-frameworks-guide.md)** -- Software 2.0 (Karpathy), OpenAI Model Spec, Anthropic RSP, EU AI Act tiers, and the AI PM playbook. Read for the conceptual grounding behind the PRD sections.
- **[references/eval-design-guide.md](references/eval-design-guide.md)** -- golden sets, pairwise eval, RAGAS, Promptfoo, Langfuse, online vs offline eval, drift detection. Read when designing Section 10's eval suite.
- **[references/red-flags.md](references/red-flags.md)** -- concrete examples of how AI PRDs go wrong and how to fix them. Read when reviewing a draft for quality.
- **assets/ai_feature_prd_template.md** -- full 11-section AI PRD template. Use to author the artifact.
- **assets/eval_spec_template.md** -- eval contract: golden set, metrics, cadence, owners.
- **assets/guardrail_checklist.md** -- input/output/HIL guardrail walkthrough.
- **assets/failure_mode_taxonomy.md** -- AI-specific failure mode catalogue and mitigations.

## Scope & Limitations

**In Scope:** the 11-section AI Feature PRD template (model selection with primary/fallback/switch logic, eval criteria with golden set + hallucination/refusal/latency/cost metrics, guardrail layers, failure-mode taxonomy, deployment ramp with gates, cost model + per-tenant metering, ethical review with EU AI Act tier declaration).

**Out of Scope:** building/running evals (use Promptfoo, Langfuse, Anthropic Console, Braintrust); cost-model arithmetic (use `engineering/llm-cost-optimizer/`); regulatory classification deep dive (use `ra-qm-team/eu-ai-act-specialist/`, `ra-qm-team/iso42001-ai-management/`); standard PRD structure for non-AI features (use `create-prd/`); detailed system architecture (engineering RFC); production model training pipelines (MLOps tooling).

**Important Caveats:** model versions move fast — re-evaluate the primary every 90 days and design the PRD so a model swap is a controlled change, not a rewrite. A "100% acceptance" target means the golden set is too easy (real features land at 85-95% on hard tasks). Cost projections at low traffic underestimate real spend — model a 10x scenario before launch. Treat refusal policy as living guidance. AI features in regulated industries (health, finance, legal) require human-in-the-loop on every high-stakes action.

## Files

| File | Purpose |
|------|---------|
| `assets/ai_feature_prd_template.md` | Full 11-section template |
| `assets/eval_spec_template.md`, `assets/guardrail_checklist.md`, `assets/failure_mode_taxonomy.md` | Eval contract, guardrail walkthrough, failure modes |
| `references/ai-prd-structure.md`, `references/eval-design-guide.md`, `references/ai-pm-frameworks-guide.md`, `references/red-flags.md` | Section-by-section guide, eval design, frameworks, failure modes |
| `examples/ai-meeting-notes-summarizer.md` | Worked AI PRD |

Related skills: `execution/create-prd` for the 8-section spine, `engineering/llm-cost-optimizer` for cost math, `ra-qm-team/eu-ai-act-specialist` for risk-tier classification.
