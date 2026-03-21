#!/usr/bin/env python3
import argparse
import json
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Generate markdown documentation from dbt manifest/catalog.")
    parser.add_argument("--model", required=True, help="Model name to generate documentation for")
    parser.add_argument("--manifest", default="target/manifest.json", help="Path to manifest.json")
    parser.add_argument("--catalog", default="target/catalog.json", help="Path to catalog.json (optional)")
    return parser.parse_args()

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def generate_markdown(manifest, catalog, model_name):
    # Find model in manifest
    model_node = None
    for node_id, data in manifest.get("nodes", {}).items():
        if data.get("name") == model_name:
            model_node = data
            break
            
    if not model_node:
        print(f"Error: Model {model_name} not found.", file=sys.stderr)
        sys.exit(1)
        
    description = model_node.get("description", "No description provided.")
    columns = model_node.get("columns", {})
    depends_on = model_node.get("depends_on", {}).get("nodes", [])
    
    # Try to overlay types from catalog
    cat_node = None
    for cat_id, data in catalog.get("nodes", {}).items():
        if data.get("metadata", {}).get("name") == model_name:
            cat_node = data
            break
            
    md = [f"# Model: `{model_name}`\n"]
    md.append(f"**Description:** {description}\n")
    
    md.append("## Dependencies")
    if depends_on:
        for dep in depends_on:
            dep_name = dep.split('.')[-1]
            md.append(f"- `{dep_name}`")
    else:
        md.append("*No dependencies*")
    md.append("\n")
    
    md.append("## Column Dictionary")
    md.append("| Column Name | Type | Description | Tests |")
    md.append("|---|---|---|---|")
    
    for c_name, c_data in columns.items():
        desc = c_data.get("description", "")
        # Get tests
        tests = []
        for child_id in manifest.get("child_map", {}).get(model_node["unique_id"], []):
            if child_id.startswith("test."):
                child_data = manifest.get("nodes", {}).get(child_id, {})
                if child_data.get("column_name") == c_name:
                    test_type = child_id.split('.')[1]
                    tests.append(test_type)
        
        test_str = ", ".join(tests) if tests else "none"
        
        c_type = "UNKNOWN"
        if cat_node and c_name in cat_node.get("columns", {}):
            c_type = cat_node["columns"][c_name].get("type", "UNKNOWN")
            
        md.append(f"| `{c_name}` | `{c_type}` | {desc} | {test_str} |")
        
    return "\n".join(md)

def main():
    args = parse_args()
    manifest = load_json(args.manifest)
    catalog = load_json(args.catalog)
    
    if not manifest:
        print(f"Error: Manifest not found at {args.manifest}", file=sys.stderr)
        sys.exit(1)
        
    md = generate_markdown(manifest, catalog, args.model)
    print(md)

if __name__ == "__main__":
    main()
