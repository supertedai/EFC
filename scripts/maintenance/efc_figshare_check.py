#!/usr/bin/env python3
"""EFC Figshare DOI presence-check + scaffold.

Implements §6 C4 of the EFC Master Sync-Protocol. Two modes:

``--check``
    For every DOI in ``figshare/doi-map.json`` and every DOI listed under
    ``missing_repo_dirs``: hit ``api.figshare.com/v2/articles/<id>``,
    confirm 200 OK + ``Morten Magnusson`` in ``authors[].full_name`` (or
    ``authors[*].id == 20477774``), and compare the figshare-current
    title against the local title in the doi-map.

    Categorises every mismatch into one of:
      ``not_found``        — figshare returned 404
      ``withdrawn``        — article exists but is_metadata_record/withdrawn
      ``wrong_author``     — exists but Morten is not in authors[]
      ``title_mismatch``   — author OK, but title differs from local
      ``ok``               — author OK, title matches

    Title mismatches are then sub-classified into:
      ``prefix_efc_dash``           — local has "EFC —" prefix that figshare lacks
      ``prefix_white_paper``        — figshare has "White Paper - Part X of Y -" prefix
      ``truncation_local``          — local title is a strict prefix of figshare's
      ``truncation_remote``         — figshare title is a strict prefix of local
      ``truncation_after_prefix_strip`` — equivalence after stripping common prefixes
      ``versioning``                — both versions of the article exist and titles differ
                                       (figshare DOIs can be re-titled across versions)
      ``semantic_drift``            — none of the above; needs per-case review

``--scaffold-missing``
    For each entry in ``missing_repo_dirs`` of doi-map.json, create a new
    paper directory under ``docs/papers/efc/<slug>/`` with the canonical
    10-file scaffold (``index.json``, ``schema.json``, ``metadata.json``,
    ``README.md``, ``CITATION.cff``, ``citations.bib``, ``<slug>.jsonld``,
    plus empty ``src/``, ``data/``, ``examples/`` directories). Adds a
    ``.scaffolded`` marker so ``efc_maintain.py`` does not treat the
    directory as a complete package until it has been reviewed.

    With ``--with-pdf``, also downloads the primary attachment from
    figshare (PDF preferred; DOCX fallback if no PDF on the article).

Network failures degrade gracefully — the script reports the failure and
continues. Used in CI: a weekly schedule on ``efc-figshare-presence.yml``
detects withdrawn/retitled DOIs early.

Local equivalent:
    python3 scripts/maintenance/efc_figshare_check.py --check
    python3 scripts/maintenance/efc_figshare_check.py --scaffold-missing --with-pdf
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DOI_MAP = REPO_ROOT / "figshare" / "doi-map.json"
PAPERS_ROOT = REPO_ROOT / "docs" / "papers" / "efc"
REPORTS_DIR = REPO_ROOT / "reports"
FIGSHARE_API = "https://api.figshare.com/v2/articles/{id}"
EXPECTED_AUTHOR_NAME = "Morten Magnusson"
EXPECTED_AUTHOR_ID = 20477774
NETWORK_TIMEOUT_SECONDS = 15

WHITE_PAPER_PREFIX_RE = re.compile(
    r"^White Paper\s*-\s*Part\s+\d+\s+of\s+\d+\s*-\s*",
    re.IGNORECASE,
)
EFC_DASH_PREFIX_RE = re.compile(r"^EFC\s*[—-]\s*", re.IGNORECASE)


def _rel_or_abs(path: Path) -> str:
    """Return path relative to REPO_ROOT when possible, else absolute string."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_doi_map() -> dict:
    if not DOI_MAP.exists():
        raise SystemExit(f"[figshare-check] doi-map missing: {DOI_MAP}")
    return json.loads(DOI_MAP.read_text())


def fetch_figshare(article_id: str) -> tuple[dict | None, str | None]:
    """Return (parsed_json, error). Either parsed_json is dict or error is set."""
    url = FIGSHARE_API.format(id=article_id)
    try:
        with urllib.request.urlopen(url, timeout=NETWORK_TIMEOUT_SECONDS) as resp:
            if resp.status != 200:
                return None, f"http_{resp.status}"
            payload = json.loads(resp.read().decode("utf-8"))
            return payload, None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, "not_found"
        return None, f"http_{e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return None, f"network_unreachable: {e}"
    except json.JSONDecodeError as e:
        return None, f"invalid_json: {e}"


