#!/usr/bin/env python3
"""
EFC AI-Friendly Package Generator

Walks every paper directory under docs/papers/efc/ and ensures a uniform
AI-friendly metadata layer is present:

  - index.json         (stable identity; created if missing)
  - metadata.json      (schema-aligned superset; created if missing)
  - <slug>.jsonld      (schema.org ScholarlyArticle; created if missing)
  - README.md          (human-readable summary; created if missing)
  - ai_manifest.json   (machine-truth view of files; ALWAYS regenerated)

Hand-curated packages are preserved: existing files are never overwritten
except for ai_manifest.json which is the live view of directory contents.

Idempotent. Safe to run on every session start.

Also writes docs/papers/efc/ai_friendly_index.json with a catalogue of all
generated packages.
"""
from __future__ import annotations
import json
import os
import re
import sys
import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "papers", "efc"))
TODAY = datetime.date.today().isoformat()

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf",
    "efc_graph_edges.json", "efc_graph_schema.json",
    "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
    "_archived",
}


def slugify(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    return s[:120] or "paper"


def humanize(name: str) -> str:
    s = name.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def list_files(d: str):
    out = []
    for root, dirs, files in os.walk(d):
        # Skip transient/cache directories that vary across machines
        dirs[:] = [x for x in dirs if x not in ("__pycache__", ".git", ".pytest_cache", ".mypy_cache", ".ipynb_checkpoints")]
        for f in files:
            if f.endswith((".pyc", ".pyo")) or f == ".DS_Store":
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, d)
            try:
                size = os.path.getsize(p)
            except OSError:
                size = 0
            out.append((rel, size))
    return sorted(out)


def find_pdfs(files):
    return [f for f, _ in files if f.lower().endswith(".pdf")]


def find_text_excerpts(d: str, files):
    excerpts = {}
    for rel, _ in files:
        if rel.lower().endswith((".md", ".txt", ".tex", ".rst")) and rel != "README.md":
            try:
                with open(os.path.join(d, rel), "r", errors="ignore") as fh:
                    excerpts[rel] = fh.read(4000)
            except OSError:
                pass
    return excerpts


def regime_guess(text: str):
    return [r for r in ("L0", "L1", "L2", "L3") if re.search(rf"\b{r}\b", text)]


def track_guess(name: str, text: str):
    n = (name + " " + text).lower()
    if any(k in n for k in ["sparc", "rotation", "lensing", "bao", "cmb", "desi", "hubble",
                             "growth", "isw", "rsd", "cluster", "cosmolog"]):
        return "Spor 1 — Galactic/Cosmological"
    if any(k in n for k in ["cognit", "psychiatric", "rlhf", "consciousness", "neural",
                             "human-ai", "co-reflection", "symbiosis"]):
        return "Spor 2/3 — Cognitive / Human-AI"
    if any(k in n for k in ["grid", "graph", "discrete", "field equation", "action",
                             "ppn", "eft", "relativistic"]):
        return "Spor 4 — Theory / Grid / EFT"
    return "Spor general"


def write_if_absent(path: str, content: str) -> bool:
    if os.path.exists(path):
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)
    return True


def write_always(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)


def write_json_idempotent(path: str, payload: dict, ts_field: str = "generated") -> bool:
    """Write payload as JSON, but preserve the existing ts_field timestamp
    when no other field has changed. Prevents daily diff churn on files that
    only differ in their auto-stamped 'generated' date.

    Returns True if the file was (re)written, False if untouched.
    """
    if os.path.exists(path):
        try:
            with open(path) as fh:
                existing = json.load(fh)
        except (OSError, json.JSONDecodeError):
            existing = None
        if isinstance(existing, dict):
            old_no_ts = {k: v for k, v in existing.items() if k != ts_field}
            new_no_ts = {k: v for k, v in payload.items() if k != ts_field}
            if old_no_ts == new_no_ts:
                return False
            if ts_field in existing and ts_field not in payload:
                payload = dict(payload)
                payload[ts_field] = existing[ts_field]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fh:
        fh.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return True


