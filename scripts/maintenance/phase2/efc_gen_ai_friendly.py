#!/usr/bin/env python3
"""
efc_gen_ai_friendly.py — [PHASE2_STAGED] Phase 2 rewrite of the AI-friendly
manifest generator with PDF scanning.

⚠️  DO NOT RUN AGAINST THE LIVE REPO.  ⚠️

This script OVERWRITES `docs/papers/efc/<paper>/index.json` with a
file-listing schema, destroying the ~27-field paper-metadata schema
that Phase 1 DOI propagation relies on. See
`scripts/maintenance/phase2/README.md` (Conflict 1) for details.

Execution is blocked by a runtime guard unless you pass
`--i-know-this-is-staged`.

For each paper directory under docs/papers/efc/:
  1. Read existing metadata.json (or create from PDF filename + DOI pattern)
  2. Generate/update: index.json, schema.json, JSON-LD, citations.bib
  3. Create stub src/, data/, examples/ dirs if missing
  4. Extract DOIs, test results, Δχ² values from PDF text (via pdftotext)
  5. Write paper_extractions.json with everything found

Usage (ONLY from a test fixture — never from the real repo root):
    python3 scripts/maintenance/phase2/efc_gen_ai_friendly.py \\
        --root /tmp/efc_phase2_test --i-know-this-is-staged
"""

from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PAPERS_DIR = REPO_ROOT / "docs" / "papers" / "efc"


def find_paper_dirs(base: Path) -> list[Path]:
    dirs: list[Path] = []
    if not base.exists():
        return dirs
    for d in sorted(base.rglob("*")):
        if d.is_dir() and list(d.glob("*.pdf")):
            if not any(d.is_relative_to(existing) and d != existing for existing in dirs):
                dirs.append(d)
    return dirs


def extract_pdf_text(pdf_path: Path, max_pages: int = 20) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", "-l", str(max_pages), str(pdf_path), "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ""


def extract_figshare_dois(text: str) -> list[str]:
    pattern = r"10\.6084/m9\.figshare\.(\d{7,8})"
    found = re.findall(pattern, text)
    standalone = re.findall(r"\b(31\d{6})\b", text)
    return sorted(set(found + standalone))


def extract_arxiv_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"arXiv:(\d{4}\.\d{4,5})", text)))


def extract_quantitative_results(text: str) -> dict:
    results: dict = {}
    for pat in (
        r"[Δ\\Delta]\s*χ[²2]\s*[=≈]\s*([−\-]?\d+\.?\d*)",
        r"Delta\s*chi2?\s*[=≈]\s*([−\-]?\d+\.?\d*)",
    ):
        m = re.findall(pat, text)
        if m:
            results["delta_chi2_values"] = [float(v.replace("−", "-")) for v in m]
            break
    for pat in (r"[Δ\\Delta]\s*AIC\s*[=≈]\s*([−\-+]?\d+\.?\d*)",):
        m = re.findall(pat, text)
        if m:
            results["delta_aic_values"] = [float(v.replace("−", "-")) for v in m]
            break
    m = re.findall(r"(\d+\.?\d*)\s*[σ\\sigma]", text)
    if m:
        results["sigma_values"] = [float(v) for v in m]
    if re.search(r"\bPASS\b", text):
        results["has_pass"] = True
    if re.search(r"\bFAIL\b", text):
        results["has_fail"] = True
    if re.search(r"\bDISCREPANT\b", text, re.IGNORECASE):
        results["has_discrepant"] = True
    if re.search(r"pre.?regist", text, re.IGNORECASE):
        results["pre_registered"] = True
    if re.search(r"frozen.?param|no.?refitt?ing|keff\s*=\s*0", text, re.IGNORECASE):
        results["frozen_params"] = True
    val_ids = re.findall(r"EFC-VAL-\d{4}-\d{3}", text)
    if val_ids:
        results["validation_report_ids"] = sorted(set(val_ids))
    return results


