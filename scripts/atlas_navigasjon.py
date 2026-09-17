#!/usr/bin/env python3
"""atlas_navigasjon — maal om atlaset kan navigeres i ALLE tre lag.

Atlaset har tre lag som ikke er det samme:

    NODER    (schema/regime_nodes.jsonld)      det konseptuelle kartet
    MOTORER  (efc_inference/engine/*.py)       koden som regner
    NATS     (schema/nats_domener.snapshot)    stroemmene som baerer data

Et oppslagsverk som bare kjenner ett av lagene, kan ikke svare paa «hvor
kommer dette tallet fra?» eller «hva mater denne motoren?». Maalt
2026-09-17 fantes koblingene emne -> motor som PROSA i
`docs/nats-koblingskart.md` — dokumentert for et menneske, ikke kjoerbart
for den som skal navigere.

Denne modulen maaler hvor langt navigasjonen faktisk rekker, og NAVNGIR
hullene. Den er en maaling, ikke en garanti: et tomt hull-liste betyr at
hver node, motor og emne har en vei til de andre lagene.

Feilmodusen den finnes for aa hindre: «jeg trodde jeg kunne navigere
atlaset» naar det egentlig bare var nodene jeg kunne lese.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

STANDARD_REF = "origin/main"

MOTOR_KATALOG = "efc_inference/engine"
NODE_STI = "schema/regime_nodes.jsonld"
SNAPSHOT_STI = "schema/nats_domener.snapshot.json"


class NavigasjonFeil(RuntimeError):
    """Grunnlaget kunne ikke leses. Aldri stille tomt svar."""


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise NavigasjonFeil(
            f"git {' '.join(args)} feilet i {repo}: {p.stderr.strip()}")
    return p.stdout


def les_noder(repo: Path, ref: str) -> list[dict]:
    raa = _git(repo, "show", f"{ref}:{NODE_STI}")
    return json.loads(raa)["nodes"]


def les_motorer(repo: Path, ref: str) -> list[str]:
    """Motornavn fra git-treet — ikke fra disken.

    Samme regel som `atlas_lesing`: en arbeidskopi som svarer, leser som et
    levende atlas. En motorfil som ligger ucommittet paa disken finnes ikke
    for den som leser fra refen.

    Mangler katalogen, er svaret TOMT — ikke en feil. Git sporer ikke tomme
    kataloger, og en repo uten motorer er en gyldig repo. Maalt: uten dette
    krasjet `naviger()` med `fatal: Not a valid object name` i stedet for aa
    rapportere null motorer.
    """
    try:
        ut = _git(repo, "ls-tree", "--name-only", f"{ref}:{MOTOR_KATALOG}")
    except NavigasjonFeil:
        return []
    return sorted(
        Path(l).stem for l in ut.splitlines()
        if l.endswith(".py") and not l.endswith("__init__.py")
        and not l.endswith("base_engine.py"))


def les_snapshot(repo: Path, ref: str) -> dict:
    raa = _git(repo, "show", f"{ref}:{SNAPSHOT_STI}")
    d = json.loads(raa)
    return d.get("domener", d)



def _epistemisk(noder: list[dict]) -> dict:
    """Hva sloeyfa INNEHOLDER — ikke bare hva den er koblet til.

    Maalt 2026-09-17 ved aa bruke oppslaget: 0 av 73 offentlige noder kunne
    felles av en observasjon. Det er ikke en koblingsfeil — det er en
    egenskap ved innholdet, og den forsvant saa snart samtalen var over.

    Offentlige og interne telles hver for seg: de offentlige er det
    PUBLISERTE atlaset, og et hull der er alvorligere enn blant vaare egne.
    """
    def har_falsifikator(n: dict) -> bool:
        return "ville_falsifisere" in json.dumps(n, ensure_ascii=False)

    offentlige = [n for n in noder if n.get("synlighet") == "offentlig"]

    def tell(pred, mengde: list[dict]) -> tuple[int, int]:
        return sum(1 for n in mengde if pred(n)), len(mengde)

    def har(n: dict, felt: str) -> bool:
        return bool(n.get(felt))

    return {
        "falsifikator": tell(har_falsifikator, noder),
        "falsifikator_offentlig": tell(har_falsifikator, offentlige),
        "prediksjon": tell(lambda n: har(n, "prediction"), noder),
        "oppgjoer": tell(lambda n: har(n, "settlement"), noder),
        "offentlige": len(offentlige),
    }


def naviger(repo: str | Path, ref: str = STANDARD_REF) -> dict:
    """Maal navigasjonen paa tvers av noder, motorer og NATS.

    Returnerer dekningsgraden OG hullene, navngitt. Et hull er ikke en feil
    — `verden.vaer` er ikke dekket fordi ingen har bygget den noden ennå.
    Men et UNEVNT hull er en feil: da ser kartet komplett ut uten aa vaere det.
    """
    repo = Path(repo)
    noder = les_noder(repo, ref)
    motorer = les_motorer(repo, ref)
    snapshot = les_snapshot(repo, ref)

    node_ider = {n.get("id") for n in noder}
    domene_til_noder: dict[str, list[str]] = {}
    for n in noder:
        b = n.get("buss_domene")
        if b:
            nid = n.get("id")
            if nid:
                domene_til_noder.setdefault(b, []).append(nid)

    # node -> motor: konvensjonen er at node-id-en baerer motornavnet
    # (`efc.water_phase_engine` -> `water`). Maalt: alle 19 motorer har en node.
    motor_til_node: dict[str, str] = {}
    for m in motorer:
        for nid in node_ider:
            if nid and m in nid:
                motor_til_node[m] = nid
                break

    # emner: hvert domene i snapshotet har en liste av emner
    alle_emner: list[str] = []
    for domene, v in snapshot.items():
        for e in (v or {}).get("emner", []):
            alle_emner.append(f"{domene}.{e}")

    emner_med_node = [e for e in alle_emner
                      if e.rsplit(".", 1)[0].split(".", 2)[0:2]
                      and ".".join(e.split(".")[:2]) in domene_til_noder]
    emner_uten_node = [e for e in alle_emner if e not in emner_med_node]

    # En motor naar bussen naar dens NODE har et `buss_domene`. Uten det
    # finnes ingen vei fra stroemmen tilbake til koden som regnet den.
    motorer_uten_buss = [
        m for m in motorer
        if not any(n.get("buss_domene") for n in noder
                   if n.get("id") == motor_til_node.get(m))]

    # Hvilke domener paa bussen har INGEN node?
    domener_uten_node = sorted(d for d in snapshot if d not in domene_til_noder)

    return {
        "ref": ref,
        "commit": _git(repo, "rev-parse", ref).strip(),
        "lag": {"noder": len(noder), "motorer": len(motorer),
                "emner": len(alle_emner),
                "buss_domener": len(snapshot)},
        "kobling": {
            "motor_til_node": motor_til_node,
            "domene_til_noder": {k: sorted(v) for k, v in sorted(domene_til_noder.items())},
        },
        "hull": {
            "emner_uten_node": sorted(emner_uten_node),
            "domener_uten_node": domener_uten_node,
            "motorer_uten_buss": sorted(motorer_uten_buss),
        },
        "epistemisk": _epistemisk(noder),
        "dekning": {
            "emner": (len(alle_emner) - len(emner_uten_node), len(alle_emner)),
            "domener": (len(snapshot) - len(domener_uten_node), len(snapshot)),
            "motorer": (len(motorer) - len(motorer_uten_buss), len(motorer)),
        },
    }


if __name__ == "__main__":
    import sys

    d = naviger(sys.argv[1] if len(sys.argv) > 1 else ".", )
    lag = d["lag"]
    print(f"{d['ref']} @ {d['commit'][:8]}")
    print(f"  lag      : {lag['noder']} noder · {lag['motorer']} motorer · "
          f"{lag['emner']} emner i {lag['buss_domener']} domener")
    for navn, (n, t) in d["dekning"].items():
        print(f"  {navn:9}: {n}/{t} naar fram")
    e = d["epistemisk"]
    print(f"  epistemisk: kan felles {e['falsifikator_offentlig'][0]}/{e['falsifikator_offentlig'][1]} "
          f"offentlige · prediksjon {e['prediksjon'][0]} · oppgjoer {e['oppgjoer'][0]}")
    for navn, hull in d["hull"].items():
        if hull:
            print(f"  HULL {navn} ({len(hull)}): {', '.join(str(h) for h in hull[:5])}"
                  f"{' ...' if len(hull) > 5 else ''}")
