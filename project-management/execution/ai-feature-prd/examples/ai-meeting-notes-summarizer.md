# Example: AI Meeting Notes Summarizer for Acme Analytics

> Real-world scenario showing how to apply the AI Feature PRD skill end-to-end.

## Context

Acme Analytics is a Series-C B2B SaaS (analytics-and-reporting product for mid-market companies, ~3,400 paying customers, ~$48M ARR). The Customer Success team runs ~600 QBR calls per quarter. The repeated complaint from CSMs: "I spend 45 minutes after every call writing notes, action items, and stakeholder follow-ups. Half of it is from memory because Otter transcripts are unstructured."

Product leadership has approved building an in-app "AI Meeting Notes Summarizer" that ingests a transcript (from Zoom, Google Meet, or paste) and emits a structured summary, action items, sentiment cues, and a draft follow-up email. Target users: internal CSMs first (eat-our-own-dog-food), then customer-facing for QBR exports.

The PM (Priya, Senior PM, Customer Workflows) needs an AI Feature PRD that survives review by Eng, ML, Trust & Safety, Legal, and the CFO who is allergic to runaway model bills.

## Inputs

- 12 CSM interviews from `discovery/interview-synthesis/` (transcript-pain quantified)
- An internal eval set of 80 sanitized transcripts already collected by Trust & Safety
- Engineering capacity: 1 ML engineer + 2 backend + 1 frontend, 10-week slot
- Cost ceiling from CFO: under $0.07 per summary at GA, must alert at 80% of monthly budget
- EU customers ~28% of base, so EU AI Act risk-tier declaration is required before model selection
- Existing flag system (LaunchDarkly) and observability stack (Langfuse + Datadog)

## Applying the skill

1. **Declared EU AI Act tier first.** Pulled in `ra-qm-team/eu-ai-act-specialist/`. The feature is **Limited Risk** (transparency obligation, no automated decisions about people). Locked this before model choice so the eval bar would reflect it.
2. **Defined the golden set before any prompt.** PM + Trust & Safety curated 200 transcripts: 140 common cases, 40 edge cases (multi-speaker, accents, off-topic chat), 20 adversarial (PII-laden, prompt-injection attempts).
3. **Filled the 11 sections** from `assets/ai_feature_prd_template.md`. Sections 1-8 followed `create-prd/` patterns; 9-11 were the heavy lift.
4. **Forced the model alternatives table.** Engineering wanted to start with a fine-tune. The prompt-first heuristic won the room: prompt + RAG over the user's prior QBR notes for tone matching. Fine-tune deferred to v2.
5. **Locked numeric eval thresholds** before any prompt was written. Acceptance >= 90% on golden set, hallucination <= 2%, p95 latency < 2.0s, cost per summary < $0.05.
6. **Wired the deployment ramp** to `feature-flag-strategy/` shape A (linear) with a shadow stage and an internal-only stage gated on acceptance >= 85%.
7. **Pre-mortemed the AI-specific failure modes** with `discovery/pre-mortem/` (hallucinated action items, prompt-injection from a hostile transcript, model outage during a high-volume QBR week).

Key decision quoted from the review: *"We name `claude-sonnet-4.5` as primary and `gpt-5-mini` as fallback. Switch trigger is acceptance regression > 5 points week-over-week, or vendor outage > 30 min."*

## The artifact

````markdown
# PRD-AI: Meeting Notes Summarizer (v1)

**Status:** Approved for Build
**Author:** Priya Shah (Sr PM, Customer Workflows)
**Reviewers:** N. Okafor (Eng Lead), L. Park (ML Lead), R. Diaz (Trust & Safety), M. Hughes (Legal), J. Tran (CFO)
**Date:** 2026-05-22
**EU AI Act Risk Tier:** Limited Risk

## 1. Summary

A Claude-Sonnet-4.5-based assistant integrated into Acme Analytics that converts a call transcript (Zoom / Meet / pasted) into a structured QBR summary, action items, sentiment snapshot, and draft follow-up email. Internal CSMs first, customer-facing export in v1.1.

## 2. Contacts

