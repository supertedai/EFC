#!/usr/bin/env python3
"""h4_min01_remaal — remåler tallene beslutningsnotatet bygger på.

Notatet: docs/notes/EFC_H4-MIN-01_fire_frys_beslutningsnotat_2026-09-18.md (§1).
Ingenting åpnes utover repoet; ingenting skrives. Kjøres fra repo-roten:

    python3 docs/notes/proposals/h4_min01_remaal.py

Tallene er en DATO, ikke en egenskap: de gjelder commiten skriptet leser, og
atlaset flytter seg (H4 målte 82 noder, notatet 89).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROT = pathlib.Path(__file__).resolve().parents[3]
if not (ROT / "schema" / "regime_nodes.jsonld").exists():
    sys.exit(f"feil rot: {ROT}")

ATLAS = ROT / "schema/regime_nodes.jsonld"
PAKKER = sorted((ROT / "docs/papers/efc").glob("*/index.json"))
LEDGER = ROT / "docs/validation-ledger/data/tests.json"

# Termsettet er målt, ikke gjettet: H4 oppgir ikke sin egen regex, og dens
# «34 av 356» lot seg ikke reprodusere (§1 i notatet).
BREDT = r"blind|frys|frossen|frosset|freeze|frozen|forseglet|forsegling|sealed|seal\b"


def main() -> int:
    atlas_txt = ATLAS.read_text(encoding="utf-8")
    atlas = json.loads(atlas_txt)
    noder = atlas["nodes"]

    print("== atlaset ==")
    print(f"  noder                              : {len(noder)}")
    print(f"  noder med prediction               : {[n.get('id') for n in noder if 'prediction' in n]}")
    print(f"  noder med settlement               : {[n.get('id') for n in noder if 'settlement' in n]}")

    korpus_doi = set()
    pakker_med_pred = pakker_med_kc = 0
    pred_total = kc_total = 0
    sealed_pakker = []
    treff = {"holdout": 0, "bredt": 0, "pred_eller_kc": 0}
    for p in PAKKER:
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("doi"):
            korpus_doi.add(d["doi"])
        sp = d.get("sealed_predictions") or []
        kc = d.get("kill_criteria") or []
        pred_total += len(sp)
        kc_total += len(kc)
        pakker_med_pred += bool(sp)
        pakker_med_kc += bool(kc)
        if d.get("paper_type") == "sealed_prediction":
            sealed_pakker.append((d.get("doi"), p.parent.name))
        kctxt = json.dumps(kc, ensure_ascii=False).lower()
        for x in sp:
            b = json.dumps(x, ensure_ascii=False).lower()
            treff["holdout"] += bool(re.search("holdout", b))
            bredt = bool(re.search(BREDT, b))
            treff["bredt"] += bredt
            treff["pred_eller_kc"] += bredt or bool(re.search(BREDT, kctxt))

    print("\n== korpuset ==")
    print(f"  pakker med index.json              : {len(PAKKER)}")
    print(f"  pakker med sealed_predictions      : {pakker_med_pred}")
    print(f"  pakker med kill_criteria           : {pakker_med_kc}")
    print(f"  forseglede prediksjoner            : {pred_total}")
    print(f"  kill-kriterier                     : {kc_total}")
    print(f"  unike DOI-er                       : {len(korpus_doi)}")
    print(f"  paper_type=sealed_prediction       : {len(sealed_pakker)}")
    print(f"  korpus-DOI-er atlaset viser til    : {sum(1 for d in korpus_doi if d in atlas_txt)}")
    synlige = [d for d, _ in sealed_pakker if d in atlas_txt]
    print(f"  sealed-pakker synlige i atlaset    : {len(synlige)} av {len(sealed_pakker)}"
          f" ({', '.join(synlige) if synlige else 'ingen'})")

    print("\n== prediksjonsflatens termer (per prediksjon) ==")
    for k, v in treff.items():
        print(f"  {k:20s}: {v} av {pred_total}")
    print("  H4 oppga 34 av 356 — ikke reprodusert med noen av disse definisjonene")

    print("\n== validitetsledgeren ==")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    print(f"  total_count                        : {ledger.get('total_count')} (version {ledger.get('version')})")
    blob = json.dumps(ledger, ensure_ascii=False).lower()
    print("  termer:", {w: blob.count(w) for w in ["holdout", "sealed", "blind", "frozen"]})

    ge = [n for n in noder if n.get("id") == "efc.growth_engine"]
    if ge:
        pred = ge[0].get("prediction", {})
        print("\n== efc.growth_engine ==")
        print(f"  sealed_doi                         : {pred.get('sealed_doi')}")
        print(f"  sealing_sha256                     : {str(pred.get('sealing_sha256'))[:16]}…")
        print(f"  arbiter / arbiter_waiting_for      : {pred.get('arbiter')!r} / {pred.get('arbiter_waiting_for')!r}")
        print(f"  issued_at / valid_for              : {pred.get('issued_at')} / {pred.get('valid_for')}")
        print(f"  frys                               : {pred.get('freeze')}")
        print(f"  har settlement                     : {'settlement' in ge[0]}")
        print(f"  har korrigendum                    : {'korrigendum' in ge[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
