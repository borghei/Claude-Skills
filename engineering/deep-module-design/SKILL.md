---
name: deep-module-design
description: >
  Design deep modules with small interfaces and rank shallow, pass-through or leaky
  code for deepening. Use when designing a module interface, improving codebase
  architecture, or making code easier to test.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: software-design
  updated: 2026-11-08
  tags: [module-design, deep-modules, information-hiding, seams, refactoring, testability, architecture-review]
---

# Deep Module Design

Module-level design for code that is getting harder to change. A deep module
gives callers a lot of behaviour behind a small interface; a shallow one makes
them learn almost as much as it does. This skill measures where a codebase is
shallow, ranks the places where deepening would pay back, writes the review,
and then designs the replacement interface at least twice before anyone writes
it. The goal: callers get a lot done through very little surface, a change
stays inside one module, and tests exercise the same interface callers use.

## When to use this skill

- **Designing a new module** and wanting its interface right before callers multiply
- **"Improve the architecture of this codebase"** — find and rank deepening opportunities
- **A change keeps touching five files** for one business rule
- **Tests are brittle** because they reach past interfaces into internals
- **Layers that only forward calls** — services that call repositories that call clients, each adding nothing
- **Choosing between interface proposals** for the same module

## Inputs the skill expects

- The code: a path to scan, or the module and its callers for a design task
- Change history if available (`git log`), to weight hotspots
- The project's glossary and recorded decisions, so names and past choices are respected
- For a design task: the responsibilities the module must own and its dependencies
- Constraints: public API stability, number of callers, test coverage today

## Clarify First

What most shapes the output is whether this is a review of existing code or the design of one module, and how much change the codebase can absorb. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Review or design:** a review scans and ranks many candidates; a design goes deep on one module and compares interfaces.
- **Scope and hotspots:** a named pain point beats a whole-repo scan; without one, change frequency decides where to look.
- **Interface stability:** a published library interface rules out merges a private module would allow.
- **Recorded decisions:** a candidate that contradicts one is only worth raising if the pain justifies reopening it.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Rank shallow, pass-through and leaky modules in the sample order-management codebase
python3 engineering/deep-module-design/scripts/module_depth.py \
  --input engineering/deep-module-design/assets/sample_codebase.json

# Compare three candidate interfaces for the merged order-intake module
python3 engineering/deep-module-design/scripts/interface_compare.py \
  --input engineering/deep-module-design/assets/sample_designs.json
