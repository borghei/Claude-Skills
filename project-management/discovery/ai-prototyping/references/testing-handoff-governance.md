# Testing, Handoff and Governance

Deep reference for running prototype tests without fooling yourself, handing a prototype to engineering without shipping it by accident, and keeping prototype tools inside security, privacy, IP and accessibility guardrails.

---

## 1. Running the test

### Before the session [PROVEN]

- **Pre-register the threshold.** Write the success and kill criteria in the plan before the first session. A threshold chosen after seeing results is a rationalization.
- **Recruit the target segment.** Colleagues, friends and the sales team's favorite customer are not the segment. Screen for the behavior the hypothesis is about.
- **Write goal-based tasks.** "You have three expenses waiting. Deal with the one that breaks policy." Not "Click the red badge." Tasks that name UI elements test reading, not usability.
- **Dry-run the prototype on every task.** Generated prototypes break at the edges. A dead click in session 1 wastes a participant.

### During the session

- Say plainly: "This is an early prototype. Some things will not work. We are testing the design, not you."
- Do not help. When a participant is stuck, ask "What would you expect to happen?" and note it as a failure.
- Record **behavior** per task: unassisted success, time, errors, hesitation points. Record quotes separately.
- For desirability, end with a **commitment ask** (waitlist, pilot sign-up, calendar slot, letter of intent). Count commitments, not compliments.

### Avoiding demo-ware bias [RECOMMENDED]

Demo-ware bias is what happens when a polished prototype is *presented* rather than *tested*. The audience reacts to the polish and the presenter's enthusiasm, and the team hears validation.

| Symptom | Fix |
|---------|-----|
| The PM drives the prototype while the user watches | The user drives. The PM is silent. |
| Feedback is "looks great", "love it" | Ask for a commitment. Measure task success. |
| Only the happy path exists | Include at least one task that hits an error or edge state. |
| Stakeholders see it before users do | Show users first; stakeholders get the findings, not the demo. |
| Results reported as "users liked it" | Report "5 of 6 completed task 2 unassisted against a bar of 5 of 6". |
| One variant only | Test two or three variants so preference has a comparison. |

### Synthesizing

- Tabulate each task by participant (success / fail / assisted). Look at the failures first.
- Compare against the pre-set threshold. Three outcomes only: **validated**, **invalidated**, **inconclusive** (re-run with fixes, do not extend forever).
- Record results on the hypothesis, not in a slide. The handoff checker reads them from there.

---

## 2. What must still be written down

A prototype shows **a** solution. It does not record **why**, **for whom**, **how we will know it worked**, or **what we decided not to do**. These live in the spec or PRD, and in the handoff:

| Item | Why the prototype cannot carry it |
|------|-----------------------------------|
| Problem and users, with evidence | Screens show a solution; the problem is invisible in them |
| Success metrics (baseline, target, window) | A prototype has no production data |
| Constraints (technical, legal, budget, timeline) | Generation tools ignore constraints they were not given |
| Non-goals | Every visible element looks in scope unless written out |
| Risks and open questions | Unvalidated hypotheses look settled once rendered |
| Data and privacy decisions | The prototype used fake data; the product will not |

---

## 3. Handoff to engineering

### Principle: a prototype is not production code [PROVEN]

Generated prototype code is optimized for speed of learning. Unless the team has explicitly built it on the production stack with production review, assume it skips:

- **Auth and authorization** (hard-coded users, no roles)
- **Error, empty, loading and offline states**
- **Accessibility** (labels, focus order, contrast, screen reader support)
- **Security** (input validation, output encoding, rate limiting, dependency review, secrets handling)
- **Performance** (small synthetic datasets, no pagination, no caching)
- **Data model** (flat mocks, no migrations, no audit trail)
- **Observability** (no logging, metrics or alerts)
- **Tests**

List each explicitly in the handoff's **throwaway list**. `prototype_handoff_checker.py` warns when any of the first six are missing from it.

### Disposition: throwaway or starting point

