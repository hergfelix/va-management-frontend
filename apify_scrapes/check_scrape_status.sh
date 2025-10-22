#!/bin/bash

API_KEY="apify_api_B8Evmar820Ef8MpPrQH5daMqSgi0el2Ytjxf"

echo "🔍 Checking Apify Scrape Status..."
echo ""

# Check Sept run
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📅 SEPT 23-29 SCRAPE (Run ID: VblICUptmTJPJzd3b)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "https://api.apify.com/v2/acts/GdWCkxBtKWOsKjdch/runs/VblICUptmTJPJzd3b?token=$API_KEY" | \
  python3 -c "import sys, json; data=json.load(sys.stdin)['data']; print(f\"Status: {data['status']}\"); print(f\"Started: {data.get('startedAt', 'N/A')}\"); print(f\"Finished: {data.get('finishedAt', 'Not yet')}\"); print(f\"Results: {data['chargedEventCounts'].get('result', 0)} posts\"); print(f\"Cost: \${data.get('usageTotalUsd', 0):.2f}\")"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📅 OCT 12-13 SCRAPE (Run ID: 7u1XkXtr70mwA3Qc6)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "https://api.apify.com/v2/acts/GdWCkxBtKWOsKjdch/runs/7u1XkXtr70mwA3Qc6?token=$API_KEY" | \
  python3 -c "import sys, json; data=json.load(sys.stdin)['data']; print(f\"Status: {data['status']}\"); print(f\"Started: {data.get('startedAt', 'N/A')}\"); print(f\"Finished: {data.get('finishedAt', 'Not yet')}\"); print(f\"Results: {data['chargedEventCounts'].get('result', 0)} posts\"); print(f\"Cost: \${data.get('usageTotalUsd', 0):.2f}\")"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Run this script again in 5-10 minutes to check progress!"
echo "   When both show 'SUCCEEDED', I'll download the results."
