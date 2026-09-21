# AI PM Frameworks Guide

A working reference for the frameworks, mental models, and policies that inform a 2026-era AI Feature PRD. Each entry includes its source (where an official one exists), the core idea, and the slot where it shows up in the PRD.

## 1. Software 2.0 (Andrej Karpathy)

**Core idea:** In Software 1.0, the spec is human-written code. In Software 2.0, the spec is the dataset and the loss function -- the model weights are *compiled* from data. The PRD must spec **the data, the metric, and the eval**, not just the function signature.

**PRD slot:** Section 9.2 (architecture choice) and Section 10 (eval as spec). The "behavior" of an AI feature is defined by its evals, not by its code.

**Practical implication:** A PRD that says "the assistant should be helpful" is a Software 1.0 PRD pretending to be 2.0. A 2.0 PRD says "the assistant achieves >= 90% acceptance on the v1 golden set of 200 customer support queries, with hallucination rate <= 2% by faithfulness rubric."

## 2. OpenAI Model Spec (style)

**Source:** OpenAI Model Spec (public document, regularly updated). Defines intended behavior, refusals, and chain-of-command for an AI assistant.

**Core idea:** An AI assistant's behavior is a *policy*, not a feature. The policy must distinguish what the model should never do, what it should refuse, what it should redirect, and what it should answer plainly -- with examples for each.

**PRD slot:** Section 10.4 (refusal policy). Borrow the style: enumerate categories, give concrete examples per category, define the override hierarchy (system > developer > user > tool output).

**Practical implication:** "Don't be harmful" is not a refusal policy. A real refusal policy lists: medical-advice queries that route to a disclaimer + professional resources, code-generation requests that touch credentials and are refused outright, ambiguous-intent queries that ask a clarifying question.

## 3. Anthropic Responsible Scaling Policy (RSP)

**Source:** Anthropic Responsible Scaling Policy (versioned public document). Defines AI Safety Levels (ASL) and the controls that ship with each tier.

**Core idea:** Capability tiers determine controls. As model capability increases, the deployment controls scale up: stronger evals, harder red-teaming, more restricted deployment surfaces, and explicit hard-no use cases.

**PRD slot:** Section 10.5 (failure modes) and Section 10.7 (ethical review). Adapt the tier framing to your feature: what is the worst plausible misuse, and what controls block it?

**Practical implication:** A PRD for an internal-only auto-summarizer needs lighter controls than a PRD for a customer-facing agent that can take action on a user's account. Name the tier.

## 4. EU AI Act Risk Tiers

**Source:** Regulation (EU) 2024/1689 -- the EU Artificial Intelligence Act, as amended by the Digital Omnibus on AI (Regulation (EU) 2026/1744, in force 27 July 2026). Phased compliance through 2028.

