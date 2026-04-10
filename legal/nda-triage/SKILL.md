---
name: nda-triage
description: >
  Rapid NDA screening with GREEN/YELLOW/RED classification. 10-point
  checklist for incoming NDAs. Use when triaging NDAs, screening
  non-disclosure agreements, or routing NDAs for approval.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: nda-screening
  updated: 2026-04-10
  tags: [nda, screening, triage, non-disclosure, legal-review]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# NDA Triage

Rapid NDA screening tool that classifies incoming NDAs as GREEN (standard approval), YELLOW (counsel review), or RED (significant issues). Uses a 10-point screening checklist to evaluate agreement structure, definitions, obligations, carveouts, and problematic provisions.

---

## Table of Contents

- [Tools](#tools)
  - [NDA Screener](#nda-screener)
  - [NDA Checklist](#nda-checklist)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
  - [Standard NDA Triage](#standard-nda-triage)
  - [Bulk NDA Processing](#bulk-nda-processing)
- [Routing Recommendations](#routing-recommendations)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Tools

### NDA Screener

Scans NDA text for red flags and outputs GREEN/YELLOW/RED classification with reasoning.

```bash
# Screen an NDA file
python scripts/nda_screener.py nda_draft.txt

# JSON output for integration
python scripts/nda_screener.py incoming_nda.md --json

# Save screening results
python scripts/nda_screener.py nda_draft.txt --output screening.json --json
```

**What it detects:**
- Missing standard carveouts (public knowledge, prior possession, independent development, third-party receipt, legal compulsion)
- Non-solicitation and non-compete clauses
- Perpetual confidentiality obligations
- Overbroad definition of confidential information
- Residuals clauses granting usage rights to ideas/concepts
- IP assignment or license grants
- Liquidated damages provisions
- Unlimited audit rights
- One-sided obligations

**Classification Rules:**

| Level | Criteria | Routing |
|-------|----------|---------|
| GREEN | All 5 carveouts present, no problematic provisions, standard structure | Business approver; no counsel needed |
| YELLOW | 1-2 missing carveouts, minor problematic provisions, or non-standard terms | Legal counsel review within 48 hours |
| RED | 3+ missing carveouts, non-compete/non-solicitation, IP assignment, perpetual term with no exit | Senior counsel review; do not sign |

---

### NDA Checklist

Generates a compliance checklist for an NDA, checking all 10 screening criteria with pass/fail status.

```bash
# Generate checklist for an NDA
python scripts/nda_checklist.py nda_draft.txt

# JSON output
python scripts/nda_checklist.py nda_draft.txt --json

# Save checklist
python scripts/nda_checklist.py nda_draft.txt --output checklist.json --json
```

**10-Point Screening Criteria:**

| # | Criterion | What It Checks |
|---|-----------|---------------|
| 1 | Agreement Structure | Mutual vs. one-way; parties identified; purpose stated |
| 2 | Definition of Confidential Info | Scope, specificity, marking requirements |
| 3 | Obligations | Standard of care, use restrictions, disclosure limits |
| 4 | Standard Carveouts | 5 required: public knowledge, prior possession, independent development, third-party receipt, legal compulsion |
| 5 | Permitted Disclosures | Representatives, advisors, affiliates with need-to-know |
| 6 | Term & Duration | Reasonable term, survival period, obligations after expiry |
| 7 | Return/Destruction | Obligation to return or destroy upon request/termination |
| 8 | Remedies | Injunctive relief, damages, indemnification scope |
| 9 | Problematic Provisions | Non-solicitation, non-compete, exclusivity, residuals, IP assignment, audit rights |
| 10 | Governing Law | Jurisdiction, dispute resolution mechanism |

---

## Reference Guides

### NDA Screening Criteria
`references/nda_screening_criteria.md`

Complete evaluation reference covering:
- All 10 screening criteria with detailed sub-items
- GREEN/YELLOW/RED classification rules with specific examples
- Common NDA issues with standard positions
- Redline approaches for common problems

---

## Workflows

### Standard NDA Triage

1. **Receive NDA** -- Save as `.txt` or `.md` file
2. **Screen** -- Run `nda_screener.py` for quick RED/YELLOW/GREEN classification
3. **Checklist** -- Run `nda_checklist.py` for detailed 10-point evaluation
4. **Route** -- Follow routing recommendations based on classification
5. **Track** -- Log screening result and routing decision

### Bulk NDA Processing

```bash
# Screen multiple NDAs
for nda in ndas/*.txt; do
  echo "=== $nda ==="
  python scripts/nda_screener.py "$nda"
  echo ""
done

# Generate JSON report for all NDAs
for nda in ndas/*.txt; do
  python scripts/nda_screener.py "$nda" --json --output "results/$(basename $nda .txt).json"
done
```

---

## Routing Recommendations

| Classification | Approver | Timeline | Escalation |
|---------------|----------|----------|------------|
| GREEN | Business owner or designated approver | Same day; sign within 24 hours | None required |
| YELLOW | Legal counsel review | 48-hour turnaround | Escalate to senior counsel if no response in 72 hours |
| RED | Senior legal counsel | 5 business day turnaround | Escalate to General Counsel if deal-critical |

### GREEN Fast-Track Conditions

All of the following must be true for GREEN classification:
- Mutual NDA (both parties bound)
- All 5 standard carveouts present
- No non-solicitation, non-compete, or exclusivity clauses
- No IP assignment or license grants
- No residuals clause
- Term is 2-5 years (not perpetual)
- Return/destruction obligation present
- Standard remedies (injunctive relief, no liquidated damages)

### RED Escalation Triggers

Any one of the following triggers RED classification:
- Non-compete clause of any scope
- Non-solicitation clause covering employees or customers
- IP assignment or broad license grant
- Missing 3 or more standard carveouts
- Perpetual obligations with no termination right
- Liquidated damages for breach
- Exclusivity provision

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Screener classifies everything as YELLOW | NDA uses non-standard formatting that breaks pattern matching | Ensure NDA is clean plain text; remove PDF artifacts and headers/footers |
| Missing carveouts false positive | Carveouts are present but use unusual language | Review the full "Exceptions" or "Exclusions" section manually; the screener checks common phrasings |
| Non-compete not detected | Non-compete is embedded in definitions or obligations section rather than standalone | Search the full document for "compete", "competitive", "restrict" manually |
| Checklist shows PASS but screener shows RED | Checklist evaluates presence; screener evaluates content quality | Use both tools together; the screener's RED overrides checklist PASS |
| Script errors on large files | NDA text exceeds expected size (>100KB) | Ensure the file contains only the NDA text, not appendices or exhibits |

---

## Success Criteria

- **NDA triage under 5 minutes:** Automated screening replaces 30-minute manual review.
- **Zero missed RED-severity issues:** Every non-compete, IP assignment, and missing carveout is flagged.
- **GREEN NDAs signed within 24 hours:** Fast-track routing eliminates bottleneck for standard agreements.
- **YELLOW NDAs resolved within 48 hours:** Counsel review turnaround meets SLA.
- **Consistent classification across reviewers:** 10-point checklist eliminates subjective "looks fine" approvals.
- **100% of NDAs screened before routing:** No NDA reaches an approver without automated triage.

---

## Scope & Limitations

**Covers:**
- Pattern-based screening of NDA text for structural issues and problematic provisions
- 10-point compliance checklist against standard NDA requirements
- GREEN/YELLOW/RED classification with routing recommendations
- Detection of non-solicitation, non-compete, IP assignment, residuals, and other problematic clauses
- Missing carveout identification

**Does NOT cover:**
- **Legal advice** -- classification is a screening aid, not a legal opinion
- **Negotiation or redlining** -- use `nda-review` for deep clause analysis and redline generation
- **Multi-party NDAs** -- optimized for bilateral (two-party) agreements
- **Industry-specific NDA requirements** (healthcare, defense, government) -- patterns target commercial NDAs
- **Non-English NDAs** -- pattern matching is English-language only

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| Signing GREEN-classified NDAs without any human review | Automated screening cannot catch business-context risks (e.g., NDA with a direct competitor) | GREEN classification means low legal risk, not zero risk; business approver must still review |
| Using triage as a substitute for deep NDA review on complex deals | Triage checks structure and red flags, not clause quality or negotiation position | Run `nda-review` skill for M&A, joint venture, or high-value partnership NDAs |
| Ignoring YELLOW classifications because "it's just an NDA" | YELLOW items like missing carveouts or residuals clauses create real legal exposure | Route all YELLOW NDAs to counsel; missing independent development carveout alone can cost millions |
| Treating all NDAs as equal regardless of counterparty relationship | NDA with a startup partner requires different scrutiny than NDA with a Fortune 500 vendor | Adjust review depth based on counterparty, deal value, and information sensitivity |

---

## Tool Reference

### nda_screener.py

**Purpose:** Scans NDA text for red flags and problematic provisions. Outputs GREEN/YELLOW/RED classification with detailed reasoning.

**Usage:**

```bash
python scripts/nda_screener.py <nda_file> [--json] [--output FILE]
```

**Flags:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `nda_file` | *(positional)* | | Path to NDA text file (.txt or .md) |
| `--json` | | off | Output in JSON format |
| `--output` | `-o` | *(stdout)* | Write output to file |

**Example Output (JSON):**

```json
{
  "file": "vendor_nda.txt",
  "classification": "YELLOW",
  "red_flags": [
    {
      "id": "missing_carveout_independent_development",
      "severity": "YELLOW",
      "description": "Missing independent development carveout",
      "recommendation": "Add standard independent development exception"
    }
  ],
  "carveouts": {
    "public_knowledge": true,
    "prior_possession": true,
    "independent_development": false,
    "third_party_receipt": true,
    "legal_compulsion": true
  },
  "summary": "1 missing carveout; no critical issues. Route to counsel for review."
}
```

---

### nda_checklist.py

**Purpose:** Generates a 10-point compliance checklist for an NDA, evaluating each screening criterion as PASS/FAIL with notes.

**Usage:**

```bash
python scripts/nda_checklist.py <nda_file> [--json] [--output FILE]
```

**Flags:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `nda_file` | *(positional)* | | Path to NDA text file (.txt or .md) |
| `--json` | | off | Output in JSON format |
| `--output` | `-o` | *(stdout)* | Write output to file |

**Example Output:**

```
NDA COMPLIANCE CHECKLIST
========================
File: vendor_nda.txt
Overall: YELLOW (8/10 PASS)

 #  Criterion                    Status  Notes
 1  Agreement Structure          PASS    Mutual NDA; both parties identified
 2  Definition of Confidential   PASS    Reasonably scoped with marking requirement
 3  Obligations                  PASS    Standard of care; use restrictions present
 4  Standard Carveouts           FAIL    Missing: independent development
 5  Permitted Disclosures        PASS    Representatives and advisors covered
 6  Term & Duration              PASS    3-year term with 2-year survival
 7  Return/Destruction           PASS    Return or destroy within 30 days
 8  Remedies                     PASS    Injunctive relief; no liquidated damages
 9  Problematic Provisions       FAIL    Residuals clause detected
10  Governing Law                PASS    Delaware law; state courts
```
