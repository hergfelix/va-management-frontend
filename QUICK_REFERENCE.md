# 🚀 Quick Reference Card

## Start Monitoring (Choose One)

### Simple Monitor
```bash
./scripts/monitor_agents.sh
```
Shows: Process status, latest results, system metrics

### Agent Orchestration (Like the video)
```bash
./scripts/start_orchestration.sh
```
Shows: 4 specialized agents, PM coordination, task complexity

---

## The 4 Agents

| Agent | Script | What It Does |
|-------|--------|--------------|
| 🔵 **SCRAPER** | `production_scraper_237_urls.py` | Extract TikTok data (43 columns) |
| 🟡 **RECOVERY** | `retry_failed_with_account_scraping.py` | Retry failures with fallback |
| 🟢 **ENRICHMENT** | `enrich_account_data.py` | Fill missing account data |
| 🔍 **VALIDATOR** | (automatic) | Monitor data quality |

---

## Activate an Agent

```bash
# Left pane - activate agents here
source venv/bin/activate
python 02_Scraping_Systems/01_TikTok_Scrapers/[agent_script].py
```

---

## Understanding Tokens

- **Tokens** = Units of text (4 chars ≈ 1 token)
- **Task Complexity** = How many agents active (0-100)
- **1 agent** = 25/100 complexity
- **All agents** = 100/100 complexity

---

## PM Workflow

1. **You**: Tell PM what you need
2. **PM (Me)**: Decide which agents to activate
3. **Agents**: Execute specialized tasks
4. **Monitor**: Watch right pane for progress
5. **PM**: Coordinate next action

---

## Current Session Status

**Completed**: ✅ SCRAPER (223/235) → ✅ RECOVERY (232/235)
**Active**: 🔄 ENRICHMENT (14/158 accounts)
**Next**: Database import preparation

---

## Terminal Setup

```
┌─────────────────┬──────────────┐
│  LEFT PANE      │  RIGHT PANE  │
│  (PM / Work)    │  (Agents)    │
│                 │              │
│  • Chat with PM │  • Agent     │
│  • Run commands │    monitor   │
│  • Activate     │  • Real-time │
│    agents       │    status    │
│                 │              │
│  60-70% width   │  30-40% width│
└─────────────────┴──────────────┘
```

Split: `Cmd+\` or click split icon in terminal

---

## Stop Monitoring

Press `Ctrl+C` in right pane

---

## Files Created

- `scripts/monitor_agents.sh` - Simple monitoring
- `scripts/agent_orchestrator.sh` - Advanced orchestration
- `scripts/start_orchestration.sh` - Orchestration launcher
- `AGENT_ORCHESTRATION_GUIDE.md` - Full guide
- `SPLIT_TERMINAL_SETUP.md` - Setup instructions

---

## Need Help?

Read the full guides:
- `AGENT_ORCHESTRATION_GUIDE.md` - Complete system explanation
- `SPLIT_TERMINAL_SETUP.md` - Terminal setup steps
