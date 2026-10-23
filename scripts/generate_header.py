#!/usr/bin/env python3
"""Build assets/header.svg: a theme-aware README banner with a treemap of skills per domain.

Reads the per-domain counts from skills.json, so re-run it after build_manifest.py
whenever skills are added or removed:

    python3 scripts/generate_header.py
    python3 scripts/generate_header.py --force-dark /tmp/dark.svg   # preview for renderers without @media
    python3 scripts/generate_header.py --social assets/social-preview.svg
        # 1280x640 card for the GitHub social preview and the site's og:image;
        # convert to PNG with any SVG renderer, e.g. rsvg-convert -w 1280 in.svg -o out.png

Standard library only.
"""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description="Generate the README header SVG from skills.json.")
parser.add_argument("out", nargs="?", help="Output path (default: assets/header.svg)")
parser.add_argument("--force-dark", action="store_true", help="Always use the dark palette (for previews)")
parser.add_argument("--social", action="store_true", help="Build the 1280x640 social preview card instead")
args = parser.parse_args()
repo = Path(__file__).resolve().parent.parent
out = Path(args.out) if args.out else repo / "assets" / ("social-preview.svg" if args.social else "header.svg")
domains = json.load(open(f"{repo}/skills.json"))["domains"]
total = sum(d["count"] for d in domains.values())

LABEL = {
    "engineering": "Engineering", "project-management": "Project Mgmt", "marketing": "Marketing",
    "c-level-advisor": "C-Level", "ra-qm-team": "Compliance", "business-growth": "Growth",
    "legal": "Legal", "personal-productivity": "Productivity", "product-team": "Product",
    "tools": "LinkedIn", "vertical-advisors": "Verticals", "business-operations": "Ops",
    "data-analytics": "Data", "sales-success": "Sales", "hr-operations": "HR", "documents": "Docs",
    "research": "Research", "research-ops": "Research Ops", "markdown-html": "MD→HTML",
    "finance": "Finance", "workflow": "Workflow",
}
# The README's four groups
GROUP = {
    "c-level-advisor": "a", "business-growth": "a", "business-operations": "a", "finance": "a",
    "sales-success": "a", "hr-operations": "a", "vertical-advisors": "a",
    "project-management": "b", "product-team": "b", "engineering": "b", "data-analytics": "b",
    "ra-qm-team": "c", "legal": "c",
    "marketing": "d", "tools": "d", "personal-productivity": "d", "documents": "d",
    "markdown-html": "d", "research": "d", "research-ops": "d", "workflow": "d",
}

items = sorted(((k, v["count"]) for k, v in domains.items()), key=lambda x: -x[1])


def worst(row, w):
    s = sum(a for _, a in row)
    return max(max(w * w * a / (s * s), (s * s) / (w * w * a)) for _, a in row)


def squarify(items, x, y, w, h):
    """Squarified treemap (Bruls et al.). items carry areas already scaled to w*h."""
    rects = []
    items = list(items)
    while items:
        short = min(w, h)
        row = [items.pop(0)]
        while items and worst(row + [items[0]], short) <= worst(row, short):
            row.append(items.pop(0))
        s = sum(a for _, a in row)
        if w >= h:
            col_w = s / h
            cy = y
            for k, a in row:
                rects.append((k, x, cy, col_w, a / col_w))
                cy += a / col_w
            x += col_w
            w -= col_w
        else:
            row_h = s / w
            cx = x
            for k, a in row:
                rects.append((k, cx, y, a / row_h, row_h))
                cx += a / row_h
            y += row_h
            h -= row_h
    return rects


