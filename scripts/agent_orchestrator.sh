#!/bin/bash
# Agent Orchestration Dashboard
# Coordinates multiple specialized agents for complex tasks

clear

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           🎯 AGENT ORCHESTRATION SYSTEM                      ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Task Queue
echo "📋 TASK QUEUE:"
echo "═══════════════════════════════════════════════════════════════"

if [ -f ".agent_tasks" ]; then
    cat .agent_tasks
else
    echo "⚪ No active tasks"
fi

echo ""
echo "🤖 SPECIALIZED AGENTS:"
echo "═══════════════════════════════════════════════════════════════"

# Agent 1: Data Scraping Agent
if pgrep -f "production_scraper" > /dev/null; then
    echo -e "${GREEN}✅ SCRAPER AGENT${NC}        : ACTIVE"
    echo "   Task: Extracting TikTok video metrics"
    echo "   Status: Processing URL batch"
else
    echo -e "${YELLOW}⭕ SCRAPER AGENT${NC}        : STANDBY"
fi

# Agent 2: Retry & Recovery Agent
if pgrep -f "retry_failed" > /dev/null; then
    echo -e "${GREEN}✅ RECOVERY AGENT${NC}      : ACTIVE"
    echo "   Task: Retrying failed URLs with fallback strategies"
    echo "   Status: Account-level scraping in progress"
else
    echo -e "${YELLOW}⭕ RECOVERY AGENT${NC}      : STANDBY"
fi

# Agent 3: Data Enrichment Agent
if pgrep -f "enrich_account" > /dev/null; then
    echo -e "${GREEN}✅ ENRICHMENT AGENT${NC}    : ACTIVE"
    echo "   Task: Filling missing account follower data"

    # Get latest log to show progress
    LATEST_CSV=$(ls -t COMPLETE_*.csv 2>/dev/null | head -1)
    if [ -f "$LATEST_CSV" ]; then
        ENRICHED=$(tail -n +2 "$LATEST_CSV" 2>/dev/null | awk -F',' '$14 > 0' | wc -l | xargs)
        echo "   Status: ${ENRICHED} accounts enriched"
    fi
else
    echo -e "${YELLOW}⭕ ENRICHMENT AGENT${NC}    : STANDBY"
fi

# Agent 4: Quality Validation Agent
echo -e "${BLUE}🔍 VALIDATOR AGENT${NC}     : MONITORING"
echo "   Task: Continuous data quality checks"

if [ -f "COMPLETE_SCRAPED_DATA_WITH_RETRIES"*.csv ]; then
    LATEST=$(ls -t COMPLETE_*.csv | head -1)
    TOTAL=$(tail -n +2 "$LATEST" 2>/dev/null | wc -l | xargs)
    WITH_DATA=$(tail -n +2 "$LATEST" 2>/dev/null | awk -F',' '$6 > 0' | wc -l | xargs)

    if [ "$TOTAL" -gt 0 ]; then
        QUALITY=$((WITH_DATA * 100 / TOTAL))

        if [ "$QUALITY" -ge 90 ]; then
            echo -e "   Status: ${GREEN}Quality Score: ${QUALITY}% (EXCELLENT)${NC}"
        elif [ "$QUALITY" -ge 70 ]; then
            echo -e "   Status: ${YELLOW}Quality Score: ${QUALITY}% (GOOD)${NC}"
        else
            echo -e "   Status: ${RED}Quality Score: ${QUALITY}% (NEEDS IMPROVEMENT)${NC}"
        fi
    fi
fi

echo ""
echo "📊 SYSTEM METRICS:"
echo "═══════════════════════════════════════════════════════════════"

# Token/Resource Usage (simulated)
ACTIVE_AGENTS=$(pgrep -f "scraper|retry|enrich" | wc -l | xargs)
echo "Active Agents: ${ACTIVE_AGENTS}/4"

# CPU and Memory
CPU=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | cut -d'%' -f1)
MEM=$(top -l 1 | grep PhysMem | awk '{print $2}' | sed 's/M/MB/')
echo "CPU Usage: ${CPU}%"
echo "Memory: ${MEM}"

# Task Complexity Score (based on active processes)
COMPLEXITY=$((ACTIVE_AGENTS * 25))
echo "Task Complexity: ${COMPLEXITY}/100"

echo ""
echo "🎯 PM COORDINATION:"
echo "═══════════════════════════════════════════════════════════════"

# Determine what PM should coordinate next
if [ "$ACTIVE_AGENTS" -eq 0 ]; then
    echo "⚪ All agents on standby - awaiting instructions"
elif pgrep -f "enrich_account" > /dev/null; then
    echo "🔄 Data enrichment in progress"
    echo "   Next: Database import preparation"
elif pgrep -f "retry_failed" > /dev/null; then
    echo "🔄 Recovering failed URLs"
    echo "   Next: Account data enrichment"
elif pgrep -f "production_scraper" > /dev/null; then
    echo "🔄 Initial scraping in progress"
    echo "   Next: Retry failed URLs with fallback"
else
    echo "✅ All scraping complete"
    echo "   Next: Prepare final database import"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "⏰ Last Update: $(date '+%H:%M:%S')"
echo "🔄 Auto-refresh: Every 3 seconds"
echo ""
