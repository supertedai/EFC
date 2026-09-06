#!/usr/bin/env python3
"""
EFC Auto-Metadata Generator

Scans docs/papers/efc/ for directories that contain a PDF but lack
an index.json (bare uploads). Generates a minimal metadata package:

  index.json, metadata.json, CITATION.cff, README.md, *.jsonld

Uses pdftotext (poppler-utils) to extract title, DOI, and date from
the PDF text. If pdftotext is unavailable, generates placeholder
metadata that can be filled in manually.

Run standalone:
    python3 scripts/maintenance/efc_auto_metadata.py

Or as part of the maintenance pipeline (called by efc_maintain.py).

Exit 0 = all packages complete, exit 1 = new packages generated.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
from datetime import date

# The efc: namespace is defined ONCE, in efc_ontology.py (C9). This generator
# used to carry its own copy of an older binding and would have re-created
# the drift C9 exists to stop, on the robot's own auto-commit (review finding
# 2026-09-06). Same directory, so the import works from efc_maintain.py, from
# `python3 scripts/maintenance/efc_auto_metadata.py` and from
# sync_engine/handlers.py alike.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from efc_ontology import NS as EFC_NS  # noqa: E402
from efc_identity import served_id, ROOT as _REPO_ROOT  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}

AUTHOR = "Morten Magnusson"
ORCID = "0009-0002-4860-5095"
AFFILIATION = "Symbiose Research, Sandnes, Norway"


def find_bare_pdfs():
    """Find paper dirs that have PDFs but no index.json."""
    bare = []
    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        d = os.path.join(PAPERS, name)
        if not os.path.isdir(d):
            continue
        has_index = os.path.exists(os.path.join(d, "index.json"))
        pdfs = [f for f in os.listdir(d) if f.lower().endswith(".pdf")]
        if pdfs and not has_index:
            bare.append((name, d, pdfs[0]))
    return bare


def extract_pdf_text(pdf_path, max_chars=5000):
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout[:max_chars] if result.returncode == 0 else ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def parse_title(text, dirname):
    """Extract title from PDF text or derive from dirname."""
    if text:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        # Title is usually the first non-empty line(s) before "Abstract" or author
        title_lines = []
        for line in lines[:10]:
            if re.match(r"(Abstract|Author|ORCID|Research Note|Morten)", line, re.I):
                break
            if len(line) > 10:
                title_lines.append(line)
        if title_lines:
            return " ".join(title_lines[:3])
    # Fallback: derive from directory name
    return dirname.replace("_", " ").replace("-", " ").title()


def parse_doi(text):
    """Extract DOI from PDF text."""
    if text:
        m = re.search(r"10\.6084/m9\.figshare\.(\d+)", text)
        if m:
            return f"10.6084/m9.figshare.{m.group(1)}"
    return None


def parse_date(text):
    """Extract date from PDF text."""
    if text:
        m = re.search(r"((?:January|February|March|April|May|June|July|August|"
                      r"September|October|November|December)\s+\d{1,2},?\s+\d{4})", text)
        if m:
            from datetime import datetime
            try:
                dt = datetime.strptime(m.group(1).replace(",", ""), "%B %d %Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
    return date.today().isoformat()


def generate_package(dirname, dirpath, pdf_name):
    """Generate full metadata package for a bare PDF directory."""
    pdf_path = os.path.join(dirpath, pdf_name)
    text = extract_pdf_text(pdf_path)

    title = parse_title(text, dirname)
    doi = parse_doi(text)
    pub_date = parse_date(text)
    short_id = dirname.lower().replace("_", "-")

    # Extract keywords from title
    keywords = [w for w in title.split() if len(w) > 3 and w[0].isupper()][:6]
    keywords = ["Energy-Flow Cosmology"] + keywords

    # index.json
    index = {
        "$schema": "./schema.json",
        "id": short_id,
        "title": title,
        "description": f"Auto-generated package for {title}.",
        "version": "1.0",
        "date": pub_date,
        "keywords": keywords,
        "author": {
            "name": AUTHOR,
            "orcid": ORCID,
            "affiliation": AFFILIATION,
        },
        "files": {
            "pdf": pdf_name,
            "readme": "README.md",
        },
    }
    if doi:
        index["doi"] = doi
        index["figshare_url"] = f"https://doi.org/{doi}"

    with open(os.path.join(dirpath, "index.json"), "w") as f:
        json.dump(index, f, indent=2)

    # metadata.json
    metadata = {
        "title": title,
        "short_id": short_id,
        "version": "1.0",
        "date": pub_date,
        "author": {
            "name": AUTHOR,
            "orcid": ORCID,
            "affiliation": AFFILIATION,
        },
        "license": "CC-BY-4.0",
        "keywords": keywords,
        "files": {"pdf": pdf_name, "readme": "README.md"},
    }
    if doi:
        metadata["doi"] = doi
        metadata["paper"] = {
            "doi": doi,
            "figshare_url": f"https://doi.org/{doi}",
        }

    with open(os.path.join(dirpath, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    # CITATION.cff
    cff = f"""cff-version: 1.2.0
