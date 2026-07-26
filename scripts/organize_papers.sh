#!/usr/bin/env bash

set -e

ROOT="docs/papers/efc"
SOURCE_DIR="docs"
ARTICLES_DIR="$ROOT"

echo "=== EFC Full-Automatic Paper Organizer ==="

mkdir -p "$ARTICLES_DIR"

# Finn alle PDF-filer i docs/
PDFS=$(find "$SOURCE_DIR" -maxdepth 3 -type f -name "*.pdf")

for pdf in $PDFS; do
    filename=$(basename "$pdf")
    base="${filename%.pdf}"

    # Lag mappe
    target_dir="$ARTICLES_DIR/$base"
    mkdir -p "$target_dir/assets"

    echo "→ Organiserer: $base"

    # Flytt PDF
    mv "$pdf" "$target_dir/" 2>/dev/null || true

    # Finn matchende JSON-LD
    json=$(find "$SOURCE_DIR" -maxdepth 3 -type f -name "$base.jsonld" | head -n 1)
    if [[ -n "$json" ]]; then
        mv "$json" "$target_dir/" 2>/dev/null || true
    fi

    # Finn matchende `.md` eller `.html`
    md=$(find "$SOURCE_DIR" -maxdepth 3 -type f -name "$base.md" | head -n 1)
    html=$(find "$SOURCE_DIR" -maxdepth 3 -type f -name "$base.html" | head -n 1)

    if [[ -n "$md" ]]; then mv "$md" "$target_dir/" 2>/dev/null || true; fi
    if [[ -n "$html" ]]; then mv "$html" "$target_dir/" 2>/dev/null || true; fi

done

echo "=== Flytter gjenværende JSON-LD som ikke er matchet ==="
UNASSIGNED=$(find "$SOURCE_DIR" -maxdepth 3 -type f -name "*.jsonld")

for json in $UNASSIGNED; do
    filename=$(basename "$json")
    base="${filename%.jsonld}"

    target_dir="$ARTICLES_DIR/$base"
    mkdir -p "$target_dir/assets"

    mv "$json" "$target_dir/" 2>/dev/null || true

done

echo "=== Fjerner gamle tomme mapper ==="
find "$SOURCE_DIR" -type d -empty -delete || true

echo "=== FULL ORGANISERING FULLFØRT ==="
