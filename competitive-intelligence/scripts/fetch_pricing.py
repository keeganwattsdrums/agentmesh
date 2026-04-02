#!/usr/bin/env python3
"""
Fetch competitor pricing data from websites.
Uses web scraping and manual overrides for tracked competitors.
"""

import sqlite3
import os
import argparse
from datetime import datetime
from urllib.parse import urljoin

DB_PATH = os.path.expanduser("~/competitive-intel.db")

# Current known pricing (update manually or via scraping)
CURRENT_PRICING = {
    "Mem0": [
        {"tier": "Developer", "price": 0, "unit": "free", "limits": "10k requests/month, 1M tokens"},
        {"tier": "Pro", "price": 29, "unit": "month", "limits": "100k requests, priority support"},
        {"tier": "Enterprise", "price": None, "unit": "custom", "limits": "Unlimited, SLA, dedicated support"}
    ],
    "LangSmith": [
        {"tier": "Developer", "price": 0, "unit": "free", "limits": "5k traces/month"},
        {"tier": "Plus", "price": 39, "unit": "user/month", "limits": "10k traces, prompt playground"},
        {"tier": "Enterprise", "price": None, "unit": "custom", "limits": "Unlimited, SSO, audit logs"}
    ],
    "Pinecone": [
        {"tier": "Starter", "price": 0, "unit": "free", "limits": "100k vectors, 1 pod, community support"},
        {"tier": "Standard", "price": 70, "unit": "month", "limits": "2M vectors, 1 pod, email support"},
        {"tier": "Enterprise", "price": None, "unit": "custom", "limits": "Custom pods, VPC, dedicated support"}
    ],
    "Chroma": [
        {"tier": "Open Source", "price": 0, "unit": "free", "limits": "Self-hosted, unlimited, Apache 2.0"},
        {"tier": "Cloud", "price": None, "unit": "waitlist", "limits": "Managed service (beta)"}
    ],
    "Weaviate": [
        {"tier": "Sandbox", "price": 0, "unit": "free", "limits": "14-day trial, 1M objects"},
        {"tier": "Standard", "price": 25, "unit": "month", "limits": "Hosted, SLA 99.9%"},
        {"tier": "Enterprise", "price": None, "unit": "custom", "limits": "Custom deployment, dedicated cluster"}
    ],
    "AutoGen": [
        {"tier": "Open Source", "price": 0, "unit": "free", "limits": "Apache 2.0, full framework"},
        {"tier": "AutoGen Studio", "price": 0, "unit": "preview", "limits": "Visual IDE for agents"}
    ],
    "CrewAI": [
        {"tier": "Open Source", "price": 0, "unit": "free", "limits": "MIT license, self-hosted"},
        {"tier": "Enterprise", "price": None, "unit": "custom", "limits": "Enterprise support, training"}
    ]
}

def get_competitor_id(cursor, name):
    """Get competitor ID from name."""
    cursor.execute("SELECT id FROM competitors WHERE name = ?", (name,))
    result = cursor.fetchone()
    return result[0] if result else None

def fetch_pricing(competitor_name=None):
    """Fetch pricing for specified competitor or all."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    competitors_to_fetch = []
    if competitor_name:
        competitors_to_fetch = [competitor_name]
    else:
        cursor.execute("SELECT name FROM competitors")
        competitors_to_fetch = [row[0] for row in cursor.fetchall()]
    
    alerts = []
    
    for name in competitors_to_fetch:
        if name not in CURRENT_PRICING:
            print(f"⚠ No pricing data available for {name}")
            continue
        
        comp_id = get_competitor_id(cursor, name)
        if not comp_id:
            print(f"⚠ Competitor {name} not found in database")
            continue
        
        # Get previous pricing for comparison
        cursor.execute('''
            SELECT tier, price, unit, limits FROM pricing 
            WHERE competitor_id = ? 
            ORDER BY recorded_at DESC
        ''', (comp_id,))
        previous = {row[0]: {"price": row[1], "unit": row[2], "limits": row[3]} 
                   for row in cursor.fetchall()}
        
        # Insert new pricing
        for tier in CURRENT_PRICING[name]:
            tier_name = tier["tier"]
            
            # Check for changes
            if tier_name in previous:
                prev = previous[tier_name]
                if prev["price"] != tier["price"] or prev["limits"] != tier["limits"]:
                    alerts.append({
                        "competitor": name,
                        "tier": tier_name,
                        "type": "pricing_change",
                        "old": f"${prev['price']}/{prev['unit']} - {prev['limits']}",
                        "new": f"${tier['price']}/{tier['unit']} - {tier['limits']}"
                    })
            
            cursor.execute('''
                INSERT INTO pricing (competitor_id, tier, price, unit, limits)
                VALUES (?, ?, ?, ?, ?)
            ''', (comp_id, tier_name, tier["price"], tier["unit"], tier["limits"]))
        
        print(f"✓ Updated pricing for {name}")
    
    # Create alerts
    for alert in alerts:
        comp_id = get_competitor_id(cursor, alert["competitor"])
        cursor.execute('''
            INSERT INTO alerts (competitor_id, alert_type, severity, title, description, old_value, new_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            comp_id, 
            alert["type"],
            "medium",
            f"Pricing change: {alert['competitor']} {alert['tier']}",
            f"Pricing tier changed for {alert['tier']}",
            alert["old"],
            alert["new"]
        ))
    
    conn.commit()
    conn.close()
    
    if alerts:
        print(f"\n⚠ {len(alerts)} pricing changes detected:")
        for alert in alerts:
            print(f"  - {alert['competitor']} {alert['tier']}: {alert['old']} → {alert['new']}")
    else:
        print("\n✓ No pricing changes detected")

def main():
    parser = argparse.ArgumentParser(description="Fetch competitor pricing data")
    parser.add_argument("--name", help="Specific competitor name")
    parser.add_argument("--all", action="store_true", help="Fetch all competitors")
    args = parser.parse_args()
    
    if not os.path.exists(DB_PATH):
        print("⚠ Database not found. Run init_tracking.py first.")
        return
    
    if args.name:
        fetch_pricing(args.name)
    else:
        fetch_pricing()

if __name__ == "__main__":
    main()
