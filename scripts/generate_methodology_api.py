#!/usr/bin/env python3
"""
Generate methodology API endpoint for EFC.

Creates:
    api/v1/methodology.json

Source:
    methodology/open-process.json
    methodology/ (markdown files defined in hasPart)

This allows:
    - LLMs to read methodology structure
    - Search engines to index the methodological layer
    - Downstream tools to consume the reflective process as API data
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METHOD_DIR = ROOT / "methodology"
OPEN_PROCESS = METHOD_DIR / "open-process.json"
OUTPUT = ROOT / "api" / "v1" / "methodology.json"

GITHUB_BASE = "https://github.com/supertedai/EFC/blob/main/methodology/"


def main():
    if not OPEN_PROCESS.exists():
        print("❌ open-process.json not found. Cannot generate methodology API.")
        return

    # Load methodology definition
    data = json.loads(OPEN_PROCESS.read_text(encoding="utf-8"))

    output = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "EFC Methodology Layer",
        "description": data.get("description", "Methodological structure for EFC."),
        "source": "https://github.com/supertedai/EFC",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "hasPart": []
    }

    has_part = data.get("hasPart", [])

    for part in has_part:
        name = part.get("name")
        if not name:
            continue

        md_file = METHOD_DIR / name
        exists = md_file.exists()

        output["hasPart"].append({
            "name": name,
            "url": GITHUB_BASE + name,
            "exists": exists
        })

        if exists:
            print(f"📄 Found methodology file: {name}")
        else:
            print(f"⚠️ Missing methodology file: {name}")

    # Ensure output directory exists
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # Write final JSON
    OUTPUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"✅ Generated methodology API: {OUTPUT}")


if __name__ == "__main__":
    main()
