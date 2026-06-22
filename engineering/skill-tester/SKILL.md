---
name: skill-tester
description: >
  Validate and score Claude Code skill packages for quality, completeness, and best-practice
  compliance. Tests Python scripts, checks YAML frontmatter, and generates reports. Use when
  creating, validating, or auditing skill packages.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: meta-skills
  tier: POWERFUL
  updated: 2026-06-17
---
# Skill Tester

Validate skill packages for structure compliance, test Python scripts for syntax and stdlib-only imports, and score quality across four dimensions (documentation, code quality, completeness, usability) with letter grades and improvement recommendations. Supports BASIC, STANDARD, and POWERFUL tier classification.

## Core Capabilities

- **Structure validation** — check required files, directory layout, YAML frontmatter, and required SKILL.md sections against tier thresholds.
- **Script testing** — AST syntax checks, stdlib-only import analysis, argparse and `__main__`-guard detection, runtime `--help` and sample-data execution.
- **Quality scoring** — four equally weighted dimensions producing an overall score, letter grade (A+ through F), and a prioritized improvement roadmap.
- **Tier classification** — BASIC / STANDARD / POWERFUL requirements for SKILL.md depth, script count/LOC, argparse, output formats, and error handling.
- **Dual output** — human-readable reports and `--json` for CI/CD gating with meaningful exit codes.

## When to Use

- Creating a new skill and validating it before publishing.
- Auditing an existing skill's structure, scripts, and quality.
- Embedding a quality gate into a CI/CD pipeline.

## Clarify First

Before validating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target skill path** — the skill directory to validate, test, and score (the subject of all three tools)
- [ ] **Target tier** — BASIC / STANDARD / POWERFUL (`--tier`; sets the required sections, script count, and structural thresholds)
- [ ] **Pass bar** — the minimum quality score / whether failures gate CI (`--minimum-score`, exit codes)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Validate skill structure and documentation
python skill_validator.py engineering/my-skill --tier POWERFUL --json

# Test all Python scripts in a skill
python script_tester.py engineering/my-skill --timeout 30

# Score quality with improvement roadmap
python quality_scorer.py engineering/my-skill --detailed --minimum-score 75
```

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `skill_validator.py` | Validate structure, frontmatter, required sections, and scripts against tier rules | `python scripts/skill_validator.py engineering/my-skill --tier POWERFUL --json` |
| `script_tester.py` | Static + runtime tests of scripts (syntax, imports, argparse, `--help`, samples) | `python scripts/script_tester.py engineering/my-skill --timeout 60 --json` |
| `quality_scorer.py` | Score four quality dimensions with letter grade and improvement roadmap | `python scripts/quality_scorer.py engineering/my-skill --detailed --minimum-score 75 --json` |

See **[references/tool-reference.md](references/tool-reference.md)** for full parameter tables, output formats, and exit codes.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-cicd.md](references/workflows-and-cicd.md)** — the three core validation workflows, the tier-requirements and quality-scoring tables, CI/CD integration, anti-patterns, troubleshooting, and success criteria. Read when running a validation pass or wiring a CI gate.
- **[references/tool-reference.md](references/tool-reference.md)** — full parameter tables, output formats, and exit codes for the three Python tools. Read when scripting the tools or interpreting JSON output.
- **[references/skill-structure-specification.md](references/skill-structure-specification.md)** — the authoritative specification for skill directory structure, required files, and frontmatter. Read when defining what "valid structure" means.
- **[references/tier-requirements-matrix.md](references/tier-requirements-matrix.md)** — the full BASIC/STANDARD/POWERFUL requirements matrix with detailed criteria per tier. Read when classifying or upgrading a skill's tier.
- **[references/quality-scoring-rubric.md](references/quality-scoring-rubric.md)** — the detailed scoring rubric with per-component weights and grading bands. Read when interpreting or tuning quality scores.

## Scope & Limitations

**Covers:**
- Structural validation of skill directories against tier-specific requirements (BASIC, STANDARD, POWERFUL)
- Static analysis of Python scripts including syntax checking, import validation, argparse detection, and main guard verification
- Multi-dimensional quality scoring across documentation, code quality, completeness, and usability
- Dual output formatting (JSON for CI/CD pipelines, human-readable for developer consumption)

**Does NOT cover:**
- Functional correctness of script logic or algorithm accuracy — the tester verifies structure and conventions, not business logic
- Performance benchmarking or memory profiling of scripts — see `engineering/performance-profiler` for runtime analysis
- Security vulnerability scanning of script code — see `engineering/skill-security-auditor` for dependency and code security audits
- Cross-skill dependency resolution or integration testing — skills are validated in isolation without verifying inter-skill compatibility

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/skill-security-auditor` | Run security audit after validation passes | `skill_validator.py` confirms structure compliance, then `skill-security-auditor` scans for vulnerabilities in the same skill path |
| `engineering/ci-cd-pipeline-builder` | Embed skill-tester as a quality gate stage | Pipeline builder generates workflow YAML that invokes `skill_validator.py`, `script_tester.py`, and `quality_scorer.py` sequentially |
| `engineering/changelog-generator` | Feed quality score deltas into changelog entries | Compare `quality_scorer.py` JSON output between releases to surface quality improvements or regressions |
| `engineering/pr-review-expert` | Attach validation report to pull request reviews | `skill_validator.py --json` output is posted as a PR comment for reviewer context |
| `engineering/performance-profiler` | Complement structural testing with runtime profiling | After `script_tester.py` confirms execution succeeds, `performance-profiler` measures execution time and resource usage |
| `engineering/tech-debt-tracker` | Track quality score trends over time | Periodic `quality_scorer.py --json` output is ingested to detect score degradation and flag technical debt |
