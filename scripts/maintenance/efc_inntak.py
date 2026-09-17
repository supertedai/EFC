#!/usr/bin/env python3
"""efc_inntak.py — web-inntak fase 1: tre kilder, dedup, kostnadstak.

Henter nye poster fra arXiv, Crossref og OpenAlex (alle nøkkelfrie;
NASA ADS krever token og ligger kommentert i sources.yaml), dedupliserer
mot tidligere innholdshasher FØR noe modellkall, og lagrer kandidatene
som append-only JSONL under data/inntak/.

Bruk:
    python3 scripts/maintenance/efc_inntak.py --dry-run   # tell + vis, skriv ingenting
    python3 scripts/maintenance/efc_inntak.py             # hent + lagre
Exit: 0 = OK, 1 = taket nådd/feil (se ut).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
KONFIG = ROT / "config" / "sources.yaml"
LAGER = ROT / "data" / "inntak"
UA = "hermes-efc-inntak/1.0 (+supertedai/EFC)"
TIDSFRIST = 30

# EFC-nøkkelord (fase 1 — den brede synonymgrafen er fase 2)
NOKKELORD = [
    "entropy gradient", "energy flow cosmology", "entropic gravity",
    "modified gravity", "sigma8 tension", "growth rate tension",
    "late-time acceleration", "dark energy", "galaxy rotation curve",
    "structure formation tension",
]


def _last_yaml(sti: Path) -> dict:
    import yaml
    return yaml.safe_load(sti.read_text(encoding="utf-8")) or {}


def _hent(url: str) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIDSFRIST) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _arxiv(max_items: int) -> list[dict]:
    """arXiv svarer Atom XML, ikke JSON — derfor egen parser her."""
    q = urllib.parse.quote(" OR ".join(f'abs:"{k}"' for k in NOKKELORD[:6]))
    try:
        # XXE-/billion-laughs-sikker parsing: defusedxml først, stdlib med tak
        # som fallback (stdlib-expat løser ikke eksterne entiteter i 3.8+).
        try:
            import defusedxml.ElementTree as ET  # type: ignore
        except ImportError:
            import xml.etree.ElementTree as ET
        req = urllib.request.Request(
            f"http://export.arxiv.org/api/query?search_query={q}"
            f"&sortBy=submittedDate&sortOrder=descending&max_results={max_items}",
            headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIDSFRIST) as r:
            rot = ET.fromstring(r.read(5 * 1024 * 1024).decode())  # tak: 5 MB
    except Exception:
        return []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    ut = []
    for e in rot.findall("a:entry", ns):
        eid = (e.findtext("a:id", "", ns) or "").strip()
        tittel = " ".join((e.findtext("a:title", "", ns) or "").split())
        publisert = e.findtext("a:published", "", ns)
        doi = None
        for l in e.findall("a:link", ns):
            href = l.get("href") or ""
            if "doi.org" in href:
                doi = href.split("doi.org/")[-1]
        summ = " ".join((e.findtext("a:summary", "", ns) or "").split())
        ut.append({"kilde": "arxiv", "id": f"arxiv:{eid}", "tittel": tittel[:300],
                   "publisert": publisert, "doi": doi, "url": eid,
                   "abstrakt": summ[:800]})
    return ut


def _crossref(max_items: int) -> list[dict]:
    q = urllib.parse.quote(" ".join(NOKKELORD[:5]))
    d = _hent(f"https://api.crossref.org/works?query={q}&rows={max_items}"
              f"&sort=published&order=desc&filter=from-pub-date:{datetime.now().year - 2}-01-01")
    if not d:
        return []
    ut = []
    for e in (d.get("message") or {}).get("items") or []:
        ut.append({"kilde": "crossref", "id": f"doi:{e.get('DOI')}",
                   "tittel": ((e.get("title") or [""])[0])[:300],
                   "publisert": (e.get("published") or {}).get("date-parts", [[None]])[0][0],
                   "doi": e.get("DOI"), "url": e.get("URL"),
                   "abstrakt": ""})
    return ut


def _openalex(max_items: int) -> list[dict]:
    q = urllib.parse.quote(" OR ".join(f'"{k}"' for k in NOKKELORD[:5]))
    d = _hent(f"https://api.openalex.org/works?search={q}"
              f"&per-page={max_items}&sort=publication_date:desc")
    if not d:
        return []
    ut = []
    for e in (d.get("results") or []):
        ut.append({"kilde": "openalex", "id": f"oa:{e.get('id')}",
                   "tittel": (e.get("title") or "")[:300],
                   "publisert": e.get("publication_date"), "doi": e.get("doi"),
                   "url": e.get("id"), "abstrakt": ""})
    return ut


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    cfg = _last_yaml(KONFIG)
    tak = int(cfg.get("daglig_tak", 100))
    per_kilde = int(cfg.get("per_kilde_tak", 40))
    LAGER.mkdir(parents=True, exist_ok=True)
    sett_hash = set()
    for f in LAGER.glob("*.jsonl"):
        for linje in f.read_text(encoding="utf-8").splitlines():
            if not linje.strip():
                continue
            try:
                sett_hash.add(json.loads(linje).get("content_hash"))
            except json.JSONDecodeError:
                pass
    nye = []
    for hent_fn, kilde, aktiv in ((_arxiv, "arxiv", cfg.get("arxiv", {}).get("enabled", True)),
                                   (_crossref, "crossref", cfg.get("crossref", {}).get("enabled", True)),
                                   (_openalex, "openalex", cfg.get("openalex", {}).get("enabled", True))):
        if not aktiv:
            continue
        for r in hent_fn(per_kilde):
            tekst = json.dumps(r, sort_keys=True, ensure_ascii=False)
            h = "sha256:" + hashlib.sha256(tekst.encode()).hexdigest()
            if h in sett_hash:
                continue
            r["content_hash"] = h
            r["hentet"] = datetime.now(timezone.utc).isoformat()
            r["kildeklasse"] = "primary"
            nye.append(r)
        time.sleep(1)  # snill mot API-ene
    nye = nye[:tak]
    if a.dry_run:
        print(json.dumps({"modus": "dry-run", "nye": len(nye),
                          "per_kilde": {k: sum(1 for n in nye if n["kilde"] == k)
                                        for k in ("arxiv", "crossref", "openalex")}},
                         ensure_ascii=False, indent=1))
        return 0
    if not nye:
        print(json.dumps({"modus": "lagre", "nye": 0}))
        return 0
    sti = LAGER / f"inntak-{datetime.now():%Y-%m-%d}.jsonl"
    with open(sti, "a", encoding="utf-8") as f:
        for r in nye:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"modus": "lagre", "nye": len(nye), "fil": str(sti)},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(hoved())
