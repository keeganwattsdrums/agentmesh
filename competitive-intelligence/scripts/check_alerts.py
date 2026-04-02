#!/usr/bin/env python3
"""
Check for competitor alerts and changes.
Outputs detected changes and creates alert entries.
"""

import sqlite3
import os
import argparse
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser("~/competitive-intel.db")

def get_recent_alerts(days=7, unacknowledged_only=False):
    """Get recent alerts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    since = datetime.now() - timedelta(days=days)
    
    if unacknowledged_only:
        cursor.execute('''
            SELECT c.name, a.alert_type, a.severity, a.title, a.description, 
                   a.old_value, a.new_value, a.detected_at
            FROM alerts a
            JOIN competitors c ON a.competitor_id = c.id
            WHERE a.detected_at > ? AND a.acknowledged = FALSE
            ORDER BY a.detected_at DESC
        ''', (since,))
    else:
        cursor.execute('''
            SELECT c.name, a.alert_type, a.severity, a.title, a.description, 
                   a.old_value, a.new_value, a.detected_at
            FROM alerts a
            JOIN competitors c ON a.competitor_id = c.id
            WHERE a.detected_at > ?
            ORDER BY a.detected_at DESC
        ''', (since,))
    
    results = cursor.fetchall()
    conn.close()
    return results

def check_alerts(output_format="table", days=7):
    """Check and display alerts."""
    alerts = get_recent_alerts(days, unacknowledged_only=False)
    
    if not alerts:
        print("✓ No alerts in the last {} days".format(days))
        return
    
    if output_format == "markdown":
        print("## Recent Alerts\n")
        for alert in alerts:
            comp, alert_type, severity, title, desc, old, new, detected = alert
            print(f"**{title}** ({severity.upper()})")
            print(f"- Competitor: {comp}")
            print(f"- Type: {alert_type}")
            print(f"- Detected: {detected}")
            if old and new:
                print(f"- Change: {old} → {new}")
            print()
    
    elif output_format == "json":
        import json
        alert_list = []
        for alert in alerts:
            alert_list.append({
                "competitor": alert[0],
                "type": alert[1],
                "severity": alert[2],
                "title": alert[3],
                "description": alert[4],
                "old_value": alert[5],
                "new_value": alert[6],
                "detected_at": alert[7]
            })
        print(json.dumps(alert_list, indent=2))
    
    else:  # table
        print(f"Recent Alerts (last {days} days):\n")
        for alert in alerts:
            comp, alert_type, severity, title, desc, old, new, detected = alert
            print(f"[{severity.upper()}] {title}")
            print(f"  Competitor: {comp} | Type: {alert_type} | Date: {detected}")
            if old and new:
                print(f"  Change: {old} → {new}")
            print()

def acknowledge_alert(alert_id):
    """Mark an alert as acknowledged."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE alerts SET acknowledged = TRUE WHERE id = ?
    ''', (alert_id,))
    
    conn.commit()
    conn.close()
    print(f"✓ Acknowledged alert {alert_id}")

def main():
    parser = argparse.ArgumentParser(description="Check competitor alerts")
    parser.add_argument("--days", type=int, default=7, help="Days to look back")
    parser.add_argument("--output", choices=["table", "markdown", "json"], 
                       default="table", help="Output format")
    parser.add_argument("--unacknowledged", action="store_true", 
                       help="Show only unacknowledged alerts")
    parser.add_argument("--acknowledge", type=int, help="Acknowledge alert by ID")
    args = parser.parse_args()
    
    if not os.path.exists(DB_PATH):
        print("⚠ Database not found. Run init_tracking.py first.")
        return
    
    if args.acknowledge:
        acknowledge_alert(args.acknowledge)
    else:
        check_alerts(args.output, args.days)

if __name__ == "__main__":
    main()