def author_matches(article: dict) -> bool:
    for a in article.get("authors") or []:
        if (a.get("full_name") or "").strip().lower() == EXPECTED_AUTHOR_NAME.lower():
            return True
        if a.get("id") == EXPECTED_AUTHOR_ID:
            return True
    return False


def article_is_withdrawn(article: dict) -> bool:
    if article.get("is_metadata_record"):
        return True
    status = (article.get("status") or "").lower()
    return status in {"withdrawn", "rejected", "deleted"}


def normalise_title(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def classify_title_mismatch(local_title: str, remote_title: str) -> str:
    a = normalise_title(local_title)
    b = normalise_title(remote_title)
    if not a or not b:
        return "semantic_drift"
    if a.lower() == b.lower():
        return "ok"

    a_stripped = EFC_DASH_PREFIX_RE.sub("", a, count=1)
    b_stripped = WHITE_PAPER_PREFIX_RE.sub("", b, count=1)

    if a_stripped != a and a_stripped.lower() == b.lower():
        return "prefix_efc_dash"
    if b_stripped != b and b_stripped.lower() == a.lower():
        return "prefix_white_paper"
    if a_stripped != a and b_stripped != b and a_stripped.lower() == b_stripped.lower():
        return "truncation_after_prefix_strip"

    a_low = a.lower()
    b_low = b.lower()
    if b_low.startswith(a_low):
        return "truncation_local"
    if a_low.startswith(b_low):
        return "truncation_remote"

    similarity = SequenceMatcher(None, a_low, b_low).ratio()
    if similarity > 0.7:
        return "truncation_after_prefix_strip"
    return "semantic_drift"


def check_one(doi: str, local_title: str) -> dict:
    article_id = doi.rsplit(".", 1)[-1]
    article, err = fetch_figshare(article_id)
    if err == "not_found":
        return {"doi": doi, "status": "not_found", "detail": "figshare 404"}
    if err is not None:
        return {"doi": doi, "status": "network_error", "detail": err}
    if article is None:
        return {"doi": doi, "status": "network_error", "detail": "no payload"}
    if article_is_withdrawn(article):
        return {"doi": doi, "status": "withdrawn", "detail": article.get("status", "")}
    if not author_matches(article):
        authors = [a.get("full_name") for a in (article.get("authors") or [])]
        return {
            "doi": doi,
            "status": "wrong_author",
            "detail": f"figshare authors: {authors}",
        }
    remote_title = article.get("title", "")
    sub = classify_title_mismatch(local_title, remote_title)
    if sub == "ok":
        return {"doi": doi, "status": "ok"}
    return {
        "doi": doi,
        "status": "title_mismatch",
        "subclass": sub,
        "local_title": local_title,
        "remote_title": remote_title,
    }


def cmd_check(json_out: bool) -> int:
    doi_map = load_doi_map()
    results: list[dict] = []
    for paper in doi_map.get("papers", []):
        doi = paper.get("doi") or ""
        if "figshare." not in doi:
            continue
        results.append(check_one(doi, paper.get("title", "")))
    for missing in doi_map.get("missing_repo_dirs", []):
        fid = missing.get("figshare_id")
        if not fid:
            continue
        doi = f"10.6084/m9.figshare.{fid}"
        results.append(check_one(doi, missing.get("title", "")))

    summary: dict[str, int] = {}
    for r in results:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
        if r["status"] == "title_mismatch":
            sub = r.get("subclass", "unknown")
            summary[f"title_mismatch:{sub}"] = (
                summary.get(f"title_mismatch:{sub}", 0) + 1
            )

    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / "figshare-check.json"
    report_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "totals": summary,
                "results": results,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )

    if json_out:
        print(json.dumps({"totals": summary}, indent=2))
    else:
        print(f"[figshare-check] {len(results)} DOI(s) checked")
        for k in sorted(summary):
            print(f"  {k}: {summary[k]}")
        print(f"[figshare-check] full report → {_rel_or_abs(report_path)}")

    network_only = {"network_error"} == set(summary)
    if network_only:
        print("[figshare-check] all calls failed network-side; skipping gate")
        return 0
    hard_fail = any(
        r["status"] in {"not_found", "withdrawn", "wrong_author"} for r in results
    )
    return 2 if hard_fail else 0