**Application timeline (as of September 2026 -- re-check the Commission's AI Act page before relying on a date):**

| Obligation | Applies from |
|---|---|
| Prohibited practices + AI literacy | 2 February 2025 |
| General-purpose AI (GPAI) model obligations | 2 August 2025 |
| Transparency obligations (Art. 50: chatbots, deepfakes, AI-generated content) | 2 August 2026 |
| High-risk systems in Annex III areas (employment, education, credit, etc.) | 2 December 2027 (moved from 2 August 2026 by the Omnibus) |
| High-risk systems embedded in products under EU product-safety law (Annex I) | 2 August 2028 (moved from 2 August 2027 by the Omnibus) |

Official sources: the Commission's AI Act policy page (digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) and the Omnibus text in the Official Journal (eur-lex.europa.eu, OJ L 2026/1744).

**Core idea:** Four risk tiers:
- **Unacceptable risk** -- banned (social scoring, manipulative behavioral systems, certain biometric uses).
- **High risk** -- regulated heavily (medical devices, education scoring, employment, critical infrastructure, law enforcement). Requires conformity assessment, technical documentation, human oversight, accuracy + robustness specs.
- **Limited risk** -- transparency obligations (chatbots, deepfakes, AI-generated content disclosure).
- **Minimal risk** -- unregulated (most consumer AI features).

**PRD slot:** Section 10.7 (ethical review checklist) and Section 5 (excluded segments). State the tier on page one.

**Practical implication:** If the product is sold or used in the EU, the tier determines your audit, documentation, and human-oversight obligations. The deferral moves the high-risk deadline, not the classification: a feature that is High-risk still needs its conformity work scoped now, and Limited-risk transparency duties already apply. Pair with `ra-qm-team/eu-ai-act-specialist/` for the full conformity assessment.

## 5. The AI PM Job: Four Responsibilities

**Core idea:** The AI PM job sits at the intersection of (a) defining the eval, (b) selecting the right architecture (prompt vs RAG vs fine-tune vs agent), (c) managing the cost-quality-latency Pareto, and (d) handling non-determinism in UX. A common failure: teams jump to fine-tuning before they have iterated on prompts and retrieval.

**PRD slot:** Section 9.2 (architecture choice with rejected alternatives) and Section 7 (UX patterns for non-determinism, such as cite-source, regenerate, undo).

**Practical implication:** The PRD must justify the architecture choice against the cheaper alternative. "We need a fine-tune because the prompt does not work" is a hypothesis -- the PRD captures the eval evidence that supports or refutes it.

## 6. Conventional AI PRD Structure

**Core idea:** AI feature PRDs are converging on a shared structure: a model card section, an eval section, a guardrails section, and a deployment-ramp section. The patterns are settled; reuse them.

**PRD slot:** All of Sections 9-11.

**Practical implication:** Do not invent a new PRD structure for AI features. Reuse the conventional sections so reviewers can navigate familiar territory.

## 7. ISO 42001 (AI Management System)

**Source:** ISO/IEC 42001:2023 -- AI management system standard.

**Core idea:** An organization shipping AI needs a *system*, not a one-off process. Policy, scope, roles, risk management, impact assessment, supplier management, and lifecycle controls -- all auditable.

**PRD slot:** Section 11.4 (lifecycle) ties to the AI management system. The PRD does not contain the full AIMS, but it references it.

**Practical implication:** For B2B SaaS targeting regulated buyers, an ISO 42001 program is a sales-enabler. Pair with `ra-qm-team/iso42001-ai-management/`.

## 8. NIST AI Risk Management Framework (AI RMF)

**Source:** NIST AI RMF 1.0 (2023), Generative AI Profile (2024).

**Core idea:** Govern -> Map -> Measure -> Manage. A risk-management lifecycle adapted to AI. Useful for US-headquartered teams that want a voluntary, non-regulatory framework.

**PRD slot:** Section 10 evaluation methodology often cites the AI RMF Measure function.

## 9. Failure-mode taxonomy for AI

A useful PM-level taxonomy (compiled across the literature and 2024-2026 incident reports):

| Failure | Description | Mitigation |
|---|---|---|
| **Hallucination** | Fluent but factually false output | Retrieval, citation requirement, faithfulness check |
| **Sycophancy** | Agreement with user's stated belief over the truth | System prompt instruction; pairwise eval against neutral baseline |
| **Refusal misfire (over-refuse)** | Refuses benign requests | Benign-prompt eval; loosen system prompt; pick better-calibrated model |
| **Refusal misfire (under-refuse)** | Answers harmful requests | Red-team set; output filter; better-aligned model |
| **Prompt injection** | User input overrides system prompt | Input sanitization; structured prompts; out-of-band tool authorization |
| **Jailbreak** | Adversarial wrapper bypasses refusal | Red-team set; layered guardrails; output classifier |
| **PII leakage** | Model surfaces private info from context or training | Pre-prompt redaction; output PII filter |
| **Bias / disparate quality** | Quality varies by demographic group | Subgroup eval; representative golden set; bias audit |
| **Drift** | Quality degrades over time without code change | Online sampling; periodic re-eval; canary against held-out set |
| **Latency tail** | p95/p99 spikes during load | Smaller fallback model; cache; context-window pruning |
| **Cost spike** | Token usage balloons | Per-tenant meter; auto-throttle; switch to cheaper model |
| **Tool misuse** | Agent calls a tool incorrectly or maliciously | Tool-schema validation; out-of-band approval for destructive tools |

The full taxonomy with mitigations lives in `assets/failure_mode_taxonomy.md`.

## 10. Useful 2026 production-eval tooling

| Tool | Role | When to use |
|---|---|---|
| **Promptfoo** | Offline eval framework | Local + CI eval of prompts; multiple model comparisons |
| **Langfuse** | Production trace + eval | Open-source observability; large-scale trace inspection |
| **Anthropic Console** | Trace + eval for Claude | Native option for Claude-based features; built-in evals |
| **Braintrust** | Eval + experiment platform | Hosted eval workflows for teams |
| **OpenAI Evals** | Eval framework | OpenAI-centric stacks |
| **Weights & Biases Weave** | LLM application observability | If you already use W&B |
| **LlamaGuard 3 / 4** | Input/output safety classifier | Stand-alone guard model in the pipeline |
| **RAGAS** | RAG-specific eval (faithfulness, context relevance) | Any RAG feature |

Pick one offline + one online tool minimum.

## 11. Cost-quality-latency triangle

The classic Pareto for AI features. Every architecture decision moves on this triangle:

```
       quality
         /\
        /  \
       /    \
      /------\
   cost      latency
```

A bigger model raises quality and cost and (usually) latency. RAG raises quality and latency and cost. Fine-tuning raises quality and cost (offline) and lowers cost (online, for the same quality). Caching lowers cost and latency but only on cache-hits.

A real PRD picks two corners and *deliberately* accepts the third as a constraint. "We want best-in-class quality at low latency, and we accept the cost premium" is honest. "We want all three" is a roadmap to a quality regression in 6 months when finance pushes back.

## 12. The "AI premium" question

The PRD must answer: *Why is this an AI feature, not a deterministic feature?*

Good answers:
- The task is unbounded (open-ended generation, summarization, translation).
- The task requires natural-language understanding of free-form input.
- The latency-quality tradeoff favors an LLM over a rules engine.
- The product gains a step-function in capability that justifies the cost.

Bad answers (these are tells that the team is AI-washing):
- "Because everyone else is doing AI."
- "Because the CEO wants AI in the product."
- "Because we have Claude/GPT credits."
- "Because we can charge more for AI."

If you cannot write a credible "AI premium" paragraph, the feature should be deterministic.

## Official sources

- OpenAI, "Model Spec" (latest version)
- Anthropic, "Responsible Scaling Policy" (latest version)
- Regulation (EU) 2024/1689 ("EU AI Act"), as amended by Regulation (EU) 2026/1744 (Digital Omnibus on AI)
- NIST AI RMF 1.0 + Generative AI Profile
- ISO/IEC 42001:2023

---
**Last Updated:** 2026-09-21
