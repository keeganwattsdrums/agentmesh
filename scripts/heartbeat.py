#!/usr/bin/env python3
"""
AgentMesh Aggressive Engagement Heartbeat
Runs every 5 minutes to check Moltbook and ENGAGE
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
                log(f"ALERT: Post {post_id[-8:]} has {new_count} new interactions - NEEDS RESPONSE")
        
        return notifs, karma, post_activity
        
    except Exception as e:
        log(f"Moltbook error: {e}")
        return 0, 0, []

def check_api_health():
    """Check if API is responding"""
    try:
        r = requests.get(f"{API_URL}/health", timeout=10)
        if r.status_code == 200:
            data = r.json()
            agents = data.get("agents", 0)
            log(f"API: healthy, {agents} agents registered")
            return True, agents
        else:
            log(f"API: unhealthy (status {r.status_code})")
            return False, 0
    except Exception as e:
        log(f"API error: {e}")
        return False, 0

def browse_and_engage():
    """Browse feed and find engagement opportunities"""
    headers = {"Authorization": f"Bearer {MOLTBOOK_KEY}"}
    try:
        # Get hot posts
        r = requests.get("https://www.moltbook.com/api/v1/feed?sort=hot&limit=5", 
                        headers=headers, timeout=10)
        data = r.json()
        posts = data.get('posts', [])
        
        # Find relevant posts
        relevant_keywords = ['memory', 'context', 'agent', 'infrastructure', 'karma', 'echo']
        opportunities = []
        
        for post in posts:
            title = post.get('title', '').lower()
            if any(kw in title for kw in relevant_keywords):
                opportunities.append({
                    'id': post['id'],
                    'title': post['title'],
                    'author': post['author']['name'],
                    'upvotes': post['upvotes']
                })
        
        if opportunities:
            log(f"Found {len(opportunities)} engagement opportunities")
            for opp in opportunities[:2]:  # Top 2
                log(f"  → {opp['upvotes']}↑ | {opp['title'][:50]}...")
        
        return opportunities
        
    except Exception as e:
        log(f"Browse error: {e}")
        return []

if __name__ == "__main__":
    log("=== AGGRESSIVE HEARTBEAT ===")
    
    # Check services
    notifs, karma, activity = check_moltbook()
    api_ok, agents = check_api_health()
    
    # Browse for opportunities
    opportunities = browse_and_engage()
    
    # Summary
    if notifs > 0:
        log(f"ACTION NEEDED: {notifs} unread notifications - RESPOND NOW")
    
    if opportunities:
        log(f"ENGAGE: {len(opportunities)} relevant posts found")
    
    if agents > 0:
        log(f"METRIC: {agents} API users!")
    
    log("=== HEARTBEAT COMPLETE ===\n")
