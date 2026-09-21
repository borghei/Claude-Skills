---
name: ai-prototyping
description: >
  Idea to AI-generated prototype to customer validation to engineering
  handoff. Use when deciding prototype vs spec, choosing fidelity,
  briefing AI prototyping tools, testing with users, or handing a
  prototype to engineering.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-09-21
  python-tools: prototype_plan.py, prototype_handoff_checker.py
  tech-stack: ai-prototyping, product-discovery, usability-testing, handoff
---

# AI Prototyping

AI app builders, AI design tools and AI coding assistants turn an idea into a clickable or working prototype in hours. That changes the economics of discovery and adds three failure modes: prototyping what should have been specified, mistaking a polished demo for validation, and shipping prototype code by accident.

The agent runs the whole loop: **decide** whether to prototype, **pick the fidelity rung**, **brief** the generation tool, **test** with real users against pre-set thresholds, and **hand off** with everything a prototype cannot carry. Two stdlib tools gate the steps teams skip most: untestable hypotheses and incomplete handoffs.

## When to use

- A team wants to "just build it with AI" and someone must decide if that is the right move
- Choosing between a clickable mock, a working prototype on synthetic data, or a spec
- Writing the brief for an AI prototyping tool so the output is testable
- Planning a prototype test: tasks, participants, success and kill criteria
- Handing a validated prototype to engineering without it becoming production code by default
- Setting governance for prototype tools: data, security, IP, accessibility

**When NOT to use:** the dominant risk is viability (pricing, margin, legal) - model it; the solution is already known (parity feature, regulatory requirement) - write the spec; there is no evidence the problem exists - interview users first; you need a *rate* with a confidence interval - run a powered quantitative test.

## Clarify First

Before planning, confirm these inputs. If any is unknown or vague, ASK - do not assume:

- [ ] **Hypotheses and their uncertainty type** - desirability, usability, feasibility or viability (drives the rung, and whether a prototype can answer it at all)
- [ ] **Pre-set success threshold per hypothesis** - the bar that validates or kills it (without it, any result reads as success)
- [ ] **Data constraints** - is real customer data approved for prototype tools, or synthetic only? (caps fidelity at F3 until approved)
- [ ] **Stage** - planning, mid-test, or handing off (selects which tool runs)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# 1. Plan: fidelity, method, sample, success + kill criteria per hypothesis
python3 project-management/discovery/ai-prototyping/scripts/prototype_plan.py \
  --input hypotheses.json                      # exit 2 = a hypothesis is untestable

# 2. Brief the tool with assets/prototype_brief_template.md, test, record findings

# 3. Gate the handoff (JSON or the markdown template)
python3 project-management/discovery/ai-prototyping/scripts/prototype_handoff_checker.py \
  --input handoff.md --strict                  # exit 2 = handoff incomplete
