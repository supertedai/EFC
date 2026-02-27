#!/bin/bash
# Configure Technitium DNS Server for DNS-over-HTTPS (DoH)
# - Rekursiv: Ren rekursjon (root → TLD → autoritativ), ingen forwarders
# - Autoritativ: DoH-listener slik at klienter bruker sikker kanal
# - DNSSEC: Aktivert for validering
# - Port 53: Deaktiveres (alt over DoH)
#
# Usage: ./configure-technitium-doh.sh

set -euo pipefail

DNS_SERVER="http://192.168.1.34:5380"

# --- Autentisering ---
# Token kan settes via miljøvariabel TECHNITIUM_TOKEN eller som første argument
TOKEN="${1:-${TECHNITIUM_TOKEN:-}}"

if [ -z "$TOKEN" ]; then
    echo "Bruk: ./configure-technitium-doh.sh <token>"
    echo "  eller: TECHNITIUM_TOKEN=xxx ./configure-technitium-doh.sh"
    echo ""
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
else
    echo ">> Bruker oppgitt API-token."
fi

# --- Hent nåværende innstillinger ---
echo ">> Henter nåværende innstillinger..."
CURRENT=$(curl -s "${DNS_SERVER}/api/settings/get?token=${TOKEN}")
echo "   Nåværende forwarders: $(echo "$CURRENT" | jq '.response.forwarders')"
echo "   Rekursjon:           $(echo "$CURRENT" | jq '.response.enableRecursion')"
echo "   DNSSEC:              $(echo "$CURRENT" | jq '.response.dnssecValidation')"

# --- 1. Aktiver ren rekursjon, fjern alle forwarders ---
echo ""
echo ">> Aktiverer ren rekursiv oppløsning (ingen forwarders)..."
echo "   Serveren vil spørre root-servere → TLD → autoritative direkte."

RECURSION_RESULT=$(curl -s "${DNS_SERVER}/api/settings/set?token=${TOKEN}" \
    --data-urlencode "enableRecursion=true" \
    --data-urlencode "forwarders=" \
    --data-urlencode "dnssecValidation=true")

STATUS=$(echo "$RECURSION_RESULT" | jq -r '.status')
if [ "$STATUS" = "ok" ]; then
    echo "   Ren rekursjon aktivert, forwarders fjernet, DNSSEC aktivert."
else
    echo "   FEIL:"
    echo "$RECURSION_RESULT" | jq .
fi

# --- 2. Aktiver DoH-listener (sikker kanal for klienter) ---
echo ""
echo ">> Aktiverer DNS-over-HTTPS listener for klienter..."

DOH_RESULT=$(curl -s "${DNS_SERVER}/api/settings/set?token=${TOKEN}" \
    --data-urlencode "enableDnsOverHttp=true" \
    --data-urlencode "enableDnsOverHttps=true" \
    --data-urlencode "dnsOverHttpPort=80" \
    --data-urlencode "dnsOverHttpsPort=443")

STATUS=$(echo "$DOH_RESULT" | jq -r '.status')
if [ "$STATUS" = "ok" ]; then
    echo "   DoH-listener aktivert (HTTPS port 443, HTTP port 80)."
else
    echo "   FEIL ved aktivering av DoH:"
    echo "$DOH_RESULT" | jq .
fi

# --- 3. Deaktiver vanlig DNS på port 53 ---
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

echo ""
echo "   === Endelig konfigurasjon ==="
echo "   Rekursjon:         $(echo "$FINAL" | jq '.response.enableRecursion')"
echo "   Forwarders:        $(echo "$FINAL" | jq '.response.forwarders')"
echo "   DNSSEC:            $(echo "$FINAL" | jq '.response.dnssecValidation')"
echo "   DoH (HTTPS):       $(echo "$FINAL" | jq '.response.enableDnsOverHttps')"
echo "   DoH port:          $(echo "$FINAL" | jq '.response.dnsOverHttpsPort')"
echo "   UDP (port 53):     $(echo "$FINAL" | jq '.response.enableDnsOverUdp')"
echo "   TCP (port 53):     $(echo "$FINAL" | jq '.response.enableDnsOverTcp')"

echo ""
echo "Ferdig! Technitium DNS kjører nå med:"
echo "  - Ren rekursiv oppløsning (ingen forwarders)"
echo "  - DNSSEC-validering aktivert"
echo "  - Klienter kobler til via DoH (HTTPS)"
echo ""
echo "MERK: For HTTPS trenger du et TLS-sertifikat."
echo "Konfigurer dette i Technitium: Settings > Web Service > TLS Certificate"
echo "eller bruk innebygd Let's Encrypt (ACME)."
echo ""
echo "Test med: curl -s 'https://192.168.1.34/dns-query?name=example.com&type=A' -H 'accept: application/dns-json'"
