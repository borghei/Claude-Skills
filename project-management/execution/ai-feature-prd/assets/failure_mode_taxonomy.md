# AI Failure Mode Taxonomy

A working catalogue of the failure modes a 2026-era AI feature must plan for, with detection and mitigation patterns. Use this as input to PRD Section 10.5 (Failure Modes & Graceful Degradation) and the pre-mortem.

---

## Quality failures

### Hallucination

**What:** Fluent but factually incorrect output. The model invents facts, citations, APIs, or sources.

**Detection:**
- Faithfulness eval (RAGAS or custom rubric) on golden + online samples.
- Citation-validity check (does the cited source exist; does it support the claim?).
- User-feedback: thumbs-down with "factually wrong" reason.

**Mitigation:**
- Retrieval-augmented generation with strict cite-or-refuse instructions.
- Lower temperature where the model exposes it; otherwise tighten the output contract or raise reasoning effort.
- Add "If you do not know, say so" to system prompt; reward refusal in fine-tune signal.
- Switch to a less hallucination-prone model variant.

### Sycophancy

**What:** Model agrees with the user's stated belief even when it is wrong.

**Detection:** Pairwise eval with prompts that assert false premises. Did the model push back or comply?

**Mitigation:** System prompt instruction to challenge incorrect premises politely. Use a model with explicit anti-sycophancy training. Pairwise eval against a neutral-baseline variant.

### Over-refusal (refusal misfire, benign)

**What:** Model refuses benign requests, often via excessive caution.

**Detection:** Benign-prompt eval set; refusal rate on this set should be <= 5%.

**Mitigation:** Calibrate refusal policy; provide examples of benign-and-answerable requests; pick a model with better refusal calibration; reduce overly-broad refusal phrases in the system prompt.

### Under-refusal (refusal misfire, harmful)

**What:** Model answers harmful requests, often via jailbreak or role-play wrapper.

**Detection:** Red-team eval set; refusal rate should be >= 98%.

**Mitigation:** Layered guardrails (input + pre-prompt + in-model + output); rotate red-team set quarterly; add successful jailbreaks to the red-team set as regression cases.

### Format non-compliance

**What:** Output does not match the declared JSON / template structure.

**Detection:** Schema validator post-response.

**Mitigation:** Use structured-output mode (constrained decoding); few-shot examples in the prompt; retry-with-correction loop; switch to a model with better format adherence.

---

## Security failures

### Prompt injection

**What:** Untrusted input (e.g., a document, a webpage, a tool result) contains instructions that override the system prompt.

**Detection:** Pre-prompt classifier on retrieved content; output-side detector for "told to ignore previous instructions" patterns.

**Mitigation:** Trusted-prompt architecture (system prompt walls off untrusted content); content sanitization; tool authorization re-check; structured prompts that mark untrusted content explicitly (`<user-content>...</user-content>`).

### Jailbreak

**What:** User wraps a harmful request in a role-play, hypothetical, or DAN-style framing that bypasses refusal training.

**Detection:** Red-team eval; output classifier; known-jailbreak pattern matcher.

**Mitigation:** Pick a well-aligned model; layered output filtering; rotate red-team set; rate-limit prompt-length to limit elaborate wrapper attacks.

### Data exfiltration

**What:** Model is induced to reveal its system prompt, retrieved private data, or training data.

**Detection:** Output filter for known system-prompt fragments; PII outflow scanner.

**Mitigation:** Never put secrets in the system prompt; separate retrieval from generation (do not pass raw documents containing PII unless required); output-side PII scanner; reduce context-window leakage by truncating sources.

### Tool misuse

**What:** Agentic model invokes a tool incorrectly or maliciously.

**Detection:** Tool-call schema validation; idempotency checks; post-hoc audit of tool invocations.

**Mitigation:** Tool authorization re-check; dry-run + confirmation for destructive tools; per-tool rate limits; bounded tool scope.

---

## Privacy failures

### PII leakage in output

**What:** Model surfaces private information from retrieved context or from training data memorization.

**Detection:** Output-side PII scanner (Presidio, custom classifier).

**Mitigation:** Pre-prompt redaction; output PII filter; train/fine-tune on PII-stripped data; minimize retrieval scope to caller's authorized data.

### PII leakage in logs

