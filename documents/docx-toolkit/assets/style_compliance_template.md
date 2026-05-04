# Allowed Paragraph Styles (Style Guide)

Use this template to declare which paragraph styles your team allows. Run the auditor against any candidate document; flag any document using styles outside this list.

---

## Allowed Styles

| Style name (in Word) | Use for | Notes |
|---------------------|---------|-------|
| `Normal` | Body text | Default; do not modify |
| `Heading 1` | Major sections | One per document or major part |
| `Heading 2` | Subsections | Required between H1 and H3 |
| `Heading 3` | Sub-subsections | Avoid going deeper |
| `List Paragraph` | Bulleted / numbered lists | Standard list style |
| `Quote` | Block quotations | Indented, italicized |
| `Caption` | Figure / table captions | Auto-numbered |
| `Footer` | Page footer content | Includes confidentiality marking |

---

## Disallowed Styles

Anything not on the allowed list. Common drift offenders:

- `Body Text 2`, `Body Text 3` — collapse to `Normal`
- `Heading 4`, `Heading 5` — restructure or use `Heading 3`
- Inline overrides (bold, color) instead of named styles
- Custom named styles inherited from older templates

---

## Validation Workflow

1. Run auditor: `python scripts/docx_auditor.py document.docx`
2. Compare `styles_used` output against this template
3. Any style not on the allowed list → reformat the offending paragraphs
4. Re-run audit until `styles_used` is a subset of the allowed list

---

## Tips

- **Lock the template.** Distribute a `.dotx` template containing only allowed styles. New documents start clean.
- **Train, then enforce.** Style sprawl usually comes from copy-paste from email or other documents. A short style-guide deck plus the audit-as-gate prevents most of it.
- **Don't fight the brand team.** If marketing says the heading color is `#1A47BC`, use it via the named style, not inline.
