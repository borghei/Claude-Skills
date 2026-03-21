#!/usr/bin/env python3
"""Positioning Map Generator - Create competitive positioning maps from attribute data.

Plots brands on a 2-axis positioning map, identifies white space opportunities,
and calculates positioning distance between competitors.

Usage:
    python positioning_map_generator.py competitors.json
    python positioning_map_generator.py competitors.json --json
    python positioning_map_generator.py --demo
"""

import argparse
import json
import math
import sys


def calculate_distance(brand_a, brand_b):
    """Calculate Euclidean distance between two brands on the map."""
    dx = brand_a["x"] - brand_b["x"]
    dy = brand_a["y"] - brand_b["y"]
    return math.sqrt(dx * dx + dy * dy)


def find_clusters(brands, threshold=20):
    """Find clusters of brands that are positioned closely."""
    clusters = []
    assigned = set()

    for i, brand_a in enumerate(brands):
        if i in assigned:
            continue
        cluster = [brand_a]
        assigned.add(i)
        for j, brand_b in enumerate(brands):
            if j in assigned:
                continue
            if calculate_distance(brand_a, brand_b) < threshold:
                cluster.append(brand_b)
                assigned.add(j)
        if len(cluster) > 1:
            clusters.append(cluster)

    return clusters


def find_white_space(brands, grid_size=10):
    """Find positioning white space (empty areas on the map)."""
    # Create a grid and mark occupied cells
    grid = {}
    for x in range(0, 101, grid_size):
        for y in range(0, 101, grid_size):
            grid[(x, y)] = True  # True = available

    for brand in brands:
        bx = round(brand["x"] / grid_size) * grid_size
        by = round(brand["y"] / grid_size) * grid_size
        # Mark surrounding cells as occupied
        for dx in range(-grid_size, grid_size * 2, grid_size):
            for dy in range(-grid_size, grid_size * 2, grid_size):
                key = (bx + dx, by + dy)
                if key in grid:
                    grid[key] = False

    # Find available spaces
    white_spaces = []
    for (x, y), available in grid.items():
        if available and 10 <= x <= 90 and 10 <= y <= 90:
            # Calculate minimum distance to nearest brand
            min_dist = min(
                math.sqrt((x - b["x"]) ** 2 + (y - b["y"]) ** 2)
                for b in brands
            ) if brands else 100

            white_spaces.append({
                "x": x,
                "y": y,
                "distance_to_nearest": round(min_dist, 1),
            })

    # Sort by distance (most open space first)
    white_spaces.sort(key=lambda w: w["distance_to_nearest"], reverse=True)
    return white_spaces[:5]  # Top 5 opportunities


def generate_text_map(brands, x_axis, y_axis, width=60, height=25):
    """Generate an ASCII text positioning map."""
    lines = []
    lines.append(f"  {y_axis.get('high', 'High')}")
    lines.append("  " + "-" * width)

    # Create grid
    grid = [[" " for _ in range(width)] for _ in range(height)]

    # Place brands on grid
    for brand in brands:
        gx = int(brand["x"] / 100 * (width - 1))
        gy = int((100 - brand["y"]) / 100 * (height - 1))  # Invert Y
        gx = max(0, min(width - 1, gx))
        gy = max(0, min(height - 1, gy))

        label = brand.get("name", "?")[:6]
        # Place marker
        for ci, ch in enumerate(label):
            if gx + ci < width:
                grid[gy][gx + ci] = ch

    # Add axis labels and borders
    for row in grid:
        lines.append("  |" + "".join(row) + "|")

    lines.append("  " + "-" * width)
    x_low = x_axis.get("low", "Low")
    x_high = x_axis.get("high", "High")
    padding = width - len(x_low) - len(x_high)
    lines.append(f"  {x_low}{' ' * max(padding, 1)}{x_high}")
    lines.append(f"  {y_axis.get('low', 'Low')}")

    return "\n".join(lines)


