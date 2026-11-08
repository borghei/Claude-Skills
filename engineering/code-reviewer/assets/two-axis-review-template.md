# Review: <branch or PR title>

**Base:** `<base ref>` (`<base sha>`)  ·  **Head:** `<head sha>`  ·  **Diff:** `git diff <base>...<head>`
**Commits:** <n>  ·  **Files:** <n>  ·  **Lines changed:** <n>
**Spec source:** <path, issue link, or "none found">
**Standards sources:** <files>

## Standards

<Report from the standards pass, lightly cleaned. One finding per bullet.>

- `<file:line>` — <what is wrong>. Rule: <source file> — "<rule>". **Hard** | **Judgement**

**Summary:** <n> findings; most serious: <one line>.

## Spec

<Report from the spec pass. Quote the spec line for every finding.>

### Missing or partial
- "<spec line>" — <what is missing>

### Not asked for
- `<file:line>` — <behaviour>. Bucket: enabling | unrequested | speculative

### Built wrongly
- "<spec line>" — <how the implementation differs>

**Summary:** <n> findings; most serious: <one line>.

## Overlaps

- <finding raised by both passes, listed once here>

## Verdict

**<Approve | Request changes | Block>** — <one sentence naming the deciding finding(s)>
