#!/usr/bin/env python3
"""
Generate feature comparison matrices across competitors.
"""

import sqlite3
import os
import argparse
import json

DB_PATH = os.path.expanduser("~/competitive-intel.db")

CATEGORY_FEATURES = {
    "memory": ["memory_type", "integration", "deployment", "api_type", "persistence", "multi_user"],
    "observability": ["tracing", "evaluation", "prompt_management", "monitoring", "integration", "cost_tracking"],
    "vector-db": ["indexing", "metadata_filtering", "hybrid_search", "scaling", "deployment", "query_interface"],
    "agent-framework": ["agent_types", "conversation_flow", "code_execution", "human_in_loop", "tools", "process"]
}

def get_features_by_category(category=None):
    """Get feature data organized by category."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if category:
        cursor.execute('''
            SELECT c.name, c.category, f.feature_name, f.feature_value
            FROM competitors c
            JOIN features f ON c.id = f.competitor_id
            WHERE c.category = ?
            ORDER BY c.name, f.feature_name
        ''', (category,))
    else:
        cursor.execute('''
            SELECT c.name, c.category, f.feature_name, f.feature_value
            FROM competitors c
            JOIN features f ON c.id = f.competitor_id
            ORDER BY c.category, c.name, f.feature_name
        ''')
    
    results = cursor.fetchall()
    conn.close()
    return results

def generate_matrix(category=None, output_format="markdown"):
    """Generate feature comparison matrix."""
    data = get_features_by_category(category)
    
    if not data:
        print("No feature data found.")
        return
    
    # Organize by competitor
    competitors = {}
    for row in data:
        name, cat, feature, value = row
        if name not in competitors:
            competitors[name] = {"category": cat, "features": {}}
        try:
            value = json.loads(value)
        except:
            pass
        competitors[name]["features"][feature] = value
    
    if output_format == "markdown":
        print("## Feature Comparison Matrix\n")
        
        current_category = None
        for name, info in competitors.items():
            if info["category"] != current_category:
                current_category = info["category"]
                print(f"\n### {current_category.upper()}\n")
            
            print(f"**{name}**")
            for feature, value in sorted(info["features"].items()):
                if isinstance(value, list):
                    value = ", ".join(value)
                print(f"- {feature.replace('_', ' ').title()}: {value}")
            print()
    
    elif output_format == "json":
        print(json.dumps(competitors, indent=2))
    
    elif output_format == "csv":
        import csv
        import sys
        
        # Get all unique features
        all_features = set()
        for info in competitors.values():
            all_features.update(info["features"].keys())
        all_features = sorted(all_features)
        
        writer = csv.writer(sys.stdout)
        headers = ["Competitor", "Category"] + [f.replace('_', ' ').title() for f in all_features]
        writer.writerow(headers)
        
        for name, info in competitors.items():
            row = [name, info["category"]]
            for feature in all_features:
                value = info["features"].get(feature, "N/A")
                if isinstance(value, list):
                    value = "; ".join(value)
                row.append(value)
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="Compare competitor features")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--output", choices=["markdown", "json", "csv"], 
                       default="markdown", help="Output format")
    args = parser.parse_args()
    
    if not os.path.exists(DB_PATH):
        print("⚠ Database not found. Run init_tracking.py first.")
        return
    
    generate_matrix(args.category, args.output)

if __name__ == "__main__":
    main()
