# Workflows, Tiers & CI/CD

Read this for the three core validation workflows, the tier/scoring tables, CI/CD integration, anti-patterns, troubleshooting, and success criteria.

## Core Workflows

### Workflow 1: Validate a New Skill

1. Run `skill_validator.py` with target tier to check structure, frontmatter, required sections, and scripts
2. Review errors (blocking) and warnings (non-blocking) in the report
3. Fix all errors -- missing SKILL.md, invalid frontmatter, external imports
4. **Validation checkpoint:** Score >= 60; zero errors; all scripts pass `ast.parse()`

```bash
python skill_validator.py engineering/my-skill --tier STANDARD --json
```

### Workflow 2: Test Skill Scripts

1. Run `script_tester.py` to execute syntax validation, import analysis, and runtime tests
2. Review per-script results: argparse detection, `--help` output, sample data execution
3. Fix failures: add `if __name__ == "__main__"` guards, replace external imports with stdlib
4. **Validation checkpoint:** All scripts pass syntax; zero external imports; `--help` exits cleanly

```bash
python script_tester.py engineering/my-skill --timeout 60 --json
```

### Workflow 3: Score and Improve Quality

1. Run `quality_scorer.py` with `--detailed` for component-level breakdowns
2. Review the prioritized improvement roadmap (up to 5 items)
3. Address HIGH-priority items first (documentation gaps, missing error handling)
4. Re-run to verify score improvement
5. **Validation checkpoint:** Overall score >= 75; no dimension below 50%

```bash
python quality_scorer.py engineering/my-skill --detailed --minimum-score 75 --json
```

## Tier Requirements

| Requirement | BASIC | STANDARD | POWERFUL |
|-------------|-------|----------|----------|
| SKILL.md lines | 40-500 | 40-500 | 40-500 |
| Python scripts | 1 (100-300 LOC) | 1-2 (300-500 LOC) | 2-3 (500-800 LOC) |
| Argparse | Basic | Subcommands | Multiple modes |
| Output formats | Single | JSON + text | JSON + text + validation |
| Error handling | Essential | Comprehensive | Advanced recovery |

## Quality Scoring Dimensions

| Dimension | Weight | Measures |
|-----------|--------|----------|
| Documentation | 25% | SKILL.md depth, README clarity, reference quality |
| Code Quality | 25% | Complexity, error handling, output consistency |
| Completeness | 25% | Required files, sample data, expected outputs |
| Usability | 25% | Argparse help text, example clarity, ease of setup |

**Grades:** A+ (97+) through F (<40). Exit code 0 for A+ through C-, exit code 2 for D, exit code 1 for F.

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Validate Changed Skills
  run: |
    for skill in $(git diff --name-only | grep -E '^engineering/[^/]+/' | cut -d'/' -f1-2 | sort -u); do
      python engineering/skill-tester/scripts/skill_validator.py $skill --json
      python engineering/skill-tester/scripts/script_tester.py $skill
      python engineering/skill-tester/scripts/quality_scorer.py $skill --minimum-score 75
    done
```

## Anti-Patterns

- **Padding SKILL.md with filler** -- line count thresholds measure substantive content; blank lines and boilerplate do not count
- **External imports disguised as stdlib** -- the import allowlist is manually maintained; if a legit stdlib module is flagged, add it to `stdlib_modules`
- **Missing argparse help strings** -- usability scoring requires `help=` parameters on every argument; empty help strings score zero
- **No `__main__` guard** -- scripts without `if __name__ == "__main__"` fail runtime tests when imported
- **Relying on SKILL.md for usability** -- usability is scored from scripts and README independently; a detailed SKILL.md does not compensate for missing `--help` output

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `SKILL.md too short` error despite sufficient content | Validator counts only non-blank lines; blank lines inflate raw line count but are excluded from the tally | Remove excessive blank lines or add more substantive content sections to meet the tier threshold |
| YAML frontmatter parse failure | Frontmatter contains invalid YAML syntax (unquoted colons, tabs instead of spaces, missing closing `---`) | Validate frontmatter through `yaml.safe_load()` locally; ensure the closing `---` marker is present on its own line |
| External import false positive | The stdlib module allowlist in `skill_validator.py` and `script_tester.py` is manually maintained and may not include every standard library module | Add the missing module name to the `stdlib_modules` set in the relevant script, or restructure the import |
| Script execution timeout during testing | Script requires interactive input, enters an infinite loop, or performs long-running computation | Increase `--timeout` value, add early-exit logic for missing arguments, or ensure scripts exit cleanly when no input is provided |
| Tier compliance check fails despite passing individual checks | `_validate_tier_compliance` only examines `skill_md_exists`, `min_scripts_count`, and `skill_md_length`; other failures (e.g., missing directories) are reported separately | Fix the specific critical checks listed in the error message; review the `TIER_REQUIREMENTS` dictionary for the target tier |
| Quality scorer reports low usability despite good documentation | Usability dimension scores help text inside scripts, `README.md` usage sections, and practical example files independently of SKILL.md content | Add `argparse` help strings with `help=` parameters, include a `Usage` section in README.md, and place sample/example files in the `assets/` directory |
| `--json` flag produces no output | Script raised an unhandled exception before reaching the output formatter; errors are written to stderr | Run with `--verbose` to see the full traceback on stderr, then address the underlying exception |

## Success Criteria

- **Structure pass rate above 95%**: Validated skills pass all required-file and directory-structure checks on first run in at least 95% of cases.
- **Script syntax zero-defect**: Every Python script in a validated skill compiles without `SyntaxError` via `ast.parse()`.
- **Standard library compliance 100%**: No external (non-stdlib) imports detected across all validated scripts.
- **Quality score consistency within 5 points**: Re-running `quality_scorer.py` on an unchanged skill produces scores that vary by no more than 5 points across runs.
- **Execution time under 10 seconds per skill**: Full validation, testing, and scoring pipeline completes in under 10 seconds for a single skill with up to 3 scripts.
- **Actionable recommendation density**: Every skill scoring below 75/100 receives at least 3 prioritized improvement suggestions in the roadmap.
- **CI/CD gate reliability**: When integrated as a GitHub Actions step, the tool exits with non-zero status for every skill that fails critical checks, blocking the merge.
