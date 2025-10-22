# Split Terminal Setup Guide

**Create a monitoring setup with dual-pane terminals like in professional development videos**

## Quick Setup (3 Steps)

### 1. Split Your Terminal in Cursor

**Option A: Using Cursor's Built-in Terminal Split**
1. Open terminal in Cursor (`` Ctrl+` `` or View → Terminal)
2. Click the **split terminal** icon (two vertical panes) in the terminal toolbar
3. You now have two side-by-side terminals

**Option B: Using Keyboard Shortcut**
- Mac: `Cmd+\` while terminal is focused
- Windows/Linux: `Ctrl+Shift+5`

### 2. Run Monitoring Dashboard (Right Pane)

In the **right terminal pane**, run:
```bash
./scripts/monitor_agents.sh
```

You'll see:
```
╔═══════════════════════════════════════════════════════════════╗
║           🤖 TIKTOK SCRAPER AGENT MONITOR                    ║
╚═══════════════════════════════════════════════════════════════╝

📊 ACTIVE PROCESSES:
═══════════════════════════════════════════════════════════════
✅ Account Enrichment             : RUNNING
⭕ Main Scraper (237 URLs)         : IDLE
⭕ Retry Failed URLs              : IDLE

📈 LATEST RESULTS:
═══════════════════════════════════════════════════════════════
📄 Latest File: COMPLETE_SCRAPED_DATA_WITH_RETRIES_20251022_163305.csv
📊 Total Videos: 262
✅ Successful: 223
📈 Success Rate: 85%

🔄 SYSTEM STATUS:
═══════════════════════════════════════════════════════════════
⏰ Time: 16:35:42
💻 CPU: 12.4%
🧠 Memory: 35G
```

**Updates every 2 seconds automatically**

### 3. Use Left Pane for Chat/Commands

The **left terminal pane** is for:
- Claude Code chat interface
- Running one-off commands
- Checking results
- Interactive work

---

## What the Monitor Shows

### Active Processes Section
- **✅ RUNNING** = Process is actively scraping
- **⭕ IDLE** = Process not running

Monitors:
1. **Main Scraper (237 URLs)** - production_scraper_237_urls.py
2. **Retry Failed URLs** - retry_failed_with_account_scraping.py
3. **Account Enrichment** - enrich_account_data.py

### Latest Results Section
- Most recent CSV file output
- Total videos processed
- Successful extractions count
- Success rate percentage

### System Status Section
- Current time
- CPU usage
- Memory usage

---

## Advanced Usage

### Run Scraper and Monitor Simultaneously

**Right Pane (Monitoring):**
```bash
./scripts/monitor_agents.sh
```

**Left Pane (Execute Scraper):**
```bash
source venv/bin/activate
python 02_Scraping_Systems/01_TikTok_Scrapers/production_scraper_237_urls.py
```

Watch the right pane update in real-time showing:
- Process changing from ⭕ IDLE → ✅ RUNNING
- Success rate increasing
- System resources updating

### Stop Monitoring

Press `Ctrl+C` in the right pane to stop the monitor.

### Restart Monitoring

Simply run `./scripts/monitor_agents.sh` again - it picks up where it left off.

---

## Troubleshooting

### "Permission denied" error
```bash
chmod +x scripts/monitor_agents.sh
```

### Monitor shows "No CSV files found"
Wait for first scraper to complete and generate output file.

### Process shows IDLE but script is running
Monitor checks for specific script names. Make sure you're running:
- `production_scraper_237_urls.py`
- `retry_failed_with_account_scraping.py`
- `enrich_account_data.py`

---

## Professional Setup Tips

### Resize Panes
- Drag the divider between panes to adjust sizes
- Right pane should be ~30-40% width for monitoring
- Left pane should be ~60-70% width for work

### Color Customization
Edit `scripts/monitor_agents.sh` to customize:
- Symbols: ✅ ⭕ 📊 💻 🧠
- Colors: Add ANSI color codes
- Refresh rate: Change `sleep 2` at bottom

### Multiple Monitors
If you have multiple screens:
- Left pane: Main work terminal
- Right pane: Monitoring dashboard
- External monitor: Cursor chat interface

---

## Current Project Status

**Account Enrichment Running**: Currently enriching 158 unique accounts to fill missing follower/post data

**Latest Results**: COMPLETE_SCRAPED_DATA_WITH_RETRIES_20251022_163305.csv
- 262 total videos
- 223 with data (85% success)
- Account enrichment will increase this to ~95%+

**Next Steps**:
1. Let account enrichment complete (~2-3 hours)
2. Final enriched CSV will have complete data
3. Ready for database import
