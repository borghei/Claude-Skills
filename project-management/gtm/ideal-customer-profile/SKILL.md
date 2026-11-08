---
name: ideal-customer-profile
description: >
  Defines which accounts to sell to across eight dimensions with explicit
  exclusions, then scores real accounts against that profile. Use when defining or refining
  an ICP, building a qualification rubric, or diagnosing poor pipeline.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: go-to-market
  updated: 2026-11-08
  python-tools: icp_scorer.py
  tech-stack: icp, ideal-customer-profile, firmographics, jtbd
  tags:
    - icp
    - buyer-persona
    - firmographics
    - jobs-to-be-done
    - segmentation
---

# Ideal Customer Profile (ICP)

The agent defines which companies to sell to, sharply enough that a BDR could build a list from it tomorrow and that it excludes most of the market. Marketing uses it to target, sales to qualify, product to prioritise. The ICP describes the account; the persona describes the human buyer inside it.

**Done looks like:** all eight dimensions defined (firmographics, tech stack, buyer persona, job to be done, existing alternatives, trigger events, budget authority, reachability) with specifics; written exclusions; an addressable list size; a weighted rubric that sorts real accounts into strong / workable / marginal / disqualify; `icp_scorer.py --mode validate` exits 0.

## When to Use

- Defining an ICP for a new product or segment, or refining one from closed-won customers
- Pipeline quality or conversion is poor and nobody agrees who the customer is
- Building a sales qualification rubric or an outbound target list

The ICP feeds `project-management/gtm/gtm-strategy`.

## Clarify First

