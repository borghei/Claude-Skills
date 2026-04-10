---
name: statute-analysis
description: >
  Statute and regulation interpretation framework. Use when reading statutes,
  classifying requirements, analyzing operative keywords, applying canons of
  construction, or mapping compliance obligations from legislative text.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: statutory-interpretation
  updated: 2026-04-10
  tags: [statute, regulation, compliance, interpretation, legal-analysis]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Statute Analysis

Production-ready framework for reading, interpreting, and applying statutes, regulations, and rules. Covers the full lifecycle from identifying the legal hierarchy through extracting actionable requirements and mapping implementation obligations.

---

## Table of Contents

- [Legal Hierarchy](#legal-hierarchy)
- [Preliminary Steps](#preliminary-steps)
- [Tools](#tools)
- [Core Interpretation Techniques](#core-interpretation-techniques)
- [Canons of Construction](#canons-of-construction)
- [Interpretation Sources](#interpretation-sources)
- [Requirement Classification](#requirement-classification)
- [Cross-Jurisdictional Analysis](#cross-jurisdictional-analysis)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope and Limitations](#scope-and-limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Legal Hierarchy

Understanding the source hierarchy is the foundation of statutory analysis.

| Source | Created By | Authority | Example |
|--------|-----------|-----------|---------|
| Constitution | Sovereign/people | Supreme | U.S. Constitution, EU Treaties |
| Statute | Legislature | Primary legislation | GDPR, Clean Air Act, AI Act |
| Regulation | Executive agency | Delegated authority | FDA 21 CFR, FTC rules |
| Rule | Agency or court | Procedural/interpretive | Federal Rules of Civil Procedure |
| Guidance | Agency | Non-binding, persuasive | FDA guidance documents, CNIL guides |
| Case law | Courts | Binding within jurisdiction | Supreme Court precedent |

**Key principle:** Higher sources override lower sources. Regulations cannot exceed statutory authority. Guidance cannot create new obligations not grounded in statute.

---

## Preliminary Steps

Before interpreting any statutory provision, complete these checks:

1. **Verify currency and status** -- Is this the current, in-force version? Check for amendments, repeals, or sunset clauses. Use official sources (government gazettes, EUR-Lex, congress.gov).
2. **Understand the regulatory ecosystem** -- What regulations, rules, and guidance implement this statute? Map the full hierarchy.
3. **Browse the full structure** -- Read the table of contents, definitions section, scope provisions, and transitional articles before diving into specific sections.
4. **Identify the definitions section** -- Almost all statutes define key terms. These definitions override ordinary meaning.
5. **Check effective dates** -- Different provisions may have different effective dates. Map the compliance timeline.
6. **Identify your role** -- Statutes impose different obligations depending on the reader's role (e.g., "provider" vs "deployer" in the EU AI Act, "controller" vs "processor" in GDPR).

---

## Tools

### Statute Keyword Analyzer

Scans statute text for operative keywords and classifies obligations, permissions, conditions, and exemptions.

```bash
# Analyze a statute file
python scripts/statute_keyword_analyzer.py --input statute.txt

# Analyze with JSON output
python scripts/statute_keyword_analyzer.py --input regulation.txt --json

# Analyze inline text
python scripts/statute_keyword_analyzer.py --text "The controller shall implement appropriate technical measures..."

# Save analysis report
python scripts/statute_keyword_analyzer.py --input statute.txt --output analysis.json
```

### Requirement Classifier

Classifies statutory requirements by type, implementation team, enforcement mechanism, and penalty.

```bash
# Classify requirements from a JSON list
python scripts/requirement_classifier.py --input requirements.json

# Classify with JSON output
python scripts/requirement_classifier.py --input requirements.json --json

# Classify inline requirement
python scripts/requirement_classifier.py --text "Controllers must provide data subjects with a privacy notice at the point of collection"

# Generate implementation matrix
python scripts/requirement_classifier.py --input requirements.json --output matrix.json
```

---

## Core Interpretation Techniques

### Definitions Analysis

Statutory definitions control meaning. Pay attention to the verb used:

| Verb | Type | Meaning | Example |
|------|------|---------|---------|
| "means" | Exhaustive | The definition is complete; no other meaning applies | "'Personal data' means any information relating to an identified or identifiable natural person" |
| "includes" | Illustrative | The definition provides examples but is not limited to them | "'Processing' includes collection, recording, organization, structuring..." |
| "does not include" | Exclusion | Explicitly carves out items from scope | "'Consumer' does not include a natural person acting in a commercial or employment context" |
| "refers to" | Pointer | Incorporates an external definition | "'Harmonised standard' refers to a European standard as defined in Regulation (EU) No 1025/2012" |

### Operative Keywords

| Keyword | Classification | Legal Effect |
|---------|---------------|-------------|
| **shall** | Mandatory | Creates an obligation; must be done |
| **must** | Mandatory | Same as "shall" in modern drafting |
| **may** | Permissive | Creates permission; optional |
| **may not** | Prohibitive | Creates a prohibition |
| **and** | Conjunctive | All listed items required |
| **or** | Disjunctive | Any listed item sufficient |
| **unless** | Exception | Negates the rule when condition is met |
| **except** | Exception | Carves out specific items from the rule |
| **subject to** | Conditional | Rule applies but another provision modifies it |
| **notwithstanding** | Override | This provision prevails over conflicting provisions |
| **provided that** | Condition | Adds a requirement that must be satisfied |
| **if...then** | Conditional | Trigger condition and consequence |
| **upon** | Temporal trigger | Action required when event occurs |

### Conjunctive vs Disjunctive Analysis

This distinction determines whether ALL conditions must be met or ANY single condition suffices.

| Pattern | Reading | Practical Impact |
|---------|---------|-----------------|
| "A, B, and C" | All three required | Must satisfy every element |
| "A, B, or C" | Any one sufficient | Satisfy any single element |
| "A, B, and/or C" | Ambiguous | Flag for clarification; analyze context |
| "both A and B" | Explicitly conjunctive | Must satisfy both |
| "either A or B" | Explicitly disjunctive | Satisfy one |
| Serial comma ambiguity | Context-dependent | Apply whole-act rule for consistency |

---

## Canons of Construction

See `references/canons_of_construction.md` for the complete 12-canon reference.

### Quick Reference

| Canon | Core Rule | When to Apply |
|-------|----------|---------------|
| General-Terms Canon | General terms get general meaning | Default interpretation |
| Expressio Unius | Expressing one thing excludes others | Specific lists without catchall |
| Whole-Act Rule | Interpret provisions consistently | Apparent conflicts between sections |
| Consistent Usage | Same term = same meaning throughout | Term appears multiple times |
| Meaningful Variation | Different terms = different meanings | Similar but distinct terms used |
| Surplusage Canon | Every word has meaning; no redundancy | Tempted to treat words as surplus |
| Noscitur a Sociis | Words known by their associates | Ambiguous term in a list |
| Ejusdem Generis | General follows specific = limited | "...and other similar" patterns |
| Against Ineffectiveness | Prefer reading that gives effect | Two possible readings |
| Avoiding Absurdity | Reject absurd outcomes | Literal reading produces nonsensical result |
| Remedial Statutes | Construe liberally | Consumer protection, safety statutes |
| Rule of Lenity | Ambiguity favors the regulated party | Criminal or penalty provisions |

---

## Interpretation Sources

When statutory text is ambiguous, consult sources in this order:

| Priority | Source | Weight | Where to Find |
|----------|--------|--------|---------------|
| 1 | Statutory text itself | Controlling | Official gazette, codified law |
| 2 | Definitions section | Controlling | Usually first articles/sections |
| 3 | Legislative purpose (recitals, preamble) | Strong | Preamble, "Whereas" clauses |
| 4 | Canons of construction | Strong | Legal treatises, case law |
| 5 | Case law interpreting the provision | Strong-to-moderate | Court databases |
| 6 | Agency regulations implementing statute | Moderate | Agency websites, CFR |
| 7 | Agency guidance and FAQs | Persuasive only | Agency websites |
| 8 | Legislative history | Weak (varies by jurisdiction) | Congressional record, Hansard |
| 9 | Academic commentary | Persuasive only | Legal journals |

---

## Requirement Classification

Every statutory requirement maps to an implementation category:

| Type | Description | Typical Owner | Example |
|------|-------------|---------------|---------|
| Disclosure | Information must be provided to someone | Legal / Compliance | Privacy notice requirements |
| Operational | Process or procedure must exist | Operations / Compliance | Record-keeping obligations |
| Technical | System capability or safeguard required | Engineering | Encryption, access controls |
| UI/Design | User interface must include specific elements | Product / Design | Consent mechanisms, opt-out buttons |
| Organizational | Governance structure or role required | Management / HR | Appointing a DPO, board oversight |
| Documentation | Written records must be maintained | Legal / Compliance | Impact assessments, audit trails |
| Reporting | Information must be submitted to authority | Legal / Compliance | Breach notification, annual reports |

---

## Cross-Jurisdictional Analysis

When requirements from multiple jurisdictions apply:

1. **Map applicable jurisdictions** -- Where are your users, your entity, and your data?
2. **Identify overlapping requirements** -- Many frameworks share common obligations.
3. **Find the highest common denominator** -- Design for the strictest requirement that satisfies all jurisdictions.
4. **Flag conflicts** -- Where requirements genuinely conflict, document the conflict and seek legal advice.
5. **Check preemption** -- Federal law may preempt state law; EU regulations may preempt member state law.

---

## Enforcement Analysis

For each statutory requirement, assess enforcement risk:

| Factor | Assessment Questions |
|--------|---------------------|
| Enforcement authority | Which agency enforces? How active are they? |
| Penalty types | Civil fines, criminal penalties, administrative sanctions? |
| Penalty severity | Fixed amounts, percentage of turnover, per-violation? |
| Cure periods | Is there a right to cure before penalties apply? |
| Private right of action | Can individuals sue for violations? |
| Enforcement history | Has this provision been actively enforced? |
| Regulatory guidance | Has the agency clarified enforcement priorities? |

---

## Reference Guides

| Guide | Path | Description |
|-------|------|-------------|
| Canons of Construction | `references/canons_of_construction.md` | 12 canons with definitions, examples, and misapplication warnings |
| Statutory Structure | `references/statutory_structure.md` | How statutes are organized, effective dates, preemption, enforcement |

---

## Workflows

### Workflow 1: First Reading of a New Statute

1. Browse the full table of contents and structure.
2. Read the definitions section and scope provisions.
3. Check effective dates and transitional provisions.
4. Identify your role under the statute.
5. Run `scripts/statute_keyword_analyzer.py` on the full text.
6. Review the obligation/permission/exception map.
7. Identify provisions that apply to your role.
8. **Validation:** Definitions cataloged, role identified, key obligations listed.

### Workflow 2: Requirement Extraction and Classification

1. Extract all provisions containing "shall," "must," or mandatory language.
2. For each requirement, identify: who (subject), what (action), when (trigger/deadline), how (standard).
3. Run `scripts/requirement_classifier.py` on the extracted requirements.
4. Review the implementation matrix.
5. Assign each requirement to an implementation team.
6. Prioritize by enforcement risk and deadline.
7. **Validation:** Every mandatory provision classified, assigned, and prioritized.

### Workflow 3: Cross-Reference Resolution

1. Identify all cross-references in the target provision ("subject to Article X," "as defined in Section Y").
2. Read each referenced provision in full.
3. Determine whether the cross-reference modifies, limits, or supplements the target provision.
4. Check for circular references or chains (A references B which references C).
5. Document the complete picture -- the target provision as modified by all cross-references.
6. **Validation:** All cross-references resolved; no orphan references.

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Term not defined in statute | Legislature used ordinary meaning | Apply general-terms canon; check case law for judicial definitions |
| "And/or" ambiguity | Drafting imprecision | Check legislative history; apply whole-act rule; flag for legal review |
| Conflicting provisions | Later provision may override earlier | Check for "notwithstanding" clauses; apply later-in-time rule |
| Undefined threshold | Delegated to regulation | Check implementing regulations and agency guidance |
| Provision seems to have no effect | May be transitional or placeholder | Check effective dates and amendment history |
| Cross-reference to repealed section | Statute not updated after amendment | Check saving clauses; apply presumption against ineffectiveness |

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| All defined terms cataloged | 100% of definitions section mapped |
| Obligations extracted | Every "shall/must" provision identified |
| Requirements classified | Each requirement has type, owner, enforcement, and priority |
| Cross-references resolved | No unresolved references remain |
| Enforcement risk assessed | Every material obligation has enforcement analysis |
| Implementation matrix complete | Requirements mapped to teams with timelines |

---

## Scope & Limitations

**In scope:** Reading and interpreting statutory text, extracting requirements, classifying obligations, applying canons of construction, mapping enforcement risk.

**Out of scope:** Providing legal advice, predicting court outcomes, drafting legislation, interpreting case law holdings, constitutional analysis.

**Disclaimer:** This skill provides a structured methodology for statutory analysis. It does not constitute legal advice. Always consult qualified legal counsel for binding interpretations.

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| Reading a section in isolation | Statutes are interconnected; isolated reading misses cross-references, definitions, and scope limitations | Always read definitions, scope, and cross-referenced provisions before interpreting |
| Treating guidance as law | Agency guidance is non-binding and can change; building compliance solely on guidance creates risk | Use guidance to inform interpretation but anchor compliance to statutory text |
| Ignoring "what the statute doesn't say" | Silence can mean permission, delegation, or an oversight; assuming the statute covers everything leads to compliance gaps | Affirmatively check: does the statute address this scenario? If not, analyze why and what fills the gap |
| Applying one jurisdiction's interpretation to another | "Personal data" in GDPR is not identical to "personal information" in CCPA; cross-pollinating definitions creates errors | Analyze each statute independently using its own definitions and interpretive framework |
| Skipping the definitions section | Statutory definitions override ordinary meaning; missing them leads to fundamental misreadings | Always read the definitions section first, before any substantive analysis |

---

## Tool Reference

| Tool | Input | Output | Use Case |
|------|-------|--------|----------|
| `statute_keyword_analyzer.py` | Statute text file or inline text | Obligation/permission/exception map | First pass analysis of any legislative text |
| `requirement_classifier.py` | List of requirements (text or JSON) | Implementation matrix with types, teams, enforcement | Converting statutory obligations to actionable implementation tasks |
