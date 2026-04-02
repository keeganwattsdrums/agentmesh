---
name: competitive-intelligence
description: Competitive intelligence and market monitoring system for tracking competitor pricing, features, launches, and positioning. Use when the user needs to monitor competitors, analyze market positioning, track pricing changes, compare features, or generate competitive intelligence reports. Covers competitor tracking setup, automated monitoring, feature comparison matrices, and weekly competitive reports.
---

# Competitive Intelligence System

A comprehensive system for monitoring competitors and market opportunities in the AI/ML infrastructure space.

## Quick Start

1. **Initialize tracking database**: Run `scripts/init_tracking.py`
2. **Add competitors**: Edit `references/competitors.yaml` with target companies
3. **Run analysis**: Use `scripts/analyze_competitor.py --name <competitor>`
4. **Generate report**: Use `scripts/generate_report.py --weekly`

## Core Workflows

### 1. Competitor Tracking Setup

Initialize the tracking system:

```bash
python3 ~/.openclaw/skills/competitive-intelligence/scripts/init_tracking.py
```

This creates:
- `competitive-intel.db` - SQLite database for tracking
- Default competitor profiles (Mem0, LangSmith, Pinecone, Chroma, Weaviate, AutoGen, CrewAI)
- Monitoring templates

### 2. Pricing Monitoring

Check competitor pricing:

```bash
# Fetch latest pricing for all tracked competitors
python3 ~/.openclaw/skills/competitive-intelligence/scripts/fetch_pricing.py --all

# Check specific competitor
python3 ~/.openclaw/skills/competitive-intelligence/scripts/fetch_pricing.py --name pinecone

# Compare pricing across vector DBs
python3 ~/.openclaw/skills/competitive-intelligence/scripts/compare_pricing.py --category vector-db
```

### 3. Feature Comparison

Generate feature comparison matrices:

```bash
# Full feature comparison
python3 ~/.openclaw/skills/competitive-intelligence/scripts/compare_features.py --output markdown

# Category-specific comparison
python3 ~/.openclaw/skills/competitive-intelligence/scripts/compare_features.py --category memory
```

### 4. Market Positioning Analysis

Analyze competitive positioning:

```bash
python3 ~/.openclaw/skills/competitive-intelligence/scripts/analyze_positioning.py
```

### 5. Alert System

Check for competitor changes:

```bash
# Check all competitors for updates
python3 ~/.openclaw/skills/competitive-intelligence/scripts/check_alerts.py

# Set up automated monitoring (cron)
python3 ~/.openclaw/skills/competitive-intelligence/scripts/setup_monitoring.py --frequency daily
```

### 6. Weekly Report Generation

Generate comprehensive weekly report:

```bash
python3 ~/.openclaw/skills/competitive-intelligence/scripts/generate_report.py --weekly --output pdf
```

## Manual Tracking Templates

Use these templates when automated tracking isn't possible:

- **Pricing Tracker**: `assets/templates/pricing_tracker.md`
- **Feature Matrix**: `assets/templates/feature_matrix.md`
- **Launch Tracker**: `assets/templates/launch_tracker.md`
- **Positioning Map**: `assets/templates/positioning_template.md`

## Reference Data

Pre-loaded competitor intelligence:

- **Competitor Profiles**: See `references/competitors.yaml` for baseline data on Mem0, LangSmith, Pinecone, Chroma, Weaviate, AutoGen, CrewAI
- **Pricing History**: Historical pricing data in database
- **Feature Database**: Structured feature comparisons

## Database Schema

The SQLite database (`competitive-intel.db`) contains:

| Table | Purpose |
|-------|---------|
| `competitors` | Basic company info, category, website |
| `pricing` | Historical pricing data |
| `features` | Feature comparisons |
| `launches` | Product launches and announcements |
| `positioning` | Market positioning data |
| `alerts` | Detected changes and alerts |

## Categories

Competitors are organized by category:

| Category | Competitors |
|----------|-------------|
| `memory` | Mem0 |
| `observability` | LangSmith |
| `vector-db` | Pinecone, Chroma, Weaviate |
| `agent-framework` | AutoGen, CrewAI |

## Alert Types

The system tracks these change types:

- `pricing_change` - Price increases/decreases, new tiers
- `feature_launch` - New features or capabilities
- `positioning_shift` - Messaging or positioning changes
- `integration_add` - New integrations announced
- `funding_news` - Funding rounds or financial news

## Output Formats

Scripts support multiple output formats:

- `markdown` - Human-readable reports
- `json` - Structured data for integrations
- `csv` - Spreadsheet-compatible
- `pdf` - Professional reports (requires md-to-pdf skill)

## Integration with Other Skills

- Use `md-to-pdf` skill to convert markdown reports to PDF
- Use `web_search`/`web_fetch` for real-time competitor research
- Use `daily-report` skill for broader market intelligence

## Advanced Usage

### Custom Competitor Addition

Add a new competitor to tracking:

```bash
python3 ~/.openclaw/skills/competitive-intelligence/scripts/add_competitor.py \
  --name "NewCo" \
  --category "vector-db" \
  --website "https://newco.ai" \
  --pricing-url "https://newco.ai/pricing"
```

### Historical Analysis

Analyze trends over time:

```bash
python3 ~/.openclaw/skills/competitive-intelligence/scripts/analyze_trends.py \
  --metric pricing \
  --competitor pinecone \
  --days 90
```

### Custom Report Templates

Modify `assets/templates/weekly_report_template.md` for custom report formatting.

## Maintenance

- Review and update `references/competitors.yaml` monthly
- Verify pricing URLs are still valid
- Update feature matrices when new capabilities launch
- Archive old alerts to keep database performant