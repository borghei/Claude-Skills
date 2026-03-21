#!/usr/bin/env python3
import argparse
import json
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze downstream impact of a dbt model.")
    parser.add_argument("--model", required=True, help="Name of the dbt model (e.g., fct_orders)")
    parser.add_argument("--manifest", default="target/manifest.json", help="Path to dbt manifest.json")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    return parser.parse_args()

def load_manifest(manifest_path):
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest file not found at {manifest_path}. Have you run 'dbt compile'?", file=sys.stderr)
        sys.exit(1)
    with open(manifest_path, 'r') as f:
        return json.load(f)

def build_parent_map(manifest):
    """Returns a map of node -> children (downstream)"""
    return manifest.get("child_map", {})

def get_node_id(manifest, model_name):
    # Search for model node
    nodes = manifest.get("nodes", {})
    for node_id, node_data in nodes.items():
        if node_data.get("name") == model_name and node_data.get("resource_type") == "model":
            return node_id
    return None

def analyze_impact(manifest, model_name):
    node_id = get_node_id(manifest, model_name)
    if not node_id:
        print(f"Error: Model '{model_name}' not found in manifest.", file=sys.stderr)
        sys.exit(1)
    
    child_map = build_parent_map(manifest)
    
    # BFS to find all downstream
    queue = [node_id]
    visited = set()
    exposures = []
    downstream_models = []
    tests = []
    
    nodes = manifest.get("nodes", {})
    manifest_exposures = manifest.get("exposures", {})
    
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        
        children = child_map.get(current, [])
        for child in children:
            if child not in visited:
                queue.append(child)
                child_type = child.split('.')[0]
                if child_type == "model":
                    downstream_models.append(nodes.get(child, {}).get("name", child))
                elif child_type == "test":
                    tests.append(child)
                elif child_type == "exposure":
                    exposures.append(manifest_exposures.get(child, {}).get("name", child))
    
    return {
        "model": model_name,
        "direct_and_indirect_children_count": len(visited) - 1,
        "downstream_models": list(set(downstream_models)),
        "downstream_exposures": list(set(exposures)),
        "downstream_tests": len(set(tests))
    }

def main():
    args = parse_args()
    manifest = load_manifest(args.manifest)
    impact = analyze_impact(manifest, args.model)
    
    if args.json:
        print(json.dumps(impact, indent=2))
    else:
        print(f"🔍 Impact Analysis for: {impact['model']}")
        print("=" * 40)
        print(f"Total Downstream Nodes : {impact['direct_and_indirect_children_count']}")
        print(f"Downstream Tests      : {impact['downstream_tests']}")
        print(f"\n📊 Downstream Models ({len(impact['downstream_models'])}):")
        for m in sorted(impact['downstream_models']):
            print(f"  - {m}")
        
        print(f"\n⚠️  Downstream Exposures ({len(impact['downstream_exposures'])}):")
        if not impact['downstream_exposures']:
            print("  None")
        for e in sorted(impact['downstream_exposures']):
            print(f"  - Dashboard/App: {e}")

if __name__ == "__main__":
    main()
