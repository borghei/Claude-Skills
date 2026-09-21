# Prototype Decision Guide

Deep reference for choosing **whether** to prototype, **how far up the fidelity ladder** to go, and **how to brief** an AI generation tool. SKILL.md holds the short version; this file holds the reasoning and the edge cases.

---

## 1. Prototype vs. spec: the uncertainty test

Every product bet carries four kinds of risk. They are the standard product-discovery risk categories, and they map cleanly to what a prototype can and cannot tell you.

| Uncertainty | The question | Can a prototype answer it? | Best first move |
|-------------|--------------|----------------------------|-----------------|
| **Desirability** | Will the target users want this enough to change behavior? | Partly. A prototype shows the idea concretely, but stated interest is weak evidence. Pair it with a commitment ask. | Interview or smoke test if there is no evidence yet; then a clickable concept with a commitment ask. |
| **Usability** | Can users figure out how to use it and succeed at the job? | Yes. This is what prototypes are best at. | Clickable or working prototype, moderated task test. |
| **Feasibility** | Can we build it with our stack, data, latency and cost limits? | Yes, if the prototype exercises the riskiest technical path. A pretty UI over mocked calls proves nothing. | Engineering spike, often with an AI coding assistant, measured against a technical bar. |
| **Viability** | Does it work for the business: pricing, margin, legal, sales, support, brand? | No. A prototype can support a conversation, never settle it. | Model it (unit economics, pricing research) and get the review (legal, security, finance). |

### Decision rules [RECOMMENDED]

1. **Write the spec first** when the dominant risk is viability, or when the solution is already well understood (a known pattern, a regulatory requirement, a parity feature). Prototyping a known solution is theater.
2. **Prototype first** when the dominant risk is usability or desirability and the team is arguing about what the thing should look like. Ten minutes with a working flow ends debates that a document keeps alive.
3. **Spike first** when the dominant risk is feasibility. Build the hardest path, not the happy screens.
4. **Do both, in parallel** when risk is spread. The prototype carries the learning; the spec carries the decision (problem, metrics, constraints, non-goals, risks).
5. **Do neither yet** when there is no evidence the problem exists. Go talk to users.

`scripts/prototype_plan.py` encodes these rules. It weights each hypothesis by `impact x evidence gap` and reports whether the initiative is prototype-led or spec-led.

---

## 2. The fidelity ladder

| Rung | What it is | Typical tool category | Good for | Traps |
|------|------------|-----------------------|----------|-------|
| **F0** No prototype | Interview script, landing page, spreadsheet model, written spec | None | Viability, early desirability, known solutions | Skipping it because generating screens feels like progress |
| **F1** Prompted mock | Static screens generated from a prompt | AI design tool, AI app builder | Concept tests, aligning stakeholders, comparing 3 directions fast | Users react to visual polish, not the idea |
| **F2** Clickable | Linked screens, scripted happy path | AI design tool, AI app builder | Navigation, information architecture, first-use comprehension | Participants hit an unlinked area and the session derails |
| **F3** Working, synthetic data | Real logic, real state, fake data | AI app builder, AI coding assistant | Dynamic flows (filters, validation, multi-step forms), feasibility spikes | Synthetic data too clean: real data is messier |
| **F4** Working, real data | Real logic on real (approved) data | AI coding assistant in an approved environment | Data-dependent value (recommendations, search relevance, AI output quality) | Privacy and security exposure; the prototype quietly becomes production |

### Climbing rules [RECOMMENDED]

- **Start at the lowest rung that can falsify the hypothesis.** If a static screen can kill the idea, do not build a working app.
- **Climb only when the lower rung passed** or when the lower rung cannot, by construction, test the risk (for example, AI output quality needs F3 or F4).
- **F4 requires written approval** from the data owner and security before any real customer data touches a prototype tool. `prototype_plan.py` downgrades F4 to F3 until `constraints.real_data_approved` is true.
- **Generate variants, not versions.** Two or three variants of the same flow, each representing a different candidate solution, teach more than one polished version.

---

## 3. Briefing an AI generation tool

AI app builders, AI design tools and AI coding assistants all respond to the same brief structure. Use `assets/prototype_brief_template.md`.

### The seven parts of a good prototype prompt

1. **Role and disposability.** "You are building a throwaway prototype to test one hypothesis. It will not ship." This reduces the tool's tendency to add scaffolding you will then have to explain away.
2. **User and context.** Persona, device, environment, accessibility needs. "A finance approver on a phone between meetings" produces a different layout than "an approver".
3. **The job, in the user's words.** Taken from interviews, not from the team's feature list.
4. **An explicit screen and state list.** Include the error or empty states the test tasks will hit. Tools generate happy paths by default.
5. **Synthetic data, supplied or described.** Never let the tool pull or invent realistic personal data. Supply the dataset or describe its shape.
6. **Constraints.** Platform, visual style (existing design tokens or deliberately plain), accessibility baseline, "no login".
7. **Out of scope.** The things the tool will be tempted to add. Anything you did not ask for is a distraction in the test.

### Iteration pattern [RECOMMENDED]

- Generate, then **edit the brief, not the output**, when the result is structurally wrong. Patching generated output by hand drifts away from the brief and makes variants inconsistent.
- Keep each variant's brief in version control next to the test plan. The brief is the reproducible record of what was tested.
- Stop polishing when the prototype can run every test task. Extra fidelity beyond the tasks is waste and biases participants toward "it looks finished".

---

## 4. Worked decision examples

| Situation | Dominant risk | Recommendation |
|-----------|---------------|----------------|
| "Should approvals move to mobile?" with anecdotal requests | Desirability | F2 concept with a pilot-waitlist ask, 2 variants |
| New multi-step onboarding with branching logic | Usability | F3 working prototype with synthetic accounts |
| "Can we summarize support threads well enough?" | Feasibility (AI quality) | F3 spike on synthetic or public data; F4 only with approval |
| Adding SSO for enterprise deals | Viability / known solution | F0: spec it. The pattern is known; the risk is scope and sales timing |
| New pricing tier | Viability | F0: pricing research and a model. A prototype pricing page cannot prove willingness to pay |
| Replacing a report with a dashboard | Usability + desirability | F2 clickable with real-shaped synthetic data; test with current report users |

---

## 5. Sample size guidance, stated honestly

`prototype_plan.py` prints planning defaults, not statistical guarantees:

- **Usability rounds:** small qualitative rounds (5-8 target users per segment), fix what you saw, then run another round. Small rounds find the big problems; they do not estimate rates.
- **Desirability:** a slightly larger qualitative set per segment (8-12) with a **commitment** ask, because opinions vary more than task behavior.
- **Feasibility and viability:** no user sample. They are judged against a technical bar or a business review.

If a decision needs a *rate* with a confidence interval (conversion, retention, preference share), a prototype test is the wrong instrument. Use a powered quantitative test (A/B, survey with a sample size calculation) after the prototype has narrowed the options.
