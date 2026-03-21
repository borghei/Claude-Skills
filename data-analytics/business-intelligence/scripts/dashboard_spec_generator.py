#!/usr/bin/env python3
"""Generate dashboard layout specifications from KPI definitions.

Reads a KPI definitions file and produces a structured dashboard
specification with chart types, layout positions, filters, and
recommended visualizations.

Usage:
    python dashboard_spec_generator.py --definitions kpis.json
    python dashboard_spec_generator.py --definitions kpis.json --title "Sales Dashboard" --json
    python dashboard_spec_generator.py --definitions kpis.json --layout 2-column

KPI definition format:
[
    {
        "name": "Monthly Revenue",
        "type": "currency",
        "aggregation": "sum",
        "dimensions": ["region", "product"],
        "time_grain": "monthly",
        "target": 100000,
        "chart_hint": "trend"
    }
]
"""

import argparse
import json
import os
import sys
from datetime import datetime


# ---------------------------------------------------------------------------
# Chart type selection logic
# ---------------------------------------------------------------------------

CHART_RULES = {
    "trend": {"chart": "line", "alt": "area", "reason": "Shows metric change over time"},
    "comparison": {"chart": "bar", "alt": "column", "reason": "Compares values across categories"},
    "composition": {"chart": "donut", "alt": "stacked_bar", "reason": "Shows parts of a whole"},
    "distribution": {"chart": "histogram", "alt": "box_plot", "reason": "Shows data distribution"},
    "kpi_card": {"chart": "scorecard", "alt": "gauge", "reason": "Highlights a single key metric"},
    "table": {"chart": "data_table", "alt": "pivot_table", "reason": "Shows detailed records"},
    "geographic": {"chart": "choropleth", "alt": "bubble_map", "reason": "Maps data geographically"},
}


def _infer_chart_type(kpi: dict) -> str:
    """Infer best chart type from KPI definition."""
    if kpi.get("chart_hint"):
        return kpi["chart_hint"]
    agg = kpi.get("aggregation", "sum")
    dims = kpi.get("dimensions", [])
    time_grain = kpi.get("time_grain")

    if time_grain and not dims:
        return "trend"
    if time_grain and dims:
        return "trend"  # trend with dimension breakdown
    if len(dims) == 0:
        return "kpi_card"
    if len(dims) == 1:
        return "comparison"
    if any(d in ("region", "country", "state", "city") for d in dims):
        return "geographic"
    return "comparison"


def _generate_widget(kpi: dict, position: int, layout: str) -> dict:
    chart_key = _infer_chart_type(kpi)
    chart_info = CHART_RULES.get(chart_key, CHART_RULES["kpi_card"])

    # Calculate grid position
    if layout == "2-column":
        cols = 2
    elif layout == "3-column":
        cols = 3
    else:
        cols = 2

    row = position // cols
    col = position % cols

    widget = {
        "id": f"widget_{position + 1}",
        "title": kpi["name"],
        "chart_type": chart_info["chart"],
        "alt_chart_type": chart_info["alt"],
        "chart_rationale": chart_info["reason"],
        "metric": {
            "name": kpi["name"],
            "aggregation": kpi.get("aggregation", "sum"),
            "type": kpi.get("type", "number"),
        },
        "layout": {
            "row": row,
            "col": col,
            "width": 1,
            "height": 1,
        },
    }

    if kpi.get("dimensions"):
        widget["dimensions"] = kpi["dimensions"]

    if kpi.get("time_grain"):
        widget["time_grain"] = kpi["time_grain"]

    if kpi.get("target") is not None:
        widget["target"] = kpi["target"]
        widget["show_target_line"] = True

    if kpi.get("filters"):
        widget["filters"] = kpi["filters"]

    return widget


