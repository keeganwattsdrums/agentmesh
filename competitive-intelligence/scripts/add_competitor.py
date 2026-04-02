#!/usr/bin/env python3
"""
Add a new competitor to the tracking database.
"""

import sqlite3
import os
import argparse

DB_PATH = os.path.expanduser("~/competitive-intel.db")

def add_competitor(name, category, website, pricing_url=None, docs_url=None, 
                   description=None, founded=None, funding=None):
    """Add a new competitor to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO competitors 
            (name, category, website, pricing_url, docs_url, description, founded, funding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, website, pricing_url, docs_url, description, founded, funding))
        
        conn.commit()
        print(f"✓ Added competitor: {name}")
        print(f"  Category: {category}")
        print(f"  Website: {website}")
        
    except sqlite3.IntegrityError:
        print(f"⚠ Competitor '{name}' already exists")
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description="Add a competitor to tracking")
    parser.add_argument("--name", required=True, help="Competitor name")
    parser.add_argument("--category", required=True, 
                       choices=["memory", "observability", "vector-db", "agent-framework"],
                       help="Category")
    parser.add_argument("--website", required=True, help="Website URL")
    parser.add_argument("--pricing-url", help="Pricing page URL")
    parser.add_argument("--docs-url", help="Documentation URL")
    parser.add_argument("--description", help="Brief description")
    parser.add_argument("--founded", help="Year founded")
    parser.add_argument("--funding", help="Funding information")
    args = parser.parse_args()
    
    if not os.path.exists(DB_PATH):
        print("⚠ Database not found. Run init_tracking.py first.")
        return
    
    add_competitor(
        args.name, 
        args.category, 
        args.website,
        args.pricing_url,
        args.docs_url,
        args.description,
        args.founded,
        args.funding
    )

if __name__ == "__main__":
    main()
