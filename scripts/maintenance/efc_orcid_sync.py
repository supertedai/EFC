#!/usr/bin/env python3
"""
EFC ORCID Sync — ORCID profile as DOI source-of-truth
======================================================

Author's ORCID record is the authoritative list of *what has been
published*. The repo is the authoritative list of *what is reproduced
and analysed*. This script compares the two on every maintenance pass
and reports any drift in three buckets:

  1. on_orcid_not_in_repo  — paper exists on ORCID but not in
                              docs/papers/efc/. Repo needs to download
                              + process the package.
  2. in_repo_not_on_orcid  — DOI exists in repo but not on ORCID.
                              Either the ORCID record is stale, or
                              the repo holds a draft/unregistered DOI.
  3. matched               — DOI present on both sides. No action.

Behaviour
---------
* Live mode (default): fetch ORCID public works API. Cache the raw
  response in .claude/orcid_cache.json (24h TTL).
* Cached mode: if --use-cache or network is unreachable, read from
  the cache and proceed.
* --apply does NOT auto-download papers (requires Figshare API key
  + PDF processing). It only updates the report and stamps the
  source-of-truth status into .claude/.

Output
------
.claude/orcid_sync_report.json:
  {
    "checked_at": "2026-05-02T...",
    "orcid_id": "0009-0002-4860-5095",
    "source": "live" | "cache" | "offline",
    "orcid_works_count": N,
    "orcid_dois": [...],
    "repo_dois": [...],
    "matched": [...],
    "on_orcid_not_in_repo": [...],   # action: download + process
    "in_repo_not_on_orcid": [...],   # action: register on ORCID
  }

Exit codes
----------
  0  — clean (perfect match, or only matched + cache fallback)
  1  — drift detected (one or both bucket non-empty)
  2  — fatal error (offline + no cache)
"""
from __future__ import annotations
import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
CLAUDE_DIR = os.path.join(REPO, ".claude")
CACHE_PATH = os.path.join(CLAUDE_DIR, "orcid_cache.json")
REPORT_PATH = os.path.join(CLAUDE_DIR, "orcid_sync_report.json")

ORCID_ID_DEFAULT = "0009-0002-4860-5095"
ORCID_API_BASE = "https://pub.orcid.org/v3.0"
CACHE_TTL_SECONDS = 24 * 3600
HTTP_TIMEOUT = 15

FIGSHARE_DOI_RE = re.compile(r"10\.6084/m9\.figshare\.(\d{7,9})")
SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}


def _http_get_json(url: str, timeout: int = HTTP_TIMEOUT):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "EFC-ORCID-Sync/1.0 (+https://github.com/supertedai/EFC)",
        },
    )
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _reports_equivalent(prev, curr):
    """True if two reports differ only in volatile fields (checked_at)."""
    if not isinstance(prev, dict) or not isinstance(curr, dict):
        return False
    volatile = {"checked_at"}
    a = {k: v for k, v in prev.items() if k not in volatile}
    b = {k: v for k, v in curr.items() if k not in volatile}
    return a == b


def _bare(doi):
    if not doi:
        return None
    m = FIGSHARE_DOI_RE.search(str(doi))
    return m.group(1) if m else None


def fetch_orcid_works(orcid_id: str, use_cache: bool = False):
    """Return (works_list, source) where source ∈ {live, cache, offline}."""
    cached = _load_json(CACHE_PATH)
    cache_fresh = False
    if cached and isinstance(cached, dict):
        ts = cached.get("fetched_at_epoch", 0)
        if time.time() - ts < CACHE_TTL_SECONDS:
            cache_fresh = True

    if use_cache and cached:
        return cached.get("works", []), "cache"

    if cache_fresh and not use_cache:
        # Still hit network if cache is fresh? No — fresh cache short-circuits.
        return cached.get("works", []), "cache"

    try:
        summary = _http_get_json(f"{ORCID_API_BASE}/{orcid_id}/works")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ssl.SSLError) as exc:
        if cached:
            print(
                f"[efc-orcid] network unreachable ({type(exc).__name__}); "
                f"falling back to cache from "
                f"{datetime.fromtimestamp(cached.get('fetched_at_epoch', 0), tz=timezone.utc).isoformat()}"
            )
            return cached.get("works", []), "cache"
        print(f"[efc-orcid] network unreachable ({type(exc).__name__}) and no cache available")
        return [], "offline"

    works = []
    groups = summary.get("group", []) if isinstance(summary, dict) else []
    for grp in groups:
        external_ids = []
        for eid in (grp.get("external-ids", {}) or {}).get("external-id", []) or []:
            etype = (eid.get("external-id-type") or "").lower()
            evalue = eid.get("external-id-value") or ""
            if etype == "doi":
                external_ids.append(evalue.strip())
        # Title and put-code from work-summary
        summaries = grp.get("work-summary", []) or []
        title = ""
        put_code = None
        publication_year = None
        work_type = ""
        for s in summaries:
            t = ((s.get("title") or {}).get("title") or {}).get("value") or ""
            if t and not title:
                title = t
            if put_code is None:
                put_code = s.get("put-code")
            py = ((s.get("publication-date") or {}).get("year") or {}).get("value")
            if py and not publication_year:
                publication_year = py
            if not work_type:
                work_type = s.get("type") or ""
        works.append({
            "title": title,
            "put_code": put_code,
            "publication_year": publication_year,
            "type": work_type,
            "dois": external_ids,
        })

    payload = {
        "orcid_id": orcid_id,
        "fetched_at_epoch": int(time.time()),
        "fetched_at_iso": datetime.now(timezone.utc).isoformat(),
        "works_count": len(works),
        "works": works,
    }
    _save_json(CACHE_PATH, payload)
    return works, "live"


