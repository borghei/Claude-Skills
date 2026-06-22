---
name: domain-name-brainstormer
description: >
  Generate and score candidate brand, product, and domain names for
  memorability and pronounceability. Use when naming a new product, company,
  or feature, brainstorming brand names, or finding an available .com.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: branding
  updated: 2026-05-04
  python-tools: name_generator.py
  tech-stack: branding, naming
---

# Domain Name Brainstormer

Generate and score candidate brand / domain names from seed words using common naming patterns. The script does not check live registration — it produces candidates fast so you can spend your time evaluating the best ones.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Best Practices](#best-practices)

---

## Keywords

domain, domain name, naming, brand naming, product name, company name, .com, brainstorm, naming brainstorm, brand identity, naming strategy

---

## Clarify First

Before generating names, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Seed words** — 3-7 words describing the product, value, or feeling; every candidate is built from these
- [ ] **Brand tone** — serious/technical vs playful/coined steers which patterns (blend, vowel-drop, prefix-suffix) to favor
- [ ] **TLD preference** — .com vs .ai/.io/.co changes the shortlist and whether the `tld_suffix` pattern applies

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

---

## Quick Start

### Generate 200 Candidates in 30 Seconds

```bash
python scripts/name_generator.py "data,insight,signal" --count 200
```

Then:
1. Eliminate anything > 12 characters
2. Eliminate anything that's hard to spell after hearing it once
3. Eliminate anything that sounds like a competitor
4. Take the top 10-15 to a registrar (manually) to check availability across .com / .ai / .io / .co

---

## Core Workflows

### Workflow 1: Seed-Word Brainstorm

**Goal:** Convert a few keywords describing the product into 100+ ranked candidates.

**Steps:**
1. List 3-7 seed words that describe the product, value, or feeling
2. Run: `python scripts/name_generator.py "seed1,seed2,seed3" --count 200`
3. Sort the output by score (highest first)
4. Apply the elimination filter from `references/naming_framework.md`
5. Pick a shortlist of 10-15 to manually check for trademark and domain availability

**Expected Output:** Ranked list of candidates with scores, classified by pattern (vowel-drop, blend, prefix-suffix, TLD-as-suffix).

**Time Estimate:** 5-10 minutes.

### Workflow 2: Pattern-Specific Generation

**Goal:** Get more of one specific pattern (e.g., only blends, or only TLD-as-suffix names).

**Steps:**
1. Run with pattern filter: `python scripts/name_generator.py "fast,ship" --pattern blend --count 100`
2. Available patterns: `vowel_drop`, `prefix_suffix`, `blend`, `tld_suffix`, `repeat`, `all`
3. Iterate seeds until you have 20+ candidates worth taking to availability checks

**Expected Output:** Pattern-specific list.

**Time Estimate:** 5 minutes per pattern variation.

### Workflow 3: Trademark / Availability Pre-Check

**Goal:** Avoid wasting energy on names that are obviously taken.

**Steps:**
1. Take the shortlist from Workflow 1 or 2
2. **Manually** check each on:
   - A domain registrar (Namecheap, Cloudflare, Porkbun) for .com / .ai / .io / .co
   - The USPTO TESS database (or your jurisdiction's trademark office) for live trademarks in the relevant class
   - A regular Google search for existing usage
3. Drop anything with a live trademark in the same product class, an active product on a similar domain, or a trademarked .com that you do not own

> The script does **not** automate registrar lookups — those need real network calls and rate-limited APIs. Doing this step manually for a 10-name shortlist takes 10-15 minutes.

---

## Tools

### name_generator.py

Generates candidate names by applying naming patterns to seed words and scores each on length, pronounceability, and uniqueness.

```bash
# Default: 100 candidates, all patterns
python scripts/name_generator.py "data,signal,insight"

# More results
python scripts/name_generator.py "data,signal" --count 300

# One pattern only
python scripts/name_generator.py "data,signal" --pattern vowel_drop

# JSON for programmatic use
python scripts/name_generator.py "data,signal" --json
```

**Patterns implemented:**
- `vowel_drop` — Remove inner vowels: "data" → "dta", "insight" → "nsght"
- `prefix_suffix` — Add common naming prefixes/suffixes: "ly", "ify", "io", "lab", "labs", "hq", "co", "stack", "kit", "app"
- `blend` — Combine two seeds: "data" + "signal" → "dasignal", "datignal"
- `tld_suffix` — Treat TLD as part of the name: "send.fast" reads as "sendfast"
- `repeat` — Doubling pattern: "data" → "datadata"

**Score (0-100) factors:**
- Length 5-10 chars scores highest
- Pronounceability via consonant-vowel ratio
- Penalty for common-word collisions
- Penalty for hyphens or numbers (these dilute brand)

---

## Reference Guides

- **`references/naming_framework.md`** — Why names matter, the elimination filter, naming-pattern playbook, common pitfalls

---

## Best Practices

- **Don't pre-commit to .com.** A `.io` or `.ai` is fine for most B2B products in 2026; `.com` matters less than it did a decade ago.
- **Say it out loud.** If you can't tell someone the domain in a noisy bar and have them spell it correctly, drop it.
- **Avoid naming-collisions.** A "DataLoop" in your space and a "DataLoop" in adjacent SaaS will cause confusion forever.
- **Don't pick the first one.** Generate 200, filter to 30, shortlist 10, sit on the shortlist for 24 hours. The one that still feels right after sleeping is the one.
- **Trademark before launching.** A great name with a trademark conflict will cost you a rebrand later.

---

## Integration Points

- Pairs with `marketing/brand-strategist/` for brand-narrative work
- Pairs with `marketing/landing-page-generator/` for messaging once a name is chosen
- Used by `c-level-advisor/` workflows during company / product launches
