import { test } from "node:test";
import assert from "node:assert/strict";
import { loadManifest, findSkill } from "../src/manifest.js";
import { detectTarget, getTarget, TARGET_NAMES } from "../src/detect.js";
import { mkdtemp, mkdir, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

test("manifest loads and has skills", async () => {
  const m = await loadManifest();
  assert.ok(m.skills.length > 0, "manifest has skills");
  assert.ok(m.schema_version, "has schema version");
  assert.ok(m.skill_count === m.skills.length, "count matches array length");
});

test("every skill has required fields", async () => {
  const m = await loadManifest();
  for (const s of m.skills) {
    assert.ok(typeof s.name === "string" && s.name.length > 0, `name missing: ${s.path}`);
    assert.ok(typeof s.domain === "string", `domain missing: ${s.name}`);
    assert.ok(typeof s.description === "string", `description not string: ${s.name}`);
    assert.ok(Array.isArray(s.files), `files not array: ${s.name}`);
    assert.ok(Array.isArray(s.tags), `tags not array: ${s.name}`);
  }
});

test("findSkill finds exact match", async () => {
  const skill = await findSkill("focused-fix");
  assert.equal(skill.name, "focused-fix");
});

test("findSkill throws NOT_FOUND for missing skill", async () => {
  await assert.rejects(() => findSkill("this-skill-does-not-exist-xyz"), {
    code: "NOT_FOUND",
  });
});

test("getTarget returns known target", () => {
  const t = getTarget("claude");
  assert.equal(t.name, "claude");
  assert.ok(t.installDir);
});

test("getTarget throws for unknown target", () => {
  assert.throws(() => getTarget("bogus-assistant"));
});

test("TARGET_NAMES includes all core targets", () => {
  for (const name of ["claude", "cursor", "codex", "gemini", "copilot"]) {
    assert.ok(TARGET_NAMES.includes(name), `${name} missing from TARGET_NAMES`);
  }
});

test("detectTarget finds claude when .claude/ exists", async () => {
  const dir = await mkdtemp(join(tmpdir(), "cs-test-"));
  await mkdir(join(dir, ".claude"));
  const target = await detectTarget(dir);
  assert.equal(target?.name, "claude");
});

test("detectTarget finds cursor via .cursorrules", async () => {
  const dir = await mkdtemp(join(tmpdir(), "cs-test-"));
  await writeFile(join(dir, ".cursorrules"), "# rules");
  const target = await detectTarget(dir);
  assert.equal(target?.name, "cursor");
});

test("detectTarget returns null for empty dir", async () => {
  const dir = await mkdtemp(join(tmpdir(), "cs-test-"));
  const target = await detectTarget(dir);
  assert.equal(target, null);
});
