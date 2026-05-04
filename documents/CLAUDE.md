# Documents Domain

Production-grade document automation skills for the four Office formats Anthropic ships official skills for. Each toolkit reads OOXML or PDF directly using the Python standard library only.

## Skills in This Domain

| Skill | Folder | Tool | Use For |
|-------|--------|------|---------|
| Docx Toolkit | `docx-toolkit/` | `docx_auditor.py` | Word document audit (comments, tracked changes, headings, styles) |
| PDF Toolkit | `pdf-toolkit/` | `pdf_auditor.py` | PDF metadata, security, encryption, embedded JS / files |
| Pptx Toolkit | `pptx-toolkit/` | `pptx_auditor.py` | PowerPoint audit (slides, density, notes, animations, hidden slides) |
| Xlsx Toolkit | `xlsx-toolkit/` | `xlsx_auditor.py` | Excel audit (sheets, formulas, hidden sheets, external links, named ranges) |

## Design Notes

- All scripts use stdlib only (`zipfile`, `xml.etree.ElementTree`, `re`).
- All scripts support `--json` for programmatic use.
- Read-only by design — these are *audit* tools, not generators.
- For *generating* documents, use the templates in each `assets/` folder and edit in the source app.
- For programmatic generation needs, install the relevant library separately (`python-docx`, `python-pptx`, `openpyxl`, `pdfplumber`).

## Cross-Domain Integration

| Pair with… | When |
|------------|------|
| `legal/` | Contract redline audits (docx + pdf) |
| `c-level-advisor/board-deck-builder` | Board deck handoff (pptx + pdf) |
| `finance/` | Financial model review (xlsx) |
| `marketing/` | Whitepaper / case-study handoff (pdf, docx) |
| `personal-productivity/` | Resume PDF audit before submission |

## Adding a New Skill to This Domain

1. Create folder `documents/<skill-name>/`
2. Add `SKILL.md` with frontmatter (name, description, keywords)
3. Implement Python tool in `scripts/` — stdlib only, dual JSON + human output
4. Write a knowledge base in `references/`
5. Provide a user-facing template / checklist in `assets/`
6. Add a row to the table above
