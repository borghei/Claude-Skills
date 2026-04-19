import { Command } from "commander";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { listCommand } from "./commands/list.js";
import { searchCommand } from "./commands/search.js";
import { infoCommand } from "./commands/info.js";
import { addCommand } from "./commands/add.js";
import { createCommand } from "./commands/create.js";
import { updateCommand } from "./commands/update.js";
import { removeCommand } from "./commands/remove.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PKG_PATH = resolve(__dirname, "..", "package.json");

export async function run(argv) {
  const pkg = JSON.parse(await readFile(PKG_PATH, "utf8"));
  const program = new Command();

  program
    .name("claude-skills")
    .description("Install skills from the Claude Skills library into any AI assistant.")
    .version(pkg.version);

  program
    .command("list")
    .description("List all available skills, grouped by domain")
    .option("-d, --domain <domain>", "Filter to one domain")
    .option("--json", "Output as JSON")
    .action(listCommand);

  program
    .command("search <query>")
    .description("Search skills by name, description or tag")
    .option("--json", "Output as JSON")
    .action(searchCommand);

  program
    .command("info <skill>")
    .description("Show full detail for one skill")
    .option("--json", "Output as JSON")
    .action(infoCommand);

  program
    .command("add <skill>")
    .description("Install a skill into the detected (or chosen) AI assistant")
    .option("--to <target>", "Force target: claude, cursor, codex, gemini, copilot, windsurf, cline, aider, goose")
    .option("--dir <path>", "Install into a specific directory (overrides target detection)")
    .option("--force", "Overwrite if the skill's already installed")
    .action(addCommand);

  program
    .command("create <name>")
    .description("Scaffold a new skill from the template")
    .option("--domain <domain>", "Domain for the new skill", "engineering")
    .action(createCommand);

  program
    .command("update [skill]")
    .description("Update one installed skill, or all if none given")
    .action(updateCommand);

  program
    .command("remove <skill>")
    .description("Remove an installed skill")
    .action(removeCommand);

  await program.parseAsync(argv);
}
