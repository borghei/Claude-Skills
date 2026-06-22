---
name: resume-tailor
description: >
  Tailor a resume to a job description by extracting keywords, scoring match,
  and rewriting bullets for impact. Use when applying to a role, optimizing
  for ATS keyword match, or customizing a cover letter.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: career
  updated: 2026-05-04
  python-tools: resume_matcher.py
  tech-stack: ATS, job-search
---

# Resume Tailor

Tailor a base resume to a specific job description with keyword-match scoring, gap analysis, and rewritten-bullet suggestions.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Templates](#templates)
- [Best Practices](#best-practices)

---

## Keywords

resume, CV, job application, ATS, applicant tracking system, keyword match, resume tailoring, cover letter, job description, hiring, recruiter, career, job search, bullet rewrite, accomplishment, impact statement

---

## Clarify First

Before tailoring the resume, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target job description** — the verbatim JD; it drives keyword extraction and the entire match score
- [ ] **Base resume content** — your actual experience and bullets; without it there is nothing to score or rewrite
- [ ] **Target seniority / title** — IC vs lead vs exec sets which keywords matter and the altitude of rewritten bullets
- [ ] **Truth boundary** — which listed skills you genuinely have vs. aspirational, so additions are honest rather than keyword-stuffed

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

---

## Quick Start

### Tailor a Resume in 5 Minutes

1. Save the job description as `jd.txt`
2. Save your base resume text as `resume.txt`
3. Run the matcher:
   ```bash
   python scripts/resume_matcher.py resume.txt jd.txt
   ```
4. Review the keyword-gap report
5. Rewrite low-scoring bullets using `references/bullet_rewrite_patterns.md`
6. Cross-check the final resume against the rewritten template in `assets/tailored_resume_template.md`

---

## Core Workflows

### Workflow 1: Match Score and Keyword Gap

**Goal:** Get a quantitative score for how well the current resume matches a target job description before submitting.

**Steps:**
1. Capture the job description verbatim into `jd.txt`
2. Run: `python scripts/resume_matcher.py resume.txt jd.txt`
3. Review the score — anything below 70% means significant gaps
4. Read the missing-keywords list; classify each as (a) skills you have but did not list, (b) skills you do not have, (c) buzzwords that do not apply
5. Add (a) to the resume; ignore (c); be honest about (b)

**Expected Output:** A score, a kept-keyword list, and a missing-keyword list.

**Time Estimate:** 5-10 minutes per job description.

### Workflow 2: Bullet Rewrite for Impact

**Goal:** Convert task-oriented bullets ("responsible for…") into impact bullets that match recruiter and ATS expectations.

**Steps:**
1. Identify weak bullets — anything starting with "Responsible for" or "Helped with"
2. Apply the **CAR pattern** (Challenge, Action, Result) from `references/bullet_rewrite_patterns.md`
3. Quantify wherever possible (percentages, dollar amounts, time saved, scale)
4. Re-run the matcher to confirm score improvement

**Expected Output:** Bullet list rewritten in CAR format with metrics.

**Time Estimate:** 5 minutes per bullet.

### Workflow 3: Cover Letter Hooks

**Goal:** Pull the strongest 3-5 hooks from the resume that map directly to the top requirements in the job description.

**Steps:**
1. Run matcher in JSON mode: `python scripts/resume_matcher.py resume.txt jd.txt --json`
2. Take the top 5 matched keywords by relevance
3. For each, find the matching resume bullet
4. Use them as evidence sentences in the cover letter

**Expected Output:** 3-5 evidence sentences for the cover letter.

**Time Estimate:** 10 minutes.

---

## Tools

### resume_matcher.py

Reads a resume text file and a job description text file, returns:

- A **match score** (0-100) based on keyword overlap weighted by JD frequency
- A **kept keywords** list (in both resume and JD)
- A **missing keywords** list (in JD only)
- A **resume-only keywords** list (in resume but not JD — candidate to drop)

```bash
# Human-readable
python scripts/resume_matcher.py resume.txt jd.txt

# JSON for programmatic use
python scripts/resume_matcher.py resume.txt jd.txt --json
```

---

## Reference Guides

- **`references/bullet_rewrite_patterns.md`** — CAR pattern, action-verb library, quantification examples, weak-phrase blacklist
- **`references/ats_optimization_guide.md`** — How ATS parses resumes, formatting do's and don'ts, keyword density bounds

---

## Templates

- **`assets/tailored_resume_template.md`** — A bare resume skeleton with section ordering, length guidance, and keyword-placement notes. Fill in your content.

---

## Best Practices

- **Tailor every time.** A generic resume sent to ten roles performs worse than ten tailored versions.
- **Honesty over keyword stuffing.** Add only skills you actually have. Hiring managers can tell.
- **Keep one master resume.** Tailor variants from a single source of truth.
- **Two pages max.** Even for senior roles, two pages is the ceiling outside academia.
- **Plain text, single-column.** ATS systems still mishandle tables, graphics, and multi-column layouts.

---

## Integration Points

- Pairs with `personal-productivity/lead-researcher/` for prepping informational interviews
- Pairs with `marketing/copywriting/` for cover letter prose quality
- Used by `agents/personas/` workflows when authoring sample profiles
