#!/usr/bin/env python3
"""
quick_status.py — One-line status check
Run this anytime to see current state
"""

import json
from datetime import datetime

def main():
    # Load status
    try:
        with open("logs/status.json") as f:
            status = json.load(f)
        
        m = status.get("moltbook", {})
        a = status.get("api", {})
        r = status.get("revenue", {})
        
        print(f"🕐 {status.get('timestamp', 'unknown')[:16]}")
        print(f"📊 Karma: {m.get('karma',0)} | 👥 Followers: {m.get('followers',0)} | 🔔 Notifs: {m.get('notifications',0)}")
        print(f"🤖 API: {a.get('status','unknown')} | Agents: {a.get('agents',0)}")
        print(f"💰 Revenue: ${r.get('revenue',0)} | Customers: {r.get('customers',0)}")
        
        if m.get('alerts'):
            print(f"🚨 ALERTS: {', '.join(m['alerts'])}")
        
        if status.get('needs_action'):
            print("⚡ ACTION NEEDED")
            
    except Exception as e:
        print(f"Status unavailable: {e}")
        print("Run: python3 scripts/heartbeat.py")

if __name__ == "__main__":
    main()
