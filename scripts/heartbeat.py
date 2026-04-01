#!/usr/bin/env python3
"""
AgentMesh Autonomous Heartbeat
Runs every 30 minutes to check Moltbook and engage
"""

import requests
import json
from datetime import datetime

MOLTBOOK_KEY = "moltbook_sk_5xw8GdT-a89_UbjeLmU1D7HAJ-gACaOD"
API_URL = "https://cuddly-bears-punch.loca.lt"

def log(message):
    timestamp = datetime.now().isoformat()
    log_line = f"{timestamp} | {message}"
    print(log_line)
    with open("logs/heartbeat.log", "a") as f:
        f.write(log_line + "\n")

def check_moltbook():
    """Check Moltbook for notifications and activity"""
    headers = {"Authorization": f"Bearer {MOLTBOOK_KEY}"}
    try:
        r = requests.get("https://www.moltbook.com/api/v1/home", headers=headers, timeout=10)
        data = r.json()
        
        account = data.get("your_account", {})
        notifs = account.get("unread_notification_count", 0)
        karma = account.get("karma", 0)
        
        log(f"Moltbook: {notifs} notifications, karma: {karma}")
        
        # Check post activity
        post_activity = data.get("activity_on_your_posts", [])
        for activity in post_activity:
            post_id = activity.get("post_id", "")
            new_count = activity.get("new_notification_count", 0)
            if new_count > 0:
                log(f"Post {post_id[-8:]}: {new_count} new interactions")
        
        return notifs
        
    except Exception as e:
        log(f"Moltbook error: {e}")
        return 0

def check_api_health():
    """Check if API is responding"""
    try:
        r = requests.get(f"{API_URL}/health", timeout=10)
        if r.status_code == 200:
            data = r.json()
            agents = data.get("agents", 0)
            log(f"API: healthy, {agents} agents registered")
            return True
        else:
            log(f"API: unhealthy (status {r.status_code})")
            return False
    except Exception as e:
        log(f"API error: {e}")
        return False

if __name__ == "__main__":
    log("=== Heartbeat Start ===")
    
    # Check services
    notifs = check_moltbook()
    api_ok = check_api_health()
    
    # Summary
    if notifs > 0:
        log(f"ACTION NEEDED: {notifs} unread notifications")
    
    log("=== Heartbeat Complete ===\n")
