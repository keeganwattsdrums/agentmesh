#!/usr/bin/env python3
"""
AgentMesh Autonomous Heartbeat
Runs every 5 minutes via cron
Logs status and creates summary for easy reporting
"""

import requests
import json
import os
from datetime import datetime

MOLTBOOK_KEY = "moltbook_sk_5xw8GdT-a89_UbjeLmU1D7HAJ-gACaOD"
API_URL = "https://cuddly-bears-punch.loca.lt"

def log(message):
    timestamp = datetime.now().isoformat()
    log_line = f"{timestamp} | {message}"
    print(log_line)
    with open("logs/heartbeat.log", "a") as f:
        f.write(log_line + "\n")

def save_status(status_data):
    """Save current status to JSON for easy reading"""
    with open("logs/status.json", "w") as f:
        json.dump(status_data, f, indent=2)

def check_moltbook():
    headers = {"Authorization": f"Bearer {MOLTBOOK_KEY}"}
    try:
        r = requests.get("https://www.moltbook.com/api/v1/home", headers=headers, timeout=10)
        data = r.json()
        
        account = data.get("your_account", {})
        notifs = account.get("unread_notification_count", 0)
        karma = account.get("karma", 0)
        followers = account.get("followerCount", 0)
        
        log(f"Moltbook: {notifs} notifications, karma: {karma}, followers: {followers}")
        
        # Check for actionable items
        alerts = []
        post_activity = data.get("activity_on_your_posts", [])
        for activity in post_activity:
            new_count = activity.get("new_notification_count", 0)
            if new_count > 0:
                alerts.append(f"{new_count} new on post")
                log(f"ALERT: {new_count} new interactions")
        
        # Check DMs
        dms = data.get("your_direct_messages", {})
        unread_dms = dms.get("unread_message_count", 0) if isinstance(dms.get("unread_message_count"), int) else 0
        if unread_dms > 0:
            alerts.append(f"{unread_dms} unread DMs")
        
        return {
            "notifications": notifs,
            "karma": karma,
            "followers": followers,
            "unread_dms": unread_dms,
            "alerts": alerts
        }
        
    except Exception as e:
        log(f"Moltbook error: {e}")
        return {"notifications": 0, "karma": 0, "followers": 0, "unread_dms": 0, "alerts": [], "error": str(e)}

def check_api_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=10)
        if r.status_code == 200:
            data = r.json()
            agents = data.get("agents", 0)
            log(f"API: healthy, {agents} agents")
            return {"status": "healthy", "agents": agents}
        else:
            log(f"API: unhealthy ({r.status_code})")
            return {"status": f"error_{r.status_code}", "agents": 0}
    except Exception as e:
        log(f"API error: {e}")
        return {"status": "down", "agents": 0, "error": str(e)}

def browse_opportunities():
    headers = {"Authorization": f"Bearer {MOLTBOOK_KEY}"}
    try:
        r = requests.get("https://www.moltbook.com/api/v1/feed?sort=hot&limit=5", 
                        headers=headers, timeout=10)
        data = r.json()
        posts = data.get('posts', [])
        
        keywords = ['memory', 'context', 'agent', 'infrastructure', 'ai', 'build']
        opportunities = []
        
        for post in posts:
            title = post.get('title', '').lower()
            if any(kw in title for kw in keywords):
                opportunities.append({
                    'id': post['id'],
                    'title': post['title'][:50],
                    'upvotes': post['upvotes'],
                    'author': post['author']['name']
                })
        
        if opportunities:
            log(f"Found {len(opportunities)} opportunities")
            for opp in opportunities[:2]:
                log(f"  → {opp['upvotes']}↑ | {opp['title']}")
        
        return opportunities
        
    except Exception as e:
        log(f"Browse error: {e}")
        return []

if __name__ == "__main__":
    log("=== CRON HEARTBEAT ===")
    
    # Gather all data
    moltbook = check_moltbook()
    api = check_api_health()
    opportunities = browse_opportunities()
    
    # Create status summary
    status = {
        "timestamp": datetime.now().isoformat(),
        "moltbook": moltbook,
        "api": api,
        "opportunities_count": len(opportunities),
        "needs_action": len(moltbook.get("alerts", [])) > 0 or moltbook.get("notifications", 0) > 0
    }
    
    save_status(status)
    
    # Log summary
    if status["needs_action"]:
        log("ACTION NEEDED: Check notifications/alerts")
    
    if api["agents"] > 0:
        log(f"🎉 NEW API USER! Total: {api['agents']}")
    
    log("=== HEARTBEAT COMPLETE ===\n")
