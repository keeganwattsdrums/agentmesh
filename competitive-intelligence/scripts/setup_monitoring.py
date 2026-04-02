#!/usr/bin/env python3
"""
Setup automated monitoring for competitor tracking.
Creates cron jobs or scheduled tasks.
"""

import os
import argparse

CRON_DAILY = """# Competitive Intelligence Daily Check
0 9 * * * python3 ~/.openclaw/skills/competitive-intelligence/scripts/fetch_pricing.py --all >> ~/competitive-intel.log 2>&1
0 9 * * * python3 ~/.openclaw/skills/competitive-intelligence/scripts/check_alerts.py >> ~/competitive-intel.log 2>&1
"""

CRON_WEEKLY = """# Competitive Intelligence Weekly Report
0 9 * * 1 python3 ~/.openclaw/skills/competitive-intelligence/scripts/generate_report.py --weekly >> ~/competitive-intel.log 2>&1
"""

def setup_cron(frequency="daily"):
    """Setup cron jobs for monitoring."""
    import subprocess
    
    # Get existing crontab
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        current_crontab = result.stdout
    except:
        current_crontab = ""
    
    # Add new cron jobs
    if frequency == "daily":
        new_cron = CRON_DAILY
    elif frequency == "weekly":
        new_cron = CRON_WEEKLY
    else:  # both
        new_cron = CRON_DAILY + "\n" + CRON_WEEKLY
    
    # Check if already exists
    if "competitive-intelligence" in current_crontab:
        print("⚠ Competitive intelligence cron jobs already exist")
        print("  Run 'crontab -e' to edit manually")
        return
    
    # Add to crontab
    new_crontab = current_crontab + "\n" + new_cron + "\n"
    
    # Install new crontab
    process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
    process.communicate(input=new_crontab)
    
    print(f"✓ Setup {frequency} monitoring")
    print("  Jobs scheduled:")
    if frequency in ["daily", "both"]:
        print("    - Daily pricing check at 9:00 AM")
        print("    - Daily alert check at 9:00 AM")
    if frequency in ["weekly", "both"]:
        print("    - Weekly report generation Mondays at 9:00 AM")
    print(f"\n  Logs: ~/competitive-intel.log")

def print_manual_setup():
    """Print manual setup instructions."""
    print("""
# Manual Monitoring Setup

## Option 1: Cron (Linux/Mac)

Add to crontab with `crontab -e`:

# Daily competitor checks
0 9 * * * python3 ~/.openclaw/skills/competitive-intelligence/scripts/fetch_pricing.py --all
0 9 * * * python3 ~/.openclaw/skills/competitive-intelligence/scripts/check_alerts.py

# Weekly report (Mondays at 9 AM)
0 9 * * 1 python3 ~/.openclaw/skills/competitive-intelligence/scripts/generate_report.py --weekly

## Option 2: Systemd Timer (Linux)

Create ~/.config/systemd/user/competitive-intel.service:
```
[Unit]
Description=Competitive Intelligence Check

[Service]
Type=oneshot
ExecStart=python3 %h/.openclaw/skills/competitive-intelligence/scripts/fetch_pricing.py --all
```

Create ~/.config/systemd/user/competitive-intel.timer:
```
[Unit]
Description=Run Competitive Intelligence daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable: systemctl --user enable --now competitive-intel.timer

## Option 3: Windows Task Scheduler

Create a batch file competitive-intel.bat:
```batch
@echo off
python3 %USERPROFILE%\\.openclaw\\skills\\competitive-intelligence\\scripts\\fetch_pricing.py --all
```

Use Task Scheduler to run daily at 9:00 AM.
""")

def main():
    parser = argparse.ArgumentParser(description="Setup automated monitoring")
    parser.add_argument("--frequency", choices=["daily", "weekly", "both", "manual"],
                       default="daily", help="Monitoring frequency")
    args = parser.parse_args()
    
    if args.frequency == "manual":
        print_manual_setup()
    else:
        try:
            setup_cron(args.frequency)
        except Exception as e:
            print(f"⚠ Could not setup cron automatically: {e}")
            print("\nUse --frequency manual for manual setup instructions")

if __name__ == "__main__":
    main()
