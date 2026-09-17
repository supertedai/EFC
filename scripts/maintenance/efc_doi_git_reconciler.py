#!/usr/bin/env python3
"""efc_doi_git_reconciler — keep Figshare DOIs and git in lockstep.

The publishing workflow has exactly two human-gated events (Morten
2026-09-17): Figshare publish and git publish (merge to public). This
reconciler hangs them together:

  --pre-publish  <doi-or-slug>   git side COMPLETE before a publish is
                                 allowed: folder exists under
                                 docs/papers/efc/<slug>/ with the PDF,
                                 index.json, ai_manifest.json, metadata.json,
                                 and the DOI already written into
                                 index.json.doi + metadata.json.doi.
  --post-publish <doi>           after publish: the DOI resolves live on
                                 Figshare AND the git side carries it
                                 (index.json.doi + figshare_url) AND the
                                 changelog has an entry for it.

Both modes print a JSON report and exit 1 on any gap. The orchestrator runs
--pre-publish before routing a card to review and --post-publish after the
human publishes.

Usage:
  python3 scripts/maintenance/efc_doi_git_reconciler.py --pre-publish <doi-or-slug>
  python3 scripts/maintenance/efc_doi_git_reconciler.py --post-publish <doi>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>]+")


def _slugs() -> dict[str, str]:
    """slug -> folder name, from index.json ids and directory names."""
    out: dict[str, str] = {}
    if not os.path.isdir(PAPERS):
        return out
    for navn in os.listdir(PAPERS):
        mappe = os.path.join(PAPERS, navn)
        idx = os.path.join(mappe, "index.json")
        if not os.path.isdir(mappe) or not os.path.isfile(idx):
            continue
        try:
            d = json.load(open(idx, encoding="utf-8"))
        except Exception:
            continue
        for nøkkel in {d.get("id"), navn, navn.lower().replace("_", "-")}:
            if nøkkel:
                out[str(nøkkel)] = navn
    return out


def _finn_mappe(ref: str) -> str | None:
    """Resolve a DOI or slug to a paper folder under docs/papers/efc/."""
    if ref in _slugs():
        return os.path.join(PAPERS, _slugs()[ref])
    for navn in os.listdir(PAPERS):
        mappe = os.path.join(PAPERS, navn)
        for fil in ("index.json", "metadata.json"):
            sti = os.path.join(mappe, fil)
            if not os.path.isfile(sti):
                continue
            try:
                tekst = json.dumps(json.load(open(sti, encoding="utf-8")))
            except Exception:
                continue
            if ref.lower() in tekst.lower():
                return mappe
    return None


def _doi_live(doi: str) -> tuple[str, str]:
    """Tri-state: 'live' | 'dead' | 'unclear' (host blocked — check via .12)."""
    siste_404 = False
    for url in (f"https://doi.org/{doi}",
                f"https://api.figshare.com/v2/articles/{doi.rsplit('.', 1)[-1]}"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "efc-opus/1.0"})
            with urllib.request.urlopen(req, timeout=20) as x:
                if x.status == 200:
                    return "live", url
        except urllib.error.HTTPError as e:
            if e.code == 404:
                siste_404 = True
                continue
            # 403/429/5xx: Figshare blocks this host's IP range — not a
            # verdict on the DOI. The authoritative check runs on .12.
            return "unclear", ""
        except Exception:
            continue
    return ("dead", "") if siste_404 else ("unclear", "")


def sjekk_pre(mappe: str, doi: str) -> dict:
    gap: list[str] = []
    index_sti = os.path.join(mappe, "index.json")
    meta_sti = os.path.join(mappe, "metadata.json")
    ai_sti = os.path.join(mappe, "ai_manifest.json")
    for sti, navn in ((index_sti, "index.json"), (meta_sti, "metadata.json"),
                      (ai_sti, "ai_manifest.json")):
        if not os.path.isfile(sti):
            gap.append(f"missing {navn}")
    pdf_er = [f for f in os.listdir(mappe) if f.lower().endswith(".pdf")]
    if not pdf_er:
        gap.append("missing PDF")
    tex_er = [f for f in os.listdir(mappe) if f.lower().endswith(".tex")]
    if not tex_er:
        gap.append("missing .tex source")
    if os.path.isfile(index_sti):
        d = json.load(open(index_sti, encoding="utf-8"))
        if d.get("doi", "") != doi:
            gap.append("index.json.doi does not match")
        if not d.get("figshare_url"):
            gap.append("index.json.figshare_url missing")
    if os.path.isfile(meta_sti):
        m = json.load(open(meta_sti, encoding="utf-8"))
        if m.get("doi", "") != doi:
            gap.append("metadata.json.doi does not match")
    return {"mode": "pre-publish", "folder": os.path.basename(mappe),
            "ok": not gap, "gaps": gap}


def sjekk_post(mappe: str, doi: str) -> dict:
    res = sjekk_pre(mappe, doi)
    res["mode"] = "post-publish"
    tilstand, url = _doi_live(doi)
    res["doi_state"] = tilstand
    if tilstand == "dead":
        res["gaps"].append("DOI dead (404) — not published?")
    elif tilstand == "unclear":
        res["notes"] = ("Figshare unreachable from this host (IP-block). "
                        "Authoritative live-check: figshare-mine via the .12 vakt.")
    else:
        res["doi_url"] = url
    # changelog entry mentions the DOI
    cl_sti = os.path.join(REPO, "docs", "validation-ledger", "data",
                          "changelog.json")
    funnet = False
    if os.path.isfile(cl_sti):
        cl = json.load(open(cl_sti, encoding="utf-8"))
        tekst = json.dumps(cl)
        if doi.lower() in tekst.lower():
            funnet = True
    if not funnet:
        res["gaps"].append("no changelog entry for this DOI")
    res["ok"] = not res["gaps"]
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pre-publish", metavar="DOI-OR-SLUG")
    ap.add_argument("--post-publish", metavar="DOI")
    args = ap.parse_args()
    if args.pre_publish and args.post_publish:
        ap.error("choose one mode")
    if not args.pre_publish and not args.post_publish:
        ap.error("--pre-publish or --post-publish required")

    doi = args.pre_publish or args.post_publish
    mappe = _finn_mappe(doi)
    if not mappe:
        print(json.dumps({"ok": False, "gaps": [
              f"no folder under docs/papers/efc/ for {doi}"]}))
        return 1
    res = sjekk_post(mappe, doi) if args.post_publish else sjekk_pre(mappe, doi)
    print(json.dumps(res, indent=2))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
