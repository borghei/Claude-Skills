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
# Domain display metadata (no emojis — icons handled via inline SVG)
# ---------------------------------------------------------------------------

DOMAIN_META = {
    "engineering":        {"label": "Engineering",        "desc": "Architecture, fullstack, AI/ML, security, and infrastructure"},
    "marketing":          {"label": "Marketing",          "desc": "Content creation, SEO, demand gen, campaign analytics"},
    "c-level-advisor":    {"label": "C-Level Advisory",   "desc": "CEO, CTO, CFO, and CISO strategic advisory"},
    "project-management": {"label": "Project Management", "desc": "Discovery, execution, Atlassian MCP integration"},
    "business-growth":    {"label": "Business & Growth",  "desc": "Customer success, sales engineering, revenue ops"},
    "ra-qm-team":        {"label": "Compliance",         "desc": "ISO 13485, MDR, FDA, SOC 2, GDPR, EU AI Act, NIS2"},
    "data-analytics":     {"label": "Data Analytics",     "desc": "BI, ML ops, analytics engineering, data pipelines"},
    "product-team":       {"label": "Product",            "desc": "RICE scoring, OKRs, user stories, UX research"},
    "sales-success":      {"label": "Sales",              "desc": "Account executive, sales ops, solutions architect"},
    "hr-operations":      {"label": "HR Operations",      "desc": "Talent acquisition, people analytics, HR business partner"},
    "finance":            {"label": "Finance",            "desc": "DCF valuation, budgeting, forecasting, ratio analysis"},
}

