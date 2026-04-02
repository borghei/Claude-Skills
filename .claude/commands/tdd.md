---
description: Guide a Test-Driven Development workflow for the current task.
---

Apply TDD (Red-Green-Refactor) to the current task:

1. **Understand the requirement** — clarify what behavior needs to be implemented.
2. **Detect test framework** — scan for jest.config, pytest.ini, vitest.config, .rspec, etc.
3. **Red phase — Write a failing test:**
   - Write the simplest test that describes the desired behavior
   - Run it — confirm it fails for the right reason (not a syntax error)
   - Test should be specific: one behavior per test
4. **Green phase — Make it pass:**
   - Write the minimum code to make the test pass
   - No premature optimization or abstraction
   - "Fake it till you make it" is acceptable at this stage
5. **Refactor phase — Clean up:**
   - Remove duplication between test and production code
   - Improve naming and structure
   - Run tests again — all must still pass
6. **Repeat** for the next behavior.

**Guidelines:**
- Test naming: `should [expected behavior] when [condition]`
- One assertion per test (prefer)
- Test the interface, not the implementation
- If you need a mock, question the design first
- Run the full test suite after each green phase to catch regressions

**Framework-specific hints:**
- Jest/Vitest: use `describe/it/expect` blocks
- pytest: use plain functions with `assert`
- Go: use `testing.T` with table-driven tests
