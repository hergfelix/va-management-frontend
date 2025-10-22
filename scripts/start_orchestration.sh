#!/bin/bash
# Start Agent Orchestration System with Live Monitoring

cd "$(dirname "$0")/.."

clear

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         🚀 STARTING AGENT ORCHESTRATION SYSTEM               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "This will start a live monitoring dashboard showing:"
echo "  • Active specialized agents (Scraper, Recovery, Enrichment)"
echo "  • Real-time task coordination by PM"
echo "  • System metrics and quality scores"
echo "  • Task complexity indicators"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""
sleep 2

# Make sure script is executable
chmod +x scripts/agent_orchestrator.sh

# Run orchestrator in loop
while true; do
    clear
    ./scripts/agent_orchestrator.sh
    sleep 3
done
