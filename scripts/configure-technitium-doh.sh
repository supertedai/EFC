#!/bin/bash
# Configure Technitium DNS Server for secure DNS protocols
# - Rekursiv: Ren rekursjon (root → TLD → autoritativ), ingen forwarders
# - Sikre protokoller: DoH, DoT, DoQ, DoH/3 aktivert
# - DNSSEC: Aktivert for validering
# - Port 53: Deaktiveres (alt over sikre kanaler)
#
# Usage: ./configure-technitium-doh.sh [token]
#        TECHNITIUM_TOKEN=xxx ./configure-technitium-doh.sh

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
echo "   UDP (port 53):       $(echo "$CURRENT" | jq '.response.enableDnsOverUdp')"
echo "   TCP (port 53):       $(echo "$CURRENT" | jq '.response.enableDnsOverTcp')"
echo "   DoH:                 $(echo "$CURRENT" | jq '.response.enableDnsOverHttps')"
echo "   DoT:                 $(echo "$CURRENT" | jq '.response.enableDnsOverTls')"
echo "   DoQ:                 $(echo "$CURRENT" | jq '.response.enableDnsOverQuic')"
echo "   DoH/3:               $(echo "$CURRENT" | jq '.response.enableDnsOverHttp3')"

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

# --- 2. Aktiver alle sikre DNS-protokoller ---
echo ""
echo ">> Aktiverer sikre DNS-protokoller..."
echo "   DNS-over-HTTP     (port 80)  - for reverse proxy / ACME"
echo "   DNS-over-HTTPS    (port 443) - DoH"
echo "   DNS-over-TLS      (port 853) - DoT"
echo "   DNS-over-QUIC     (port 853) - DoQ"
echo "   DNS-over-HTTP/3   (port 443) - DoH/3"

PROTO_RESULT=$(curl -s "${DNS_SERVER}/api/settings/set?token=${TOKEN}" \
    --data-urlencode "enableDnsOverHttp=true" \
    --data-urlencode "enableDnsOverHttps=true" \
    --data-urlencode "enableDnsOverTls=true" \
    --data-urlencode "enableDnsOverQuic=true" \
    --data-urlencode "enableDnsOverHttp3=true" \
    --data-urlencode "dnsOverHttpPort=80" \
    --data-urlencode "dnsOverTlsPort=853" \
    --data-urlencode "dnsOverHttpsPort=443" \
    --data-urlencode "dnsOverQuicPort=853")

STATUS=$(echo "$PROTO_RESULT" | jq -r '.status')
if [ "$STATUS" = "ok" ]; then
    echo "   Alle sikre protokoller aktivert OK."
else
    echo "   FEIL ved aktivering av sikre protokoller:"
    echo "$PROTO_RESULT" | jq .
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

# --- 4. TLS-sertifikat ---
echo ""
read -p "Sti til TLS-sertifikat (.pfx/.p12), eller trykk Enter for å hoppe over: " TLS_PATH
if [ -n "$TLS_PATH" ]; then
    read -sp "Sertifikat-passord (Enter for ingen): " TLS_PASS
    echo

    TLS_RESULT=$(curl -s "${DNS_SERVER}/api/settings/set?token=${TOKEN}" \
        --data-urlencode "tlsCertificatePath=${TLS_PATH}" \
        --data-urlencode "tlsCertificatePassword=${TLS_PASS}")

    STATUS=$(echo "$TLS_RESULT" | jq -r '.status')
    if [ "$STATUS" = "ok" ]; then
        echo "   TLS-sertifikat konfigurert: ${TLS_PATH}"
    else
        echo "   FEIL ved TLS-konfigurasjon:"
        echo "$TLS_RESULT" | jq .
    fi
else
    echo "   Hopper over TLS-sertifikat."
    echo "   MERK: DoT, DoQ og DoH krever TLS-sertifikat for å fungere!"
fi

# --- 5. Verifiser konfigurasjon ---
echo ""
echo ">> Verifiserer endelig konfigurasjon..."
FINAL=$(curl -s "${DNS_SERVER}/api/settings/get?token=${TOKEN}")

echo ""
echo "   ╔══════════════════════════════════════╗"
echo "   ║      Endelig DNS-konfigurasjon       ║"
echo "   ╠══════════════════════════════════════╣"
echo "   ║ Rekursjon:       $(printf '%-18s' "$(echo "$FINAL" | jq -r '.response.enableRecursion')") ║"
echo "   ║ Forwarders:      $(printf '%-18s' "$(echo "$FINAL" | jq -r '.response.forwarders // "ingen"')") ║"
echo "   ║ DNSSEC:          $(printf '%-18s' "$(echo "$FINAL" | jq -r '.response.dnssecValidation')") ║"
echo "   ╠══════════════════════════════════════╣"
echo "   ║ UDP port 53:     $(printf '%-18s' "$(echo "$FINAL" | jq -r '.response.enableDnsOverUdp')") ║"
echo "   ║ TCP port 53:     $(printf '%-18s' "$(echo "$FINAL" | jq -r '.response.enableDnsOverTcp')") ║"
echo "   ╠══════════════════════════════════════╣"
echo "   ║ DoH (HTTPS/443): $(printf '%-18s' "$(echo "$FINAL" | jq -r '.response.enableDnsOverHttps')") ║"
echo "   ║ DoH (HTTP/80):   $(printf '%-18s' "$(echo "$FINAL" | jq -r '.response.enableDnsOverHttp')") ║"
echo "   ║ DoH/3:           $(printf '%-18s' "$(echo "$FINAL" | jq -r '.response.enableDnsOverHttp3')") ║"
echo "   ║ DoT (853):       $(printf '%-18s' "$(echo "$FINAL" | jq -r '.response.enableDnsOverTls')") ║"
echo "   ║ DoQ (853):       $(printf '%-18s' "$(echo "$FINAL" | jq -r '.response.enableDnsOverQuic')") ║"
echo "   ╚══════════════════════════════════════╝"

echo ""
echo "Ferdig! Technitium DNS kjører nå med:"
echo "  - Ren rekursiv oppløsning (ingen forwarders)"
echo "  - DNSSEC-validering"
echo "  - DoH, DoT, DoQ, DoH/3 aktivert"
echo ""
echo "Klient-endepunkter:"
echo "  DoH:  https://192.168.1.34/dns-query"
echo "  DoT:  tls://192.168.1.34:853"
echo "  DoQ:  quic://192.168.1.34:853"
