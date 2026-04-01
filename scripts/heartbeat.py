#!/usr/bin/env python3
"""
AgentMesh Autonomous Heartbeat with User Notifications
Runs every 5 minutes via cron - NOW SENDS UPDATES TO USER
"""

import requests
import json
import os
import subprocess
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
    with open("logs/status.json", "w") as f:
        json.dump(status_data, f, indent=2)

def notify_user(title, message):
    """Send notification to user via OpenClaw message system"""
    try:
        # Write to a notification file that can be picked up
        notification = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "urgent": "payment" in message.lower() or "agent" in message.lower()
        }
        with open("logs/notifications.jsonl", "a") as f:
            f.write(json.dumps(notification) + "\n")
        log(f"NOTIFICATION: {title}")
    except Exception as e:
        log(f"Notification error: {e}")

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
                title = activity.get('post_title', 'Unknown')[:30]
                alerts.append(f"{new_count} new on {title}")
                log(f"ALERT: {new_count} new interactions")
                notify_user("Moltbook Activity", f"{new_count} new interactions on: {title}")
        
        # Check DMs
        dms = data.get("your_direct_messages", {})
        unread_dms = dms.get("unread_message_count", 0) if isinstance(dms.get("unread_message_count"), int) else 0
        if unread_dms > 0:
            alerts.append(f"{unread_dms} unread DMs")
            notify_user("New DM", f"You have {unread_dms} unread direct message(s)")
        
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
            
            if agents > 0:
                notify_user("🎉 NEW API USER!", f"Agent count: {agents}. Check for payments!")
            
            return {"status": "healthy", "agents": agents}
        else:
            log(f"API: unhealthy ({r.status_code})")
            return {"status": f"error_{r.status_code}", "agents": 0}
    except Exception as e:
        log(f"API error: {e}")
        return {"status": "down", "agents": 0, "error": str(e)}

def check_revenue():
    """Check if we have any new payments"""
    try:
        with open("data/revenue.json") as f:
            rev = json.load(f)
            customers = rev.get("metrics", {}).get("customers", 0)
            revenue = rev.get("metrics", {}).get("total_revenue", 0)
            
            # Check if this is new (compare with last known)
            last_known_file = "logs/last_revenue.txt"
            last_known = 0
            try:
                with open(last_known_file) as f:
                    last_known = int(f.read().strip())
            except:
                pass
            
            if customers > last_known:
                notify_user("💰 REVENUE ALERT!", f"New customer! Total: {customers}, Revenue: ${revenue}")
                with open(last_known_file, "w") as f:
                    f.write(str(customers))
            
            return {"customers": customers, "revenue": revenue}
    except Exception as e:
        log(f"Revenue check error: {e}")
        return {"customers": 0, "revenue": 0}

if __name__ == "__main__":
    log("=== CRON HEARTBEAT ===")
    
    # Gather all data
    moltbook = check_moltbook()
    api = check_api_health()
    revenue = check_revenue()
    
    # Create status summary
    status = {
        "timestamp": datetime.now().isoformat(),
        "moltbook": moltbook,
        "api": api,
        "revenue": revenue,
        "needs_action": len(moltbook.get("alerts", [])) > 0 or moltbook.get("notifications", 0) > 0 or api["agents"] > 0
    }
    
    save_status(status)
    
    # Always log summary
    summary = f"Cron: Karma {moltbook['karma']}, Agents {api['agents']}, Revenue ${revenue['revenue']}"
    log(summary)
    
    # Send daily summary every 4th run (every 20 minutes)
    minute = datetime.now().minute
    if minute % 20 == 0:
        notify_user("📊 Status Update", f"Karma: {moltbook['karma']}, Agents: {api['agents']}, Revenue: ${revenue['revenue']}")
    
    if status["needs_action"]:
        log("ACTION NEEDED: Check notifications/alerts")
    
    log("=== HEARTBEAT COMPLETE ===\n")
