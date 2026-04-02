#!/usr/bin/env python3
"""
generate_site.py — Static site generator for Claude Skills.

Reads skills.json and SKILL.md files to generate a complete static website
in the site/ directory with skill pages, domain pages, agents catalog,
commands catalog, sitemap, robots.txt, and llms.txt.

Usage:
    python scripts/generate_site.py                          # Full site
    python scripts/generate_site.py --skill senior-backend   # One skill
    python scripts/generate_site.py --domain engineering      # One domain
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from html import escape

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SKILLS_JSON = REPO_ROOT / "skills.json"
SITE_DIR = REPO_ROOT / "site"
BASE_URL = "https://borghei.github.io/Claude-Skills"
GITHUB_URL = "https://github.com/borghei/Claude-Skills"

# ---------------------------------------------------------------------------
# Domain display metadata
# ---------------------------------------------------------------------------

DOMAIN_META = {
    "engineering":        {"label": "Engineering",        "icon": "&#x1F528;",          "desc": "Architecture, fullstack, AI/ML, security, and infrastructure"},
    "marketing":          {"label": "Marketing",          "icon": "&#x1F4E3;",          "desc": "Content creation, SEO, demand gen, campaign analytics"},
    "c-level-advisor":    {"label": "C-Level Advisory",   "icon": "&#x1F451;",          "desc": "CEO, CTO, CFO, and CISO strategic advisory"},
    "project-management": {"label": "Project Management", "icon": "&#x1F4CB;",          "desc": "Discovery, execution, Atlassian MCP integration"},
    "business-growth":    {"label": "Business & Growth",  "icon": "&#x1F4C8;",          "desc": "Customer success, sales engineering, revenue ops"},
    "ra-qm-team":        {"label": "Compliance",         "icon": "&#x1F6E1;&#xFE0F;",  "desc": "ISO 13485, MDR, FDA, SOC 2, GDPR, EU AI Act, NIS2"},
    "data-analytics":     {"label": "Data Analytics",     "icon": "&#x1F4CA;",          "desc": "BI, ML ops, analytics engineering, data pipelines"},
    "product-team":       {"label": "Product",            "icon": "&#x1F4E6;",          "desc": "RICE scoring, OKRs, user stories, UX research"},
    "sales-success":      {"label": "Sales",              "icon": "&#x1F4B0;",          "desc": "Account executive, sales ops, solutions architect"},
    "hr-operations":      {"label": "HR Operations",      "icon": "&#x1F465;",          "desc": "Talent acquisition, people analytics, HR business partner"},
    "finance":            {"label": "Finance",            "icon": "&#x1F4B5;",          "desc": "DCF valuation, budgeting, forecasting, ratio analysis"},
}

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_catalog():
    """Load skills.json catalog."""
    with open(SKILLS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def load_skill_md(skill_path):
    """Read a SKILL.md file and return its raw text, or empty string."""
    full = REPO_ROOT / skill_path
    if full.exists():
        return full.read_text(encoding="utf-8")
    return ""


def parse_tools_section(md_text):
    """Extract tool names and descriptions from Tools Overview section."""
    tools = []
    in_section = False
    for line in md_text.splitlines():
        if re.match(r"^##\s+Tools Overview", line, re.I):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line) and not re.match(r"^###", line):
            break
        if in_section and re.match(r"^###\s+", line):
            name = re.sub(r"^###\s+\d*\.?\s*", "", line).strip()
            tools.append({"name": name, "desc": ""})
        elif in_section and tools and not tools[-1]["desc"]:
            stripped = line.strip()
            if stripped and not stripped.startswith("```") and not stripped.startswith("**"):
                # first non-empty prose line after heading
                if stripped.startswith("-") or stripped.startswith("*"):
                    stripped = stripped.lstrip("-* ")
                tools[-1]["desc"] = stripped
    return tools


def parse_quick_start(md_text):
    """Extract Quick Start section content."""
    lines = md_text.splitlines()
    collecting = False
    result = []
    for line in lines:
        if re.match(r"^##\s+Quick Start", line, re.I):
            collecting = True
            continue
        if collecting and re.match(r"^##\s+", line) and not re.match(r"^###", line):
            break
        if collecting:
            result.append(line)
    text = "\n".join(result).strip()
    # strip leading ---
    text = re.sub(r"^---\s*", "", text).strip()
    return text


def collect_agents():
    """Collect agent .md files from agents/ directory."""
    agents_dir = REPO_ROOT / "agents"
    agents = []
    if not agents_dir.exists():
        return agents
    for md_file in sorted(agents_dir.rglob("*.md")):
        if md_file.name == "CLAUDE.md":
            continue
        rel = md_file.relative_to(REPO_ROOT)
        text = md_file.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)
        name = meta.get("name", md_file.stem)
        desc = meta.get("description", "")
        domain = meta.get("domain", "")
        agents.append({"name": name, "description": desc, "domain": domain, "path": str(rel)})
    return agents


def collect_commands():
    """Collect slash command .md files from .claude/commands/."""
    cmds_dir = REPO_ROOT / ".claude" / "commands"
    cmds = []
    if not cmds_dir.exists():
        return cmds
    for md_file in sorted(cmds_dir.rglob("*.md")):
        if md_file.name == "README.md":
            continue
        rel = md_file.relative_to(REPO_ROOT)
        text = md_file.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)
        name = md_file.stem
        # handle git/cm -> git:cm
        if md_file.parent.name != "commands":
            name = f"{md_file.parent.name}:{md_file.stem}"
        desc = meta.get("description", "")
        cmds.append({"name": name, "description": desc, "path": str(rel)})
    return cmds


def _parse_frontmatter(text):
    """Simple YAML frontmatter parser (key: value pairs only)."""
    meta = {}
    if not text.startswith("---"):
        return meta
    end = text.find("---", 3)
    if end == -1:
        return meta
    block = text[3:end].strip()
    current_key = None
    for line in block.splitlines():
        if line.startswith("  ") and current_key:
            # continuation of multiline value
            meta[current_key] = (meta.get(current_key, "") + " " + line.strip()).strip()
            continue
        m = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if m:
            current_key = m.group(1)
            val = m.group(2).strip()
            if val.startswith(">") or val.startswith("|"):
                val = ""
            meta[current_key] = val
    return meta


# ---------------------------------------------------------------------------
# HTML template system
# ---------------------------------------------------------------------------

def _css():
    """Return the inline CSS matching the existing site design."""
    return """