def build_tiles(tx, ty, tw, th, animate=True):
    """Lay out the treemap inside (tx, ty, tw, th) and return its SVG tiles."""
    scale = tw * th / total
    rects = squarify([(k, c * scale) for k, c in items], tx, ty, tw, th)
    tiles = []
    for i, (k, x, y, w, h) in enumerate(rects):
        x2, y2, w2, h2 = x + GAP / 2, y + GAP / 2, w - GAP, h - GAP
        g = GROUP[k]
        lab = ""
        if w2 > 78 and h2 > 44:
            big = w2 > 150 and h2 > 90
            fs = 22 if big else 14
            ns = 40 if big else 20
            while fs > 10 and len(LABEL[k]) * fs * 0.6 > w2 - 22:
                fs -= 1
            lab = (f'<text class="tl" x="{x2 + 12:.1f}" y="{y2 + 12 + ns * 0.8:.1f}" font-size="{ns}">{count[k]}</text>'
                   f'<text class="tn" x="{x2 + 12:.1f}" y="{y2 + 18 + ns * 0.8 + fs:.1f}" font-size="{fs}">{LABEL[k]}</text>')
        elif w2 > 34 and h2 > 26:
            lab = f'<text class="tl" x="{x2 + w2 / 2:.1f}" y="{y2 + h2 / 2 + 5:.1f}" font-size="13" text-anchor="middle">{count[k]}</text>'
        style = f' style="animation-delay:{0.15 + i * 0.06:.2f}s, {3 + i * 1.7:.1f}s"' if animate else ""
        tiles.append(
            f'<g class="tile"{style}>'
            f'<title>{LABEL[k]}: {count[k]} skills</title>'
            f'<rect class="g{g}" x="{x2:.1f}" y="{y2:.1f}" width="{w2:.1f}" height="{h2:.1f}" rx="5"/>{lab}</g>'
        )
    return tiles, len(rects)


def legend(tx, y):
    return f'''<g class="sans" font-size="13">
  <rect class="ga" x="{tx}" y="{y}" width="10" height="10" rx="2"/><text class="mute" x="{tx + 16}" y="{y + 9}">Leadership &amp; business</text>
  <rect class="gb" x="{tx + 170}" y="{y}" width="10" height="10" rx="2"/><text class="mute" x="{tx + 186}" y="{y + 9}">Product &amp; engineering</text>
  <rect class="gc" x="{tx + 338}" y="{y}" width="10" height="10" rx="2"/><text class="mute" x="{tx + 354}" y="{y + 9}">Compliance &amp; legal</text>
  <rect class="gd" x="{tx + 482}" y="{y}" width="10" height="10" rx="2"/><text class="mute" x="{tx + 498}" y="{y + 9}">Content</text>
</g>'''