Before defining the ICP, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Existing customers vs greenfield:** refine from closed-won/best-customer patterns vs design-partner proxy (the real ICP comes from data, not a guess).
- **The JTBD the product solves:** what customers are trying to accomplish (anchors firmographics, alternatives, and trigger events).
- **Reachable channels you have:** paid / outbound / events / content / partners (an ICP you can't reach is academic; drives the Reachability dimension).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Complete ICP definition: exit 0
python3 project-management/gtm/ideal-customer-profile/scripts/icp_scorer.py \
  --input project-management/gtm/ideal-customer-profile/assets/sample_icp.json --mode validate --format markdown
```

```bash
# Thin ICP (4 of 8 dimensions, no exclusions): exit 1
python3 project-management/gtm/ideal-customer-profile/scripts/icp_scorer.py \
  --input project-management/gtm/ideal-customer-profile/assets/sample_icp_flawed.json --mode validate --format markdown
```

```bash
# Rank four accounts: Northwind 95 strong, Contoso 68 workable, Fabrikam 45 marginal, Tailspin 20 disqualify
python3 project-management/gtm/ideal-customer-profile/scripts/icp_scorer.py \
  --input project-management/gtm/ideal-customer-profile/assets/sample_accounts.json --mode score --format markdown
```

```bash
# Input schema and flags
python3 project-management/gtm/ideal-customer-profile/scripts/icp_scorer.py --help
```

## Tools Overview

`icp_scorer.py` is the quality gate for this skill. **What the scorer checks:** validate mode counts the eight dimensions marked defined (fail under six), warns when firmographics are not specific, triggers are not listed, the addressable list is missing or under 200, or there are no disqualification criteria. Score mode normalises the weights to 100, converts each 0-3 rating to a share of its weight, and bands at 80 / 60 / 40. The `defined` and `specific` flags are self-reported: read the definitions too.

**Exit codes:** `0` no fail findings · `1` validate: fewer than six dimensions defined; score: no accounts · `2` unreadable file, invalid JSON or a top level that is not an object. `--mode` is required. JSON by default, `--format markdown`, `--output FILE`.

## Workflow

1. **Start from your best customers.** List the top 20 by health, revenue and expansion and find what they share; that is the real ICP. Without customers, use design partners and plan to revise after 10-20 real ones.
2. **Reject myth ICPs.** "100-10,000 employees", "innovative companies", "companies that want to grow", "enterprise": none of these exclude anyone.
3. **Define the eight dimensions** specifically, plus exclusions. Test each: could a BDR build a list from it tomorrow? Triggers should be events that start buying (a new executive, a funding round, a regulatory deadline, an incident), not "they have budget". A worked example and the specificity, tech-stack, trigger and reachability tests are in the appendix of `references/icp-dimensions-deep.md`.
4. **Validate.** Write the ICP as JSON (schema in `--help`; `assets/sample_icp.json`) and run validate mode. It must pass with no fail findings; then verify that each warning is fixed.
5. **Build the rubric and score accounts.** Rate each account 0-3 on industry, size, geography, tech stack, buyer role, trigger, budget authority and timeline, weighted (default weights in `--help`). Run score mode on a real list and check the bands match the sales team's gut on accounts they know; if not, fix the weights.
6. **Refresh quarterly** as new customers, product changes and market shifts move the pattern.

## Anti-Patterns

### An ICP that excludes nobody
**Mistake:** "B2B companies with 100-10,000 employees."
**Why it happens:** Narrowing feels like losing deals.
**Instead:** Write exclusions first. A real ICP rules out most of the market.

### The ICP you wish you had
**Mistake:** The ICP describes the customers the team wants, not the ones who buy, stay and expand.
**Why it happens:** Aspirational logos are more exciting than the current base.
**Instead:** Derive it from the top 20 customers and test it against closed-lost deals.

### Unreachable ICP
**Mistake:** A precise profile nobody can find through any channel the company has.
**Why it happens:** Reachability is treated as marketing's problem later.
**Instead:** Size the addressable list and name the channels before adopting the ICP.

More: `references/icp-refinement-from-data.md`.

## Scope & Limitations

**In Scope:**
- An ICP across eight dimensions: firmographics, tech-stack signals, buyer persona, JTBD, existing alternatives, trigger events, budget authority and reachability
- Refining the ICP from top customers by health, revenue and expansion, or from design partners when there are no customers yet
- A yes/no qualification rubric for sales
- Two tool modes: `--mode validate` audits an ICP definition for completeness and disqualification criteria, and `--mode score` scores accounts with weighted criteria (`icp_scorer.py`)

**Out of Scope:**
- Finding, enriching or scraping account data; the tool scores only accounts the user lists
- The wider go-to-market plan built on the ICP (see `project-management/gtm/gtm-strategy/`)
- Detailed buyer personas and user research (see `product-team/ux-researcher-designer/`)
- CRM lead scoring and pipeline operations (see `business-growth/revenue-operations/`)
- Competitive analysis of who else serves the ICP (see `business-growth/competitive-teardown/`)

**Important Caveats:**
- Every per-account fit score and every `defined` or `specific` flag is entered by hand. The tool checks and weights them but does not verify them.
- Scoring weights and the 80 / 60 / 40 band cut-offs are starting defaults to tune against closed-won and closed-lost data.
- A greenfield ICP is a hypothesis until 10-20 real customers confirm it.
- ICPs drift with the product and the market. The skill expects a quarterly refresh.

## Files

| File | Purpose |
|------|---------|
| `scripts/icp_scorer.py` | ICP validation and account scoring |
| `assets/sample_icp.json` | Complete eight-dimension ICP; validate exits 0 |
| `assets/sample_icp_flawed.json` | Thin ICP; validate exits 1 |
| `assets/sample_accounts.json` | Four accounts across all four bands |
| `assets/icp_template.md` | Fill-in template |

## Reference Documentation

- [references/icp-dimensions-deep.md](references/icp-dimensions-deep.md): Each dimension in depth; appendix with worked example and tests
- [references/icp-refinement-from-data.md](references/icp-refinement-from-data.md): Refining an ICP from closed customers

## Related skills

- `project-management/gtm/gtm-strategy` — uses ICP as input
- `project-management/strategy-frameworks/business-model-canvas` — segments block
- `project-management/discovery/customer-interview-script` — interview-based ICP discovery
- `business-growth/competitive-teardown` — competitive context
- `c-level-advisor/cro-advisor` — sales context
- `c-level-advisor/cmo-advisor` — marketing context
