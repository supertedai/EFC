#!/bin/bash
# ------------------------------------------------------
# update-schema.sh  (failsafe-versjon)
# Henter sitemap fra energyflow-cosmology.com,
# konverterer alle <loc>-lenker til JSON-format,
# og avslutter alltid med exit 0.
# ------------------------------------------------------

set +e  # deaktiver "exit on error" fullstendig

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
SITEMAP_URL="https://energyflow-cosmology.com/sitemap.xml"
OUTPUT_JSON="$BASE_DIR/sitemap-links.json"

echo "🔄 Henter sitemap fra $SITEMAP_URL ..."

# Kontroller at jq finnes
if ! command -v jq >/dev/null 2>&1; then
  echo "⚠️  jq ikke installert – hopper over oppdatering."
  exit 0
fi

# Hent sitemap
curl -fsSL -L "$SITEMAP_URL" -o /tmp/sitemap.xml 2>/dev/null
if [ $? -ne 0 ]; then
  echo "⚠️  Kunne ikke hente sitemap fra $SITEMAP_URL"
  exit 0
fi

# Konverter til JSON
grep -oP '(?<=<loc>)[^<]+' /tmp/sitemap.xml > /tmp/locs.txt 2>/dev/null
if [ ! -s /tmp/locs.txt ]; then
  echo "⚠️  Ingen <loc>-lenker funnet i sitemap – hopper over oppdatering."
  exit 0
fi

jq -R . < /tmp/locs.txt | jq -s . > "$OUTPUT_JSON" 2>/dev/null
if [ $? -eq 0 ]; then
  COUNT=$(jq length "$OUTPUT_JSON" 2>/dev/null)
  echo "✅ Lagret sitemap-links.json med $COUNT lenker."
else
  echo "⚠️  Feil ved konvertering til JSON."
fi

exit 0
