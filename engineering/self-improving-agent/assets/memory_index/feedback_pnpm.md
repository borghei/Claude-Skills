---
name: Use pnpm, not npm
description: Package installs in this repo go through pnpm
type: feedback
---
Run `pnpm install` and `pnpm add`. `npm install` rewrites the lockfile format and breaks CI.
Seen three times: two install fixes and one CI failure.
