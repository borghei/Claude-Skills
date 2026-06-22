---
name: grants
description: >
  Grant writing and proposal architecture: funder fit, proposal structure,
  budget design, and success-factor scoring. Use when writing a grant proposal,
  evaluating funder fit, auditing a draft for competitiveness, or planning a
  budget.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: research
  domain: research
  updated: 2026-05-27
  tags: [grants, proposals, funding, nih, nsf, foundation, research, budget]
---

# Grant Writing & Proposal Architecture

A skill for crafting competitive grant proposals across funder types:
government (NIH, NSF, DOE, ARPA), foundation, corporate, philanthropic,
and SBIR / STTR. Focuses on the **architecture** of a winning proposal:
fit, structure, narrative, budget — not boilerplate templating.

## When to use this skill

- Evaluating **funder fit** before investing weeks in a proposal
- **Designing the proposal structure** for a specific funder
- Writing or auditing the **narrative** for competitiveness
- Designing a **realistic, defensible budget**
- Pre-submission **proposal review** for common failure modes
- Building a **grants strategy** (which to apply to over the year)

## Inputs the advisor expects

- The funder name + specific program / RFP
- The research / project idea (problem, approach, outcomes)
- Team composition (PI, co-investigators, key personnel)
- Institutional / org context
- Past funding history
- Budget envelope (or constraint)
- Submission deadline

## Clarify First

Before generating the proposal, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Funder + specific program / RFP** — sets the mental model (NIH 5-criteria vs NSF merit+impact vs foundation mission fit); drives structure and narrative
- [ ] **Project idea (problem, approach, outcomes)** — drives the significance/innovation narrative and the Heilmeier answers
- [ ] **Budget envelope** — drives budget design and whether scope matches the funder's typical award size
- [ ] **Team composition (PI, key personnel)** — drives the investigator/environment fit dimension

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Score funder fit before committing

1. Capture funder, program, project idea, team strengths.
2. Run `funder_fit_scorer.py` to grade fit on 7 dimensions.
3. If fit < 65, look for better-aligned funder; don't waste 4 weeks.

```bash
python3 grants/scripts/funder_fit_scorer.py \
  --input funder_fit.json --format markdown
```

### Workflow 2 — Validate proposal structure against funder expectations

1. Capture the proposal section list + page allocation.
2. Run `proposal_structure_validator.py` against funder type expectations.
3. Adjust before drafting deep.

```bash
python3 grants/scripts/proposal_structure_validator.py \
  --input proposal_structure.json --funder-type nih --format markdown
```

### Workflow 3 — Audit budget for realism

1. Capture budget line items with justifications.
2. Run `budget_realism_checker.py` against funder norms + project scope.
3. Adjust before submission.

```bash
python3 grants/scripts/budget_realism_checker.py \
  --input budget.json --format markdown
```

## Decision frameworks

### Funder fit dimensions
1. **Topic alignment** — does the funder fund this area?
2. **Mechanism alignment** — does the funder fund this *kind* of work (R&D, services, scale-up)?
3. **Stage alignment** — early-stage / mid / scale?
4. **Geographic alignment** — does the funder fund your region?
5. **Team profile alignment** — does the funder fund your kind of team?
6. **Budget envelope alignment** — does the funder's typical award size match?
7. **Competitive density** — is it 5% acceptance or 35%?

A score below 65 across these is usually a "skip this funder" signal.

### Funder type — distinct mental models

| Funder type | Emphasizes | De-emphasizes |
|-------------|-----------|---------------|
| NIH | Significance + innovation + approach + investigator + environment (5 criteria) | Commercial outcome |
| NSF | Intellectual merit + broader impacts | Direct commercial outcome |
| ARPA / DARPA | Heilmeier catechism (defined moonshot question) | Incremental work |
| SBIR / STTR | Commercial path + technical risk | Pure science |
| Foundation | Mission fit + measurable outcomes | Pure academic novelty |
| Corporate | Commercial relevance to sponsor | Independence from sponsor |
| Crowdfunding | Story + community appeal | Technical rigor |

Write to the funder's mental model, not a generic "good grant."

### The Heilmeier catechism (good for any proposal)
1. What are you trying to do?
2. How is it done today; what are the limits?
3. What's new in your approach; why succeed?
4. Who cares; if you succeed, what difference does it make?
5. What are the risks; how will you mitigate?
6. How much will it cost; how long?
7. What are the mid-term + final outcomes you'll deliver?

A proposal that can't answer all seven crisply isn't ready.

## Common engagements

### "Help me decide between two RFPs"
1. Score both for fit; the higher one is usually right.
2. If close: which has earlier deadline / smaller proposal effort?
3. Don't submit to both same year unless funders are independent.

### "Audit my draft proposal"
1. Check funder-fit assumptions (did the program actually fund what you're proposing?)
2. Check structure against funder template
3. Check narrative: is the problem compelling? approach novel?
4. Check budget: realistic + justified
5. Check team credentials: matches scope?
6. Read for: jargon, vague claims, unjustified assumptions

### "We've never applied for an NIH R01. What's the prep?"
1. Smaller grant first (R21, K, F32) if eligible — build track record
2. Talk to a program officer before drafting (essential)
3. Pre-submission inquiry where allowed
4. Get a mock review from someone who's reviewed for NIH

## Anti-patterns to avoid

- **Applying without funder fit.** Wastes 4-8 weeks.
- **Generic proposal sent to multiple funders.** Each wants a specific mental model.
- **Budget that doesn't match scope.** Reviewer red flag.
- **Vague significance statement.** "This is important" without specifics.
- **No risk discussion.** Reviewers know there's risk; not acknowledging it = naive.
- **Team without right credentials.** Match key personnel to scope.
- **Submitting at last minute.** Errors; missed letters of support.

## References

- `references/funder-fit-and-research-strategy.md` — fit dimensions, funder types, multi-funder strategy
- `references/proposal-structure-and-narrative.md` — per-funder structures, narrative discipline
- `references/budget-design-and-justification.md` — budget categories, indirect costs, common errors

## Related skills

- `research/litreview` — literature review for proposals
- `c-level-advisor/general-counsel-advisor` — legal review of terms
- `c-level-advisor/cfo-advisor` — financial review
