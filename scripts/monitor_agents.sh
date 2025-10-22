#!/bin/bash
# Live Agent Monitoring Dashboard
# Shows real-time status of running scrapers and agents

clear

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           🤖 TIKTOK SCRAPER AGENT MONITOR                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

while true; do
    # Move cursor to top
    tput cup 4 0

    echo "📊 ACTIVE PROCESSES:"
    echo "═══════════════════════════════════════════════════════════════"

    # Check for running Python scrapers
    if pgrep -f "production_scraper_237_urls.py" > /dev/null; then
        echo "✅ Main Scraper (237 URLs)         : RUNNING"
    else
        echo "⭕ Main Scraper (237 URLs)         : IDLE"
    fi

    if pgrep -f "retry_failed_with_account_scraping.py" > /dev/null; then
        echo "✅ Retry Failed URLs              : RUNNING"
    else
        echo "⭕ Retry Failed URLs              : IDLE"
    fi

    if pgrep -f "enrich_account_data.py" > /dev/null; then
        echo "✅ Account Enrichment             : RUNNING"
    else
        echo "⭕ Account Enrichment             : IDLE"
    fi

    echo ""
    echo "📈 LATEST RESULTS:"
    echo "═══════════════════════════════════════════════════════════════"

    # Find latest CSV file
    LATEST_CSV=$(ls -t COMPLETE_*.csv 2>/dev/null | head -1)

    if [ -f "$LATEST_CSV" ]; then
        echo "📄 Latest File: $LATEST_CSV"

        # Count total rows (excluding header)
        TOTAL=$(tail -n +2 "$LATEST_CSV" 2>/dev/null | wc -l | xargs)
        echo "📊 Total Videos: $TOTAL"

        # Count successful (views > 0)
        SUCCESS=$(tail -n +2 "$LATEST_CSV" 2>/dev/null | awk -F',' '$6 > 0' | wc -l | xargs)
        echo "✅ Successful: $SUCCESS"

        if [ "$TOTAL" -gt 0 ]; then
            PERCENT=$((SUCCESS * 100 / TOTAL))
            echo "📈 Success Rate: ${PERCENT}%"
        fi
    else
        echo "⚠️  No CSV files found yet"
    fi

    echo ""
    echo "🔄 SYSTEM STATUS:"
    echo "═══════════════════════════════════════════════════════════════"
    echo "⏰ Time: $(date '+%H:%M:%S')"
    echo "💻 CPU: $(top -l 1 | grep "CPU usage" | awk '{print $3}' | cut -d'%' -f1)%"
    echo "🧠 Memory: $(top -l 1 | grep PhysMem | awk '{print $2}' | sed 's/M/MB/')"

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "Press Ctrl+C to stop monitoring"

    # Update every 2 seconds
    sleep 2
done
