# Competitive Intelligence System

A comprehensive skill for OpenClaw that enables continuous monitoring of competitors and market opportunities in the AI/ML infrastructure space.

## What Was Delivered

### SKILL.md
Main skill file with:
- Quick start guide
- Core workflows (6 main features)
- Database schema documentation
- Integration guides
- Maintenance instructions

### Scripts (9 Python scripts)

| Script | Purpose |
|--------|---------|
| `init_tracking.py` | Initialize SQLite database with 7 default competitors |
| `fetch_pricing.py` | Update pricing data for competitors |
| `compare_pricing.py` | Generate pricing comparison tables |
| `compare_features.py` | Generate feature comparison matrices |
| `check_alerts.py` | Detect and display competitor changes |
| `generate_report.py` | Create weekly competitive intelligence reports |
| `analyze_positioning.py` | Analyze market positioning and differentiation |
| `add_competitor.py` | Add new competitors to tracking |
| `setup_monitoring.py` | Setup automated monitoring (cron/systemd) |

### Templates (5 Markdown templates)

| Template | Use Case |
|----------|----------|
| `pricing_tracker.md` | Manual pricing tracking |
| `feature_matrix.md` | Feature comparison matrices |
| `launch_tracker.md` | Product launch monitoring |
| `positioning_template.md` | Market positioning analysis |
| `weekly_report_template.md` | Weekly CI report structure |

### Reference Data

`competitors.yaml` - Baseline data on all 7 tracked competitors:
- Mem0 (memory)
- LangSmith (observability)
- Pinecone (vector DB)
- Chroma (vector DB)
- Weaviate (vector DB)
- AutoGen (agent framework)
- CrewAI (agent framework)

## Features Implemented

### 1. Competitor Tracking Template ✅
- SQLite database schema
- 7 pre-loaded competitors
- Easy competitor addition
- Category organization

### 2. Pricing Monitoring Framework ✅
- Automated pricing fetching
- Historical price tracking
- Change detection with alerts
- Category-wise comparison

### 3. Feature Comparison Matrix ✅
- Structured feature database
- Category-specific comparisons
- Multiple output formats (markdown, json, csv)

### 4. Market Positioning Analysis ✅
- Positioning map generation
- Differentiation analysis
- Market position tracking
- Strategic recommendations

### 5. Alert System ✅
- Automated change detection
- Alert logging and tracking
- Acknowledgment system
- Severity levels

### 6. Weekly Report Template ✅
- Automated report generation
- Executive summary
- Trends and insights
- Action items tracking

## Pricing Intelligence

Tracked pricing ranges:
- **Mem0**: $0-29/month (Developer to Pro)
- **LangSmith**: $0-39/user/month (Developer to Plus)
- **Pinecone**: $0-70/month (Starter to Standard)
- **Chroma**: Free (open source)
- **Weaviate**: $0-25/month (Sandbox to Standard)
- **AutoGen**: Free (open source)
- **CrewAI**: Free (open source + enterprise)

Target pricing for new product: **$29-199/month** fits within competitive range.

## Quick Start

```bash
# Initialize the database
python3 ~/.openclaw/skills/competitive-intelligence/scripts/init_tracking.py

# Compare pricing
python3 ~/.openclaw/skills/competitive-intelligence/scripts/compare_pricing.py

# Generate weekly report
python3 ~/.openclaw/skills/competitive-intelligence/scripts/generate_report.py --weekly

# Setup automated monitoring
python3 ~/.openclaw/skills/competitive-intelligence/scripts/setup_monitoring.py --frequency daily
```

## Installation Location

All files installed to:
```
~/.openclaw/skills/competitive-intelligence/
├── SKILL.md
├── scripts/
│   ├── init_tracking.py
│   ├── fetch_pricing.py
│   ├── compare_pricing.py
│   ├── compare_features.py
│   ├── check_alerts.py
│   ├── generate_report.py
│   ├── analyze_positioning.py
│   ├── add_competitor.py
│   └── setup_monitoring.py
├── assets/templates/
│   ├── pricing_tracker.md
│   ├── feature_matrix.md
│   ├── launch_tracker.md
│   ├── positioning_template.md
│   └── weekly_report_template.md
└── references/
    └── competitors.yaml
```

Database created at: `~/competitive-intel.db`

## Usage in OpenClaw

The skill triggers automatically when users ask about:
- "Track competitor pricing"
- "Generate competitive intelligence report"
- "Compare features with competitors"
- "Monitor competitor launches"
- "Analyze market positioning"
- Any competitive intelligence related tasks
