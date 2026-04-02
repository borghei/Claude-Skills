#!/usr/bin/env python3
"""
cs — Claude Skills CLI

The main command-line interface for the universal AI skills library.
Search, browse, install, and inspect 200+ production-ready skills.

Usage:
    cs search <query>              Search skills by name, description, tags
    cs list                        List all skills grouped by domain
    cs install <skill> <target>    Copy a skill to your project
    cs info <skill-name>           Show detailed skill information
    cs stats                       Repository statistics dashboard
    cs doctor                      Health check all skills
    cs bundle <name> <target>      Install a pre-defined skill bundle
"""

import argparse
import json
import os
import re
import shutil
import sys
import textwrap
from pathlib import Path

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------------------

_NO_COLOR = False


def _supports_color():
    if _NO_COLOR:
        return False
    if os.environ.get("NO_COLOR"):
        return False
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    return True


def _c(code, text):
    if not _supports_color():
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(t):      return _c("1", t)
def dim(t):       return _c("2", t)
def green(t):     return _c("32", t)
def yellow(t):    return _c("33", t)
def blue(t):      return _c("34", t)
def magenta(t):   return _c("35", t)
def cyan(t):      return _c("36", t)
def red(t):       return _c("31", t)
def bg_blue(t):   return _c("44;97", t)
def bg_green(t):  return _c("42;97", t)
def bg_red(t):    return _c("41;97", t)


# ---------------------------------------------------------------------------
# Repo / catalog helpers
# ---------------------------------------------------------------------------

def find_repo_root():
    """Walk up from this script's location to find the directory containing skills.json."""
    candidate = Path(__file__).resolve().parent
    for _ in range(10):
        if (candidate / "skills.json").exists():
            return candidate
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    # Fallback: try cwd
    cwd = Path.cwd()
    for _ in range(10):
        if (cwd / "skills.json").exists():
            return cwd
        parent = cwd.parent
        if parent == cwd:
            break
        cwd = parent
    return None