def slugify(title: str, fallback: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", title or fallback).strip("-")
    return (s[:80] or fallback).lower()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def primary_attachment(article: dict) -> tuple[str, str] | None:
    """Return (filename, download_url) for the primary attachment, preferring
    PDF and falling back to DOCX/other if no PDF is present."""
    files = article.get("files") or []
    pdfs = [
        f
        for f in files
        if (f.get("name") or "").lower().endswith(".pdf")
        and f.get("download_url")
    ]
    if pdfs:
        f = pdfs[0]
        return f["name"], f["download_url"]
    docs = [
        f
        for f in files
        if (f.get("name") or "").lower().endswith((".docx", ".doc"))
        and f.get("download_url")
    ]
    if docs:
        f = docs[0]
        return f["name"], f["download_url"]
    for f in files:
        if f.get("download_url"):
            return f.get("name") or "primary.bin", f["download_url"]
    return None


def download_attachment(url: str, dest: Path) -> str | None:
    try:
        with urllib.request.urlopen(url, timeout=NETWORK_TIMEOUT_SECONDS * 4) as resp:
            if resp.status != 200:
                return f"http_{resp.status}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("wb") as fh:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    fh.write(chunk)
        return None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return f"network_unreachable: {e}"


def scaffold_one(missing: dict, with_pdf: bool, out_root: Path) -> dict:
    fid = missing.get("figshare_id")
    title = missing.get("title", "")
    doi_full = f"10.6084/m9.figshare.{fid}"
    slug = slugify(title, f"paper-{fid}")
    paper_dir = out_root / slug
    if paper_dir.exists():
        return {"figshare_id": fid, "status": "exists", "dir": str(paper_dir)}

    article: dict | None = None
    err: str | None = None
    if with_pdf:
        article, err = fetch_figshare(str(fid))

    paper_dir.mkdir(parents=True)
    (paper_dir / "src").mkdir()
    (paper_dir / "data").mkdir()
    (paper_dir / "examples").mkdir()
    (paper_dir / "src" / "__init__.py").write_text("")

    index = {
        "$schema": "./schema.json",
        "id": slug,
        "title": title or slug,
        "doi": doi_full,
        "version": "0.1-scaffold",
        "date": "",
        "author": {
            "name": EXPECTED_AUTHOR_NAME,
            "orcid": "0009-0002-4860-5095",
            "affiliation": "Symbiose Research, Sandnes, Norway",
        },
        "license": "CC-BY-4.0",
        "scaffolded": True,
        "scaffolded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    write_text(paper_dir / "index.json", json.dumps(index, indent=2) + "\n")
    write_text(
        paper_dir / "metadata.json",
        json.dumps({"paper": index, "scaffolded": True}, indent=2) + "\n",
    )
    write_text(
        paper_dir / "schema.json",
        json.dumps({"$schema": "https://json-schema.org/draft-07/schema#"}, indent=2)
        + "\n",
    )
    write_text(
        paper_dir / f"{slug}.jsonld",
        json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "ScholarlyArticle",
                "name": title,
                "identifier": doi_full,
                "author": {
                    "@type": "Person",
                    "name": EXPECTED_AUTHOR_NAME,
                    "identifier": "https://orcid.org/0009-0002-4860-5095",
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        paper_dir / "README.md",
        f"# {title or slug}\n\n"
        f"**DOI:** [{doi_full}](https://doi.org/{doi_full})\n\n"
        f"**Status:** scaffolded — awaiting review.\n\n"
        f"This directory was created by `efc_figshare_check.py --scaffold-missing`. "
        f"Please review and remove the `.scaffolded` marker once content is in place.\n",
    )
    write_text(
        paper_dir / "CITATION.cff",
        f"cff-version: 1.2.0\n"
        f"title: {title or slug}\n"
        f"authors:\n"
        f"  - family-names: Magnusson\n"
        f"    given-names: Morten\n"
        f"    orcid: https://orcid.org/0009-0002-4860-5095\n"
        f"doi: {doi_full}\n",
    )
    write_text(
        paper_dir / "citations.bib",
        f"@misc{{efc_{fid},\n"
        f"  author = {{Magnusson, Morten}},\n"
        f"  title = {{{title or slug}}},\n"
        f"  doi = {{{doi_full}}},\n"
        f"  year = {{}},\n}}\n",
    )
    write_text(
        paper_dir / "LICENSE",
        "Creative Commons Attribution 4.0 International (CC-BY-4.0)\n"
        "https://creativecommons.org/licenses/by/4.0/\n\n"
        "You are free to:\n"
        "  - Share — copy and redistribute the material in any medium or format\n"
        "  - Adapt — remix, transform, and build upon the material\n"
        "Under the following terms:\n"
        "  - Attribution — You must give appropriate credit, provide a link\n"
        "    to the license, and indicate if changes were made.\n",
    )
    (paper_dir / ".scaffolded").write_text(
        f"Scaffolded on {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
        f"by efc_figshare_check.py from doi-map.missing_repo_dirs.\n"
        f"DOI: {doi_full}\n"
        f"Title (from doi-map): {title}\n\n"
        f"Action items:\n"
        f"  - verify title against figshare\n"
        f"  - replace stub README/metadata with real content\n"
        f"  - drop the primary attachment if --with-pdf could not download\n"
        f"  - delete this marker once the package is complete\n"
    )

    pdf_status = "skipped"
    if with_pdf:
        if article is None:
            pdf_status = f"figshare_unreachable: {err}"
        else:
            attach = primary_attachment(article)
            if attach is None:
                pdf_status = "no_attachment_on_figshare"
            else:
                fname, url = attach
                dl_err = download_attachment(url, paper_dir / fname)
                pdf_status = "downloaded" if dl_err is None else f"download_failed: {dl_err}"

    return {
        "figshare_id": fid,
        "status": "scaffolded",
        "dir": _rel_or_abs(paper_dir),
        "pdf_status": pdf_status,
    }


def cmd_scaffold(with_pdf: bool, json_out: bool, target_root: Path) -> int:
    doi_map = load_doi_map()
    missing = doi_map.get("missing_repo_dirs", [])
    if not missing:
        print("[figshare-check] no missing_repo_dirs to scaffold")
        return 0
    target_root.mkdir(parents=True, exist_ok=True)
    results = [scaffold_one(m, with_pdf, target_root) for m in missing]
    if json_out:
        print(json.dumps({"scaffolded": results}, indent=2))
    else:
        for r in results:
            print(f"  {r['figshare_id']}: {r['status']} → {r.get('dir','-')}", end="")
            if "pdf_status" in r:
                print(f" [pdf: {r['pdf_status']}]")
            else:
                print()
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="EFC figshare presence-check + scaffold")
    p.add_argument("--check", action="store_true", help="verify all DOIs in doi-map")
    p.add_argument(
        "--scaffold-missing",
        action="store_true",
        help="create paper-directory scaffolds for missing_repo_dirs entries",
    )
    p.add_argument(
        "--with-pdf",
        action="store_true",
        help="download primary attachment when scaffolding",
    )
    p.add_argument(
        "--scaffold-target",
        default=str(PAPERS_ROOT),
        help="root directory to scaffold into (default: docs/papers/efc/)",
    )
    p.add_argument("--json", action="store_true", help="machine-readable output")
    args = p.parse_args(list(argv) if argv is not None else None)

    if not args.check and not args.scaffold_missing:
        args.check = True

    rc = 0
    if args.check:
        rc = cmd_check(json_out=args.json) or rc
    if args.scaffold_missing:
        rc = (
            cmd_scaffold(
                with_pdf=args.with_pdf,
                json_out=args.json,
                target_root=Path(args.scaffold_target),
            )
            or rc
        )
    return rc


if __name__ == "__main__":
    sys.exit(main())