:root {
  --bg: #0a0a0f;
  --bg-card: #12121a;
  --bg-terminal: #0d0d14;
  --text: #f0f0f0;
  --text-muted: #a0a0a0;
  --accent-blue: #00d4ff;
  --accent-violet: #7c3aed;
  --gradient: linear-gradient(135deg, var(--accent-blue), var(--accent-violet));
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
  --radius: 12px;
  --radius-sm: 8px;
  --max-width: 1200px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }
body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  overflow-x: hidden;
}
a { color: var(--accent-blue); text-decoration: none; transition: opacity 0.2s; }
a:hover { opacity: 0.8; }
.container { max-width: var(--max-width); margin: 0 auto; padding: 0 24px; }
.gradient-text {
  background: var(--gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Nav */
.nav { position: sticky; top: 0; z-index: 100; background: rgba(10,10,15,0.92); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255,255,255,0.06); padding: 16px 0; }
.nav-inner { display: flex; align-items: center; justify-content: space-between; }
.nav-brand { font-weight: 800; font-size: 1.1rem; color: var(--text); }
.nav-brand:hover { opacity: 1; }
.nav-links { display: flex; gap: 28px; align-items: center; }
.nav-links a { color: var(--text-muted); font-size: 0.9rem; font-weight: 500; }
.nav-links a:hover { color: var(--accent-blue); opacity: 1; }
.nav-links a.active { color: var(--accent-blue); }

/* Breadcrumbs */
.breadcrumbs { padding: 20px 0 0; font-size: 0.85rem; color: var(--text-muted); }
.breadcrumbs a { color: var(--text-muted); }
.breadcrumbs a:hover { color: var(--accent-blue); }
.breadcrumbs .sep { margin: 0 8px; opacity: 0.4; }

/* Page header */
.page-header { padding: 48px 0 32px; }
.page-title { font-size: clamp(1.75rem, 4vw, 2.75rem); font-weight: 800; margin-bottom: 12px; letter-spacing: -0.01em; }
.page-subtitle { color: var(--text-muted); max-width: 700px; font-size: 1.05rem; }

/* Search + Filter */
.filter-bar { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 32px; }
.search-input {
  flex: 1; min-width: 200px; padding: 12px 16px;
  background: var(--bg-card); border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-sm); color: var(--text); font-family: var(--font);
  font-size: 0.9rem; outline: none; transition: border-color 0.2s;
}
.search-input:focus { border-color: var(--accent-blue); }
.search-input::placeholder { color: var(--text-muted); }
.filter-select {
  padding: 12px 16px; background: var(--bg-card); border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-sm); color: var(--text); font-family: var(--font);
  font-size: 0.9rem; outline: none; cursor: pointer;
}

/* Skill cards grid */
.skills-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding-bottom: 60px; }
.skill-card {
  background: var(--bg-card); border: 1px solid rgba(255,255,255,0.06);
  border-radius: var(--radius); padding: 24px; transition: border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  display: flex; flex-direction: column;
}
.skill-card:hover {
  border-color: rgba(0,212,255,0.3);
  box-shadow: 0 0 30px rgba(0,212,255,0.08), 0 0 60px rgba(124,58,237,0.06);
  transform: translateY(-3px);
}
.skill-card h3 { font-size: 1rem; font-weight: 700; margin-bottom: 8px; }
.skill-card h3 a { color: var(--text); }
.skill-card h3 a:hover { color: var(--accent-blue); }
.skill-card p { font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; flex: 1; }
.skill-meta { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.skill-tag {
  font-family: var(--font-mono); font-size: 0.7rem; padding: 3px 8px;
  background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.15);
  border-radius: 4px; color: var(--accent-blue);
}
.skill-domain-badge {
  font-family: var(--font-mono); font-size: 0.7rem; padding: 3px 8px;
  background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.2);
  border-radius: 4px; color: var(--accent-violet);
}
.tools-count {
  font-family: var(--font-mono); font-size: 0.75rem;
  color: var(--text-muted); margin-top: 10px;
}