def analyze_positioning(data):
    """Analyze competitive positioning data."""
    brands = data.get("brands", data.get("competitors", []))
    x_axis = data.get("x_axis", {"label": "X Axis", "low": "Low", "high": "High"})
    y_axis = data.get("y_axis", {"label": "Y Axis", "low": "Low", "high": "High"})

    # Calculate distances between all pairs
    distances = []
    for i, a in enumerate(brands):
        for j, b in enumerate(brands):
            if i < j:
                dist = calculate_distance(a, b)
                distances.append({
                    "brand_a": a.get("name", f"Brand {i}"),
                    "brand_b": b.get("name", f"Brand {j}"),
                    "distance": round(dist, 1),
                })

    distances.sort(key=lambda d: d["distance"])

    # Find clusters and white space
    clusters = find_clusters(brands)
    white_spaces = find_white_space(brands)

    # Identify the most differentiated brand
    avg_distances = {}
    for brand in brands:
        name = brand.get("name", "unknown")
        dists = [d["distance"] for d in distances if name in (d["brand_a"], d["brand_b"])]
        avg_distances[name] = round(sum(dists) / len(dists), 1) if dists else 0

    most_differentiated = max(avg_distances.items(), key=lambda x: x[1]) if avg_distances else None
    least_differentiated = min(avg_distances.items(), key=lambda x: x[1]) if avg_distances else None

    # Quadrant analysis
    quadrants = {"top_right": [], "top_left": [], "bottom_right": [], "bottom_left": []}
    for brand in brands:
        name = brand.get("name", "unknown")
        if brand["x"] >= 50 and brand["y"] >= 50:
            quadrants["top_right"].append(name)
        elif brand["x"] < 50 and brand["y"] >= 50:
            quadrants["top_left"].append(name)
        elif brand["x"] >= 50 and brand["y"] < 50:
            quadrants["bottom_right"].append(name)
        else:
            quadrants["bottom_left"].append(name)

    return {
        "brands": brands,
        "axes": {"x": x_axis, "y": y_axis},
        "distances": distances,
        "clusters": [[b.get("name", "?") for b in c] for c in clusters],
        "white_space_opportunities": white_spaces,
        "quadrants": quadrants,
        "most_differentiated": {"name": most_differentiated[0], "avg_distance": most_differentiated[1]} if most_differentiated else None,
        "least_differentiated": {"name": least_differentiated[0], "avg_distance": least_differentiated[1]} if least_differentiated else None,
        "avg_distances": avg_distances,
    }


def get_demo_data():
    return {
        "x_axis": {"label": "Innovation", "low": "Traditional", "high": "Innovative"},
        "y_axis": {"label": "Price", "low": "Affordable", "high": "Premium"},
        "brands": [
            {"name": "Us", "x": 75, "y": 60},
            {"name": "CompA", "x": 30, "y": 80},
            {"name": "CompB", "x": 80, "y": 85},
            {"name": "CompC", "x": 25, "y": 30},
            {"name": "CompD", "x": 60, "y": 40},
        ],
    }


def format_report(analysis):
    """Format human-readable positioning analysis."""
    lines = []
    lines.append("=" * 65)
    lines.append("COMPETITIVE POSITIONING MAP ANALYSIS")
    lines.append("=" * 65)

    # Text map
    lines.append(generate_text_map(
        analysis["brands"],
        analysis["axes"]["x"],
        analysis["axes"]["y"],
    ))
    lines.append("")

    # Quadrant analysis
    lines.append("--- QUADRANT ANALYSIS ---")
    x_axis = analysis["axes"]["x"]
    y_axis = analysis["axes"]["y"]
    lines.append(f"  {y_axis.get('high','High')} + {x_axis.get('high','High')}: {', '.join(analysis['quadrants']['top_right']) or 'Empty'}")
    lines.append(f"  {y_axis.get('high','High')} + {x_axis.get('low','Low')}: {', '.join(analysis['quadrants']['top_left']) or 'Empty'}")
    lines.append(f"  {y_axis.get('low','Low')} + {x_axis.get('high','High')}: {', '.join(analysis['quadrants']['bottom_right']) or 'Empty'}")
    lines.append(f"  {y_axis.get('low','Low')} + {x_axis.get('low','Low')}: {', '.join(analysis['quadrants']['bottom_left']) or 'Empty'}")
    lines.append("")

    # Closest competitors
    if analysis["distances"]:
        lines.append("--- CLOSEST COMPETITORS ---")
        for d in analysis["distances"][:3]:
            lines.append(f"  {d['brand_a']} <-> {d['brand_b']}: distance {d['distance']}")
        lines.append("")

    # Clusters
    if analysis["clusters"]:
        lines.append("--- COMPETITIVE CLUSTERS ---")
        for i, cluster in enumerate(analysis["clusters"], 1):
            lines.append(f"  Cluster {i}: {', '.join(cluster)}")
        lines.append("")

    # Differentiation
    if analysis["most_differentiated"]:
        md = analysis["most_differentiated"]
        lines.append(f"Most differentiated: {md['name']} (avg distance: {md['avg_distance']})")
    if analysis["least_differentiated"]:
        ld = analysis["least_differentiated"]
        lines.append(f"Least differentiated: {ld['name']} (avg distance: {ld['avg_distance']})")
    lines.append("")

    # White space
    if analysis["white_space_opportunities"]:
        lines.append("--- WHITE SPACE OPPORTUNITIES ---")
        for ws in analysis["white_space_opportunities"][:3]:
            lines.append(f"  Position ({ws['x']}, {ws['y']}): {ws['distance_to_nearest']:.0f} units from nearest competitor")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate competitive positioning maps")
    parser.add_argument("input", nargs="?", help="JSON file with competitor positioning data")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = analyze_positioning(data)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