| Role | Name |
|---|---|
| PM | Priya Shah |
| Eng Lead | N. Okafor |
| Design Lead | E. Lindqvist |
| ML / Applied Research | L. Park |
| Trust & Safety | R. Diaz |
| Legal & Compliance | M. Hughes |
| Exec Sponsor | C. Bell (VP Product) |

## 3. Background

CSM interviews (n=12) and a 4-week instrumented diary study found CSMs spend 38-52 min after each QBR call on note-taking and follow-up drafting. Total cost: ~530 CSM-hours/quarter. Frontier LLMs (Claude Sonnet, GPT-5 class) cleared the structured-summarization benchmark on internal pilots in March 2026 at acceptance > 88%. Two competitors (Gong, Fathom) shipped similar features in Q1 2026; the gap is now visible in deal reviews.

## 4. Objective

**Business benefit:** reduce post-call CSM admin by 60%, unlock ~320 CSM-hours/quarter for proactive outreach.
**Customer benefit (internal):** faster follow-up; higher-quality action items.
**Customer benefit (external, v1.1):** branded summary export for the customer's stakeholders.

**Key Results (Q3 2026):**
- KR1: 60% of QBR calls processed via summarizer within 6 weeks of internal launch
- KR2: Acceptance rate on golden set >= 90%
- KR3: CSM post-call admin time reduced from 45 min median to 18 min median (self-reported diary)
- KR4: Cost per summary < $0.05 (CFO gate)

## 5. Market Segments

| Segment | JTBD | In/Out v1 |
|---|---|---|
| Acme CSMs (internal) | "Turn a 60-min QBR into a structured follow-up in 5 min" | IN |
| Customer admins (external) | "Share a polished QBR summary with our exec team" | IN v1.1 |
| Sales AEs (internal) | "Summarize discovery calls" | OUT v1 (different shape) |
| End-customer end-users | n/a | OUT (no end-user surface) |

Excluded for safety: any call involving health, legal advice, or minors. The system refuses to process transcripts flagged as such.

## 6. Value Proposition

- **Gains:** structured output (sections + action items + sentiment) faster than human note-taking.
- **Pains:** removes the "what did we agree to?" memory cost; reduces missed action items.
- **AI premium:** sentiment shift detection + linkage to prior QBR notes via RAG -- a deterministic rules-based summarizer cannot do either.

## 7. Solution

**P0:** Transcript ingest (paste + Zoom integration), structured summary (5 sections), action items with owners + dates, sentiment snapshot per stakeholder, draft follow-up email.
**P1:** Branded export PDF, RAG over prior QBRs for tone continuity.
**P2:** Multi-language (DE, FR, ES) summaries; long-call chunking > 90 min.

**Prompt sketch:**

```
Role: A Customer Success briefing assistant for Acme Analytics.
Goal: Produce a structured QBR summary from a meeting transcript.
Inputs: transcript (with speaker labels), customer record (tier, prior NPS, last QBR summary if any).
Constraints:
  - Cite the transcript turn(s) supporting each action item.
  - Never invent attendees, dates, dollar figures, or product names.
  - If the transcript is < 200 tokens, refuse and ask the user to confirm.
  - If the transcript contains medical, legal, or minor-related content, refuse.
Output format: JSON with keys: summary_sections, action_items[], sentiment_by_stakeholder, draft_email.
Tools: cite_transcript_turn(turn_id), lookup_customer_record(customer_id).
```

## 8. Release

| Stage | Audience | Gate to next |
|---|---|---|
| Shadow | Production transcripts mirrored; no UI | No crashes; acceptance >= 80% on a 50-transcript live sample |
| Internal | 12 CSMs, 4 weeks | Acceptance >= 85%; no Sev1/2 |
| Canary | 25% of CSMs | Acceptance >= 90%; cost per summary <= $0.06 |
| GA | 100% CSMs | Stable for 2 weeks |
| v1.1 (customer-facing export) | Flag-gated per tenant | After GA + 30 days |

## 9. AI System Design

### 9.1 Model selection

