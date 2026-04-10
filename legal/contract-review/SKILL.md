---
name: contract-review
description: >
  Contract review assistant analyzing agreements against playbooks.
  GREEN/YELLOW/RED severity. Use when reviewing vendor contracts,
  SaaS agreements, service agreements, or generating redline suggestions.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: contract-analysis
  updated: 2026-04-10
  tags: [contract-review, redline, negotiation, risk-assessment, legal]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Contract Review

Automated contract review tools that analyze agreements against organizational playbooks, classify clause risk with GREEN/YELLOW/RED severity, and generate prioritized redline suggestions with fallback positions.

---

## Table of Contents

- [Tools](#tools)
  - [Contract Analyzer](#contract-analyzer)
  - [Redline Generator](#redline-generator)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
  - [Standard Contract Review](#standard-contract-review)
  - [Rapid Risk Triage](#rapid-risk-triage)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Tools

### Contract Analyzer

Analyzes contract text files for clause types, missing standard clauses, and risk indicators.

```bash
# Analyze a contract file
python scripts/contract_analyzer.py contract.txt

# JSON output for pipeline integration
python scripts/contract_analyzer.py agreement.md --json

# Save analysis to file
python scripts/contract_analyzer.py contract.txt --output analysis.json --json
```

**What it detects:**
- Clause types: Limitation of Liability, Indemnification, IP, Data Protection, Term & Termination, Governing Law, Reps & Warranties, Force Majeure, Confidentiality, Payment Terms
- Missing standard clauses against a baseline checklist
- Risk indicators: uncapped liability, perpetual terms, unilateral indemnification, automatic renewal without opt-out, broad IP assignment, unlimited audit rights

**Risk Classification:**

| Level | Meaning | Action |
|-------|---------|--------|
| RED | Deal-breaker risk | Must negotiate before signing |
| YELLOW | Material concern | Should negotiate, may accept with mitigation |
| GREEN | Standard or favorable | Acceptable as-is |

---

### Redline Generator

Takes contract analysis JSON and generates formatted redline suggestions with priority tiers.

```bash
# Generate redlines from analysis
python scripts/contract_analyzer.py contract.txt --json --output analysis.json
python scripts/redline_generator.py analysis.json

# JSON output
python scripts/redline_generator.py analysis.json --json

# Save redlines to file
python scripts/redline_generator.py analysis.json --output redlines.md
```

**Output includes:**
- Priority tier (Must-Have / Should-Have / Nice-to-Have)
- Preferred redline language
- Rationale for each change
- Fallback position if counterparty rejects
- Negotiation notes

**Priority Tiers:**

| Tier | Label | Description |
|------|-------|-------------|
| 1 | Must-Have | Deal-breakers; walk away if rejected |
| 2 | Should-Have | Strong preferences; push hard but negotiable |
| 3 | Nice-to-Have | Concession candidates; trade for Tier 1-2 wins |

---

## Reference Guides

### Clause Analysis Guide
`references/clause_analysis_guide.md`

Deep reference covering 8+ clause types:
- Limitation of Liability (cap types, carveouts, consequential damages)
- Indemnification (mutuality, scope, procedure)
- IP (ownership, licenses, work-for-hire, feedback)
- Data Protection (DPA, sub-processors, breach notification, transfers)
- Term & Termination (auto-renewal, cure periods, transition)
- Governing Law (jurisdiction, arbitration, jury waiver)
- Representations & Warranties
- Force Majeure

### Negotiation Playbook
`references/negotiation_playbook.md`

Negotiation priority framework with:
- Tier 1 deal-breakers and walkaway criteria
- Tier 2 strong preferences with trading strategies
- Tier 3 concession candidates for strategic give-backs
- Redline format template
- Common negotiation pitfalls

---

## Workflows

### Standard Contract Review

1. **Ingest** -- Save contract as `.txt` or `.md` file
2. **Analyze** -- Run `contract_analyzer.py` with `--json` flag
3. **Review findings** -- Check RED items first, then YELLOW
4. **Generate redlines** -- Run `redline_generator.py` on analysis output
5. **Prioritize** -- Focus on Must-Have redlines, prepare fallbacks for Should-Have
6. **Send to counsel** -- Attach analysis and redlines for final review

### Rapid Risk Triage

1. Run `contract_analyzer.py` in text mode for quick scan
2. If any RED findings: escalate immediately to legal counsel
3. If YELLOW only: schedule review within 48 hours
4. If all GREEN: proceed with standard approval workflow

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `Error: File not found` | Contract file path is incorrect or file does not exist | Verify the file path; use absolute paths if relative paths fail |
| No clauses detected | Contract uses unusual formatting or non-standard clause headers | Ensure contract is plain text; strip PDF artifacts before analysis |
| All clauses marked GREEN | Contract is genuinely favorable, or text extraction missed key sections | Manually verify critical clauses (liability, indemnification, IP) are present in the input file |
| Redline generator produces empty output | Analysis JSON has no YELLOW or RED findings | Confirm analysis JSON is valid; re-run analyzer if contract was updated |
| False positive on uncapped liability | Liability section references a cap elsewhere in the document | Review the full Limitation of Liability section; the tool scans for cap keywords within each clause boundary |
| Missing clause false positive | Clause exists but uses non-standard heading (e.g., "Damages Cap" instead of "Limitation of Liability") | The analyzer checks multiple heading variants; add custom aliases if your organization uses unique terminology |

---

## Success Criteria

- **Contract review time reduced by 50%:** Automated clause identification and risk classification eliminates manual scanning.
- **Zero missed RED-severity clauses:** Every uncapped liability, unilateral indemnification, and broad IP assignment is flagged before human review.
- **Redline generation under 2 minutes:** From analysis JSON to prioritized redline document.
- **Consistent risk classification across reviewers:** GREEN/YELLOW/RED framework eliminates subjective assessments.
- **100% of contracts reviewed with structured output:** Every agreement gets a clause inventory and risk report before negotiation begins.
- **Negotiation success rate above 80% on Must-Have items:** Tier 1 redlines with prepared fallbacks improve negotiation outcomes.

---

## Scope & Limitations

**Covers:**
- Static text analysis of contract clauses using keyword and pattern matching
- Clause type identification across 10+ standard commercial contract categories
- Risk indicator detection: uncapped liability, perpetual terms, unilateral obligations, auto-renewal traps
- Missing clause detection against a standard commercial contract baseline
- Prioritized redline generation with fallback positions

**Does NOT cover:**
- **Legal advice** -- this tool supports review, it does not replace qualified legal counsel
- **Jurisdiction-specific compliance** -- use `ra-qm-team` skills for regulatory compliance (GDPR, SOC 2, etc.)
- **Contract execution or e-signature workflows** -- out of scope
- **Multi-document cross-reference** (e.g., checking SOW against MSA) -- analyze each document separately
- **Non-English contracts** -- pattern matching is English-language only

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| Signing contracts with only GREEN findings and no human review | Automated analysis cannot catch context-dependent risks, ambiguous language, or business-specific concerns | Always have qualified counsel review before execution, even on all-GREEN contracts |
| Treating all RED findings as equal | Some RED items are structural deal-breakers while others may be resolvable with a single word change | Use the redline generator to assess effort and fallback positions for each RED finding |
| Skipping the redline fallback positions | Entering negotiation with only preferred positions leaves no room for strategic concession | Always prepare Must-Have fallbacks and identify Nice-to-Have items to trade away |
| Running analysis on poorly extracted text | PDF-to-text conversion artifacts break clause detection patterns | Clean the text file before analysis: remove headers, footers, page numbers, and formatting artifacts |

---

## Tool Reference

### contract_analyzer.py

**Purpose:** Analyzes contract text files for clause types, identifies missing standard clauses, and flags risk indicators with GREEN/YELLOW/RED severity classification.

**Usage:**

```bash
python scripts/contract_analyzer.py <contract_file> [--json] [--output FILE]
```

**Flags:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `contract_file` | *(positional)* | | Path to contract text file (.txt or .md) |
| `--json` | | off | Output in JSON format |
| `--output` | `-o` | *(stdout)* | Write output to file |

**Example Output (JSON):**

```json
{
  "file": "vendor_agreement.txt",
  "clauses_found": [
    {
      "type": "limitation_of_liability",
      "severity": "RED",
      "text_snippet": "...liability shall not be limited...",
      "risk_flags": ["uncapped_liability"],
      "notes": "No liability cap found; uncapped exposure"
    }
  ],
  "missing_clauses": ["force_majeure", "data_protection"],
  "risk_summary": {"RED": 2, "YELLOW": 3, "GREEN": 5},
  "overall_risk": "RED"
}
```

---

### redline_generator.py

**Purpose:** Takes contract analysis JSON and generates formatted redline suggestions with priority tiers, rationale, and fallback positions.

**Usage:**

```bash
python scripts/redline_generator.py <analysis_json> [--json] [--output FILE]
```

**Flags:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `analysis_json` | *(positional)* | | Path to contract analysis JSON file |
| `--json` | | off | Output in JSON format |
| `--output` | `-o` | *(stdout)* | Write output to file |

**Example Output:**

```
REDLINE SUGGESTIONS
===================

[MUST-HAVE] Limitation of Liability — Uncapped Liability
  Severity: RED
  Preferred: "Aggregate liability shall not exceed 12 months of fees paid."
  Rationale: Uncapped liability creates unlimited financial exposure.
  Fallback: "Aggregate liability shall not exceed 24 months of fees paid."

[SHOULD-HAVE] Indemnification — Unilateral Indemnification
  Severity: YELLOW
  Preferred: "Each party shall indemnify the other for breaches of this Agreement."
  Rationale: Mutual indemnification balances risk between parties.
  Fallback: "Indemnification obligations shall be subject to the liability cap."
```