def collect_repo_dois():
    """Return dict {bare_doi: paper_directory}."""
    out = {}
    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        p = os.path.join(PAPERS, name)
        if not os.path.isdir(p):
            continue
        idx = _load_json(os.path.join(p, "index.json")) or {}
        bare = _bare(idx.get("doi"))
        if bare:
            out[bare] = name
    return out


def main():
    parser = argparse.ArgumentParser(description="EFC ORCID source-of-truth sync")
    parser.add_argument("--orcid-id", default=ORCID_ID_DEFAULT)
    parser.add_argument("--use-cache", action="store_true",
                        help="Read from .claude/orcid_cache.json without hitting network")
    parser.add_argument("--apply", action="store_true",
                        help="Reserved for future auto-download; currently a no-op")
    args = parser.parse_args()

    works, source = fetch_orcid_works(args.orcid_id, use_cache=args.use_cache)

    orcid_dois = set()
    orcid_doi_to_title = {}
    for w in works:
        for doi in w.get("dois", []):
            bare = _bare(doi)
            if bare:
                orcid_dois.add(bare)
                if bare not in orcid_doi_to_title:
                    orcid_doi_to_title[bare] = w.get("title") or ""

    repo_dois = collect_repo_dois()
    repo_doi_set = set(repo_dois.keys())

    matched = sorted(orcid_dois & repo_doi_set)
    on_orcid_not_in_repo = sorted(orcid_dois - repo_doi_set)
    in_repo_not_on_orcid = sorted(repo_doi_set - orcid_dois)

    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "orcid_id": args.orcid_id,
        "source": source,
        "orcid_works_count": len(works),
        "orcid_dois_count": len(orcid_dois),
        "repo_dois_count": len(repo_dois),
        "matched_count": len(matched),
        "on_orcid_not_in_repo_count": len(on_orcid_not_in_repo),
        "in_repo_not_on_orcid_count": len(in_repo_not_on_orcid),
        "matched": matched,
        "on_orcid_not_in_repo": [
            {"doi": b, "title": orcid_doi_to_title.get(b, "")}
            for b in on_orcid_not_in_repo
        ],
        "in_repo_not_on_orcid": [
            {"doi": b, "directory": repo_dois.get(b, "")}
            for b in in_repo_not_on_orcid
        ],
    }
    # Only rewrite the report if something meaningful changed. Otherwise the
    # rolling `checked_at` timestamp produces a noise diff on every run and
    # spams git history with empty SessionStart commits.
    previous = _load_json(REPORT_PATH)
    if not _reports_equivalent(previous, report):
        _save_json(REPORT_PATH, report)

    print("=" * 72)
    print(f"EFC ORCID source-of-truth sync — source={source}")
    print("=" * 72)
    print(f"  ORCID works               : {len(works)}")
    print(f"  ORCID Figshare DOIs       : {len(orcid_dois)}")
    print(f"  Repo Figshare DOIs        : {len(repo_dois)}")
    print(f"  Matched                   : {len(matched)}")
    print(f"  On ORCID, not in repo     : {len(on_orcid_not_in_repo)}")
    print(f"  In repo, not on ORCID     : {len(in_repo_not_on_orcid)}")
    if on_orcid_not_in_repo:
        print()
        print("PAPERS ON ORCID, NOT IN REPO (action: download + process):")
        for b in on_orcid_not_in_repo[:20]:
            print(f"  - 10.6084/m9.figshare.{b}  {orcid_doi_to_title.get(b, '')[:80]}")
        if len(on_orcid_not_in_repo) > 20:
            print(f"  ... +{len(on_orcid_not_in_repo) - 20} more")
    if in_repo_not_on_orcid:
        print()
        print("DOIs IN REPO, NOT ON ORCID (action: register on ORCID or check draft status):")
        for b in in_repo_not_on_orcid[:20]:
            print(f"  - 10.6084/m9.figshare.{b}  {repo_dois.get(b, '')[:80]}")
        if len(in_repo_not_on_orcid) > 20:
            print(f"  ... +{len(in_repo_not_on_orcid) - 20} more")
    print("=" * 72)

    if source == "offline":
        return 2
    if on_orcid_not_in_repo or in_repo_not_on_orcid:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
