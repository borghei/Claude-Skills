# Document Extraction Methodology

Best practices for extracting structured data from legal documents into comparison matrices.

## Table of Contents

- [Column Definition Guidelines](#column-definition-guidelines)
- [Extraction Schema](#extraction-schema)
- [Citation Standards](#citation-standards)
- [Confidence Scoring](#confidence-scoring)
- [Agent Processing Strategy](#agent-processing-strategy)
- [Conflict Resolution](#conflict-resolution)
- [Error Handling](#error-handling)
- [Output Formats](#output-formats)

## Column Definition Guidelines

### Principles

| Principle | Bad Example | Good Example | Why |
|-----------|-------------|-------------|-----|
| Be specific | "Date" | "Effective Date" | A contract may contain dozens of dates |
| Use domain terms | "Money limit" | "Liability Cap" | Domain-specific terms reduce ambiguity |
| Define scope | "Parties" | "Contracting Parties (full legal names)" | Clarifies what exactly to extract |
| One value per column | "Dates and Terms" | Separate "Effective Date" and "Term" columns | Enables clean tabular output |
| Include guidance | "Governing Law" | "Governing Law (jurisdiction and choice of law clause)" | Tells agent where to look |

### Column Definition Format

Each column should be defined with:

```
Column Name: [Specific name]
Description: [What to extract]
Where to look: [Typical location in document]
Format: [Expected format of the value]
Example: [Example of a correct extraction]
```

### Example Column Definitions

```
Column: Effective Date
Description: The date on which the agreement becomes effective
Where to look: First page, preamble, or "Effective Date" definition section
Format: YYYY-MM-DD
Example: 2026-01-15

Column: Governing Law
Description: The jurisdiction whose laws govern the agreement
Where to look: Governing law or choice of law clause, typically near end of agreement
Format: State/Country name
Example: State of Delaware

Column: Liability Cap
Description: Maximum aggregate liability amount or formula
Where to look: Limitation of liability clause
Format: Dollar amount or formula description
Example: $5,000,000 or "12 months of fees paid"
```

## Extraction Schema

### Per-Document Extraction JSON

```json
{
  "filename": "contract_a.pdf",
  "extractions": {
    "Parties": {
      "value": "Acme Corporation and Beta Industries LLC",
      "citation": "p.1, Preamble",
      "confidence": "HIGH"
    },
    "Effective Date": {
      "value": "2026-01-15",
      "citation": "p.1, Section 1.1",
      "confidence": "HIGH"
    },
    "Liability Cap": {
      "value": "NOT FOUND",
      "citation": "",
      "confidence": "NOT_FOUND"
    }
  }
}
```

### Multi-Document Agent Result JSON

```json
{
  "agent_id": "agent_1",
  "processed_date": "2026-04-10T14:30:00",
  "document_count": 5,
  "documents": [
    {
      "filename": "contract_a.pdf",
      "extractions": {
        "Column Name": {
          "value": "extracted value or NOT FOUND",
          "citation": "p.3, Section 2.1",
          "confidence": "HIGH"
        }
      }
    }
  ]
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| filename | string | Yes | Original filename of the document |
| extractions | object | Yes | Map of column name to extraction result |
| value | string | Yes | Extracted value or "NOT FOUND" |
| citation | string | Yes | Page number (PDF) or section/paragraph (DOCX) |
| confidence | string | Yes | HIGH, MEDIUM, LOW, or NOT_FOUND |

## Citation Standards

### By Document Type

| Document Type | Citation Format | Example |
|--------------|----------------|---------|
| PDF | Page number | "p.3" or "pp.3-4" |
| PDF (with sections) | Page + section | "p.3, Section 2.1" |
| DOCX | Section/paragraph | "Section 5.2, para 3" |
| DOCX (with headers) | Header path | "Article III > Section 3.2(a)" |
| TXT/MD | Line number or heading | "Line 45" or "Under 'Definitions'" |
| Multi-page clause | Start-end pages | "pp.7-9, Article IV" |

### Citation Requirements

| Requirement | Detail |
|-------------|--------|
| Every value needs citation | No extracted value should lack a source reference |
| Precision matters | "p.3" is better than "somewhere in the document" |
| Quote when ambiguous | If the value is inferred, include the source quote |
| NOT FOUND citation | Leave citation empty for NOT FOUND values |
| Multiple locations | If value appears in multiple places, cite the most authoritative |

### Citation Examples

| Scenario | Citation |
|----------|----------|
| Clear, single location | "p.5, Section 3.1" |
| Defined term | "p.2, 'Effective Date' definition" |
| Scattered information | "p.3 (parties), p.1 (preamble confirms)" |
| Inferred from context | "p.7, para 2 (inferred from termination clause language)" |
| Cross-reference | "p.4, Section 2.3 (cross-referencing Exhibit A)" |

## Confidence Scoring

### Confidence Levels

| Level | Score | Definition | When to Use |
|-------|-------|-----------|-------------|
| HIGH | 3 | Exact value found with clear, unambiguous citation | The document explicitly states the value in a clearly labeled section |
| MEDIUM | 2 | Value inferred from context or multiple possible interpretations exist | The value is implied but not explicitly stated; or the section is ambiguous |
| LOW | 1 | Value uncertain; weak evidence; may require human verification | Partial match; the value is mentioned in a different context; or conflicting information |
| NOT_FOUND | 0 | Value not found in the document | Thorough search reveals no matching information |

### Confidence Decision Tree

```
Is the value explicitly stated in a clearly labeled section?
├── YES → Is the citation unambiguous?
│   ├── YES → HIGH
│   └── NO → MEDIUM (multiple possible source locations)
└── NO → Is the value inferable from context?
    ├── YES → Is the inference strong?
    │   ├── YES → MEDIUM
    │   └── NO → LOW
    └── NO → NOT_FOUND
```

### Confidence Calibration Examples

| Extraction | Value | Confidence | Rationale |
|-----------|-------|-----------|-----------|
| Effective Date from "This Agreement is effective as of January 15, 2026" | 2026-01-15 | HIGH | Explicit, unambiguous |
| Term from "This Agreement shall continue for a period of three (3) years" | 3 years | HIGH | Explicit duration |
| Governing Law from "shall be governed by the laws of the State of Delaware" | Delaware | HIGH | Standard clause, clear |
| Liability Cap when only indemnification cap is stated | $5M (indemnification only) | MEDIUM | Related but not identical |
| Renewal from termination clause mentioning "auto-renewal unless 90 days notice" | Auto-renew, 90 days notice | MEDIUM | Embedded in termination clause |
| IP Ownership when document discusses license but not ownership | License granted, ownership unclear | LOW | Inference from license terms |
| Non-compete when not mentioned anywhere | NOT FOUND | NOT_FOUND | No relevant clause found |

## Agent Processing Strategy

### Document Distribution

```
Number of documents: N
Maximum agents: 10
Documents per agent: ceil(N / min(agents, 10))

Example:
  25 documents, 5 agents → 5 documents each
  100 documents, 10 agents → 10 documents each
  3 documents, 1 agent → 3 documents
```

### Allocation Table

| Documents | Agents | Per Agent | Estimated Time |
|-----------|--------|-----------|---------------|
| 1-5 | 1 | All | 2-5 min |
| 6-15 | 2-3 | 3-5 | 5-10 min |
| 16-40 | 4-6 | 4-7 | 10-15 min |
| 41-100 | 7-10 | 5-10 | 15-25 min |
| 100+ | 10 | 10+ | 25+ min |

### Agent Prompt Template

```
You are a legal document extraction agent. Your task is to extract specific
data points from {count} legal documents.

For each document, extract the following columns:

{for each column}
- **{column_name}**: {column_description}
  Look for this in: {where_to_look}
  Expected format: {format}
{end for}

For EACH extracted value, provide:
1. "value": The exact value found (or "NOT FOUND")
2. "citation": Page number/section reference (e.g., "p.3, Section 2.1")
3. "confidence": One of HIGH, MEDIUM, LOW, NOT_FOUND

Output your results as JSON matching this schema:
{schema}

Important rules:
- Extract values exactly as stated in the document
- Always include a citation for every non-NOT_FOUND value
- Do not infer values that are not present
- When uncertain between two values, choose the one from the more authoritative section
- If a value appears in multiple places, use the definition section
```

## Conflict Resolution

### When Conflicts Occur

Conflicts arise when multiple agents or extraction passes produce different values for the same document and column.

| Conflict Type | Resolution Strategy |
|--------------|-------------------|
| Different values, different confidence | Keep higher confidence value |
| Different values, same confidence | Mark as conflict; require manual review |
| Same value, different citations | Keep both citations for completeness |
| One found, one NOT_FOUND | Keep the found value if confidence >= MEDIUM |
| Both NOT_FOUND | Mark as NOT_FOUND |

### Conflict Resolution Process

1. **Detect**: Aggregator identifies cells where multiple values exist
2. **Compare**: Check confidence levels of competing values
3. **Auto-resolve**: If confidence clearly differs, keep higher
4. **Flag**: If cannot auto-resolve, mark as conflict
5. **Review**: Human reviews all flagged conflicts against source documents
6. **Resolve**: Update matrix with verified value

## Error Handling

### Common Errors

| Error | Cause | Handling |
|-------|-------|---------|
| Unreadable document | Corrupted file, password-protected, scanned image | Log error; mark all columns as NOT_FOUND with note |
| Agent timeout | Document too large or complex | Retry with single document; increase timeout |
| Column not found in any document | Column definition too specific or wrong document type | Review column definition; confirm applicability |
| Malformed extraction JSON | Agent output formatting error | Attempt JSON repair; if fails, re-process document |
| Partial results | Agent processed some but not all documents | Identify missing documents; reassign to new agent |
| Encoding errors | Non-UTF-8 characters in document | Attempt encoding detection; process with fallback encoding |

### Error Recovery Strategy

```
For each document in the pipeline:
  1. Attempt extraction
  2. If error → Log error type and document
  3. If recoverable error → Retry once with adjusted parameters
  4. If persistent error → Mark document as "ERROR" in matrix
  5. Continue with remaining documents
  6. Report all errors in summary statistics
```

## Output Formats

### Markdown Table

Best for: Human review, documentation, reports.

```markdown
| Document | Parties | Effective Date | Term |
|----------|---------|---------------|------|
| contract_a.pdf | Acme / Beta [p.1] | 2026-01-15 [p.2] | 3 years [p.3] |
```

### JSON

Best for: Programmatic consumption, further processing, database import.

```json
{
  "matrix": [
    {
      "document": "contract_a.pdf",
      "columns": {
        "Parties": {
          "value": "Acme Corporation and Beta Industries LLC",
          "citation": "p.1, Preamble",
          "confidence": "HIGH"
        }
      }
    }
  ]
}
```

### Color Coding (for Excel/Spreadsheet)

When converting to Excel (external tool):

| Confidence | Cell Color | Hex Code |
|-----------|-----------|----------|
| HIGH | Green | #C6EFCE |
| MEDIUM | Yellow | #FFEB9C |
| LOW | Red | #FFC7CE |
| NOT_FOUND | Gray | #D9D9D9 |
| Conflict | Orange | #FFA500 |

### Excel Output Structure

| Sheet | Contents |
|-------|----------|
| Document Review | Main matrix with values, citations in cell comments |
| Summary | Statistics: documents processed, coverage per column, confidence distribution |
| Conflicts | All detected conflicts requiring manual review |
| Metadata | Extraction parameters, agent assignments, processing timestamps |
