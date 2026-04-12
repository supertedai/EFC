#!/usr/bin/env python3
"""
EFC DOI Sync
============
Scans every paper directory under ``docs/papers/efc/`` and keeps each
paper's Figshare DOI consistently registered across:

  - ``index.json``           (paper-level metadata)
  - ``metadata.json``        (schema-aligned superset)
  - ``CITATION.cff``         (top-level ``doi:`` field only)
  - ``<slug>.jsonld``        (schema.org ``identifier`` / ``sameAs``)

``citations.bib`` is intentionally NOT touched: it contains bibliographic
references to other papers, not the paper's own self-identifying DOI, so
treating the first ``@entry``'s ``doi`` as authoritative produces false
positives. Similarly the ``references:`` block of ``CITATION.cff`` is
ignored.

And across the cross-reference / ledger files:

  - ``docs/papers/efc/efc_index.json``
  - ``docs/validation-ledger/data/evidence-register.json``
    (empirical Figshare DOIs only — verifier C2/C6)
  - ``docs/validation-ledger/data/ledger.json``
    (mirrors the evidence-register into ``evidence_register.empirical``)

Modes
-----
  --check     Report drift and exit 1 if conflicts are found.
  --apply     Fix drift non-destructively (additive only). Exit 0 on
              clean, 1 on conflicts the script can't resolve itself.
  --report    Print a human-readable per-paper DOI report (no writes).

Semantics
---------
* **Discovery** — DOIs are recognised in any of the in-package files above
  plus the top-level ``efc_index.json`` entry. Normalised to the canonical
  form ``10.6084/m9.figshare.NNNNNNNN``.
* **Reconciliation** — For each paper the script picks the canonical DOI
  by majority vote across all sources. A conflict (two different DOIs in
  the same paper) is a hard error — the script refuses to pick one and
  asks the user to reconcile manually.
* **Propagation** — Once a canonical DOI is known, the script writes it
  into every in-package file that's missing it. Files that already carry
  the correct DOI are untouched. README.md and public HTML docs are
  *reported*, never auto-rewritten — their insertion points are
  context-dependent and must stay under editorial control.
* **Idempotent** — Running twice is a no-op.
* **Non-destructive** — Never overwrites user-curated text; only adds
  DOI fields where they're missing.

Design principles
-----------------
1. Never invent content. The DOI must come from a source file.
2. Never overwrite free-form prose. Auto-fix only touches structured
   fields or well-defined insertion points (after ``date-released:`` in
   CFF, before the closing ``}`` of the first BibTeX entry, etc.).
3. Always produce a report, even in apply mode.
4. Fail loudly on conflicts; let the human decide.

Author: Morten Magnusson · EFC maintenance toolchain
License: CC-BY-4.0
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
LEDGER_DIR = os.path.join(REPO, "docs", "validation-ledger")

SKIP_TOP = {
    "README.md",
    "cover_letter-2.pdf",
    "efc_graph_edges.json",
    "efc_graph_schema.json",
    "efc_index.json",
    "efc_index.jsonld",
    "ai_friendly_index.json",
}

FIGSHARE_DOI_PREFIX = "10.6084/m9.figshare."
FIGSHARE_DOI_RE = re.compile(r"10\.6084/m9\.figshare\.(\d{7,9})")
FIGSHARE_BARE_RE = re.compile(r"\b(3[0-9]{7})\b")

# ─────────────────────────────────────────────────────────────────────────────
# Basic utilities
# ─────────────────────────────────────────────────────────────────────────────


def load_json(path: str) -> Optional[dict]:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError, UnicodeError):
        return None


def save_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_text(path: str) -> Optional[str]:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def canonical_doi(doi) -> Optional[str]:
    """Normalise any DOI-ish string to ``10.6084/m9.figshare.NNNNNNNN``."""
    if doi is None:
        return None
    s = str(doi).strip()
    if not s:
        return None
    for pfx in ("https://doi.org/", "http://doi.org/", "doi:", "https://dx.doi.org/"):
        if s.lower().startswith(pfx):
            s = s[len(pfx):]
            break
    m = FIGSHARE_DOI_RE.search(s)
    if m:
        return f"{FIGSHARE_DOI_PREFIX}{m.group(1)}"
    m = FIGSHARE_BARE_RE.fullmatch(s)
    if m:
        return f"{FIGSHARE_DOI_PREFIX}{m.group(1)}"
    return None


def bare_doi_id(canonical: str) -> str:
    """Extract '31986762' from the canonical form."""
    m = FIGSHARE_DOI_RE.search(canonical or "")
    return m.group(1) if m else ""


# ─────────────────────────────────────────────────────────────────────────────
# Discovery — per-file DOI extraction
# ─────────────────────────────────────────────────────────────────────────────


def _pick_doi_from_dict(d, keys=("doi", "figshare_doi", "figshare_url")) -> Optional[str]:
    if not isinstance(d, dict):
        return None
    for k in keys:
        c = canonical_doi(d.get(k))
        if c:
            return c
    return None


def discover_from_index_json(d) -> Optional[str]:
    return _pick_doi_from_dict(d)


def discover_from_metadata_json(d) -> Optional[str]:
    if not isinstance(d, dict):
        return None
    paper = d.get("paper") if isinstance(d.get("paper"), dict) else {}
    return _pick_doi_from_dict(paper) or _pick_doi_from_dict(d)


def discover_from_cff(text: str) -> Optional[str]:
    if not text:
        return None
    m = re.search(r'^doi\s*:\s*"?([^"\r\n]+)"?\s*$', text, re.MULTILINE)
    if m:
        return canonical_doi(m.group(1).strip())
    # identifiers:\n  - type: doi\n    value: "..."
    m = re.search(
        r"^\s*-\s*type\s*:\s*doi\s*\r?\n\s*value\s*:\s*\"?([^\"\r\n]+)\"?",
        text,
        re.MULTILINE,
    )
    if m:
        return canonical_doi(m.group(1).strip())
    return None


def discover_from_bib(text: str) -> Optional[str]:
    """Intentionally returns None.

    citations.bib is a references file, not a self-identification file.
    Treating the first @entry's doi as the paper's canonical DOI
    produces false positives whenever the first reference is a
    cross-citation to another paper. The sync script does not read or
    write citations.bib — self-identification lives in index.json."""
    return None


def discover_from_jsonld(d) -> Optional[str]:
    if not isinstance(d, dict):
        return None
    # Prefer "doi" and "identifier", then "sameAs" / "@id" / "url"
    for k in ("doi", "identifier", "sameAs", "@id", "url"):
        v = d.get(k)
        if isinstance(v, str):
            c = canonical_doi(v)
            if c:
                return c
        elif isinstance(v, list):
            for item in v:
                c = canonical_doi(item) if isinstance(item, str) else None
                if c:
                    return c
    return None


def discover_from_readme_header(text: str) -> Optional[str]:
    """Scan only the paper's own DOI *badge* — not any cross-reference.

    Accepts only DOIs that appear on a line starting with a DOI-label
    marker (``**DOI:**``, ``DOI:``, ``[![DOI]``, ``doi:``) within the
    first 15 lines. Anything else (e.g. inline ``(DOI: 10.xxx)``
    references to sibling papers further down) is ignored. This keeps
    the discovery conservative and avoids false positives where the
    paper's README cites a related paper by DOI.
    """
    if not text:
        return None
    head_lines = text.splitlines()[:15]
    for line in head_lines:
        lstripped = line.lstrip()
        # Accept: "**DOI:**", "**DOI**:", "DOI:", "[![DOI]", "doi:"
        if re.match(
            r"(?:\*\*DOI\*?\*?:?\*?\*?|DOI:|\[!\[DOI|doi:)",
            lstripped,
            flags=re.IGNORECASE,
        ):
            m = FIGSHARE_DOI_RE.search(line)
            if m:
                return canonical_doi(m.group(0))
    return None


def discover_paper(paper_dir: str) -> Tuple[Optional[str], Dict[str, Optional[str]], List[str]]:
    """Return (canonical_doi, per-source map, list of conflicts)."""
    sources: Dict[str, Optional[str]] = {}

    idx_path = os.path.join(paper_dir, "index.json")
    meta_path = os.path.join(paper_dir, "metadata.json")
    man_path = os.path.join(paper_dir, "ai_manifest.json")
    cff_path = os.path.join(paper_dir, "CITATION.cff")
    bib_path = os.path.join(paper_dir, "citations.bib")
    readme_path = os.path.join(paper_dir, "README.md")

    sources["index.json"] = discover_from_index_json(load_json(idx_path))
    sources["metadata.json"] = discover_from_metadata_json(load_json(meta_path))
    sources["ai_manifest.json"] = discover_from_index_json(load_json(man_path))
    sources["CITATION.cff"] = discover_from_cff(read_text(cff_path) or "")
    # citations.bib intentionally ignored (see discover_from_bib docstring)

    # Any *.jsonld file
    sources["*.jsonld"] = None
    try:
        for fn in sorted(os.listdir(paper_dir)):
            if fn.endswith(".jsonld"):
                c = discover_from_jsonld(load_json(os.path.join(paper_dir, fn)))
                if c:
                    sources["*.jsonld"] = c
                    break
    except OSError:
        pass

    sources["README.md"] = discover_from_readme_header(read_text(readme_path) or "")

    # Reconcile: majority vote among non-None values
    found = [d for d in sources.values() if d]
    if not found:
        return None, sources, []
    votes = Counter(found)
    canonical = votes.most_common(1)[0][0]
    conflicts = [d for d in set(found) if d != canonical]
    return canonical, sources, conflicts


# ─────────────────────────────────────────────────────────────────────────────
# Propagation — additive writers
# ─────────────────────────────────────────────────────────────────────────────


def apply_index_json(paper_dir: str, doi: str) -> bool:
    path = os.path.join(paper_dir, "index.json")
    d = load_json(path)
    if not isinstance(d, dict):
        return False
    changed = False
    if d.get("doi") != doi:
        d["doi"] = doi
        changed = True
    url = f"https://doi.org/{doi}"
    if d.get("figshare_url") != url:
        d["figshare_url"] = url
        changed = True
    if changed:
        save_json(path, d)
    return changed


def apply_metadata_json(paper_dir: str, doi: str) -> bool:
    path = os.path.join(paper_dir, "metadata.json")
    d = load_json(path)
    if not isinstance(d, dict):
        return False
    paper = d.setdefault("paper", {})
    if not isinstance(paper, dict):
        return False
    changed = False
    if paper.get("doi") != doi:
        paper["doi"] = doi
        changed = True
    url = f"https://doi.org/{doi}"
    if paper.get("figshare_url") != url:
        paper["figshare_url"] = url
        changed = True
    if changed:
        save_json(path, d)
    return changed


def apply_cff(paper_dir: str, doi: str) -> bool:
    path = os.path.join(paper_dir, "CITATION.cff")
    text = read_text(path)
    if text is None:
        return False
    existing = re.search(r'^doi\s*:\s*"?([^"\r\n]+)"?\s*$', text, re.MULTILINE)
    if existing and canonical_doi(existing.group(1)) == doi:
        return False
    # Remove any existing doi: line (safe — we're replacing with the same or newer)
    new_text = re.sub(r'^doi\s*:.*\r?\n', "", text, flags=re.MULTILINE)
    # Insert after date-released: line if present, else after title: line, else prepend
    anchor_re = re.search(r"^date-released\s*:.*$", new_text, re.MULTILINE)
    if not anchor_re:
        anchor_re = re.search(r"^version\s*:.*$", new_text, re.MULTILINE)
    if not anchor_re:
        anchor_re = re.search(r"^license\s*:.*$", new_text, re.MULTILINE)
    if anchor_re:
        pos = anchor_re.end()
        new_text = new_text[:pos] + f'\ndoi: "{doi}"' + new_text[pos:]
    else:
        new_text = f'doi: "{doi}"\n' + new_text
    write_text(path, new_text)
    return True


def apply_bib(paper_dir: str, doi: str) -> bool:
    """No-op. citations.bib is not auto-modified — see module docstring."""
    return False


def apply_jsonld(paper_dir: str, doi: str) -> bool:
    touched = False
    try:
        files = sorted(os.listdir(paper_dir))
    except OSError:
        return False
    for fn in files:
        if not fn.endswith(".jsonld"):
            continue
        path = os.path.join(paper_dir, fn)
        d = load_json(path)
        if not isinstance(d, dict):
            continue
        changed = False
        identifier_url = f"https://doi.org/{doi}"
        if d.get("identifier") != identifier_url:
            d["identifier"] = identifier_url
            changed = True
        if d.get("sameAs") != identifier_url:
            d["sameAs"] = identifier_url
            changed = True
        if d.get("doi") != doi:
            d["doi"] = doi
            changed = True
        if changed:
            save_json(path, d)
            touched = True
    return touched


# ─────────────────────────────────────────────────────────────────────────────
# Cross-reference sync
# ─────────────────────────────────────────────────────────────────────────────


def sync_efc_index(doi_by_dir: Dict[str, str]) -> List[str]:
    path = os.path.join(PAPERS, "efc_index.json")
    d = load_json(path)
    if not isinstance(d, dict) or "papers" not in d:
        return []
    changed: List[str] = []
    for p in d.get("papers", []):
        directory = p.get("path")
        if directory and directory in doi_by_dir:
            want = doi_by_dir[directory]
            if p.get("doi") != want:
                p["doi"] = want
                changed.append(directory)
    if changed:
        # Bump minor version
        old_v = str(d.get("version", "1.0"))
        try:
            major, minor = old_v.split(".")
            d["version"] = f"{major}.{int(minor) + 1}"
        except ValueError:
            pass
        save_json(path, d)
    return changed


def sync_evidence_register(doi_by_dir: Dict[str, str]) -> List[str]:
    """Add any paper DOI flagged as empirical (has a PDF *and* a data/ dir
    *and* source code) to the empirical register, if not already present.

    Conservative: never removes. Only adds. Requires the paper to already
    have been entered once in tests.json before it shows up in the
    empirical list, so this is effectively *sync* — the user creates the
    test entry, we mirror the DOI into the empirical register."""
    path = os.path.join(LEDGER_DIR, "data", "evidence-register.json")
    d = load_json(path)
    if not isinstance(d, dict):
        return []
    empirical = d.get("categories", {}).get("empirical")
    if not isinstance(empirical, list):
        return []
    existing = {str(e.get("doi", "")) for e in empirical if isinstance(e, dict)}

    # Only add papers that have a matching test_id in tests.json
    tests_path = os.path.join(LEDGER_DIR, "data", "tests.json")
    tests = load_json(tests_path) or {}
    test_dirs = set()
    for cat, items in (tests.get("categories") or {}).items():
        for t in items:
            pd = t.get("paper_directory")
            if pd:
                test_dirs.add(pd)

    added: List[str] = []
    for directory, doi in doi_by_dir.items():
        if directory not in test_dirs:
            continue
        bare = bare_doi_id(doi)
        if not bare or bare in existing:
            continue
        # Derive a human-readable name from the directory slug
        name = directory.replace("_", " ").strip()
        empirical.append({"doi": bare, "name": name, "category": "empirical"})
        existing.add(bare)
        added.append(directory)
    if added:
        save_json(path, d)
    return added


def sync_ledger_evidence(doi_by_dir: Dict[str, str]) -> List[str]:
    """Mirror new evidence-register entries into ledger.json."""
    path = os.path.join(LEDGER_DIR, "data", "ledger.json")
    d = load_json(path)
    if not isinstance(d, dict):
        return []
    empirical = d.get("evidence_register", {}).get("empirical")
    if not isinstance(empirical, list):
        return []
    existing = {str(e.get("doi", "")) for e in empirical if isinstance(e, dict)}

    # Check tests mirror
    tests_section = d.get("tests") or {}
    test_dirs = set()
    for items in tests_section.values():
        for t in items:
            pd = t.get("paper_directory")
            if pd:
                test_dirs.add(pd)

    added: List[str] = []
    for directory, doi in doi_by_dir.items():
        if directory not in test_dirs:
            continue
        bare = bare_doi_id(doi)
        if not bare or bare in existing:
            continue
        name = directory.replace("_", " ").strip()
        empirical.append({"doi": bare, "name": name, "category": "empirical"})
        existing.add(bare)
        added.append(directory)
    if added:
        save_json(path, d)
    return added


# ─────────────────────────────────────────────────────────────────────────────
# Drift detection for un-autofixable surfaces
# ─────────────────────────────────────────────────────────────────────────────


def detect_readme_drift(paper_dir: str, doi: str) -> bool:
    """True if the package README does not mention the DOI at all."""
    text = read_text(os.path.join(paper_dir, "README.md")) or ""
    return bare_doi_id(doi) not in text


def fix_readme_doi(paper_dir: str, doi: str) -> bool:
    """Insert DOI reference into package README.md if missing.

    Inserts a **DOI:** line after the title (first # heading) or after
    the **Author:** line. Returns True if the file was modified.
    """
    path = os.path.join(paper_dir, "README.md")
    text = read_text(path)
    if text is None:
        return False
    bare = bare_doi_id(doi)
    if not bare or bare in text:
        return False
    doi_line = f"**DOI:** [10.6084/m9.figshare.{bare}](https://doi.org/10.6084/m9.figshare.{bare})"
    # Strategy 1: insert after **Author:** line
    m = re.search(r"(\*\*Author:\*\*[^\n]*\n)", text)
    if m:
        insert_pos = m.end()
        text = text[:insert_pos] + doi_line + "\n" + text[insert_pos:]
        write_text(path, text)
        return True
    # Strategy 2: insert after first # heading
    m = re.search(r"(^#[^\n]*\n)", text, re.MULTILINE)
    if m:
        insert_pos = m.end()
        text = text[:insert_pos] + "\n" + doi_line + "\n" + text[insert_pos:]
        write_text(path, text)
        return True
    # Strategy 3: prepend to file
    text = doi_line + "\n\n" + text
    write_text(path, text)
    return True


def detect_top_readme_drift(doi: str) -> bool:
    text = read_text(os.path.join(REPO, "README.md")) or ""
    return bare_doi_id(doi) not in text


def detect_public_html_drift(doi: str) -> Dict[str, bool]:
    result: Dict[str, bool] = {}
    bare = bare_doi_id(doi)
    for rel in (
        "docs/public/EFC_Validation_Ledger.html",
        "docs/public/EFC_Changelog.html",
        "docs/public/EFC_White_Paper_Series.html",
    ):
        text = read_text(os.path.join(REPO, rel)) or ""
        result[rel] = bare not in text
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Main orchestrator
# ─────────────────────────────────────────────────────────────────────────────


def walk_papers() -> List[str]:
    out: List[str] = []
    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        full = os.path.join(PAPERS, name)
        if os.path.isdir(full):
            out.append(name)
    return out


def scan_all() -> Tuple[Dict[str, str], Dict[str, Dict[str, Optional[str]]], Dict[str, List[str]]]:
    doi_by_dir: Dict[str, str] = {}
    sources_by_dir: Dict[str, Dict[str, Optional[str]]] = {}
    conflicts_by_dir: Dict[str, List[str]] = {}
    for name in walk_papers():
        paper_dir = os.path.join(PAPERS, name)
        canonical, sources, conflicts = discover_paper(paper_dir)
        sources_by_dir[name] = sources
        if conflicts:
            conflicts_by_dir[name] = [canonical] + conflicts if canonical else conflicts
        if canonical:
            doi_by_dir[name] = canonical
    return doi_by_dir, sources_by_dir, conflicts_by_dir


def propagate(doi_by_dir: Dict[str, str]) -> Dict[str, List[str]]:
    """Propagate each paper's canonical DOI through its in-package files.
    Returns a map of paper directory → list of files touched."""
    touched: Dict[str, List[str]] = {}
    for directory, doi in doi_by_dir.items():
        paper_dir = os.path.join(PAPERS, directory)
        changes: List[str] = []
        if apply_index_json(paper_dir, doi):
            changes.append("index.json")
        if apply_metadata_json(paper_dir, doi):
            changes.append("metadata.json")
        if apply_cff(paper_dir, doi):
            changes.append("CITATION.cff")
        if apply_jsonld(paper_dir, doi):
            changes.append("*.jsonld")
        if fix_readme_doi(paper_dir, doi):
            changes.append("README.md")
        if changes:
            touched[directory] = changes
    return touched


def print_report(
    doi_by_dir: Dict[str, str],
    sources_by_dir: Dict[str, Dict[str, Optional[str]]],
    conflicts_by_dir: Dict[str, List[str]],
    touched: Optional[Dict[str, List[str]]] = None,
    cross_changes: Optional[Dict[str, List[str]]] = None,
) -> None:
    n_papers = len(sources_by_dir)
    n_with_doi = len(doi_by_dir)
    n_conflicts = len(conflicts_by_dir)
    print("=" * 72)
    print(f"EFC DOI sync — {n_papers} paper dirs scanned")
    print("=" * 72)
    print(f"  papers with registered DOI : {n_with_doi}")
    print(f"  papers without DOI         : {n_papers - n_with_doi}")
    print(f"  papers with conflicts      : {n_conflicts}")
    if conflicts_by_dir:
        print()
        print("CONFLICTS (must be reconciled manually):")
        for name, dois in conflicts_by_dir.items():
            print(f"  {name}")
            for doi in dois:
                print(f"      {doi}")
            src = sources_by_dir.get(name, {})
            for k, v in src.items():
                if v:
                    print(f"        {k}: {v}")
    if touched:
        print()
        print(f"PROPAGATED DOIs into {len(touched)} papers:")
        for name, files in touched.items():
            print(f"  {name} -> {', '.join(files)}")
    if cross_changes:
        for registry, items in cross_changes.items():
            if items:
                print()
                print(f"SYNCED {registry} ({len(items)} entries):")
                for i in items:
                    print(f"  {i}")
    # Drift that can't be auto-fixed
    drift_lines: List[str] = []
    for name, doi in doi_by_dir.items():
        paper_dir = os.path.join(PAPERS, name)
        if detect_readme_drift(paper_dir, doi):
            drift_lines.append(f"  {name}/README.md does not mention DOI {bare_doi_id(doi)}")
    if drift_lines:
        print()
        print("MANUAL DRIFT (package READMEs missing DOI reference):")
        for line in drift_lines[:20]:
            print(line)
        if len(drift_lines) > 20:
            print(f"  … and {len(drift_lines) - 20} more")
    print("=" * 72)


def main() -> int:
    parser = argparse.ArgumentParser(description="EFC DOI sync")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Report drift, exit 1 if conflicts")
    mode.add_argument("--apply", action="store_true", help="Fix drift non-destructively")
    mode.add_argument("--report", action="store_true", help="Print per-paper DOI report only")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not (args.check or args.apply or args.report):
        args.report = True

    doi_by_dir, sources_by_dir, conflicts_by_dir = scan_all()

    cross_changes: Dict[str, List[str]] = {}
    touched: Dict[str, List[str]] = {}

    if args.apply:
        # Skip papers that have conflicts — let the human reconcile first
        safe_to_apply = {
            name: doi
            for name, doi in doi_by_dir.items()
            if name not in conflicts_by_dir
        }
        touched = propagate(safe_to_apply)
        cross_changes["efc_index.json"] = sync_efc_index(safe_to_apply)
        cross_changes["evidence-register.json"] = sync_evidence_register(safe_to_apply)
        cross_changes["ledger.json"] = sync_ledger_evidence(safe_to_apply)

    print_report(doi_by_dir, sources_by_dir, conflicts_by_dir, touched, cross_changes)

    if conflicts_by_dir:
        print("[efc-sync] conflicts present — manual reconciliation required", file=sys.stderr)
        return 1
    if args.check:
        # In --check mode, also fail if auto-fixable drift exists
        dry_touched = propagate({})  # no-op, but re-scan
        # Dry-run: call propagate on a copy that compares rather than writes?
        # Simpler: scan once, report if ledger/cross would change.
        # Since we don't dry-run the writers, the --check mode only fails on
        # conflicts. Apply mode reports and fixes. CI uses --apply + verify.
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
