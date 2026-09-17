#!/usr/bin/env python3
"""validate_activity_log.py — fase 1-kontroll av logs/activity.jsonl.

Append-only er en git-egenskap, ikke en fil-egenskap: CI kjører med
--base origin/main og krever at diffen på logs/ BARE er innsettinger
(sjekkes i CI-steget, ikke her — her valideres linjene). Dette skriptet
sjekker per linje: gyldig JSON, obligatoriske felter, unik event_id,
gyldig ISO-8601-tid, kjent action, rolle innenfor enum.

Statusordene (t_882cfca): `statusord` er en VALGFRI liste med verdier fra
{maskinelt kontrollert, eksternt verifisert, faglig godkjent}. De tre ordene
er gjensidig uavhengige — ingen av dem impliserer de to andre, og vakten
legger aldri til eller krever et ord som ikke står i posten. Den ene regelen
som håndheves: «faglig godkjent» kan bare stå på en post med role=menneske,
fordi faglig godkjenning ikke kan delegeres til en etikett (avgjørelsen
2026-09-17, §«Tre statusord som aldri må blandes»). Å skrive «maskinelt
kontrollert» er prosesskontroll og kan gjøres av en profil; å skrive
«faglig godkjent» er menneskets.

Bruk: python3 scripts/maintenance/validate_activity_log.py [--json]
Exit: 0 = OK, 1 = feil.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
LOGG = ROT / "logs" / "activity.jsonl"

AKSJONER = {
    "card_created", "lease_acquired", "branch_created", "file_changed",
    "validation_finished", "commit_created", "pr_opened", "review_completed",
    "merge_completed", "remote_readback", "public_readback", "blocked",
    "unblocked", "card_closed", "rollback_completed",
}
ROLLER = {"researcher", "orchestrator", "faber", "opus-core", "verifier", "legacy", "menneske"}
STATUSORD = {"maskinelt kontrollert", "eksternt verifisert", "faglig godkjent"}
MENNESKELIGE_ORD = {"faglig godkjent"}
PLIKT = ["event_id", "occurred_at", "action", "role", "kanban_card",
         "files", "why", "result", "reversible"]


def sjekk_statusord(e: dict, nr: int) -> list[dict]:
    """Statusordene er gjensidig uavhengige.

    Denne funksjonen legger ALDRI til et ord og krever ALDRI et ord som ikke
    står i posten — den avviser bare ukjente verdier, duplikater, tom liste,
    og «faglig godkjent» på en post som ikke er menneskets.
    """
    feil: list[dict] = []
    if "statusord" not in e:
        return feil
    v = e["statusord"]
    if not isinstance(v, list) or not v:
        return [{"type": "bad_statusord", "linje": nr,
                 "msg": "statusord må være en ikke-tom liste"}]
    sett: set[str] = set()
    for ord_ in v:
        if ord_ not in STATUSORD:
            feil.append({"type": "unknown_statusord", "linje": nr, "statusord": ord_})
        if ord_ in sett:
            feil.append({"type": "duplicate_statusord", "linje": nr, "statusord": ord_})
        sett.add(ord_)
    if (sett & MENNESKELIGE_ORD) and e.get("role") != "menneske":
        feil.append({"type": "faglig_godkjent_uten_menneske", "linje": nr,
                     "role": e.get("role")})
    return feil


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    feil = []
    sett = set()
    if not LOGG.is_file():
        feil.append({"type": "missing_log", "msg": str(LOGG)})
    else:
        for nr, linje in enumerate(LOGG.read_text(encoding="utf-8").splitlines(), 1):
            if not linje.strip():
                continue
            try:
                e = json.loads(linje)
            except json.JSONDecodeError as ex:
                feil.append({"type": "invalid_json", "linje": nr, "msg": str(ex)[:100]})
                continue
            for felt in PLIKT:
                if felt not in e or e[felt] in (None, ""):
                    feil.append({"type": "missing_field", "linje": nr, "felt": felt})
            if e.get("event_id") in sett:
                feil.append({"type": "duplicate_event_id", "linje": nr, "id": e["event_id"]})
            sett.add(e.get("event_id"))
            if e.get("action") not in AKSJONER:
                feil.append({"type": "unknown_action", "linje": nr, "action": e.get("action")})
            if e.get("role") not in ROLLER:
                feil.append({"type": "unknown_role", "linje": nr, "role": e.get("role")})
            try:
                datetime.fromisoformat(str(e.get("occurred_at", "")).replace("Z", "+00:00"))
            except ValueError:
                feil.append({"type": "invalid_timestamp", "linje": nr})
            feil += sjekk_statusord(e, nr)
    if a.json:
        print(json.dumps({"feil": feil}, ensure_ascii=False, indent=1))
    else:
        print(f"activity-log: {len(feil)} feil")
        for f in feil[:20]:
            print("  ", f)
    return 1 if feil else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
