# Prototype Handoff: <initiative name>

<!-- Fill every section. Validate with:
     python3 scripts/prototype_handoff_checker.py --input this-file.md
     Headings are matched by keyword, so keep the words shown in each heading. -->

**Owner (PM):** <name>  **Engineering lead:** <name>  **Date:** <YYYY-MM-DD>

## Prototype link
- <URL to the prototype, version or commit>

## Disposition
- <throwaway | starting point> - <one sentence on what engineering may reuse>

## Problem and users
- <Who has the problem, what it costs them, and the evidence (interviews, tickets, data)>

## Success metrics
- <Metric> - baseline <value>, target <value>, window <period>

## Validated findings
- <Hypothesis> - <n> participants - threshold <pre-set bar> - result <what happened> - <validated | invalidated | open>

## Acceptance criteria
- Given <context>, when <action>, then <observable, measurable result>

## Non-goals
- <What this build will explicitly not do, even though the prototype showed it>

## Constraints
- <Technical, legal, budget, timeline>

## Risks and open questions
- <Risk, owner, how and when it gets retired>

## Throwaway list (what the prototype skipped)
- Auth: <...>
- Error states: <...>
- Accessibility: <...>
- Security: <...>
- Performance: <...>
- Data model: <...>

## Data and privacy
- Real customer data used in prototype tools: <no | yes - approval reference>
- <Where the prototype data came from; what the tool retains>

## Security
- <Secrets used? Repo/tool access? Is generated code being merged? Review path>

## Accessibility
- <Baseline for the production build, e.g. WCAG 2.2 AA, plus known gaps from testing>

## IP and licensing
- <Tool terms reviewed? Output ownership? Third-party assets, fonts, code licenses>