title: "{title}"
message: "If you use this work, please cite it as below."
authors:
  - family-names: "Magnusson"
    given-names: "Morten"
    orcid: "https://orcid.org/{ORCID}"
    affiliation: "{AFFILIATION}"
date-released: "{pub_date}"
version: "1.0"
{f'doi: "{doi}"' if doi else '# doi: (pending)'}
license: "CC-BY-4.0"
repository-code: "https://github.com/supertedai/EFC"
"""
    with open(os.path.join(dirpath, "CITATION.cff"), "w") as f:
        f.write(cff)

    # jsonld
    jsonld = {
        "@context": {
            "@vocab": "https://schema.org/",
            "efc": EFC_NS,
        },
        "@type": "ScholarlyArticle",
        "name": title,
        "author": {
            "@type": "Person",
            "name": AUTHOR,
            "affiliation": {
                "@type": "Organization",
                "name": "Symbiose Research",
                "address": "Sandnes, Norway",
            },
            "identifier": f"https://orcid.org/{ORCID}",
        },
        "datePublished": pub_date,
        "license": "https://creativecommons.org/licenses/by/4.0/",
    }
    jsonld_name = f"{short_id}.jsonld"
    # @id on every document (C12): the DOI URL when the paper has one, else
    # the file's own identifier under the project authority. `doi:` CURIEs
    # were written before 2026-09-06 and were not resolvable IRIs.
    if doi:
        jsonld["@id"] = f"https://doi.org/{doi}"
        jsonld["identifier"] = f"https://doi.org/{doi}"
        jsonld["sameAs"] = f"https://doi.org/{doi}"
        jsonld["doi"] = doi
    else:
        jsonld["@id"] = served_id(os.path.relpath(os.path.join(dirpath, jsonld_name), str(_REPO_ROOT)).replace(os.sep, "/"))

    with open(os.path.join(dirpath, jsonld_name), "w") as f:
        json.dump(jsonld, f, indent=2)

    # README.md
    readme = f"""# {title}

## AI-Friendly Package

- **DOI:** {f'[{doi}](https://doi.org/{doi})' if doi else '(pending)'}
- **Version:** 1.0
- **Author:** {AUTHOR} (ORCID: [{ORCID}](https://orcid.org/{ORCID}))
- **Affiliation:** {AFFILIATION}
- **Date:** {pub_date}
- **License:** CC-BY-4.0

---

## Overview

{f'Auto-generated metadata package for {title}.' }
"""
    with open(os.path.join(dirpath, "README.md"), "w") as f:
        f.write(readme)

    return doi


def main():
    bare = find_bare_pdfs()
    if not bare:
        print("[efc-auto-meta] all paper directories have index.json")
        return 0

    print(f"[efc-auto-meta] {len(bare)} bare PDF(s) found, generating metadata:")
    for dirname, dirpath, pdf_name in bare:
        doi = generate_package(dirname, dirpath, pdf_name)
        doi_str = doi or "(no DOI found)"
        print(f"  {dirname}: {doi_str}")

    print(f"[efc-auto-meta] generated {len(bare)} package(s)")
    return 1  # signal that new packages were created


if __name__ == "__main__":
    sys.exit(main())
