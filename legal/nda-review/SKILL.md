---
name: nda-review
description: >
  Deep clause-by-clause NDA review from Recipient or Discloser perspective.
  Produces issue log with redlines, fallbacks, rationales, owners, deadlines.
  Use when reviewing NDAs for negotiation or approval.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: nda-analysis
  updated: 2026-04-10
  tags: [nda, review, clause-analysis, redline, negotiation]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# NDA Review

Deep clause-by-clause NDA review tool that analyzes agreements from Recipient or Discloser perspective. Produces structured issue logs with preferred redlines, fallback positions, rationale, owners, and deadlines.

---

## Table of Contents

- [Tools](#tools)
  - [NDA Clause Reviewer](#nda-clause-reviewer)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
  - [Full NDA Review](#full-nda-review)
  - [Perspective-Based Review](#perspective-based-review)
- [Immediate Red Flags](#immediate-red-flags)
- [Review Checklists](#review-checklists)
- [Variation Callouts](#variation-callouts)
- [Risk Rating Guide](#risk-rating-guide)
- [Common Pitfalls](#common-pitfalls)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Tools

### NDA Clause Reviewer

Performs deep analysis of NDA text, extracting and classifying each clause against best practices. Detects overbroad definitions, missing carveouts, problematic residuals, IP grants, indemnification, and audit rights.

```bash
# Review from recipient perspective (default)
python scripts/nda_clause_reviewer.py nda_draft.txt

# Review from discloser perspective
python scripts/nda_clause_reviewer.py nda_draft.txt --perspective discloser

# JSON output for integration
python scripts/nda_clause_reviewer.py nda_draft.txt --json

# Save issue log
python scripts/nda_clause_reviewer.py nda_draft.txt --output issues.json --json
```

**What it produces:**
- Clause-by-clause issue log with H/M/L risk ratings
- Preferred redline for each issue
- Fallback position if preferred is rejected
- Rationale for each recommendation
- Owner assignment (legal, business, executive)
- Deadline category (pre-signing, 30-day, 90-day)

---

## Reference Guides

### NDA Clause Reference
`references/nda_clause_reference.md`

Five deep reference modules:
- Duration & Scope (term, survival, scope limitations)
- Key Clauses (definition, purpose, permitted use, marking)
- Party Obligations (standard of care, use restriction, disclosure limits)
- Remedies & Liability (injunctive relief, damages, indemnification)
- Standard Exceptions (public knowledge, prior possession, independent development, third-party receipt, legal compulsion)

### NDA Review Templates
`references/nda_review_templates.md`

Output templates and worked examples:
- Executive Summary format
- Clause-by-clause Issue Log table format
- Ownership and timing defaults by topic category
- Worked examples for social media endorsement and group licensing scenarios

---

## Workflows

### Full NDA Review

1. **Triage first** -- Run `nda-triage` skill for quick GREEN/YELLOW/RED classification
2. **Deep review** -- Run `nda_clause_reviewer.py` with appropriate `--perspective`
3. **Review issue log** -- Address HIGH-risk items first, then MEDIUM, then LOW
4. **Prepare redlines** -- Use preferred positions; prepare fallbacks
5. **Assign owners** -- Legal owns clause language; business owns commercial terms
6. **Set deadlines** -- Pre-signing items before next meeting; post-signing items within 30-90 days
7. **Negotiate** -- Present redlines; use fallbacks as needed
8. **Final review** -- Verify all issues resolved before execution

### Perspective-Based Review

| Perspective | Focus Areas | Key Concerns |
|-------------|-------------|--------------|
| Recipient | Scope of obligations, carveouts, residuals, return/destruction | Protecting freedom to operate; avoiding contamination claims |
| Discloser | Definition breadth, remedies, duration, permitted disclosures | Maximizing protection; ensuring adequate enforcement |

---

## Immediate Red Flags

Stop review and escalate if any of these 7 red flags are present.

| # | Red Flag | Why It Matters | Escalation |
|---|----------|---------------|------------|
| 1 | Non-compete clause | Restricts business operations; requires separate consideration and analysis | Senior counsel immediately |
| 2 | IP assignment or license grant | Transfers rights beyond confidentiality scope | Senior counsel immediately |
| 3 | Non-solicitation of employees or customers | Employment law implications; may be unenforceable | Senior counsel within 24 hours |
| 4 | Missing 3+ standard carveouts | Fundamentally deficient NDA | Counsel review before any response |
| 5 | Liquidated damages or penalty clause | Transforms NDA into penalty contract | Senior counsel within 24 hours |
| 6 | Perpetual obligations with no termination | Indefinite legal burden with no exit | Counsel review within 48 hours |
| 7 | Exclusivity provision | Limits engagement with other parties | Business leadership + counsel |

---

## Review Checklists

### Recipient Checklist (8 Topics)

| # | Topic | Key Questions | Risk if Missing |
|---|-------|---------------|-----------------|
| 1 | Definition Scope | Is confidential info bounded? Is there a marking requirement? | Overbroad definition traps all shared information |
| 2 | Standard Carveouts | Are all 5 carveouts present and properly drafted? | Missing carveouts restrict legitimate business activities |
| 3 | Permitted Use | Is use restricted to stated purpose? Can we share with advisors? | Overly restrictive use limits may impede evaluation |
| 4 | Residuals | Is there a residuals clause? Is it narrow or broad? | Broad residuals clause benefits; narrow or absent protects discloser |
| 5 | Return/Destruction | Return or destroy option? Retention exception for backups? | No retention exception is impractical for electronic data |
| 6 | Term & Survival | Reasonable term? Reasonable survival period? Termination right? | Perpetual obligations are burdensome |
| 7 | Remedies | Injunctive relief only? Or liquidated damages/indemnification? | Excessive remedies shift risk disproportionately |
| 8 | Problematic Provisions | Non-compete? Non-solicitation? IP assignment? Audit rights? | These provisions have no place in a standard NDA |

### Discloser Checklist (5 Topics)

| # | Topic | Key Questions | Risk if Missing |
|---|-------|---------------|-----------------|
| 1 | Definition Breadth | Does definition cover all information we will share? All forms? | Gaps in definition leave information unprotected |
| 2 | Obligation Strength | Standard of care adequate? Written agreements from recipients? | Weak obligations increase risk of unauthorized disclosure |
| 3 | Remedies | Injunctive relief available? Is it meaningful in this jurisdiction? | Without adequate remedies, NDA is unenforceable in practice |
| 4 | Duration | Is the term long enough? Does survival cover our exposure window? | Short terms may expire before information loses value |
| 5 | Recipient Limits | Who can receive? Is need-to-know enforced? Downstream binding? | Unrestricted sharing exposes information to unauthorized parties |

---

## Variation Callouts

Different NDA contexts require different review emphasis.

### M&A Context

| Additional Concern | Reason | Recommended Position |
|-------------------|--------|---------------------|
| Standstill provision | Prevents hostile acquisition moves during due diligence | Accept if mutual and time-limited (12-18 months) |
| Non-solicitation of employees | Standard in M&A NDAs | Accept if limited to key employees for 12 months |
| Broader definition | M&A requires extensive information sharing | Accept broader definition with strong carveouts |
| Longer survival | Sensitive strategic information shared | 3-5 year survival is appropriate |
| Residuals clause sensitivity | Competitive intelligence at stake | Resist residuals clause or narrow significantly |

### Employment Context

| Additional Concern | Reason | Recommended Position |
|-------------------|--------|---------------------|
| Invention assignment | Employer IP ownership | Separate from NDA; use invention assignment agreement |
| Post-employment obligations | Obligations after employment ends | Limit survival to 2 years; ensure enforceability |
| Scope of work product | What the employee creates | Define in employment agreement, not NDA |
| Non-compete enforceability | Varies by jurisdiction | Review local law before including; may be void |

### VC / Fundraising Context

| Additional Concern | Reason | Recommended Position |
|-------------------|--------|---------------------|
| Investor portfolio conflicts | VC may have portfolio companies in same space | Include portfolio company exclusion or conflict provision |
| Residuals clause | VCs see many similar pitches | Resist; protect trade secrets and specific data |
| Term limitations | VCs want short obligations | 2-3 year term acceptable; ensure adequate survival |
| Definition scope | Founders want maximum protection | Balance with investor need for portfolio flexibility |

---

## Risk Rating Guide

| Rating | Criteria | Action | Timeline |
|--------|----------|--------|----------|
| HIGH (H) | Could result in material legal or financial exposure; deal-breaker potential | Must resolve before signing | Pre-signing |
| MEDIUM (M) | Creates meaningful risk but manageable; strong preference to resolve | Should resolve; accept with documented risk if necessary | Within 30 days |
| LOW (L) | Minor preference; improves agreement but not material | Nice to resolve; concede if needed for higher-priority wins | Within 90 days |

### Risk Rating by Issue Type

| Issue Type | Typical Rating | Escalation |
|-----------|---------------|------------|
| Missing carveout (any) | M-H | Counsel |
| Overbroad definition | M | Counsel |
| Non-compete/non-solicitation | H | Senior counsel |
| IP assignment | H | Senior counsel |
| Residuals clause (broad) | M | Counsel |
| Perpetual obligations | M-H | Counsel |
| No return/destruction | M | Counsel |
| Liquidated damages | H | Senior counsel |
| Missing governing law | L-M | Counsel |
| One-sided obligations | M | Counsel |

---

## Common Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| Reviewing without knowing your perspective | Recipient and discloser have opposing interests on many clauses | Always set `--perspective` flag; review with clear role in mind |
| Treating the NDA as "just a formality" | Missing problematic provisions that create real obligations | Run full clause review on every NDA, regardless of perceived importance |
| Negotiating clause-by-clause in document order | Wastes time on early low-priority clauses; may not reach critical issues | Prioritize by risk rating; address H items first |
| Accepting "standard" NDAs without review | Every organization's "standard" is different; one party's standard favors that party | No NDA is truly standard; always review |
| Ignoring context (M&A, employment, VC) | Standard NDA review misses context-specific risks | Use variation callouts for specialized contexts |
| Not preparing fallback positions | Stuck when counterparty rejects preferred redline | Prepare preferred + fallback for every H and M item |
| Signing before resolving H-rated issues | Creates material legal exposure | Require all H items resolved or executive sign-off |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| All issues rated LOW | NDA is genuinely well-drafted, or text extraction lost key sections | Manually verify critical sections (definition, carveouts, remedies) are in the input file |
| Perspective flag has no effect | Tool adjusts weighting, not detection; same issues found either way | Perspective changes risk ratings and recommendations, not issue detection |
| Too many issues generated | NDA is non-standard or poorly drafted | Focus on H-rated issues first; use the issue log as a negotiation roadmap |
| Script misses embedded provisions | Non-compete or IP clause hidden in definitions or general provisions | Search full document for "compete", "assign", "license", "solicit" manually |
| Output format does not match template | Tool outputs structured data, not final deliverable | Use `references/nda_review_templates.md` to format the output for stakeholders |

---

## Success Criteria

- **Complete clause-by-clause review in under 15 minutes:** Automated analysis replaces 1-2 hours of manual review.
- **Zero missed HIGH-risk issues:** Every non-compete, IP assignment, and missing carveout is identified.
- **Actionable redlines for every H and M issue:** Each issue has preferred position, fallback, and rationale.
- **Clear ownership assignment:** Every issue has a designated owner (legal, business, executive).
- **Perspective-appropriate recommendations:** Recipient and discloser reviews produce different risk weightings.
- **Context-aware review:** M&A, employment, and VC variations are flagged when relevant.

---

## Scope & Limitations

**Covers:**
- Deep clause-by-clause NDA analysis with pattern matching and risk classification
- Perspective-based review (Recipient vs. Discloser)
- Issue log generation with redlines, fallbacks, rationale, owners, and deadlines
- Detection of 7 immediate red flags for triage
- Context variation awareness (M&A, Employment, VC)

**Does NOT cover:**
- **Legal advice** -- this tool supports review, it does not replace qualified legal counsel
- **Rapid triage** -- use `nda-triage` for quick GREEN/YELLOW/RED screening
- **Contract types beyond NDAs** -- use `contract-review` for general commercial agreements
- **Jurisdiction-specific enforceability analysis** -- requires local counsel assessment
- **Non-English NDAs** -- pattern matching is English-language only

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| Running deep review without triage first | Wastes time on detailed analysis of NDAs that should be rejected outright (RED triage) | Always run `nda-triage` first; only proceed to deep review for YELLOW or GREEN-with-complexity |
| Using Recipient perspective for both sides | Recipient perspective minimizes obligations and maximizes carveouts, which is wrong if you are the discloser | Always set the correct `--perspective` flag based on your role |
| Accepting all LOW-rated issues without review | Some LOW issues are low-risk individually but create cumulative exposure when combined | Review the full issue log for interaction effects; multiple LOW issues in the same area may compound to MEDIUM |
| Skipping the variation callouts for specialized contexts | Standard NDA review misses M&A standstill provisions, employment invention assignment, VC portfolio conflicts | Check the variation callouts section for your specific deal context |

---

## Tool Reference

### nda_clause_reviewer.py

**Purpose:** Performs deep clause-by-clause NDA analysis. Detects overbroad definitions, missing carveouts, problematic provisions, and generates an issue log with redlines, fallbacks, rationale, owners, and deadlines.

**Usage:**

```bash
python scripts/nda_clause_reviewer.py <nda_file> [--perspective PERSPECTIVE] [--json] [--output FILE]
```

**Flags:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `nda_file` | *(positional)* | | Path to NDA text file (.txt or .md) |
| `--perspective` | `-p` | `recipient` | Review perspective: `recipient` or `discloser` |
| `--json` | | off | Output in JSON format |
| `--output` | `-o` | *(stdout)* | Write output to file |

**Example Output (JSON):**

```json
{
  "file": "vendor_nda.txt",
  "perspective": "recipient",
  "issues": [
    {
      "id": 1,
      "clause": "Definition of Confidential Information",
      "issue": "Overbroad definition with no marking requirement",
      "risk": "H",
      "preferred_redline": "Narrow to information marked Confidential or confirmed in writing within 10 days",
      "fallback": "Add marking requirement for written; 10-day confirmation for oral",
      "rationale": "Overbroad definition traps all shared information as confidential",
      "owner": "legal",
      "deadline": "pre-signing"
    }
  ],
  "summary": {
    "total_issues": 5,
    "high": 2,
    "medium": 2,
    "low": 1
  }
}
```

**Example Output (Text):**

```
NDA CLAUSE REVIEW — ISSUE LOG
==============================
File: vendor_nda.txt
Perspective: Recipient
Issues Found: 5 (H:2 M:2 L:1)

 #  Risk  Clause                           Issue
 1  H     Definition of Confidential Info  Overbroad definition; no marking requirement
        Preferred: Narrow to marked information with 10-day oral confirmation
        Fallback:  Add marking requirement for written; 10-day confirmation for oral
        Rationale: Overbroad definition traps all shared information
        Owner: legal | Deadline: pre-signing

 2  H     Standard Carveouts               Missing independent development carveout
        Preferred: Add standard independent development exception
        Fallback:  Add with documentary evidence requirement
        Rationale: Missing carveout blocks internal R&D
        Owner: legal | Deadline: pre-signing
```