count = dict(items)
GAP = 3
W, H = 1280, 420
TX, TY, TW, TH = 676, 44, 560, 332
tiles, n_rects = build_tiles(TX, TY, TW, TH)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Claude Skills</title>
<desc id="d">{total} skills across {len(items)} domains, drawn as a treemap where each tile is a domain sized by its number of skills.</desc>
<style>
  .bg{{fill:#f7f6f2}} .ink{{fill:#16181d}} .mute{{fill:#5b616b}} .acc{{fill:#c4572f}}
  .cmd{{fill:#ffffff;stroke:#dedbd2}} .cmdt{{fill:#16181d}}
  .ga{{fill:#c4572f}} .gb{{fill:#2f5bb8}} .gc{{fill:#14806a}} .gd{{fill:#8a5cc2}}
  .tl,.tn{{fill:#ffffff;font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
  .tl{{font-weight:800}} .tn{{font-weight:600;opacity:.92}}
  .sans{{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
  .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
  .tile{{animation:rise .5s cubic-bezier(.2,.7,.2,1) both, glow 26s ease-in-out infinite}}
  .tile rect{{transition:opacity .2s}}
  .cursor{{animation:blink 1.1s steps(1) infinite}}
  @keyframes rise{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
  @keyframes glow{{0%,94%,100%{{filter:none}}96%{{filter:brightness(1.35) saturate(1.1)}}}}
  @keyframes blink{{50%{{opacity:0}}}}
  @media (prefers-color-scheme:dark){{
    .bg{{fill:#0f1115}} .ink{{fill:#f1efe9}} .mute{{fill:#9aa1ad}} .acc{{fill:#ef8a5c}}
    .cmd{{fill:#171a20;stroke:#2a2f38}} .cmdt{{fill:#e9e6df}}
    .ga{{fill:#d0653b}} .gb{{fill:#3d6fd6}} .gc{{fill:#1a9a80}} .gd{{fill:#9a6ed6}}
  }}
  @media (prefers-reduced-motion:reduce){{.tile,.cursor{{animation:none}}}}
</style>
<rect class="bg" width="{W}" height="{H}"/>
<rect class="acc" x="64" y="70" width="44" height="6" rx="3"/>
<text class="ink sans" x="62" y="152" font-size="66" font-weight="800" letter-spacing="-2">Claude Skills</text>
<text class="mute sans" x="64" y="198" font-size="23" font-weight="500">Turn your AI assistant into a specialist.</text>
<text class="mute sans" x="64" y="230" font-size="17">{total} skills · {len(items)} domains · Python tools that compute, not guess</text>
<rect class="cmd" x="64" y="282" width="540" height="52" rx="10" stroke-width="1.5"/>
<text class="acc mono" x="86" y="315" font-size="17" font-weight="600">❯</text>
<text class="cmdt mono" x="108" y="315" font-size="17">/plugin marketplace add borghei/Claude-Skills</text>
<rect class="acc cursor" x="586" y="300" width="2" height="18"/>
{"".join(tiles)}
{legend(TX, TY + TH + 14)}
</svg>
'''
if args.social:
    agents = len(list((repo / "agents").rglob("cs-*.md"))) + len(
        [p for p in (repo / "agents" / "personas").glob("*.md") if p.name != "README.md"])
    tools = sum(d.get("tools", 0) for d in domains.values())
    SW, SH = 1280, 640
    STX, STY, STW, STH = 704, 92, 512, 424
    s_tiles, _ = build_tiles(STX, STY, STW, STH, animate=False)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SW} {SH}" width="{SW}" height="{SH}" role="img" aria-labelledby="t d">
<title id="t">Claude Skills</title>
<desc id="d">{total} skills across {len(items)} domains for Claude Code, Cursor, Codex and other AI assistants.</desc>
<style>
  .bg{{fill:#0f1115}} .ink{{fill:#f1efe9}} .mute{{fill:#9aa1ad}} .acc{{fill:#ef8a5c}} .num{{fill:#f1efe9}}
  .cmd{{fill:#171a20;stroke:#2a2f38}} .cmdt{{fill:#e9e6df}}
  .ga{{fill:#d0653b}} .gb{{fill:#3d6fd6}} .gc{{fill:#1a9a80}} .gd{{fill:#9a6ed6}}
  .tl,.tn{{fill:#ffffff;font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
  .tl{{font-weight:800}} .tn{{font-weight:600;opacity:.92}}
  .sans{{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
  .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
</style>
<rect class="bg" width="{SW}" height="{SH}"/>
<rect class="acc" x="72" y="118" width="52" height="7" rx="3.5"/>
<text class="ink sans" x="68" y="222" font-size="86" font-weight="800" letter-spacing="-3">Claude Skills</text>
<text class="mute sans" x="72" y="278" font-size="29" font-weight="500">Turn your AI assistant into a specialist.</text>
<g class="sans">
  <text x="72" y="368"><tspan class="num" font-size="40" font-weight="800">{total}</tspan><tspan class="mute" font-size="20" dx="8">skills</tspan></text>
  <text x="250" y="368"><tspan class="num" font-size="40" font-weight="800">{len(items)}</tspan><tspan class="mute" font-size="20" dx="8">domains</tspan></text>
  <text x="414" y="368"><tspan class="num" font-size="40" font-weight="800">{agents}</tspan><tspan class="mute" font-size="20" dx="8">agents</tspan></text>
  <text x="72" y="420"><tspan class="num" font-size="40" font-weight="800">{tools}</tspan><tspan class="mute" font-size="20" dx="8">Python tools that compute, not guess</tspan></text>
</g>
<rect class="cmd" x="72" y="462" width="560" height="56" rx="10" stroke-width="1.5"/>
<text class="acc mono" x="94" y="497" font-size="18" font-weight="600">❯</text>
<text class="cmdt mono" x="118" y="497" font-size="18">/plugin marketplace add borghei/Claude-Skills</text>
{"".join(s_tiles)}
{legend(STX, STY + STH + 16)}
<text class="mute mono" x="72" y="586" font-size="16">github.com/borghei/Claude-Skills</text>
</svg>
'''
if args.force_dark:
    svg = svg.replace("@media (prefers-color-scheme:dark){", "@media all{")
open(out, "w").write(svg)
print(f"Wrote {out} ({len(items)} domains, {total} skills)")