```

## Workflows

### Workflow 1 — Architecture review: scan, rank, report [RECOMMENDED]

The agent finds deepening opportunities, ranks them, and writes a report; it does not propose signatures until a candidate is chosen.

1. Choose where to look: the requester's named area, or the most-changed paths over six months (the churn one-liner is in `references/architecture-review-playbook.md`).
2. Read the glossary and recorded decisions for those areas first.
3. Run the analyser from the repository root so module names match the churn keys:

   ```bash
   python3 engineering/deep-module-design/scripts/module_depth.py \
     --path . --churn churn.json --format json > depth.json
   ```

4. Read each flagged module and its callers. Apply the deletion test: would deleting it concentrate complexity or spread it? Discard acceptable shapes (adapters at real seams, type definitions, framework handlers).
5. Score the survivors 1–3 on change frequency, pain evidence, locality gain, test gain and migration risk; keep the top 3–5.
6. Write the report from `assets/architecture-review-template.md`: friction with evidence, proposed deepening in plain words, leverage and locality gains, test impact, before/after sketch, strength label.
7. End with one top recommendation and ask which candidate to explore.

Validation checkpoint: every candidate cites evidence (churn, a bug, a duplicated rule), uses glossary names, and states which tests move or get deleted.

### Workflow 2 — Interrogate the chosen candidate [RECOMMENDED]

1. Name the one concept the module will own. If the name needs "and", split it.
2. List the callers and what the most common one needs.
3. Classify each dependency: in-process, local stand-in, remote owned, third party (table in `references/depth-principles.md`).
4. Place the seam where behaviour varies, and name its two adapters.
5. Decide which error modes callers must distinguish; translate the rest at the seam.
6. Record new or sharpened terms in the glossary as they settle; offer to record a lasting rejection as a decision.

### Workflow 3 — Design the interface twice and compare [PROVEN]

1. Write at least two designs under different constraints: smallest surface, common caller first, flexible, or port-based (`assets/interface-design-brief-template.md`).
2. For each, list entry points (params, error modes, ordering rules), config knobs, what it hides, what it leaves to callers, common-case call count, seams with adapters, and the common caller's code.
3. Encode them as JSON shaped like `assets/sample_designs.json` and run the comparison:

   ```bash
   python3 engineering/deep-module-design/scripts/interface_compare.py \
     --input engineering/deep-module-design/assets/sample_designs.json --format json
   ```

4. Fix rule violations: unplaced responsibilities, single-adapter seams, near-identical designs. The sample exits 1 on purpose — design B has a one-adapter seam and design C drops the event-publishing responsibility.
5. Recommend one design with reasons. When the margin is under one point, propose a hybrid.

### Workflow 4 — Migrate without breaking callers [PROVEN]

1. Write tests at the new interface first, from the common caller's scenarios.
2. Build the deep module behind it, reusing old code internally.
3. Move callers one at a time with the build green after each.
4. Delete the absorbed shallow modules and the tests that pinned their internals.
5. Re-run `module_depth.py` on the area and verify that the candidate no longer appears in the flagged list.

## Decision frameworks

### Is this module earning its place?

| Signal | Deepen or merge | Keep as is |
|--------|-----------------|-----------|
| Deletion test | Complexity vanishes when inlined | Complexity spreads to N callers |
| Pass-through share | ≥ 50% of functions only forward | Each function adds a rule, translation or check |
| Seam | One adapter, nothing varies | Two adapters, behaviour varies across them |
| Callers' preparation | Every caller repeats the same setup | Callers call it directly |
| Tests | Reach past the interface | Go through the interface only |

### Default thresholds in `module_depth.py` [RECOMMENDED]

| Flag | Default | Meaning |
|------|---------|---------|
| `--shallow-below` | 4.0 | Under 4 code lines per interface unit, with 3+ entry points, is shallow |
| `--deep-above` | 8.0 | 8+ lines per interface unit is reported as deep |
| `--pass-ratio` | 0.5 | Half or more functions forwarding (and at least two) marks a pass-through layer |
| `--max-params` | 5 | More parameters than this marks a leaky entry point |

Interface cost counts each entry point as 1 plus its parameters. The ratio is a pointer, not a verdict: read the code before reporting a module.

### Where should the seam go? [PROVEN]

Put a seam only where you can name two adapters. Storage, messaging and third-party services earn ports; steps inside one calculation do not. Keep internal seams private to the module's own tests.

## Anti-Patterns

### Extracting for Testability Alone
**Mistake:** Splitting a function into many tiny pure helpers so each can be unit-tested, while the bugs live in how they are combined.
**Why it happens:** Small functions are easy to test and the coverage number rises.
**Instead:** Test through the interface that callers use. Keep helpers private; the deep module's interface is the test surface.

### The Forwarding Stack
**Mistake:** Controller → service → manager → repository, where three of the four layers forward their arguments unchanged.
**Why it happens:** A layered template was applied by rule, not by need, and each layer "might need logic later".
**Instead:** Run the deletion test on each layer. Merge pass-throughs into the module that owns the behaviour; add a layer back when it has a second adapter or a real rule.

### The Hypothetical Seam
**Mistake:** Introducing an interface plus factory for a dependency that has exactly one implementation and no test fake.
**Why it happens:** It looks like good design and costs little at first.
**Instead:** Add a seam when a second adapter exists — usually the in-memory fake the tests need. Until then it is indirection that callers must read through.

### Designing Once
**Mistake:** Shipping the first interface that came to mind for a module many callers will depend on.
**Why it happens:** The first design works, and alternatives feel like extra work.
**Instead:** Write at least two designs under different constraints and compare them with `interface_compare.py`. The second design usually reveals a responsibility the first leaked to callers.

### Layering New Tests Over Old
**Mistake:** Adding tests at the new deep interface but keeping all the old tests on the absorbed internals.
**Why it happens:** Deleting tests feels like losing safety.
**Instead:** Once the new interface's tests cover the behaviour, delete the old ones. Tests that pin internals make the next refactor as expensive as this one.

## Files

### Tools Overview

| Script | Purpose | Exit codes |
|--------|---------|------------|
| `scripts/module_depth.py` | Per-module entry points, interface cost, code lines, depth, pass-through functions, long parameter lists and private-name imports for Python (AST) and JS/TS (pattern based); ranks opportunities, weighted by `--churn` | 0 nothing flagged, 1 shallow / pass-through / leaky modules found, 2 input error |
| `scripts/interface_compare.py` | Scores candidate interfaces on interface cost, depth, caller burden; enforces placed responsibilities, two-adapter seams and distinct designs; recommends one | 0 all designs valid, 1 rule violations, 2 input error |

Both take `--format text|json`. `module_depth.py` accepts `--path` for real code or `--input` for a JSON bundle of `{"files": {name: source}, "churn": {name: count}}`; test files are skipped unless `--include-tests`.

### Reference Documentation

| File | Purpose |
|------|---------|
| `references/depth-principles.md` | Vocabulary, five module tests, leak catalogue, seams and adapters, dependency categories and test strategy, design moves, acceptable shallow shapes |
| `references/architecture-review-playbook.md` | Seven-phase review: hotspots, scan, rank rubric, report, interrogation, design twice, migration; question bank |
| `assets/architecture-review-template.md` | Report with candidate cards, ranking and before/after sketches |
| `assets/interface-design-brief-template.md` | One brief per candidate design, feeding the comparison JSON |
| `assets/sample_codebase.json` | Seven-module order-management bundle — analyser exits 1 with six flagged modules |
| `assets/sample_designs.json` | Three interface designs for order intake — comparison exits 1, recommends design A |

## Scope & Limitations

**In Scope:**
- Module-level design inside one codebase: interfaces, depth, information hiding, seams, adapters, testability.
- Codebase reviews that rank deepening opportunities and produce a written report.
- Comparing two or more interface designs for one module and recommending one.
- Migration steps from shallow modules to a deep one, including test replacement.

**Out of Scope:**
- System-level architecture — service boundaries, data stores, scaling, deployment topology; the senior-architect skill owns those decisions.
- Mechanical refactoring execution and code formatting.
- Maintaining the project glossary and decision records themselves (this skill reads them and proposes additions).
- Languages other than Python and JS/TS for the analyser; the principles apply to any language.

**Important Caveats:**
- JS/TS analysis uses patterns, not a parser: unusual export styles, overloads and decorators can be miscounted. Python analysis uses the standard `ast` module and is exact on syntax.
- Depth as lines per interface unit is a proxy. Adapters, type modules and framework handlers are flagged but often fine; read before reporting.
- `interface_compare.py` scores what you describe. A design described optimistically scores optimistically; the usage example is the honesty check.
