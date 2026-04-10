# NDA Review Templates

Output templates for NDA review deliverables. Includes Executive Summary format, clause-by-clause Issue Log table, ownership and timing defaults, and worked examples.

---

## Table of Contents

- [Executive Summary Template](#executive-summary-template)
- [Clause-by-Clause Issue Log](#clause-by-clause-issue-log)
- [Ownership and Timing Defaults](#ownership-and-timing-defaults)
- [Worked Example: Social Media Endorsement NDA](#worked-example-social-media-endorsement-nda)
- [Worked Example: Group Licensing NDA](#worked-example-group-licensing-nda)
- [Redline Delivery Template](#redline-delivery-template)

---

## Executive Summary Template

Use this format for communicating NDA review findings to business stakeholders.

### Template

```
NDA REVIEW — EXECUTIVE SUMMARY
================================
Agreement:    [Counterparty Name] Mutual/Unilateral NDA
Reviewer:     [Name]
Date:         [Date]
Perspective:  Recipient / Discloser
Status:       GREEN / YELLOW / RED

OVERVIEW
--------
[1-2 sentence description of the NDA scope and purpose]

RISK ASSESSMENT
---------------
HIGH-risk issues:   [count]
MEDIUM-risk issues: [count]
LOW-risk issues:    [count]

KEY FINDINGS
------------
1. [Most critical finding with one-line description]
2. [Second most critical finding]
3. [Third most critical finding]

RECOMMENDATION
--------------
[One of the following:]
- SIGN: No material issues. Proceed with execution.
- NEGOTIATE: [X] issues require resolution before signing.
  Priority items: [list top 2-3 issues]
- REJECT: Material structural deficiencies. [Brief reason]
- ESCALATE: [Brief reason and escalation target]

NEXT STEPS
----------
1. [Specific action item with owner]
2. [Specific action item with owner]
3. [Specific action item with owner]

TIMELINE
--------
Redlines due to counterparty: [date]
Target execution date: [date]
```

### Filled Example

```
NDA REVIEW — EXECUTIVE SUMMARY
================================
Agreement:    Acme Corp Mutual NDA
Reviewer:     Legal Team
Date:         2026-04-10
Perspective:  Recipient
Status:       YELLOW

OVERVIEW
--------
Mutual NDA covering evaluation of potential technology partnership.
Standard bilateral structure with 3-year term.

RISK ASSESSMENT
---------------
HIGH-risk issues:   1
MEDIUM-risk issues: 2
LOW-risk issues:    1

KEY FINDINGS
------------
1. Missing independent development carveout (HIGH) — blocks R&D freedom
2. Overbroad definition without marking requirement (MEDIUM)
3. Residuals clause with no trade secret exclusion (MEDIUM)

RECOMMENDATION
--------------
NEGOTIATE: 3 issues require resolution before signing.
Priority items: independent development carveout, definition narrowing

NEXT STEPS
----------
1. Legal to prepare redline with carveout language (owner: outside counsel)
2. Business to confirm scope of anticipated information sharing (owner: BD lead)
3. Schedule counterparty call to discuss redlines (owner: legal)

TIMELINE
--------
Redlines due to counterparty: 2026-04-14
Target execution date: 2026-04-21
```

---

## Clause-by-Clause Issue Log

### Table Format

| # | Risk | Clause | Issue | Preferred Redline | Fallback | Rationale | Owner | Deadline |
|---|------|--------|-------|-------------------|----------|-----------|-------|----------|
| 1 | H | [Clause name] | [Issue description] | [Proposed language] | [Alternative] | [Why it matters] | [legal/business/exec] | [pre-signing/30d/90d] |

### Column Definitions

| Column | Description | Values |
|--------|-------------|--------|
| # | Sequential issue number | 1, 2, 3... |
| Risk | Risk rating | H (High), M (Medium), L (Low) |
| Clause | NDA clause or section | Definition, Carveouts, Obligations, Remedies, Term, etc. |
| Issue | Brief description of the problem | Factual, specific |
| Preferred Redline | Recommended contract language change | Specific proposed language |
| Fallback | Alternative if preferred is rejected | Less ideal but acceptable |
| Rationale | Why this change matters | Business or legal justification |
| Owner | Who is responsible for resolution | legal, business, executive |
| Deadline | When this must be resolved | pre-signing, 30-day, 90-day |

### Filled Example

| # | Risk | Clause | Issue | Preferred Redline | Fallback | Rationale | Owner | Deadline |
|---|------|--------|-------|-------------------|----------|-----------|-------|----------|
| 1 | H | Carveouts | Missing independent development carveout | Add: "Information independently developed without use of or reference to Confidential Information" | Add with documentary evidence requirement | Missing carveout blocks internal R&D; contamination risk | legal | pre-signing |
| 2 | M | Definition | Overbroad; no marking requirement | Narrow to marked information with 10-day oral confirmation | Add "reasonably understood to be confidential" standard | All shared information becomes confidential without marking | legal | pre-signing |
| 3 | M | Residuals | Broad residuals clause; no trade secret exclusion | Delete residuals clause | Narrow to exclude trade secrets and specific data | Residuals clause undermines NDA protection for key information | legal | pre-signing |
| 4 | L | Governing Law | Counterparty's home jurisdiction | Change to neutral jurisdiction (Delaware) | Accept with arbitration under AAA rules | Unfamiliar jurisdiction increases litigation cost | legal | pre-signing |

---

## Ownership and Timing Defaults

### Owner Assignment by Topic

| Topic Category | Default Owner | Escalation To | Rationale |
|---------------|---------------|---------------|-----------|
| Definition scope and carveouts | Legal counsel | Senior counsel | Legal interpretation; enforceability |
| Obligations and standard of care | Legal counsel | Senior counsel | Legal risk assessment |
| Remedies and liability | Legal counsel | General counsel | Financial exposure |
| Term and duration | Business lead | Legal counsel | Business relationship decision |
| Purpose and scope | Business lead | Legal counsel | Business context dependent |
| Governing law and jurisdiction | Legal counsel | General counsel | Litigation strategy |
| Non-compete / non-solicitation | Senior counsel | General counsel | Significant business restriction |
| IP assignment | Senior counsel | General counsel | Material IP implications |
| Data protection provisions | Privacy counsel / DPO | Legal counsel | Regulatory compliance |
| Commercial terms | Business lead | Finance | Business decision |

### Deadline Categories

| Category | Meaning | Standard Timeline | Applies To |
|----------|---------|-------------------|------------|
| Pre-signing | Must be resolved before execution | Before next counterparty meeting | All H-risk issues; structural M-risk issues |
| 30-day | Should be resolved within 30 days of signing | 30 calendar days | M-risk issues that can be addressed via amendment |
| 90-day | Nice to resolve within 90 days | 90 calendar days | L-risk issues; process improvements |

### Escalation Triggers

| Trigger | Escalation Target | Timeline |
|---------|-------------------|----------|
| Any H-risk issue unresolved after 2 negotiation rounds | General counsel | Immediate |
| Counterparty refuses all fallback positions | Senior counsel + business leadership | Within 48 hours |
| Non-compete or IP clause in NDA | Senior counsel | Immediate upon detection |
| Deal timeline pressure vs. unresolved issues | General counsel + business sponsor | Before signing deadline |

---

## Worked Example: Social Media Endorsement NDA

### Context
A consumer brand asks an influencer to sign an NDA before discussing a paid endorsement partnership. The influencer is the **recipient** of confidential brand strategy information.

### Issue Log

| # | Risk | Clause | Issue | Preferred Redline | Fallback | Owner | Deadline |
|---|------|--------|-------|-------------------|----------|-------|----------|
| 1 | H | Definition | "All information shared during any meeting or call" — no marking, no boundaries | Narrow to information relating to the endorsement campaign, marked Confidential | Add: "reasonably understood to be confidential given the context" | legal | pre-signing |
| 2 | H | Carveouts | Missing independent development carveout | Add all 5 standard carveouts | At minimum add public knowledge and independent development | legal | pre-signing |
| 3 | H | Problematic | Non-compete: "shall not endorse competing brands for 24 months" | Delete entirely; address exclusivity in endorsement agreement, not NDA | Reduce to 6 months, limited to directly competing products | legal | pre-signing |
| 4 | M | Term | 5-year term with 3-year survival for endorsement evaluation | Reduce to 1-year term with 1-year survival | 2-year term with 2-year survival | business | pre-signing |
| 5 | M | Remedies | Liquidated damages of $50,000 per breach | Delete; use standard breach remedies | Cap at $10,000 with materiality threshold | legal | pre-signing |
| 6 | L | Governing Law | New York law; exclusive jurisdiction | Accept (standard for media/entertainment) | N/A | legal | pre-signing |

### Key Observations
- Non-compete clause in an NDA is a RED flag; should be in the endorsement agreement with proper consideration
- Liquidated damages are excessive for an NDA; more appropriate for the endorsement agreement itself
- 5-year term is disproportionate to the likely engagement duration

---

## Worked Example: Group Licensing NDA

### Context
A sports league shares player performance data with a data analytics company for a licensing evaluation. The analytics company is the **recipient** of proprietary player data, statistics, and business terms.

### Issue Log

| # | Risk | Clause | Issue | Preferred Redline | Fallback | Owner | Deadline |
|---|------|--------|-------|-------------------|----------|-------|----------|
| 1 | H | Definition | Includes "any derivative analysis or insights generated from the data" | Limit to raw data provided; exclude independently generated analysis | Add: "derivatives are confidential only if they would reveal the underlying Confidential Information" | legal | pre-signing |
| 2 | H | Residuals | No residuals clause; analytics team will inherently retain knowledge | Add standard residuals clause for general knowledge and techniques | Add residuals limited to general analytical methodology, excluding specific data points | business | pre-signing |
| 3 | M | IP | "All analysis, models, and outputs shall be the property of the League" | NDA should not address IP; reserve for licensing agreement | Add: "Pre-existing analytical tools and methodologies remain property of the recipient" | legal | pre-signing |
| 4 | M | Term | 3-year term covering evaluation period | Reduce to 12 months (evaluation should not take 3 years) | Accept 18 months with convenience termination after 6 months | business | pre-signing |
| 5 | M | Return | "Return or destroy all data, analyses, derivatives, and models" | Limit to raw data; retain independently created analysis | Add retention exception for de-identified aggregate statistics | legal | pre-signing |
| 6 | L | Permitted | No disclosure to sub-contractors or cloud service providers | Add: permitted disclosure to sub-contractors bound by equivalent obligations | Add: permitted storage on secure cloud infrastructure | legal | pre-signing |

### Key Observations
- Derivative works clause is critical -- analytics company must protect its ability to use general skills and knowledge
- Residuals clause is important FROM the recipient perspective (unusual) because analysts will inherently retain general knowledge
- IP ownership clause has no place in an NDA; defer to the licensing agreement
- Return/destruction of independently created analysis is unreasonable

---

## Redline Delivery Template

Use this format when sending redline markup to the counterparty.

### Email Template

```
Subject: [Company Name] — NDA Redline Comments

Dear [Counterparty Contact],

Thank you for sharing the proposed NDA. We have completed our review and
have the following comments, organized by priority:

MUST-RESOLVE (before execution):
1. [Section X.X] — [Brief description and proposed language]
2. [Section X.X] — [Brief description and proposed language]

STRONG PREFERENCES (recommend resolving):
3. [Section X.X] — [Brief description and proposed language]
4. [Section X.X] — [Brief description and proposed language]

MINOR COMMENTS (flexible):
5. [Section X.X] — [Brief description and proposed language]

We are happy to discuss these comments at your convenience. Our goal is
to finalize the NDA by [target date] so we can proceed with [purpose].

Best regards,
[Name]
```

### Redline Markup Format

For each redline in the marked-up document:

```
[SECTION X.X — CLAUSE NAME]

CURRENT TEXT:
"[Exact current language from the NDA]"

PROPOSED TEXT:
"[Your proposed replacement language, with changes highlighted]"

RATIONALE:
[One sentence explaining why the change is needed]

PRIORITY: Must-Resolve / Strong Preference / Minor Comment
```
