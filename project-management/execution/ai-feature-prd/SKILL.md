---
name: ai-feature-prd
description: >
  AI/ML feature PRD scaffolding for the modern AI product manager. Use to
  extend a standard PRD with AI-specific sections covering model selection,
  evals, guardrails, failure modes, human-in-the-loop, AI metrics, and cost
  monitoring.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: ai-prd, ml-prd, llm-product, evals, guardrails, responsible-ai
---
# AI Feature PRD Expert

## Overview

AI and ML features break the assumptions a standard PRD takes for granted. Outputs are non-deterministic. Quality is statistical, not categorical. The "spec" is half product, half eval suite. A regular PRD that says "Search returns the top result" is replaced by "the assistant returns a helpful, harmless, on-policy answer with a refusal rate under 4% on the golden set, p95 latency under 1.8s, and cost-per-conversation under $0.05."

This skill produces an **AI Feature PRD** that extends the standard 8-section PRD (see `create-prd/`) with three additional sections built for the realities of shipping AI: **AI System Design** (Section 9), **Eval & Safety Plan** (Section 10), and **Operations & Cost** (Section 11). It draws on Karpathy's "Software 2.0" framing (the model *is* the spec), Anthropic's Responsible Scaling Policy patterns, the OpenAI Model Spec style for defining intended behavior, the Reforge AI PM curriculum, and the EU AI Act's risk-tier model. This is a template-based skill -- no Python tool; the artifact is a markdown PRD. Pair this with `engineering/llm-cost-optimizer/` for the cost-model math and with `ra-qm-team/eu-ai-act-specialist/` for the regulatory classification.

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

Before drafting the AI PRD, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **AI task & surface** — what the model does and where it appears to the user (drives Section 9 model selection + architecture pattern: prompt vs RAG vs fine-tune vs agent)
- [ ] **Quality & safety bar** — the acceptance / hallucination / refusal / latency targets that define "good enough" (drives Section 10's eval criteria and golden set)
- [ ] **Risk / regulatory tier** — EU AI Act tier or regulated context (health, finance, legal) (drives Section 10.7 ethical review and where human-in-the-loop is mandatory)
- [ ] **Cost & traffic envelope** — expected volume and cost-per-call ceiling (drives Section 11's cost model and the deployment ramp gates)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## References

Pull the reference that matches the task; keep this file lean and load detail on demand.

- **[references/ai-prd-structure.md](references/ai-prd-structure.md)** — why a separate AI PRD is needed (standard-vs-AI comparison), the full 11-section framework with every sub-section (model selection, architecture pattern, data flow, prompt contract, eval criteria, golden set, guardrails, refusal policy, failure modes, HIL, ethical checklist, cost model, deployment ramp, lifecycle), the authoring workflow, tools/assets, troubleshooting, and success criteria. Read when drafting any AI Feature PRD.
- **[references/ai-pm-frameworks-guide.md](references/ai-pm-frameworks-guide.md)** -- Software 2.0 (Karpathy), OpenAI Model Spec, Anthropic RSP, Reforge AI PM, EU AI Act tiers, and the AI PM playbook. Read for the conceptual grounding behind the PRD sections.
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

## Integration Points

| Integration | Direction | Description |
|---|---|---|
| `create-prd/` | Extends | Sections 1-8 follow the standard PRD; this skill adds 9-11 |
| `prfaq/` | Pairs with | Working Backwards PR for AI features should call out the AI premium plainly |
| `north-star-metric/` | Feeds into | NSM should include an AI-quality input (acceptance rate, win rate) |
| `brainstorm-okrs/` | Feeds into | KRs in Section 4 tie to eval targets in Section 10.1 |
| `feature-flag-strategy/` | Pairs with | Section 11.3 ramp executes via feature flags |
| `engineering/llm-cost-optimizer/` | Pairs with | Section 11.1 cost model uses the optimizer's math |
| `ra-qm-team/eu-ai-act-specialist/` | Receives from | Risk tier declaration in Section 10.7 |
| `ra-qm-team/iso42001-ai-management/` | Pairs with | AI management system documentation aligns with PRD lifecycle in 11.4 |
| `discovery/pre-mortem/` | Feeds into | AI-specific failure modes (hallucination, jailbreak, drift) populate the pre-mortem |
| `discovery/identify-assumptions/` | Pairs with | "The base model can do this" is the single biggest AI-PRD assumption; validate before commit |
| `status-update-generator/` | Feeds into | Weekly status surfaces eval drift, cost variance, safety incidents |
