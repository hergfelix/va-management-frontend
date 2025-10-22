#!/bin/bash

# Read accounts and build profiles array
ACCOUNTS_FILE="/Users/felixhergenroeder/tiktok_accounts.txt"
PROFILES=""
while IFS= read -r account; do
  if [ ! -z "$account" ]; then
    PROFILES="${PROFILES}\"https://www.tiktok.com/@${account}\","
  fi
done < "$ACCOUNTS_FILE"
# Remove trailing comma
PROFILES=${PROFILES%,}

# Create Apify Actor input JSON
cat > /Users/felixhergenroeder/apify_input_oct.json << INNER_EOF
{
  "excludePinnedPosts": false,
  "profiles": [${PROFILES}],
  "resultsPerPage": 50,
  "shouldDownloadCovers": false,
  "shouldDownloadSlideshowImages": true,
  "shouldDownloadSubtitles": false,
  "shouldDownloadVideos": false,
  "postFromDate": "2025-10-12",
  "postToDate": "2025-10-13"
}
INNER_EOF

echo "✅ Created Apify input for Oct 12-13"
echo "Total accounts: $(wc -l < $ACCOUNTS_FILE)"
echo ""
echo "Starting Apify Actor run..."

# Start Apify Actor
curl -X POST https://api.apify.com/v2/acts/GdWCkxBtKWOsKjdch/runs \
  -H "Authorization: Bearer apify_api_B8Evmar820Ef8MpPrQH5daMqSgi0el2Ytjxf" \
  -H "Content-Type: application/json" \
  -d @/Users/felixhergenroeder/apify_input_oct.json \
  > /Users/felixhergenroeder/apify_run_oct.json

echo ""
echo "✅ Apify Actor started for Oct 12-13"
cat /Users/felixhergenroeder/apify_run_oct.json
