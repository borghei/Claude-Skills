#!/usr/bin/env python3
"""
Skill Installer - Install individual skills from Claude Skills Library

Installs a single skill (or one per domain group) into your project with
optional auto-update support. Supports Claude Code, Cursor, VS Code/Copilot,
Codex, and generic project layouts.

Usage:
    python skill-installer.py list                              # List all skills
    python skill-installer.py list --group engineering-team     # List skills in a group
    python skill-installer.py install content-creator           # Install a skill
    python skill-installer.py install senior-fullstack --agent cursor
    python skill-installer.py install ceo-advisor --auto-update # Enable auto-updates
    python skill-installer.py update                            # Update all installed skills
    python skill-installer.py update content-creator            # Update specific skill
    python skill-installer.py status                            # Show installed skills
    python skill-installer.py uninstall content-creator         # Remove a skill
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_URL = "https://github.com/borghei/Claude-Skills"
MANIFEST_FILE = ".claude-skills.json"

AGENT_DIRS = {
    "claude": Path.home() / ".claude" / "skills",
    "cursor": Path(".cursor") / "skills",
    "vscode": Path(".github") / "skills",
    "copilot": Path(".github") / "skills",
    "codex": Path.home() / ".codex" / "skills",
    "goose": Path.home() / ".config" / "goose" / "skills",
    "project": Path(".skills"),
}

DEFAULT_AGENT = "project"


def find_repo_root():
    """Find the Claude-Skills repository root (where this script lives)."""
    script_dir = Path(__file__).resolve().parent
    # scripts/ lives one level below repo root
    repo_root = script_dir.parent
    if (repo_root / "CLAUDE.md").exists():
        return repo_root
    return None


def discover_skills(repo_root):
    """Discover all skills in the repository, grouped by domain."""
    skills = {}
    for skill_md in sorted(repo_root.rglob("SKILL.md")):
        rel = skill_md.relative_to(repo_root)
        parts = rel.parts
        # Skip sample/test skills and nested SKILL.md (e.g., assets/sample-skill)
        if "assets" in parts or "node_modules" in parts or ".git" in parts:
            continue
        if len(parts) < 2:
            continue
        group = parts[0]
        skill_name = parts[1]
        skill_dir = repo_root / group / skill_name
        # Parse frontmatter for description
        description = ""
        try:
            text = skill_md.read_text(encoding="utf-8")
            if text.startswith("---"):
                end = text.find("---", 3)
                if end > 0:
                    fm = text[3:end]
                    for line in fm.splitlines():
                        if line.strip().startswith("description:"):
                            description = line.split(":", 1)[1].strip().strip(">-").strip()
                            break
        except Exception:
            pass
        if group not in skills:
            skills[group] = {}
        skills[group][skill_name] = {
            "path": str(skill_dir.relative_to(repo_root)),
            "description": description[:120] if description else "",
            "has_scripts": (skill_dir / "scripts").is_dir()
            and any((skill_dir / "scripts").glob("*.py")),
            "has_references": (skill_dir / "references").is_dir()
            and any((skill_dir / "references").glob("*.md")),
            "has_assets": (skill_dir / "assets").is_dir()
            and any(p for p in (skill_dir / "assets").iterdir() if p.name != ".gitkeep"),
        }
    return skills


def load_manifest(target_dir):
    """Load the installed skills manifest."""
    manifest_path = Path(target_dir) / MANIFEST_FILE
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"installed": {}, "auto_update": False, "source": REPO_URL}


def save_manifest(target_dir, manifest):
    """Save the installed skills manifest."""
    manifest_path = Path(target_dir) / MANIFEST_FILE
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def get_target_dir(agent):
    """Get the target installation directory for the agent."""
    return AGENT_DIRS.get(agent, AGENT_DIRS[DEFAULT_AGENT])


def copy_skill(repo_root, skill_path, target_dir):
    """Copy a skill directory to the target location."""
    src = repo_root / skill_path
    # Skill name is the last component of the path
    skill_name = Path(skill_path).name
    dest = Path(target_dir) / skill_name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        src,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )
    return dest


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_list(args, repo_root):
    """List available skills."""
    skills = discover_skills(repo_root)
    if args.group:
        if args.group not in skills:
            print(f"Error: Unknown group '{args.group}'", file=sys.stderr)
            print(f"Available groups: {', '.join(sorted(skills.keys()))}", file=sys.stderr)
            sys.exit(1)
        groups = {args.group: skills[args.group]}
    else:
        groups = skills

    if args.json:
        print(json.dumps(groups, indent=2))
        return

    total = 0
    for group_name in sorted(groups.keys()):
        group_skills = groups[group_name]
        print(f"\n  {group_name} ({len(group_skills)} skills)")
        print(f"  {'─' * 50}")
        for name in sorted(group_skills.keys()):
            info = group_skills[name]
            tier = []
            if info["has_scripts"]:
                tier.append("scripts")
            if info["has_references"]:
                tier.append("refs")
            if info["has_assets"]:
                tier.append("assets")
            tier_str = ", ".join(tier) if tier else "docs"
            desc = info["description"][:60] + "..." if len(info["description"]) > 60 else info["description"]
            print(f"    {name:<35} [{tier_str}]")
            if desc:
                print(f"      {desc}")
            total += 1

    print(f"\n  Total: {total} skills across {len(groups)} groups")
    print(f"\n  Install:  python {sys.argv[0]} install <skill-name>")
    print(f"  Details:  python {sys.argv[0]} list --group <group-name>")


def cmd_install(args, repo_root):
    """Install a skill into the target directory."""
    skill_name = args.skill_name
    agent = args.agent or DEFAULT_AGENT
    target_dir = get_target_dir(agent)
    auto_update = args.auto_update

    # Find the skill
    skills = discover_skills(repo_root)
    found_group = None
    found_info = None
    for group, group_skills in skills.items():
        if skill_name in group_skills:
            found_group = group
            found_info = group_skills[skill_name]
            break

    if not found_info:
        print(f"Error: Skill '{skill_name}' not found.", file=sys.stderr)
        # Suggest similar names
        all_names = [n for g in skills.values() for n in g.keys()]
        suggestions = [n for n in all_names if skill_name.lower() in n.lower()]
        if suggestions:
            print(f"Did you mean: {', '.join(suggestions[:5])}?", file=sys.stderr)
        sys.exit(1)

    # Check one-per-group enforcement
    manifest = load_manifest(target_dir)
    for installed_name, installed_info in manifest.get("installed", {}).items():
        if installed_info.get("group") == found_group and installed_name != skill_name:
            if not args.force:
                print(
                    f"Warning: Group '{found_group}' already has '{installed_name}' installed.",
                    file=sys.stderr,
                )
                print(
                    f"Use --force to install multiple skills from the same group,",
                    file=sys.stderr,
                )
                print(
                    f"or uninstall '{installed_name}' first.",
                    file=sys.stderr,
                )
                sys.exit(1)

    # Install
    dest = copy_skill(repo_root, found_info["path"], target_dir)

    # Update manifest
    now = datetime.now(timezone.utc).isoformat()
    manifest["installed"][skill_name] = {
        "group": found_group,
        "path": found_info["path"],
        "installed_at": now,
        "updated_at": now,
        "auto_update": auto_update,
    }
    if auto_update:
        manifest["auto_update"] = True
    save_manifest(target_dir, manifest)

    if args.json:
        print(
            json.dumps(
                {
                    "success": True,
                    "skill": skill_name,
                    "group": found_group,
                    "target": str(dest),
                    "auto_update": auto_update,
                },
                indent=2,
            )
        )
    else:
        print(f"\n  Installed '{skill_name}' from {found_group}")
        print(f"  Target:      {dest}")
        print(f"  Auto-update: {'enabled' if auto_update else 'disabled'}")
        if auto_update:
            print(f"\n  To update:   python {sys.argv[0]} update")
            print(f"  Or run the GitHub Action: skill-auto-update.yml")
        print(f"\n  One skill per group policy active.")
        print(f"  Use --force to override if needed.")


def cmd_update(args, repo_root):
    """Update installed skills from the repository."""
    agent = args.agent or DEFAULT_AGENT
    target_dir = get_target_dir(agent)
    manifest = load_manifest(target_dir)

    if not manifest.get("installed"):
        print("No skills installed. Use 'install' first.", file=sys.stderr)
        sys.exit(1)

    skill_filter = args.skill_name
    updated = []
    skipped = []

    for skill_name, info in manifest["installed"].items():
        if skill_filter and skill_name != skill_filter:
            continue
        if not info.get("auto_update", False) and not skill_filter:
            skipped.append(skill_name)
            continue

        skill_path = info.get("path")
        src = repo_root / skill_path
        if not src.exists():
            skipped.append(skill_name)
            continue

        copy_skill(repo_root, skill_path, target_dir)
        info["updated_at"] = datetime.now(timezone.utc).isoformat()
        updated.append(skill_name)

    save_manifest(target_dir, manifest)

    if args.json:
        print(json.dumps({"updated": updated, "skipped": skipped}, indent=2))
    else:
        if updated:
            print(f"\n  Updated {len(updated)} skill(s):")
            for name in updated:
                print(f"    - {name}")
        if skipped:
            print(f"\n  Skipped {len(skipped)} (auto-update disabled or not found):")
            for name in skipped:
                print(f"    - {name}")
        if not updated and not skipped:
            print(f"  Skill '{skill_filter}' not found in installed list.")


def cmd_status(args, repo_root):
    """Show installed skills status."""
    agent = args.agent or DEFAULT_AGENT
    target_dir = get_target_dir(agent)
    manifest = load_manifest(target_dir)

    installed = manifest.get("installed", {})
    if not installed:
        print("No skills installed.", file=sys.stderr)
        sys.exit(0)

    if args.json:
        print(json.dumps(manifest, indent=2))
        return

    print(f"\n  Installed Skills ({len(installed)})")
    print(f"  {'─' * 55}")
    print(f"  {'Skill':<30} {'Group':<20} {'Auto-Update'}")
    print(f"  {'─' * 55}")
    for name in sorted(installed.keys()):
        info = installed[name]
        auto = "yes" if info.get("auto_update") else "no"
        group = info.get("group", "unknown")
        print(f"  {name:<30} {group:<20} {auto}")

    print(f"\n  Target: {target_dir}")
    print(f"  Source: {manifest.get('source', REPO_URL)}")


def cmd_uninstall(args, repo_root):
    """Remove an installed skill."""
    skill_name = args.skill_name
    agent = args.agent or DEFAULT_AGENT
    target_dir = get_target_dir(agent)
    manifest = load_manifest(target_dir)

    if skill_name not in manifest.get("installed", {}):
        print(f"Skill '{skill_name}' is not installed.", file=sys.stderr)
        sys.exit(1)

    # Remove directory
    dest = Path(target_dir) / skill_name
    if dest.exists():
        shutil.rmtree(dest)

    # Update manifest
    del manifest["installed"][skill_name]
    save_manifest(target_dir, manifest)

    if args.json:
        print(json.dumps({"success": True, "uninstalled": skill_name}, indent=2))
    else:
        print(f"\n  Uninstalled '{skill_name}'")
        print(f"  Removed: {dest}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Install individual skills from Claude Skills Library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                              List all available skills
  %(prog)s list --group engineering-team     List engineering skills
  %(prog)s install content-creator           Install content-creator skill
  %(prog)s install senior-fullstack --agent cursor --auto-update
  %(prog)s update                            Update all auto-update skills
  %(prog)s status                            Show installed skills
  %(prog)s uninstall content-creator         Remove a skill
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list
    p_list = subparsers.add_parser("list", help="List available skills")
    p_list.add_argument("--group", "-g", help="Filter by domain group")
    p_list.add_argument("--json", action="store_true", help="Output JSON")

    # install
    p_install = subparsers.add_parser("install", help="Install a skill")
    p_install.add_argument("skill_name", help="Name of the skill to install")
    p_install.add_argument(
        "--agent",
        "-a",
        choices=list(AGENT_DIRS.keys()),
        help=f"Target agent (default: {DEFAULT_AGENT})",
    )
    p_install.add_argument(
        "--auto-update",
        action="store_true",
        help="Enable automatic updates for this skill",
    )
    p_install.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Allow multiple skills from the same group",
    )
    p_install.add_argument("--json", action="store_true", help="Output JSON")

    # update
    p_update = subparsers.add_parser("update", help="Update installed skills")
    p_update.add_argument("skill_name", nargs="?", help="Specific skill to update (updates all if omitted)")
    p_update.add_argument(
        "--agent",
        "-a",
        choices=list(AGENT_DIRS.keys()),
        help=f"Target agent (default: {DEFAULT_AGENT})",
    )
    p_update.add_argument("--json", action="store_true", help="Output JSON")

    # status
    p_status = subparsers.add_parser("status", help="Show installed skills")
    p_status.add_argument(
        "--agent",
        "-a",
        choices=list(AGENT_DIRS.keys()),
        help=f"Target agent (default: {DEFAULT_AGENT})",
    )
    p_status.add_argument("--json", action="store_true", help="Output JSON")

    # uninstall
    p_uninstall = subparsers.add_parser("uninstall", help="Remove a skill")
    p_uninstall.add_argument("skill_name", help="Name of the skill to remove")
    p_uninstall.add_argument(
        "--agent",
        "-a",
        choices=list(AGENT_DIRS.keys()),
        help=f"Target agent (default: {DEFAULT_AGENT})",
    )
    p_uninstall.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    repo_root = find_repo_root()
    if not repo_root:
        print("Error: Cannot find Claude-Skills repository root.", file=sys.stderr)
        print("Run this script from inside the repository.", file=sys.stderr)
        sys.exit(1)

    commands = {
        "list": cmd_list,
        "install": cmd_install,
        "update": cmd_update,
        "status": cmd_status,
        "uninstall": cmd_uninstall,
    }

    commands[args.command](args, repo_root)


if __name__ == "__main__":
    main()
