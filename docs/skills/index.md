---
title: Skill Catalog
---

# Skill Catalog

242 production-ready skills across 14 domains, each with Python CLI tools, reference guides, and templates.

## Domains at a Glance

| Domain | Skills | Tools | Page |
|---|:---:|:---:|---|
| Engineering | 76 | 224 | [View all](engineering.md) |
| Marketing | 38 | 115 | [View all](marketing.md) |
| C-Level Advisory | 26 | 73 | [View all](c-level.md) |
| Project Management | 22 | 53 | [View all](product.md#project-management) |
| RA/QM & Compliance | 21 | 38 | [View all](compliance.md) |
| Business Growth | 16 | 48 | [View all](business.md#business-growth) |
| Product Team | 8 | 15 | [View all](product.md#product-team) |
| Data & Analytics | 5 | 16 | [View all](other.md#data--analytics) |
| Sales & Success | 5 | 15 | [View all](business.md#sales--success) |
| HR & Operations | 4 | 12 | [View all](other.md#hr--operations) |
| Finance | 3 | 10 | [View all](business.md#finance) |
| Legal (Experimental) | 17 | 34 | [View all](legal.md) |
| **Total** | **242** | **647** | |

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
