# Depth Principles

The vocabulary and rules this skill uses to judge module design. Use the terms
exactly as defined here in reviews and reports; mixing "component", "service",
"layer" and "module" for the same thing is how design conversations drift.

## Contents

- [Vocabulary](#vocabulary)
- [What depth is and is not](#what-depth-is-and-is-not)
- [Five tests for a module](#five-tests-for-a-module)
- [Information hiding and how it leaks](#information-hiding-and-how-it-leaks)
- [Seams and adapters](#seams-and-adapters)
- [Dependency categories and how to test across them](#dependency-categories-and-how-to-test-across-them)
- [Interface design moves](#interface-design-moves)
- [Shapes that look shallow but are fine](#shapes-that-look-shallow-but-are-fine)

## Vocabulary

| Term | Meaning in this skill | Say this instead of |
|------|----------------------|---------------------|
| **Module** | Any unit with an interface and an implementation: a function, a class, a file, a package, a service | component, unit, layer (when you mean a single unit) |
| **Interface** | Everything a caller must know to use the module correctly: names and parameters, but also error modes, ordering rules, required configuration, performance expectations, invariants | API, signature (both too narrow) |
| **Implementation** | The code behind the interface | internals, guts |
| **Depth** | How much behaviour a caller gets per unit of interface they must learn | — |
| **Deep module** | Small interface, substantial hidden behaviour | — |
| **Shallow module** | Interface nearly as large as what it does | thin wrapper (when it is not deliberate) |
| **Pass-through** | A function or method whose body only forwards its arguments to another call | delegation (when it adds nothing) |
| **Seam** | A place where behaviour can be changed without editing the code at that place — where an interface lives | boundary |
| **Adapter** | A concrete thing that fills a seam: the production database client, an in-memory fake | implementation (when the role is the topic) |
| **Leverage** | What callers gain from depth: more capability per thing learned | — |
| **Locality** | What maintainers gain from depth: a change, a bug, or a rule lives in one place | — |
| **Leak** | A design decision that is supposed to be hidden but that callers must know about | — |

## What depth is and is not

Depth is a judgement about leverage, not a line-count ratio. `module_depth.py`
reports implementation lines per interface unit because that is cheap to
compute and correlates with leverage, but it is a pointer to where to look, not
a verdict:

- A module can be padded with code and still be shallow if callers must
  understand all of it to use it.
- A short module can be deep if a two-line interface hides a subtle rule
  (rounding policy, idempotency, retry semantics) that every caller would
  otherwise reimplement.
- Interface size counts what callers must *know*, so an ordering rule ("call
  `open` before `read`") or a required config value costs as much as a parameter.
  `interface_compare.py` weights ordering rules at 2 and error modes at 0.5 for this reason.

Depth is also a property of the interface, not of the internal structure. A deep
module may be built from many small private functions, internal seams and
helpers — they simply do not appear in what callers see.

## Five tests for a module

| Test | Question | Shallow signal |
|------|----------|----------------|
| Deletion | If this module were deleted and its callers inlined the code, would complexity spread or vanish? | It vanishes: the module was only indirection |
| Caller memory | What must a new caller learn before the first correct call? | They must learn the module's internals anyway |
| Change locality | When the business rule it implements changes, how many files change? | The rule is spread across the module and its callers |
| Test surface | Can its behaviour be tested only through its interface? | Tests reach past the interface into internals |
| Name | Can it be named after one domain concept without "and", "manager", "helper", "utils"? | The name is a list of verbs or a generic noun |

A module that fails two or more is a deepening candidate.

## Information hiding and how it leaks

A module should own decisions — a data format, an algorithm, a policy, a
protocol — so that changing the decision touches only that module. Common
ways the decision escapes:

| Leak | Example | Fix |
|------|---------|-----|
| Shared format knowledge | Writer and reader of a file both encode the column order | One module owns the format and exposes read and write |
| Split by time instead of knowledge | `load_config`, `validate_config`, `apply_config` as three modules that all know the config schema | One config module that loads, validates and applies |
| Pass-through parameters | `retry_count` threaded through four signatures to reach the one function that uses it | Let the using module own the setting; inject it once |
| Exposed representation | Returning the internal list so callers mutate it | Return a copy, or expose operations instead of data |
| Private names reached from outside | `from pricing import _RATES`, `import { _applyTax }` | Promote it to the interface on purpose, or move the caller's logic inside |
| Ordering requirements | `init()` must precede `run()` | Construct ready-to-use objects; do setup inside the first call |
| Errors that callers must decode | Raising the storage driver's exception types | Translate to the module's own error modes at the seam |
| Configuration sprawl | Twelve knobs with defaults nobody understands | Choose defaults inside; expose only what callers truly vary |

`module_depth.py` detects two leak shapes mechanically: entry points with more
than `--max-params` parameters and imports of names that start with an
underscore. The rest need reading.

## Seams and adapters

- **A seam is justified by variation.** One adapter means the seam is
  hypothetical; two adapters (typically production plus a test fake) make it
  real. `interface_compare.py` rejects designs with single-adapter seams.
- **Place the seam where behaviour varies**, not where the code happens to be
  split today. A seam around the storage client is useful; a seam between two
  steps of one calculation usually is not.
- **Internal seams stay internal.** A module may have seams that only its own
  tests use. Do not add them to the public interface because a test wants them.
- **Adapters translate.** Driver exceptions, wire formats and vendor types stop
  at the adapter; the module's interface speaks the domain's language.

## Dependency categories and how to test across them

Classify each dependency of a deepening candidate; the category decides how the
deepened module is tested.

| Category | Examples | Seam? | Test approach |
|----------|----------|-------|---------------|
| In-process | Pure calculations, in-memory state | No | Merge freely; test through the new interface directly |
| Local with a stand-in | Embedded or in-memory database, temp filesystem | Internal only | Run the stand-in in tests; no port in the public interface |
| Remote, owned by you | Your other services, internal queues | Yes: a port with a network adapter and an in-memory adapter | Tests use the in-memory adapter; contract tests cover the network one |
| Remote, third party | Payment, messaging, identity providers | Yes: a port, with a fake adapter for tests | Fake adapter in tests; a small, separate suite against the provider's sandbox |

**Replace tests, do not stack them.** Once tests exist at the deepened module's
interface, delete the old tests on the shallow pieces it absorbed. Tests that
pin the internals turn every refactor into a test rewrite.

## Interface design moves

Moves that increase depth, roughly in order of how often they pay off:

1. **Merge a pass-through into its target.** If `OrderService.get` only calls `OrderRepository.get`, one of them is not earning its place.
2. **Pull complexity down.** When every caller does the same preparation before calling, move it inside.
3. **Make the common case one call.** Optional arguments with sensible defaults beat a builder sequence for 90% of callers.
4. **Define errors away.** Where a case can be handled sensibly inside (deleting something already gone, an empty range), handle it instead of raising.
5. **Accept dependencies instead of constructing them.** Pass the storage adapter in; do not instantiate it inside. This creates the seam tests need.
6. **Return values instead of mutating arguments.** A function that returns the discount is easier to test and to reason about than one that edits the cart.
7. **Group by knowledge, not by step.** Code that shares a decision belongs in one module even if it runs at different times.

## Shapes that look shallow but are fine

`module_depth.py` flags these; most can be accepted after a look:

| Shape | Why it is acceptable | When it is not |
|-------|---------------------|----------------|
| Adapter at a real seam | Its job is translation; depth lives in the module behind the port | It is the only adapter and nothing varies |
| Public facade of a package | Re-exports give callers one import site | It adds wrappers that change names but not behaviour |
| Data definitions (types, schemas, enums) | They are vocabulary, not behaviour | Behaviour is scattered in callers because the type has none |
| Framework-required handlers | The framework dictates the signature | The handler contains business rules that belong in a deep module |
| Test fixtures and builders | Excluded by default; included only with `--include-tests` | — |
