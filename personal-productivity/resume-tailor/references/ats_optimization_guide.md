# ATS Optimization Guide

Most resumes pass through an Applicant Tracking System (ATS) before a human ever sees them. ATS parses your resume, extracts structured fields, and ranks you against the job description. Optimize for both the parser and the human — never one at the expense of the other.

---

## How ATS Parses a Resume

1. **Extracts text** from PDF or DOCX (PDF is fine if exported from a word processor — never an image).
2. **Tags sections** by header words (Experience, Education, Skills, etc.).
3. **Pulls keywords** from each section.
4. **Scores** match against the JD keyword list.
5. **Ranks** alongside other applicants.

A resume that scores poorly here may never reach a recruiter, regardless of qualifications.

---

## Formatting Do's

- **Single-column layout.** Multi-column resumes confuse parsers — text gets reordered.
- **Standard section headers.** Use "Experience", "Education", "Skills", "Projects" — not "Where I've Been" or "What I Bring."
- **Plain fonts.** Arial, Calibri, Helvetica, Times — 10-12pt body, 12-14pt headers.
- **Black text on white background.**
- **Use bullet points (•, -, *)** rather than long paragraphs.
- **Save as DOCX or PDF** (PDF must be text-based, not scanned).
- **Include both spelled-out and acronym** versions of key terms ("Search Engine Optimization (SEO)").
- **Date format:** "Mar 2023 – Present" or "03/2023 – Present" — be consistent.

---

## Formatting Don'ts

- **No tables.** ATS frequently mis-parses cells.
- **No graphics, icons, or charts.** Visual elements are often dropped or rendered as garbage text.
- **No headers / footers** for content. Some parsers skip them entirely.
- **No text boxes.** Same problem as tables.
- **No fancy bullet glyphs** (★, ▶, ✓). Stick to •, -, *.
- **No images of text** — never export a resume as an image PDF.
- **No hyperlinks as the only contact info.** Always include the plain text URL.

---

## Keyword Density

- **Target 1.5%-3% density** for primary keywords (each appears 1-3 times for a one-page resume).
- **Match the JD's exact phrasing** when possible — if it says "Kubernetes", use "Kubernetes", not "K8s alone".
- **Use the term in context**, not as a list dump. "Built a Kubernetes-based deployment pipeline" beats "Skills: Kubernetes."
- **Mirror seniority signals** — "led", "owned", "architected" for senior roles.

---

## Skills Section: Skim-Friendly Lists

Group skills by category, not as one long blob:

```
Languages: Python, TypeScript, Go
Cloud / Infra: AWS, Kubernetes, Terraform, Docker
Data: PostgreSQL, Snowflake, dbt, Airflow
Other: GraphQL, REST APIs, gRPC
```

This format parses cleanly and skims well.

---

## File Naming

Name files predictably so recruiters and ATS dashboards can find them later:

```
FirstLast-Resume-CompanyName.pdf
FirstLast-Resume-RoleTitle.pdf
```

Avoid spaces, version numbers, or dates in the filename.

---

## Common ATS Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Mis-parsed dates | Roles appear in wrong order | Use "Mar 2023 – Present" format consistently |
| Lost contact info | Phone or email missing | Move out of headers/footers into body |
| Skills missed | Match score drops despite having skills | Move skills out of sidebar, into a labeled section |
| Garbled formatting | Random characters in extracted text | Re-export from Word/Google Docs as DOCX |
| No section recognition | All bullets lumped together | Use standard section headers verbatim |

---

## Length Guidance

- **0-7 years experience:** 1 page.
- **7-15 years:** 1-2 pages.
- **15+ years:** 2 pages maximum unless academic/research CV.
- **Never 3 pages outside academia.**

---

## Final Pre-Submit Checklist

- [ ] Single column, no tables, no graphics
- [ ] Standard section headers
- [ ] Plain text version readable when copy-pasted into a notepad
- [ ] All five top JD keywords appear at least once
- [ ] No weak-phrase blacklist matches
- [ ] Filename in `FirstLast-Resume-CompanyName.pdf` format
- [ ] Both DOCX and PDF generated and tested