def extract_test_entries(text: str) -> list[str]:
    PATTERN_MAP = {
        r"rotation\s+curve|SPARC|RAR": "val_rotation_curves",
        r"weak.?lensing|cosmic\s+shear|KiDS|DES\s+Y[36]": "val_weak_lensing",
        r"BAO\s+transfer|cross.?survey": "val_bao_transfer",
        r"ISW\s+cross|void\s+ISW|sign.?flip": "val_isw",
        r"CMB\s+power|Planck.*TT": "val_cmb_power",
        r"Solar\s+System|PPN|Cassini": "val_solar_system",
        r"Bullet\s+Cluster": "val_bullet_cluster",
        r"cluster\s+entropy|ICM\s+thermo": "val_cluster_entropy",
        r"H.?0\s+tension|Hubble\s+tension": "val_h0_tension",
        r"JWST.*early\s+galax|high.?z\s+abundance": "val_jwst_early",
        r"μ.*Σ\s+valley|survival\s+valley": "val_mu_sigma_valley",
        r"lensing\s+barrier": "val_lensing_barrier",
        r"fσ.*8.*LOO|leave.?one.?out": "val_fσ8_loo",
        r"multi.?epoch.*growth|fσ8.*trajectory": "val_multi_epoch_growth",
        r"KT[1-5]|Newton\s+recovery|Graph.?AQUAL": "val_discrete_gravity",
        r"regime\s+transition.*μ|stiffness\s+response": "val_regime_transition",
        r"EFC-C|consciousness|neural\s+entropy": "val_efc_c",
        r"P3.*lensing|S8.*ratio|DES\s+Y6": "val_p3_lensing",
        r"Relativistic\s+Action|F\(φ\)R": "val_relativistic_action",
        r"Covariant\s+EFT": "val_covariant_eft",
        r"BE\s+RAR|Bose.*Einstein.*RAR": "val_be_rar",
        r"six.?probe\s+kill|kill.?test": "val_six_probe_kill",
    }
    hints: list[str] = []
    for pattern, entry_id in PATTERN_MAP.items():
        if re.search(pattern, text, re.IGNORECASE):
            hints.append(entry_id)
    return hints


def ensure_dir_structure(paper_dir: Path) -> None:
    for sub in ("src", "data", "examples"):
        d = paper_dir / sub
        d.mkdir(exist_ok=True)
        readme = d / "README.md"
        if not readme.exists():
            readme.write_text(f"# {sub}/\n\nAuto-generated stub. Add {sub} files here.\n")


def read_or_create_metadata(paper_dir: Path) -> dict:
    meta_path = paper_dir / "metadata.json"
    if meta_path.exists():
        with open(meta_path, "r") as f:
            return json.load(f)
    pdfs = list(paper_dir.glob("*.pdf"))
    name = paper_dir.name
    doi_match = re.search(r"(\d{8})", name)
    meta = {
        "title": name.replace("_", " ").replace("-", " ").title(),
        "directory": str(paper_dir.relative_to(REPO_ROOT)),
        "primary_pdf": pdfs[0].name if pdfs else "",
        "figshare_id": doi_match.group(1) if doi_match else "",
        "doi": f"10.6084/m9.figshare.{doi_match.group(1)}" if doi_match else "",
        "created": datetime.now(timezone.utc).isoformat(),
        "ai_generated": True,
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    return meta


def generate_index_json(paper_dir: Path, metadata: dict) -> None:
    files = []
    for f in sorted(paper_dir.rglob("*")):
        if f.is_file() and f.name != ".DS_Store":
            rel = str(f.relative_to(paper_dir))
            role = _classify_file_role(f)
            files.append({"path": rel, "role": role, "size": f.stat().st_size})
    index = {
        "package": metadata.get("title", paper_dir.name),
        "version": "1.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }
    with open(paper_dir / "index.json", "w") as f:
        json.dump(index, f, indent=2)


def _classify_file_role(f: Path) -> str:
    ext = f.suffix.lower()
    name = f.name.lower()
    if ext == ".pdf":
        return "primary_document"
    if ext == ".bib":
        return "bibliography"
    if ext == ".jsonld" or name.endswith(".jsonld"):
        return "linked_data"
    if "schema" in name and ext == ".json":
        return "json_schema"
    if "metadata" in name and ext == ".json":
        return "metadata"
    if ext == ".json":
        return "data" if "data" in str(f.parent) else "config"
    if ext == ".py":
        return "implementation" if "src" in str(f.parent) else "demo"
    if ext == ".csv":
        return "table_data"
    if ext in (".md", ".txt"):
        return "documentation"
    return "other"


def generate_schema_json(paper_dir: Path, metadata: dict) -> None:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": f"EFC Paper: {metadata.get('title', '')}",
        "type": "object",
        "properties": {
            "doi": {"type": "string", "pattern": r"^10\.\d{4,}/.+$"},
            "title": {"type": "string"},
            "figshare_id": {"type": "string", "pattern": r"^\d{8}$"},
        },
    }
    with open(paper_dir / "schema.json", "w") as f:
        json.dump(schema, f, indent=2)


def generate_jsonld(paper_dir: Path, metadata: dict) -> None:
    doi = metadata.get("doi", "")
    jsonld = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "name": metadata.get("title", ""),
        "identifier": doi,
        "url": f"https://doi.org/{doi}" if doi else "",
        "isPartOf": {
            "@type": "CreativeWorkSeries",
            "name": "Energy-Flow Cosmology (EFC) Working Papers",
        },
        "datePublished": metadata.get("created", ""),
    }
    fname = paper_dir.name.replace(" ", "-").lower()
    with open(paper_dir / f"{fname}.jsonld", "w") as f:
        json.dump(jsonld, f, indent=2)


