#!/usr/bin/env python3
"""Build assets/header.svg: a theme-aware README banner with a treemap of skills per domain.

Reads the per-domain counts from skills.json, so re-run it after build_manifest.py
whenever skills are added or removed:

    python3 scripts/generate_header.py
    python3 scripts/generate_header.py --force-dark /tmp/dark.svg   # preview for renderers without @media

Standard library only.
"""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description="Generate the README header SVG from skills.json.")
parser.add_argument("out", nargs="?", help="Output path (default: assets/header.svg)")
parser.add_argument("--force-dark", action="store_true", help="Always use the dark palette (for previews)")
args = parser.parse_args()
repo = Path(__file__).resolve().parent.parent
out = Path(args.out) if args.out else repo / "assets" / "header.svg"
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


W, H = 1280, 420
TX, TY, TW, TH = 676, 44, 560, 332
scale = TW * TH / total
rects = squarify([(k, c * scale) for k, c in items], TX, TY, TW, TH)
count = dict(items)

GAP = 3
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
    tiles.append(
        f'<g class="tile" style="animation-delay:{0.15 + i * 0.06:.2f}s, {3 + i * 1.7:.1f}s">'
        f'<title>{LABEL[k]}: {count[k]} skills</title>'
        f'<rect class="g{g}" x="{x2:.1f}" y="{y2:.1f}" width="{w2:.1f}" height="{h2:.1f}" rx="5"/>{lab}</g>'
    )

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
<g class="sans" font-size="13">
  <rect class="ga" x="{TX}" y="{TY + TH + 14}" width="10" height="10" rx="2"/><text class="mute" x="{TX + 16}" y="{TY + TH + 23}">Leadership &amp; business</text>
  <rect class="gb" x="{TX + 170}" y="{TY + TH + 14}" width="10" height="10" rx="2"/><text class="mute" x="{TX + 186}" y="{TY + TH + 23}">Product &amp; engineering</text>
  <rect class="gc" x="{TX + 338}" y="{TY + TH + 14}" width="10" height="10" rx="2"/><text class="mute" x="{TX + 354}" y="{TY + TH + 23}">Compliance &amp; legal</text>
  <rect class="gd" x="{TX + 482}" y="{TY + TH + 14}" width="10" height="10" rx="2"/><text class="mute" x="{TX + 498}" y="{TY + TH + 23}">Content</text>
</g>
</svg>
'''
if args.force_dark:
    svg = svg.replace("@media (prefers-color-scheme:dark){", "@media all{")
open(out, "w").write(svg)
print(f"Wrote {out} ({len(rects)} domains, {total} skills)")
