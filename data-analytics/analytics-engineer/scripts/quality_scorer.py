#!/usr/bin/env python3
import argparse
import json
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Generate a quality score for a dbt model.")
    parser.add_argument("--model", required=True, help="Model to score")
    parser.add_argument("--manifest", default="target/manifest.json", help="Path to manifest")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    return parser.parse_args()

def load_json(path):
    if not os.path.exists(path):
        print(f"Error: Could not find {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r') as f:
        return json.load(f)

def run_checks(manifest, model_name):
    # Find node
    node = None
    for n_id, data in manifest.get("nodes", {}).items():
        if data.get("name") == model_name and data.get("resource_type") == "model":
            node = data
            break
            
    if not node:
        print(f"Error: Model {model_name} not found.", file=sys.stderr)
        sys.exit(1)
        
    score = 100
    deductions = []
    
    # Check 1: Model has a description
    if not node.get("description"):
        score -= 20
        deductions.append("-20: Model is missing a description in .yml")
        
    # Check 2: Column descriptions
    columns = node.get("columns", {})
    if not columns:
        score -= 20
        deductions.append("-20: No columns documented in .yml")
    else:
        undocumented = [c for c, d in columns.items() if not d.get("description")]
        if undocumented:
            penalty = min(20, len(undocumented) * 5)
            score -= penalty
            deductions.append(f"-{penalty}: {len(undocumented)} columns missing descriptions")
            
    # Check 3: Layer violations
    raw_sql = node.get("raw_code", "").upper()
    if model_name.startswith("stg_"):
        if " JOIN " in raw_sql:
            score -= 30
            deductions.append("-30: Staging model contains JOIN operations (Layer violation)")
        if "GROUP BY" in raw_sql:
            score -= 30
            deductions.append("-30: Staging model contains GROUP BY aggregations (Layer violation)")
            
    elif model_name.startswith("dim_") or model_name.startswith("fct_"):
        # Marts should probably have dependent intermediate or staging models
        parents = node.get("depends_on", {}).get("nodes", [])
        raw_sources = [p for p in parents if p.startswith("source.")]
        if raw_sources:
            score -= 20
            deductions.append("-20: Mart directly selects from source instead of staging (Layer violation)")

    # Check 4: Testing 
    # Look at tests bound to this node
    tests = []
    for child_id in manifest.get("child_map", {}).get(node["unique_id"], []):
        if child_id.startswith("test."):
            tests.append(child_id)
            
    if not tests:
        score -= 30
        deductions.append("-30: Model has zero tests configured")
        
    return {
        "model": model_name,
        "score": max(0, score),
        "deductions": deductions
    }

def main():
    args = parse_args()
    manifest = load_json(args.manifest)
    
    result = run_checks(manifest, args.model)
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
        
    print(f"Quality Score for: {result['model']}")
    print("=" * 40)

    score_display = ""
    if result['score'] >= 90: score_display = f"[PASS] {result['score']}/100 (Excellent)"
    elif result['score'] >= 70: score_display = f"[WARN] {result['score']}/100 (Needs Work)"
    else: score_display = f"[FAIL] {result['score']}/100 (Critical Action Required)"

    print(score_display)

    if result['deductions']:
        print("\nDeductions:")
        for r in result['deductions']:
            print(f"  {r}")
    else:
        print("\nPerfect Score! Model follows all enforced conventions.")

if __name__ == "__main__":
    main()
