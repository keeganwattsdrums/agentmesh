#!/usr/bin/env python3
"""
revenue_tracker.py — Track all revenue metrics
"""

import json
import os
from datetime import datetime

DATA_FILE = "/root/.openclaw/workspace/agentmesh/data/revenue.json"

def load_data():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "payments": [],
            "leads": [],
            "metrics": {
                "total_revenue": 0,
                "mrr": 0,
                "customers": 0
            }
        }

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def record_payment(amount, customer, source):
    """Record new payment"""
    data = load_data()
    payment = {
        "amount": amount,
        "customer": customer,
        "source": source,
        "timestamp": datetime.now().isoformat()
    }
    data["payments"].append(payment)
    data["metrics"]["total_revenue"] += amount
    data["metrics"]["mrr"] += amount
    data["metrics"]["customers"] += 1
    save_data(data)
    print(f"🎉 PAYMENT RECORDED: ${amount} from {customer}")
    return payment

def get_metrics():
    data = load_data()
    return data["metrics"]

if __name__ == "__main__":
    metrics = get_metrics()
    print(f"💰 Total Revenue: ${metrics['total_revenue']}")
    print(f"📈 MRR: ${metrics['mrr']}")
    print(f"👥 Customers: {metrics['customers']}")
    
    # Check for first payment milestone
    if metrics['customers'] == 0:
        print("⏳ Waiting for first payment...")
    else:
        print("🚀 Revenue flowing!")
