#!/usr/bin/env python3
"""
Compare pricing across competitors within a category or all competitors.
Outputs formatted comparison tables.
"""

import sqlite3
import os
import argparse

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

DB_PATH = os.path.expanduser("~/competitive-intel.db")

def get_pricing_by_category(category=None):
    """Get pricing data organized by category."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if category:
        cursor.execute('''
            SELECT c.name, c.category, p.tier, p.price, p.unit, p.limits
            FROM competitors c
            JOIN pricing p ON c.id = p.competitor_id
            WHERE c.category = ?
            ORDER BY c.name, p.price ASC NULLS LAST
        ''', (category,))
    else:
        cursor.execute('''
            SELECT c.name, c.category, p.tier, p.price, p.unit, p.limits
            FROM competitors c
            JOIN pricing p ON c.id = p.competitor_id
            ORDER BY c.category, c.name, p.price ASC NULLS LAST
        ''')
    
    results = cursor.fetchall()
    conn.close()
    return results

def format_price(price, unit):
    """Format price for display."""
    if price is None:
        return f"Custom/{unit}"
    if price == 0:
        return "Free"
    return f"${price}/{unit}"

def compare_pricing(category=None, output_format="table"):
    """Generate pricing comparison."""
    data = get_pricing_by_category(category)
    
    if not data:
        print("No pricing data found.")
        return
    
    # Organize by competitor
    competitors = {}
    for row in data:
        name, cat, tier, price, unit, limits = row
        if name not in competitors:
            competitors[name] = {"category": cat, "tiers": []}
        competitors[name]["tiers"].append({
            "tier": tier,
            "price": format_price(price, unit),
            "limits": limits
        })
    
    if output_format == "markdown":
        print("## Pricing Comparison\n")
        
        current_category = None
        for name, info in competitors.items():
            if info["category"] != current_category:
                current_category = info["category"]
                print(f"\n### {current_category.upper()}\n")
            
            print(f"**{name}**")
            for tier in info["tiers"]:
                print(f"- {tier['tier']}: {tier['price']} ({tier['limits']})")
            print()
    
    elif output_format == "json":
        import json
        print(json.dumps(competitors, indent=2))
    
    else:  # table
        table_data = []
        for name, info in competitors.items():
            for tier in info["tiers"]:
                table_data.append([
                    name,
                    info["category"],
                    tier["tier"],
                    tier["price"],
                    tier["limits"]
                ])
        
        if HAS_TABULATE:
            print(tabulate(table_data, 
                          headers=["Competitor", "Category", "Tier", "Price", "Limits"],
                          tablefmt="grid"))
        else:
            # Simple fallback table
            print(f"{'Competitor':<15} {'Category':<15} {'Tier':<15} {'Price':<15} {'Limits'}")
            print("-" * 80)
            for row in table_data:
                print(f"{row[0]:<15} {row[1]:<15} {row[2]:<15} {row[3]:<15} {row[4]}")

def main():
    parser = argparse.ArgumentParser(description="Compare competitor pricing")
    parser.add_argument("--category", help="Filter by category (memory, observability, vector-db, agent-framework)")
    parser.add_argument("--output", choices=["table", "markdown", "json"], 
                       default="table", help="Output format")
    args = parser.parse_args()
    
    if not os.path.exists(DB_PATH):
        print("⚠ Database not found. Run init_tracking.py first.")
        return
    
    compare_pricing(args.category, args.output)

if __name__ == "__main__":
    main()
