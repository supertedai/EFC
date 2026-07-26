#!/usr/bin/env python3
import json
from pathlib import Path
import sys

def validate_paper(paper_dir):
    errors = []
    warnings = []

    # Required files
    required = [
        "citations.bib",
        paper_dir.name + ".jsonld",
        "index.json",
    ]

    for f in required:
        path = paper_dir / f
        if not path.exists():
            errors.append(f"Missing file: {path}")

    # PDF is optional (drafts), but warn
    pdf = paper_dir / (paper_dir.name + ".pdf")
    if not pdf.exists():
        warnings.append(f"PDF missing (OK for drafts)")

    # Markdown optional
    md = paper_dir / (paper_dir.name + ".md")
    if not md.exists():
        warnings.append("Markdown missing (OK for drafts)")

    # Validate JSON-LD
    jsonld_path = paper_dir / (paper_dir.name + ".jsonld")
    if jsonld_path.exists():
        try:
            json.loads(jsonld_path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"Invalid JSON-LD: {e}")

    # Validate index.json
    index_path = paper_dir / "index.json"
    if index_path.exists():
        try:
            index_data = json.loads(index_path.read_text(encoding="utf-8"))
            if "id" not in index_data:
                errors.append("index.json missing 'id'")
            if "title" not in index_data:
                errors.append("index.json missing 'title'")
        except Exception as e:
            errors.append(f"Invalid index.json: {e}")

    return errors, warnings


def main():
    base = Path("docs/papers/efc")
    if not base.exists():
        print("No papers found.")
        sys.exit(1)

    total_failures = 0
    total = 0

    print(f"[INFO] Validating papers in {base}\n")

    for paper_dir in sorted(base.iterdir()):
        if not paper_dir.is_dir():
            continue

        total += 1
        print(f"=== Validating {paper_dir.name} ===")

        errors, warnings = validate_paper(paper_dir)

        if errors:
            total_failures += 1
            print("✖ ERRORS:")
            for e in errors:
                print("  -", e)
            print("Result: FAIL\n")
        else:
            print("✔ No structural errors")
            if warnings:
                print("! WARNINGS:")
                for w in warnings:
                    print("  -", w)
            print("Result: PASS\n")

    print("----------------------------------")
    print(f"Validated: {total}")
    print(f"Failures:  {total_failures}")
    print(f"Passed:    {total - total_failures}")
    print("----------------------------------")

    # EXIT CODE IS NOW CORRECT:
    if total_failures > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