def generate_dashboard_spec(kpi_defs: list, title: str, layout: str) -> dict:
    widgets = []

    # KPI cards come first (top row)
    kpi_cards = []
    detail_widgets = []
    for kpi in kpi_defs:
        chart_type = _infer_chart_type(kpi)
        if chart_type == "kpi_card":
            kpi_cards.append(kpi)
        else:
            detail_widgets.append(kpi)

    position = 0
    for kpi in kpi_cards:
        w = _generate_widget(kpi, position, layout)
        w["section"] = "summary"
        widgets.append(w)
        position += 1

    for kpi in detail_widgets:
        w = _generate_widget(kpi, position, layout)
        w["section"] = "detail"
        widgets.append(w)
        position += 1

    # Global filters
    all_dims = set()
    for kpi in kpi_defs:
        all_dims.update(kpi.get("dimensions", []))

    time_grains = set()
    for kpi in kpi_defs:
        if kpi.get("time_grain"):
            time_grains.add(kpi["time_grain"])

    filters = []
    if time_grains:
        filters.append({
            "name": "date_range",
            "type": "date_range",
            "default": "last_30_days",
        })
    for dim in sorted(all_dims):
        filters.append({
            "name": dim,
            "type": "multi_select",
            "default": "all",
        })

    spec = {
        "dashboard": {
            "title": title,
            "layout": layout,
            "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "total_widgets": len(widgets),
            "sections": {
                "summary": sum(1 for w in widgets if w.get("section") == "summary"),
                "detail": sum(1 for w in widgets if w.get("section") == "detail"),
            },
        },
        "global_filters": filters,
        "widgets": widgets,
        "design_notes": [
            "Place summary KPI cards in the top row for immediate visibility.",
            "Trend charts should show comparison to target or prior period.",
            "Limit dashboard to 5-8 widgets per page for readability.",
            "Use consistent color palette: GREEN #28A745, YELLOW #FFC107, RED #DC3545.",
            "Dashboard load time target: < 5 seconds.",
        ],
    }

    return spec


def _format_text(spec: dict) -> str:
    lines = []
    d = spec["dashboard"]
    lines.append(f"Dashboard Specification: {d['title']}")
    lines.append("=" * 60)
    lines.append(f"Layout: {d['layout']}  |  Widgets: {d['total_widgets']}  |  Generated: {d['generated_at']}")
    lines.append(f"Summary cards: {d['sections']['summary']}  |  Detail charts: {d['sections']['detail']}")
    lines.append("")

    if spec.get("global_filters"):
        lines.append("Global Filters:")
        for f in spec["global_filters"]:
            lines.append(f"  - {f['name']} ({f['type']}, default: {f['default']})")
        lines.append("")

    lines.append("Widgets:")
    lines.append("-" * 60)
    for w in spec["widgets"]:
        target_str = f"  Target: {w['target']}" if w.get("target") else ""
        dims_str = f"  Dimensions: {', '.join(w['dimensions'])}" if w.get("dimensions") else ""
        lines.append(f"  [{w['id']}] {w['title']}")
        lines.append(f"    Chart: {w['chart_type']} (alt: {w['alt_chart_type']})")
        lines.append(f"    Reason: {w['chart_rationale']}")
        lines.append(f"    Position: row={w['layout']['row']}, col={w['layout']['col']}")
        if target_str:
            lines.append(f"   {target_str}")
        if dims_str:
            lines.append(f"   {dims_str}")
        if w.get("time_grain"):
            lines.append(f"    Time grain: {w['time_grain']}")
        lines.append("")

    lines.append("Design Notes:")
    for note in spec.get("design_notes", []):
        lines.append(f"  - {note}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate dashboard layout specifications from KPI definitions.")
    parser.add_argument("--definitions", required=True, help="Path to KPI definitions JSON file")
    parser.add_argument("--title", default="Analytics Dashboard", help="Dashboard title")
    parser.add_argument("--layout", choices=["2-column", "3-column"], default="2-column", help="Layout style")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not os.path.exists(args.definitions):
        print(f"Error: File not found: {args.definitions}", file=sys.stderr)
        sys.exit(1)

    with open(args.definitions, "r") as f:
        kpi_defs = json.load(f)

    if not isinstance(kpi_defs, list) or not kpi_defs:
        print("Error: Definitions file must contain a non-empty JSON array.", file=sys.stderr)
        sys.exit(1)

    spec = generate_dashboard_spec(kpi_defs, args.title, args.layout)

    if args.json:
        print(json.dumps(spec, indent=2))
    else:
        print(_format_text(spec))

    sys.exit(0)


if __name__ == "__main__":
    main()
