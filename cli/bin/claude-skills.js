#!/usr/bin/env node
import { run } from "../src/index.js";

run(process.argv).catch((err) => {
  process.stderr.write(`\nclaude-skills: ${err.message}\n`);
  if (process.env.CLAUDE_SKILLS_DEBUG) {
    process.stderr.write(`${err.stack}\n`);
  }
  process.exit(1);
});
