#!/usr/bin/env bash

set -e

ROOT="docs/papers/efc"
SOURCE_DIR="docs"
ARTICLES_DIR="$ROOT"

echo "=== EFC Full-Automatic Paper Organizer ==="

mkdir -p "$ARTICLES_DIR"

# Find all PDF files in docs/
PDFS=$(find "$SOURCE_DIR" -maxdepth 3 -type f -name "*.pdf")

for pdf in $PDFS; do
    filename=$(basename "$pdf")
    base="${filename%.pdf}"

    # Create the directory
    target_dir="$ARTICLES_DIR/$base"
    mkdir -p "$target_dir/assets"

    echo "→ Organizing: $base"

    # Move the PDF
    mv "$pdf" "$target_dir/" 2>/dev/null || true

    # Find the matching JSON-LD
    json=$(find "$SOURCE_DIR" -maxdepth 3 -type f -name "$base.jsonld" | head -n 1)
    if [[ -n "$json" ]]; then
        mv "$json" "$target_dir/" 2>/dev/null || true
    fi

    # Find the matching `.md` or `.html`
    md=$(find "$SOURCE_DIR" -maxdepth 3 -type f -name "$base.md" | head -n 1)
    html=$(find "$SOURCE_DIR" -maxdepth 3 -type f -name "$base.html" | head -n 1)

    if [[ -n "$md" ]]; then mv "$md" "$target_dir/" 2>/dev/null || true; fi
    if [[ -n "$html" ]]; then mv "$html" "$target_dir/" 2>/dev/null || true; fi

done

echo "=== Moving the remaining JSON-LD that was not matched ==="
UNASSIGNED=$(find "$SOURCE_DIR" -maxdepth 3 -type f -name "*.jsonld")

for json in $UNASSIGNED; do
    filename=$(basename "$json")
    base="${filename%.jsonld}"

    target_dir="$ARTICLES_DIR/$base"
    mkdir -p "$target_dir/assets"

    mv "$json" "$target_dir/" 2>/dev/null || true

done

echo "=== Removing old empty directories ==="
find "$SOURCE_DIR" -type d -empty -delete || true

echo "=== FULL ORGANIZATION COMPLETE ==="
