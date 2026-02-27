#!/bin/bash
# Configure Technitium DNS Server for DNS-over-HTTPS (DoH)
# - Recursive: Use DoH forwarders instead of plain DNS (port 53)
# - Authoritative: Enable DoH listener on the server
#
# Usage: ./configure-technitium-doh.sh

set -euo pipefail

DNS_SERVER="http://192.168.1.34:5380"

# --- Autentisering ---
read -p "Brukernavn: " DNS_USER
read -sp "Passord: " DNS_PASS
echo

echo ">> Logger inn på Technitium DNS..."
LOGIN_RESPONSE=$(curl -s "${DNS_SERVER}/api/user/login?user=${DNS_USER}&pass=${DNS_PASS}&includeInfo=true")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token // empty')
if [ -z "$TOKEN" ]; then
    echo "FEIL: Kunne ikke logge inn. Sjekk brukernavn/passord."
    echo "$LOGIN_RESPONSE" | jq .
    exit 1
fi
echo "   Innlogget OK."

# --- Hent nåværende innstillinger ---
echo ">> Henter nåværende innstillinger..."
CURRENT=$(curl -s "${DNS_SERVER}/api/settings/get?token=${TOKEN}")
echo "   Nåværende DNS-port: $(echo "$CURRENT" | jq '.response.dnsServerLocalEndPoints')"
echo "   Nåværende forwarders: $(echo "$CURRENT" | jq '.response.forwarders')"

# --- 1. Konfigurer rekursive DoH-forwarders ---
echo ""
echo ">> Konfigurerer rekursive DoH-forwarders..."
echo "   (Cloudflare, Google, Quad9 over HTTPS)"

# Sett forwarders til DoH
FORWARDER_RESULT=$(curl -s "${DNS_SERVER}/api/settings/set?token=${TOKEN}" \
    --data-urlencode "forwarders=https://cloudflare-dns.com/dns-query,https://dns.google/dns-query,https://dns.quad9.net/dns-query" \
    --data-urlencode "forwarderProtocol=HttpsJson")

STATUS=$(echo "$FORWARDER_RESULT" | jq -r '.status')
if [ "$STATUS" = "ok" ]; then
    echo "   Rekursive DoH-forwarders konfigurert OK."
else
    echo "   FEIL ved konfigurasjon av forwarders:"
    echo "$FORWARDER_RESULT" | jq .
fi

# --- 2. Aktiver DoH-listener på serveren (autoritativ) ---
echo ""
echo ">> Aktiverer DNS-over-HTTPS listener..."

# Aktiver DoH på port 443
DOH_RESULT=$(curl -s "${DNS_SERVER}/api/settings/set?token=${TOKEN}" \
    --data-urlencode "enableDnsOverHttp=true" \
    --data-urlencode "enableDnsOverHttps=true" \
    --data-urlencode "dnsOverHttpPort=80" \
    --data-urlencode "dnsOverHttpsPort=443")

STATUS=$(echo "$DOH_RESULT" | jq -r '.status')
if [ "$STATUS" = "ok" ]; then
    echo "   DoH-listener aktivert OK (HTTPS port 443, HTTP port 80)."
else
    echo "   FEIL ved aktivering av DoH:"
    echo "$DOH_RESULT" | jq .
fi

# --- 3. Deaktiver vanlig DNS på port 53 (valgfritt) ---
echo ""
read -p "Vil du deaktivere vanlig DNS på port 53? (j/n): " DISABLE_53
if [ "$DISABLE_53" = "j" ]; then
    echo ">> Deaktiverer vanlig DNS (port 53)..."
    DISABLE_RESULT=$(curl -s "${DNS_SERVER}/api/settings/set?token=${TOKEN}" \
        --data-urlencode "enableDnsOverUdp=false" \
        --data-urlencode "enableDnsOverTcp=false")

    STATUS=$(echo "$DISABLE_RESULT" | jq -r '.status')
    if [ "$STATUS" = "ok" ]; then
        echo "   Port 53 (UDP+TCP) deaktivert."
    else
        echo "   FEIL:"
        echo "$DISABLE_RESULT" | jq .
    fi
else
    echo "   Port 53 forblir aktiv."
fi

# --- 4. Verifiser konfigurasjon ---
echo ""
echo ">> Verifiserer endelig konfigurasjon..."
FINAL=$(curl -s "${DNS_SERVER}/api/settings/get?token=${TOKEN}")

echo "   DoH aktivert:     $(echo "$FINAL" | jq '.response.enableDnsOverHttps')"
echo "   DoH port:         $(echo "$FINAL" | jq '.response.dnsOverHttpsPort')"
echo "   Forwarders:       $(echo "$FINAL" | jq '.response.forwarders')"
echo "   Forwarder proto:  $(echo "$FINAL" | jq '.response.forwarderProtocol')"
echo "   UDP (port 53):    $(echo "$FINAL" | jq '.response.enableDnsOverUdp')"
echo "   TCP (port 53):    $(echo "$FINAL" | jq '.response.enableDnsOverTcp')"

echo ""
echo "Ferdig! Technitium DNS bruker nå DoH for sikre oppslag."
echo ""
echo "MERK: For at DoH-listeneren skal fungere med HTTPS trenger du et TLS-sertifikat."
echo "Du kan konfigurere dette i Technitium under Settings > Web Service > TLS Certificate."
echo "Alternativt kan du bruke Let's Encrypt via Technitium sitt innebygde ACME-støtte."
