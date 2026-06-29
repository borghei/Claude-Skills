---
title: Skill Catalog
---

# Skill Catalog

343 production-ready skills across 17 domains, each with Python CLI tools, reference guides, and templates.

## Domains at a Glance

| Domain | Skills | Tools | Page |
|---|:---:|:---:|---|
| **★ Project Management** (most-used) | **66** | **82+** | **[View all](project-management.md)** |
| Engineering | 86 | 245 | [View all](engineering.md) |
| Marketing | 39 | 118+ | [View all](marketing.md) |
| C-Level Advisory | 31 | 88+ | [View all](c-level.md) |
| RA/QM & Compliance | 27 | 50+ | [View all](compliance.md) |
| Business Growth | 20 | 60+ | [View all](business.md#business-growth) |
| Legal (Experimental) | 17 | 34 | [View all](legal.md) |
| Product Team | 13 | 30+ | [View all](product.md) |
| Research (new) | 4 | 12 | [View all](research.md) |
| Personal Productivity | 10 | — | [View all](other.md) |
| Vertical Advisors | 7 | — | [View all](other.md) |
| Data & Analytics | 5 | 16 | [View all](other.md#data--analytics) |
| Sales & Success | 5 | 15 | [View all](business.md#sales--success) |
| HR & Operations | 4 | 12 | [View all](other.md#hr--operations) |
| Documents | 4 | — | [View all](other.md) |
| Finance | 3 | 10 | [View all](business.md#finance) |
| Workflow (meta-skills) | 2 | — | [View all](other.md) |
| **Total** | **343** | **786** | |

## Skill Package Structure

Every skill follows the same structure:

```
skill-name/
├── SKILL.md        # Master documentation and workflows
├── scripts/        # Python CLI tools (standard library only)
├── references/     # Expert knowledge bases
└── assets/         # User templates
```

**Design philosophy:** Skills are self-contained packages. Each includes executable tools (Python scripts), knowledge bases (markdown references), and user-facing templates. Extract a skill folder and use it immediately.

## How to Use a Skill

1. **Read the SKILL.md** -- Contains workflows, best practices, and when to use it
2. **Run the scripts** -- `python skill-name/scripts/tool.py [args]` for automated analysis
3. **Reference the knowledge** -- `references/` contains expert-curated frameworks
4. **Apply templates** -- `assets/` has ready-to-customize deliverable templates

!!! tip "Browse by domain"
    Use the sidebar to jump to a specific domain, or search for a skill by name.