/* Skill detail page */
.skill-detail { padding-bottom: 80px; }
.skill-detail h2 { font-size: 1.5rem; font-weight: 700; margin: 40px 0 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.06); }
.skill-detail h3 { font-size: 1.15rem; font-weight: 600; margin: 24px 0 12px; }
.skill-detail p, .skill-detail li { font-size: 0.95rem; color: var(--text-muted); line-height: 1.7; }
.skill-detail ul, .skill-detail ol { margin-left: 20px; margin-bottom: 16px; }
.skill-detail li { margin-bottom: 6px; }
.skill-detail pre {
  background: var(--bg-terminal); border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-sm); padding: 16px 20px; overflow-x: auto;
  font-family: var(--font-mono); font-size: 0.85rem; line-height: 1.7;
  color: var(--accent-blue); margin: 12px 0 20px;
}
.skill-detail code {
  font-family: var(--font-mono); font-size: 0.85rem;
  background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;
}
.skill-detail pre code { background: none; padding: 0; }

/* Tools list */
.tool-item { background: var(--bg-card); border: 1px solid rgba(255,255,255,0.06); border-radius: var(--radius-sm); padding: 16px 20px; margin-bottom: 12px; }
.tool-item h4 { font-size: 0.95rem; font-weight: 600; margin-bottom: 4px; }
.tool-item p { font-size: 0.85rem; color: var(--text-muted); margin: 0; }

/* Related skills */
.related-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px; }

/* Agents grid */
.agents-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding-bottom: 60px; }
.agent-card {
  background: var(--bg-card); border: 1px solid rgba(255,255,255,0.06);
  border-radius: var(--radius); padding: 24px; transition: border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}
.agent-card:hover {
  border-color: rgba(124,58,237,0.3);
  box-shadow: 0 0 30px rgba(124,58,237,0.08), 0 0 60px rgba(0,212,255,0.06);
  transform: translateY(-3px);
}
.agent-card h3 { font-size: 1rem; font-weight: 700; margin-bottom: 6px; }
.agent-card p { font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; }

/* Commands grid */
.commands-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; padding-bottom: 60px; }
.command-card {
  background: var(--bg-card); border: 1px solid rgba(255,255,255,0.06);
  border-radius: var(--radius); padding: 24px; transition: border-color 0.3s, box-shadow 0.3s, transform 0.3s;
}
.command-card:hover {
  border-color: rgba(0,212,255,0.3);
  box-shadow: 0 0 30px rgba(0,212,255,0.08);
  transform: translateY(-3px);
}
.command-card h3 { font-family: var(--font-mono); font-size: 1rem; font-weight: 600; margin-bottom: 6px; color: var(--accent-blue); }
.command-card p { font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; }

/* Footer */
.footer { padding: 40px 0; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 40px; }
.footer-inner { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }
.footer-links { display: flex; align-items: center; gap: 12px; font-size: 0.875rem; color: var(--text-muted); }
.footer-links a { color: var(--text-muted); }
.footer-links a:hover { color: var(--accent-blue); }
.footer-sep { color: rgba(255,255,255,0.15); }
.footer-credit { font-size: 0.875rem; color: var(--text-muted); }
.footer-credit a { color: var(--text); font-weight: 600; }

/* Count badge */
.count-badge { display: inline-block; font-family: var(--font-mono); font-size: 0.8rem; color: var(--accent-blue); margin-left: 8px; }