Say which, in one sentence. "Starting point" is legitimate only when the prototype was built on the production stack, in a repository engineering owns, and it still goes through normal code review and security review. Otherwise it is throwaway, and engineering reuses flow, copy and decisions, not code.

### Extracting acceptance criteria from a validated prototype

1. For each test task that passed, write the **observable outcome** as a Given/When/Then.
2. For each failure that was fixed, write a criterion that would have caught it ("the violation badge appears above the approve button").
3. Add non-functional criteria the prototype ignored: performance budget, accessibility level, security requirements.
4. Keep criteria testable: a number, a state, a visible element. "Recap should be good" is not a criterion.

### The handoff package

Use `assets/handoff_template.md` (or the JSON shape in `assets/handoff_complete.json`) and run:

```bash
python3 scripts/prototype_handoff_checker.py --input handoff.md
python3 scripts/prototype_handoff_checker.py --input handoff.md --strict   # warnings block too
```

---

## 4. Governance

### Data and privacy

- **Default: no real customer, employee or partner data in prototype tools.** Many AI tools process and may retain inputs; their terms differ and change. Use synthetic data built to the real data's shape.
- Real data (fidelity F4) needs a written approval reference from the data owner and security/privacy, and the tool's data-retention and training-on-inputs settings checked and recorded.
- If personal data was used without approval, treat it as a potential data incident and follow your organization's incident process. Do not quietly delete and move on.

### Security

- No production secrets, API keys, internal hostnames or customer identifiers in prompts, code or screenshots.
- Prototype repositories: private, owned by the team, archived read-only after the handoff.
- Prompt injection: when a prototype calls an LLM with user-supplied or retrieved content, treat that content as untrusted. OWASP lists prompt injection first in its Top 10 for LLM applications (LLM01:2025, genai.owasp.org). A prototype is where this pattern gets copied into production, so flag it in the handoff.
- Generated code that will be reused goes through the same review, dependency scanning and security review as any other code.

### Intellectual property

- Check the tool's terms for output ownership and whether inputs are used for training. Record who checked and when.
- Avoid pasting proprietary third-party material (competitor screenshots, licensed fonts, paid icon sets) into generation prompts.
- Generated code may resemble open-source code. If the prototype becomes a starting point, it needs the same license and provenance review as other code.

### Accessibility baseline

- Brief the tool with an accessibility baseline: labelled controls, visible focus, sufficient contrast. The W3C Web Content Accessibility Guidelines (WCAG 2.2, a W3C Recommendation, w3.org/TR/WCAG22) define levels A, AA and AAA; many organizations set AA as their baseline.
- Recruit at least some participants who use assistive technology when the product's users do. A prototype that fails them early is cheaper than a rebuild later.
- Put accessibility gaps found during testing in the throwaway list and the acceptance criteria.

---

## 5. Health rubric - is this prototype effort healthy?

Score each dimension 0-2 (0 = absent, 1 = partial, 2 = solid). 12+ of 16 is healthy; under 8 means stop and fix the process before building more.

| Dimension | 2 looks like |
|-----------|--------------|
| Hypothesis quality | Every hypothesis has uncertainty type, metric, threshold, segment (`prototype_plan.py` exits 0) |
| Right instrument | Viability routed to F0; lowest falsifying rung chosen |
| Variants | 2-3 variants per key flow, each a distinct solution |
| Test rigor | Pre-registered thresholds, goal-based tasks, target segment, user drives |
| Evidence | Findings reported as counts against thresholds; commitment asks for desirability |
| Written decisions | Problem, metrics, constraints, non-goals, risks in the spec/PRD |
| Handoff | `prototype_handoff_checker.py` exits 0; disposition stated; acceptance criteria extracted |
| Governance | No unapproved real data; secrets clean; IP and accessibility recorded |

---

## 6. Sources

- W3C, *Web Content Accessibility Guidelines (WCAG) 2.2*, W3C Recommendation: https://www.w3.org/TR/WCAG22/
- OWASP GenAI Security Project, *LLM01:2025 Prompt Injection*: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
