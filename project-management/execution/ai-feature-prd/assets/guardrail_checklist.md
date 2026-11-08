# AI Guardrail Checklist

A pre-launch walkthrough across the six standard guardrail layers. Every AI feature should pass through this checklist before the canary stage.

**Feature:** [Name]
**Reviewer:** [Safety / Trust reviewer]
**Date:** 2026-05-22
**Stage:** Pre-canary / Pre-GA / Periodic audit

---

## Layer 1: Input filter

Catches problems before the model sees them.

- [ ] **PII redaction** -- emails, phone numbers, SSNs, credit cards stripped or hashed before retrieval and before the prompt assembly. Tool: [regex + classifier / LlamaGuard / Presidio].
- [ ] **Intent classification** -- low-confidence or off-scope intents are routed away from the LLM (to a help page, an FAQ, or a human).
- [ ] **Length guard** -- inputs above N tokens are truncated or rejected with a clear error message.
- [ ] **Encoding / unicode normalization** -- handle homoglyph attacks and zero-width characters.
- [ ] **Rate limiting** -- per-user and per-tenant ceiling enforced before the model is called.
- [ ] **Authentication check** -- the user has rights to ask this question of this knowledge base / take this action.

## Layer 2: Pre-prompt (system prompt)

The system prompt is the strongest control plane you own.

- [ ] **Role and goal** stated unambiguously in the first paragraph.
- [ ] **Refusal policy** explicit; refuses harmful, off-policy, and off-scope requests.
- [ ] **Output format** specified (JSON schema, response template, or examples).
- [ ] **Tool authorization** specified -- which tools can be invoked and under what preconditions.
- [ ] **Citation requirement** (for RAG) -- model instructed to cite source for every claim.
- [ ] **Identity / branding** -- model identifies as the company's assistant, not "Claude" / "ChatGPT".
- [ ] **Prompt versioned** in source control with PR-level review.
- [ ] **Prompt protected** -- user content never overrides system content (use trusted-prompt patterns).

## Layer 3: In-model

The model choice itself is a control.

- [ ] **Primary model** is a well-aligned, frontier-tier model with known refusal training (Claude family, GPT family, Gemini family at the comparable tier).
- [ ] **Fallback model** is also a well-aligned model (do not fail over to a less-safe model just to save cost).
- [ ] **Variance control** fits the model: where temperature is exposed, set the lowest value that gives acceptable variance; reasoning models often fix sampling, so use the output schema, the prompt contract and the effort setting instead.
- [ ] **Max tokens** capped to prevent runaway generation.
- [ ] **Stop sequences** set to prevent leak of system prompt or tool outputs.
- [ ] **Safety-policy headers / params** set on the API (e.g., Anthropic's safety classifiers, OpenAI's moderation hooks).

## Layer 4: Output filter

Catches problems before the response reaches the user.

- [ ] **Content classifier** flags policy-violating output (LlamaGuard output mode, Anthropic content classifier, custom moderation model).
- [ ] **PII outflow** scanned -- the model is not leaking PII it retrieved.
- [ ] **Jailbreak-success detector** -- the response is checked against known jailbreak patterns ("Here's how to make...", "Sure, ignoring my previous instructions...").
- [ ] **Schema validation** -- structured outputs validated against the declared JSON schema; invalid outputs trigger retry-with-correction or fallback.
- [ ] **Citation validation (RAG)** -- citations point to a real source in the retrieved set; orphan citations trigger a regeneration.
- [ ] **Profanity / brand-safety filter** -- applied as policy requires.

## Layer 5: Post-response (programmatic checks)

Logic after the LLM has produced output but before the user sees it.

- [ ] **Schema check** for tool-call arguments before execution.
- [ ] **Idempotency / dedup** for tool calls that should not repeat.
- [ ] **Authorization re-check** for high-stakes actions -- the LLM may have decided to act, but the user must still have permission.
- [ ] **Side-effect dry-run** for destructive actions (delete, send, charge): show preview, require confirmation.
- [ ] **Confidence threshold** -- self-rated or judge-rated confidence below threshold triggers human review.

## Layer 6: Human-in-the-loop

The escape hatch.

- [ ] **Hard gates** documented and enforced -- high-stakes actions never auto-execute (defined in PRD Section 10.6).
- [ ] **Soft gates** -- low-confidence outputs route to a review queue with named owner and SLA.
- [ ] **Sampling review** -- 1-5% of production traffic reviewed weekly; results recorded against the golden-set rubric.
- [ ] **User-initiated escalation** -- a clear "talk to a human" path exists in the UI at every step.
- [ ] **Escalation logging** -- every handoff to a human is logged with reason and outcome.

---

## Cross-cutting checks

- [ ] **Disparate-impact audit** -- model performance broken out by demographic subgroups; gap within tolerance.
- [ ] **Red-team set passed** -- refusal-on-harmful rate >= 98% on the current red-team set.
- [ ] **Drift monitoring** -- online sampling running and alerting.
- [ ] **Runbook published** -- on-call has documented response to each failure mode in PRD Section 10.5.
- [ ] **Incident process** -- safety incidents have a defined triage flow, with Legal/Compliance loop-in for high-tier issues.
- [ ] **Privacy review** -- data flow signed off by Legal/Compliance.
- [ ] **EU AI Act tier** -- declared; if "High", conformity assessment underway with `ra-qm-team/eu-ai-act-specialist/`.

---

## Sign-off

Feature cleared for the [canary / GA] stage when all checks above are green or have an explicit, time-bound exception.

| Role | Name | Date | Notes |
|---|---|---|---|
| Safety reviewer | | | |
| PM | | | |
| ML lead | | | |
| Eng lead | | | |