# Inline SVG icons (16x16, stroke-based line icons)
SVG_ICONS = {
    "arrow-right": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
    "github": '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>',
    "tools": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>',
    "folder": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>',
    "terminal": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>',
    "search": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "grid": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    "users": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
    "command": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 3a3 3 0 00-3 3v12a3 3 0 003 3 3 3 0 003-3 3 3 0 00-3-3H6a3 3 0 00-3 3 3 3 0 003 3 3 3 0 003-3V6a3 3 0 00-3-3 3 3 0 00-3 3 3 3 0 003 3h12a3 3 0 003-3 3 3 0 00-3-3z"/></svg>',
    "external": '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',
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
# HTML template system — claude.ai-inspired cream/terracotta design
# ---------------------------------------------------------------------------

def _css():
    """Return the inline CSS for the cream/terracotta design system."""
    return """
:root {
  --bg: #faf9f5;
  --bg-secondary: #f0eee6;
  --text: #141413;
  --text-muted: #5e5d59;
  --accent: #d97757;
  --accent-deep: #c6613f;
  --border: rgba(20,20,19,0.1);
  --border-strong: rgba(20,20,19,0.18);
  --white: #ffffff;
  --radius: 8px;
  --radius-lg: 12px;
  --font-serif: Georgia, 'Times New Roman', serif;
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'SF Mono', SFMono-Regular, ui-monospace, 'Cascadia Code', Menlo, monospace;
  --max-width: 1200px;
  --shadow-sm: 0 1px 2px rgba(20,20,19,0.04);
  --shadow: 0 1px 3px rgba(20,20,19,0.06), 0 1px 2px rgba(20,20,19,0.04);
  --shadow-md: 0 4px 12px rgba(20,20,19,0.08), 0 1px 3px rgba(20,20,19,0.06);
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }
body {
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  overflow-x: hidden;
}
a { color: var(--accent); text-decoration: none; transition: color 0.15s; }
a:hover { color: var(--accent-deep); }
.container { max-width: var(--max-width); margin: 0 auto; padding: 0 24px; }
code { font-family: var(--font-mono); font-size: 0.875em; }

/* Navbar */
.navbar {
  position: sticky; top: 0; z-index: 100;
  background: rgba(250,249,245,0.92); backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  padding: 14px 0;
}
.navbar .container { display: flex; align-items: center; justify-content: space-between; }
.nav-logo {
  font-family: var(--font-serif); font-weight: 700; font-size: 1.1rem;
  color: var(--text); letter-spacing: -0.01em;
}
.nav-logo:hover { color: var(--text); }
.nav-links { display: flex; gap: 28px; align-items: center; }
.nav-links a {
  color: var(--text-muted); font-size: 0.9rem; font-weight: 500;
  transition: color 0.15s;
}
.nav-links a:hover { color: var(--text); }
.nav-links a.active { color: var(--accent); }
.nav-links a.gh-link { display: inline-flex; align-items: center; gap: 5px; }

/* Breadcrumbs */
.breadcrumbs { padding: 20px 0 0; font-size: 0.85rem; color: var(--text-muted); }
.breadcrumbs a { color: var(--text-muted); }
.breadcrumbs a:hover { color: var(--accent); }
.breadcrumbs .sep { margin: 0 8px; opacity: 0.4; }

/* Page header */
.page-header { padding: 48px 0 32px; }
.page-title {
  font-family: var(--font-serif); font-size: clamp(1.75rem, 4vw, 2.75rem);
  font-weight: 700; margin-bottom: 12px; letter-spacing: -0.02em;
  color: var(--text);
}
.page-subtitle { color: var(--text-muted); max-width: 700px; font-size: 1.05rem; line-height: 1.6; }

/* Count badge (inline with title) */
.count-badge {
  display: inline-block; font-family: var(--font-mono); font-size: 0.8rem;
  color: var(--accent); background: rgba(217,119,87,0.08);
  padding: 2px 10px; border-radius: 20px; margin-left: 8px;
  vertical-align: middle; font-weight: 500;
}

/* Search + Filter */
.filter-bar { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 32px; }
.search-input {
  flex: 1; min-width: 200px; padding: 10px 14px 10px 38px;
  background: var(--white); border: 1px solid var(--border-strong);
  border-radius: var(--radius); color: var(--text); font-family: var(--font-sans);
  font-size: 0.9rem; outline: none; transition: border-color 0.2s, box-shadow 0.2s;
}
.search-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(217,119,87,0.1); }
.search-input::placeholder { color: var(--text-muted); }
.search-wrap { position: relative; flex: 1; min-width: 200px; }
.search-wrap svg { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
.filter-select {
  padding: 10px 14px; background: var(--white); border: 1px solid var(--border-strong);
  border-radius: var(--radius); color: var(--text); font-family: var(--font-sans);
  font-size: 0.9rem; outline: none; cursor: pointer;
}
.filter-select:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(217,119,87,0.1); }

/* Card grid */
.skills-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; padding-bottom: 60px; }
.skill-card {
  background: var(--white); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 20px 22px;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
  display: flex; flex-direction: column;
}
.skill-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.skill-card h3 { font-size: 0.95rem; font-weight: 600; margin-bottom: 6px; }
.skill-card h3 a { color: var(--text); }
.skill-card h3 a:hover { color: var(--accent); }
.skill-card p { font-size: 0.85rem; color: var(--text-muted); line-height: 1.55; flex: 1; }

/* Badges */
.badge-bar { display: flex; gap: 6px; flex-wrap: wrap; margin: 10px 0 6px; }
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-family: var(--font-mono); font-size: 0.7rem; padding: 3px 9px;
  border-radius: 5px; font-weight: 500; white-space: nowrap;
}
.badge-domain { background: rgba(217,119,87,0.1); border: 1px solid rgba(217,119,87,0.2); color: var(--accent-deep); }
.badge-subdomain { background: rgba(20,20,19,0.04); border: 1px solid var(--border); color: var(--text-muted); }
.badge-version { background: rgba(20,20,19,0.03); border: 1px solid var(--border); color: var(--text-muted); }
.badge-tools { background: rgba(20,20,19,0.04); border: 1px solid var(--border); color: var(--text-muted); }
.badge-refs { background: rgba(217,119,87,0.06); border: 1px solid rgba(217,119,87,0.15); color: var(--accent); }

/* Tags */
.skill-meta { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
.tag {
  font-family: var(--font-mono); font-size: 0.65rem; padding: 2px 8px;
  background: var(--bg-secondary); border: 1px solid var(--border);
  border-radius: 4px; color: var(--text-muted);
}

/* Example pills on domain summary cards */
.example-pills { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
.example-pill {
  font-family: var(--font-mono); font-size: 0.65rem; padding: 2px 7px;
  background: var(--bg-secondary); border: 1px solid var(--border);
  border-radius: 4px; color: var(--text-muted);
}

/* Skill detail page */
.skill-detail { padding-bottom: 80px; }
.skill-detail h2 {
  font-family: var(--font-serif); font-size: 1.4rem; font-weight: 700;
  margin: 40px 0 16px; padding-top: 16px;
  border-top: 1px solid var(--border); color: var(--text);
}
.skill-detail h3 { font-size: 1.05rem; font-weight: 600; margin: 20px 0 10px; }
.skill-detail p, .skill-detail li { font-size: 0.95rem; color: var(--text-muted); line-height: 1.7; }
.skill-detail ul, .skill-detail ol { margin-left: 20px; margin-bottom: 16px; }
.skill-detail li { margin-bottom: 6px; }
.skill-detail pre {
  background: var(--bg-secondary); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px 20px; overflow-x: auto;
  font-family: var(--font-mono); font-size: 0.85rem; line-height: 1.7;
  color: var(--text); margin: 12px 0 20px;
}
.skill-detail code {
  font-family: var(--font-mono); font-size: 0.85rem;
  background: var(--bg-secondary); padding: 2px 6px; border-radius: 4px;
}
.skill-detail pre code { background: none; padding: 0; }

/* Platform tabs */
.platform-tabs { display: flex; gap: 0; border-bottom: 1px solid var(--border); margin-bottom: 0; }
.tab-btn {
  padding: 10px 18px; font-size: 0.85rem; font-weight: 500;
  font-family: var(--font-sans); background: none; border: none;
  border-bottom: 2px solid transparent; color: var(--text-muted);
  cursor: pointer; transition: color 0.15s, border-color 0.15s;
}
.tab-btn:hover { color: var(--text); }
.tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); }
.tab-content { display: none; }
.tab-content.active { display: block; }
.tab-content pre {
  border-top: none; border-radius: 0 0 var(--radius) var(--radius);
  margin-top: 0;
}

/* Tools list */
.tool-item {
  background: var(--white); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 18px; margin-bottom: 10px;
}
.tool-item h4 { font-size: 0.9rem; font-weight: 600; margin-bottom: 3px; color: var(--text); }
.tool-item p { font-size: 0.85rem; color: var(--text-muted); margin: 0; }

/* Related skills */
.related-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 16px; }

/* Agents grid */
.agents-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; padding-bottom: 60px; }
.agent-card {
  background: var(--white); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 20px 22px;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.agent-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.agent-card h3 { font-size: 0.95rem; font-weight: 600; margin-bottom: 6px; color: var(--text); }
.agent-card p { font-size: 0.85rem; color: var(--text-muted); line-height: 1.55; }
.agent-card .view-link {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.8rem; margin-top: 10px; color: var(--accent);
}

/* Commands grid */
.commands-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; padding-bottom: 60px; }
.command-card {
  background: var(--white); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 20px 22px;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.command-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.command-card h3 {
  font-family: var(--font-mono); font-size: 0.95rem; font-weight: 600;
  margin-bottom: 6px; color: var(--accent);
}
.command-card p { font-size: 0.85rem; color: var(--text-muted); line-height: 1.55; }
.command-card .view-link {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.8rem; margin-top: 10px; color: var(--accent);
}

/* Buttons */
.btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 18px; border-radius: var(--radius); font-size: 0.875rem;
  font-weight: 500; font-family: var(--font-sans);
  border: 1px solid transparent; cursor: pointer;
  transition: background 0.15s, color 0.15s, box-shadow 0.15s;
  text-decoration: none;
}
.btn-primary { background: var(--text); color: var(--bg); border-color: var(--text); }
.btn-primary:hover { background: #2a2a28; color: var(--bg); box-shadow: var(--shadow); }
.btn-secondary { background: transparent; color: var(--text); border-color: var(--border-strong); }
.btn-secondary:hover { background: var(--bg-secondary); color: var(--text); box-shadow: var(--shadow-sm); }

/* Section heading */
.section-heading {
  font-family: var(--font-serif); font-size: 1.25rem; font-weight: 700;
  margin-bottom: 20px; color: var(--text);
}

/* Footer */
.footer {
  padding: 36px 0; border-top: 1px solid var(--border); margin-top: 40px;
  background: var(--bg);
}
.footer-inner { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }
.footer-links {
  display: flex; align-items: center; gap: 12px;
  font-size: 0.85rem; color: var(--text-muted);
}
.footer-links a { color: var(--text-muted); }
.footer-links a:hover { color: var(--accent); }
.footer-sep { color: var(--border-strong); }
.footer-credit { font-size: 0.85rem; color: var(--text-muted); }
.footer-credit a { color: var(--text); font-weight: 600; }

/* Responsive */
@media (max-width: 768px) {
  .skills-grid, .agents-grid, .related-grid { grid-template-columns: repeat(2, 1fr); }
  .commands-grid { grid-template-columns: 1fr; }
  .nav-links { gap: 16px; }
  .platform-tabs { overflow-x: auto; }
  .tab-btn { padding: 8px 12px; font-size: 0.8rem; white-space: nowrap; }
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
    gh_icon = SVG_ICONS["github"]
    return f"""<nav class="navbar">
  <div class="container">
    <a href="{BASE_URL}/" class="nav-logo">Claude Skills</a>
    <div class="nav-links">
      <a href="{BASE_URL}/skills/"{ _cls("skills")}>Skills</a>
      <a href="{BASE_URL}/agents/"{ _cls("agents")}>Agents</a>
      <a href="{BASE_URL}/commands/"{ _cls("commands")}>Commands</a>
      <a href="{GITHUB_URL}" target="_blank" rel="noopener" class="gh-link">{gh_icon} GitHub</a>
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


def page(title, description, canonical, body, active="", breadcrumbs=None, og_url=None, jsonld=None, extra_js=""):
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

    js_tag = ""
    if extra_js:
        js_tag = f"<script>{extra_js}</script>"

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
{js_tag}
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

    # Badge bar
    badges = f'<span class="badge badge-domain">{escape(dl)}</span>'
    if subdomain:
        badges += f' <span class="badge badge-subdomain">{escape(pretty_name(subdomain))}</span>'
    if version:
        badges += f' <span class="badge badge-version">v{escape(version)}</span>'
    if tools_count:
        badges += f' <span class="badge badge-tools">{SVG_ICONS["tools"]} {tools_count} tool{"s" if tools_count != 1 else ""}</span>'
    if has_refs:
        badges += ' <span class="badge badge-refs">references</span>'
    badge_bar = f'<div class="badge-bar">{badges}</div>'

    # Tags as pills
    tags_html = "".join(f'<span class="tag">{escape(t)}</span>' for t in tags)
    if tags_html:
        tags_html = f'<div class="skill-meta" style="margin-bottom:24px">{tags_html}</div>'

    # How to Use — tabbed platform selector
    skill_dir = os.path.dirname(skill_path)
    how_to = f"""<h2>How to Use</h2>
<div class="platform-tabs">
  <button class="tab-btn active" data-tab="claude">Claude Code</button>
  <button class="tab-btn" data-tab="codex">Codex</button>
  <button class="tab-btn" data-tab="gemini">Gemini CLI</button>
  <button class="tab-btn" data-tab="cursor">Cursor</button>
  <button class="tab-btn" data-tab="manual">Manual</button>
</div>
<div class="tab-content active" id="tab-claude">
  <pre><code># Add to your project
cs install {escape(skill_dir)} ./

# Or copy directly
git clone {GITHUB_URL}.git
cp -r Claude-Skills/{escape(skill_dir)} your-project/</code></pre>
</div>
<div class="tab-content" id="tab-codex">
  <pre><code># The skill is available in your Codex workspace at:
.codex/skills/{escape(name)}/

# Reference the SKILL.md in your Codex instructions
# or copy it into your project:
cp -r .codex/skills/{escape(name)} your-project/</code></pre>
</div>
<div class="tab-content" id="tab-gemini">
  <pre><code># The skill is available in your Gemini CLI workspace at:
.gemini/skills/{escape(name)}/

# Reference the SKILL.md in your Gemini instructions
# or copy it into your project:
cp -r .gemini/skills/{escape(name)} your-project/</code></pre>
</div>
<div class="tab-content" id="tab-cursor">
  <pre><code># Add to your .cursorrules or workspace settings:
# Reference: {escape(skill_dir)}/SKILL.md

# Or copy the skill folder into your project:
git clone {GITHUB_URL}.git
cp -r Claude-Skills/{escape(skill_dir)} your-project/</code></pre>
</div>
<div class="tab-content" id="tab-manual">
  <pre><code># Clone and copy
git clone {GITHUB_URL}.git
cp -r Claude-Skills/{escape(skill_dir)} your-project/

# Or download just this skill
curl -sL {GITHUB_URL}/archive/main.tar.gz | tar xz --strip=1 Claude-Skills-main/{escape(skill_dir)}</code></pre>
</div>"""

    if tools_count:
        how_to += f"""
<h3>Run Python Tools</h3>
<pre><code>python {escape(skill_dir)}/scripts/tool_name.py --help</code></pre>"""

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
    ext_icon = SVG_ICONS["external"]
    source_html = f'<p style="margin-top:32px"><a href="{GITHUB_URL}/tree/main/{skill_path}" target="_blank" rel="noopener" class="btn btn-secondary">View on GitHub {ext_icon}</a></p>'

    # Tab-switching JS
    tab_js = """
document.querySelectorAll('.tab-btn').forEach(function(btn){
  btn.addEventListener('click',function(){
    document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active')});
    document.querySelectorAll('.tab-content').forEach(function(c){c.classList.remove('active')});
    btn.classList.add('active');
    document.getElementById('tab-'+btn.dataset.tab).classList.add('active');
  });
});
"""

    body = f"""
<article class="skill-detail">
  <div class="page-header">
    <h1 class="page-title">{escape(pn)}</h1>
    <p class="page-subtitle">{escape(desc)}</p>
    {badge_bar}
    {tags_html}
  </div>
  {how_to}
  {tools_html}
  {qs_html}
  {related_html}
  {source_html}
</article>"""

    return page(title, desc, canonical, body, active="skills", breadcrumbs=breadcrumbs, jsonld=jsonld, extra_js=tab_js)


def gen_domain_page(domain, skills, catalog):
    """Generate a domain index page."""
    dl = domain_label(domain)
    dm = DOMAIN_META.get(domain, {})
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

    search_icon = SVG_ICONS["search"]
    filter_html = f"""<div class="filter-bar">
  <div class="search-wrap">
    {search_icon}
    <input type="text" class="search-input" placeholder="Search {dl} skills..." id="domain-search" onkeyup="filterCards()">
  </div>
</div>"""

    cards = []
    for s in sorted(skills, key=lambda x: x["name"]):
        tags = "".join(f'<span class="tag">{escape(t)}</span>' for t in s.get("tags", [])[:4])
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

    search_js = """
function filterCards(){
  var q=document.getElementById('domain-search').value.toLowerCase();
  document.querySelectorAll('.skill-card').forEach(function(c){
    var n=c.getAttribute('data-name')||'';
    var t=c.getAttribute('data-tags')||'';
    var txt=c.textContent.toLowerCase();
    c.style.display=(n.includes(q)||t.includes(q)||txt.includes(q))?'':'none';
  });
}
"""

    body = f"""
<div class="page-header">
  <h1 class="page-title">{escape(dl)} <span class="count-badge">{count} skills</span></h1>
  <p class="page-subtitle">{escape(desc_short)}. {tools_total} Python automation tools.</p>
</div>
{filter_html}
<div class="skills-grid">
{"".join(cards)}
</div>"""

    return page(title, description, canonical, body, active="skills", breadcrumbs=breadcrumbs, extra_js=search_js)


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

    search_icon = SVG_ICONS["search"]
    filter_html = f"""<div class="filter-bar">
  <div class="search-wrap">
    {search_icon}
    <input type="text" class="search-input" placeholder="Search {total} skills..." id="skill-search" onkeyup="filterSkills()">
  </div>
  <select class="filter-select" id="domain-filter" onchange="filterSkills()">
    <option value="">All Domains</option>
    {domain_options}
  </select>
</div>"""

    # Domain summary cards
    domain_summary = []
    for d in sorted(all_skills_by_domain.keys()):
        dm = DOMAIN_META.get(d, {})
        dl_name = domain_label(d)
        cnt = len(all_skills_by_domain[d])
        tc = sum(s.get("tools", 0) for s in all_skills_by_domain[d])
        examples = [s["name"] for s in all_skills_by_domain[d][:4]]
        pills = "".join(f'<span class="example-pill">{escape(pretty_name(e))}</span>' for e in examples)
        if cnt > len(examples):
            pills += f'<span class="example-pill">+{cnt - len(examples)} more</span>'
        domain_summary.append(
            f'<a href="{BASE_URL}/skills/{d}/" class="skill-card" style="text-decoration:none">'
            f'<h3>{escape(dl_name)}</h3>'
            f'<div class="badge-bar"><span class="badge badge-domain">{cnt} skills</span><span class="badge badge-tools">{tc} tools</span></div>'
            f'<p>{escape(dm.get("desc", ""))}</p>'
            f'<div class="example-pills">{pills}</div></a>'
        )

    # All skill cards
    cards = []
    for s in sorted(catalog["skills"], key=lambda x: x["name"]):
        tags = "".join(f'<span class="tag">{escape(t)}</span>' for t in s.get("tags", [])[:3])
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

    search_js = """
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
"""

    body = f"""
<div class="page-header">
  <h1 class="page-title">Skill Catalog <span class="count-badge">{total} skills</span></h1>
  <p class="page-subtitle">{escape(description)}</p>
</div>

<h2 class="section-heading">Browse by Domain</h2>
<div class="skills-grid" style="margin-bottom:48px">
{"".join(domain_summary)}
</div>

<h2 class="section-heading">All Skills</h2>
{filter_html}
<div class="skills-grid" id="all-skills">
{"".join(cards)}
</div>"""

    return page(title, description, canonical, body, active="skills", breadcrumbs=breadcrumbs, extra_js=search_js)


def gen_agents_page(agents):
    """Generate agents catalog page."""
    title = "AI Agents - Claude Skills"
    description = f"{len(agents)} specialized AI agents for executive and lead roles."
    canonical = f"{BASE_URL}/agents/"
    breadcrumbs = [("Home", f"{BASE_URL}/"), ("Agents", None)]

    ext_icon = SVG_ICONS["external"]
    cards = []
    for a in sorted(agents, key=lambda x: x["name"]):
        dl = domain_label(a["domain"]) if a["domain"] else ""
        badge = f'<span class="badge badge-domain">{escape(dl)}</span>' if dl else ""
        cards.append(
            f'<div class="agent-card">'
            f'<h3>{escape(pretty_name(a["name"]))}</h3>'
            f'{f"""<div class="badge-bar">{badge}</div>""" if badge else ""}'
            f'<p>{escape(truncate(a.get("description", ""), 160))}</p>'
            f'<a href="{GITHUB_URL}/tree/main/{a["path"]}" target="_blank" rel="noopener" class="view-link">View source {ext_icon}</a>'
            f'</div>'
        )

    body = f"""
<div class="page-header">
  <h1 class="page-title">AI Agents <span class="count-badge">{len(agents)}</span></h1>
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

    ext_icon = SVG_ICONS["external"]
    cards = []
    for c in sorted(commands, key=lambda x: x["name"]):
        cards.append(
            f'<div class="command-card">'
            f'<h3>/{escape(c["name"])}</h3>'
            f'<p>{escape(truncate(c.get("description", ""), 200))}</p>'
            f'<a href="{GITHUB_URL}/tree/main/{c["path"]}" target="_blank" rel="noopener" class="view-link">View source {ext_icon}</a>'
            f'</div>'
        )

    body = f"""
<div class="page-header">
  <h1 class="page-title">Slash Commands <span class="count-badge">{len(commands)}</span></h1>
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