| Field | Value |
|---|---|
| Primary model | `claude-sonnet-4.5` (Anthropic, via Bedrock, eu-west-1 for EU tenants) |
| Fallback model | `gpt-5-mini` (OpenAI, via Azure, EU regional) for outage; `claude-haiku-4` for cost cap |
| Reason chosen | Highest acceptance on golden-set pilot (91% vs 84% for `gpt-5-mini`, 79% for `claude-haiku-4`); strong refusal behavior on PII-laden transcripts |
| Update policy | Re-evaluate primary every 90 days (next: 2026-08-22) |
| Switch trigger | Acceptance regression > 5 points WoW, or vendor outage > 30 min |

### 9.2 Architecture pattern

Chosen: **Prompt + RAG**. Retrieval over the customer's prior 4 QBR summaries (if any) for tone and continuity.

Rejected:
- Pure prompt -- loses continuity across QBRs.
- Fine-tune -- 200-transcript dataset too small; prompt-first principle applies.
- Agentic tool use -- no multi-step task; over-engineering.

### 9.3 Data flow

```
Transcript (paste/Zoom) -> PII scrubber (regex + LlamaGuard 3) -> Retrieval (prior QBR summaries) -> Claude Sonnet 4.5 -> Output schema validator -> Sentiment classifier (post-pass) -> UI
```

- User data leaves boundary to Anthropic via Bedrock under existing DPA (EU residency for EU tenants).
- Transcripts retained 30 days for eval sampling; opt-out at tenant level.
- No training-data use (Anthropic opt-out confirmed).
- Logs: Langfuse traces, 90-day retention, RBAC restricted to ML + Trust & Safety.

### 9.4 Prompt contract

In source control at `prompts/qbr_summarizer/v1.yaml`. Every prompt change is a PR with an eval delta.

## 10. Eval & Safety Plan

### 10.1 Eval criteria

| Metric | Target | Method | Cadence |
|---|---|---|---|
| Acceptance rate (golden set) | >= 90% | Human review, 200-item gold set | Weekly during build, monthly post-GA |
| Hallucination rate (citation-faithfulness) | <= 2% | RAGAS-style faithfulness vs transcript | Weekly |
| Refusal rate (benign inputs) | <= 4% | 100-transcript benign set | Pre-launch + monthly |
| Refusal rate (out-of-scope: health/legal/minor) | >= 98% | 50-transcript red-team set | Pre-launch + on prompt change |
| Action-item attribution accuracy | >= 95% | Human review on golden set | Weekly |
| p95 latency | < 2000 ms (90-min transcript) | Datadog | Continuous |
| Cost per summary | < $0.05 | Token accounting | Continuous |

### 10.2 Golden set

- Size: 200 transcripts (140 common, 40 edge, 20 adversarial)
- Owned by PM (Priya); ML (L. Park) runs evals; failures reviewed weekly
- In source control at `evals/qbr_summarizer/golden_v1/`; refresh 20% quarterly

### 10.3 Guardrails

| Layer | Implementation |
|---|---|
| Input filter | Regex PII scrub + LlamaGuard 3 classifier; refuse if health/legal/minor flagged |
| Pre-prompt | System prompt enforces "never invent attendees/dates/dollars"; refusal rules |
| In-model | `claude-sonnet-4.5` chosen partly for refusal training |
| Output filter | Schema validator (rejects malformed JSON); citation check (every action item must map to a transcript turn) |
| Post-response | Sentiment classifier as a separate pass (not in main prompt) |
| Human-in-loop | CSM must click "Send" on the draft email; nothing auto-sends |

### 10.4 Refusal policy

The summarizer refuses to:
- Process transcripts containing medical advice, legal advice, or content involving minors.
- Generate summaries for transcripts shorter than 200 tokens (asks user to confirm).
- Infer protected attributes (race, religion, sexual orientation) about stakeholders, even if hinted in transcript.

The summarizer redirects (does not refuse) when:
- A user asks for an opinion on the customer's strategy -- redirect to "I can summarize what was said; the strategic call is yours."

### 10.5 Failure modes