def build_for_dir(name: str):
    d = os.path.join(ROOT, name)
    if not os.path.isdir(d):
        return None
    # We need the PDF list + excerpts before writing anything, but the
    # full ``files`` snapshot (used by ai_manifest.json) must come LAST,
    # after every other idempotent write below.  Otherwise the first run
    # on a fresh paper directory writes a stale manifest that omits the
    # LICENSE / citations.bib / schema.json we are about to create, and
    # a second pass produces a diff.  See issue traced in PR #155 follow-up.
    initial_files = list_files(d)
    pdfs = find_pdfs(initial_files)
    excerpts = find_text_excerpts(d, initial_files)
    excerpt_blob = " ".join(excerpts.values())
    title = humanize(name)
    slug = slugify(name)
    regs = regime_guess(excerpt_blob + " " + name)
    track = track_guess(name, excerpt_blob)

    pkg_base = {
        "id": slug,
        "directory": name,
        "title": title,
        "author": "Morten Magnusson",
        "orcid": "0009-0002-4860-5095",
        "affiliation": "Symbiose Research",
        "license": "CC-BY-4.0",
        "package_type": "ai-friendly-paper",
        "schema_version": "1.0",
        "generated": TODAY,
        "track": track,
        "regimes": regs,
        "primary_pdf": pdfs[0] if pdfs else None,
        "all_pdfs": pdfs,
    }

    created = []
    idx = {
        "id": slug,
        "title": title,
        "author": pkg_base["author"],
        "orcid": pkg_base["orcid"],
        "affiliation": pkg_base["affiliation"],
        "license": pkg_base["license"],
        "track": track,
        "regimes": regs,
        "primary_pdf": pkg_base["primary_pdf"],
        "files": [p for p, _ in initial_files],
        "see_also": "ai_manifest.json",
    }
    if write_if_absent(os.path.join(d, "index.json"),
                       json.dumps(idx, indent=2, ensure_ascii=False) + "\n"):
        created.append("index.json")

    meta = {
        "schema_version": "1.0",
        "package_type": "ai-friendly-paper",
        "paper": {
            "title": title,
            "directory": name,
            "author": {"name": pkg_base["author"], "orcid": pkg_base["orcid"], "affiliation": pkg_base["affiliation"]},
            "license": pkg_base["license"],
        },
        "domain": {"track": track, "regimes": regs},
        "files": [{"path": p, "bytes": s} for p, s in initial_files],
        "primary_pdf": pkg_base["primary_pdf"],
    }
    if write_if_absent(os.path.join(d, "metadata.json"),
                       json.dumps(meta, indent=2, ensure_ascii=False) + "\n"):
        created.append("metadata.json")

    jsonld = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "name": title,
        "author": {
            "@type": "Person",
            "name": pkg_base["author"],
            "identifier": "https://orcid.org/" + pkg_base["orcid"],
            "affiliation": {"@type": "Organization", "name": pkg_base["affiliation"]},
        },
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "keywords": ["Energy-Flow Cosmology", "EFC"] + regs,
        "about": [track],
    }
    if write_if_absent(os.path.join(d, slug + ".jsonld"),
                       json.dumps(jsonld, indent=2, ensure_ascii=False) + "\n"):
        created.append(slug + ".jsonld")

    pdf_line = f"**Primary PDF:** `{pkg_base['primary_pdf']}`\n\n" if pkg_base["primary_pdf"] else ""
    files_md = "\n".join(f"- `{p}` ({s} B)" for p, s in initial_files[:50])
    if len(initial_files) > 50:
        files_md += f"\n- … ({len(initial_files)-50} more)"
    readme = f"""# {title}

**Author:** Morten Magnusson (ORCID 0009-0002-4860-5095) · Symbiose Research
**License:** CC-BY-4.0 · **Track:** {track} · **Regimes:** {", ".join(regs) if regs else "—"}

{pdf_line}This directory is an **AI-friendly** package: machine-readable metadata
(`index.json`, `metadata.json`, `ai_manifest.json`, `*.jsonld`) accompanies the
source materials so that LLMs and automated agents can ingest, cite, and
reproduce the work without scraping the PDF.

## Files

{files_md}

## Provenance

Auto-generated AI-friendly wrapper ({TODAY}). Hand-curated packages
(`WP4_BOSS_transfer_validation`, `Multi_epoch_Growth_Rate_Test_of_EFC`) provide
the schema reference; this directory follows the same conventions.
"""
    if write_if_absent(os.path.join(d, "README.md"), readme):
        created.append("README.md")

    # ── Additional 10/10 standard files ──────────────────
    # CITATION.cff
    cff = f"""cff-version: 1.2.0
message: "If you use this work, please cite it as below."
title: "{title}"
type: software
authors:
  - family-names: "Magnusson"
    given-names: "Morten"
    orcid: "https://orcid.org/0009-0002-4860-5095"
    affiliation: "Symbiose Research, Norway"
version: "1.0"
date-released: "{TODAY}"
license: "CC-BY-4.0"
repository-code: "https://github.com/supertedai/EFC"
keywords:
  - "Energy-Flow Cosmology"
{chr(10).join('  - "' + r + '"' for r in regs) if regs else '  - "EFC"'}
abstract: >
  {title}. Part of the Energy-Flow Cosmology research programme.
"""
    if write_if_absent(os.path.join(d, "CITATION.cff"), cff):
        created.append("CITATION.cff")

    # LICENSE
    lic = """Creative Commons Attribution 4.0 International (CC-BY-4.0)

Copyright (c) 2026 Morten Magnusson

You are free to share and adapt this material for any purpose, including
commercially, as long as you give appropriate credit.

Full license text: https://creativecommons.org/licenses/by/4.0/legalcode
"""
    if write_if_absent(os.path.join(d, "LICENSE"), lic):
        created.append("LICENSE")

    # citations.bib
    bib = f"""@misc{{magnusson2026_{slug.replace('-', '_')[:40]},
  author = {{Magnusson, Morten}},
  title = {{{title}}},
  year = {{2026}},
  publisher = {{Figshare}},
  url = {{https://github.com/supertedai/EFC}},
  note = {{Energy-Flow Cosmology research programme}}
}}
"""
    if write_if_absent(os.path.join(d, "citations.bib"), bib):
        created.append("citations.bib")

    # schema.json
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": f"{title} Schema",
        "type": "object",
        "properties": {
            "paper_id": {"type": "string"},
            "title": {"type": "string"},
            "version": {"type": "string"},
            "doi": {"type": ["string", "null"]},
            "key_results": {"type": "array", "items": {"type": "object"}},
            "parameters": {"type": "object"},
            "predictions": {"type": "array"},
        },
        "required": ["paper_id", "title"],
    }
    if write_if_absent(os.path.join(d, "schema.json"),
                       json.dumps(schema, indent=2, ensure_ascii=False) + "\n"):
        created.append("schema.json")

    # Re-scan NOW so ai_manifest.json reflects every file we just wrote.
    # This is the fix: previously the manifest was written before the
    # LICENSE / citations.bib / schema.json calls, leaving a stale snapshot
    # on first run.
    final_files = list_files(d)
    pkg = dict(pkg_base)
    pkg["files"] = [{"path": p, "bytes": s} for p, s in final_files if p != "ai_manifest.json"]
    pkg["n_files"] = len(final_files)
    pkg["n_pdfs"] = len(pdfs)
    write_json_idempotent(os.path.join(d, "ai_manifest.json"), pkg)

    return {
        "name": name, "title": title, "track": track, "regimes": regs,
        "primary_pdf": pkg["primary_pdf"], "created": created, "n_files": len(final_files),
    }


def main():
    summary = []
    for name in sorted(os.listdir(ROOT)):
        if name in SKIP_TOP:
            continue
        full = os.path.join(ROOT, name)
        if not os.path.isdir(full):
            continue
        s = build_for_dir(name)
        if s:
            summary.append(s)
    out_path = os.path.join(ROOT, "ai_friendly_index.json")
    write_json_idempotent(out_path, {
        "generated": TODAY,
        "n_packages": len(summary),
        "packages": summary,
    })
    created_total = sum(len(s["created"]) for s in summary)
    print(f"[efc-gen] {len(summary)} packages · {created_total} new files · catalogue: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
