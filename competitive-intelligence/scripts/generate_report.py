#!/usr/bin/env python3
"""
Generate weekly competitive intelligence reports.
Outputs comprehensive markdown reports with all tracked data.
"""

import sqlite3
import os
import argparse
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser("~/competitive-intel.db")

def get_competitor_summary():
    """Get summary of all competitors."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT name, category, description, funding, founded
        FROM competitors
        ORDER BY category, name
    ''')
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_pricing_summary():
    """Get latest pricing for each competitor."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.name, c.category, p.tier, p.price, p.unit, p.limits, p.recorded_at
        FROM competitors c
        JOIN pricing p ON c.id = p.competitor_id
        WHERE p.recorded_at = (
            SELECT MAX(recorded_at) 
            FROM pricing p2 
            WHERE p2.competitor_id = c.id AND p2.tier = p.tier
        )
        ORDER BY c.category, c.name, p.price ASC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_recent_launches(days=7):
    """Get recent product launches."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    since = datetime.now() - timedelta(days=days)
    
    cursor.execute('''
        SELECT c.name, l.launch_type, l.title, l.description, l.announced_at
        FROM launches l
        JOIN competitors c ON l.competitor_id = c.id
        WHERE l.announced_at > ? OR l.recorded_at > ?
        ORDER BY l.announced_at DESC
    ''', (since, since))
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_recent_alerts(days=7):
    """Get recent alerts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    since = datetime.now() - timedelta(days=days)
    
    cursor.execute('''
        SELECT c.name, a.alert_type, a.severity, a.title, a.description, a.detected_at
        FROM alerts a
        JOIN competitors c ON a.competitor_id = c.id
        WHERE a.detected_at > ?
        ORDER BY a.detected_at DESC
    ''', (since,))
    
    results = cursor.fetchall()
    conn.close()
    return results

def generate_weekly_report(output_format="markdown"):
    """Generate comprehensive weekly report."""
    
    competitors = get_competitor_summary()
    pricing = get_pricing_summary()
    launches = get_recent_launches(7)
    alerts = get_recent_alerts(7)
    
    report_date = datetime.now().strftime("%Y-%m-%d")
    
    if output_format == "markdown":
        report = f"""# Competitive Intelligence Report
**Week of:** {report_date}

---

## Executive Summary

This report covers {len(competitors)} tracked competitors across 4 categories:
- **Memory**: Mem0
- **Observability**: LangSmith  
- **Vector DBs**: Pinecone, Chroma, Weaviate
- **Agent Frameworks**: AutoGen, CrewAI

### This Week's Highlights
"""
        
        if alerts:
            report += f"\n- **{len(alerts)} competitor alerts** detected\n"
        else:
            report += "\n- No significant competitor alerts this week\n"
        
        if launches:
            report += f"- **{len(launches)} product launches/announcements**\n"
        else:
            report += "- No major product launches this week\n"
        
        # Competitor Overview
        report += "\n---\n\n## Competitor Overview\n\n"
        current_category = None
        for comp in competitors:
            name, category, desc, funding, founded = comp
            if category != current_category:
                current_category = category
                report += f"\n### {category.upper()}\n\n"
            report += f"**{name}** ({funding}, {founded})\n"
            report += f"- {desc}\n\n"
        
        # Pricing Overview
        report += "\n---\n\n## Pricing Overview\n\n"
        current_category = None
        for price in pricing:
            name, category, tier, price_val, unit, limits, recorded = price
            if category != current_category:
                current_category = category
                report += f"\n### {category.upper()}\n\n"
            price_str = f"${price_val}/{unit}" if price_val else f"Custom/{unit}"
            if price_val == 0:
                price_str = "Free"
            report += f"- **{name}** {tier}: {price_str} ({limits})\n"
        
        # Alerts Section
        report += "\n---\n\n## Recent Alerts\n\n"
        if alerts:
            for alert in alerts:
                comp, alert_type, severity, title, desc, detected = alert
                report += f"### {title}\n"
                report += f"- **Competitor:** {comp}\n"
                report += f"- **Type:** {alert_type}\n"
                report += f"- **Severity:** {severity}\n"
                report += f"- **Detected:** {detected}\n"
                report += f"- **Details:** {desc}\n\n"
        else:
            report += "No alerts detected in the past week.\n"
        
        # Launches Section
        report += "\n---\n\n## Product Launches\n\n"
        if launches:
            for launch in launches:
                comp, launch_type, title, desc, announced = launch
                report += f"### {title}\n"
                report += f"- **Competitor:** {comp}\n"
                report += f"- **Type:** {launch_type}\n"
                report += f"- **Announced:** {announced}\n"
                if desc:
                    report += f"- **Details:** {desc}\n"
                report += "\n"
        else:
            report += "No product launches recorded in the past week.\n"
        
        # Market Insights
        report += """\n---

## Market Insights

### Trends Observed
- Vector database market continues to consolidate
- Memory solutions gaining traction for agent applications
- Pricing pressure on observability tools

### Recommendations
1. Monitor pricing changes weekly
2. Track feature parity in memory layer
3. Watch for new integrations announced

---

*Report generated by Competitive Intelligence System*
"""
        
        print(report)
        
        # Save to file
        filename = f"competitive-report-{report_date}.md"
        with open(filename, "w") as f:
            f.write(report)
        print(f"\n✓ Report saved to {filename}")
        
    elif output_format == "json":
        import json
        data = {
            "date": report_date,
            "competitors": [{"name": c[0], "category": c[1], "description": c[2]} for c in competitors],
            "pricing_count": len(pricing),
            "alerts": [{"competitor": a[0], "type": a[1], "title": a[3]} for a in alerts],
            "launches": [{"competitor": l[0], "title": l[2]} for l in launches]
        }
        print(json.dumps(data, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Generate competitive intelligence reports")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly report")
    parser.add_argument("--output", choices=["markdown", "json", "pdf"], 
                       default="markdown", help="Output format")
    args = parser.parse_args()
    
    if not os.path.exists(DB_PATH):
        print("⚠ Database not found. Run init_tracking.py first.")
        return
    
    if args.weekly or True:  # Default to weekly
        generate_weekly_report(args.output)

if __name__ == "__main__":
    main()