def generate_citations_bib(paper_dir: Path, metadata: dict) -> None:
    doi = metadata.get("doi", "")
    fig_id = metadata.get("figshare_id", "")
    title = metadata.get("title", "")
    bib = f"""@misc{{efc_{fig_id},
  title  = {{{title}}},
  author = {{EFC Research Programme}},
  year   = {{2026}},
  doi    = {{{doi}}},
  url    = {{https://doi.org/{doi}}},
  note   = {{Energy-Flow Cosmology working paper}}
}}
"""
    bib_path = paper_dir / "citations.bib"
    if not bib_path.exists():
        bib_path.write_text(bib)


def process_one_paper(paper_dir: Path) -> dict:
    print(f"  Processing: {paper_dir.name}")
    metadata = read_or_create_metadata(paper_dir)
    ensure_dir_structure(paper_dir)
    generate_index_json(paper_dir, metadata)
    generate_schema_json(paper_dir, metadata)
    generate_jsonld(paper_dir, metadata)
    generate_citations_bib(paper_dir, metadata)
    pdfs = list(paper_dir.glob("*.pdf"))
    extraction = {
        "directory": str(paper_dir.relative_to(REPO_ROOT)),
        "figshare_id": metadata.get("figshare_id", ""),
        "doi": metadata.get("doi", ""),
        "title": metadata.get("title", ""),
        "dois_referenced": [],
        "arxiv_ids": [],
        "quantitative": {},
        "test_hints": [],
    }
    if pdfs:
        text = extract_pdf_text(pdfs[0])
        if text:
            extraction["dois_referenced"] = extract_figshare_dois(text)
            extraction["arxiv_ids"] = extract_arxiv_ids(text)
            extraction["quantitative"] = extract_quantitative_results(text)
            extraction["test_hints"] = extract_test_entries(text)
    return extraction


def _phase2_safety_guard(args: argparse.Namespace) -> None:
    """Block accidental execution against the real repo."""
    if not getattr(args, "i_know_this_is_staged", False):
        print(
            "ERROR: This is a PHASE 2 STAGED script that would overwrite "
            "138 paper-metadata index.json files with a file-listing schema.",
            file=sys.stderr,
        )
        print(
            "       See scripts/maintenance/phase2/README.md for the "
            "conflict details and migration checklist.",
            file=sys.stderr,
        )
        print(
            "       Pass --i-know-this-is-staged to bypass this guard.",
            file=sys.stderr,
        )
        sys.exit(2)
    if args.root == REPO_ROOT:
        print(
            "ERROR: --root is pointing at the live repository. "
            "This script must only run against a test fixture.",
            file=sys.stderr,
        )
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="[PHASE2_STAGED] AI-friendly generator")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--i-know-this-is-staged", action="store_true")
    args = parser.parse_args()

    _phase2_safety_guard(args)

    papers_dir = args.root / "docs" / "papers" / "efc"
    extractions_file = args.root / "docs" / "validation-ledger" / "paper_extractions.json"
    if not papers_dir.exists():
        print(f"Papers directory not found: {papers_dir}")
        sys.exit(1)
    extractions_file.parent.mkdir(parents=True, exist_ok=True)

    paper_dirs = find_paper_dirs(papers_dir)
    print(f"Found {len(paper_dirs)} paper directories")

    all_extractions = []
    all_dois: set[str] = set()
    for pd in paper_dirs:
        ext = process_one_paper(pd)
        all_extractions.append(ext)
        if ext["figshare_id"]:
            all_dois.add(ext["figshare_id"])
        all_dois.update(ext["dois_referenced"])

    output = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_papers": len(paper_dirs),
        "total_unique_dois": len(all_dois),
        "all_dois": sorted(all_dois),
        "papers": all_extractions,
    }
    with open(extractions_file, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nDone. {len(paper_dirs)} papers processed.")
    print(f"  Unique DOIs found: {len(all_dois)}")
    print(f"  Extractions: {extractions_file}")


if __name__ == "__main__":
    main()
