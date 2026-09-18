#!/usr/bin/env python3
"""Les eitt ord eller ein node gjennom minne, motor og NATS."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

STANDARD_REF = "origin/main"
NODE_STI = "schema/regime_nodes.jsonld"
DEKNING_STI = "schema/atlas_dekning.json"
NATS_STI = "schema/nats_domener.snapshot.json"
MOTOR_STI = "efc_inference/engine"


class InngangFeil(RuntimeError):
    """Grunnlaget kunne ikkje lesast."""


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True)
    if p.returncode:
        raise InngangFeil(f"git {' '.join(args)} feilet: {p.stderr.strip()}")
    return p.stdout


def json_ref(repo: Path, ref: str, sti: str) -> dict:
    return json.loads(git(repo, "show", f"{ref}:{sti}"))


def motorfiler(repo: Path, ref: str) -> list[str]:
    """Motorfiler i git-treet paa `ref`.

    En TOM liste betyr at katalogen finnes og ikke har motorer. Foerste utgave
    svelget ogsaa «katalogen finnes ikke» og svarte det samme — «ingen
    motorfil» — og da ser et manglende tre ut som et funn. Naas katalogen ikke
    finnes, sier kallet fra.
    """
    try:
        filer = git(repo, "ls-tree", "--name-only", f"{ref}:{MOTOR_STI}")
    except InngangFeil as e:
        raise InngangFeil(
            f"{MOTOR_STI} finnes ikke paa {ref} — motorlaget er ikke lest"
        ) from e
    return sorted(Path(x).stem for x in filer.splitlines()
                  if x.endswith(".py") and Path(x).stem not in {"__init__", "base_engine"})


def node_motor(node_id: str, motorer: list[str]) -> str | None:
    suffix = node_id.rsplit(".", 1)[-1]
    if not suffix.endswith("_engine"):
        return None
    navn = suffix[:-7]
    return f"{navn}.py" if navn in motorer else None


def kjent_hull(dekning: dict, ordet: str) -> dict | None:
    needle = ordet.lower().replace("-", "_")
    for domene, data in sorted(dekning.get("domener", {}).items()):
        if needle == domene.lower() or needle in domene.lower().split("."):
            return {"domene": domene, **data}
        if any(needle == str(n).lower() for n in data.get("noder", [])):
            return None
    return None


def emne_oppslag(repo: Path, sha: str, ordet: str) -> tuple[list[str], bool]:
    """Del resloseren med `atlas_lesing` i stedet for aa ha to sannheter.

    Maalt i review 2026-09-18: denne inngangen slo bare opp EKSAKTE node-id-er
    og buss-domener. Ordet «entropy gradient» kunne da svares «ATLASET VET
    IKKE» her, mens `atlas_lesing --emne` svarte med treff — to innganger, to
    svar, samme spoersmaal. Den ene inngangen skal ikke ha sin egen ordbok.

    Returnerer (linjer, er_registrert_begrep). Det siste flagget finnes fordi
    «atlaset vet ikke» er FEIL svar naar begrepet staar i navnerommet:
    atlaset vet hva ordet er, det har bare ingen node for det.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import atlas_lesing
    except ImportError as e:  # pragma: no cover - bare naar fila mangler
        return ([f"EMNE: ikke slaat opp — atlas_lesing kunne ikke leses ({e})"],
                False)
    svar = atlas_lesing.finn(repo, ordet, sha)
    treff = svar.get("treff", [])
    begrep = [t for t in treff if t.get("trefftype") == "navnerom"]
    linjer = [f"EMNE: {svar['antall']} treff i banken"
              + (" — ATLASET VET IKKE" if svar.get("hull") else "")]
    for t in treff[:5]:
        merke = " (navnerom, ingen node)" if t.get("trefftype") == "navnerom" else ""
        linjer.append(f"  {t.get('id', '?')}{merke}")
    if begrep:
        linjer.append(f"  begrepet er registrert, men har ingen node: "
                      f"{begrep[0].get('grunn', 'grunn ikke oppgitt')}")
    if svar.get("hull"):
        kjent = atlas_lesing._kjent_hull(
            atlas_lesing._dekning(repo, sha, False), ordet)
        if kjent:
            linjer.append(f"  kjent hull: {kjent.get('domene')} — "
                          f"{kjent.get('begrunnelse', 'ingen grunn oppgitt')}")
    return linjer, bool(begrep)


