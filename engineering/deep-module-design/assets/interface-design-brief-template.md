# Interface Design Brief — <module concept>

Fill one brief per candidate design. Two or more briefs, each written under a
different constraint, go into the comparison.

## Shared context (identical across briefs)

- **Concept the module owns:** <one domain concept, glossary name>
- **Modules it absorbs:** <paths>
- **Callers today:** <list, with the most common caller marked>
- **Responsibilities that must be placed** (hidden or handed to callers):
  1. <responsibility>
  2. <responsibility>
- **Dependencies and categories:** <dependency — in-process / local stand-in / remote owned / third party>
- **Recorded decisions to respect:** <ids>

## This design

- **Constraint:** smallest surface | common caller first | flexible | port-based
- **Entry points:**

| Name | Parameters | Returns | Error modes | Ordering rules |
|------|-----------|---------|-------------|----------------|
| | | | | |

- **Configuration knobs:** <list, with defaults>
- **Hides:** <responsibilities kept inside>
- **Leaves to callers:** <responsibilities callers must handle>
- **Seams and adapters:** <seam — adapter 1, adapter 2>
- **Common caller's code:**

```
<the three to five lines the most common caller writes>
```

- **Invariants:** <what is always true after any call>
- **Where leverage is high / thin:** <one line each>

## Comparison entry

Copy the entry points, knobs, hides, leaks, seams and common-case call count
into the `designs` list of the comparison JSON and run `interface_compare.py`.
