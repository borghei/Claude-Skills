---
title: <Document title>
author: <Team or person>
date: <YYYY-MM-DD>
status: draft
audience: <exec / working team / external>
---

# <Document title>

<Two to four sentences: what question this document answers, what it covers, and
what it concludes. A reader who stops here should still know the recommendation.>

[TOC]

## Context {#sec:context}

<What is true today and why it matters now. Numbers, not adjectives. This section
earns the reader's attention — if the situation is not clearly a problem, the
rest of the document has no purpose.>

![<Describe what the figure shows, 15-125 characters>](figures/<name>.png){#fig:context}

## Analysis {#sec:analysis}

<The evidence. One subsection per line of argument.>

### <First line of argument>

<Prose. Reference evidence by number — [@fig:context], [@tbl:options] — never
"the chart below".>

| Option | <Dimension> | <Dimension> | <Dimension> |
|--------|-------------|-------------|-------------|
| A      |             |             |             |
| B      |             |             |             |
| C      |             |             |             |

Table: <What the table shows and how to read it> {#tbl:options}

### <Second line of argument>

<Prose. Put the caveat that would break the sentence in a footnote.[^caveat]>

## Recommendation {#sec:recommendation}

**<State the recommendation in bold, as a directive, in one sentence.>**

<Why this option and not the others. Reference [@tbl:options] explicitly. Name
the option you rejected and why — a recommendation that does not say what it
rejected reads as though only one option was considered.>

### What this costs

<The honest downside. Every recommendation has one. Omitting it does not make it
disappear; it makes the reader distrust the rest.>

### What happens next

1. <Action> — <owner> — <date>
2. <Action> — <owner> — <date>

## Open questions {#sec:open}

- <Question that would change the recommendation if answered differently>
- <Question that does not block the decision but needs an owner>

---

[^caveat]: <The qualification, the exception, or the assumption that a careful
    reader would otherwise challenge.>

<!--
Before publishing:
  1. crossref_auditor.py  — labels, references, alt text, heading hierarchy
  2. md_to_html.py        — convert; the gate fails on unresolved references
  3. print_profile.py     — if this will be printed or exported to PDF
  4. Proof every page of the PDF, not just the first three
-->
