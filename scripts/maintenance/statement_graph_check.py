#!/usr/bin/env python3
"""statement_graph_check.py — fase 1-sjekker for EFC-statement-grafen.

Sjekker at public/graph/statements.yaml + evidence.yaml henger sammen:
unike ID-er, referensiell integritet, eier og status på alt, ingen
superseded som aktiv, evidens-pekere som finnes, og at appears_on-sider
finnes i page-meta. Orphan-statements (tom appears_on) er INFO-funn i
fase 1 — side-kartleggingen er en egen arbeidskø, ikke en feil.

Anker-sjekkene (stale_page-klassen) er HARDE:
  * en appears_on-oppføring med `anchor` MÅ finnes som
    data-statement-id="<anchor>" i den siden den peker på (anchor_missing);
  * en side som bærer et data-statement-id grafen ikke tilskriver den, er
    en selvmotsigelse (anchor_ghost);
  * en primærside uten anker er en uverifiserbar hovedkobling
    (primary_uten_anker).
En kobling UTEN anker er ikke verifisert; den listes i anchor_queue (INFO)
som arbeidskø, og gjøres hard ved å sette `anchor` når den er etterprøvd.

Bruk:
    python3 scripts/maintenance/statement_graph_check.py          # menneskelig rapport
    python3 scripts/maintenance/statement_graph_check.py --json   # maskinlesbar (CI)

Exit: 0 = ingen harde feil; 1 = harde feil; 2 = bruksfeil.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
GRAF = ROT / "public" / "graph"
META = ROT / "public" / "page-meta"

ID_FORMAT = re.compile(r"^(efc|ev)\.[a-z0-9]+\.[a-z0-9]+(\.[a-z0-9]+)?$")
STATUS_GYLDIG = {"active", "superseded", "withdrawn", "candidate", "falsified"}
NIVAA_GYLDIG = {"documented", "reconstruction", "partial_support",
                "pending_external_validation", "independent_support",
                "falsified", "superseded"}


def _last_yaml(sti: Path) -> dict:
    import yaml  # fraktes med repoets avhengigheter
    with open(sti, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return d if isinstance(d, dict) else {}


# ---------------------------------------------------------------------------
# Anker-mekanikken (stale_page-klassen)
# ---------------------------------------------------------------------------
# En påstand som grafen sier står på en offentlig side skal kunne VISES på den
# siden. Ankeret er et HTML-attributt — data-statement-id="<id>" — på det
# elementet som bærer påstanden. Uten det er appears_on en påstand om en side
# ingen kan etterprøve: fase-1-kartleggingen (2026-09-17) konkluderte med fire
# orphan-påstander som alle fantes på sidene, og med tre koblinger (efc.sparc.001)
# til sider som ikke bærer dem. Begge feilretningene fanges her.
ANCHOR_ATTR = re.compile(r'data-statement-id\s*=\s*"([^"]+)"')


def _side_sti(page_id: str, meta: dict) -> Path | None:
    """Path til siden bak page_id, eller None hvis den ikke finnes."""
    m = meta.get(page_id) or {}
    raa = str(m.get("path") or "").strip()
    if not raa:
        return None
    kandidat = raa.split(" ")[0].lstrip("/")   # «/docs/index.html — inngangssiden»
    for sti in (ROT / "docs" / "public" / kandidat, ROT / kandidat,
                ROT / "docs" / kandidat):
        if sti.is_file():
            return sti
    return None


def _ankere(sti: Path) -> set[str]:
    return set(ANCHOR_ATTR.findall(sti.read_text(encoding="utf-8", errors="replace")))


def sjekk() -> dict:
    funn: dict[str, list[dict]] = {
        "harde": [], "info": [],
        "orphan": [], "dangling_reference": [], "missing_owner": [],
        "unsupported_claim": [], "hidden_contradiction": [],
        "anchor_missing": [], "anchor_ghost": [], "anchor_queue": [],
    }
    if not GRAF.is_dir() or not META.is_dir():
        funn["harde"].append({"type": "missing_structure",
                              "msg": "public/graph/ eller public/page-meta/ mangler"})
        return funn
    st = _last_yaml(GRAF / "statements.yaml").get("statements", [])
    ev = _last_yaml(GRAF / "evidence.yaml").get("evidence", [])
    meta_sider = {p.stem for p in META.glob("*.yaml")}
    page_meta = {p.stem: (_last_yaml(p)) for p in META.glob("*.yaml")}
    side_ankere: dict[str, set[str]] = {}
    for pid in meta_sider:
        sti = _side_sti(pid, page_meta)
        side_ankere[pid] = _ankere(sti) if sti else set()
    st_ids: dict[str, dict] = {}
    ev_ids: dict[str, dict] = {}

    for s in st:
        sid = s.get("statement_id")
        if not isinstance(sid, str) or not ID_FORMAT.match(sid):
            funn["harde"].append({"type": "invalid_statement_id", "msg": f"ugyldig ID: {sid!r}"})
            continue
        if sid in st_ids:
            funn["harde"].append({"type": "duplicate_statement_id", "msg": f"duplikat: {sid}"})
        st_ids[sid] = s
        if not s.get("owner_role"):
            funn["missing_owner"].append({"id": sid})
        if s.get("status") not in STATUS_GYLDIG:
            funn["harde"].append({"type": "invalid_status", "id": sid, "status": s.get("status")})
        if s.get("epistemic_level") not in NIVAA_GYLDIG:
            funn["harde"].append({"type": "invalid_epistemic_level",
                                  "id": sid, "level": s.get("epistemic_level")})
        if s.get("status") == "superseded" and not s.get("supersedes"):
            pass  # superseded står for seg; ingenting å kreve
        if not s.get("appears_on"):
            funn["orphan"].append({"id": sid, "text": (s.get("text") or "")[:60]})
        else:
            for a in s["appears_on"]:
                pid = a.get("page_id")
                if pid not in meta_sider:
                    funn["dangling_reference"].append(
                        {"id": sid, "page": pid, "msg": "siden finnes ikke i page-meta"})
                    continue
                anker = a.get("anchor")
                if not anker:
                    funn["anchor_queue"].append(
                        {"id": sid, "page": pid, "role": a.get("role") or "cited",
                         "msg": "appears_on uten anchor — ikke verifisert mot sideteksten"})
                    if (a.get("role") or "") == "primary":
                        funn["harde"].append(
                            {"type": "primary_uten_anker", "id": sid, "page": pid,
                             "msg": "primærside må bære et verifiserbart anker"})
                    continue
                if anker not in side_ankere.get(pid, set()):
                    funn["anchor_missing"].append(
                        {"id": sid, "page": pid, "anchor": anker,
                         "msg": "siden inneholder ikke data-statement-id=\"%s\"" % anker})
        if s.get("status") == "active" and s.get("supersedes"):
            superseded_av = s["supersedes"]
            if isinstance(superseded_av, list):
                for g in superseded_av:
                    gammel = st_ids.get(g)
                    if gammel and gammel.get("status") == "active":
                        funn["hidden_contradiction"].append(
                            {"id": sid, "msg": f"{g} er superseded men fortsatt active"})
        ev_refs = s.get("supported_by") or []
        if not ev_refs and s.get("kind") not in ("model_definition", "hypothesis"):
            funn["unsupported_claim"].append(
                {"id": sid, "kind": s.get("kind"),
                 "msg": "empirisk/liknende påstand uten evidens eller hypotesestatus"})

    for e in ev:
        eid = e.get("evidence_id")
        if not isinstance(eid, str) or not ID_FORMAT.match(eid):
            funn["harde"].append({"type": "invalid_evidence_id", "msg": f"ugyldig: {eid!r}"})
            continue
        if eid in ev_ids:
            funn["harde"].append({"type": "duplicate_evidence_id", "msg": f"duplikat: {eid}"})
        ev_ids[eid] = e
        if e.get("type") == "external_source":
            lok = e.get("locator") or {}
            if not (lok.get("doi") or lok.get("url")):
                funn["harde"].append(
                    {"type": "external_source_uten_lenke", "id": eid,
                     "msg": "ekstern kilde må ha doi eller url i locator"})
        for ref in e.get("supports_scope", []):
            if ref not in st_ids:
                funn["dangling_reference"].append(
                    {"id": eid, "msg": f"evidensen støtter ukjent statement {ref}"})

    for s in st:
        for ref in (s.get("supported_by") or []):
            if ref not in ev_ids:
                funn["dangling_reference"].append(
                    {"id": s.get("statement_id"), "msg": f"ukjent evidens {ref}"})
        for ref in (s.get("contradicts") or []) + (s.get("supersedes") or []):
            if ref not in st_ids:
                funn["dangling_reference"].append(
                    {"id": s.get("statement_id"), "msg": f"ukjent statement {ref}"})

    # --- anker-ghost: en side bærer et anker grafen ikke tilskriver den ---
    krevd: set[tuple[str, str]] = set()
    for s in st:
        for a in (s.get("appears_on") or []):
            if a.get("page_id") and a.get("anchor"):
                krevd.add((a["page_id"], a["anchor"]))
    for pid, ankere in side_ankere.items():
        for anker in sorted(ankere):
            if (pid, anker) not in krevd:
                funn["anchor_ghost"].append(
                    {"page": pid, "anchor": anker,
                     "msg": "siden bærer et anker grafen ikke tilskriver den"})

    return funn


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    funn = sjekk()
    # Ankerbrudd er harde: en verifisert kobling som ikke holder, eller et anker
    # siden bærer uten at grafen tilskriver den påstanden.
    harde = (list(funn["harde"]) + list(funn["anchor_missing"])
             + list(funn["anchor_ghost"]))
    if a.json:
        funn["harde"] = harde
        print(json.dumps(funn, ensure_ascii=False, indent=1))
    else:
        print(f"statement-graf: {len(harde)} harde feil, "
              f"{len(funn['orphan'])} orphan (info), "
              f"{len(funn['dangling_reference'])} dangling, "
              f"{len(funn['missing_owner'])} uten eier, "
              f"{len(funn['unsupported_claim'])} uten støtte, "
              f"{len(funn['anchor_queue'])} i anker-kø (info)")
        for f in harde[:20]:
            print("  HARDT:", f)
        for f in (funn["dangling_reference"] + funn["missing_owner"]
                  + funn["unsupported_claim"])[:20]:
            print("  FUNN:", f)
        for f in funn["orphan"][:20]:
            print("  INFO (ikke kartlagt til side ennå):", f["id"], "-", f["text"])
        for f in funn["anchor_queue"][:20]:
            print("  INFO (kobling uten anker):", f["id"], "->", f["page"])
    return 1 if harde else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