```

## Tools Overview

| Tool | Input | What it does | Gate (exit 2) |
|------|-------|--------------|---------------|
| `scripts/prototype_plan.py` | Hypotheses JSON: uncertainty, impact 1-5, evidence, segment, metric, threshold, flags | Priority (`impact x evidence gap`), fidelity rung, method, tool category, participant guideline, success and kill criteria, timebox; prototype-led vs spec-led verdict; downgrades F4 to F3 until real data is approved | Any hypothesis without success metric, threshold or target segment |
| `scripts/prototype_handoff_checker.py` | Handoff JSON or markdown built from `assets/handoff_template.md` | Checks problem, metrics (baseline + target), findings (participants + result vs threshold), throwaway list, acceptance criteria, non-goals, data/privacy, security, accessibility; unfilled placeholders count as empty | Any blocker; with `--strict`, any warning |

Both support `--format markdown` (default) or `--format json` (wrapped as `{"schema", "generated_at", "data"}` per `SHARED_OUTPUT_SCHEMA.md`) and `--output <file>`.

### Exit code contract [PROVEN]

| Code | Meaning | Who fixes it |
|------|---------|--------------|
| 0 | Pass (warnings allowed unless `--strict`) | Nobody |
| 1 | Tool error: bad path, invalid JSON, invalid field value | Whoever wrote the input file |
| 2 | Gate failed: untestable hypothesis or incomplete handoff | The PM who owns it |

## Workflow

### Step 1 - Prototype or spec? [RECOMMENDED]

| Dominant uncertainty | Can a prototype answer it? | First move |
|----------------------|----------------------------|------------|
| **Desirability** - will they want it? | Partly; pair with a commitment ask | No evidence: interview or smoke test. Some evidence: clickable concept + commitment ask |
| **Usability** - can they use it? | Yes; this is what prototypes are best at | Clickable (F2) or working (F3), moderated task test |
| **Feasibility** - can we build it? | Yes, if it exercises the riskiest technical path | Engineering spike (F3) against a technical bar |
| **Viability** - does it work for the business? | No | Spec, model and review (F0) |

Prototype to *learn*; write the spec to *decide*. When risk is spread across types, do both in parallel.

### Step 2 - Pick the fidelity rung

| Rung | What | Tool category |
|------|------|---------------|
| **F0** | No prototype: interview, smoke test, model, spec | none |
| **F1** | Prompted mock, static screens | AI design tool, AI app builder |
| **F2** | Clickable, linked flows | AI design tool, AI app builder |
| **F3** | Working, synthetic data | AI app builder, AI coding assistant |
| **F4** | Working, real data - **only with written data-owner and security approval** | AI coding assistant in an approved environment |

Start at the **lowest rung that can falsify the hypothesis**; climb only when it passed or cannot test the risk by construction. Generate **2-3 variants** (one per candidate solution), not one polished version. Traps per rung and worked decisions: [references/prototype-decision-guide.md](references/prototype-decision-guide.md).

### Step 3 - Brief the generation tool

Write the brief before generating, one per variant, from [assets/prototype_brief_template.md](assets/prototype_brief_template.md): (1) role and disposability, (2) user and context, (3) the job in the user's words, (4) explicit screen and state list including error states the tasks hit, (5) synthetic data only, (6) constraints incl. an accessibility baseline, (7) out of scope. When output is structurally wrong, edit the brief and regenerate - do not hand-patch.

### Step 4 - Test with users, not at them [PROVEN]

- Pre-register success and kill thresholds before session 1; recruit the target segment, not colleagues.
- Goal-based tasks ("deal with the expense that breaks policy"), never UI instructions ("click the red badge").
- The user drives; the facilitator is silent; stuck counts as failure.
- Measure behavior per task (unassisted success, time, errors). For desirability, end with a commitment ask and count commitments, not compliments.
- Report against the bar: "5 of 6 completed task 2 unassisted against a bar of 5 of 6".

Participant numbers from the planner are planning defaults, not statistical guarantees. Demo-ware bias checklist: [references/testing-handoff-governance.md](references/testing-handoff-governance.md).

### Step 5 - Write down what the prototype cannot carry

The spec/PRD still owns: problem and users with evidence; success metrics (baseline, target, window); constraints; non-goals; risks and open hypotheses; data and privacy decisions.

### Step 6 - Hand off to engineering

Fill [assets/handoff_template.md](assets/handoff_template.md) and run the checker. **The prototype is not production code** [PROVEN]: state in one sentence whether it is *throwaway* or a *starting point* (legitimate only if built on the production stack, in an engineering-owned repo, and still code- and security-reviewed). The throwaway list names what it skipped: auth, error states, accessibility, security, performance, data model. Extract acceptance criteria: each passed task becomes a Given/When/Then; each fixed failure becomes a criterion that would have caught it; add the non-functional criteria the prototype ignored.

### Step 7 - Governance guardrails [RECOMMENDED]

| Area | Default rule |
|------|--------------|
| **Data** | No real customer, employee or partner data in prototype tools without a written approval reference; record the tool's retention and training-on-inputs settings |
| **Security** | No secrets, keys, internal hostnames or customer IDs in prompts or code; private repos archived after handoff; treat content fed to any LLM call as untrusted (OWASP LLM01:2025 Prompt Injection) |
| **IP** | Tool terms checked for output ownership; no licensed third-party assets in prompts; reused code gets license and provenance review |
| **Accessibility** | Brief every prototype with a baseline (labels, focus, contrast; WCAG 2.2 levels A/AA/AAA); record gaps in the throwaway list and acceptance criteria |

## Worked Example

[examples/mobile-expense-approvals.md](examples/mobile-expense-approvals.md) - four hypotheses for mobile expense approvals, planned, tested and handed off.

| Command | Exit | Why |
|---------|------|-----|
| `prototype_plan.py --input assets/hypotheses_sample.json` | 0 | H3 downgraded F4 to F3 (real data not approved); H4 routed to F0 (viability) |
| `prototype_plan.py --input assets/hypotheses_untestable.json` | 2 | "Reps will love it" has no metric, threshold or segment |
| `prototype_handoff_checker.py --input examples/mobile-expense-approvals.md` | 0 | Complete markdown handoff |
| `prototype_handoff_checker.py --input assets/handoff_complete.json` | 0 | One open finding carried as a risk (warning) |
| `prototype_handoff_checker.py --input assets/handoff_incomplete.json` | 2 | Real recordings uploaded without approval; no throwaway list; zero-participant "finding" |

A 0-16 health rubric for a team's prototyping practice is in [references/testing-handoff-governance.md](references/testing-handoff-governance.md#5-health-rubric---is-this-prototype-effort-healthy).

## Anti-Patterns

### The Polished Wrong Answer
**Mistake:** Generating a high-fidelity prototype of the first idea and testing only that.
**Why it happens:** Generation is so cheap the team skips solution divergence and goes straight to screens.
**Instead:** Lowest falsifying rung first, 2-3 variants. A polished prototype of the wrong opportunity is still waste.

### Demo-ware Validation
**Mistake:** Presenting the prototype and recording "they loved it" as validation.
**Why it happens:** Demos feel like tests, audiences are polite, polish reads as progress.
**Instead:** The user drives, thresholds are pre-set, desirability ends with a commitment ask, results are counts against the bar.

### The Accidental Production App
**Mistake:** The prototype repo gets a few fixes and becomes v1 without anyone deciding it should.
**Why it happens:** It already works, and rebuilding feels like waste under deadline pressure.
**Instead:** State the disposition at handoff, list what was skipped, and gate with `prototype_handoff_checker.py`.

### Real Data for Realism
**Mistake:** Pasting real customer records, recordings or receipts into a prototype tool so the demo feels real.
**Why it happens:** Synthetic data looks fake and uploading is trivial.
**Instead:** Synthetic data in the real data's shape. The planner holds F4 until approval exists; the checker blocks a handoff that used real data without an approval reference.

### Prototyping a Viability Question
**Mistake:** A pricing-page prototype to "test" willingness to pay.
**Why it happens:** Prototyping becomes the team's default tool.
**Instead:** Route viability to F0 - pricing research, a unit-economics model, a legal or security review.

## Reference Documentation

- [references/prototype-decision-guide.md](references/prototype-decision-guide.md) - uncertainty test, fidelity ladder with traps, the seven-part brief, worked decisions, sample-size guidance stated honestly
- [references/testing-handoff-governance.md](references/testing-handoff-governance.md) - running sessions, demo-ware bias, what must be written down, throwaway checklist, acceptance-criteria extraction, data/security/IP/accessibility governance, health rubric, sources
- `assets/prototype_brief_template.md` - generation prompt, test script, guardrail checklist
- `assets/handoff_template.md` - markdown handoff the checker validates
- `assets/hypotheses_sample.json` / `hypotheses_untestable.json` - planner inputs (pass / gate fail)
- `assets/handoff_complete.json` / `handoff_incomplete.json` - checker inputs (pass / gate fail)

## Related skills

Self-contained; these sections elsewhere cover the same ground from their angle:

- `project-management/execution/create-prd/` - **Prototype-First Path**: prototyping alongside the PRD, and what the PRD must still contain
- `project-management/discovery/opportunity-solution-tree/` - assumption test ladder, where AI prototypes compress the prototype rungs
- `project-management/discovery/brainstorm-experiments/` - **Prototype-First Experiments**: prototypes as one experiment method with XYZ hypotheses
- `project-management/discovery/identify-assumptions/` - surfacing and classifying the assumptions tested here
- `project-management/execution/ai-feature-prd/` - when the prototype is itself an AI feature needing evals and guardrails

## Sources

- W3C, *Web Content Accessibility Guidelines (WCAG) 2.2*, W3C Recommendation - https://www.w3.org/TR/WCAG22/
- OWASP GenAI Security Project, *LLM01:2025 Prompt Injection* - https://genai.owasp.org/llmrisk/llm01-prompt-injection/
