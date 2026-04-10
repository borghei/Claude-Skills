---
name: tabular-document-review
description: >
  Extract structured data from multiple documents into comparison matrix with citations. Use for bulk document review.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: document-review
  updated: 2026-04-10
  tags: [document-review, extraction, comparison-matrix, contracts, bulk-review]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Tabular Document Review Skill

## Overview

Production-ready toolkit for extracting structured data from multiple legal documents into a comparison matrix with citations. Supports user-defined extraction columns, parallel processing with up to 10 agents, confidence scoring, and output in markdown table or structured JSON. Designed for legal teams performing bulk contract review, NDA comparison, employment agreement analysis, and lease review.

## Table of Contents

- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Extraction Scenarios](#extraction-scenarios)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

## Tools

### 1. Document Discovery (`scripts/document_discovery.py`)

Scan a directory for legal documents and generate an inventory manifest.

```bash
python scripts/document_discovery.py /path/to/contracts

python scripts/document_discovery.py /path/to/ndas --types pdf,docx --json

python scripts/document_discovery.py /path/to/leases --types pdf,docx,txt,md --min-size 1024
```

### 2. Extraction Aggregator (`scripts/extraction_aggregator.py`)

Aggregate multiple extraction result JSONs into a unified comparison matrix.

```bash
python scripts/extraction_aggregator.py \
  --results extraction_1.json extraction_2.json extraction_3.json

python scripts/extraction_aggregator.py \
  --results-dir ./extraction_results/ --json

python scripts/extraction_aggregator.py \
  --results-dir ./extraction_results/ \
  --format markdown \
  --output review_matrix.md

python scripts/extraction_aggregator.py \
  --results extraction_1.json extraction_2.json \
  --columns "Parties,Effective Date,Term,Governing Law"
```

## Reference Guides

| Reference | Purpose |
|-----------|---------|
| `references/extraction_methodology.md` | Document extraction best practices, JSON schema, agent prompts |
| `references/common_extraction_columns.md` | Pre-defined column sets for contracts, NDAs, employment, leases |

## Workflows

### 5-Step Document Review Pipeline

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 1. Gather Requirements | Define document folder, output filename, columns to extract | Manual | Column list, file path |
| 2. Discover Documents | Scan directory for target documents | `document_discovery.py` | Document manifest JSON |
| 3. Process Documents | Extract values per column with citations (parallel agents) | AI agents (external) | Per-document extraction JSONs |
| 4. Collect Results | Aggregate extraction JSONs into unified matrix | `extraction_aggregator.py` | Consolidated matrix |
| 5. Generate Output | Export as markdown table or structured JSON | `extraction_aggregator.py` | Final deliverable |

### Parallel Processing Strategy

| Agents | Documents per Agent | Use When |
|--------|-------------------|----------|
| 1 | All | 1-5 documents |
| 2-3 | ceil(N/agents) | 6-15 documents |
| 4-6 | ceil(N/agents) | 16-40 documents |
| 7-10 | ceil(N/agents) | 41-100 documents |
| 10 (max) | ceil(N/10) | 100+ documents |

### Agent Prompt Template

Each agent receives a prompt structured as:

```
You are reviewing {count} legal documents. For each document, extract the
following columns:

{column_definitions}

For each value extracted:
1. Provide the exact value found
2. Include the page number (PDF) or section/paragraph (DOCX/MD)
3. Rate your confidence: HIGH (exact match), MEDIUM (inferred), LOW (uncertain)
4. If not found, record "NOT FOUND" with confidence LOW

Output as JSON per the extraction schema.
```

### Confidence Scoring

| Level | Color Code | Definition |
|-------|-----------|------------|
| HIGH | Green | Exact value found with clear citation |
| MEDIUM | Yellow | Value inferred from context; multiple possible interpretations |
| LOW | Red / Not Found | Value uncertain or not found in document |

### Output Format

**Sheet 1: Document Review**

| Document | Parties | Effective Date | Term | Governing Law | ... |
|----------|---------|---------------|------|---------------|-----|
| contract_a.pdf | Acme / Beta [p.1] | 2026-01-15 [p.2] | 3 years [p.3] | Delaware [p.12] | ... |
| contract_b.pdf | Gamma / Delta [p.1] | NOT FOUND | 2 years [p.4] | New York [p.10] | ... |

**Sheet 2: Summary**

| Metric | Value |
|--------|-------|
| Documents processed | 25 |
| Columns extracted | 8 |
| Average confidence | 87% |
| Not found rate | 12% |

## Extraction Scenarios

### Contract Review

| Column | What to Extract |
|--------|----------------|
| Parties | All contracting parties with full legal names |
| Effective Date | Contract effective or execution date |
| Term | Duration of the agreement |
| Renewal | Auto-renewal terms and notice period |
| Governing Law | Jurisdiction governing the agreement |
| Liability Cap | Maximum liability amount or formula |
| Indemnification | Indemnification obligations and scope |
| IP Ownership | Intellectual property ownership provisions |
| Termination Rights | Termination triggers and notice requirements |
| Data Protection | Data protection or privacy obligations |

### NDA Review

| Column | What to Extract |
|--------|----------------|
| Parties | Disclosing and receiving parties |
| Type | Mutual or one-way |
| Definition Scope | How "confidential information" is defined |
| Exceptions | Standard exceptions to confidentiality |
| Term | Duration of confidentiality obligations |
| Survival | Survival period after termination |
| Return/Destruction | Obligations on termination |
| Remedies | Available remedies for breach |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Discovery finds 0 documents | Wrong path or file types | Verify path exists; check `--types` matches actual file extensions |
| Extraction JSONs have wrong schema | Agent prompt incomplete | Use the extraction schema from `extraction_methodology.md` |
| Aggregator shows conflicts | Multiple values for same cell | Review source documents; aggregator marks conflicts for manual review |
| High "NOT FOUND" rate | Columns too specific for document type | Use column definitions from `common_extraction_columns.md`; broaden definitions |
| Confidence all LOW | Agent unable to locate values | Check column definitions are specific enough; verify document is readable |
| Aggregator crashes on large set | Too many result files loaded at once | Process in batches of 50 results; use `--columns` to limit output width |
| Markdown table misaligned | Long values or special characters | Use `--format json` for machine processing; truncate long values |
| Missing citations | Agent did not include page/section references | Reinforce citation requirement in agent prompt; check extraction schema |

## Success Criteria

- **Extraction Coverage**: 90%+ of defined columns populated across all documents
- **Confidence Distribution**: 70%+ of extractions rated HIGH confidence
- **Citation Accuracy**: Every extracted value includes verifiable page/section citation
- **Processing Speed**: 50+ documents processed within 30 minutes using parallel agents
- **Matrix Completeness**: Final matrix includes all documents and all columns with no orphan rows

## Scope & Limitations

**This skill covers:**
- Document inventory and discovery across PDF, DOCX, TXT, and MD formats
- Aggregation of extraction results from parallel agent processing into unified matrix
- Pre-defined column sets for contracts, NDAs, employment agreements, and leases
- Confidence scoring and conflict detection for extracted values
- Markdown and JSON output formats

**This skill does NOT cover:**
- Actual document parsing or text extraction (requires external libraries or AI agents)
- OCR processing for scanned documents
- Excel/XLSX output generation (use JSON output and convert externally)
- Automated legal analysis or risk assessment of extracted values
- Document comparison or redlining between versions

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|--------------|-------------|-----------------|
| Vague column definitions | "Date" could match dozens of dates in a contract | Use specific definitions: "Effective Date" with guidance on where to look |
| Skipping document discovery | Unknown document count leads to wrong agent allocation | Always run discovery first; use manifest for pipeline planning |
| Ignoring LOW confidence results | Missing or uncertain data treated as fact | Review all LOW confidence cells manually; flag in final report |
| Processing 100+ docs with 1 agent | Slow, context window overflow, quality degradation | Use parallel processing: ceil(N/10) documents per agent, max 10 agents |
| No citation requirement | Cannot verify extracted values against source | Require page/section citation for every extraction; reject uncited values |

## Tool Reference

### `scripts/document_discovery.py`

Scan directory for legal documents and generate inventory manifest.

```
usage: document_discovery.py [-h] [--json]
                              [--types TYPES]
                              [--min-size MIN_SIZE]
                              [--max-size MAX_SIZE]
                              directory

positional arguments:
  directory             Path to directory containing documents

options:
  -h, --help            Show help message and exit
  --json                Output in JSON format
  --types TYPES         Comma-separated file extensions to include
                        (default: pdf,docx,doc,txt,md,rtf)
  --min-size MIN_SIZE   Minimum file size in bytes (default: 0)
  --max-size MAX_SIZE   Maximum file size in bytes (default: no limit)
```

### `scripts/extraction_aggregator.py`

Aggregate extraction results into unified comparison matrix.

```
usage: extraction_aggregator.py [-h] [--json]
                                 [--results RESULTS [RESULTS ...]]
                                 [--results-dir RESULTS_DIR]
                                 [--format {markdown,json}]
                                 [--columns COLUMNS]
                                 [--output OUTPUT]

options:
  -h, --help            Show help message and exit
  --json                Output in JSON format (alias for --format json)
  --results             One or more extraction result JSON files
  --results-dir         Directory containing extraction result JSON files
  --format              Output format: markdown table or JSON (default: markdown)
  --columns             Comma-separated column names to include (default: all)
  --output              Write output to file instead of stdout
```
