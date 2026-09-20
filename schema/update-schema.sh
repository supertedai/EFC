#!/bin/bash
# ------------------------------------------------------
# update-schema.sh  (failsafe version)
# Fetches the sitemap from energyflow-cosmology.com,
# converts every <loc> link to JSON format,
# and always exits with exit 0.
# ------------------------------------------------------

set +e  # disable "exit on error" completely

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
SITEMAP_URL="https://energyflow-cosmology.com/sitemap.xml"
OUTPUT_JSON="$BASE_DIR/sitemap-links.json"

echo "🔄 Fetching the sitemap from $SITEMAP_URL ..."

# Check that jq is installed
if ! command -v jq >/dev/null 2>&1; then
  echo "⚠️  jq not installed – skipping the update."
  exit 0
fi

# Fetch the sitemap
curl -fsSL -L "$SITEMAP_URL" -o /tmp/sitemap.xml 2>/dev/null
if [ $? -ne 0 ]; then
  echo "⚠️  Could not fetch the sitemap from $SITEMAP_URL"
  exit 0
fi

# Convert to JSON
grep -oP '(?<=<loc>)[^<]+' /tmp/sitemap.xml > /tmp/locs.txt 2>/dev/null
if [ ! -s /tmp/locs.txt ]; then
  echo "⚠️  No <loc> links found in the sitemap – skipping the update."
  exit 0
fi

jq -R . < /tmp/locs.txt | jq -s . > "$OUTPUT_JSON" 2>/dev/null
if [ $? -eq 0 ]; then
  COUNT=$(jq length "$OUTPUT_JSON" 2>/dev/null)
  echo "✅ Saved sitemap-links.json with $COUNT links."
else
  echo "⚠️  Error converting to JSON."
fi

exit 0