/* Badge bar (skill detail pages) */
.badge-bar { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0 20px; }
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-family: var(--font-mono); font-size: 0.75rem; padding: 4px 10px;
  border-radius: 6px; font-weight: 500; white-space: nowrap;
}
.badge-domain { background: rgba(124,58,237,0.12); border: 1px solid rgba(124,58,237,0.25); color: var(--accent-violet); }
.badge-subdomain { background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.15); color: var(--accent-blue); }
.badge-version { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: var(--text-muted); }
.badge-tools { background: rgba(40,200,64,0.1); border: 1px solid rgba(40,200,64,0.2); color: #28c840; }
.badge-refs { background: rgba(254,188,46,0.1); border: 1px solid rgba(254,188,46,0.2); color: #febc2e; }

/* Example skill pills on domain cards */
.example-pills { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
.example-pill {
  font-family: var(--font-mono); font-size: 0.65rem; padding: 2px 7px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 4px; color: var(--text-muted);
}

/* Responsive */
@media (max-width: 768px) {
  .skills-grid, .agents-grid, .related-grid { grid-template-columns: repeat(2, 1fr); }
  .commands-grid { grid-template-columns: 1fr; }
  .nav-links { gap: 16px; }
}
@media (max-width: 480px) {
  .skills-grid, .agents-grid, .related-grid { grid-template-columns: 1fr; }
  .filter-bar { flex-direction: column; }
}
"""


def _nav(active=""):
    """Navigation bar HTML."""
    def _cls(name):
        return ' class="active"' if active == name else ""
    return f"""<nav class="nav">
  <div class="container nav-inner">
    <a href="{BASE_URL}/" class="nav-brand"><span class="gradient-text">Claude Skills</span></a>
    <div class="nav-links">
      <a href="{BASE_URL}/"{ _cls("home")}>Home</a>
      <a href="{BASE_URL}/skills/"{ _cls("skills")}>Skills</a>
      <a href="{BASE_URL}/agents/"{ _cls("agents")}>Agents</a>
      <a href="{BASE_URL}/commands/"{ _cls("commands")}>Commands</a>
      <a href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub</a>
    </div>
  </div>
</nav>"""


def _footer():
    return f"""<footer class="footer">
  <div class="container footer-inner">
    <div class="footer-links">
      <a href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub</a>
      <span class="footer-sep">&middot;</span>
      <span>MIT + Commons Clause</span>
      <span class="footer-sep">&middot;</span>
      <a href="https://buymeacoffee.com/borghei" target="_blank" rel="noopener">Buy Me a Coffee</a>
    </div>
    <div class="footer-credit">Built by <a href="https://github.com/borghei" target="_blank" rel="noopener">borghei</a></div>
  </div>
</footer>"""


def page(title, description, canonical, body, active="", breadcrumbs=None, og_url=None, jsonld=None):
    """Wrap body content in a full HTML page."""
    og = og_url or canonical
    bc_html = ""
    if breadcrumbs:
        parts = []
        for label, url in breadcrumbs:
            if url:
                parts.append(f'<a href="{url}">{escape(label)}</a>')
            else:
                parts.append(f"<span>{escape(label)}</span>")
        bc_html = f'<div class="breadcrumbs container">{"<span class=sep>/</span>".join(parts)}</div>'

    ld_tag = ""
    if jsonld:
        ld_tag = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description[:200])}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description[:200])}">
  <meta property="og:url" content="{og}">
  <meta property="og:type" content="website">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  {ld_tag}
  <style>{_css()}</style>
</head>
<body>
{_nav(active)}
{bc_html}
<main class="container">
{body}
</main>
{_footer()}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pretty_name(slug):
    """Convert a-slug-name to A Slug Name."""
    return " ".join(w.capitalize() for w in slug.split("-"))


def domain_label(domain):
    m = DOMAIN_META.get(domain)
    return m["label"] if m else pretty_name(domain)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_file(path, content):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def truncate(text, length=160):
    text = text.replace("\n", " ").strip()
    if len(text) <= length:
        return text
    return text[:length - 3].rsplit(" ", 1)[0] + "..."


def md_code_to_html(text):
    """Minimal markdown code-block to HTML conversion."""
    # Replace ```lang\n...\n``` with <pre><code>
    def _repl(m):
        code = escape(m.group(2))
        return f"<pre><code>{code}</code></pre>"
    return re.sub(r"```(\w*)\n(.*?)```", _repl, text, flags=re.DOTALL)


# ---------------------------------------------------------------------------
# Page generators
# ---------------------------------------------------------------------------

def gen_skill_page(skill, catalog, all_skills_by_domain):
    """Generate an individual skill HTML page."""
    name = skill["name"]
    domain = skill["domain"]
    desc = skill.get("description", "")
    tags = skill.get("tags", [])
    tools_count = skill.get("tools", 0)
    skill_path = skill.get("path", "")

    md_text = load_skill_md(skill_path)
    tools_list = parse_tools_section(md_text)
    quick_start = parse_quick_start(md_text)

    dl = domain_label(domain)
    pn = pretty_name(name)
    title = f"{pn} - Claude Skills"
    canonical = f"{BASE_URL}/skills/{domain}/{name}.html"
    breadcrumbs = [
        ("Home", f"{BASE_URL}/"),
        ("Skills", f"{BASE_URL}/skills/"),
        (dl, f"{BASE_URL}/skills/{domain}/"),
        (pn, None),
    ]

    jsonld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": pn,
        "description": desc,
        "applicationCategory": dl,
        "operatingSystem": "Any",
        "url": canonical,
        "author": {"@type": "Person", "name": "borghei"},
        "license": "https://opensource.org/licenses/MIT",
    }

    subdomain = skill.get("subdomain", "")
    version = skill.get("version", "")
    has_refs = skill.get("has_references", False)

    # Badge bar: domain, subdomain, version, tools, references
    badges = f'<span class="badge badge-domain">{escape(dl)}</span>'
    if subdomain:
        badges += f' <span class="badge badge-subdomain">{escape(pretty_name(subdomain))}</span>'
    if version:
        badges += f' <span class="badge badge-version">v{escape(version)}</span>'
    if tools_count:
        badges += f' <span class="badge badge-tools">{tools_count} tool{"s" if tools_count != 1 else ""}</span>'
    if has_refs:
        badges += ' <span class="badge badge-refs">references</span>'
    badge_bar = f'<div class="badge-bar">{badges}</div>'

    # Tags as pills
    tags_html = "".join(f'<span class="skill-tag">{escape(t)}</span>' for t in tags)
    if tags_html:
        tags_html = f'<div class="skill-meta" style="margin-bottom:24px">{tags_html}</div>'

    # Tools section
    tools_html = ""
    if tools_list:
        items = "".join(
            f'<div class="tool-item"><h4>{escape(t["name"])}</h4><p>{escape(t["desc"])}</p></div>'
            for t in tools_list
        )
        tools_html = f"<h2>Python Tools</h2>{items}"

    # Quick Start
    qs_html = ""
    if quick_start:
        qs_html = f"<h2>Quick Start</h2>{md_code_to_html(quick_start)}"

    # How to use
    skill_dir = os.path.dirname(skill_path)
    how_to = f"""<h2>How to Use This Skill</h2>

<h3>With Claude Code</h3>
<p>Copy the skill folder to your project:</p>
<pre><code>git clone {GITHUB_URL}.git
cp -r Claude-Skills/{escape(skill_dir)} your-project/</code></pre>

<h3>With the CS CLI</h3>
<pre><code>cs install {escape(skill_dir)} ./</code></pre>

<h3>With OpenAI Codex</h3>
<p>The skill is available in <code>.codex/skills/{escape(name)}/</code></p>

<h3>With Gemini CLI</h3>
<p>The skill is available in <code>.gemini/skills/{escape(name)}/</code></p>

<h3>Manual Copy</h3>
<pre><code>curl -sL {GITHUB_URL}/archive/main.tar.gz | tar xz --strip=1 Claude-Skills-main/{escape(skill_dir)}</code></pre>"""

    if tools_count:
        how_to += f"""

<h3>Run Python Tools</h3>
<pre><code>python {escape(skill_dir)}/scripts/tool_name.py --help</code></pre>"""

    # Related skills (same domain, max 6)
    related = [s for s in all_skills_by_domain.get(domain, []) if s["name"] != name][:6]
    related_html = ""
    if related:
        cards = "".join(
            f'<a href="{BASE_URL}/skills/{s["domain"]}/{s["name"]}.html" class="skill-card" style="text-decoration:none">'
            f'<h3>{escape(pretty_name(s["name"]))}</h3>'
            f'<p>{escape(truncate(s.get("description", ""), 100))}</p></a>'
            for s in related
        )
        related_html = f'<h2>Related Skills in {escape(dl)}</h2><div class="related-grid">{cards}</div>'

    # Source link
    source_html = f'<p style="margin-top:32px"><a href="{GITHUB_URL}/tree/main/{skill_path}" target="_blank" rel="noopener">View source on GitHub &rarr;</a></p>'

    body = f"""
<article class="skill-detail">
  <div class="page-header">
    <h1 class="page-title">{escape(pn)}</h1>
    {badge_bar}
    <p class="page-subtitle">{escape(desc)}</p>
    {tags_html}
  </div>
  {how_to}
  {tools_html}
  {qs_html}
  {related_html}
  {source_html}
</article>"""

    return page(title, desc, canonical, body, active="skills", breadcrumbs=breadcrumbs, jsonld=jsonld)


def gen_domain_page(domain, skills, catalog):
    """Generate a domain index page."""
    dl = domain_label(domain)
    dm = DOMAIN_META.get(domain, {})
    icon = dm.get("icon", "")
    desc_short = dm.get("desc", f"Skills in the {dl} domain")
    count = len(skills)
    tools_total = sum(s.get("tools", 0) for s in skills)

    title = f"{dl} Skills - Claude Skills"
    description = f"{count} {dl} skills with {tools_total} Python tools. {desc_short}"
    canonical = f"{BASE_URL}/skills/{domain}/"
    breadcrumbs = [
        ("Home", f"{BASE_URL}/"),
        ("Skills", f"{BASE_URL}/skills/"),
        (dl, None),
    ]

    # Search bar
    filter_html = f"""<div class="filter-bar">
  <input type="text" class="search-input" placeholder="Search {dl} skills..." id="domain-search" onkeyup="filterCards()">
</div>"""

    # Cards with category/subdomain/tools badges + tag pills
    cards = []
    for s in sorted(skills, key=lambda x: x["name"]):
        tags = "".join(f'<span class="skill-tag">{escape(t)}</span>' for t in s.get("tags", [])[:4])
        tc = s.get("tools", 0)
        subdomain = s.get("subdomain", "")
        badges = f'<span class="badge badge-domain">{escape(dl)}</span>'
        if subdomain:
            badges += f' <span class="badge badge-subdomain">{escape(pretty_name(subdomain))}</span>'
        if tc:
            badges += f' <span class="badge badge-tools">{tc} tool{"s" if tc != 1 else ""}</span>'
        cards.append(
            f'<a href="{BASE_URL}/skills/{s["domain"]}/{s["name"]}.html" class="skill-card" data-name="{escape(s["name"])}" data-tags="{escape(" ".join(s.get("tags", [])))}" style="text-decoration:none">'
            f'<h3>{escape(pretty_name(s["name"]))}</h3>'
            f'<p>{escape(truncate(s.get("description", ""), 120))}</p>'
            f'<div class="badge-bar">{badges}</div>'
            f'<div class="skill-meta">{tags}</div></a>'
        )

    search_js = """<script>
function filterCards(){
  var q=document.getElementById('domain-search').value.toLowerCase();
  document.querySelectorAll('.skill-card').forEach(function(c){
    var n=c.getAttribute('data-name')||'';
    var t=c.getAttribute('data-tags')||'';
    var txt=c.textContent.toLowerCase();
    c.style.display=(n.includes(q)||t.includes(q)||txt.includes(q))?'':'none';
  });
}
</script>"""

    body = f"""
<div class="page-header">
  <h1 class="page-title">{icon} {escape(dl)} <span class="count-badge">{count} skills</span></h1>
  <p class="page-subtitle">{escape(desc_short)}. {tools_total} Python automation tools.</p>
</div>
{filter_html}
<div class="skills-grid">
{"".join(cards)}
</div>
{search_js}"""

    return page(title, description, canonical, body, active="skills", breadcrumbs=breadcrumbs)


def gen_skills_index(catalog, all_skills_by_domain):
    """Generate the main skills catalog page."""
    total = len(catalog["skills"])
    total_tools = sum(d.get("tools", 0) for d in catalog.get("domains", {}).values())
    title = "All Skills - Claude Skills"
    description = f"{total} production-ready AI skills across {len(catalog.get('domains', {}))} domains with {total_tools} Python tools."
    canonical = f"{BASE_URL}/skills/"
    breadcrumbs = [("Home", f"{BASE_URL}/"), ("Skills", None)]

    # Domain filter options
    domain_options = "".join(
        f'<option value="{d}">{domain_label(d)}</option>'
        for d in sorted(all_skills_by_domain.keys())
    )

    filter_html = f"""<div class="filter-bar">
  <input type="text" class="search-input" placeholder="Search {total} skills..." id="skill-search" onkeyup="filterSkills()">
  <select class="filter-select" id="domain-filter" onchange="filterSkills()">
    <option value="">All Domains</option>
    {domain_options}
  </select>
</div>"""

    # Domain summary cards with example skill names as pills
    domain_summary = []
    for d in sorted(all_skills_by_domain.keys()):
        dm = DOMAIN_META.get(d, {})
        icon = dm.get("icon", "")
        dl = domain_label(d)
        cnt = len(all_skills_by_domain[d])
        tc = sum(s.get("tools", 0) for s in all_skills_by_domain[d])
        # Pick up to 4 example skill names
        examples = [s["name"] for s in all_skills_by_domain[d][:4]]
        pills = "".join(f'<span class="example-pill">{escape(pretty_name(e))}</span>' for e in examples)
        if cnt > len(examples):
            pills += f'<span class="example-pill">+{cnt - len(examples)} more</span>'
        domain_summary.append(
            f'<a href="{BASE_URL}/skills/{d}/" class="skill-card" style="text-decoration:none">'
            f'<h3>{icon} {escape(dl)}</h3>'
            f'<div class="badge-bar"><span class="badge badge-tools">{cnt} skills</span><span class="badge badge-version">{tc} tools</span></div>'
            f'<p>{escape(dm.get("desc", ""))}</p>'
            f'<div class="example-pills">{pills}</div></a>'
        )

    # All skill cards with badges
    cards = []
    for s in sorted(catalog["skills"], key=lambda x: x["name"]):
        tags = "".join(f'<span class="skill-tag">{escape(t)}</span>' for t in s.get("tags", [])[:3])
        tc = s.get("tools", 0)
        subdomain = s.get("subdomain", "")
        badges = f'<span class="badge badge-domain">{escape(domain_label(s["domain"]))}</span>'
        if subdomain:
            badges += f' <span class="badge badge-subdomain">{escape(pretty_name(subdomain))}</span>'
        if tc:
            badges += f' <span class="badge badge-tools">{tc} tool{"s" if tc != 1 else ""}</span>'
        cards.append(
            f'<a href="{BASE_URL}/skills/{s["domain"]}/{s["name"]}.html" class="skill-card" '
            f'data-name="{escape(s["name"])}" data-domain="{escape(s["domain"])}" '
            f'data-tags="{escape(" ".join(s.get("tags", [])))}" style="text-decoration:none">'
            f'<h3>{escape(pretty_name(s["name"]))}</h3>'
            f'<p>{escape(truncate(s.get("description", ""), 120))}</p>'
            f'<div class="badge-bar">{badges}</div>'
            f'<div class="skill-meta">{tags}</div></a>'
        )

    search_js = """<script>
function filterSkills(){
  var q=(document.getElementById('skill-search').value||'').toLowerCase();
  var d=document.getElementById('domain-filter').value;
  document.querySelectorAll('#all-skills .skill-card').forEach(function(c){
    var name=c.getAttribute('data-name')||'';
    var dom=c.getAttribute('data-domain')||'';
    var tags=c.getAttribute('data-tags')||'';
    var txt=c.textContent.toLowerCase();
    var matchQ=!q||name.includes(q)||tags.includes(q)||txt.includes(q);
    var matchD=!d||dom===d;
    c.style.display=(matchQ&&matchD)?'':'none';
  });
}
</script>"""

    body = f"""
<div class="page-header">
  <h1 class="page-title"><span class="gradient-text">Skill Catalog</span> <span class="count-badge">{total} skills</span></h1>
  <p class="page-subtitle">{escape(description)}</p>
</div>

<h2 style="font-size:1.3rem;font-weight:700;margin-bottom:20px">Browse by Domain</h2>
<div class="skills-grid" style="margin-bottom:48px">
{"".join(domain_summary)}
</div>

<h2 style="font-size:1.3rem;font-weight:700;margin-bottom:20px">All Skills</h2>
{filter_html}
<div class="skills-grid" id="all-skills">
{"".join(cards)}
</div>
{search_js}"""

    return page(title, description, canonical, body, active="skills", breadcrumbs=breadcrumbs)


def gen_agents_page(agents):
    """Generate agents catalog page."""
    title = "AI Agents - Claude Skills"
    description = f"{len(agents)} specialized AI agents for executive and lead roles."
    canonical = f"{BASE_URL}/agents/"
    breadcrumbs = [("Home", f"{BASE_URL}/"), ("Agents", None)]

    cards = []
    for a in sorted(agents, key=lambda x: x["name"]):
        dl = domain_label(a["domain"]) if a["domain"] else ""
        badge = f'<span class="skill-domain-badge">{escape(dl)}</span>' if dl else ""
        cards.append(
            f'<div class="agent-card">'
            f'<h3>{escape(pretty_name(a["name"]))}</h3>'
            f'{badge}'
            f'<p>{escape(truncate(a.get("description", ""), 160))}</p>'
            f'<p style="margin-top:8px"><a href="{GITHUB_URL}/tree/main/{a["path"]}" target="_blank" rel="noopener" style="font-size:0.8rem">View source &rarr;</a></p>'
            f'</div>'
        )

    body = f"""
<div class="page-header">
  <h1 class="page-title">Role-Based <span class="gradient-text">AI Agents</span> <span class="count-badge">{len(agents)}</span></h1>
  <p class="page-subtitle">Specialized agents for every executive and lead role. Each agent orchestrates multiple skills for comprehensive workflows.</p>
</div>
<div class="agents-grid">
{"".join(cards)}
</div>"""

    return page(title, description, canonical, body, active="agents", breadcrumbs=breadcrumbs)


def gen_commands_page(commands):
    """Generate commands catalog page."""
    title = "Slash Commands - Claude Skills"
    description = f"{len(commands)} slash commands for Claude Code including git workflows, reviews, and audits."
    canonical = f"{BASE_URL}/commands/"
    breadcrumbs = [("Home", f"{BASE_URL}/"), ("Commands", None)]

    cards = []
    for c in sorted(commands, key=lambda x: x["name"]):
        cards.append(
            f'<div class="command-card">'
            f'<h3>/{escape(c["name"])}</h3>'
            f'<p>{escape(truncate(c.get("description", ""), 200))}</p>'
            f'<p style="margin-top:8px"><a href="{GITHUB_URL}/tree/main/{c["path"]}" target="_blank" rel="noopener" style="font-size:0.8rem">View source &rarr;</a></p>'
            f'</div>'
        )

    body = f"""
<div class="page-header">
  <h1 class="page-title"><span class="gradient-text">Slash Commands</span> <span class="count-badge">{len(commands)}</span></h1>
  <p class="page-subtitle">Built-in commands for Claude Code. Type <code>/command-name</code> in your Claude Code session to run.</p>
</div>
<div class="commands-grid">
{"".join(cards)}
</div>"""

    return page(title, description, canonical, body, active="commands", breadcrumbs=breadcrumbs)


# ---------------------------------------------------------------------------
# Sitemap, robots.txt, llms.txt
# ---------------------------------------------------------------------------

def gen_sitemap(pages):
    """Generate sitemap.xml from a list of (url, lastmod) tuples."""
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url, priority in pages:
        u = ET.SubElement(urlset, "url")
        ET.SubElement(u, "loc").text = url
        ET.SubElement(u, "lastmod").text = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        ET.SubElement(u, "priority").text = str(priority)
    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    out = '<?xml version="1.0" encoding="UTF-8"?>\n'
    out += ET.tostring(urlset, encoding="unicode")
    return out


def gen_robots_txt():
    return f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""


def gen_llms_txt(catalog, agents, commands):
    """Generate llms.txt following the llms.txt convention."""
    total = len(catalog["skills"])
    domains = catalog.get("domains", {})
    total_tools = sum(d.get("tools", 0) for d in domains.values())

    lines = [
        "# Claude Skills",
        "",
        f"> The Universal AI Skills Library -- {total} production-ready skills across {len(domains)} domains with {total_tools} Python automation tools.",
        "",
        f"Website: {BASE_URL}",
        f"Repository: {GITHUB_URL}",
        "License: MIT + Commons Clause",
        "Author: borghei",
        "",
        "## What This Is",
        "",
        "Claude Skills is a library of reusable, production-ready skill packages that bundle domain expertise,",
        "best practices, analysis tools, and strategic frameworks. Works with every major AI coding assistant:",
        "Claude Code, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose, and more.",
        "",
        "## How to Use",
        "",
        "```",
        f"git clone {GITHUB_URL}.git",
        "cp -r Claude-Skills/engineering/senior-backend your-project/",
        "python your-project/senior-backend/scripts/api_scaffolder.py --help",
        "```",
        "",
        "## Domains",
        "",
    ]

    for d in sorted(domains.keys()):
        info = domains[d]
        dl = domain_label(d)
        lines.append(f"- {dl}: {info.get('count', 0)} skills, {info.get('tools', 0)} tools")

    lines += ["", "## All Skills", ""]
    for s in sorted(catalog["skills"], key=lambda x: (x["domain"], x["name"])):
        lines.append(f"- [{pretty_name(s['name'])}]({BASE_URL}/skills/{s['domain']}/{s['name']}.html): {truncate(s.get('description', ''), 120)}")

    if agents:
        lines += ["", "## Agents", ""]
        for a in sorted(agents, key=lambda x: x["name"]):
            lines.append(f"- {a['name']}: {truncate(a.get('description', ''), 120)}")

    if commands:
        lines += ["", "## Slash Commands", ""]
        for c in sorted(commands, key=lambda x: x["name"]):
            lines.append(f"- /{c['name']}: {truncate(c.get('description', ''), 120)}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def generate_full_site():
    """Generate the complete static site."""
    catalog = load_catalog()
    skills = catalog["skills"]
    agents = collect_agents()
    commands = collect_commands()

    # Group skills by domain
    by_domain = {}
    for s in skills:
        by_domain.setdefault(s["domain"], []).append(s)

    sitemap_pages = []
    generated = 0

    # 1. Skills index
    html = gen_skills_index(catalog, by_domain)
    write_file(str(SITE_DIR / "skills" / "index.html"), html)
    sitemap_pages.append((f"{BASE_URL}/skills/", "0.9"))
    generated += 1

    # 2. Domain pages
    for domain, domain_skills in sorted(by_domain.items()):
        html = gen_domain_page(domain, domain_skills, catalog)
        write_file(str(SITE_DIR / "skills" / domain / "index.html"), html)
        sitemap_pages.append((f"{BASE_URL}/skills/{domain}/", "0.8"))
        generated += 1

    # 3. Individual skill pages
    for s in skills:
        html = gen_skill_page(s, catalog, by_domain)
        write_file(str(SITE_DIR / "skills" / s["domain"] / f"{s['name']}.html"), html)
        sitemap_pages.append((f"{BASE_URL}/skills/{s['domain']}/{s['name']}.html", "0.7"))
        generated += 1

    # 4. Agents page
    html = gen_agents_page(agents)
    write_file(str(SITE_DIR / "agents" / "index.html"), html)
    sitemap_pages.append((f"{BASE_URL}/agents/", "0.8"))
    generated += 1

    # 5. Commands page
    html = gen_commands_page(commands)
    write_file(str(SITE_DIR / "commands" / "index.html"), html)
    sitemap_pages.append((f"{BASE_URL}/commands/", "0.8"))
    generated += 1

    # 6. Sitemap
    sitemap_pages.insert(0, (f"{BASE_URL}/", "1.0"))
    xml = gen_sitemap(sitemap_pages)
    write_file(str(SITE_DIR / "sitemap.xml"), xml)
    generated += 1

    # 7. robots.txt
    write_file(str(SITE_DIR / "robots.txt"), gen_robots_txt())
    generated += 1

    # 8. llms.txt
    write_file(str(SITE_DIR / "llms.txt"), gen_llms_txt(catalog, agents, commands))
    generated += 1

    print(f"Generated {generated} files in {SITE_DIR}/")
    print(f"  - {len(skills)} skill pages")
    print(f"  - {len(by_domain)} domain pages")
    print(f"  - 1 skills index, 1 agents page, 1 commands page")
    print(f"  - sitemap.xml, robots.txt, llms.txt")


def generate_single_skill(skill_name):
    """Generate a single skill page."""
    catalog = load_catalog()
    by_domain = {}
    for s in catalog["skills"]:
        by_domain.setdefault(s["domain"], []).append(s)

    matches = [s for s in catalog["skills"] if s["name"] == skill_name]
    if not matches:
        print(f"Error: skill '{skill_name}' not found in skills.json")
        sys.exit(1)

    for s in matches:
        html = gen_skill_page(s, catalog, by_domain)
        path = write_file(str(SITE_DIR / "skills" / s["domain"] / f"{s['name']}.html"), html)
        print(f"Generated {path}")


def generate_single_domain(domain_name):
    """Generate pages for a single domain."""
    catalog = load_catalog()
    by_domain = {}
    for s in catalog["skills"]:
        by_domain.setdefault(s["domain"], []).append(s)

    if domain_name not in by_domain:
        print(f"Error: domain '{domain_name}' not found. Available: {', '.join(sorted(by_domain.keys()))}")
        sys.exit(1)

    domain_skills = by_domain[domain_name]

    # Domain index
    html = gen_domain_page(domain_name, domain_skills, catalog)
    path = write_file(str(SITE_DIR / "skills" / domain_name / "index.html"), html)
    print(f"Generated {path}")

    # Individual skill pages
    for s in domain_skills:
        html = gen_skill_page(s, catalog, by_domain)
        path = write_file(str(SITE_DIR / "skills" / s["domain"] / f"{s['name']}.html"), html)
        print(f"Generated {path}")

    print(f"\n{len(domain_skills) + 1} pages generated for {domain_label(domain_name)}")


def main():
    parser = argparse.ArgumentParser(description="Generate Claude Skills static site")
    parser.add_argument("--skill", help="Generate page for a single skill by name")
    parser.add_argument("--domain", help="Generate pages for a single domain")
    args = parser.parse_args()

    if args.skill:
        generate_single_skill(args.skill)
    elif args.domain:
        generate_single_domain(args.domain)
    else:
        generate_full_site()


if __name__ == "__main__":
    main()
