#!/usr/bin/env python3
import argparse
import json
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Compare two dbt catalog.json files to detect schema drift.")
    parser.add_argument("--source", required=True, help="Path to source catalog.json (e.g. prod)")
    parser.add_argument("--target", required=True, help="Path to target catalog.json (e.g. dev)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    return parser.parse_args()

def load_catalog(path):
    if not os.path.exists(path):
        print(f"Error: Catalog not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r') as f:
        return json.load(f)

def build_schema_map(catalog):
    nodes = catalog.get("nodes", {})
    schema_map = {}
    for node_id, data in nodes.items():
        if node_id.startswith("model."):
            model_name = data.get("metadata", {}).get("name", node_id)
            columns = data.get("columns", {})
            schema_map[model_name] = {
                c_name.lower(): c_data.get("type", "UNKNOWN").upper()
                for c_name, c_data in columns.items()
            }
    return schema_map

def compare_schemas(source_map, target_map):
    results = {
        "new_models": [],
        "dropped_models": [],
        "modified_models": {}
    }
    
    for model, s_cols in source_map.items():
        if model not in target_map:
            results["dropped_models"].append(model)
        else:
            t_cols = target_map[model]
            model_diff = {"new_columns": [], "dropped_columns": [], "type_changes": []}
            
            for c_name, c_type in s_cols.items():
                if c_name not in t_cols:
                    model_diff["dropped_columns"].append(c_name)
                elif t_cols[c_name] != c_type:
                    model_diff["type_changes"].append({
                        "column": c_name,
                        "old_type": c_type,
                        "new_type": t_cols[c_name]
                    })
                    
            for c_name in t_cols.keys():
                if c_name not in s_cols:
                    model_diff["new_columns"].append(c_name)
                    
            if any(model_diff.values()):
                results["modified_models"][model] = model_diff
                
    for model in target_map.keys():
        if model not in source_map:
            results["new_models"].append(model)
            
    return results

def main():
    args = parse_args()
    source_cat = load_catalog(args.source)
    target_cat = load_catalog(args.target)
    
    source_map = build_schema_map(source_cat)
    target_map = build_schema_map(target_cat)
    
    diff = compare_schemas(source_map, target_map)
    
    if args.json:
        print(json.dumps(diff, indent=2))
        return
        
    print("🔍 Schema Diff Analysis")
    print("=" * 40)
    print(f"New Models Added   : {len(diff['new_models'])}")
    print(f"Models Dropped     : {len(diff['dropped_models'])}")
    print(f"Models Modified    : {len(diff['modified_models'])}")
    
    if diff["dropped_models"]:
        print("\n⚠️  WARNING: Models Dropped")
        for m in diff["dropped_models"]:
            print(f"  - {m}")
            
    if diff["modified_models"]:
        print("\n📊 Model Modifications:")
        for model, changes in diff["modified_models"].items():
            if changes["dropped_columns"]:
                print(f"\n  [!] {model} - DROPPED COLUMNS (Breaking Change!):")
                for c in changes["dropped_columns"]:
                    print(f"      - {c}")
            if changes["type_changes"]:
                print(f"\n  [~] {model} - TYPE CHANGES:")
                for tc in changes["type_changes"]:
                    print(f"      - {tc['column']}: {tc['old_type']} -> {tc['new_type']}")
            if changes["new_columns"]:
                print(f"\n  [+] {model} - NEW COLUMNS:")
                for c in changes["new_columns"]:
                    print(f"      - {c}")

if __name__ == "__main__":
    main()