| Failure | Detection | Response |
|---|---|---|
| Primary model outage | Bedrock health-check + error rate alert | Fail over to `gpt-5-mini`; banner in UI |
| Acceptance drops > 5 pts WoW | Weekly Langfuse eval CI | Roll back prompt version; on-call ML paged |
| Hallucinated action item | Citation-check + user "incorrect" flag | Tighten prompt; add to golden set |
| Prompt injection via transcript | Output filter + "instruction-leak" detector | Patch input scrubber; add to red-team set |
| Cost spike per tenant | Per-tenant token meter | Throttle or downgrade to `claude-haiku-4` |
| Latency > 2s on long transcripts | p95 alert | Chunk and parallelize |

### 10.6 Human-in-the-loop

- **Hard gate:** the draft follow-up email never auto-sends. CSM must click Send.
- **Soft gate:** when model self-confidence < 0.6 on any action item, item flagged "review me" in UI.
- **Sampling review:** Trust & Safety reviews 3% of production summaries weekly.

### 10.7 Ethical review

- [x] Affected populations: CSMs (workflow change); customer stakeholders (their words summarized)
- [x] Tested with bilingual/accented English transcripts (n=18)
- [x] Failure-mode cost: a hallucinated action item could damage a customer relationship; HIL mitigates
- [x] EU AI Act tier declared: **Limited Risk** (transparency obligation)
- [x] GDPR DPIA filed (lawful basis: legitimate interest; opt-out at tenant)
- [x] Users informed they are interacting with AI (banner + disclosure in summary footer)
- [x] Non-AI alternative: blank notes template (existing) remains available

## 11. Operations & Cost

### 11.1 Cost model

| Line | Formula | Estimate at 600 QBR/mo |
|---|---|---|
| Inference (primary) | 600 * 18k input tokens * $3/Mtok + 600 * 2k output * $15/Mtok | ~$50/mo |
| Inference (fallback, <= 10%) | n/a | ~$5/mo |
| Embeddings (RAG) | 600 * 4k tokens * $0.13/Mtok | ~$0.30/mo |
| Vector store (Pinecone serverless) | flat | ~$70/mo |
| Eval runs | 200 * 4 model calls/wk * $0.01 | ~$32/mo |
| Langfuse / observability | events-based | ~$40/mo |
| **Total v1** | | **~$200/mo** |

At 10x traffic (6000 QBR/mo): ~$1,250/mo. Modeled with `engineering/llm-cost-optimizer/`.

### 11.2 Cost monitoring

- Per-tenant token meter (Langfuse).
- Alert at 80% of monthly budget; auto-throttle at 120%.
- Cost-per-successful-interaction metric (cost / accepted summaries) reviewed weekly.

### 11.3 Deployment strategy

Wired via LaunchDarkly flag `qbr_summarizer_v1`. Shape A (linear) with internal-first gate.

### 11.4 Lifecycle

- Re-eval primary model 2026-08-22.
- Prompt versioned at `prompts/qbr_summarizer/v1.yaml`; bumps require PR + eval delta.
- Golden-set refresh quarterly (10-20% rotation).
- Deprecate when accuracy < 80% on golden set for 3 consecutive weeks, or product surface area changes.
````

## Why this works

- Names a primary model (`claude-sonnet-4.5`), a fallback (`gpt-5-mini`), and a numeric switch trigger -- exits the "use the best model" trap.
- Eval thresholds (90% acceptance, 2% hallucination, $0.05/summary) are numeric and pre-locked, so quality cannot be rationalized after launch.
- Declares EU AI Act risk tier on day 1, avoiding the "Legal vetoes at week 9" failure mode.
- Cost model includes a 10x sensitivity and an auto-throttle, satisfying the CFO gate explicitly.
- Human-in-the-loop "hard gate" on email send guards the highest-stakes action without blocking the workflow.

## What's next

- Pair with [../create-prd/](../create-prd/) for the standard PRD pattern that Sections 1-8 follow.
- Pair with [../feature-flag-strategy/](../feature-flag-strategy/) for the rollout flag mechanics.
- Pair with [../../discovery/pre-mortem/](../../discovery/pre-mortem/) to expand the AI-specific failure-mode list.
- Feed metrics back to [../north-star-metric/](../north-star-metric/) -- QBR-summarizer acceptance becomes an input metric for the "CSM productivity" NSM.
- Use [../post-mortem/](../post-mortem/) when (not if) the first acceptance regression hits.
