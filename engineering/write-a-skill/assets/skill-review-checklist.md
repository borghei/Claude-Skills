# Skill Publication Review Checklist

Copy this into the PR that adds the skill. Every box must be checked by someone
other than the author before merge. `skill_lint.py` covers the mechanical half;
the judgement half is yours.

**Skill:** `<domain>/<name>`
**Reviewer:** `<name>`
**Lint result:** `python3 engineering/write-a-skill/scripts/skill_lint.py --skill <path> --strict`

## Mechanical (the linter proves these)

- [ ] Frontmatter has `name`, `description`, `license`, and all six `metadata` fields
- [ ] `name` matches the folder name exactly
- [ ] Description is ≤ 240 characters and contains a `Use when ...` clause
- [ ] SKILL.md is under 500 lines; each reference is under 800
- [ ] Every script is 150-300 lines, has argparse, `--format`, and a `__main__` guard
- [ ] Every import resolves to the standard library
- [ ] Required sections present in order; at least 3 anti-patterns
- [ ] `assets/` ships at least one `sample_*.json`

## Judgement (only a human proves these)

- [ ] **Activation** — read only the description. Can you name three user
      sentences that should activate it, and three near-miss sentences that
      should not? If the near-misses also match, the triggers are too broad.
- [ ] **Opinion** — every recommendation states a position, a reason, and an
      escape hatch. No section presents a menu of equal options.
- [ ] **Thresholds** — decision tables contain real numbers, not "it depends"
      or "as appropriate."
- [ ] **Anti-patterns are real** — each one describes a mistake the author has
      actually seen, with a root cause that sounds reasonable on the surface.
- [ ] **Scripts earn their place** — each does analysis a human would otherwise
      do by hand for 15+ minutes. No script is a formatter around user input.
- [ ] **Runnable** — every bash block in Workflows was executed verbatim against
      the shipped sample data, and its output was pasted into the PR.
- [ ] **Self-contained** — copy the folder to an empty directory. SKILL.md still
      reads, scripts still run, no path breaks. `standards/` is the only
      permitted outbound reference.
- [ ] **Quality bar** — write one sentence estimating the time saved versus
      doing the task unaided. If it is under 40%, do not publish.

## Reject reasons (write one if you decline)

| Reason | What it means |
|--------|---------------|
| Thin wrapper | The skill restates a generic process with no thresholds or tools |
| Duplicate | An existing skill in the library already owns this trigger space |
| Unrunnable | A workflow's bash block errors against the shipped samples |
| Menu writing | The skill lists options without recommending one |
| Reference dump | Content that belongs in `references/` is inflating SKILL.md |
