# Handoff: Add --dry-run to the exporter CLI

**From:** interactive session  **To:** background agent  **Date:** 2026-11-08
**Assumptions:** none

## Goal & done-state
`exporter --dry-run` prints what would be written and writes nothing. Done when the flag
exists, `tests/exporter/test_main.py` covers both modes, `make test` and `ruff check src`
pass, and a draft PR is open against `main`.

## Current state
- [x] Done: flag parsed in `src/exporter/main.py` (`build_parser()`), commit `a1b2c3d`.
- [~] In progress: write path skips output when the flag is set; `test_writes_file` passes, no dry-run test yet.
- [ ] Untouched: README usage section.

## Next steps (in order)
1. Add `test_dry_run_writes_nothing` in `tests/exporter/test_main.py`; expect no file in `tmp_path`.
2. Print the target path and row count in dry-run mode from `src/exporter/main.py`.
3. Add the flag to the README usage block.
4. Run `make test` and `ruff check src`; open a draft PR titled `feat(exporter): add --dry-run`.

**Start here:** step 1 — write the failing test first.

## Decisions already made (don't relitigate)
- Dry-run prints to stdout, not stderr — matches the existing `--verbose` output.

## Abandoned paths (tried, ruled out)
- Bare `pytest` — fails on import; use `make test` (sets `PYTHONPATH=src`).

## Stop and report when
- Any test outside `tests/exporter/` fails.
- The change needs a new dependency or touches `src/importer/`.

## Report back
- Draft PR link plus a three-line summary as the PR description; nothing else.

## Suggested skills
- tdd-guide — the red-green loop for step 1 and 2.
- code-reviewer — two-axis review of the branch before opening the PR.

## Key locations
- Branch: `feat/exporter-dry-run`
- Spec: `docs/specs/exporter-dry-run.md`