**What:** Logs contain user PII, prompts containing secrets, or retrieved sensitive context.

**Detection:** Log scanner.

**Mitigation:** Redact before logging; log only metadata; retention policy enforced; access controls on the log store.

### Cross-tenant leakage

**What:** Multi-tenant feature accidentally serves tenant A's data to tenant B.

**Detection:** Tenant-id assertion in retrieval; canary inputs that should never return cross-tenant content.

**Mitigation:** Tenant-id as a hard filter at retrieval; assert tenant boundary at every layer; per-tenant model state if fine-tuned.

---

## Operational failures

### Primary model outage

**What:** Upstream API (Anthropic, OpenAI, vendor) is down.

**Detection:** Health-check + error-rate monitor.

**Mitigation:** Fallback model in a different vendor; circuit-breaker; cached responses for common queries; graceful UI degradation.

### Quality regression on model update

**What:** Vendor updates their model and your evals drop.

**Detection:** Pinned-version policy + scheduled re-eval against new versions.

**Mitigation:** Pin to specific model versions in production; re-eval new versions in shadow before promoting; rollback path documented.

### Cost spike

**What:** Token usage balloons, often from a misuse case or a prompt regression that increases output length.

**Detection:** Per-tenant token meter; daily cost variance alert.

**Mitigation:** Per-tenant rate limit; auto-throttle at 120% of budget; downgrade to cheaper fallback; max-tokens cap; investigate prompt regression.

### Latency tail

**What:** p95 / p99 latency spikes under load.

**Detection:** Latency alert on production telemetry.

**Mitigation:** Smaller fallback model under load; cache for common queries; context-window pruning; streaming responses to reduce perceived latency.

### Drift

**What:** Quality degrades over time without code change. Often from training-data drift in the model, retrieval-corpus drift, or user-input distribution drift.

**Detection:** Online eval sampling; periodic re-eval on the golden set; user-feedback rate.

**Mitigation:** Quarterly golden-set refresh from production logs; quarterly model re-evaluation; retrieval-corpus health check.

---

## Fairness & ethical failures

### Disparate quality across demographics

**What:** Model performs worse for certain demographic groups (language, dialect, name patterns, accents).

**Detection:** Subgroup eval on the golden set; demographic breakdown of online metrics.

**Mitigation:** Representative golden set; subgroup-aware fine-tuning; bias audit pre-launch; UI accommodations.

### Reinforcement of stereotypes

**What:** Model output perpetuates stereotyped associations (e.g., gendered occupational defaults).

**Detection:** Targeted eval prompts; manual review of representative outputs.

**Mitigation:** Prompt instruction to avoid stereotyped defaults; representative training/fine-tune data; output review.

### Deceptive use

**What:** Feature is used to deceive (impersonation, fake content, manipulation).

**Detection:** Use-policy review; pattern of misuse in logs.

**Mitigation:** Watermarking / provenance signals on AI-generated content; clear AI-disclosure to end-users; abuse-report flow; usage terms enforcement.

---

## Reliability & maintainability failures

### Prompt drift (engineering)

**What:** Nobody knows what the live prompt is; production has diverged from source control.

**Detection:** Prompt-version assertion in CI; production prompt fetched + compared to repo on deploy.

**Mitigation:** Prompts in source control; deployment process injects version; deploy-time check.

### Eval rot

**What:** Eval set is no longer representative of production.

**Detection:** Compare eval set distribution against production sample.

**Mitigation:** Quarterly refresh; mine production for new failure cases; retire memorized examples.

### Owner drift

**What:** Original PM/ML owner moves on; nobody owns the eval or the policy.

**Detection:** Org chart review.

**Mitigation:** Named owners in the eval spec; succession plan; knowledge transfer in the runbook.

---

## Severity classification

| Severity | Example | Response |
|---|---|---|
| **P0 (safety)** | Jailbreak success on production prompt; cross-tenant leakage | Immediate prompt patch + post-mortem within 7 days |
| **P0 (outage)** | Primary model down + fallback not configured | Failover; incident review |
| **P1** | Hallucination spike; cost spike beyond auto-throttle | 24-hour response; rollback path |
| **P2** | Drift detected on online sampling | Weekly review; planned re-tuning |
| **P3** | Format compliance regression on minor prompt change | PR-level fix |

---

**Last updated:** 2026-05-22