def load_catalog(repo_root):
    """Load and return the skills.json catalog dict."""
    path = repo_root / "skills.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_bundles(repo_root):
    """Load bundles.json if it exists."""
    path = repo_root / "bundles.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_skill(catalog, name):
    """Find a skill entry by exact or fuzzy name match."""
    skills = catalog.get("skills", [])
    # Exact match
    for s in skills:
        if s["name"] == name:
            return s
    # Case-insensitive
    for s in skills:
        if s["name"].lower() == name.lower():
            return s
    # Substring
    matches = [s for s in skills if name.lower() in s["name"].lower()]
    if len(matches) == 1:
        return matches[0]
    return None


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def json_out(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def hr(char="-", width=60):
    print(dim(char * width))


def section(title):
    print()
    print(bold(title))
    hr()


# ---------------------------------------------------------------------------
# Command: search
# ---------------------------------------------------------------------------

def _score_skill(skill, terms):
    """Score a skill against search terms. Higher is better."""
    score = 0
    name = skill.get("name", "").lower()
    desc = skill.get("description", "").lower()
    tags = [t.lower() for t in skill.get("tags", [])]
    domain = skill.get("domain", "").lower()
    subdomain = skill.get("subdomain", "").lower()

    for term in terms:
        t = term.lower()
        # Name exact match (highest weight)
        if t == name:
            score += 100
        elif t in name:
            score += 40
        # Tag exact match
        if t in tags:
            score += 30
        # Domain/subdomain match
        if t == domain or t in domain:
            score += 20
        if t == subdomain or (subdomain and t in subdomain):
            score += 15
        # Description match
        if t in desc:
            score += 10
            # Bonus for appearing early in description
            idx = desc.index(t)
            if idx < 50:
                score += 5
    return score


def cmd_search(args, repo_root, catalog):
    query = " ".join(args.query)
    terms = query.lower().split()
    skills = catalog.get("skills", [])

    scored = []
    for s in skills:
        sc = _score_skill(s, terms)
        if sc > 0:
            scored.append((sc, s))

    scored.sort(key=lambda x: (-x[0], x[1]["name"]))

    if args.format == "json":
        json_out([{"score": sc, **s} for sc, s in scored])
        return 0

    if not scored:
        print(yellow(f"No skills matched '{query}'."))
        print(dim("Try broader terms or run: cs list --domain <domain>"))
        return 2

    print(bold(f"  Search results for '{query}'  ") + dim(f"  ({len(scored)} match{'es' if len(scored) != 1 else ''})"))
    print()

    for rank, (sc, s) in enumerate(scored[:25], 1):
        name_str = bold(cyan(s["name"]))
        domain_str = magenta(s["domain"])
        tools_str = dim(f"{s.get('tools', 0)} tools")
        print(f"  {dim(str(rank) + '.')} {name_str}  {domain_str}  {tools_str}")
        desc = s.get("description", "")
        if desc:
            short = textwrap.shorten(desc, width=80, placeholder="...")
            print(f"     {dim(short)}")
        tags = s.get("tags", [])
        if tags:
            print(f"     {dim('tags:')} {dim(', '.join(tags[:6]))}")
        print()

    if len(scored) > 25:
        print(dim(f"  ... and {len(scored) - 25} more. Use --format json for full results."))

    return 0


# ---------------------------------------------------------------------------
# Command: list
# ---------------------------------------------------------------------------

def cmd_list(args, repo_root, catalog):
    skills = catalog.get("skills", [])
    domain_filter = args.domain.lower() if args.domain else None

    if domain_filter:
        skills = [s for s in skills if s.get("domain", "").lower() == domain_filter]
        if not skills:
            print(yellow(f"No skills found in domain '{args.domain}'."))
            avail = sorted(catalog.get("domains", {}).keys())
            print(dim(f"Available domains: {', '.join(avail)}"))
            return 2

    # Sort
    sort_key = args.sort or "domain"
    if sort_key == "name":
        skills.sort(key=lambda s: s["name"])
    elif sort_key == "tools":
        skills.sort(key=lambda s: (-s.get("tools", 0), s["name"]))
    else:
        skills.sort(key=lambda s: (s.get("domain", ""), s["name"]))

    if args.format == "json":
        json_out(skills)
        return 0

    # Group by domain
    groups = {}
    for s in skills:
        d = s.get("domain", "other")
        groups.setdefault(d, []).append(s)

    total = 0
    for domain in sorted(groups.keys()):
        entries = groups[domain]
        total += len(entries)
        domain_info = catalog.get("domains", {}).get(domain, {})
        tool_count = domain_info.get("tools", sum(s.get("tools", 0) for s in entries))
        print()
        print(f"  {bg_blue(f' {domain} ')}  {dim(f'{len(entries)} skills, {tool_count} tools')}")
        print()
        for s in entries:
            tools_str = dim(f"({s.get('tools', 0)} tools)")
            print(f"    {cyan(s['name'])}  {tools_str}")

    print()
    hr()
    print(f"  {bold('Total:')} {total} skills across {len(groups)} domains")
    return 0


# ---------------------------------------------------------------------------
# Command: install
# ---------------------------------------------------------------------------

def cmd_install(args, repo_root, catalog):
    skill_name = args.skill_path
    target = Path(args.target_dir).resolve()

    # Resolve skill from catalog
    skill = resolve_skill(catalog, skill_name)
    if not skill:
        # Try as a direct path
        direct = repo_root / skill_name
        if not direct.exists():
            print(red(f"Skill '{skill_name}' not found in catalog or as path."))
            return 2
        skill_dir = direct
        skill_display = skill_name
    else:
        # skill["path"] points to SKILL.md; parent is the skill dir
        skill_dir = repo_root / Path(skill["path"]).parent
        skill_display = skill["name"]

    if not skill_dir.is_dir():
        print(red(f"Skill directory not found: {skill_dir}"))
        return 1

    dest = target / skill_dir.name
    if dest.exists():
        if args.format != "json":
            print(yellow(f"Target already exists: {dest}"))
            print(dim("Use --force (not yet implemented) to overwrite."))
        return 1

    # Copy
    items_copied = []
    dest.mkdir(parents=True, exist_ok=True)

    for item_name in ["SKILL.md", "scripts", "references", "assets"]:
        src = skill_dir / item_name
        if src.exists():
            dst = dest / item_name
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            items_copied.append(item_name)

    # If nothing matched the standard layout, copy everything
    if not items_copied:
        shutil.rmtree(dest)
        shutil.copytree(skill_dir, dest)
        items_copied = ["(entire directory)"]

    if args.format == "json":
        json_out({
            "installed": skill_display,
            "source": str(skill_dir),
            "destination": str(dest),
            "items": items_copied,
        })
        return 0

    print(green(f"  Installed '{skill_display}' -> {dest}"))
    print()
    for item in items_copied:
        print(f"    {dim('+')} {item}")
    print()
    print(dim("  Tip: read SKILL.md for usage instructions."))
    return 0


# ---------------------------------------------------------------------------
# Command: info
# ---------------------------------------------------------------------------

def cmd_info(args, repo_root, catalog):
    skill = resolve_skill(catalog, args.skill_name)
    if not skill:
        print(red(f"Skill '{args.skill_name}' not found."))
        suggestions = []
        for s in catalog.get("skills", []):
            if args.skill_name.lower() in s["name"].lower():
                suggestions.append(s["name"])
        if suggestions:
            print(dim(f"Did you mean: {', '.join(suggestions[:5])}?"))
        return 2

    if args.format == "json":
        # Enrich with filesystem data
        skill_dir = repo_root / Path(skill["path"]).parent
        enriched = dict(skill)
        enriched["scripts_list"] = _list_dir_files(skill_dir / "scripts")
        enriched["references_list"] = _list_dir_files(skill_dir / "references")
        enriched["assets_list"] = _list_dir_files(skill_dir / "assets")
        json_out(enriched)
        return 0

    skill_dir = repo_root / Path(skill["path"]).parent

    print()
    sname = skill["name"]
    print(f"  {bg_blue(f' {sname} ')}")
    print()
    print(f"  {bold('Domain:')}      {magenta(skill.get('domain', 'n/a'))}")
    if skill.get("subdomain"):
        print(f"  {bold('Subdomain:')}   {skill['subdomain']}")
    print(f"  {bold('Version:')}     {skill.get('version', 'n/a')}")
    print(f"  {bold('Tools:')}       {skill.get('tools', 0)}")
    print(f"  {bold('Path:')}        {dim(str(skill_dir.relative_to(repo_root)))}")
    print()

    desc = skill.get("description", "")
    if desc:
        print(f"  {bold('Description:')}")
        for line in textwrap.wrap(desc, width=72):
            print(f"    {line}")
        print()

    tags = skill.get("tags", [])
    if tags:
        print(f"  {bold('Tags:')} {', '.join(cyan(t) for t in tags)}")
        print()

    # Scripts
    scripts = _list_dir_files(skill_dir / "scripts")
    if scripts:
        print(f"  {bold('Scripts:')}")
        for s in scripts:
            print(f"    {green(s)}")
        print()

    # References
    refs = _list_dir_files(skill_dir / "references")
    if refs:
        print(f"  {bold('References:')}")
        for r in refs:
            print(f"    {dim(r)}")
        print()

    # Related skills (same domain)
    related = [s for s in catalog.get("skills", [])
               if s["domain"] == skill["domain"] and s["name"] != skill["name"]]
    if related:
        print(f"  {bold('Related skills')} {dim('(same domain)')}:")
        for r in related[:8]:
            print(f"    {cyan(r['name'])}")
        if len(related) > 8:
            print(f"    {dim(f'... and {len(related) - 8} more')}")
        print()

    return 0


def _list_dir_files(directory):
    """List files in a directory, returning relative names. Skips __pycache__."""
    p = Path(directory)
    if not p.is_dir():
        return []
    files = []
    for f in sorted(p.rglob("*")):
        if f.is_file() and not f.name.startswith(".") and "__pycache__" not in f.parts:
            files.append(str(f.relative_to(p)))
    return files


# ---------------------------------------------------------------------------
# Command: stats
# ---------------------------------------------------------------------------

def cmd_stats(args, repo_root, catalog):
    domains = catalog.get("domains", {})
    skills = catalog.get("skills", [])
    total_skills = catalog.get("total_skills", len(skills))
    total_tools = sum(d.get("tools", 0) for d in domains.values())

    # Count agents
    agents_dir = repo_root / "agents"
    agent_count = 0
    if agents_dir.is_dir():
        agent_count = sum(1 for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith("."))
    claude_agents_dir = repo_root / ".claude" / "agents"
    if claude_agents_dir.is_dir():
        agent_count += sum(1 for f in claude_agents_dir.iterdir() if f.is_file() and f.suffix == ".md")

    # Count commands
    commands_dir = repo_root / ".claude" / "commands"
    command_count = 0
    if commands_dir.is_dir():
        command_count = sum(1 for f in commands_dir.rglob("*.md"))

    if args.format == "json":
        json_out({
            "version": catalog.get("version", "unknown"),
            "total_skills": total_skills,
            "total_tools": total_tools,
            "total_agents": agent_count,
            "total_commands": command_count,
            "domains": {
                name: {"skills": d.get("count", 0), "tools": d.get("tools", 0)}
                for name, d in domains.items()
            },
        })
        return 0

    print()
    print(f"  {bg_blue(' Claude Skills Library ')}")
    print(f"  {dim('Version ' + catalog.get('version', 'unknown'))}")
    print()
    hr("=", 56)
    print(f"  {bold('Skills:')}    {green(str(total_skills)):>6}     {bold('Agents:')}   {green(str(agent_count)):>4}")
    print(f"  {bold('Tools:')}     {green(str(total_tools)):>6}     {bold('Commands:')} {green(str(command_count)):>4}")
    print(f"  {bold('Domains:')}   {green(str(len(domains))):>6}")
    hr("=", 56)
    print()

    # Per-domain table
    print(f"  {'Domain':<24} {'Skills':>7} {'Tools':>7}")
    hr("-", 42)
    for name in sorted(domains.keys()):
        d = domains[name]
        bar_len = min(d.get("count", 0), 30)
        bar = cyan("█" * bar_len)
        print(f"  {name:<24} {d.get('count', 0):>7} {d.get('tools', 0):>7}  {bar}")
    hr("-", 42)
    print(f"  {'TOTAL':<24} {bold(str(total_skills)):>7} {bold(str(total_tools)):>7}")
    print()

    return 0


# ---------------------------------------------------------------------------
# Command: doctor
# ---------------------------------------------------------------------------

def cmd_doctor(args, repo_root, catalog):
    skills = catalog.get("skills", [])
    issues = []
    checked = 0
    ok_count = 0

    for s in skills:
        checked += 1
        skill_path = repo_root / s.get("path", "")
        skill_dir = skill_path.parent if skill_path.suffix == ".md" else skill_path
        name = s["name"]

        # Check SKILL.md exists
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            issues.append({"skill": name, "level": "error", "msg": "Missing SKILL.md"})
        else:
            ok_count += 1

        # Check scripts compile (syntax check)
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.is_dir():
            for py in scripts_dir.glob("*.py"):
                try:
                    with open(py, "r", encoding="utf-8") as f:
                        compile(f.read(), str(py), "exec")
                    ok_count += 1
                except SyntaxError as e:
                    issues.append({
                        "skill": name,
                        "level": "error",
                        "msg": f"Syntax error in {py.name}: {e.msg} (line {e.lineno})",
                    })

        # Check references exist if declared
        if s.get("has_references"):
            refs_dir = skill_dir / "references"
            if not refs_dir.is_dir() or not any(refs_dir.iterdir()):
                issues.append({"skill": name, "level": "warn", "msg": "has_references=true but references/ empty or missing"})

        # Check assets exist if declared
        if s.get("has_assets"):
            assets_dir = skill_dir / "assets"
            if not assets_dir.is_dir() or not any(assets_dir.iterdir()):
                issues.append({"skill": name, "level": "warn", "msg": "has_assets=true but assets/ empty or missing"})

    errors = [i for i in issues if i["level"] == "error"]
    warns = [i for i in issues if i["level"] == "warn"]

    if args.format == "json":
        json_out({
            "checked": checked,
            "ok": ok_count,
            "errors": len(errors),
            "warnings": len(warns),
            "issues": issues,
        })
        return 1 if errors else 0

    print()
    print(f"  {bg_blue(' Doctor — Health Check ')}")
    print()
    print(f"  Checked {bold(str(checked))} skills, {bold(str(ok_count))} checks passed")
    print()

    if errors:
        err_label = f" {len(errors)} ERROR{'S' if len(errors) != 1 else ''} "
        print(f"  {bg_red(err_label)}")
        for i in errors:
            print(f"    {red('x')} {bold(i['skill'])}: {i['msg']}")
        print()

    if warns:
        warn_label = f"{len(warns)} warning{'s' if len(warns) != 1 else ''}"
        print(f"  {yellow(warn_label)}")
        for i in warns:
            print(f"    {yellow('!')} {i['skill']}: {dim(i['msg'])}")
        print()

    if not issues:
        print(f"  {bg_green(' ALL CLEAR ')}  No issues found.")
        print()

    return 1 if errors else 0


# ---------------------------------------------------------------------------
# Command: bundle
# ---------------------------------------------------------------------------

def cmd_bundle(args, repo_root, catalog):
    bundles = load_bundles(repo_root)

    if not bundles:
        # Generate some sensible defaults from catalog data
        bundles = _default_bundles(catalog)

    bundle_name = args.bundle_name
    target = Path(args.target_dir).resolve()

    available = bundles.get("bundles", bundles)
    if bundle_name == "list":
        if args.format == "json":
            json_out({"bundles": list(available.keys())})
            return 0
        print()
        print(f"  {bold('Available bundles:')}")
        print()
        for bname, bdata in available.items():
            desc = bdata.get("description", "") if isinstance(bdata, dict) else ""
            skills_list = bdata.get("skills", bdata) if isinstance(bdata, dict) else bdata
            count = len(skills_list) if isinstance(skills_list, list) else 0
            print(f"    {cyan(bname):<28} {dim(f'{count} skills')}  {dim(desc)}")
        print()
        return 0

    if bundle_name not in available:
        print(red(f"Bundle '{bundle_name}' not found."))
        print(dim(f"Available: {', '.join(available.keys())}"))
        print(dim("Run: cs bundle list <any-dir> to see all bundles."))
        return 2

    bdata = available[bundle_name]
    skill_names = bdata.get("skills", bdata) if isinstance(bdata, dict) else bdata
    if not isinstance(skill_names, list):
        print(red("Invalid bundle format."))
        return 1

    installed = []
    failed = []
    for sname in skill_names:
        skill = resolve_skill(catalog, sname)
        if not skill:
            failed.append(sname)
            continue
        skill_dir = repo_root / Path(skill["path"]).parent
        dest = target / skill_dir.name
        if dest.exists():
            failed.append(f"{sname} (already exists)")
            continue
        try:
            dest.mkdir(parents=True, exist_ok=True)
            for item_name in ["SKILL.md", "scripts", "references", "assets"]:
                src = skill_dir / item_name
                if src.exists():
                    dst = dest / item_name
                    if src.is_dir():
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
            installed.append(sname)
        except Exception as e:
            failed.append(f"{sname} ({e})")

    if args.format == "json":
        json_out({"bundle": bundle_name, "installed": installed, "failed": failed})
        return 1 if failed else 0

    print()
    print(f"  {bg_green(f' Bundle: {bundle_name} ')}")
    print()
    for s in installed:
        print(f"    {green('+')} {s}")
    for s in failed:
        print(f"    {red('x')} {s}")
    print()
    print(f"  {bold(str(len(installed)))} installed, {len(failed)} skipped -> {target}")
    return 1 if failed and not installed else 0


def _default_bundles(catalog):
    """Generate default bundles from catalog when bundles.json doesn't exist."""
    skills = catalog.get("skills", [])
    by_domain = {}
    for s in skills:
        by_domain.setdefault(s["domain"], []).append(s["name"])

    bundles = {}
    # One bundle per domain
    for domain, names in by_domain.items():
        bundles[domain] = {
            "description": f"All {domain} skills",
            "skills": names,
        }
    # Starter bundle
    starter_domains = ["engineering", "product-team", "project-management"]
    starter_skills = []
    for d in starter_domains:
        starter_skills.extend(by_domain.get(d, [])[:5])
    bundles["starter"] = {
        "description": "Top 5 skills from engineering, product, and PM",
        "skills": starter_skills,
    }
    # Full bundle
    bundles["all"] = {
        "description": "Every skill in the library",
        "skills": [s["name"] for s in skills],
    }
    return bundles


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="cs",
        description="Claude Skills CLI — search, browse, install, and manage AI skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              cs search "api design"       Search for API-related skills
              cs list --domain engineering  List engineering skills
              cs info churn-prevention      Show skill details
              cs install seo-auditor .      Install a skill to current dir
              cs stats                      Show library dashboard
              cs doctor                     Run health checks
              cs bundle starter ./skills    Install the starter bundle
        """),
    )
    parser.add_argument("--version", action="version", version=f"cs {__version__}")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # search
    p_search = sub.add_parser("search", help="Search skills by name, description, or tags")
    p_search.add_argument("query", nargs="+", help="Search terms")

    # list
    p_list = sub.add_parser("list", help="List all skills grouped by domain")
    p_list.add_argument("--domain", "-d", help="Filter by domain")
    p_list.add_argument("--sort", choices=["name", "tools", "domain"], default="domain",
                        help="Sort order (default: domain)")

    # install
    p_install = sub.add_parser("install", help="Copy a skill to a target directory")
    p_install.add_argument("skill_path", help="Skill name or relative path")
    p_install.add_argument("target_dir", help="Target directory")

    # info
    p_info = sub.add_parser("info", help="Show detailed information about a skill")
    p_info.add_argument("skill_name", help="Skill name")

    # stats
    sub.add_parser("stats", help="Show repository statistics dashboard")

    # doctor
    sub.add_parser("doctor", help="Health check: verify all skills are well-formed")

    # bundle
    p_bundle = sub.add_parser("bundle", help="Install a pre-defined bundle of skills")
    p_bundle.add_argument("bundle_name", help="Bundle name (or 'list' to show available)")
    p_bundle.add_argument("target_dir", help="Target directory")

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global _NO_COLOR
    parser = build_parser()
    args = parser.parse_args()

    if args.no_color:
        _NO_COLOR = True

    if not args.command:
        parser.print_help()
        return 0

    repo_root = find_repo_root()
    if repo_root is None:
        print(red("Error: Could not find skills.json. Are you inside the Claude Skills repo?"),
              file=sys.stderr)
        return 1

    catalog = load_catalog(repo_root)

    dispatch = {
        "search": cmd_search,
        "list": cmd_list,
        "install": cmd_install,
        "info": cmd_info,
        "stats": cmd_stats,
        "doctor": cmd_doctor,
        "bundle": cmd_bundle,
    }

    handler = dispatch.get(args.command)
    if handler:
        return handler(args, repo_root, catalog)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