def les(repo: str | Path, ord_eller_node: str, ref: str = STANDARD_REF) -> str:
    repo = Path(repo)
    # ÉN opploest commit. Leser vi den bevegelige refen videre, kan to filer i
    # samme svar komme fra hver sin tilstand naar refen flytter seg.
    sha = git(repo, "rev-parse", ref).strip()
    atlas = json_ref(repo, sha, NODE_STI)
    node = next((n for n in atlas.get("nodes", [])
                 if n.get("id") == ord_eller_node), None)
    nats = json_ref(repo, sha, NATS_STI).get("domener", {})
    dekning = json_ref(repo, sha, DEKNING_STI)
    try:
        motorer = motorfiler(repo, sha)
        motor_feil = None
    except InngangFeil as e:
        # Navngitt fravaer, ikke «ingen motorfil». Et manglende tre er ikke et
        # funn om at noden ikke har motor.
        motorer, motor_feil = [], str(e)
    lines = [f"INNGANG: {ord_eller_node}", f"REF: {ref} @ {sha[:8]}"]
    if node is None:
        hull = kjent_hull(dekning, ord_eller_node)
        emne_linjer, er_begrep = emne_oppslag(repo, sha, ord_eller_node)
        if er_begrep:
            # «Atlaset vet ikke» er feil svar naar begrepet er registrert.
            # Atlaset vet hva ordet ER; det har bare ingen node for det.
            lines.append("NODE: ingen node — REGISTRERT BEGREP, ingen atlasnode")
        elif hull is not None:
            lines += ["NODE: ingen node — KJENT HULL",
                      f"  domene: {hull['domene']}",
                      f"  status: {hull.get('status', 'ukjent')}"]
            lines.append(f"  grunn: {hull.get('begrunnelse', 'ingen deklarert grunn')}")
        else:
            lines.append("NODE: ingen node — ATLASET VET IKKE (ingen maaling)")
        lines += emne_linjer
        lines.append("MOTOR: ingen motorfil")
        lines.append("BUSS: ingen buss-vei")
    else:
        regime = node.get("regime") or {}
        ep = node.get("epistemikk") or {}
        s_status = (node.get("maale_paradigme") or {}).get("s_regime", "ikke deklarert")
        lines += [f"NODE: {node['id']}",
                  # Feltet heter `phase`, ikke «kode». Foerste utgave skrev
                  # «kode: regime_engine» — et navn som loey om innholdet, for
                  # nodens kode er den korte identifikatoren (RO, HB, …) som
                  # generatoren eier. Et felt som presenterer en fase som en
                  # kode er samme klasse som et svar som svarer paa noe annet.
                  f"  fase: {node.get('phase', 'ikke deklarert')}",
                  f"  regime: {regime.get('name', 'ikke deklarert')}",
                  f"  synlighet: {node.get('synlighet', 'ikke deklarert')}",
                  f"  gyldighet: {regime.get('validity', regime.get('name', 'ikke deklarert'))}",
                  f"  epistemikk: sannhet={ep.get('sannhetsstatus', 'ikke deklarert')}; evidens={ep.get('evidensstatus', 'ikke deklarert')}",
                  f"  S-akse-status: {s_status}"]
        motor = node_motor(node["id"], motorer)
        if motor_feil:
            lines.append(f"MOTOR: ikke lest — {motor_feil}")
        else:
            lines.append(f"MOTOR: {motor or 'ingen motorfil'}"
                         + (" (utledet av navnekonvensjonen node-id -> "
                            "motornavn, ikke av en deklarert kobling)"
                            if motor else ""))
        domene = node.get("buss_domene")
        if domene and domene in nats:
            emner = nats[domene].get("emner", {})
            lines.append(f"BUSS: {domene}")
            lines.extend(f"  emne: {emne}" for emne in sorted(emner))
        else:
            grunn = node.get("lagdeling", {}).get("bussgrunn") or "noden deklarerer ikkje buss_domene"
            lines += ["BUSS: ingen buss-vei", f"  grunn: {grunn}"]
    lines.append("UTENFOR REKKEVIDDE: Hindsight-banken efc eies av MCP-verktoyene mcp__hindsight_efc__*; skriptet kan ikkje lese den.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Finn kvar eit atlasord lever.")
    ap.add_argument("ord_eller_node_id")
    ap.add_argument("--ref", default=STANDARD_REF)
    ap.add_argument("repo", nargs="?", default=".")
    a = ap.parse_args()
    try:
        print(les(a.repo, a.ord_eller_node_id, a.ref))
    except (InngangFeil, json.JSONDecodeError) as e:
        print(f"FEIL: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
